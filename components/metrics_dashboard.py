"""Reusable metric card grid for benchmark-rated metrics."""

from __future__ import annotations

import streamlit as st

from schema import BenchmarkRating
from config import COLORS

_RATING_COLORS = {
    "green": "#1ABC9C",   # teal
    "yellow": "#D4A338",  # gold
    "red": "#E74C3C",     # red accent
}


def _render_metric_card(name: str, rating: BenchmarkRating) -> None:
    """Render a single metric card with color-coded rating badge."""
    color = _RATING_COLORS.get(rating.rating, COLORS["muted"])
    badge_bg = color

    html = f"""
    <div class="metric-card">
        <div class="metric-label">{name}</div>
        <div class="metric-value">{rating.value}</div>
        <div class="metric-benchmark">{rating.benchmark}</div>
        <div style="margin-top: 0.5rem;">
            <span style="background: {badge_bg}; color: white; padding: 0.15rem 0.5rem;
            border-radius: 4px; font-size: 0.75rem; font-weight: 600;">{rating.rating.upper()}</span>
        </div>
        <div style="font-size: 0.78rem; color: {COLORS['muted']}; margin-top: 0.35rem;">
            {rating.commentary}
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_metrics_dashboard(metrics_dict: dict[str, BenchmarkRating], columns: int = 3) -> None:
    """Render a grid of metric cards from a dict of name -> BenchmarkRating.

    Args:
        metrics_dict: Mapping of display name to BenchmarkRating object.
        columns: Number of columns in the grid (default 3).
    """
    items = list(metrics_dict.items())
    for row_start in range(0, len(items), columns):
        row_items = items[row_start : row_start + columns]
        cols = st.columns(columns)
        for col, (name, rating) in zip(cols, row_items):
            with col:
                _render_metric_card(name, rating)
