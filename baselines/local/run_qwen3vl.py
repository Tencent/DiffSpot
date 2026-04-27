"""Run a self-hosted Qwen3-VL endpoint (e.g. via sglang) on DiffSpot.

Usage:
    python baselines/local/run_qwen3vl.py \
        --endpoint http://<host>:30000/v1 \
        --model Qwen3-VL-235B-A22B-Instruct \
        --output results/qwen3-vl-235b/predictions.jsonl
"""

from __future__ import annotations

import argparse


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--endpoint", required=True, help="OpenAI-compatible base URL")
    parser.add_argument("--model", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--dataset-revision", default=None)
    parser.add_argument("--max-tokens", type=int, default=16384,
                        help="Set 32768+ for thinking variants.")
    parser.add_argument("--reasoning-parser", default=None,
                        help="e.g. 'qwen3' to strip </think> from content.")
    args = parser.parse_args()

    raise NotImplementedError(
        "TODO: openai.OpenAI(base_url=args.endpoint).chat.completions.create(...) loop."
    )


if __name__ == "__main__":
    main()
