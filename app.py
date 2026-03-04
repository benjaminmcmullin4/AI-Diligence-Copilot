"""Meridian | Diligence Copilot — AI-powered commercial due diligence."""

from __future__ import annotations

import os
from pathlib import Path

import streamlit as st

from config import COLORS, FIRM_NAME, APP_TITLE, APP_SUBTITLE, DB_PATH, get_api_key
from db import init_db, load_demo_samples

# ── Page config ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title=f"{FIRM_NAME} | {APP_TITLE}",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Load custom CSS ────────────────────────────────────────────────────
css_path = Path(__file__).parent / "styles" / "custom.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)

# ── Initialize DB & demo data ─────────────────────────────────────────
init_db()
load_demo_samples()

# ── Auth gate ──────────────────────────────────────────────────────────
from auth import require_auth
require_auth()

# ── Detect API key ─────────────────────────────────────────────────────
api_key = get_api_key()
demo_mode = not bool(api_key)

# ── Sidebar ────────────────────────────────────────────────────────────
from components.sidebar import render_sidebar
sidebar_state = render_sidebar()

# ── Header ─────────────────────────────────────────────────────────────
st.markdown(
    f'<h1 style="color: {COLORS["navy"]}; margin-bottom: 0;">{FIRM_NAME} | {APP_TITLE}</h1>'
    f'<p style="color: {COLORS["muted"]}; margin-top: 0;">{APP_SUBTITLE}</p>',
    unsafe_allow_html=True,
)

# Demo mode banner
if demo_mode:
    st.markdown(
        '<div class="demo-banner">'
        '🔬 <strong>Demo Mode</strong> — Add your Anthropic API key to run live analysis'
        '</div>',
        unsafe_allow_html=True,
    )

# ── Tabs ───────────────────────────────────────────────────────────────
tab_new, tab_view, tab_history = st.tabs(["New Analysis", "Analysis View", "History"])

from components.new_analysis_tab import render_new_analysis
from components.analysis_view_tab import render_analysis_view
from components.history_tab import render_history

with tab_new:
    render_new_analysis()

with tab_view:
    # Check if an analysis was loaded from sidebar or query params
    analysis_id = sidebar_state.get("loaded_analysis_id") or st.query_params.get("analysis_id")
    if analysis_id:
        render_analysis_view(analysis_id)
    else:
        st.info("Select an analysis from History or run a new one.")

with tab_history:
    render_history()
