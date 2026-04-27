"""Run an OpenAI-hosted VLM (e.g. gpt-5.4) on the DiffSpot test set.

Usage:
    python baselines/api/run_openai.py \
        --model gpt-5.4 \
        --output results/gpt-5.4/predictions.jsonl
"""

from __future__ import annotations

import argparse


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, help="OpenAI model id (e.g. gpt-5.4)")
    parser.add_argument("--output", required=True, help="Output JSONL path")
    parser.add_argument("--dataset-revision", default=None, help="HF dataset revision pin")
    parser.add_argument("--max-tokens", type=int, default=16384,
                        help="Min 16384 for thinking models; 4K causes silent truncation.")
    parser.add_argument("--temperature", type=float, default=0.0)
    args = parser.parse_args()

    raise NotImplementedError(
        "TODO: load DiffSpot via diffspot.data.load(...), call OpenAI Vision API "
        "with prompts from diffspot/prompts/, append-write to args.output."
    )


if __name__ == "__main__":
    main()
