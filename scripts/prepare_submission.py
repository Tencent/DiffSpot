"""Validate a predictions JSONL and package it for leaderboard submission.

Checks:
  - schema (id, split, model, prompt_version, prediction)
  - coverage (all 4,400 dataset items present, no duplicates)
  - prompt_version matches the official prompt files
  - prediction is non-empty for all has-diff items

Usage:
    python scripts/prepare_submission.py \
        --predictions results/<model>/predictions.jsonl \
        --output submissions/<model>.zip
"""

from __future__ import annotations

import argparse


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--predictions", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    raise NotImplementedError("TODO: validate + zip predictions.")


if __name__ == "__main__":
    main()
