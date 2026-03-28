import streamlit as st
from tutor.profile import save_profile


def render_welcome():
    # Decorative header
    st.markdown(
        """
        <div class="welcome-container">
            <div class="welcome-decorations">&#9997; &#128218; &#11088; &#127912; &#128640;</div>
            <div class="welcome-title">Homework Helper</div>
            <div class="welcome-tagline">I won't give you the answers... but I'll help you figure them out!</div>
            <div class="crayon-border"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Info card
    st.markdown(
        """
        <div class="info-card">
            <strong>How it works:</strong><br>
            &#128172; Ask me any homework question<br>
            &#128248; Or upload a photo of your worksheet<br>
            &#129504; I'll guide you step-by-step (no answers given away!)<br>
            &#127942; You'll actually learn it and feel awesome!
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # Onboarding form
    st.markdown("### Let's get to know you!")

    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input(
            "What's your name?",
            placeholder="Type your name here...",
            max_chars=50,
        )

    with col2:
        grade = st.selectbox(
            "What grade are you in?",
            options=[3, 4, 5, 6, 7, 8],
            format_func=lambda g: f"Grade {g}",
            index=2,  # Default to grade 5
        )

    subjects = st.multiselect(
        "What subjects do you need help with?",
        options=["Math", "English"],
        default=["Math"],
    )

    st.markdown("")  # Spacing

    col_left, col_center, col_right = st.columns([1, 2, 1])
    with col_center:
        if st.button("Let's Go! &#127881;", use_container_width=True):
            if not name.strip():
                st.warning("Don't forget to type your name!")
                return
            if not subjects:
                st.warning("Pick at least one subject!")
                return

            profile = {
                "name": name.strip(),
                "grade": grade,
                "subjects": [s.lower() for s in subjects],
                "learning_style": "unknown",
                "session_count": 0,
                "topics_covered": [],
            }
            save_profile(profile)
            st.rerun()
