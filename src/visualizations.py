"""Visualization helpers for A/B experiment results."""
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots


def plot_distributions(
    control: np.ndarray,
    treatment: np.ndarray,
    metric_name: str,
    experiment_name: str,
    output_path: str,
) -> None:
    fig = make_subplots(rows=1, cols=2,
                        subplot_titles=['Distribution Comparison', 'Box Plot'])
    fig.add_trace(go.Histogram(x=control,   name='Control',   opacity=0.6,
                               marker_color='#2196F3'), row=1, col=1)
    fig.add_trace(go.Histogram(x=treatment, name='Treatment', opacity=0.6,
                               marker_color='#43A047'), row=1, col=1)
    fig.add_trace(go.Box(y=control,   name='Control',   marker_color='#2196F3',
                         boxmean=True), row=1, col=2)
    fig.add_trace(go.Box(y=treatment, name='Treatment', marker_color='#43A047',
                         boxmean=True), row=1, col=2)
    fig.update_layout(
        title=f'{experiment_name} — {metric_name} Distribution',
        barmode='overlay',
        paper_bgcolor='white', plot_bgcolor='white',
        height=400, showlegend=True,
    )
    fig.write_html(output_path)


def plot_conversion_rates(
    p_control: float,
    p_treatment: float,
    ci_low: float,
    ci_high: float,
    experiment_name: str,
    output_path: str,
) -> None:
    fig = go.Figure()
    for name, val, err_lo, err_hi, color in [
        ('Control',   p_control,   0, 0, '#2196F3'),
        ('Treatment', p_treatment,
         p_treatment - (p_control + ci_low),
         (p_control + ci_high) - p_treatment,
         '#43A047'),
    ]:
        fig.add_trace(go.Bar(
            x=[name], y=[val * 100],
            name=name,
            marker_color=color,
            error_y={'type': 'data', 'array': [err_hi * 100 if name == 'Treatment' else 0],
                     'arrayminus': [err_lo * 100 if name == 'Treatment' else 0],
                     'visible': name == 'Treatment'},
        ))
    fig.update_layout(
        title=f'{experiment_name} — Conversion Rates with 95% CI',
        yaxis_title='Conversion Rate (%)',
        paper_bgcolor='white', plot_bgcolor='white',
        height=380,
    )
    fig.write_html(output_path)
