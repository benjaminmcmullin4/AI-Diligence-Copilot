"""Tests for export modules."""

from export.markdown_export import generate_memo_markdown


class TestMarkdownExport:
    def test_generates_header(self):
        md = generate_memo_markdown(
            company_name="TestCo",
            memo_markdown="# Test Memo\n\nContent here.",
            business_model="saas",
        )
        assert "company: TestCo" in md
        assert "SaaS" in md
        assert "CONFIDENTIAL" in md
        assert "# Test Memo" in md

    def test_non_saas_label(self):
        md = generate_memo_markdown(
            company_name="RetailCo",
            memo_markdown="Content",
            business_model="non_saas",
        )
        assert "Non-SaaS" in md
