# scripts/compute_price_features.py

import os
import pandas as pd
import numpy as np

# === CONFIGURATION ===
RAW_DIR = os.path.join("data", "raw")
PRICES_CSV = os.path.join(RAW_DIR, "prices.csv")

PROCESSED_DIR = os.path.join("data", "processed")
os.makedirs(PROCESSED_DIR, exist_ok=True)
PRICE_FEATURES_CSV = os.path.join(PROCESSED_DIR, "price_features.csv")

# Rolling window sizes (in trading days)
VOL_WINDOW = 252      # ~1 year of trading days
MOM_WINDOW = 126      # ~6 months of trading days

def main():
    print(f"Loading price data from {PRICES_CSV} ...")
    df = pd.read_csv(
        PRICES_CSV,
        parse_dates=["date"],
        dtype={"symbol": str, "open": float, "high": float, "low": float, "close": float, "volume": float}
    )
    print(f"  → {df.shape[0]} rows loaded for {df['symbol'].nunique()} tickers.")

    # Sort by ticker + date to ensure rolling works correctly
    df = df.sort_values(["symbol", "date"])
    
    # Compute daily returns per ticker
    df["return"] = df.groupby("symbol")["close"].pct_change()

    # Function to compute features for one ticker
    def compute_feats(grp):
        grp = grp.copy()
        # 1-year volatility: rolling std of daily returns over VOL_WINDOW days
        grp["volatility"] = grp["return"].rolling(window=VOL_WINDOW, min_periods=VOL_WINDOW).std()
        # 6-month momentum: (close / close.shift(MOM_WINDOW)) - 1
        grp["momentum"] = (grp["close"] / grp["close"].shift(MOM_WINDOW)) - 1.0
        return grp

    print("Computing rolling volatility and momentum per ticker ...")
    df_feats = df.groupby("symbol", group_keys=False).apply(compute_feats)

    # For each ticker, keep only the last (most recent) row’s features
    print("Selecting latest row per ticker ...")
    latest = df_feats.sort_values("date").groupby("symbol").tail(1)

    # We only need: symbol, volatility, momentum
    price_features = latest[["symbol", "volatility", "momentum"]].copy()

    # Drop tickers where volatility or momentum is NaN (due to insufficient history)
    price_features = price_features.dropna(subset=["volatility", "momentum"])
    print(f"  → {price_features.shape[0]} tickers have sufficient history for VOL and MOM.")

    # Write to CSV
    print(f"Saving price_features to {PRICE_FEATURES_CSV} ...")
    price_features.to_csv(PRICE_FEATURES_CSV, index=False)
    print("Done.")

if __name__ == "__main__":
    main()
