"""Clean Markdown export for IC memos."""

from datetime import datetime, timezone


def generate_memo_markdown(
    company_name: str,
    memo_markdown: str,
    business_model: str = "saas",
) -> str:
    """Wrap raw memo markdown with header and footer."""
    date_str = datetime.now(timezone.utc).strftime("%B %d, %Y")
    bm_label = "SaaS" if business_model == "saas" else "Non-SaaS"

    header = (
        f"---\n"
        f"company: {company_name}\n"
        f"type: Investment Committee Memorandum\n"
        f"business_model: {bm_label}\n"
        f"date: {date_str}\n"
        f"prepared_by: Traverse Diligence Copilot\n"
        f"classification: CONFIDENTIAL\n"
        f"---\n\n"
    )

    footer = (
        f"\n\n---\n\n"
        f"*Confidential — Prepared by Traverse Diligence Copilot on {date_str}*\n"
    )

    return header + memo_markdown + footer
