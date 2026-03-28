import streamlit as st
from tutor.engine import reset_session
from tutor.profile import save_profile


def render_sidebar(profile):
    with st.sidebar:
        # Student info header
        st.markdown(f"### &#11088; {profile['name']}")

        # Grade badge
        st.markdown(
            f'<span class="grade-badge">Grade {profile["grade"]}</span>',
            unsafe_allow_html=True,
        )

        # Subject badges
        badges_html = ""
        for subj in profile["subjects"]:
            css_class = "math" if subj == "math" else "english"
            label = subj.title()
            badges_html += f'<span class="subject-badge {css_class}">{label}</span> '
        st.markdown(badges_html, unsafe_allow_html=True)

        st.markdown("---")

        # Session stats
        msg_count = len(st.session_state.get("chat_messages", []))
        user_msgs = msg_count // 2 if msg_count > 0 else 0
        st.markdown(f"**Messages this session:** {user_msgs}")

        topics = profile.get("topics_covered", [])
        if topics:
            topics_str = ", ".join(t.replace("_", " ").title() for t in topics[-5:])
            st.markdown(f"**Topics covered:** {topics_str}")

        st.markdown("---")

        # New Chat button
        if st.button("&#127912; New Chat", use_container_width=True):
            reset_session()
            st.rerun()

        st.markdown("---")

        # Homework upload
        st.markdown("### &#128248; Upload Homework")
        uploaded_file = st.file_uploader(
            "Take a photo or upload an image/PDF",
            type=["jpg", "jpeg", "png", "gif", "webp", "pdf"],
            label_visibility="collapsed",
        )

        if uploaded_file is not None:
            # Only set upload data if not already processed
            already_sent = st.session_state.get("uploaded_image_sent", False)
            if not already_sent and "uploaded_image" not in st.session_state:
                is_pdf = uploaded_file.type == "application/pdf"
                st.session_state.uploaded_image = {
                    "bytes": uploaded_file.getvalue(),
                    "name": uploaded_file.name,
                    "type": uploaded_file.type,
                    "is_pdf": is_pdf,
                }
                if is_pdf:
                    st.success(f"PDF ready: {uploaded_file.name}")
                else:
                    st.image(uploaded_file, caption="Ready to help with this!", use_container_width=True)
                st.info("Ask a question about this in the chat!")
            elif already_sent:
                if uploaded_file.type == "application/pdf":
                    st.success(f"PDF sent: {uploaded_file.name}")
                else:
                    st.image(uploaded_file, caption="Already sent!", use_container_width=True)

        st.markdown("---")

        # About section
        with st.expander("About Homework Helper"):
            st.markdown(
                """
                **Homework Helper** is your friendly AI tutor!

                **What I do:**
                - Help you understand your homework
                - Give hints and guide you step-by-step
                - Celebrate when you get it right!

                **What I don't do:**
                - Give you the answers (sorry!)
                - Do your homework for you
                - Judge you for asking questions

                *Every question is a good question!*
                """
            )

        st.markdown("---")

        # Change profile
        with st.expander("Change Profile"):
            new_name = st.text_input("Name", value=profile["name"], key="edit_name")
            new_grade = st.selectbox(
                "Grade",
                options=[3, 4, 5, 6, 7, 8],
                index=profile["grade"] - 3,
                key="edit_grade",
            )
            new_subjects = st.multiselect(
                "Subjects",
                options=["Math", "English"],
                default=[s.title() for s in profile["subjects"]],
                key="edit_subjects",
            )
            if st.button("Update Profile", key="update_profile"):
                profile["name"] = new_name.strip() or profile["name"]
                profile["grade"] = new_grade
                profile["subjects"] = [s.lower() for s in new_subjects]
                save_profile(profile)
                reset_session()
                st.rerun()
