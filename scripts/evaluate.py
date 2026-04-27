"""End-to-end evaluation: predictions JSONL -> judge -> scores JSON.

Usage:
    python scripts/evaluate.py \
        --predictions results/<model>/predictions.jsonl \
        --judge-model gpt-oss-120b \
        --output results/<model>/scores.json
"""

from __future__ import annotations

import argparse


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--predictions", required=True)
    parser.add_argument("--judge-model", default="gpt-oss-120b")
    parser.add_argument("--reasoning-effort", default="high")
    parser.add_argument("--dataset-revision", default=None)
    parser.add_argument("--output", required=True)
    parser.add_argument("--workers", type=int, default=50,
                        help="Concurrent judge calls; default 50 is safe for welmgateway.")
    args = parser.parse_args()

    raise NotImplementedError(
        "TODO: stream predictions, call diffspot.judge.judge_item per row, "
        "diffspot.metrics.aggregate(...), write JSON to args.output."
    )


if __name__ == "__main__":
    main()
