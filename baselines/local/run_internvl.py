"""Run a self-hosted InternVL endpoint (sglang / vllm) on DiffSpot.

Usage:
    python baselines/local/run_internvl.py \
        --endpoint http://<host>:30000/v1 \
        --model InternVL3.5-30B-A3B \
        --output results/internvl3.5-30b-a3b/predictions.jsonl

Identical wire-format to ``run_qwen3vl.py``; kept as a separate file so
model-specific quirks (token limits, reasoning parsers) can be added without
forking the Qwen runner.
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
    parser.add_argument("--endpoint", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--dataset-revision", default=None)
    parser.add_argument("--max-tokens", type=int, default=16384)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    try:
        import openai
    except ImportError:
        print("openai is required: pip install openai>=1.40.0", file=sys.stderr)
        return 1

    client = openai.OpenAI(
        base_url=args.endpoint,
        api_key=os.environ.get("OPENAI_API_KEY", "EMPTY"),
    )

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
            try:
                resp = client.chat.completions.create(
                    model=args.model,
                    messages=[{"role": "user", "content": content}],
                    temperature=args.temperature,
                    max_tokens=args.max_tokens,
                )
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
