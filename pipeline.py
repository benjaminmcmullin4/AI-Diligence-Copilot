"""Three-stage LLM pipeline for investment due diligence.

Consolidates: LLM client, Stage A (Condense), Stage B (Analysis),
Stage C (Memo Rendering), and the orchestrator.
"""

from __future__ import annotations

import logging
import traceback
from typing import Callable

import instructor
from anthropic import Anthropic
from pydantic import BaseModel

from config import DB_PATH, DEFAULT_MODEL, MAX_RETRIES, MAX_TOKENS, get_api_key
from db import save_analysis
from extract import extract_website_text
from prompts import (
    STAGE_A_SYSTEM,
    STAGE_B_NON_SAAS_SYSTEM,
    STAGE_B_SAAS_SYSTEM,
    STAGE_C_SYSTEM,
    stage_a_user_prompt,
    stage_b_user_prompt,
    stage_c_user_prompt,
)
from schema import (
    AnalysisRequest,
    CondensedInput,
    ICMemo,
    MemoOutput,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════
# LLM Client
# ═══════════════════════════════════════════════════════════════════════════

def _get_llm_client():
    """Create an instructor-wrapped Anthropic client."""
    client = Anthropic(api_key=get_api_key())
    return instructor.from_anthropic(client)


def _call_llm(
    response_model: type[BaseModel],
    system: str,
    user: str,
    max_tokens: int | None = None,
) -> BaseModel:
    """Call the LLM with structured output parsing via instructor."""
    client = _get_llm_client()
    return client.chat.completions.create(
        model=DEFAULT_MODEL,
        max_tokens=max_tokens or MAX_TOKENS,
        max_retries=MAX_RETRIES,
        messages=[{"role": "user", "content": user}],
        system=system,
        response_model=response_model,
    )


# ═══════════════════════════════════════════════════════════════════════════
# Stage A: Condense
# ═══════════════════════════════════════════════════════════════════════════

def step_condense(request: AnalysisRequest, website_text: str = "") -> CondensedInput:
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

    condensed = _call_llm(
        response_model=CondensedInput,
        system=STAGE_A_SYSTEM,
        user=user_prompt,
    )

    return condensed


# ═══════════════════════════════════════════════════════════════════════════
# Stage B: Analysis
# ═══════════════════════════════════════════════════════════════════════════

def step_analysis(condensed: CondensedInput, business_model: str) -> ICMemo:
    """Stage B: Deep investment analysis, branching on SaaS vs Non-SaaS."""
    is_saas = business_model.lower() == "saas"
    system_prompt = STAGE_B_SAAS_SYSTEM if is_saas else STAGE_B_NON_SAAS_SYSTEM

    condensed_summary = condensed.model_dump_json(indent=2)

    user_prompt = stage_b_user_prompt(
        condensed_summary=condensed_summary,
        business_model=business_model,
    )

    memo = _call_llm(
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


# ═══════════════════════════════════════════════════════════════════════════
# Stage C: Memo
# ═══════════════════════════════════════════════════════════════════════════

def step_memo(memo: ICMemo) -> MemoOutput:
    """Stage C: Render the structured IC analysis into Markdown and HTML memo."""
    memo_json = memo.model_dump_json(indent=2)

    user_prompt = stage_c_user_prompt(memo_json=memo_json)

    memo_output = _call_llm(
        response_model=MemoOutput,
        system=STAGE_C_SYSTEM,
        user=user_prompt,
        max_tokens=16_000,
    )

    return memo_output


# ═══════════════════════════════════════════════════════════════════════════
# Orchestrator
# ═══════════════════════════════════════════════════════════════════════════

def run_pipeline(
    request: AnalysisRequest,
    analysis_id: str,
    progress_callback: Callable[[str, str], None] | None = None,
) -> dict:
    """Orchestrate the three-stage LLM pipeline for investment due diligence.

    Args:
        request: The validated AnalysisRequest with all raw inputs.
        analysis_id: Unique identifier for this analysis run.
        progress_callback: Optional callback(stage, status) for UI updates.

    Returns:
        dict with keys: condensed, analysis, memo, markdown, status, error.
    """
    result: dict = {
        "condensed": None,
        "analysis": None,
        "memo": None,
        "markdown": None,
        "status": "running",
        "error": None,
    }

    def _notify(stage: str, status: str) -> None:
        if progress_callback:
            try:
                progress_callback(stage, status)
            except Exception:
                pass

    try:
        # ── Optional: Fetch website text ──────────────────────────────
        website_text = ""
        if request.fetch_website and request.website_url:
            _notify("website_fetch", "running")
            try:
                website_text = extract_website_text(str(request.website_url))
                _notify("website_fetch", "complete")
            except Exception as exc:
                logger.warning("Website fetch failed: %s", exc)
                _notify("website_fetch", "failed")

        # ── Stage A: Condense ─────────────────────────────────────────
        _notify("stage_a", "running")
        condensed: CondensedInput = step_condense(request, website_text=website_text)
        result["condensed"] = condensed

        save_analysis(analysis_id, {
            "condensed_json": condensed.model_dump_json(),
            "status": "stage_a_complete",
        })
        _notify("stage_a", "complete")

        # ── Stage B: Analysis ─────────────────────────────────────────
        _notify("stage_b", "running")
        business_model = condensed.business_model or (
            request.business_model.value if request.business_model else "saas"
        )
        ic_memo: ICMemo = step_analysis(condensed, business_model)
        result["analysis"] = ic_memo

        save_analysis(analysis_id, {
            "analysis_json": ic_memo.model_dump_json(),
            "status": "stage_b_complete",
        })
        _notify("stage_b", "complete")

        # ── Stage C: Memo ─────────────────────────────────────────────
        _notify("stage_c", "running")
        memo_output: MemoOutput = step_memo(ic_memo)
        result["memo"] = memo_output
        result["markdown"] = memo_output.memo_markdown

        save_analysis(analysis_id, {
            "memo_json": memo_output.model_dump_json(),
            "memo_markdown": memo_output.memo_markdown,
            "status": "completed",
        })
        _notify("stage_c", "complete")

        result["status"] = "completed"

    except Exception as exc:
        error_msg = f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}"
        logger.error("Pipeline failed for analysis %s: %s", analysis_id, error_msg)
        result["status"] = "failed"
        result["error"] = str(exc)

        try:
            save_analysis(analysis_id, {
                "status": "failed",
                "error_message": str(exc),
            })
        except Exception as db_exc:
            logger.error("Failed to update DB with error status: %s", db_exc)

        _notify("pipeline", "failed")

    return result
