"""Run a self-hosted InternVL3 endpoint on DiffSpot.

Usage:
    python baselines/local/run_internvl.py \
        --endpoint http://<host>:30000/v1 \
        --model InternVL3-38B \
        --output results/internvl3-38b/predictions.jsonl
"""

from __future__ import annotations

import argparse


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--endpoint", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--dataset-revision", default=None)
    parser.add_argument("--max-tokens", type=int, default=16384)
    args = parser.parse_args()

    raise NotImplementedError("TODO: same shape as run_qwen3vl.py.")


if __name__ == "__main__":
    main()
