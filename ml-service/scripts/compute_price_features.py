# File: ml-service/scripts/compute_price_features.py

import os
import pandas as pd

# ===========================
# 1) HARDCODED FILEPATHS
# ===========================
PROJECT_ROOT       = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RAW_DIR            = os.path.join(PROJECT_ROOT, "data", "raw")
PROCESSED_DIR      = os.path.join(PROJECT_ROOT, "data", "processed")

PRICES_CSV         = os.path.join(RAW_DIR, "prices.csv")
PRICE_FEATURES_CSV = os.path.join(PROCESSED_DIR, "price_features.csv")

# ===========================
# 2) PARAMETERS
# ===========================
VOL_WINDOW = 252   # ~1 year of trading days
MOM_WINDOW = 126   # ~6 months of trading days

def main():
    # 2.1 Ensure processed directory exists
    os.makedirs(PROCESSED_DIR, exist_ok=True)

    # 2.2 First, load only the header row to see actual column names
    print(f"Inspecting columns in {PRICES_CSV} …")
    try:
        df_header = pd.read_csv(PRICES_CSV, nrows=0)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Could not find '{PRICES_CSV}'. Please ensure it exists under ml-service/data/raw/."
        )
    print("  → Detected columns:", df_header.columns.tolist())

    # 2.3 Now load using the correct column names.
    #     Replace these with whatever your CSV actually has.
    #     For example, if your header is ['Date', 'Ticker', 'Open', 'High', 'Low', 'Close', 'Volume'],
    #     use those exact names here:
    TIMESTAMP_COL = "Date"    # e.g., actual CSV header for date
    SYMBOL_COL    = "Symbol"  # e.g., actual CSV header for symbol
    CLOSE_COL     = "Close"   # e.g., actual CSV header for closing price

    print(f"Loading price data using ([{TIMESTAMP_COL}], [{SYMBOL_COL}], [{CLOSE_COL}]) …")
    df = pd.read_csv(
        PRICES_CSV,
        usecols=[TIMESTAMP_COL, SYMBOL_COL, CLOSE_COL],
        parse_dates=[TIMESTAMP_COL],
        dtype={SYMBOL_COL: "category"}
    )
    print(f"  → Loaded {df.shape[0]:,} rows for {df[SYMBOL_COL].nunique():,} unique tickers.")

    # 2.4 Rename columns to standardized names used below
    df.rename(columns={TIMESTAMP_COL: "date", SYMBOL_COL: "symbol", CLOSE_COL: "close"}, inplace=True)

    # 2.5 Sort by symbol then date to prepare for rolling computations
    df = df.sort_values(["symbol", "date"])

    # 2.6 Compute daily returns per ticker
    df["return"] = df.groupby("symbol")["close"].pct_change()

    # 2.7 Compute rolling volatility & momentum for each ticker
    def compute_feats(grp):
        grp = grp.copy()
        grp["volatility"] = grp["return"].rolling(window=VOL_WINDOW, min_periods=VOL_WINDOW).std()
        grp["momentum"]   = (grp["close"] / grp["close"].shift(MOM_WINDOW)) - 1.0
        return grp

    print("Computing rolling volatility & momentum per ticker …")
    df_feats = df.groupby("symbol", group_keys=False).apply(compute_feats)

    # 2.8 For each ticker, keep only the most recent row (latest date)
    print("Selecting latest row per ticker …")
    latest = df_feats.sort_values("date").groupby("symbol").tail(1)

    # 2.9 Extract symbol, volatility, momentum; drop any NaNs
    price_features = latest[["symbol", "volatility", "momentum"]].dropna(subset=["volatility", "momentum"])
    print(f"  → {price_features.shape[0]:,} tickers have full VOL & MOM data (≥ {VOL_WINDOW} days history).")

    # 2.10 Save to CSV
    print(f"Saving price features to:\n  {PRICE_FEATURES_CSV}")
    price_features.to_csv(PRICE_FEATURES_CSV, index=False)
    print("Done: 'price_features.csv' created under data/processed/.")

if __name__ == "__main__":
    main()
