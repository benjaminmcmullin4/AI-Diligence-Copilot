"""History tab -- Past analyses list."""

from __future__ import annotations

import streamlit as st

from config import COLORS, DB_PATH
from db import delete_analysis, list_analyses


def render_history() -> None:
    """Render the analysis history list."""

    st.markdown(
        f'<div class="section-header">Analysis History</div>',
        unsafe_allow_html=True,
    )

    # ── Load analyses ──
    analyses = list_analyses()

    if not analyses:
        st.info("No analyses found. Start a new analysis from the New Analysis tab.")
        return

    # ── Table Header ──
    header_cols = st.columns([3, 1.5, 1, 2, 1, 0.8])
    with header_cols[0]:
        st.markdown("**Company**")
    with header_cols[1]:
        st.markdown("**Model**")
    with header_cols[2]:
        st.markdown("**Status**")
    with header_cols[3]:
        st.markdown("**Created**")
    with header_cols[4]:
        st.markdown("**View**")
    with header_cols[5]:
        st.markdown("**Delete**")

    st.markdown(
        f'<hr style="margin: 0.25rem 0; border-color: {COLORS["light_gray"]};">',
        unsafe_allow_html=True,
    )

    # ── Rows ──
    for analysis in analyses:
        row_cols = st.columns([3, 1.5, 1, 2, 1, 0.8])

        with row_cols[0]:
            st.markdown(f"**{analysis['company_name']}**")

        with row_cols[1]:
            model_type = analysis.get("business_model", "unknown")
            badge_bg = COLORS["teal"] if model_type == "saas" else COLORS["gold_accent"]
            is_demo = analysis.get("is_demo", 0)
            demo_tag = (
                f' <span style="color: {COLORS["muted"]}; font-size: 0.7rem;">(demo)</span>'
                if is_demo
                else ""
            )
            st.markdown(
                f'<span style="background: {badge_bg}; color: white; padding: 0.15rem 0.5rem; '
                f'border-radius: 4px; font-size: 0.75rem; font-weight: 600;">'
                f'{model_type.upper()}</span>{demo_tag}',
                unsafe_allow_html=True,
            )

        with row_cols[2]:
            status = analysis.get("status", "pending")
            status_colors = {
                "completed": COLORS["teal"],
                "running": COLORS["gold_accent"],
                "failed": COLORS["red_accent"],
                "pending": COLORS["muted"],
            }
            s_color = status_colors.get(status, COLORS["muted"])
            st.markdown(
                f'<span style="background: {s_color}; color: white; padding: 0.15rem 0.5rem; '
                f'border-radius: 4px; font-size: 0.75rem; font-weight: 600;">'
                f'{status.capitalize()}</span>',
                unsafe_allow_html=True,
            )

        with row_cols[3]:
            created = analysis.get("created_at", "")[:16].replace("T", " ")
            st.caption(created)

        with row_cols[4]:
            if st.button("View", key=f"hist_view_{analysis['id']}"):
                st.session_state["loaded_analysis_id"] = analysis["id"]
                st.rerun()

        with row_cols[5]:
            if st.button("X", key=f"hist_del_{analysis['id']}", type="secondary"):
                delete_analysis(analysis["id"])
                st.rerun()
