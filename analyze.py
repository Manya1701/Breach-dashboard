"""
analyze.py
Runs the actual analysis on the cleaned dataset: KPIs, breach trends by
year, impact by sector and attack type, and the top 10 largest breaches.
Used both for a quick CLI summary and as the data source for dashboard.py.

Run: python3 analyze.py
"""

import pandas as pd

CLEAN_PATH = "data/cleaned_breaches.csv"


def load_clean_data() -> pd.DataFrame:
    df = pd.read_csv(CLEAN_PATH, parse_dates=["breach_date"])
    return df


def compute_kpis(df: pd.DataFrame) -> dict:
    return {
        "total_breaches": len(df),
        "total_records_exposed": int(df["records_exposed"].sum()),
        "avg_records_per_breach": int(df["records_exposed"].mean()),
        "most_common_attack_type": df["attack_type"].value_counts().idxmax(),
        "most_affected_sector": df.groupby("sector")["records_exposed"].sum().idxmax(),
        "date_range": f"{df['breach_date'].min().date()} to {df['breach_date'].max().date()}",
    }


def breaches_by_year(df: pd.DataFrame) -> pd.Series:
    return df.groupby("year").size().sort_index()


def attack_type_counts(df: pd.DataFrame) -> pd.Series:
    return df["attack_type"].value_counts()


def records_by_sector(df: pd.DataFrame) -> pd.Series:
    return df.groupby("sector")["records_exposed"].sum().sort_values(ascending=False)


def sector_attack_heatmap_data(df: pd.DataFrame) -> pd.DataFrame:
    return pd.crosstab(df["sector"], df["attack_type"])


def top_10_breaches(df: pd.DataFrame) -> pd.DataFrame:
    return df.nlargest(10, "records_exposed")[
        ["organization", "sector", "attack_type", "breach_date", "records_exposed"]
    ]


def main():
    df = load_clean_data()
    kpis = compute_kpis(df)

    print("=" * 55)
    print("BREACH DATA ANALYSIS SUMMARY")
    print("=" * 55)
    for k, v in kpis.items():
        print(f"{k:28}: {v}")

    print("\nBreaches by year:")
    print(breaches_by_year(df).to_string())

    print("\nTop attack types:")
    print(attack_type_counts(df).to_string())

    print("\nRecords exposed by sector:")
    print(records_by_sector(df).to_string())

    print("\nTop 10 largest breaches:")
    print(top_10_breaches(df).to_string(index=False))
    print("=" * 55)


if __name__ == "__main__":
    main()
