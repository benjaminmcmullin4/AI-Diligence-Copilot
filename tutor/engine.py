import streamlit as st
from tutor.classifier import classify_message, classify_image
from tutor.prompts import build_system_prompt


class TutorSession:
    def __init__(self, client, profile, messages=None):
        self.client = client
        self.profile = profile
        self.messages = messages or []
        self.current_subject = "general"
        self.current_topic = "general"

    def send_message_streaming(self, user_text, image_data=None, media_type=None):
        # Classify the input to get subject/topic context
        try:
            if image_data and not user_text.strip():
                classification = classify_image(
                    self.client, image_data, media_type
                )
            else:
                classification = classify_message(
                    self.client, user_text, self.profile["grade"]
                )
            self.current_subject = classification.get("subject", "general")
            self.current_topic = classification.get("topic", "general")
        except Exception:
            pass  # Keep previous classification on failure

        # Build system prompt with pedagogical context
        system_blocks = build_system_prompt(
            self.profile, self.current_subject, self.current_topic
        )

        # Build user message content
        content = []
        if image_data:
            content.append(
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": media_type or "image/jpeg",
                        "data": image_data,
                    },
                }
            )
        content.append({"type": "text", "text": user_text or "Can you help me with this homework?"})

        self.messages.append({"role": "user", "content": content})

        # Stream the response
        try:
            with self.client.messages.stream(
                model="claude-sonnet-4-6-20250514",
                max_tokens=4096,
                system=system_blocks,
                messages=self.messages,
            ) as stream:
                full_response = ""
                for text in stream.text_stream:
                    full_response += text
                    yield text

            self.messages.append({"role": "assistant", "content": full_response})

            # Update topics covered in profile
            if self.current_topic != "general":
                topics = self.profile.get("topics_covered", [])
                if self.current_topic not in topics:
                    topics.append(self.current_topic)
                    self.profile["topics_covered"] = topics

        except Exception as e:
            error_msg = f"Oops! Something went wrong. Let's try again! ({type(e).__name__})"
            self.messages.append({"role": "assistant", "content": error_msg})
            yield error_msg


def get_or_create_session(client, profile):
    """Get existing session or create new one, preserving message history across reruns."""
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    if "tutor_messages" not in st.session_state:
        st.session_state.tutor_messages = []

    session = TutorSession(
        client=client,
        profile=profile,
        messages=st.session_state.tutor_messages,
    )

    # Restore classification state
    session.current_subject = st.session_state.get("current_subject", "general")
    session.current_topic = st.session_state.get("current_topic", "general")

    return session


def save_session_state(session):
    """Persist session data to session state after each interaction."""
    st.session_state.tutor_messages = session.messages
    st.session_state.current_subject = session.current_subject
    st.session_state.current_topic = session.current_topic


def reset_session():
    """Clear all chat state for a new conversation."""
    st.session_state.chat_messages = []
    st.session_state.tutor_messages = []
    st.session_state.current_subject = "general"
    st.session_state.current_topic = "general"
    if "uploaded_image" in st.session_state:
        del st.session_state.uploaded_image
