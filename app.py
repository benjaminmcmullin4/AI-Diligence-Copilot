import anthropic
import streamlit as st
from pathlib import Path

from tutor.profile import get_profile, is_onboarded
from tutor.engine import get_or_create_session
from components.welcome import render_welcome
from components.sidebar import render_sidebar
from components.chat import render_chat

# --- Page Config (must be first Streamlit command) ---
st.set_page_config(
    page_title="Homework Helper",
    page_icon="&#9997;",
    layout="centered",
    initial_sidebar_state="auto",
)

# --- Load Google Fonts ---
st.markdown(
    """
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Caveat:wght@400;700&family=Gaegu:wght@400;700&family=Patrick+Hand&display=swap" rel="stylesheet">
    """,
    unsafe_allow_html=True,
)

# --- Load Crayon Theme CSS ---
css_path = Path(__file__).parent / "styles" / "crayon.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)


# --- Initialize Anthropic Client ---
@st.cache_resource
def get_client():
    api_key = st.secrets.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return None
    return anthropic.Anthropic(api_key=api_key)


client = get_client()

# --- Check for API Key ---
if client is None:
    st.markdown(
        """
        <div class="welcome-container">
            <div class="welcome-title">Homework Helper</div>
            <div class="crayon-border"></div>
        </div>
        <div class="error-card">
            <h3>&#128272; Setup Needed</h3>
            <p>The <strong>ANTHROPIC_API_KEY</strong> secret hasn't been set up yet.</p>
            <p>If you're the app owner, add it in Streamlit Cloud under Settings > Secrets.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

# --- Main App Routing ---
if not is_onboarded():
    render_welcome()
else:
    profile = get_profile()
    render_sidebar(profile)

    # App title in main area
    st.markdown(
        '<div style="text-align:center; margin-bottom: 0.5rem;">'
        '<span style="font-family: Gaegu, cursive; font-size: 2rem; color: #A66CFF;">'
        "&#9997; Homework Helper"
        "</span></div>",
        unsafe_allow_html=True,
    )

    session = get_or_create_session(client, profile)
    render_chat(session, profile)
