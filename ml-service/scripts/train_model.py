# scripts/train_model.py

import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
import joblib

# === CONFIGURATION ===
PROCESSED_DIR = os.path.join("data", "processed")
COMBINED_CSV = os.path.join(PROCESSED_DIR, "combined_data.csv")
MODEL_OUTPUT = "model.h5"
SCALER_OUTPUT = os.path.join(PROCESSED_DIR, "scaler.save")
HISTORY_OUTPUT = os.path.join(PROCESSED_DIR, "training_history.csv")

# Thresholds & mappings
SIZE_THRESHOLDS = {
    "LargeCap": 10e9,      # MarketCap ≥ $10B
    "MidCap_min": 2e9,     # $2B ≤ MarketCap < $10B
    "MidCap_max": 10e9,
    "SmallCap_min": 300e6, # $300M ≤ MarketCap < $2B
    "SmallCap_max": 2e9,
    "MicroCap_max": 300e6  # MarketCap < $300M
}

STYLE_THRESHOLDS = {
    "GrowthStock_rev_growth": 0.15,   # 15% YoY revenue growth
    "ValueStock_pe": 15.0,            # P/E ≤ 15
    "IncomeStock_div_yield": 0.03     # Dividend yield ≥ 3%
}

CYCLICAL_SECTORS = {
    "Technology", "Consumer Discretionary", "Materials",
    "Industrials", "Energy", "Communication Services"
}
# Any sector not in CYCLICAL_SECTORS → Defensive

SEED = 42

def load_data(path):
    print(f"Loading combined data from {path} ...")
    df = pd.read_csv(path, dtype={"symbol": str})
    print(f"  → {df.shape[0]} rows, {df.shape[1]} columns.")
    return df

def compute_labels(df):
    df = df.copy()
    # REQUIRED COLUMNS: 'MarketCap', 'RevenueGrowth', 'PE', 'DividendYield', 'sector'
    for col in ["MarketCap", "RevenueGrowth", "PE", "DividendYield", "sector"]:
        if col not in df.columns:
            raise KeyError(f"Missing column '{col}' in combined_data.csv. Found: {list(df.columns)}")

    # --- 1) Size Labels ---
    mc = df["MarketCap"].fillna(0).astype(float)
    df["LargeCap"] = (mc >= SIZE_THRESHOLDS["LargeCap"]).astype(int)
    df["MidCap"]   = ((mc >= SIZE_THRESHOLDS["MidCap_min"]) & (mc < SIZE_THRESHOLDS["MidCap_max"])).astype(int)
    df["SmallCap"] = ((mc >= SIZE_THRESHOLDS["SmallCap_min"]) & (mc < SIZE_THRESHOLDS["SmallCap_max"])).astype(int)
    df["MicroCap"] = (mc < SIZE_THRESHOLDS["MicroCap_max"]).astype(int)

    # --- 2) Style Labels ---
    df["GrowthStock"] = (df["RevenueGrowth"].fillna(0) >= STYLE_THRESHOLDS["GrowthStock_rev_growth"]).astype(int)
    df["ValueStock"]  = (df["PE"].fillna(9999) <= STYLE_THRESHOLDS["ValueStock_pe"]).astype(int)
    df["IncomeStock"] = (df["DividendYield"].fillna(0) >= STYLE_THRESHOLDS["IncomeStock_div_yield"]).astype(int)
    # Blue‐chip = LargeCap AND IncomeStock
    df["BlueChipStock"] = ((df["LargeCap"] == 1) & (df["IncomeStock"] == 1)).astype(int)

    # --- 3) Economic Sensitivity Labels ---
    df["Cyclical"]  = df["sector"].apply(lambda s: 1 if s in CYCLICAL_SECTORS else 0).astype(int)
    df["Defensive"] = (1 - df["Cyclical"]).astype(int)

    # --- 4) Sector One‐Hot Encoding ---
    unique_sectors = sorted(df["sector"].dropna().unique())
    for sect in unique_sectors:
        col_name = f"Sector_{sect.replace(' ', '')}"
        df[col_name] = (df["sector"] == sect).astype(int)

    # --- 5) Dividend Policy Labels ---
    df["DividendStock"]    = (df["DividendYield"].fillna(0) > 0).astype(int)
    df["NonDividendStock"] = (1 - df["DividendStock"]).astype(int)

    return df

def build_feature_matrix(df):
    # 1) Numeric columns (adjust if your combined_data.csv uses different names)
    numeric_cols = [
        "MarketCap",
        "RevenueGrowth",
        "PE",
        "DividendYield",
        "volatility",
        "momentum"
    ]
    missing_num = [c for c in numeric_cols if c not in df.columns]
    if missing_num:
        raise KeyError(f"Missing numeric columns: {missing_num}")

    # 2) Sector one-hot columns
    sector_cols = [c for c in df.columns if c.startswith("Sector_")]

    feature_df = df[numeric_cols + sector_cols].copy()
    scaler = StandardScaler()
    feature_df[numeric_cols] = scaler.fit_transform(feature_df[numeric_cols])

    X = feature_df.values
    feature_names = numeric_cols + sector_cols

    # Save scaler for inference
    joblib.dump(scaler, SCALER_OUTPUT)
    print(f"Saved StandardScaler to {SCALER_OUTPUT}.")

    return X, feature_names

def build_label_matrix(df):
    # 1) Size
    label_cols = ["LargeCap", "MidCap", "SmallCap", "MicroCap"]
    # 2) Style
    label_cols += ["GrowthStock", "ValueStock", "IncomeStock", "BlueChipStock"]
    # 3) Econ sensitivity
    label_cols += ["Cyclical", "Defensive"]
    # 4) Sector one-hot (must match exactly the columns created above)
    sector_label_cols = sorted([c for c in df.columns if c.startswith("Sector_")])
    label_cols += sector_label_cols
    # 5) Dividend
    label_cols += ["DividendStock", "NonDividendStock"]

    missing_lbl = [c for c in label_cols if c not in df.columns]
    if missing_lbl:
        raise KeyError(f"Missing label columns: {missing_lbl}")

    y = df[label_cols].values.astype(int)
    return y, label_cols

def split_data(X, y, test_size=0.20, val_size=0.10):
    # First split out test set
    X_train_val, X_test, y_train_val, y_test = train_test_split(
        X, y, test_size=test_size, random_state=SEED
    )
    # Then split train vs. validation
    val_fraction = val_size / (1 - test_size)
    X_train, X_val, y_train, y_val = train_test_split(
        X_train_val, y_train_val, test_size=val_fraction, random_state=SEED
    )
    print(f"Train: {X_train.shape[0]} | Val: {X_val.shape[0]} | Test: {X_test.shape[0]}")
    return X_train, X_val, X_test, y_train, y_val, y_test

def build_model(input_dim, output_dim):
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(input_dim,)),
        tf.keras.layers.Dense(128, activation="relu"),
        tf.keras.layers.Dropout(0.3),
        tf.keras.layers.Dense(64, activation="relu"),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(output_dim, activation="sigmoid")
    ])
    model.compile(
        optimizer="adam",
        loss="binary_crossentropy",
        metrics=["accuracy"]
    )
    return model

def main():
    # 1) Load data
    df = load_data(COMBINED_CSV)

    # 2) Compute labels
    df_labeled = compute_labels(df)
    print("Labels computed.")

    # 3) Build X and y
    X, feature_names = build_feature_matrix(df_labeled)
    y, label_names = build_label_matrix(df_labeled)
    print(f"Features: {len(feature_names)} columns | Labels: {len(label_names)} columns")

    # 4) Split into train/val/test
    X_train, X_val, X_test, y_train, y_val, y_test = split_data(X, y)

    # 5) Build and train model
    model = build_model(input_dim=X.shape[1], output_dim=y.shape[1])
    model.summary()

    print("Starting training ...")
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=50,
        batch_size=32,
        verbose=2
    )

    # 6) Evaluate on test set
    test_loss, test_acc = model.evaluate(X_test, y_test, verbose=0)
    print(f"Test Loss: {test_loss:.4f} | Test Acc: {test_acc:.4f}")

    # 7) Save the model
    print(f"Saving trained model to {MODEL_OUTPUT} ...")
    model.save(MODEL_OUTPUT)

    # 8) Save training history
    hist_df = pd.DataFrame(history.history)
    hist_df.to_csv(HISTORY_OUTPUT, index=False)
    print(f"Training history saved to {HISTORY_OUTPUT}.")

if __name__ == "__main__":
    main()
