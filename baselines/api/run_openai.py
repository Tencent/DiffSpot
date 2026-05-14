"""Run an OpenAI-hosted VLM (e.g. gpt-5.4) on the DiffSpot test set.

Usage:
    OPENAI_API_KEY=... python baselines/api/run_openai.py \
        --model gpt-5.4 \
        --output results/gpt-5.4/predictions.jsonl

Set ``OPENAI_BASE_URL`` to point at any OpenAI-compatible endpoint.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# Allow running as a script: ``python baselines/api/run_openai.py``
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
    parser.add_argument("--model", required=True, help="OpenAI model id (e.g. gpt-5.4)")
    parser.add_argument("--output", required=True, help="Output JSONL path")
    parser.add_argument("--dataset-revision", default=None, help="HF dataset revision pin")
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=16384,
        help="Min 16384 for thinking models; 4K causes silent truncation.",
    )
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument(
        "--reasoning-effort",
        default=None,
        help="Set to 'low'/'medium'/'high' for o-series / gpt-oss models.",
    )
    parser.add_argument(
        "--limit", type=int, default=None, help="Cap items processed (smoke test)."
    )
    args = parser.parse_args()

    try:
        import openai
    except ImportError:
        print("openai is required: pip install openai>=1.40.0", file=sys.stderr)
        return 1

    if not os.environ.get("OPENAI_API_KEY"):
        print("OPENAI_API_KEY not set", file=sys.stderr)
        return 1

    base_url = os.environ.get("OPENAI_BASE_URL")
    client = openai.OpenAI(base_url=base_url) if base_url else openai.OpenAI()

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
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{encode_image_b64(item.image_a)}"
                    },
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{encode_image_b64(item.image_b)}"
                    },
                },
            ]
            kwargs: dict = {
                "model": args.model,
                "messages": [{"role": "user", "content": content}],
                "temperature": args.temperature,
                "max_tokens": args.max_tokens,
            }
            if args.reasoning_effort:
                kwargs["extra_body"] = {"reasoning_effort": args.reasoning_effort}

            try:
                resp = client.chat.completions.create(**kwargs)
                raw = resp.choices[0].message.content or ""
            except (openai.OpenAIError, OSError, ValueError) as e:
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
