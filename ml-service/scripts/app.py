# scripts/app.py

from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
import tensorflow as tf
import joblib
import os

app = Flask(__name__)

# === CONFIGURATION ===
# Paths to artifacts
MODEL_PATH = os.path.join("model.h5")
SCALER_PATH = os.path.join("data", "processed", "scaler.save")
COMBINED_CSV = os.path.join("data", "processed", "combined_data.csv")

# Load model + scaler + combined_data DataFrame
print("Loading model ...")
model = tf.keras.models.load_model(MODEL_PATH)

print("Loading scaler ...")
scaler = joblib.load(SCALER_PATH)

print("Loading combined_data for inference ...")
data_df = pd.read_csv(COMBINED_CSV, dtype={"symbol": str})
# We will treat data_df itself as our “feature store.” For a real app, update these rows continuously.

# Precompute the feature columns (must match train_model.py’s feature selection)
NUMERIC_COLS = ["MarketCap", "RevenueGrowth", "PE", "DividendYield", "volatility", "momentum"]
SECTOR_COLS = sorted([c for c in data_df.columns if c.startswith("Sector_")])
FEATURE_COLS = NUMERIC_COLS + SECTOR_COLS

# Label names must match exactly train_model.py
LABEL_COLS = [
    "LargeCap", "MidCap", "SmallCap", "MicroCap",
    "GrowthStock", "ValueStock", "IncomeStock", "BlueChipStock",
    "Cyclical", "Defensive"
] + sorted(SECTOR_COLS) + ["DividendStock", "NonDividendStock"]


@app.route("/predict", methods=["GET"])
def predict():
    ticker = request.args.get("ticker", default=None, type=str)
    if not ticker:
        return jsonify({"error": "No ticker provided"}), 400

    ticker = ticker.upper()
    # Look up the row in data_df
    row = data_df[data_df["symbol"] == ticker]
    if row.empty:
        return jsonify({"error": f"Ticker '{ticker}' not found."}), 404

    # Extract feature values
    feats = row[FEATURE_COLS].values.astype(float)  # shape = (1, n_features)
    # Scale numeric columns (the scaler was fit on [numeric_cols + sector_cols]—sector cols remain 0/1)
    feats[:, : len(NUMERIC_COLS)] = scaler.transform(feats[:, : len(NUMERIC_COLS)])

    # Get prediction
    probs = model.predict(feats)[0]  # shape = (n_labels,)
    # Convert to boolean labels with threshold 0.5
    preds = (probs >= 0.5).astype(int)

    # Build response dict
    result = {"ticker": ticker, "labels": {}}
    for label_name, p in zip(LABEL_COLS, preds):
        result["labels"][label_name] = bool(p)

    return jsonify(result)

if __name__ == "__main__":
    # Run on port 5000 (default) accessible from localhost
    app.run(host="0.0.0.0", port=5000, debug=False)
