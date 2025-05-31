# scripts/merge_fundamentals.py

import pandas as pd
import os

# === CONFIGURATION ===
RAW_DIR = os.path.join("data", "raw")
INDICATORS_CSV = os.path.join(RAW_DIR, "indicators_by_company.csv")
COMPANIES_CSV   = os.path.join(RAW_DIR, "companies.csv")

PROCESSED_DIR = os.path.join("data", "processed")
os.makedirs(PROCESSED_DIR, exist_ok=True)
FUNDAMENTALS_CLEAN_CSV = os.path.join(PROCESSED_DIR, "fundamentals_clean.csv")

def main():
    print(f"Loading indicators from {INDICATORS_CSV} ...")
    ind = pd.read_csv(
        INDICATORS_CSV,
        parse_dates=["periodEnding"],
        dtype={"symbol": str, "indicator": str, "value": float}
    )
    print(f"  → {ind.shape[0]} rows for {ind['symbol'].nunique()} tickers.")

    print(f"Loading companies metadata from {COMPANIES_CSV} ...")
    comp = pd.read_csv(
        COMPANIES_CSV,
        dtype={"symbol": str, "name": str, "exchange": str, "sector": str, "industry": str}
    )
    print(f"  → {comp.shape[0]} companies in metadata.")

    # 1) Keep only the latest periodEnding for each (symbol, indicator)
    print("Selecting latest indicator row for each (symbol, indicator) ...")
    ind_sorted = ind.sort_values("periodEnding")
    ind_latest = ind_sorted.groupby(["symbol", "indicator"], as_index=False).tail(1)

    # 2) Pivot so each 'indicator' is its own column
    print("Pivoting indicators into wide format ...")
    features = ind_latest.pivot_table(
        index="symbol",
        columns="indicator",
        values="value"
    ).reset_index()
    # Now features.columns = ['symbol', <indicator1>, <indicator2>, ...]

    # 3) Merge in company metadata (sector, industry, exchange, name)
    print("Merging with company metadata ...")
    comp_small = comp[["symbol", "name", "exchange", "sector", "industry"]]
    merged = pd.merge(
        features,
        comp_small,
        on="symbol",
        how="left"
    )
    print(f"  → After merge: {merged.shape[0]} tickers × {merged.shape[1]} columns.")

    # 4) Filter to U.S. exchanges (NYSE, NASDAQ)
    print("Filtering to U.S. tickers (NYSE or NASDAQ) ...")
    us_mask = merged["exchange"].isin(["NYSE", "NASDAQ"])
    merged_us = merged[us_mask].copy()
    print(f"  → {merged_us.shape[0]} tickers on NYSE/NASDAQ remain.")

    # 5) Write out the cleaned fundamentals
    print(f"Saving cleaned fundamentals to {FUNDAMENTALS_CLEAN_CSV} ...")
    merged_us.to_csv(FUNDAMENTALS_CLEAN_CSV, index=False)
    print("Done.")

if __name__ == "__main__":
    main()
