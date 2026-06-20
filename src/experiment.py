"""Experiment configuration and synthetic data simulation."""
from dataclasses import dataclass, field
from typing import Literal
import numpy as np
import pandas as pd

RNG = np.random.default_rng(42)


@dataclass
class ExperimentConfig:
    name:          str
    metric:        str
    metric_type:   Literal['binary', 'continuous', 'count']
    alpha:         float = 0.05        # significance level
    power:         float = 0.80        # statistical power (1 - beta)
    mde:           float = 0.10        # minimum detectable effect (relative)
    n_per_group:   int   = None        # filled by sample_size calc or manually
    baseline:      float = None        # baseline metric value
    description:   str   = ''
    tags:          list  = field(default_factory=list)


def simulate_binary(
    n: int,
    p_control: float,
    p_treatment: float,
    seed: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Simulate conversion events (0/1) for control and treatment."""
    rng       = np.random.default_rng(seed)
    control   = pd.DataFrame({'converted': rng.binomial(1, p_control,   n), 'group': 'control'})
    treatment = pd.DataFrame({'converted': rng.binomial(1, p_treatment, n), 'group': 'treatment'})
    return control, treatment


def simulate_continuous(
    n: int,
    mean_control: float,
    mean_treatment: float,
    std: float,
    seed: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Simulate a continuous metric (e.g. revenue per user)."""
    rng       = np.random.default_rng(seed)
    control   = pd.DataFrame({'value': rng.normal(mean_control,   std, n), 'group': 'control'})
    treatment = pd.DataFrame({'value': rng.normal(mean_treatment, std, n), 'group': 'treatment'})
    return control, treatment


def simulate_skewed(
    n: int,
    shape_control: float,
    shape_treatment: float,
    scale: float = 1.0,
    seed: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Simulate a right-skewed metric (e.g. session duration) using log-normal."""
    rng       = np.random.default_rng(seed)
    control   = pd.DataFrame({'value': rng.lognormal(shape_control,   scale, n), 'group': 'control'})
    treatment = pd.DataFrame({'value': rng.lognormal(shape_treatment, scale, n), 'group': 'treatment'})
    return control, treatment
