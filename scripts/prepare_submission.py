"""Validate a predictions JSONL and package it for leaderboard submission.

Checks:
  - schema (id, split, model, prompt_version, prediction)
  - coverage (all 4,400 dataset items present, no duplicates)
  - prompt_version consistent across rows
  - prediction non-empty for all has-diff items

Usage:
    python scripts/prepare_submission.py \
        --predictions results/<model>/predictions.jsonl \
        --output submissions/<model>.zip
"""

from __future__ import annotations

import argparse
import json
import sys
import zipfile
from pathlib import Path

EXPECTED_SCHEMA_FIELDS = {"id", "split", "model", "prompt_version", "prediction"}
EXPECTED_TOTAL = 4400


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--predictions", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--expected-total", type=int, default=EXPECTED_TOTAL)
    parser.add_argument(
        "--allow-partial",
        action="store_true",
        help="Skip the coverage check (for sub-sampled debug runs).",
    )
    args = parser.parse_args()

    preds_path = Path(args.predictions)
    if not preds_path.exists():
        print(f"Predictions file not found: {preds_path}", file=sys.stderr)
        return 1

    rows: list[dict] = []
    with preds_path.open() as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"Line {line_no}: invalid JSON: {e}", file=sys.stderr)
                return 1

    errors: list[str] = []
    seen_ids: set[str] = set()
    models: set[str] = set()
    versions: set[str] = set()
    for i, row in enumerate(rows):
        missing = EXPECTED_SCHEMA_FIELDS - row.keys()
        if missing:
            errors.append(f"Row {i}: missing fields {missing}")
            continue
        if row["id"] in seen_ids:
            errors.append(f"Row {i}: duplicate id {row['id']}")
        seen_ids.add(row["id"])
        models.add(row["model"])
        versions.add(row["prompt_version"])
        if row["split"] != "no_diff" and not str(row.get("prediction", "")).strip():
            errors.append(f"Row {i}: empty prediction on has-diff item {row['id']}")

    if not args.allow_partial and len(seen_ids) != args.expected_total:
        errors.append(
            f"Coverage: found {len(seen_ids)} unique ids, expected {args.expected_total}"
        )
    if len(models) > 1:
        errors.append(f"Multiple model values: {models}")
    if len(versions) > 1:
        errors.append(f"Multiple prompt_version values: {versions}")

    if errors:
        print("VALIDATION FAILED:", file=sys.stderr)
        for e in errors[:20]:
            print(f"  - {e}", file=sys.stderr)
        if len(errors) > 20:
            print(f"  ... and {len(errors) - 20} more", file=sys.stderr)
        return 1

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(preds_path, arcname=preds_path.name)

    print(
        f"OK. {len(rows)} predictions, model={list(models)[0]}, "
        f"prompt={list(versions)[0]} -> {out_path}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
