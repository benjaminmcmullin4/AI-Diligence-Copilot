import streamlit as st


def get_profile():
    return st.session_state.get("student_profile", None)


def save_profile(profile):
    st.session_state["student_profile"] = profile


def is_onboarded():
    return get_profile() is not None


def get_profile_context_string(profile):
    grade = profile["grade"]
    name = profile["name"]
    subjects = " and ".join(profile["subjects"])

    grade_band = "elementary school"
    if grade >= 6:
        grade_band = "middle school"

    lines = [
        f"The student's name is {name}.",
        f"They are in {grade}th grade ({grade_band}).",
        f"They need help with: {subjects}.",
    ]

    style = profile.get("learning_style", "unknown")
    if style != "unknown":
        lines.append(f"Their preferred learning style is: {style}.")

    topics = profile.get("topics_covered", [])
    if topics:
        lines.append(f"Topics covered this session: {', '.join(topics)}.")

    return "\n".join(lines)
