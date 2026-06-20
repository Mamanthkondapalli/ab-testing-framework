"""Statistical hypothesis tests for A/B experiments."""
import numpy as np
import pandas as pd
from scipy import stats
from typing import Literal


def welch_ttest(
    control: np.ndarray,
    treatment: np.ndarray,
    alpha: float = 0.05,
) -> dict:
    """Welch's t-test for continuous metrics (unequal variances)."""
    t_stat, p_value = stats.ttest_ind(treatment, control, equal_var=False)
    delta           = treatment.mean() - control.mean()
    pooled_se       = np.sqrt(control.std()**2 / len(control) +
                               treatment.std()**2 / len(treatment))
    ci_low  = delta - stats.t.ppf(1 - alpha / 2, df=len(control) + len(treatment) - 2) * pooled_se
    ci_high = delta + stats.t.ppf(1 - alpha / 2, df=len(control) + len(treatment) - 2) * pooled_se

    return {
        'test':            "Welch's t-test",
        'n_control':       len(control),
        'n_treatment':     len(treatment),
        'mean_control':    round(control.mean(),   4),
        'mean_treatment':  round(treatment.mean(), 4),
        'absolute_uplift': round(delta, 4),
        'relative_uplift': round(delta / control.mean() * 100, 2),
        'ci_95_low':       round(ci_low,  4),
        'ci_95_high':      round(ci_high, 4),
        't_statistic':     round(t_stat,  4),
        'p_value':         round(p_value, 6),
        'significant':     p_value < alpha,
        'alpha':           alpha,
    }


def chi_square_test(
    n_control:       int,
    conv_control:    int,
    n_treatment:     int,
    conv_treatment:  int,
    alpha:           float = 0.05,
) -> dict:
    """Chi-square test for binary conversion metrics."""
    table   = [[conv_control,   n_control   - conv_control],
               [conv_treatment, n_treatment - conv_treatment]]
    chi2, p, _, _ = stats.chi2_contingency(table)

    p_ctrl  = conv_control   / n_control
    p_treat = conv_treatment / n_treatment
    delta   = p_treat - p_ctrl

    # Wilson CI for each proportion then combine (conservative)
    z     = stats.norm.ppf(1 - alpha / 2)
    se    = np.sqrt(p_ctrl * (1 - p_ctrl) / n_control +
                    p_treat * (1 - p_treat) / n_treatment)
    ci_low  = delta - z * se
    ci_high = delta + z * se

    return {
        'test':                 'Chi-square',
        'n_control':            n_control,
        'n_treatment':          n_treatment,
        'rate_control':         round(p_ctrl  * 100, 2),
        'rate_treatment':       round(p_treat * 100, 2),
        'absolute_uplift_pp':   round(delta   * 100, 4),
        'relative_uplift_pct':  round(delta / p_ctrl * 100, 2),
        'ci_95_low_pp':         round(ci_low  * 100, 4),
        'ci_95_high_pp':        round(ci_high * 100, 4),
        'chi2_statistic':       round(chi2, 4),
        'p_value':              round(p,    6),
        'significant':          p < alpha,
        'alpha':                alpha,
    }


def mann_whitney_test(
    control:   np.ndarray,
    treatment: np.ndarray,
    alpha:     float = 0.05,
) -> dict:
    """Mann-Whitney U test for non-normal / skewed metrics."""
    u_stat, p_value = stats.mannwhitneyu(treatment, control, alternative='two-sided')
    n1, n2   = len(control), len(treatment)
    # Common Language Effect Size
    cles     = u_stat / (n1 * n2)

    return {
        'test':          'Mann-Whitney U',
        'n_control':     n1,
        'n_treatment':   n2,
        'median_control':   round(np.median(control),   4),
        'median_treatment': round(np.median(treatment), 4),
        'median_uplift':    round(np.median(treatment) - np.median(control), 4),
        'cles':             round(cles, 4),   # P(treatment > control)
        'u_statistic':      round(u_stat, 2),
        'p_value':          round(p_value, 6),
        'significant':      p_value < alpha,
        'alpha':            alpha,
    }


def bonferroni_correction(p_values: list[float], alpha: float = 0.05) -> list[dict]:
    """Apply Bonferroni correction for multiple comparisons."""
    m = len(p_values)
    return [
        {'variant': i + 1, 'p_value': p, 'adjusted_alpha': alpha / m,
         'significant': p < alpha / m}
        for i, p in enumerate(p_values)
    ]
