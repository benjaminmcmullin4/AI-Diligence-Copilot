"""Sidebar controls for Meridian Diligence Copilot."""

from __future__ import annotations

import streamlit as st

from config import COLORS, FIRM_NAME
from db import list_analyses, get_analysis


def render_sidebar() -> dict:
    """Render sidebar controls and return a dict with sidebar state.

    Returns:
        dict with keys:
            - loaded_analysis_id: str | None  (selected past analysis)
    """
    # ── Firm branding ──────────────────────────────────────────────────
    st.sidebar.markdown(
        f'<div style="text-align: center; padding: 0.5rem 0 1rem 0;">'
        f'<span style="color: #FFFFFF; font-size: 1.2rem; font-weight: 700; '
        f'letter-spacing: 0.05em;">{FIRM_NAME}</span><br>'
        f'<span style="color: #999; font-size: 0.75rem;">Diligence Copilot</span>'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.sidebar.markdown("---")

    # ── Auth status badge ──────────────────────────────────────────────
    from auth import get_auth_email

    auth_email = get_auth_email()
    if auth_email:
        st.sidebar.markdown(
            f'<div style="background: rgba(26,188,156,0.15); padding: 0.4rem 0.8rem; '
            f'border-radius: 6px; font-size: 0.8rem; color: {COLORS["teal"]}; '
            f'margin-bottom: 0.5rem;">'
            f'Authenticated as <strong>{auth_email}</strong></div>',
            unsafe_allow_html=True,
        )

    # ── API key status ─────────────────────────────────────────────────
    from config import get_api_key

    api_key = get_api_key()
    if api_key:
        st.sidebar.success("Anthropic API key configured", icon="\u2705")
    else:
        st.sidebar.warning(
            "No API key \u2014 demo mode only. Add `ANTHROPIC_API_KEY` to `.env` for live analysis.",
            icon="\u26a0\ufe0f",
        )

    st.sidebar.markdown("---")

    # ── New Analysis button ────────────────────────────────────────────
    new_analysis_clicked = st.sidebar.button(
        "\u2795  New Analysis",
        use_container_width=True,
        type="primary",
    )
    if new_analysis_clicked:
        # Clear any loaded analysis so the New Analysis tab is active
        st.session_state.pop("loaded_analysis_id", None)

    st.sidebar.markdown("---")

    # ── Past analyses ──────────────────────────────────────────────────
    st.sidebar.markdown("## Past Analyses")
    analyses = list_analyses()

    loaded_analysis_id = None

    if analyses:
        run_labels = {
            a["id"]: f"{a['company_name'][:35]}  ({a.get('created_at', '')[:10]})"
            for a in analyses
        }
        selected_id = st.sidebar.selectbox(
            "Load previous analysis",
            options=[None] + list(run_labels.keys()),
            format_func=lambda x: "\u2014 Select \u2014" if x is None else run_labels[x],
        )
        if selected_id is not None:
            loaded_analysis_id = selected_id
    else:
        st.sidebar.caption("No past analyses yet.")

    return {
        "loaded_analysis_id": loaded_analysis_id,
    }
