"""Cohort retention chart component using Plotly."""

from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from config import COLORS
from schema import CohortVintage


def render_cohort_chart(cohort_vintages: list[CohortVintage]) -> None:
    """Render a Plotly line chart of cohort retention curves."""
    if not cohort_vintages:
        st.info("No cohort data available.")
        return

    fig = go.Figure()

    # Teal-based palette for cohort lines
    palette = [
        COLORS["teal"], "#16a085", "#2ecc71", COLORS["gold_accent"],
        COLORS["muted"], COLORS["steel_blue"], "#3498db", "#9b59b6",
        "#e67e22", COLORS["red_accent"],
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

    fig.update_layout(
        title=dict(text="Cohort Retention Curves", font=dict(color=COLORS["navy"], size=16)),
        xaxis=dict(
            title="Months Since Cohort Start",
            color=COLORS["muted"],
            gridcolor=COLORS["light_gray"],
            zeroline=False,
        ),
        yaxis=dict(
            title="Retention (%)",
            color=COLORS["muted"],
            gridcolor=COLORS["light_gray"],
            zeroline=False,
            range=[0, max(max(c.retention_pct) for c in cohort_vintages) * 1.05],
        ),
        plot_bgcolor=COLORS["white"],
        paper_bgcolor=COLORS["bg"],
        font=dict(color=COLORS["navy"], family="Inter"),
        legend=dict(
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor=COLORS["light_gray"],
            borderwidth=1,
            font=dict(color=COLORS["navy"]),
        ),
        hovermode="x unified",
        margin=dict(l=60, r=30, t=50, b=50),
    )

    st.plotly_chart(fig, use_container_width=True)
