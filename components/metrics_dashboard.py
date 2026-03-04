"""Reusable metric card grid for benchmark-rated metrics."""

import streamlit as st

from schemas.saas import BenchmarkRating


_RATING_COLORS = {
    "green": "#10b981",
    "yellow": "#f59e0b",
    "red": "#ef4444",
}

_RATING_DELTA_PREFIX = {
    "green": "",
    "yellow": "",
    "red": "",
}


def _render_metric_card(name: str, rating: BenchmarkRating) -> None:
    """Render a single metric card with color-coded rating badge."""
    color = _RATING_COLORS.get(rating.rating, "#94a3b8")
    badge_class = rating.rating if rating.rating in ("green", "yellow", "red") else ""

    html = f"""
    <div class="metric-card">
        <div class="metric-label">{name}</div>
        <div class="metric-value">{rating.value}</div>
        <div class="metric-benchmark">{rating.benchmark}</div>
        <div style="margin-top: 0.5rem;">
            <span class="risk-badge {badge_class}">{rating.rating.upper()}</span>
        </div>
        <div style="font-size: 0.78rem; color: #94a3b8; margin-top: 0.35rem;">
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
