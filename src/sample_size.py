"""Sample size and power analysis calculator."""
import math
from scipy import stats


def sample_size_proportion(
    p_baseline: float,
    mde: float,
    alpha: float = 0.05,
    power: float = 0.80,
) -> int:
    """
    Minimum n per group for a binary metric (e.g. conversion rate).
    mde: minimum detectable effect as absolute percentage points.
    """
    p1  = p_baseline
    p2  = p_baseline + mde
    p_bar = (p1 + p2) / 2
    z_a = stats.norm.ppf(1 - alpha / 2)
    z_b = stats.norm.ppf(power)
    n   = ((z_a * math.sqrt(2 * p_bar * (1 - p_bar)) +
             z_b * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2
           ) / (p2 - p1) ** 2
    return math.ceil(n)


def sample_size_mean(
    mean: float,
    std: float,
    mde_relative: float,
    alpha: float = 0.05,
    power: float = 0.80,
) -> int:
    """
    Minimum n per group for a continuous metric.
    mde_relative: minimum detectable effect as fraction of mean (e.g. 0.10 = 10%).
    """
    delta = mean * mde_relative
    z_a   = stats.norm.ppf(1 - alpha / 2)
    z_b   = stats.norm.ppf(power)
    n     = ((z_a + z_b) * std / delta) ** 2
    return math.ceil(n)


def achieved_power(
    n: int,
    mean: float,
    std: float,
    delta: float,
    alpha: float = 0.05,
) -> float:
    """Compute achieved power given a fixed sample size."""
    se    = std * math.sqrt(2 / n)
    z_a   = stats.norm.ppf(1 - alpha / 2)
    power = 1 - stats.norm.cdf(z_a - delta / se)
    return round(power, 4)


def print_sample_size_report(
    metric_type: str,
    n: int,
    alpha: float,
    power: float,
    **kwargs,
) -> None:
    print('\n' + '='*50)
    print('  SAMPLE SIZE ANALYSIS')
    print('='*50)
    print(f'  Metric type    : {metric_type}')
    for k, v in kwargs.items():
        print(f'  {k:<15}: {v}')
    print(f'  Alpha (α)      : {alpha}')
    print(f'  Power (1-β)    : {power}')
    print(f'  N per group    : {n:,}')
    print(f'  Total N needed : {n*2:,}')
    print('='*50)
