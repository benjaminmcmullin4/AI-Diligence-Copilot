from schemas.memo import CondensedInput, ICMemo
from pipeline.llm_client import call_llm
from pipeline.prompts import (
    STAGE_B_SAAS_SYSTEM,
    STAGE_B_NON_SAAS_SYSTEM,
    stage_b_user_prompt,
)


def run_stage_b(condensed: CondensedInput, business_model: str) -> ICMemo:
    """Stage B: Deep investment analysis, branching on SaaS vs Non-SaaS."""
    is_saas = business_model.lower() == "saas"
    system_prompt = STAGE_B_SAAS_SYSTEM if is_saas else STAGE_B_NON_SAAS_SYSTEM

    condensed_summary = condensed.model_dump_json(indent=2)

    user_prompt = stage_b_user_prompt(
        condensed_summary=condensed_summary,
        business_model=business_model,
    )

    memo = call_llm(
        response_model=ICMemo,
        system=system_prompt,
        user=user_prompt,
        max_tokens=16_000,
    )

    # Validate that the correct analysis branch is populated
    if is_saas and memo.saas_analysis is None:
        raise ValueError(
            "SaaS business model selected but saas_analysis was not populated by the LLM."
        )
    if not is_saas and memo.non_saas_analysis is None:
        raise ValueError(
            "Non-SaaS business model selected but non_saas_analysis was not populated by the LLM."
        )

    return memo
