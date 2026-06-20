"""Example: Homepage CTA button color A/B test (binary conversion metric)."""
import sys
sys.path.insert(0, 'src')
import os
import numpy as np

from experiment       import ExperimentConfig, simulate_binary
from sample_size      import sample_size_proportion, print_sample_size_report
from statistical_tests import chi_square_test
from reporting        import generate_html_report, generate_csv_summary
from visualizations   import plot_conversion_rates

os.makedirs('outputs/reports', exist_ok=True)
os.makedirs('outputs/charts',  exist_ok=True)

# ── 1. Experiment design ──────────────────────────────────────────────────────
cfg = ExperimentConfig(
    name        = 'Homepage CTA Button Color Test',
    metric      = 'Conversion Rate',
    metric_type = 'binary',
    baseline    = 0.052,   # 5.2% current CVR
    mde         = 0.01,    # detect +1pp lift
    alpha       = 0.05,
    power       = 0.80,
)

n = sample_size_proportion(cfg.baseline, cfg.mde, cfg.alpha, cfg.power)
print_sample_size_report('Binary (Conversion Rate)', n, cfg.alpha, cfg.power,
                         baseline_cvr=f'{cfg.baseline*100:.1f}%',
                         mde=f'+{cfg.mde*100:.1f}pp')

# ── 2. Simulate experiment data ───────────────────────────────────────────────
P_CONTROL   = 0.052
P_TREATMENT = 0.063   # 21% relative uplift

control, treatment = simulate_binary(n, P_CONTROL, P_TREATMENT)

# ── 3. Statistical test ───────────────────────────────────────────────────────
results = chi_square_test(
    n_control     = len(control),
    conv_control  = control['converted'].sum(),
    n_treatment   = len(treatment),
    conv_treatment= treatment['converted'].sum(),
    alpha         = cfg.alpha,
)

print('\n' + '='*60)
print(f"  {cfg.name}")
print('='*60)
print(f"  Metric         : {cfg.metric}")
print(f"  Control CVR    : {results['rate_control']}%   (n={results['n_control']:,})")
print(f"  Treatment CVR  : {results['rate_treatment']}%   (n={results['n_treatment']:,})")
print(f"  Abs Uplift     : {results['absolute_uplift_pp']:+.2f}pp")
print(f"  Rel Uplift     : {results['relative_uplift_pct']:+.1f}%")
print(f"  95% CI         : [{results['ci_95_low_pp']:+.2f}pp, {results['ci_95_high_pp']:+.2f}pp]")
print(f"  p-value        : {results['p_value']}")
print(f"  Significant    : {'YES ✓' if results['significant'] else 'NO ✗'}")
print('='*60)

# ── 4. Report & charts ────────────────────────────────────────────────────────
kpis = {
    'Control CVR':    f"{results['rate_control']}%",
    'Treatment CVR':  f"{results['rate_treatment']}%",
    'Absolute Uplift': f"{results['absolute_uplift_pp']:+.2f}pp",
    'Relative Uplift': f"{results['relative_uplift_pct']:+.1f}%",
    'p-value':        str(results['p_value']),
}
report_path = generate_html_report(cfg.name, results, kpis)
print(f'\nHTML report: {report_path}')

plot_conversion_rates(
    P_CONTROL, P_TREATMENT,
    results['ci_95_low_pp'] / 100, results['ci_95_high_pp'] / 100,
    cfg.name, 'outputs/charts/cta_color_conversion.html',
)
