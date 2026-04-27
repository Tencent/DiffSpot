"""Console entry points (registered in pyproject.toml).

Currently exposes:
    diffspot-eval    -- end-to-end: predictions JSONL + judge -> scores JSON
"""

from __future__ import annotations

import argparse


def evaluate() -> int:
    parser = argparse.ArgumentParser(prog="diffspot-eval")
    parser.add_argument("--predictions", required=True, help="Path to predictions JSONL")
    parser.add_argument("--output", required=True, help="Path to write scores JSON")
    parser.add_argument("--judge-model", default="gpt-oss-120b")
    parser.add_argument("--dataset-revision", default=None)
    args = parser.parse_args()

    raise NotImplementedError(
        f"Wire up: load predictions={args.predictions}, run judge={args.judge_model}, "
        f"aggregate, write to {args.output}."
    )


if __name__ == "__main__":
    evaluate()
