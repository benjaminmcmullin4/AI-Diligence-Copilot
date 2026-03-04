"""Custom CSS injection for the Traverse brand theme."""

import streamlit as st

BRAND_CSS = """
<style>
    /* ── Global Theme ── */
    :root {
        --black: #000000;
        --charcoal: #353F3F;
        --charcoal-light: #1a1f1f;
        --gray: #A8A8A8;
        --white: #FFFFFF;
        --yellow-accent: #f59e0b;
        --red-accent: #ef4444;
        --green-accent: #10b981;
        --text-primary: #FFFFFF;
        --text-secondary: #A8A8A8;
        --card-bg: #1a1f1f;
        --card-border: #353F3F;
    }

    /* ── Hide Streamlit defaults ── */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] {background: transparent;}

    /* ── Body / main area ── */
    .stApp {
        background-color: var(--black);
    }

    /* ── Branded Header ── */
    .brand-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 1rem 0 0.5rem 0;
    }
    .brand-header .brand-name {
        font-size: 2.2rem;
        font-weight: 800;
        color: var(--white);
        letter-spacing: -0.5px;
    }
    .brand-header .tagline {
        font-size: 1rem;
        color: var(--text-secondary);
        margin-left: 0.25rem;
        align-self: flex-end;
        padding-bottom: 0.35rem;
    }

    /* ── Metric Cards ── */
    .metric-card {
        background: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 0.75rem;
        transition: border-color 0.2s;
    }
    .metric-card:hover {
        border-color: var(--white);
    }
    .metric-card .metric-label {
        font-size: 0.8rem;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.25rem;
    }
    .metric-card .metric-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: var(--text-primary);
    }
    .metric-card .metric-benchmark {
        font-size: 0.75rem;
        color: var(--text-secondary);
        margin-top: 0.25rem;
    }

    /* ── Demo Cards ── */
    .demo-card {
        background: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: 12px;
        padding: 1.5rem;
        min-height: 180px;
        transition: transform 0.15s, border-color 0.2s;
    }
    .demo-card:hover {
        transform: translateY(-2px);
        border-color: var(--white);
    }
    .demo-card h3 {
        color: var(--text-primary);
        margin-bottom: 0.5rem;
    }
    .demo-card p {
        color: var(--text-secondary);
        font-size: 0.9rem;
    }

    /* ── Risk / Severity Badges ── */
    .risk-badge {
        display: inline-block;
        padding: 0.2rem 0.65rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.3px;
    }
    .risk-badge.green,
    .risk-badge.severity-1,
    .risk-badge.severity-2 {
        background: rgba(16, 185, 129, 0.15);
        color: var(--green-accent);
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    .risk-badge.yellow,
    .risk-badge.severity-3 {
        background: rgba(245, 158, 11, 0.15);
        color: var(--yellow-accent);
        border: 1px solid rgba(245, 158, 11, 0.3);
    }
    .risk-badge.red,
    .risk-badge.severity-4,
    .risk-badge.severity-5 {
        background: rgba(239, 68, 68, 0.15);
        color: var(--red-accent);
        border: 1px solid rgba(239, 68, 68, 0.3);
    }

    /* ── Status Badges ── */
    .status-badge {
        display: inline-block;
        padding: 0.2rem 0.5rem;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .status-badge.completed {
        background: rgba(16, 185, 129, 0.15);
        color: var(--green-accent);
    }
    .status-badge.running {
        background: rgba(245, 158, 11, 0.15);
        color: var(--yellow-accent);
    }
    .status-badge.failed {
        background: rgba(239, 68, 68, 0.15);
        color: var(--red-accent);
    }
    .status-badge.pending {
        background: rgba(168, 168, 168, 0.15);
        color: var(--text-secondary);
    }

    /* ── Callout Boxes ── */
    .callout-red {
        background: rgba(239, 68, 68, 0.08);
        border-left: 4px solid var(--red-accent);
        padding: 1rem 1.25rem;
        border-radius: 0 8px 8px 0;
        margin: 0.75rem 0;
    }
    .callout-green {
        background: rgba(16, 185, 129, 0.08);
        border-left: 4px solid var(--green-accent);
        padding: 1rem 1.25rem;
        border-radius: 0 8px 8px 0;
        margin: 0.75rem 0;
    }

    /* ── Sidebar tweaks ── */
    section[data-testid="stSidebar"] {
        background-color: var(--charcoal-light);
    }

    /* ── Table styling ── */
    .risk-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.88rem;
    }
    .risk-table th {
        background: var(--charcoal);
        color: var(--text-secondary);
        text-transform: uppercase;
        font-size: 0.72rem;
        letter-spacing: 0.4px;
        padding: 0.6rem 0.75rem;
        text-align: left;
        border-bottom: 2px solid var(--card-border);
    }
    .risk-table td {
        padding: 0.6rem 0.75rem;
        border-bottom: 1px solid var(--card-border);
        color: var(--text-primary);
        vertical-align: top;
    }
    .risk-table tr:hover td {
        background: rgba(255, 255, 255, 0.04);
    }
</style>
"""


def inject_custom_css() -> None:
    """Inject the Traverse brand CSS into the Streamlit page."""
    st.markdown(BRAND_CSS, unsafe_allow_html=True)
