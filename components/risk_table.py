"""Risk table component with severity color coding."""

import streamlit as st

from schemas.common import Risk


def _severity_badge(severity: int) -> str:
    """Return an HTML badge for the severity level."""
    labels = {1: "Low", 2: "Moderate", 3: "Medium", 4: "High", 5: "Critical"}
    label = labels.get(severity, str(severity))
    return f'<span class="risk-badge severity-{severity}">{severity} - {label}</span>'


def _likelihood_display(likelihood: int) -> str:
    """Return a text representation of likelihood."""
    labels = {1: "Unlikely", 2: "Possible", 3: "Moderate", 4: "Likely", 5: "Very Likely"}
    return f"{likelihood}/5 ({labels.get(likelihood, '')})"


def render_risk_table(risks: list[Risk]) -> None:
    """Render a styled HTML table of Risk objects.

    Args:
        risks: List of Risk objects to display.
    """
    if not risks:
        st.info("No risks identified.")
        return

    rows_html = ""
    for risk in risks:
        rows_html += f"""
        <tr>
            <td><strong>{risk.category}</strong></td>
            <td>{risk.description}</td>
            <td>{_severity_badge(risk.severity)}</td>
            <td>{_likelihood_display(risk.likelihood)}</td>
            <td>{risk.mitigant}</td>
            <td style="font-style: italic;">{risk.diligence_question}</td>
        </tr>
        """

    html = f"""
    <table class="risk-table">
        <thead>
            <tr>
                <th>Category</th>
                <th>Description</th>
                <th>Severity</th>
                <th>Likelihood</th>
                <th>Mitigant</th>
                <th>Diligence Question</th>
            </tr>
        </thead>
        <tbody>
            {rows_html}
        </tbody>
    </table>
    """
    st.markdown(html, unsafe_allow_html=True)
