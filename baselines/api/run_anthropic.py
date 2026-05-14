"""Run an Anthropic-hosted VLM (e.g. claude-opus-4-7) on the DiffSpot test set.

Usage:
    ANTHROPIC_API_KEY=... python baselines/api/run_anthropic.py \
        --model claude-opus-4-7 \
        --output results/claude-opus-4-7/predictions.jsonl
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from baselines._common import (  # noqa: E402
    PROMPT_VERSION,
    already_done,
    encode_image_b64,
    load_vlm_prompt,
    write_record,
)
from diffspot.data import load  # noqa: E402


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
        import anthropic
    except ImportError:
        print("anthropic is required: pip install anthropic>=0.34.0", file=sys.stderr)
        return 1

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ANTHROPIC_API_KEY not set", file=sys.stderr)
        return 1

    client = anthropic.Anthropic()
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

            content = [
                {"type": "text", "text": load_vlm_prompt(item.split)},
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": encode_image_b64(item.image_a),
                    },
                },
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": encode_image_b64(item.image_b),
                    },
                },
            ]
            try:
                resp = client.messages.create(
                    model=args.model,
                    max_tokens=args.max_tokens,
                    temperature=args.temperature,
                    messages=[{"role": "user", "content": content}],
                )
                raw = "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")
            except (anthropic.AnthropicError, OSError, ValueError) as e:
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
