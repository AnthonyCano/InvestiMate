# File: ml-service/scripts/merge_all_features.py

import pandas as pd
import os

# ===========================
# 1) HARDCODED FILEPATHS
# ===========================
PROJECT_ROOT        = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PROCESSED_DIR       = os.path.join(PROJECT_ROOT, "data", "processed")

FUND_CLEAN_CSV      = os.path.join(PROCESSED_DIR, "fundamentals_clean.csv")
PRICE_FEATS_CSV     = os.path.join(PROCESSED_DIR, "price_features.csv")
COMBINED_OUTPUT_CSV = os.path.join(PROCESSED_DIR, "combined_data.csv")


def main():
    # 1) Ensure processed directory exists
    os.makedirs(PROCESSED_DIR, exist_ok=True)

    # 2) Load cleaned fundamentals
    print(f"Loading fundamentals from:\n  {FUND_CLEAN_CSV}")
    try:
        df_fund = pd.read_csv(FUND_CLEAN_CSV, dtype={"company_id": str})
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Could not find '{FUND_CLEAN_CSV}'. Ensure merge_fundamentals.py has run successfully."
        )
    print(f"  → Fundamentals shape: {df_fund.shape} (columns: {list(df_fund.columns)})") 

    # 3) Load price features
    print(f"Loading price features from:\n  {PRICE_FEATS_CSV}")
    try:
        df_price = pd.read_csv(PRICE_FEATS_CSV, dtype={"symbol": str})
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Could not find '{PRICE_FEATS_CSV}'. Ensure compute_price_features.py has run successfully."
        )
    print(f"  → Price features shape: {df_price.shape} (columns: {list(df_price.columns)})") 

    # 4) Align keys: fundamentals use 'company_id', price features use 'symbol' 
    #    We assume company_id == ticker symbol, so rename for merging
    df_fund_renamed = df_fund.rename(columns={"company_id": "symbol"})
    print(f"Renamed 'company_id' to 'symbol' in fundamentals. New columns: {list(df_fund_renamed.columns)}")

    # 5) Merge on 'symbol' with inner join (keep only tickers present in both)
    print("Merging fundamentals with price features on 'symbol' …")
    df_combined = pd.merge(
        df_fund_renamed,
        df_price,
        on="symbol",
        how="inner",
        validate="one_to_one"   # ensures no duplicates on either side 
    )
    print(f"  → After merge: {df_combined.shape[0]:,} rows × {df_combined.shape[1]:,} columns")

    # 6) Optional: Reorder columns so that 'symbol' comes first, then fundamentals, then price features
    cols = ["symbol"] + \
           [c for c in df_combined.columns if c not in ["symbol","volatility","momentum"]] + \
           ["volatility","momentum"]
    df_combined = df_combined[cols]

    # 7) Save combined dataset
    print(f"Saving combined dataset to:\n  {COMBINED_OUTPUT_CSV}")
    df_combined.to_csv(COMBINED_OUTPUT_CSV, index=False)
    print("Done: 'combined_data.csv' created under data/processed/.")


if __name__ == "__main__":
    main()
