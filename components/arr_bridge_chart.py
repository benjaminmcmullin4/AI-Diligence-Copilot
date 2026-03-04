"""ARR bridge waterfall chart component using Plotly."""

import plotly.graph_objects as go
import streamlit as st

from schemas.saas import ARRBridge


def render_arr_bridge_chart(arr_bridge: ARRBridge) -> None:
    """Render a Plotly waterfall chart for ARR bridge.

    Shows the flow from Beginning ARR to Ending ARR through New, Expansion,
    Contraction, and Churn components.

    Args:
        arr_bridge: ARRBridge object with waterfall components.
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
        arr_bridge.contraction_arr,  # Expected negative
        arr_bridge.churn_arr,        # Expected negative
        arr_bridge.ending_arr,
    ]

    # Waterfall measure types: "absolute" for start/end, "relative" for changes
    measures = ["absolute", "relative", "relative", "relative", "relative", "total"]

    fig = go.Figure(go.Waterfall(
        name="ARR Bridge",
        orientation="v",
        measure=measures,
        x=labels,
        y=values,
        textposition="outside",
        text=[f"${v:+.1f}M" if m == "relative" else f"${v:.1f}M" for v, m in zip(values, measures)],
        connector=dict(line=dict(color="#353F3F", width=1)),
        increasing=dict(marker=dict(color="#A8A8A8")),
        decreasing=dict(marker=dict(color="#ef4444")),
        totals=dict(marker=dict(color="#000000", line=dict(color="#FFFFFF", width=2))),
    ))

    fig.update_layout(
        title=dict(
            text="ARR Bridge ($M)",
            font=dict(color="#FFFFFF", size=16),
        ),
        xaxis=dict(
            color="#A8A8A8",
            tickfont=dict(size=11),
        ),
        yaxis=dict(
            title="ARR ($M)",
            color="#A8A8A8",
            gridcolor="#353F3F",
            zeroline=False,
        ),
        plot_bgcolor="#000000",
        paper_bgcolor="#000000",
        font=dict(color="#FFFFFF"),
        showlegend=False,
        margin=dict(l=60, r=30, t=50, b=50),
    )

    st.plotly_chart(fig, use_container_width=True)
