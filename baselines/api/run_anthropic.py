"""Run an Anthropic-hosted VLM (e.g. claude-opus-4-6) on the DiffSpot test set.

Usage:
    python baselines/api/run_anthropic.py \
        --model claude-opus-4-6 \
        --output results/claude-opus-4-6/predictions.jsonl
"""

from __future__ import annotations

import argparse


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--dataset-revision", default=None)
    parser.add_argument("--max-tokens", type=int, default=16384)
    args = parser.parse_args()

    raise NotImplementedError(
        "TODO: anthropic.Anthropic().messages.create(...) with images_a/b inline."
    )


if __name__ == "__main__":
    main()
