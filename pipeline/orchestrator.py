"""Pipeline orchestrator — runs the 3-stage LLM pipeline."""

import logging
import traceback
from typing import Callable

from core.config import get_settings
from core.database import save_analysis
from core.extract import extract_website_text
from pipeline.stage_a_condense import run_stage_a
from pipeline.stage_b_analysis import run_stage_b
from pipeline.stage_c_memo import run_stage_c
from schemas.input import AnalysisRequest
from schemas.memo import CondensedInput, ICMemo, MemoOutput

logger = logging.getLogger(__name__)


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
    settings = get_settings()
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
        condensed: CondensedInput = run_stage_a(request, website_text=website_text)
        result["condensed"] = condensed

        save_analysis(settings.db_path, analysis_id, {
            "condensed_json": condensed.model_dump_json(),
            "status": "stage_a_complete",
        })
        _notify("stage_a", "complete")

        # ── Stage B: Analysis ─────────────────────────────────────────
        _notify("stage_b", "running")
        business_model = condensed.business_model or (
            request.business_model.value if request.business_model else "saas"
        )
        memo: ICMemo = run_stage_b(condensed, business_model)
        result["analysis"] = memo

        save_analysis(settings.db_path, analysis_id, {
            "analysis_json": memo.model_dump_json(),
            "status": "stage_b_complete",
        })
        _notify("stage_b", "complete")

        # ── Stage C: Memo ─────────────────────────────────────────────
        _notify("stage_c", "running")
        memo_output: MemoOutput = run_stage_c(memo)
        result["memo"] = memo_output
        result["markdown"] = memo_output.memo_markdown

        save_analysis(settings.db_path, analysis_id, {
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
            save_analysis(settings.db_path, analysis_id, {
                "status": "failed",
                "error_message": str(exc),
            })
        except Exception as db_exc:
            logger.error("Failed to update DB with error status: %s", db_exc)

        _notify("pipeline", "failed")

    return result
