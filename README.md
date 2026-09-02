# Cybersecurity Breach Data Analysis Dashboard

Cleans a messy breach dataset with Pandas, analyzes trends by attack type,
sector, and year, and renders it as a Seaborn-charted, dashboard-style HTML
report.

This project ships with `generate_dataset.py`, which creates a **synthetic** dataset
shaped like real breach-tracking data (same sector/attack-type categories
and record-count scale used in trackers like Privacy Rights Clearinghouse),
so the cleaning pipeline has genuinely messy, realistic data to work with.

## Project structure
```
breach-dashboard/
├── generate_dataset.py   # creates a synthetic, deliberately messy raw dataset
├── clean_data.py          # Pandas cleaning: casing, dates, missing values, dupes
├── analyze.py              # KPIs, trends, top breaches
├── dashboard.py            # Seaborn charts + assembled HTML dashboard
├── requirements.txt
└── data/ , reports/        # created automatically when you run things
```

## Setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run the full pipeline
```bash
python3 generate_dataset.py   # -> data/raw_breaches.csv (messy)
python3 clean_data.py          # -> data/cleaned_breaches.csv (clean)
python3 analyze.py             # prints KPIs + trends to console
python3 dashboard.py           # -> reports/*.png + reports/dashboard.html
```
Then open `reports/dashboard.html` in any browser.

## What the cleaning step actually does
- Strips stray whitespace from text fields
- Standardizes inconsistent casing ("PHISHING" / "phishing" / "Phishing" -> "Phishing")
- Parses four different mixed date formats into one consistent datetime column
- Imputes missing `records_exposed` values using the sector's median (rather
  than dropping rows, which would bias sector totals)
- Drops exact duplicate rows
- Derives a `year` column for trend analysis

## What the dashboard shows
- KPI cards: total breaches, total records exposed, avg records/breach, top
  attack type, most affected sector
- Breaches by year (trend line)
- Breach count by attack type (bar chart)
- Total records exposed by sector (bar chart)
- Sector × attack-type heatmap
- Table of the 10 largest breaches

## Possible extensions
- Swap in a real Kaggle/HIBP-derived dataset
- Add a filter/date-range picker (would need a small Flask/Streamlit app
  instead of static HTML)
- Break out by country as well as sector
