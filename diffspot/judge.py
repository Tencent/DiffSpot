"""LLM-as-Judge for DiffSpot.

The official judge is `gpt-oss-120b` with `reasoning_effort="high"` and
`temperature=0`, scoring each (GT description, GT mutations, model
prediction) triple under the prompt at `diffspot/prompts/judge.txt`. The
judge prompt is reproduced verbatim in the paper appendix.

For reproducibility, the judge model and prompt revision are pinned by
`JUDGE_VERSION` -- do not change without bumping the constant.

The judge uses an OpenAI-compatible client. By default it targets
`api.openai.com`; override with `OPENAI_BASE_URL` to point at any
OpenAI-compatible endpoint (vLLM, sglang, an internal gateway, etc.).
"""

from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path
from typing import Any

JUDGE_VERSION = "v2.0"
DEFAULT_JUDGE_MODEL = "gpt-oss-120b"
DEFAULT_REASONING_EFFORT = "high"
DEFAULT_TEMPERATURE = 0.0
DEFAULT_MAX_TOKENS = 16384

PROMPT_PATH = Path(__file__).parent / "prompts" / "judge.txt"
_PROMPT_BEGIN_MARKER = ">>> PROMPT BEGINS BELOW THIS LINE >>>"

_PROMPT_CACHE: str | None = None


def load_prompt() -> str:
    """Return the v2.0 judge prompt body (header comments stripped)."""
    global _PROMPT_CACHE
    if _PROMPT_CACHE is None:
        text = PROMPT_PATH.read_text(encoding="utf-8")
        if _PROMPT_BEGIN_MARKER in text:
            text = text.split(_PROMPT_BEGIN_MARKER, 1)[1]
        _PROMPT_CACHE = text.strip()
    return _PROMPT_CACHE


def render_prompt(*, gt_mutations: list[dict], gt_description: str, prediction: str) -> str:
    """Substitute the three template variables into the judge prompt.

    Uses ``str.replace`` (not ``str.format``) so that the literal JSON output
    schema in the prompt -- which contains its own ``{`` and ``}`` -- stays
    verbatim. This keeps ``judge.txt`` byte-identical to the paper appendix.
    """
    prompt = load_prompt()
    return (
        prompt
        .replace("{gt_json}", json.dumps(gt_mutations, ensure_ascii=False, indent=2))
        .replace("{gt_answer}", gt_description)
        .replace("{vlm_response}", prediction)
    )


def _parse_judge_json(raw: str) -> dict:
    """Extract a JSON object from a judge response.

    Tolerates ```json fences and leading/trailing prose, in case a model
    drifts from the strict-JSON instruction.
    """
    raw = raw.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
    if not raw.startswith("{"):
        m = re.search(r"\{.*\}", raw, flags=re.DOTALL)
        if m:
            raw = m.group(0)
    return json.loads(raw)


def _client():
    """Lazily construct an OpenAI-compatible client.

    Looks at ``OPENAI_API_KEY`` (required) and ``OPENAI_BASE_URL`` (optional).
    """
    try:
        from openai import OpenAI
    except ImportError as e:
        raise RuntimeError(
            "openai is required for the DiffSpot judge. "
            "Install with: pip install openai>=1.40.0"
        ) from e
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY environment variable is not set.")
    base_url = os.environ.get("OPENAI_BASE_URL")
    return OpenAI(api_key=api_key, base_url=base_url) if base_url else OpenAI(api_key=api_key)


def judge_item(
    *,
    gt_description: str,
    gt_mutations: list[dict],
    prediction: str,
    model: str = DEFAULT_JUDGE_MODEL,
    reasoning_effort: str | None = DEFAULT_REASONING_EFFORT,
    temperature: float = DEFAULT_TEMPERATURE,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    max_retries: int = 3,
    retry_backoff: float = 2.0,
) -> dict:
    """Score a single VLM prediction against GT mutations.

    Returns the v2.0 judge schema:

        {
          "mutations":      [{"gt": str, "type": str, "verdict": "correct"|"partial"|"missed", "vlm_match": str}, ...],
          "hallucinations": [str, ...],
          "summary":        {"correct": int, "partial": int, "missed": int, "hallucinated": int}
        }

    Aggregation rules used by ``diffspot.metrics``:
        has-diff: TP iff any ``mutations[*].verdict == "correct"``; else FN.
        no-diff:  TN iff ``hallucinations == []``; else FP.
    """
    rendered = render_prompt(
        gt_mutations=gt_mutations,
        gt_description=gt_description,
        prediction=prediction,
    )
    client = _client()

    last_error: Exception | None = None
    for attempt in range(max_retries):
        try:
            kwargs: dict[str, Any] = {
                "model": model,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "messages": [{"role": "user", "content": rendered}],
            }
            if reasoning_effort:
                kwargs["extra_body"] = {"reasoning_effort": reasoning_effort}
            resp = client.chat.completions.create(**kwargs)
            content = resp.choices[0].message.content or ""
            return _parse_judge_json(content)
        except (json.JSONDecodeError, ValueError) as e:
            last_error = e  # bad JSON: retry without backoff (model drift, not rate limit)
        except Exception as e:
            last_error = e
            time.sleep(retry_backoff ** attempt)

    raise RuntimeError(f"judge_item failed after {max_retries} retries: {last_error}")


def reduce_judge_label(label: dict, *, is_no_diff: bool) -> dict:
    """Reduce a raw v2.0 judge label to the binary outcomes used by metrics.

    Returns:
        {
            "is_true_positive":   bool,   # has-diff item correctly flagged
            "is_true_negative":   bool,   # no-diff item correctly left alone
            "n_correct_mutations": int,
            "n_hallucinations":   int,
        }
    """
    mutations = label.get("mutations", []) or []
    hallucinations = label.get("hallucinations", []) or []
    n_correct = sum(1 for m in mutations if m.get("verdict") == "correct")
    n_halluc = len(hallucinations)
    return {
        "is_true_positive": (not is_no_diff) and n_correct > 0,
        "is_true_negative": is_no_diff and n_halluc == 0,
        "n_correct_mutations": n_correct,
        "n_hallucinations": n_halluc,
    }
