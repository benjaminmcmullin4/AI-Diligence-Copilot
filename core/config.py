"""Application configuration using pydantic-settings."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    anthropic_api_key: str = ""
    claude_model: str = "claude-sonnet-4-20250514"
    database_path: str = "./data/traverse.db"
    max_retries: int = 2
    max_tokens: int = 8192

    # Auth settings
    auth_enabled: bool = False
    resend_api_key: str = ""
    otp_from_email: str = "onboarding@resend.dev"
    allowed_email_domains: str = ""

    @property
    def has_api_key(self) -> bool:
        return bool(self.anthropic_api_key and self.anthropic_api_key.startswith("sk-"))

    @property
    def db_path(self) -> Path:
        p = Path(self.database_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        return p


def get_settings() -> Settings:
    """Load settings from st.secrets (Streamlit Cloud) first, then env vars."""
    overrides: dict[str, str] = {}
    try:
        import streamlit as st
        secrets = st.secrets
        # Map Streamlit secrets to Settings fields
        for key in [
            "ANTHROPIC_API_KEY", "CLAUDE_MODEL", "DATABASE_PATH",
            "AUTH_ENABLED", "RESEND_API_KEY", "OTP_FROM_EMAIL",
            "ALLOWED_EMAIL_DOMAINS",
        ]:
            if key in secrets:
                overrides[key] = str(secrets[key])
    except Exception:
        pass

    if overrides:
        return Settings(**overrides)
    return Settings()
