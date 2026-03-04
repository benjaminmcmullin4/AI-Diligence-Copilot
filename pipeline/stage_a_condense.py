from schemas.input import AnalysisRequest
from schemas.memo import CondensedInput
from pipeline.llm_client import call_llm
from pipeline.prompts import STAGE_A_SYSTEM, stage_a_user_prompt


def run_stage_a(request: AnalysisRequest, website_text: str = "") -> CondensedInput:
    """Stage A: Condense raw due diligence inputs into a structured summary."""
    user_prompt = stage_a_user_prompt(
        company_name=request.company_name,
        business_model=request.business_model.value if request.business_model else "",
        financial_summary=request.get_financial_summary(),
        website_text=website_text,
        company_description=request.company_description or "",
        internal_notes=request.internal_notes or "",
        customer_reviews=request.customer_reviews or "",
        call_transcripts=request.call_transcripts or "",
        management_bios=request.management_bios or "",
        known_competitors=request.known_competitors or "",
        uploaded_text=request.uploaded_text or "",
    )

    condensed = call_llm(
        response_model=CondensedInput,
        system=STAGE_A_SYSTEM,
        user=user_prompt,
    )

    return condensed
