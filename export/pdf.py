"""PDF export using WeasyPrint."""

from datetime import datetime, timezone
from pathlib import Path

from jinja2 import Template

TEMPLATE_DIR = Path(__file__).parent / "templates"


def _load_css() -> str:
    css_path = TEMPLATE_DIR / "memo.css"
    if css_path.exists():
        return css_path.read_text(encoding="utf-8")
    return ""


def _load_template() -> Template:
    html_path = TEMPLATE_DIR / "memo.html"
    return Template(html_path.read_text(encoding="utf-8"))


def generate_memo_pdf(
    company_name: str,
    memo_html_content: str,
    business_model: str = "saas",
    sector: str = "",
) -> bytes:
    """Generate a professional PDF from memo HTML content.

    Returns PDF as bytes.
    """
    try:
        from weasyprint import HTML
    except ImportError:
        raise RuntimeError(
            "WeasyPrint is not installed. Install with: pip install weasyprint"
        )

    template = _load_template()
    inline_css = _load_css()
    date_str = datetime.now(timezone.utc).strftime("%B %Y")
    bm_label = "SaaS" if business_model == "saas" else "Non-SaaS"

    full_html = template.render(
        company_name=company_name,
        memo_html_content=memo_html_content,
        inline_css=inline_css,
        date=date_str,
        sector=sector or ("Software / SaaS" if business_model == "saas" else "Consumer / Retail"),
        business_model_label=bm_label,
    )

    html_doc = HTML(string=full_html, base_url=str(TEMPLATE_DIR))
    return html_doc.write_pdf()


def save_memo_pdf(
    output_path: str | Path,
    company_name: str,
    memo_html_content: str,
    business_model: str = "saas",
    sector: str = "",
) -> Path:
    """Generate and save a PDF to disk."""
    pdf_bytes = generate_memo_pdf(company_name, memo_html_content, business_model, sector)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(pdf_bytes)
    return output_path
