"""
dashboard.py
Builds the Seaborn visualizations and assembles them, together with the
KPIs from analyze.py, into a single static HTML dashboard — this is the
"dashboard-style report" your CV bullet describes.

Run: python3 dashboard.py
Output: reports/*.png  and  reports/dashboard.html  (open in any browser)
"""

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from analyze import (
    load_clean_data, compute_kpis, breaches_by_year, attack_type_counts,
    records_by_sector, sector_attack_heatmap_data, top_10_breaches,
)

REPORTS_DIR = "reports"
sns.set_theme(style="whitegrid")


def plot_breaches_by_year(df, out_dir):
    data = breaches_by_year(df)
    plt.figure(figsize=(7, 4))
    sns.lineplot(x=data.index, y=data.values, marker="o", color="#1F3864")
    plt.title("Breaches Reported by Year")
    plt.xlabel("Year")
    plt.ylabel("Number of Breaches")
    plt.tight_layout()
    path = os.path.join(out_dir, "breaches_by_year.png")
    plt.savefig(path)
    plt.close()
    return path


def plot_attack_type_counts(df, out_dir):
    data = attack_type_counts(df)
    plt.figure(figsize=(7, 4))
    sns.barplot(x=data.values, y=data.index, hue=data.index, palette="rocket", legend=False)
    plt.title("Breach Count by Attack Type")
    plt.xlabel("Number of Breaches")
    plt.tight_layout()
    path = os.path.join(out_dir, "attack_type_counts.png")
    plt.savefig(path)
    plt.close()
    return path


def plot_records_by_sector(df, out_dir):
    data = records_by_sector(df)
    plt.figure(figsize=(7, 4))
    sns.barplot(x=data.values / 1_000_000, y=data.index, hue=data.index, palette="mako", legend=False)
    plt.title("Total Records Exposed by Sector")
    plt.xlabel("Records Exposed (millions)")
    plt.tight_layout()
    path = os.path.join(out_dir, "records_by_sector.png")
    plt.savefig(path)
    plt.close()
    return path


def plot_sector_attack_heatmap(df, out_dir):
    data = sector_attack_heatmap_data(df)
    plt.figure(figsize=(8, 5))
    sns.heatmap(data, annot=True, fmt="d", cmap="Blues")
    plt.title("Breach Count: Sector vs Attack Type")
    plt.tight_layout()
    path = os.path.join(out_dir, "sector_attack_heatmap.png")
    plt.savefig(path)
    plt.close()
    return path


def build_html(kpis, top10_df, image_paths, out_path):
    top10_rows = "".join(
        f"<tr><td>{r.organization}</td><td>{r.sector}</td><td>{r.attack_type}</td>"
        f"<td>{r.breach_date.date()}</td><td>{r.records_exposed:,}</td></tr>"
        for r in top10_df.itertuples()
    )

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Cybersecurity Breach Data Analysis Dashboard</title>
<style>
  body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f4f6f8; margin: 0; padding: 24px; color: #222; }}
  h1 {{ color: #1F3864; }}
  .kpi-row {{ display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 28px; }}
  .kpi-card {{ background: white; border-radius: 8px; padding: 16px 20px; box-shadow: 0 1px 4px rgba(0,0,0,0.1); flex: 1; min-width: 180px; }}
  .kpi-card .label {{ font-size: 13px; color: #666; text-transform: uppercase; }}
  .kpi-card .value {{ font-size: 22px; font-weight: bold; color: #1F3864; margin-top: 4px; }}
  .charts {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
  .chart-card {{ background: white; border-radius: 8px; padding: 12px; box-shadow: 0 1px 4px rgba(0,0,0,0.1); }}
  .chart-card img {{ width: 100%; border-radius: 4px; }}
  table {{ width: 100%; border-collapse: collapse; margin-top: 12px; background: white; }}
  th, td {{ padding: 8px 12px; text-align: left; border-bottom: 1px solid #eee; }}
  th {{ background: #1F3864; color: white; }}
  section {{ margin-bottom: 32px; }}
</style>
</head>
<body>
  <h1>Cybersecurity Breach Data Analysis Dashboard</h1>
  <p style="color:#666;">Data period: {kpis['date_range']} &nbsp;|&nbsp; Synthetic demo dataset</p>

  <div class="kpi-row">
    <div class="kpi-card"><div class="label">Total Breaches</div><div class="value">{kpis['total_breaches']:,}</div></div>
    <div class="kpi-card"><div class="label">Total Records Exposed</div><div class="value">{kpis['total_records_exposed']:,}</div></div>
    <div class="kpi-card"><div class="label">Avg Records / Breach</div><div class="value">{kpis['avg_records_per_breach']:,}</div></div>
    <div class="kpi-card"><div class="label">Top Attack Type</div><div class="value">{kpis['most_common_attack_type']}</div></div>
    <div class="kpi-card"><div class="label">Most Affected Sector</div><div class="value">{kpis['most_affected_sector']}</div></div>
  </div>

  <section class="charts">
    <div class="chart-card"><img src="{os.path.basename(image_paths[0])}"></div>
    <div class="chart-card"><img src="{os.path.basename(image_paths[1])}"></div>
    <div class="chart-card"><img src="{os.path.basename(image_paths[2])}"></div>
    <div class="chart-card"><img src="{os.path.basename(image_paths[3])}"></div>
  </section>

  <section>
    <h2 style="color:#1F3864;">Top 10 Largest Breaches</h2>
    <table>
      <tr><th>Organization</th><th>Sector</th><th>Attack Type</th><th>Date</th><th>Records Exposed</th></tr>
      {top10_rows}
    </table>
  </section>
</body>
</html>
"""
    with open(out_path, "w") as f:
        f.write(html)


def main():
    os.makedirs(REPORTS_DIR, exist_ok=True)
    df = load_clean_data()
    kpis = compute_kpis(df)
    top10 = top_10_breaches(df)

    p1 = plot_breaches_by_year(df, REPORTS_DIR)
    p2 = plot_attack_type_counts(df, REPORTS_DIR)
    p3 = plot_records_by_sector(df, REPORTS_DIR)
    p4 = plot_sector_attack_heatmap(df, REPORTS_DIR)

    html_path = os.path.join(REPORTS_DIR, "dashboard.html")
    build_html(kpis, top10, [p1, p2, p3, p4], html_path)

    print(f"Charts saved to {REPORTS_DIR}/")
    print(f"Dashboard saved to {html_path} — open it in a browser")


if __name__ == "__main__":
    main()
