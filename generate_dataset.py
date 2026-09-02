"""
generate_dataset.py
Generates a SYNTHETIC data breach dataset shaped like real-world breach
trackers (sector categories, attack-type taxonomy, and record-count scale
modeled on public breach reporting, e.g. Privacy Rights Clearinghouse /
VERIS-style categories). This is not scraped or copied from any real
source — it's randomly generated so the cleaning/analysis pipeline has
realistic, genuinely messy data to work with.

Deliberately injects real-world messiness so clean_data.py has actual work
to do:
  - inconsistent casing ("phishing" vs "Phishing" vs "PHISHING")
  - mixed date formats
  - missing values in records_exposed
  - stray whitespace
  - duplicate rows

Run: python3 generate_dataset.py
Output: data/raw_breaches.csv
"""

import csv
import random
from datetime import date, timedelta

random.seed(42)

SECTORS = ["Healthcare", "Finance", "Retail", "Government", "Education", "Technology"]
ATTACK_TYPES = [
    "Phishing", "Ransomware", "Malware", "Insider Threat",
    "Unpatched Vulnerability", "Physical Theft", "Misconfiguration",
]
COUNTRIES = ["USA", "UK", "India", "Germany", "Canada", "Australia", "Brazil"]

# Rough relative severity by attack type -> influences records_exposed scale
SEVERITY_SCALE = {
    "Ransomware": (50_000, 5_000_000),
    "Unpatched Vulnerability": (20_000, 3_000_000),
    "Phishing": (500, 500_000),
    "Malware": (1_000, 800_000),
    "Insider Threat": (100, 200_000),
    "Physical Theft": (50, 50_000),
    "Misconfiguration": (10_000, 2_000_000),
}


def random_date(start_year=2018, end_year=2025):
    start = date(start_year, 1, 1)
    end = date(end_year, 12, 31)
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))


def messy_case(s: str) -> str:
    """Randomly mangle casing to simulate inconsistent data entry."""
    roll = random.random()
    if roll < 0.15:
        return s.upper()
    elif roll < 0.30:
        return s.lower()
    elif roll < 0.35:
        return f"  {s}  "  # stray whitespace
    return s


def messy_date_format(d: date) -> str:
    """Randomly pick among a few common but inconsistent date formats."""
    fmt = random.choice(["%Y-%m-%d", "%m/%d/%Y", "%d-%b-%Y", "%B %d, %Y"])
    return d.strftime(fmt)


def generate_row(row_id):
    sector = messy_case(random.choice(SECTORS))
    attack_type = messy_case(random.choice(ATTACK_TYPES))
    country = random.choice(COUNTRIES)
    breach_date = random_date()
    date_str = messy_date_format(breach_date)

    clean_attack = attack_type.strip().title()
    low, high = SEVERITY_SCALE.get(clean_attack, (1_000, 100_000))
    records_exposed = random.randint(low, high)

    # ~6% missing records_exposed to simulate real-world reporting gaps
    if random.random() < 0.06:
        records_exposed = ""

    org_name = f"Org_{row_id:04d}"

    return {
        "organization": org_name,
        "sector": sector,
        "attack_type": attack_type,
        "breach_date": date_str,
        "records_exposed": records_exposed,
        "country": country,
    }


def main(n_rows=650, out_path="data/raw_breaches.csv"):
    rows = [generate_row(i) for i in range(n_rows)]

    # inject a handful of exact duplicate rows, another real-world artifact
    duplicates = random.sample(rows, k=20)
    rows.extend(duplicates)
    random.shuffle(rows)

    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "organization", "sector", "attack_type", "breach_date",
            "records_exposed", "country",
        ])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Generated {len(rows)} rows (including {len(duplicates)} intentional "
          f"duplicates) -> {out_path}")


if __name__ == "__main__":
    main()
