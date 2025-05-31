# scripts/merge_all_features.py

import pandas as pd
import os

# === CONFIGURATION ===
PROCESSED_DIR = os.path.join("data", "processed")
FUNDAMENTALS_CLEAN_CSV = os.path.join(PROCESSED_DIR, "fundamentals_clean.csv")
PRICE_FEATURES_CSV      = os.path.join(PROCESSED_DIR, "price_features.csv")
COMBINED_CSV            = os.path.join(PROCESSED_DIR, "combined_data.csv")

def main():
    # 1) Load cleaned fundamentals
    print(f"Loading fundamentals from {FUNDAMENTALS_CLEAN_CSV} ...")
    fund = pd.read_csv(FUNDAMENTALS_CLEAN_CSV, dtype={"symbol": str})
    print(f"  → Fundamentals: {fund.shape[0]} rows × {fund.shape[1]} columns")

    # 2) Load price features
    print(f"Loading price features from {PRICE_FEATURES_CSV} ...")
    price_feats = pd.read_csv(PRICE_FEATURES_CSV, dtype={"symbol": str})
    print(f"  → Price features: {price_feats.shape[0]} rows × {price_feats.shape[1]} columns")

    # 3) Merge on 'symbol'
    print("Merging fundamentals with price features ...")
    df = pd.merge(
        fund,
        price_feats,
        on="symbol",
        how="inner"
    )
    print(f"  → After merge: {df.shape[0]} tickers × {df.shape[1]} columns")

    # 4) Compute derived features if columns exist
    #    We expect at least these columns in fund:
    #      - 'Revenue' (for current revenue)
    #      - 'RevenuePriorYear' (if available; adjust accordingly)
    #    If your Kaggle data uses different indicator names (e.g. 'totalRevenue', 'totalRevenuePriorYear'),
    #    replace below with the correct column names.
    if "Revenue" in df.columns and "RevenuePriorYear" in df.columns:
        print("Computing Year‐over‐Year Revenue Growth ...")
        df["RevenueGrowth"] = (
            df["Revenue"].astype(float) - df["RevenuePriorYear"].astype(float)
        ) / df["RevenuePriorYear"].astype(float)
    else:
        print("  → WARNING: 'Revenue' or 'RevenuePriorYear' not found; skipping RevenueGrowth.")

    # 5) Compute P/E ratio if not already present
    #    If Kaggle fundamentals used 'PE' or 'priceToEarnings', rename here accordingly.
    if "PE" not in df.columns and "priceToEarnings" in df.columns:
        df["PE"] = df["priceToEarnings"]

    # 6) Compute DividendYield if not already present
    #    If Kaggle fundamentals used 'dividendYield', rename here accordingly.
    if "DividendYield" not in df.columns and "dividendYield" in df.columns:
        df["DividendYield"] = df["dividendYield"]

    # 7) At this point, df should contain at least:
    #    - symbol, sector, MarketCap (or marketCapitalization), RevenueGrowth, PE, DividendYield, volatility, momentum, plus raw indicators.
    #    You can rename columns if needed to match the training script’s expectations.

    # 8) Save combined data
    print(f"Saving combined data to {COMBINED_CSV} ...")
    df.to_csv(COMBINED_CSV, index=False)
    print("Done. Now run train_model.py to build & train the model.")

if __name__ == "__main__":
    main()
