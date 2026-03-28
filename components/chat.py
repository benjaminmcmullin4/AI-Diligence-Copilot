import base64
import io

import streamlit as st
from PIL import Image

from tutor.engine import save_session_state


def _resize_image(image_bytes, max_size=1568):
    """Resize image so longest edge is at most max_size pixels."""
    img = Image.open(io.BytesIO(image_bytes))
    w, h = img.size
    if max(w, h) <= max_size:
        # Already small enough, return original bytes
        return image_bytes
    scale = max_size / max(w, h)
    new_w, new_h = int(w * scale), int(h * scale)
    img = img.resize((new_w, new_h), Image.LANCZOS)
    buf = io.BytesIO()
    fmt = img.format or "JPEG"
    if fmt.upper() not in ("JPEG", "PNG", "GIF", "WEBP"):
        fmt = "JPEG"
    img.save(buf, format=fmt)
    return buf.getvalue()


def _get_media_type(file_type):
    """Convert file type string to media type."""
    type_map = {
        "image/jpeg": "image/jpeg",
        "image/jpg": "image/jpeg",
        "image/png": "image/png",
        "image/gif": "image/gif",
        "image/webp": "image/webp",
    }
    return type_map.get(file_type, "image/jpeg")


def render_chat(session, profile):
    # Initialize chat messages display list
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    # Welcome message if empty chat
    if not st.session_state.chat_messages:
        grade = profile["grade"]
        name = profile["name"]
        subjects = " and ".join(s.title() for s in profile["subjects"])

        if grade <= 5:
            welcome = (
                f"Hi {name}! I'm your Homework Helper! "
                f"I'm here to help you with {subjects}. "
                f"Ask me anything, or upload a photo of your homework! "
                f"Remember -- I won't just give you answers, but I'll help you figure things out. "
                f"You've got this!"
            )
        else:
            welcome = (
                f"Hey {name}! Welcome to Homework Helper. "
                f"I'm here to help you work through {subjects} problems. "
                f"You can type a question or upload a photo of your assignment. "
                f"I'll guide you step-by-step -- no free answers, but I promise it'll make sense. "
                f"Let's get started!"
            )

        st.session_state.chat_messages.append(
            {"role": "assistant", "content": welcome}
        )

    # Render chat history
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            # If message has an image, show it
            if msg.get("image_bytes"):
                st.image(msg["image_bytes"], width=300)
            st.markdown(msg["content"])

    # Check for pending uploaded image
    pending_image = None
    pending_media_type = None
    if "uploaded_image" in st.session_state:
        img_data = st.session_state.uploaded_image
        pending_image = img_data["bytes"]
        pending_media_type = _get_media_type(img_data["type"])

    # Chat input
    user_input = st.chat_input(
        "Ask me anything about your homework..."
    )

    if user_input:
        # Prepare image data if present
        image_b64 = None
        display_image = None
        if pending_image:
            resized = _resize_image(pending_image)
            image_b64 = base64.standard_b64encode(resized).decode("utf-8")
            display_image = pending_image
            # Clear the uploaded image
            del st.session_state.uploaded_image

        # Add user message to display history
        user_msg = {"role": "user", "content": user_input}
        if display_image:
            user_msg["image_bytes"] = display_image
        st.session_state.chat_messages.append(user_msg)

        # Display user message
        with st.chat_message("user"):
            if display_image:
                st.image(display_image, width=300)
            st.markdown(user_input)

        # Stream assistant response
        with st.chat_message("assistant"):
            response = st.write_stream(
                session.send_message_streaming(
                    user_text=user_input,
                    image_data=image_b64,
                    media_type=pending_media_type,
                )
            )

        # Save assistant response to display history
        st.session_state.chat_messages.append(
            {"role": "assistant", "content": response}
        )

        # Persist session state
        save_session_state(session)
