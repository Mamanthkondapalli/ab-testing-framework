"""Generate HTML experiment reports and CSV summaries."""
import os
import csv
from datetime import datetime


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>A/B Test Report — {name}</title>
<style>
  body {{ font-family: Segoe UI, Arial, sans-serif; background: #f8f9fa; margin: 0; padding: 20px; }}
  .container {{ max-width: 900px; margin: auto; background: white; border-radius: 10px;
               box-shadow: 0 2px 12px rgba(0,0,0,0.1); padding: 30px; }}
  h1 {{ color: #1565C0; border-bottom: 2px solid #E3F2FD; padding-bottom: 10px; }}
  .kpi-grid {{ display: flex; gap: 16px; flex-wrap: wrap; margin: 20px 0; }}
  .kpi {{ background: #F5F7FA; border-radius: 8px; padding: 16px 20px; flex: 1; min-width: 140px; }}
  .kpi .label {{ color: #666; font-size: 12px; margin: 0 0 6px; }}
  .kpi .value {{ color: #1565C0; font-size: 22px; font-weight: bold; margin: 0; }}
  .result-badge {{ display: inline-block; padding: 6px 16px; border-radius: 20px;
                   font-weight: bold; font-size: 14px; margin: 16px 0; }}
  .sig   {{ background: #E8F5E9; color: #2E7D32; }}
  .insig {{ background: #FFF3E0; color: #E65100; }}
  table {{ width: 100%; border-collapse: collapse; margin: 16px 0; font-size: 14px; }}
  th {{ background: #1565C0; color: white; padding: 10px 14px; text-align: left; }}
  td {{ padding: 9px 14px; border-bottom: 1px solid #EEE; }}
  tr:nth-child(even) {{ background: #F9F9F9; }}
  .recommendation {{ background: #E8F5E9; border-left: 4px solid #43A047;
                     padding: 14px 18px; border-radius: 0 8px 8px 0; margin: 20px 0; }}
</style>
</head>
<body>
<div class="container">
  <h1>A/B Test Report</h1>
  <p style="color:#888; font-size:13px;">Experiment: <strong>{name}</strong> &nbsp;|&nbsp; Generated: {date}</p>

  <div class="kpi-grid">{kpi_blocks}</div>

  <div class="result-badge {badge_class}">{result_label}</div>

  <h3>Detailed Results</h3>
  <table>{table_rows}</table>

  <div class="recommendation">
    <strong>Recommendation:</strong> {recommendation}
  </div>
</div>
</body>
</html>
"""


def _kpi_block(label, value):
    return f'<div class="kpi"><p class="label">{label}</p><p class="value">{value}</p></div>'


def _table_rows(results: dict) -> str:
    rows = ''
    for k, v in results.items():
        rows += f'<tr><td><strong>{k}</strong></td><td>{v}</td></tr>'
    return rows


def recommendation(results: dict) -> str:
    if results.get('significant'):
        uplift = results.get('relative_uplift_pct') or results.get('relative_uplift')
        return (f'<strong>SHIP</strong> — Treatment shows a statistically significant uplift '
                f'of {uplift}% (p={results["p_value"]}). Roll out to 100% of users.')
    else:
        return (f'<strong>DO NOT SHIP</strong> — No statistically significant difference detected '
                f'(p={results["p_value"]} > α={results["alpha"]}). Extend the experiment or '
                f'rethink the treatment.')


def generate_html_report(
    experiment_name: str,
    results: dict,
    kpis: dict,
    output_dir: str = 'outputs/reports',
) -> str:
    os.makedirs(output_dir, exist_ok=True)
    sig        = results.get('significant', False)
    badge      = 'sig' if sig else 'insig'
    label      = 'SIGNIFICANT ✓' if sig else 'NOT SIGNIFICANT ✗'
    kpi_html   = ''.join(_kpi_block(k, v) for k, v in kpis.items())
    table_html = _table_rows(results)
    rec        = recommendation(results)
    html       = HTML_TEMPLATE.format(
        name=experiment_name,
        date=datetime.now().strftime('%Y-%m-%d %H:%M'),
        kpi_blocks=kpi_html,
        badge_class=badge,
        result_label=label,
        table_rows=table_html,
        recommendation=rec,
    )
    path = f"{output_dir}/{experiment_name.replace(' ', '_')}.html"
    with open(path, 'w') as f:
        f.write(html)
    return path


def generate_csv_summary(
    results_list: list[dict],
    output_dir: str = 'outputs/reports',
) -> str:
    os.makedirs(output_dir, exist_ok=True)
    path = f'{output_dir}/experiment_summary.csv'
    if not results_list:
        return path
    with open(path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=results_list[0].keys())
        writer.writeheader()
        writer.writerows(results_list)
    return path
