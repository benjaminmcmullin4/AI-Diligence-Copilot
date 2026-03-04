"""History -- Past analyses list."""

import streamlit as st

st.set_page_config(
    page_title="History | Meridian",
    page_icon=":chart_with_upwards_trend:",
    layout="wide",
)

from components.styles import inject_custom_css
from core.config import get_settings
from core.database import delete_analysis, init_db, list_analyses

inject_custom_css()
settings = get_settings()
init_db(settings.db_path)

from core.auth import require_auth
require_auth(settings)

# ── Header ──
st.markdown(
    """
    <div class="brand-header">
        <span class="brand-name">Meridian</span>
        <span class="tagline">Analysis History</span>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown("---")

# ── Load analyses ──
analyses = list_analyses(settings.db_path)

if not analyses:
    st.info("No analyses found. Start a new analysis from the dashboard.")
    if st.button("Back to Dashboard"):
        st.switch_page("app.py")
    st.stop()

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

st.markdown("<hr style='margin: 0.25rem 0; border-color: #353F3F;'>", unsafe_allow_html=True)

# ── Rows ──
for analysis in analyses:
    row_cols = st.columns([3, 1.5, 1, 2, 1, 0.8])

    with row_cols[0]:
        st.markdown(f"**{analysis['company_name']}**")

    with row_cols[1]:
        model_type = analysis.get("business_model", "unknown")
        badge_color = "green" if model_type == "saas" else "yellow"
        is_demo = analysis.get("is_demo", 0)
        demo_tag = ' <span style="color: #A8A8A8; font-size: 0.7rem;">(demo)</span>' if is_demo else ""
        st.markdown(
            f'<span class="risk-badge {badge_color}">{model_type.upper()}</span>{demo_tag}',
            unsafe_allow_html=True,
        )

    with row_cols[2]:
        status = analysis.get("status", "pending")
        st.markdown(
            f'<span class="status-badge {status}">{status.capitalize()}</span>',
            unsafe_allow_html=True,
        )

    with row_cols[3]:
        created = analysis.get("created_at", "")[:16].replace("T", " ")
        st.caption(created)

    with row_cols[4]:
        if st.button("View", key=f"hist_view_{analysis['id']}"):
            st.query_params["analysis_id"] = analysis["id"]
            st.switch_page("pages/2_Analysis_View.py")

    with row_cols[5]:
        if st.button("X", key=f"hist_del_{analysis['id']}", type="secondary"):
            delete_analysis(settings.db_path, analysis["id"])
            st.rerun()
