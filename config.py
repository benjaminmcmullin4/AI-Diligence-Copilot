"""Configuration constants, color palette, and settings."""

from __future__ import annotations

import os
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent
DB_PATH = PROJECT_ROOT / "data" / "meridian.db"
DEMO_DIR = PROJECT_ROOT / "examples" / "samples"
DEMO_FILES = ["acme_saas.json", "peak_health.json", "summit_retail.json"]

# ── Branding ──────────────────────────────────────────────────────────
FIRM_NAME = "Meridian"
APP_TITLE = "Diligence Copilot"
APP_SUBTITLE = "AI-powered commercial due diligence for growth equity"

# ── Design System ──────────────────────────────────────────────────────
COLORS = {
    "navy": "#0A0A0A",
    "steel_blue": "#333333",
    "teal": "#1ABC9C",
    "red_accent": "#E74C3C",
    "gold_accent": "#D4A338",
    "bg": "#FAFBFC",
    "text": "#1A1A1A",
    "muted": "#777777",
    "light_gray": "#ECF0F1",
    "white": "#FFFFFF",
}

FONT = "Inter"

# ── LLM Settings ───────────────────────────────────────────────────────
DEFAULT_MODEL = "claude-sonnet-4-20250514"
MAX_RETRIES = 2
MAX_TOKENS = 8192

# ── Auth Settings ──────────────────────────────────────────────────────
AUTH_ENABLED = os.environ.get("AUTH_ENABLED", "false").lower() == "true"
RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")
OTP_FROM_EMAIL = os.environ.get("OTP_FROM_EMAIL", "onboarding@resend.dev")
ALLOWED_EMAIL_DOMAINS = os.environ.get("ALLOWED_EMAIL_DOMAINS", "")


def _get_secret(key: str) -> str:
    """Read from Streamlit secrets first, then environment."""
    try:
        import streamlit as st
        val = st.secrets.get(key, "")
        if val:
            return str(val)
    except Exception:
        pass
    return os.environ.get(key, "")


def get_api_key() -> str:
    """Return the Anthropic API key if available."""
    return _get_secret("ANTHROPIC_API_KEY")
