"""Competitor comparison table component."""

from __future__ import annotations

import streamlit as st

from schema import Competitor
from config import COLORS


def _threat_stars(level: int) -> str:
    """Return a star rating string for threat level (1-5)."""
    filled = level
    empty = 5 - level
    colors = {
        1: COLORS["teal"],
        2: COLORS["teal"],
        3: COLORS["gold_accent"],
        4: COLORS["red_accent"],
        5: COLORS["red_accent"],
    }
    color = colors.get(level, COLORS["muted"])
    stars = (
        f'<span style="color: {color};">'
        + ("&#9733;" * filled)
        + ("&#9734;" * empty)
        + "</span>"
    )
    return stars


def render_competitor_table(competitors: list[Competitor]) -> None:
    """Render a styled HTML table of Competitor objects.

    Args:
        competitors: List of Competitor objects to display.
    """
    if not competitors:
        st.info("No competitors identified.")
        return

    rows_html = ""
    for comp in competitors:
        rows_html += f"""
        <tr>
            <td><strong>{comp.name}</strong></td>
            <td>{comp.description}</td>
            <td>{comp.estimated_revenue}</td>
            <td>{_threat_stars(comp.threat_level)}</td>
            <td>{comp.differentiation}</td>
            <td style="color: {COLORS['muted']}; font-size: 0.8rem;">{comp.source.value}</td>
        </tr>
        """

    html = f"""
    <table class="risk-table">
        <thead>
            <tr>
                <th>Name</th>
                <th>Description</th>
                <th>Est. Revenue</th>
                <th>Threat Level</th>
                <th>Differentiation</th>
                <th>Source</th>
            </tr>
        </thead>
        <tbody>
            {rows_html}
        </tbody>
    </table>
    """
    st.markdown(html, unsafe_allow_html=True)
