"""End-to-end evaluation: predictions JSONL -> judge -> scores JSON.

Usage:
    python scripts/evaluate.py \
        --predictions results/<model>/predictions.jsonl \
        --judge-model gpt-oss-120b \
        --output results/<model>/scores.json

Thin wrapper around ``diffspot.cli.evaluate``.
"""

from __future__ import annotations

import sys

from diffspot.cli import evaluate

if __name__ == "__main__":
    raise SystemExit(evaluate(sys.argv[1:]))
