"""Run a Google-hosted VLM (e.g. gemini-3.1-pro, gemini-3-flash) on DiffSpot.

Usage:
    python baselines/api/run_gemini.py \
        --model gemini-3.1-pro \
        --output results/gemini-3.1-pro/predictions.jsonl
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
        "TODO: google.generativeai.GenerativeModel(model).generate_content([...]) "
        "with both images attached."
    )


if __name__ == "__main__":
    main()
