"""Cohort retention chart component using Plotly."""

import plotly.graph_objects as go
import streamlit as st

from schemas.saas import CohortVintage


def render_cohort_chart(cohort_vintages: list[CohortVintage]) -> None:
    """Render a Plotly line chart of cohort retention curves.

    Each cohort vintage is rendered as a separate line. X-axis is months
    since cohort start, Y-axis is retention percentage.

    Args:
        cohort_vintages: List of CohortVintage objects to plot.
    """
    if not cohort_vintages:
        st.info("No cohort data available.")
        return

    fig = go.Figure()

    # Monochrome grayscale gradient palette
    colors = [
        "#FFFFFF", "#D0D0D0", "#A8A8A8", "#808080",
        "#606060", "#404040", "#353F3F", "#202020",
        "#C0C0C0", "#909090",
    ]

    for i, cohort in enumerate(cohort_vintages):
        color = colors[i % len(colors)]
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
        title=dict(
            text="Cohort Retention Curves",
            font=dict(color="#FFFFFF", size=16),
        ),
        xaxis=dict(
            title="Months Since Cohort Start",
            color="#A8A8A8",
            gridcolor="#353F3F",
            zeroline=False,
        ),
        yaxis=dict(
            title="Retention (%)",
            color="#A8A8A8",
            gridcolor="#353F3F",
            zeroline=False,
            range=[0, max(max(c.retention_pct) for c in cohort_vintages) * 1.05],
        ),
        plot_bgcolor="#000000",
        paper_bgcolor="#000000",
        font=dict(color="#FFFFFF"),
        legend=dict(
            bgcolor="rgba(26,31,31,0.8)",
            bordercolor="#353F3F",
            borderwidth=1,
            font=dict(color="#FFFFFF"),
        ),
        hovermode="x unified",
        margin=dict(l=60, r=30, t=50, b=50),
    )

    st.plotly_chart(fig, use_container_width=True)
