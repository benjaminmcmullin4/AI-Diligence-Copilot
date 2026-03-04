"""Meridian | Diligence Copilot — Main Dashboard."""

import streamlit as st

st.set_page_config(
    page_title="Meridian | Diligence Copilot",
    page_icon=":chart_with_upwards_trend:",
    layout="wide",
    initial_sidebar_state="expanded",
)

from components.styles import inject_custom_css
from core.config import get_settings
from core.database import init_db, list_analyses
from demo.loader import load_demo_samples

# ── Inject brand CSS ──
inject_custom_css()

# ── Settings & DB init ──
settings = get_settings()
init_db(settings.db_path)
load_demo_samples(settings.db_path)

# ── Auth gate ──
from core.auth import require_auth
require_auth(settings)

# ── Hero Header ──
st.markdown(
    """
    <div class="brand-header">
        <span class="brand-name">Meridian</span>
        <span class="tagline">Diligence Copilot</span>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown("---")

# ── API Key Status ──
if settings.has_api_key:
    st.sidebar.success("Anthropic API key configured", icon="\u2705")
else:
    st.sidebar.warning(
        "No API key — demo mode only. Add `ANTHROPIC_API_KEY` to `.env` for live analysis.",
        icon="\u26a0\ufe0f",
    )

# ── Quick Actions ──
col_action_1, col_action_2, _ = st.columns([1, 1, 2])
with col_action_1:
    if st.button("\u2795  New Analysis", use_container_width=True, type="primary"):
        st.switch_page("pages/1_New_Analysis.py")
with col_action_2:
    if st.button("\U0001f4da  View History", use_container_width=True):
        st.switch_page("pages/3_History.py")

st.markdown("")

# ── Demo Analysis Cards ──
st.subheader("Sample Analyses")
st.caption("Pre-built examples showcasing the platform. Click View to explore.")

demo_cards = [
    {
        "id": "demo-acme-saas",
        "title": "AcmeSaaS",
        "desc": "B2B vertical SaaS for CRE. $15M ARR, 125% NRR, strong unit economics.",
        "model": "SaaS",
    },
    {
        "id": "demo-peak-health",
        "title": "PeakHealth",
        "desc": "Healthcare SaaS platform. $8M ARR, 105% NRR, mixed signals on retention.",
        "model": "SaaS",
    },
    {
        "id": "demo-summit-retail",
        "title": "SummitRetail",
        "desc": "Specialty outdoor retailer. $45M revenue, 18% EBITDA margins, 28 locations.",
        "model": "Non-SaaS",
    },
]

cols = st.columns(3)
for col, card in zip(cols, demo_cards):
    with col:
        st.markdown(
            f"""
            <div class="demo-card">
                <h3>{card["title"]}</h3>
                <p>{card["desc"]}</p>
                <div style="margin-top: 0.75rem;">
                    <span class="risk-badge {'green' if card['model'] == 'SaaS' else 'yellow'}">
                        {card["model"]}
                    </span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("View Analysis", key=f"demo_{card['id']}", use_container_width=True):
            st.query_params["analysis_id"] = card["id"]
            st.switch_page("pages/2_Analysis_View.py")

st.markdown("")
st.markdown("---")

# ── Recent Analyses ──
st.subheader("Recent Analyses")

analyses = list_analyses(settings.db_path, include_demo=False)

if not analyses:
    st.info(
        "No custom analyses yet. Click **New Analysis** above to get started, "
        "or explore the sample analyses."
    )
else:
    for analysis in analyses[:10]:
        col_name, col_model, col_status, col_date, col_view = st.columns([3, 1, 1, 2, 1])
        with col_name:
            st.markdown(f"**{analysis['company_name']}**")
        with col_model:
            model_badge = "green" if analysis["business_model"] == "saas" else "yellow"
            st.markdown(
                f'<span class="risk-badge {model_badge}">{analysis["business_model"].upper()}</span>',
                unsafe_allow_html=True,
            )
        with col_status:
            status = analysis.get("status", "pending")
            st.markdown(
                f'<span class="status-badge {status}">{status.capitalize()}</span>',
                unsafe_allow_html=True,
            )
        with col_date:
            created = analysis.get("created_at", "")[:16].replace("T", " ")
            st.caption(created)
        with col_view:
            if st.button("View", key=f"view_{analysis['id']}"):
                st.query_params["analysis_id"] = analysis["id"]
                st.switch_page("pages/2_Analysis_View.py")
