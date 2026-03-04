"""Tests for pipeline modules (non-LLM logic)."""

from pipeline.prompts import STAGE_A_SYSTEM, STAGE_B_SAAS_SYSTEM, STAGE_B_NON_SAAS_SYSTEM
from pipeline.prompts import stage_a_user_prompt


class TestPrompts:
    def test_stage_a_system_prompt_exists(self):
        assert "growth equity" in STAGE_A_SYSTEM.lower()

    def test_stage_b_saas_system_mentions_nrr(self):
        assert "NRR" in STAGE_B_SAAS_SYSTEM or "net revenue retention" in STAGE_B_SAAS_SYSTEM.lower()

    def test_stage_b_non_saas_mentions_ebitda(self):
        assert "EBITDA" in STAGE_B_NON_SAAS_SYSTEM

    def test_stage_a_user_prompt_includes_company(self):
        prompt = stage_a_user_prompt(
            company_name="TestCo",
            business_model="saas",
            financial_summary="ARR: $10M",
            website_text="We make software.",
            company_description="B2B SaaS company",
            internal_notes="Strong team",
            customer_reviews="Great product",
            call_transcripts="",
            management_bios="CEO: John",
            known_competitors="Acme",
            uploaded_text="",
        )
        assert "TestCo" in prompt
        assert "ARR: $10M" in prompt
