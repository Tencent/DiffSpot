"""LLM-as-Judge for DiffSpot.

The official judge is `gpt-oss-120b` with `reasoning_effort="high"`, scoring
each (GT description, model prediction) pair under the prompt at
`diffspot/prompts/judge.txt`. The judge prompt is also reproduced verbatim in
the paper appendix.

For reproducibility, the judge model and prompt revision are pinned by
the `JUDGE_VERSION` constant — do not change without bumping the constant.
"""

from __future__ import annotations

from pathlib import Path

JUDGE_VERSION = "v1.0"
DEFAULT_JUDGE_MODEL = "gpt-oss-120b"
DEFAULT_REASONING_EFFORT = "high"

PROMPT_PATH = Path(__file__).parent / "prompts" / "judge.txt"


def load_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


def judge_item(
    gt_description: str,
    gt_mutations: list[dict],
    prediction: str,
    *,
    model: str = DEFAULT_JUDGE_MODEL,
    reasoning_effort: str = DEFAULT_REASONING_EFFORT,
) -> dict:
    """Score a single prediction against GT.

    Returns a label dict (matched_gt_count, total_gt_count,
    reported_diff_count, correct_diff_count, reported_any_change, ...).
    """
    raise NotImplementedError("judge_item() not yet implemented.")
