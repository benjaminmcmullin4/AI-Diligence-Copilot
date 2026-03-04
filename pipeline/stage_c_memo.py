from schemas.memo import ICMemo, MemoOutput
from pipeline.llm_client import call_llm
from pipeline.prompts import STAGE_C_SYSTEM, stage_c_user_prompt


def run_stage_c(memo: ICMemo) -> MemoOutput:
    """Stage C: Render the structured IC analysis into Markdown and HTML memo."""
    memo_json = memo.model_dump_json(indent=2)

    user_prompt = stage_c_user_prompt(memo_json=memo_json)

    memo_output = call_llm(
        response_model=MemoOutput,
        system=STAGE_C_SYSTEM,
        user=user_prompt,
        max_tokens=16_000,
    )

    return memo_output
