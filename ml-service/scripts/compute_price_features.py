# File: ml-service/scripts/merge_fundamentals.py

import pandas as pd
import os

# ===========================
# 1) HARDCODED FILEPATHS
# ===========================
PROJECT_ROOT       = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RAW_DIR            = os.path.join(PROJECT_ROOT, "data", "raw")
PROCESSED_DIR      = os.path.join(PROJECT_ROOT, "data", "processed")

# Wide‐by‐year fundamentals (2010–2016)
INDICATORS_CSV     = os.path.join(RAW_DIR, "indicators_by_company.csv")
# Company metadata (only has company_id, name_latest, names_previous)
COMPANIES_CSV      = os.path.join(RAW_DIR, "companies.csv")

# Output: cleaned fundamentals
FUNDAMENTALS_CLEAN = os.path.join(PROCESSED_DIR, "fundamentals_clean.csv")


def main():
    # 1) Ensure the processed directory exists
    os.makedirs(PROCESSED_DIR, exist_ok=True)

    # 2) Load the wide-format fundamentals CSV
    print(f"Loading indicators (wide-by-year) from:\n  {INDICATORS_CSV}")
    # Expect columns: company_id, indicator_id, 2010,2011,2012,2013,2014,2015,2016
    try:
        df_ind = pd.read_csv(
            INDICATORS_CSV,
            dtype={"company_id": str, "indicator_id": str}
        )
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Could not find '{INDICATORS_CSV}'. Make sure the file exists under ml-service/data/raw/."
        )

    print(f"  → Read {df_ind.shape[0]:,} rows, columns = {list(df_ind.columns)}")

    # 3) Extract the 2016 values for each (company_id, indicator_id)
    if "2016" not in df_ind.columns:
        raise KeyError(
            f"Expected a column named '2016' in {INDICATORS_CSV}, but it was not found.\n"
            f"Available columns: {list(df_ind.columns)}"
        )
    df_2016 = df_ind[["company_id", "indicator_id", "2016"]].copy()
    df_2016.rename(columns={"2016": "value_2016"}, inplace=True)
    print("  → Extracted 2016 values into 'value_2016' column.")

    # 4) Pivot so each indicator_id becomes its own column (with the 2016 value)
    print("Pivoting so that each indicator_id is a column (2016 values) …")
    df_wide = df_2016.pivot_table(
        index="company_id",
        columns="indicator_id",
        values="value_2016"
    ).reset_index()
    df_wide.columns.name = None  # remove the pivot_table name
    print(f"  → Pivoted DataFrame has shape {df_wide.shape}")

    # 5) Load company metadata from companies.csv
    print(f"Loading company metadata from:\n  {COMPANIES_CSV}")
    try:
        df_comp = pd.read_csv(
            COMPANIES_CSV,
            dtype={"company_id": str, "name_latest": str, "names_previous": str}
        )
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Could not find '{COMPANIES_CSV}'. Ensure it exists under ml-service/data/raw/."
        )

    print(f"  → Read {df_comp.shape[0]:,} rows, columns = {list(df_comp.columns)}")

    # 6) Merge pivoted fundamentals with company metadata on company_id
    print("Merging pivoted fundamentals with company metadata …")
    df_merged = pd.merge(
        df_wide,
        df_comp[["company_id", "name_latest", "names_previous"]],
        on="company_id",
        how="left"
    )
    print(f"  → After merge: {df_merged.shape[0]:,} rows × {df_merged.shape[1]:,} columns")

    # 7) (No filtering step – no exchange column exists)
    # If you later add exchange/sector data elsewhere, you can filter accordingly.

    # 8) Save the cleaned fundamentals to CSV
    print(f"Saving cleaned fundamentals to:\n  {FUNDAMENTALS_CLEAN}")
    df_merged.to_csv(FUNDAMENTALS_CLEAN, index=False)
    print("Done: 'fundamentals_clean.csv' created under data/processed/.")


if __name__ == "__main__":
    main()
