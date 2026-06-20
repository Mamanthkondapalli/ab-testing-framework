"""Example: Push notification timing test (skewed session duration metric)."""
import sys
sys.path.insert(0, 'src')
import os
import numpy as np

from experiment        import ExperimentConfig, simulate_skewed
from sample_size       import print_sample_size_report
from statistical_tests import mann_whitney_test, bonferroni_correction
from reporting         import generate_html_report, generate_csv_summary
from visualizations    import plot_distributions

os.makedirs('outputs/reports', exist_ok=True)
os.makedirs('outputs/charts',  exist_ok=True)

cfg = ExperimentConfig(
    name        = 'Push Notification Timing — Session Duration',
    metric      = 'Session Duration (minutes)',
    metric_type = 'count',
    baseline    = 4.2,
    mde         = 0.15,
    alpha       = 0.05,
    power       = 0.80,
    n_per_group = 5_000,
)
print_sample_size_report('Non-normal / Skewed (Mann-Whitney)', cfg.n_per_group,
                         cfg.alpha, cfg.power,
                         note='Set manually; use bootstrap for precise estimate')

control, treatment = simulate_skewed(cfg.n_per_group, 1.40, 1.55, scale=0.70)

results = mann_whitney_test(control['value'].values, treatment['value'].values, cfg.alpha)

print('\n' + '='*60)
print(f"  {cfg.name}")
print('='*60)
print(f"  Median Control   : {results['median_control']:.2f} min")
print(f"  Median Treatment : {results['median_treatment']:.2f} min")
print(f"  Median Uplift    : {results['median_uplift']:+.2f} min")
print(f"  CLES             : {results['cles']}  (P(treat>ctrl))")
print(f"  p-value          : {results['p_value']}")
print(f"  Significant      : {'YES ✓' if results['significant'] else 'NO ✗'}")
print('='*60)

# Multi-variant Bonferroni demo
sim_p_values = [results['p_value'], 0.032, 0.18]
bonf = bonferroni_correction(sim_p_values, alpha=cfg.alpha)
print('\nBonferroni correction (3 variants):')
for b in bonf:
    print(f"  Variant {b['variant']}: p={b['p_value']} | adj_alpha={b['adjusted_alpha']} | sig={b['significant']}")

kpis = {
    'Median Control':   f"{results['median_control']:.2f} min",
    'Median Treatment': f"{results['median_treatment']:.2f} min",
    'Uplift':           f"{results['median_uplift']:+.2f} min",
    'CLES':             str(results['cles']),
    'p-value':          str(results['p_value']),
}
generate_html_report(cfg.name, results, kpis)
plot_distributions(
    control['value'].values, treatment['value'].values,
    cfg.metric, cfg.name, 'outputs/charts/session_duration_distributions.html',
)
print('Report and chart saved to outputs/')
