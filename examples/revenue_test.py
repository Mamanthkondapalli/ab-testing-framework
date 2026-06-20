"""Example: Checkout flow redesign A/B test (continuous revenue metric)."""
import sys
sys.path.insert(0, 'src')
import os
import numpy as np

from experiment        import ExperimentConfig, simulate_continuous
from sample_size       import sample_size_mean, print_sample_size_report
from statistical_tests import welch_ttest
from reporting         import generate_html_report
from visualizations    import plot_distributions

os.makedirs('outputs/reports', exist_ok=True)
os.makedirs('outputs/charts',  exist_ok=True)

# ── 1. Experiment design ──────────────────────────────────────────────────────
cfg = ExperimentConfig(
    name        = 'Checkout Flow Redesign — Revenue Per User',
    metric      = 'Revenue per User ($)',
    metric_type = 'continuous',
    baseline    = 48.50,
    mde         = 0.08,   # detect 8% lift
    alpha       = 0.05,
    power       = 0.80,
)

STD = 22.0
n   = sample_size_mean(cfg.baseline, STD, cfg.mde, cfg.alpha, cfg.power)
print_sample_size_report('Continuous (Revenue)', n, cfg.alpha, cfg.power,
                         baseline_mean=f'${cfg.baseline}',
                         std=f'${STD}',
                         mde_relative=f'{cfg.mde*100:.0f}%')

# ── 2. Simulate ───────────────────────────────────────────────────────────────
MEAN_CTRL  = 48.50
MEAN_TREAT = 52.60   # +8.5% lift

control, treatment = simulate_continuous(n, MEAN_CTRL, MEAN_TREAT, STD)

# ── 3. Test ───────────────────────────────────────────────────────────────────
results = welch_ttest(control['value'].values, treatment['value'].values, cfg.alpha)

print('\n' + '='*60)
print(f"  {cfg.name}")
print('='*60)
print(f"  Control mean   : ${results['mean_control']:.2f}")
print(f"  Treatment mean : ${results['mean_treatment']:.2f}")
print(f"  Abs Uplift     : ${results['absolute_uplift']:+.2f}")
print(f"  Rel Uplift     : {results['relative_uplift']:+.1f}%")
print(f"  95% CI         : [${results['ci_95_low']:+.2f}, ${results['ci_95_high']:+.2f}]")
print(f"  p-value        : {results['p_value']}")
print(f"  Significant    : {'YES ✓' if results['significant'] else 'NO ✗'}")
print('='*60)

# ── 4. Report ─────────────────────────────────────────────────────────────────
kpis = {
    'Control Mean':   f"${results['mean_control']:.2f}",
    'Treatment Mean': f"${results['mean_treatment']:.2f}",
    'Uplift':         f"{results['relative_uplift']:+.1f}%",
    '95% CI':         f"[${results['ci_95_low']:+.2f}, ${results['ci_95_high']:+.2f}]",
    'p-value':        str(results['p_value']),
}
generate_html_report(cfg.name, results, kpis)
plot_distributions(
    control['value'].values, treatment['value'].values,
    cfg.metric, cfg.name, 'outputs/charts/revenue_distributions.html',
)
print('Report and chart saved to outputs/')
