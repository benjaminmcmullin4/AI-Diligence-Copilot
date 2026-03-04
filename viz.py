"""Plotly chart builders for the Meridian Diligence Copilot.

All charts use the light theme design system: white background, navy text,
teal accent, muted grid lines. Functions return Plotly Figure objects
(callers are responsible for rendering via st.plotly_chart).
"""

from __future__ import annotations

from typing import Sequence

import plotly.graph_objects as go

from config import COLORS
from schema import ARRBridge, CohortVintage, Risk


# ═══════════════════════════════════════════════════════════════════════════
# Shared layout defaults
# ═══════════════════════════════════════════════════════════════════════════

def _base_layout(**overrides) -> dict:
    """Return a base Plotly layout dict with the light theme."""
    defaults = dict(
        plot_bgcolor=COLORS["white"],
        paper_bgcolor=COLORS["bg"],
        font=dict(family="Inter, sans-serif", color=COLORS["text"]),
        margin=dict(l=60, r=30, t=50, b=50),
    )
    defaults.update(overrides)
    return defaults


def _axis_defaults(title: str = "") -> dict:
    """Return common axis styling."""
    return dict(
        title=title,
        color=COLORS["muted"],
        gridcolor=COLORS["light_gray"],
        zeroline=False,
        tickfont=dict(size=11, color=COLORS["muted"]),
    )


# ═══════════════════════════════════════════════════════════════════════════
# ARR Bridge Waterfall
# ═══════════════════════════════════════════════════════════════════════════

def arr_bridge_chart(arr_bridge: ARRBridge) -> go.Figure:
    """Create a waterfall chart showing the ARR bridge.

    Args:
        arr_bridge: ARRBridge model with waterfall components.

    Returns:
        Plotly Figure object.
    """
    labels = [
        "Beginning ARR",
        "New",
        "Expansion",
        "Contraction",
        "Churn",
        "Ending ARR",
    ]

    values = [
        arr_bridge.beginning_arr,
        arr_bridge.new_arr,
        arr_bridge.expansion_arr,
        arr_bridge.contraction_arr,
        arr_bridge.churn_arr,
        arr_bridge.ending_arr,
    ]

    measures = ["absolute", "relative", "relative", "relative", "relative", "total"]

    fig = go.Figure(go.Waterfall(
        name="ARR Bridge",
        orientation="v",
        measure=measures,
        x=labels,
        y=values,
        textposition="outside",
        text=[
            f"${v:+.1f}M" if m == "relative" else f"${v:.1f}M"
            for v, m in zip(values, measures)
        ],
        connector=dict(line=dict(color=COLORS["light_gray"], width=1)),
        increasing=dict(marker=dict(color=COLORS["teal"])),
        decreasing=dict(marker=dict(color=COLORS["red_accent"])),
        totals=dict(marker=dict(
            color=COLORS["navy"],
            line=dict(color=COLORS["light_gray"], width=2),
        )),
    ))

    fig.update_layout(
        **_base_layout(),
        title=dict(
            text="ARR Bridge ($M)",
            font=dict(color=COLORS["navy"], size=16),
        ),
        xaxis=_axis_defaults(),
        yaxis=_axis_defaults("ARR ($M)"),
        showlegend=False,
    )

    return fig


# ═══════════════════════════════════════════════════════════════════════════
# Cohort Retention Curves
# ═══════════════════════════════════════════════════════════════════════════

def cohort_retention_chart(cohort_vintages: list[CohortVintage]) -> go.Figure:
    """Create a line chart of cohort retention curves.

    Args:
        cohort_vintages: List of CohortVintage objects to plot.

    Returns:
        Plotly Figure object (empty figure if no data).
    """
    fig = go.Figure()

    if not cohort_vintages:
        fig.update_layout(**_base_layout(), title="Cohort Retention Curves (No Data)")
        return fig

    # Teal-based color palette with varying opacity/shade
    palette = [
        "#1ABC9C",  # teal
        "#16A085",  # dark teal
        "#2ECC71",  # emerald
        "#27AE60",  # dark emerald
        "#3498DB",  # blue
        "#2980B9",  # dark blue
        "#9B59B6",  # purple
        "#D4A338",  # gold
        "#E67E22",  # orange
        "#E74C3C",  # red
    ]

    for i, cohort in enumerate(cohort_vintages):
        color = palette[i % len(palette)]
        fig.add_trace(go.Scatter(
            x=cohort.months,
            y=cohort.retention_pct,
            mode="lines+markers",
            name=cohort.cohort_label,
            line=dict(color=color, width=2),
            marker=dict(size=5),
            hovertemplate=(
                f"<b>{cohort.cohort_label}</b><br>"
                "Month %{x}<br>"
                "Retention: %{y:.1f}%<extra></extra>"
            ),
        ))

    max_retention = max(max(c.retention_pct) for c in cohort_vintages) if cohort_vintages else 100

    fig.update_layout(
        **_base_layout(),
        title=dict(
            text="Cohort Retention Curves",
            font=dict(color=COLORS["navy"], size=16),
        ),
        xaxis=_axis_defaults("Months Since Cohort Start"),
        yaxis=dict(
            **_axis_defaults("Retention (%)"),
            range=[0, max_retention * 1.05],
        ),
        legend=dict(
            bgcolor=COLORS["white"],
            bordercolor=COLORS["light_gray"],
            borderwidth=1,
            font=dict(color=COLORS["text"]),
        ),
        hovermode="x unified",
    )

    return fig


# ═══════════════════════════════════════════════════════════════════════════
# Risk Heatmap
# ═══════════════════════════════════════════════════════════════════════════

def risk_heatmap(risks: list[Risk]) -> go.Figure:
    """Create a scatter-based risk heatmap (severity vs likelihood).

    Args:
        risks: List of Risk model objects.

    Returns:
        Plotly Figure object.
    """
    fig = go.Figure()

    if not risks:
        fig.update_layout(**_base_layout(), title="Risk Heatmap (No Risks Identified)")
        return fig

    severities = [r.severity for r in risks]
    likelihoods = [r.likelihood for r in risks]
    labels = [r.category for r in risks]
    descriptions = [
        r.description[:60] + "..." if len(r.description) > 60 else r.description
        for r in risks
    ]

    # Color by composite risk score
    scores = [s * l for s, l in zip(severities, likelihoods)]

    fig.add_trace(go.Scatter(
        x=severities,
        y=likelihoods,
        mode="markers+text",
        text=labels,
        textposition="top center",
        textfont=dict(size=10, color=COLORS["navy"]),
        marker=dict(
            size=[max(12, s * 4) for s in scores],
            color=scores,
            colorscale=[
                [0, COLORS["teal"]],
                [0.5, COLORS["gold_accent"]],
                [1, COLORS["red_accent"]],
            ],
            showscale=True,
            colorbar=dict(
                title="Risk Score",
                tickfont=dict(color=COLORS["muted"]),
                titlefont=dict(color=COLORS["muted"]),
            ),
            line=dict(width=1, color=COLORS["light_gray"]),
        ),
        hovertext=[f"{l}: {d}" for l, d in zip(labels, descriptions)],
        hoverinfo="text",
    ))

    fig.update_layout(
        **_base_layout(),
        xaxis=dict(
            **_axis_defaults("Severity"),
            range=[0.5, 5.5],
            dtick=1,
        ),
        yaxis=dict(
            **_axis_defaults("Likelihood"),
            range=[0.5, 5.5],
            dtick=1,
        ),
    )

    return fig


# ═══════════════════════════════════════════════════════════════════════════
# TAM / SAM / SOM Bar Chart
# ═══════════════════════════════════════════════════════════════════════════

def tam_sam_chart(
    tam_value_b: float | None = None,
    sam_value_b: float | None = None,
    som_value_b: float | None = None,
) -> go.Figure:
    """Create a grouped bar chart for TAM/SAM/SOM market sizing.

    Args:
        tam_value_b: Total Addressable Market in $B.
        sam_value_b: Serviceable Addressable Market in $B.
        som_value_b: Serviceable Obtainable Market in $B.

    Returns:
        Plotly Figure object.
    """
    tam_v = tam_value_b or 0
    sam_v = sam_value_b or 0
    som_v = som_value_b or 0

    fig = go.Figure(go.Bar(
        x=["TAM", "SAM", "SOM"],
        y=[tam_v, sam_v, som_v],
        marker_color=[
            COLORS["light_gray"],
            COLORS["muted"],
            COLORS["teal"],
        ],
        text=[f"${v:.1f}B" for v in [tam_v, sam_v, som_v]],
        textposition="outside",
        textfont=dict(color=COLORS["navy"], size=12, family="Inter, sans-serif"),
    ))

    fig.update_layout(
        **_base_layout(),
        title=dict(
            text="Market Sizing ($B)",
            font=dict(color=COLORS["navy"], size=16),
        ),
        xaxis=_axis_defaults(),
        yaxis=_axis_defaults("$B"),
        showlegend=False,
    )

    return fig
