"""Lightweight email OTP authentication for Streamlit."""

from __future__ import annotations

import hashlib
import secrets
import sqlite3
from datetime import datetime, timezone

import resend
import streamlit as st

from config import (
    ALLOWED_EMAIL_DOMAINS,
    AUTH_ENABLED,
    DB_PATH,
    OTP_FROM_EMAIL,
    RESEND_API_KEY,
)

OTP_EXPIRY_MINUTES = 10


# ── Private helpers ────────────────────────────────────────────────────────

def _get_otp_db() -> sqlite3.Connection:
    """Get a connection to the OTP database (same DB as analyses)."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute(
        """CREATE TABLE IF NOT EXISTS otp_codes (
            email TEXT NOT NULL,
            code_hash TEXT NOT NULL,
            created_at TEXT NOT NULL,
            used INTEGER DEFAULT 0
        )"""
    )
    conn.commit()
    return conn


def _hash_code(code: str) -> str:
    return hashlib.sha256(code.encode()).hexdigest()


def _generate_otp() -> str:
    return f"{secrets.randbelow(1000000):06d}"


def _send_otp_email(to_email: str, code: str) -> bool:
    """Send OTP code via Resend API."""
    if not RESEND_API_KEY:
        st.error("Resend API key not configured. Contact your administrator.")
        return False

    resend.api_key = RESEND_API_KEY

    try:
        resend.Emails.send(
            {
                "from": OTP_FROM_EMAIL,
                "to": [to_email],
                "subject": f"Meridian Diligence Copilot \u2014 Verification Code: {code}",
                "text": (
                    f"Your verification code is: {code}\n\n"
                    f"This code expires in {OTP_EXPIRY_MINUTES} minutes.\n\n"
                    f"If you did not request this code, please ignore this email.\n\n"
                    f"\u2014 Meridian Diligence Copilot"
                ),
            }
        )
        return True
    except Exception as e:
        st.error(f"Failed to send email: {e}")
        return False


def _store_otp(email: str, code: str) -> None:
    conn = _get_otp_db()
    conn.execute(
        "INSERT INTO otp_codes (email, code_hash, created_at) VALUES (?, ?, ?)",
        (email.lower(), _hash_code(code), datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
    conn.close()


def _verify_otp(email: str, code: str) -> bool:
    conn = _get_otp_db()
    cursor = conn.execute(
        "SELECT rowid, created_at FROM otp_codes WHERE email = ? AND code_hash = ? AND used = 0 "
        "ORDER BY created_at DESC LIMIT 1",
        (email.lower(), _hash_code(code)),
    )
    row = cursor.fetchone()
    if row is None:
        conn.close()
        return False

    rowid, created_at = row
    created = datetime.fromisoformat(created_at)
    elapsed = (datetime.now(timezone.utc) - created).total_seconds()

    if elapsed > OTP_EXPIRY_MINUTES * 60:
        conn.close()
        return False

    conn.execute("UPDATE otp_codes SET used = 1 WHERE rowid = ?", (rowid,))
    conn.commit()
    conn.close()
    return True


def _validate_email_domain(email: str) -> bool:
    """Check if email domain is in the allowlist (if configured)."""
    if not ALLOWED_EMAIL_DOMAINS:
        return True
    allowed = [d.strip().lower() for d in ALLOWED_EMAIL_DOMAINS.split(",") if d.strip()]
    if not allowed:
        return True
    domain = email.lower().split("@")[-1]
    return domain in allowed


def _render_login_form() -> None:
    """Render the branded login form (light theme)."""
    st.markdown(
        """
        <div class="brand-header" style="justify-content: center; padding-top: 3rem;">
            <span class="brand-name">Meridian</span>
            <span class="tagline">Diligence Copilot</span>
        </div>
        <div style="text-align: center; color: #777777; margin-bottom: 2rem;">
            Sign in to continue
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Initialize session state
    if "otp_step" not in st.session_state:
        st.session_state["otp_step"] = "email"
    if "otp_email" not in st.session_state:
        st.session_state["otp_email"] = ""

    col_spacer_l, col_form, col_spacer_r = st.columns([1, 2, 1])

    with col_form:
        if st.session_state["otp_step"] == "email":
            email = st.text_input("Email Address", placeholder="you@company.com")
            if st.button("Send Verification Code", type="primary", use_container_width=True):
                if not email or "@" not in email:
                    st.error("Please enter a valid email address.")
                elif not _validate_email_domain(email):
                    st.error("This email domain is not authorized.")
                else:
                    code = _generate_otp()
                    _store_otp(email, code)
                    if _send_otp_email(email, code):
                        st.session_state["otp_email"] = email
                        st.session_state["otp_step"] = "verify"
                        st.rerun()

        elif st.session_state["otp_step"] == "verify":
            st.info(f"A code was sent to **{st.session_state['otp_email']}**")
            code = st.text_input("Verification Code", placeholder="123456", max_chars=6)
            col_verify, col_back = st.columns(2)
            with col_verify:
                if st.button("Verify", type="primary", use_container_width=True):
                    if _verify_otp(st.session_state["otp_email"], code):
                        st.session_state["authenticated"] = True
                        st.session_state["user_email"] = st.session_state["otp_email"]
                        st.session_state.pop("otp_step", None)
                        st.session_state.pop("otp_email", None)
                        st.rerun()
                    else:
                        st.error("Invalid or expired code. Please try again.")
            with col_back:
                if st.button("Back", use_container_width=True):
                    st.session_state["otp_step"] = "email"
                    st.rerun()


# ── Public API ─────────────────────────────────────────────────────────────

def require_auth() -> None:
    """Gate page content behind OTP authentication.

    Call at the top of every page after injecting CSS.
    If AUTH_ENABLED is false, this is a no-op.
    """
    if not AUTH_ENABLED:
        return

    if st.session_state.get("authenticated"):
        return

    _render_login_form()
    st.stop()


def is_authenticated() -> bool:
    """Return True if the user has passed authentication (or auth is disabled)."""
    if not AUTH_ENABLED:
        return True
    return bool(st.session_state.get("authenticated"))


def get_auth_email() -> str:
    """Return the authenticated user's email, or empty string."""
    return st.session_state.get("user_email", "")


def render_auth_gate() -> None:
    """Alias for require_auth() — matches VC Research Agent naming convention."""
    require_auth()
