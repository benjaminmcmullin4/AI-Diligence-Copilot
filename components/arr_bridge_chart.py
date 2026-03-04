"""ARR bridge waterfall chart component using Plotly."""

from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from config import COLORS
from schema import ARRBridge


def render_arr_bridge_chart(arr_bridge: ARRBridge) -> None:
    """Render a Plotly waterfall chart for ARR bridge.

    Shows the flow from Beginning ARR to Ending ARR through New, Expansion,
    Contraction, and Churn components.
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
        text=[f"${v:+.1f}M" if m == "relative" else f"${v:.1f}M" for v, m in zip(values, measures)],
        connector=dict(line=dict(color=COLORS["light_gray"], width=1)),
        increasing=dict(marker=dict(color=COLORS["teal"])),
        decreasing=dict(marker=dict(color=COLORS["red_accent"])),
        totals=dict(marker=dict(color=COLORS["navy"], line=dict(color=COLORS["white"], width=2))),
    ))

    fig.update_layout(
        title=dict(text="ARR Bridge ($M)", font=dict(color=COLORS["navy"], size=16)),
        xaxis=dict(color=COLORS["muted"], tickfont=dict(size=11)),
        yaxis=dict(title="ARR ($M)", color=COLORS["muted"], gridcolor=COLORS["light_gray"], zeroline=False),
        plot_bgcolor=COLORS["white"],
        paper_bgcolor=COLORS["bg"],
        font=dict(color=COLORS["navy"], family="Inter"),
        showlegend=False,
        margin=dict(l=60, r=30, t=50, b=50),
    )

    st.plotly_chart(fig, use_container_width=True)
