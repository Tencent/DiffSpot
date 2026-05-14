"""Run a Google-hosted VLM (e.g. gemini-3.1-pro) on the DiffSpot test set.

Usage:
    GOOGLE_API_KEY=... python baselines/api/run_gemini.py \
        --model gemini-3.1-pro \
        --output results/gemini-3.1-pro/predictions.jsonl
"""

from __future__ import annotations

import argparse
import io
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from baselines._common import (  # noqa: E402
    PROMPT_VERSION,
    already_done,
    load_vlm_prompt,
    write_record,
)
from diffspot.data import load  # noqa: E402


def _to_pil_bytes(img) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--dataset-revision", default=None)
    parser.add_argument("--max-tokens", type=int, default=16384)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    try:
        import google.generativeai as genai
        from google.api_core import exceptions as google_exceptions
    except ImportError:
        print(
            "google-generativeai is required: pip install google-generativeai>=0.7.0",
            file=sys.stderr,
        )
        return 1

    api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("GOOGLE_API_KEY (or GEMINI_API_KEY) not set", file=sys.stderr)
        return 1
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(args.model)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    done = already_done(output_path)
    if done:
        print(f"Resuming: {len(done)} predictions already in {output_path}", file=sys.stderr)

    n_processed = 0
    with output_path.open("a") as f_out:
        for item in load(split="all", revision=args.dataset_revision):
            if item.id in done:
                continue
            if args.limit is not None and n_processed >= args.limit:
                break

            try:
                resp = model.generate_content(
                    [
                        load_vlm_prompt(item.split),
                        {"mime_type": "image/png", "data": _to_pil_bytes(item.image_a)},
                        {"mime_type": "image/png", "data": _to_pil_bytes(item.image_b)},
                    ],
                    generation_config={
                        "temperature": args.temperature,
                        "max_output_tokens": args.max_tokens,
                    },
                )
                raw = resp.text or ""
            except (google_exceptions.GoogleAPIError, OSError, ValueError) as e:
                print(f"  [error] id={item.id}: {e}", file=sys.stderr)
                continue

            write_record(f_out, id_=item.id, split=item.split, model=args.model, raw=raw)
            n_processed += 1
            if n_processed % 50 == 0:
                print(f"  processed {n_processed}", file=sys.stderr)

    print(
        f"\nDone. New: {n_processed}. Total in file: {n_processed + len(done)}. "
        f"Prompt version: {PROMPT_VERSION}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
