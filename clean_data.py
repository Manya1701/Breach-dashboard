"""
clean_data.py
Takes the raw, messy breach dataset and produces an analysis-ready cleaned
version. This is the real "cleaned real-world-style data with Pandas" work
your CV bullet describes.

Cleaning steps:
  1. Strip stray whitespace from text columns
  2. Standardize casing (Title Case) on sector / attack_type
  3. Parse the mixed date formats into a single datetime column
  4. Handle missing records_exposed (impute with the sector's median)
  5. Drop exact duplicate rows
  6. Derive a `year` column for time-trend analysis

Run: python3 clean_data.py
Input:  data/raw_breaches.csv
Output: data/cleaned_breaches.csv + a printed before/after cleaning report
"""

import pandas as pd

RAW_PATH = "data/raw_breaches.csv"
CLEAN_PATH = "data/cleaned_breaches.csv"

# The formats present in the messy generator — tried in order per row
DATE_FORMATS = ["%Y-%m-%d", "%m/%d/%Y", "%d-%b-%Y", "%B %d, %Y"]


def parse_mixed_dates(series: pd.Series) -> pd.Series:
    def parse_one(value):
        for fmt in DATE_FORMATS:
            try:
                return pd.to_datetime(value, format=fmt)
            except (ValueError, TypeError):
                continue
        return pd.NaT  # couldn't parse with any known format

    return series.apply(parse_one)


def main():
    df = pd.read_csv(RAW_PATH)
    n_raw = len(df)

    # 1. strip whitespace on text columns
    text_cols = ["organization", "sector", "attack_type", "breach_date", "country"]
    for col in text_cols:
        df[col] = df[col].astype(str).str.strip()

    # 2. standardize casing
    df["sector"] = df["sector"].str.title()
    df["attack_type"] = df["attack_type"].str.title()

    # 3. parse mixed date formats
    df["breach_date"] = parse_mixed_dates(df["breach_date"])
    unparsed_dates = df["breach_date"].isna().sum()
    df = df.dropna(subset=["breach_date"])

    # 4. handle missing records_exposed -> impute with sector median
    df["records_exposed"] = pd.to_numeric(df["records_exposed"], errors="coerce")
    missing_before = df["records_exposed"].isna().sum()
    df["records_exposed"] = df.groupby("sector")["records_exposed"].transform(
        lambda s: s.fillna(s.median())
    )
    df["records_exposed"] = df["records_exposed"].round().astype(int)

    # 5. drop exact duplicates
    n_before_dedup = len(df)
    df = df.drop_duplicates()
    n_duplicates_removed = n_before_dedup - len(df)

    # 6. derive year for trend analysis
    df["year"] = df["breach_date"].dt.year

    df = df.sort_values("breach_date").reset_index(drop=True)
    df.to_csv(CLEAN_PATH, index=False)

    print("=" * 55)
    print("DATA CLEANING REPORT")
    print("=" * 55)
    print(f"Raw rows loaded              : {n_raw}")
    print(f"Rows with unparseable dates   : {unparsed_dates} (dropped)")
    print(f"Missing records_exposed values: {missing_before} (imputed w/ sector median)")
    print(f"Exact duplicate rows removed  : {n_duplicates_removed}")
    print(f"Final cleaned row count       : {len(df)}")
    print(f"Saved to                      : {CLEAN_PATH}")
    print("=" * 55)


if __name__ == "__main__":
    main()
