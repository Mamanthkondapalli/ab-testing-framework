# A/B Testing & KPI Optimization Framework

A reusable Python framework for designing, running, and reporting on A/B experiments — covering sample size calculation, hypothesis testing (t-test, chi-square, Mann-Whitney), confidence intervals, and HTML/CSV report generation.

## Architecture

```
Experiment Config  →  Sample Size Calc  →  Data Simulation  →  Statistical Tests  →  Reports & Visualizations
  (metric, MDE,        (power analysis)      (control /           (t-test /             (HTML dashboard,
   alpha, power)                              treatment)            chi2 / MWU)           CSV summary)
```

## Tech Stack

| Layer           | Tool                              |
|-----------------|-----------------------------------|
| Language        | Python 3.10+                      |
| Statistics      | SciPy, Statsmodels                |
| Data            | Pandas, NumPy                     |
| Visualization   | Plotly, Matplotlib                |
| Reporting       | Jinja2 (HTML), CSV                |

## Project Structure

```
ab-testing-framework/
├── src/
│   ├── experiment.py         # Experiment config dataclass + data simulation
│   ├── sample_size.py        # Power analysis & sample size calculator
│   ├── statistical_tests.py  # t-test, chi-square, Mann-Whitney U
│   ├── reporting.py          # HTML + CSV report generator
│   └── visualizations.py     # Distribution plots, p-value charts
├── examples/
│   ├── conversion_rate_test.py  # Binary metric (click-through rate)
│   ├── revenue_test.py          # Continuous metric (revenue per user)
│   └── engagement_test.py       # Non-normal metric (session duration)
├── outputs/                  # Generated reports (gitignored)
├── requirements.txt
└── Makefile
```

## Statistical Tests

| Metric Type      | Test Used          | When to Use                          |
|------------------|--------------------|--------------------------------------|
| Conversion rate  | Chi-square / Z-test | Binary outcomes (click, purchase)   |
| Revenue / spend  | Welch's t-test     | Continuous, approximately normal     |
| Session duration | Mann-Whitney U     | Non-normal / heavy-tailed metrics    |

## Features

- **Sample size calculator** — MDE, alpha, power → minimum n per group
- **Sequential testing guard** — warns on peeking before target n reached
- **Multiple comparison correction** — Bonferroni for multi-variant tests
- **Confidence interval reporting** — effect size with 95% CI
- **HTML report** — shareable experiment summary with charts
- **CSV export** — raw results for stakeholder import into Excel / Power BI

## Quick Start

```bash
pip install -r requirements.txt

# Run all example experiments
make examples

# Or run a specific example
python examples/conversion_rate_test.py
python examples/revenue_test.py
python examples/engagement_test.py
```

## Example Output

```
============================================================
EXPERIMENT: Homepage CTA Button Color Test
============================================================
Metric          : Conversion Rate
Control         : 5.20%   (n=5,000)
Treatment       : 6.31%   (n=5,000)
Absolute Uplift : +1.11 pp
Relative Uplift : +21.4%
95% CI          : [+0.42 pp, +1.80 pp]
p-value         : 0.0021
Result          : SIGNIFICANT ✓  (α=0.05)
Recommendation  : SHIP — treatment outperforms control
============================================================
```
