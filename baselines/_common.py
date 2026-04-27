"""Shared helpers for baseline runners.

All runners follow the same pattern: stream DiffSpot items, encode the two
screenshots, call the model with the canonical prompts, and append-write a
predictions JSONL with the schema documented in ``baselines/README.md``.
"""

from __future__ import annotations

import base64
import io
import json
from pathlib import Path

PROMPT_DIR = Path(__file__).resolve().parents[1] / "diffspot" / "prompts"
PROMPT_VERSION = "v1.0"
_PROMPT_BEGIN_MARKER = ">>> PROMPT BEGINS BELOW THIS LINE >>>"


def load_vlm_prompt(split: str) -> str:
    """Return the canonical VLM prompt for ``split``, header comments stripped."""
    fname = "vlm_nodiff.txt" if split == "no_diff" else "vlm_diff.txt"
    text = (PROMPT_DIR / fname).read_text(encoding="utf-8")
    if _PROMPT_BEGIN_MARKER in text:
        text = text.split(_PROMPT_BEGIN_MARKER, 1)[1]
    return text.strip()


def encode_image_b64(img) -> str:
    """PIL Image -> base64 PNG string."""
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("ascii")


def already_done(output_path: Path) -> set[str]:
    """Return the set of ids already present in an existing predictions JSONL."""
    if not output_path.exists():
        return set()
    seen: set[str] = set()
    with output_path.open() as f:
        for line in f:
            try:
                seen.add(json.loads(line)["id"])
            except (json.JSONDecodeError, KeyError):
                pass
    return seen


def write_record(f_out, *, id_: str, split: str, model: str, raw: str, prediction: str | None = None) -> None:
    record = {
        "id": id_,
        "split": split,
        "model": model,
        "prompt_version": PROMPT_VERSION,
        "raw_response": raw,
        "prediction": prediction if prediction is not None else raw,
    }
    f_out.write(json.dumps(record, ensure_ascii=False) + "\n")
    f_out.flush()
