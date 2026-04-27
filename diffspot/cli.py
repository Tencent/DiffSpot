"""Console entry points for the ``diffspot`` package.

``diffspot-eval`` is registered in pyproject.toml -> [project.scripts].
"""

from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from .data import DiffSpotItem, load
from .judge import (
    DEFAULT_JUDGE_MODEL,
    DEFAULT_REASONING_EFFORT,
    JUDGE_VERSION,
    judge_item,
    reduce_judge_label,
)
from .metrics import aggregate

NO_DIFF_GT_NOTE = (
    "No changes were applied; the two screenshots are independent renderings "
    "of the same HTML."
)


def _build_gt_index(revision: str | None) -> dict[str, DiffSpotItem]:
    return {item.id: item for item in load(split="all", revision=revision)}


def _read_predictions(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def _judge_one(pred: dict, gt: DiffSpotItem, judge_kwargs: dict) -> dict:
    is_no_diff = pred["split"] == "no_diff"
    if is_no_diff:
        gt_mutations: list[dict] = []
        gt_description = NO_DIFF_GT_NOTE
    else:
        gt_mutations = gt.gt_mutations or []
        gt_description = gt.gt_description or ""

    raw = judge_item(
        gt_description=gt_description,
        gt_mutations=gt_mutations,
        prediction=pred["prediction"],
        **judge_kwargs,
    )
    binary = reduce_judge_label(raw, is_no_diff=is_no_diff)
    return {
        "id": pred["id"],
        "split": pred["split"],
        "operator": gt.operator,
        "judge_label": raw,
        **binary,
    }


def evaluate(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="diffspot-eval")
    parser.add_argument("--predictions", required=True, help="Path to predictions JSONL")
    parser.add_argument("--output", required=True, help="Path to write scores JSON")
    parser.add_argument("--judge-model", default=DEFAULT_JUDGE_MODEL)
    parser.add_argument("--reasoning-effort", default=DEFAULT_REASONING_EFFORT)
    parser.add_argument("--dataset-revision", default=None)
    parser.add_argument(
        "--workers",
        type=int,
        default=50,
        help="Concurrent judge calls; default 50.",
    )
    args = parser.parse_args(argv)

    preds_path = Path(args.predictions)
    out_path = Path(args.output)
    if not preds_path.exists():
        print(f"Predictions file not found: {preds_path}", file=sys.stderr)
        return 1

    print(
        f"Loading GT dataset (revision={args.dataset_revision or 'latest'})...",
        file=sys.stderr,
    )
    gt_index = _build_gt_index(args.dataset_revision)
    preds = _read_predictions(preds_path)

    missing = [p["id"] for p in preds if p["id"] not in gt_index]
    if missing:
        print(
            f"WARNING: {len(missing)} prediction ids not in GT (first 5: {missing[:5]})",
            file=sys.stderr,
        )
        preds = [p for p in preds if p["id"] in gt_index]

    judge_kwargs = {
        "model": args.judge_model,
        "reasoning_effort": args.reasoning_effort,
    }
    print(f"Judging {len(preds)} predictions with {args.workers} workers...", file=sys.stderr)

    judged: list[dict] = []
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futures = {
            ex.submit(_judge_one, p, gt_index[p["id"]], judge_kwargs): p["id"]
            for p in preds
        }
        for i, fut in enumerate(as_completed(futures), 1):
            try:
                judged.append(fut.result())
            except Exception as e:
                pid = futures[fut]
                print(f"  [error] judge failed for id={pid}: {e}", file=sys.stderr)
            if i % 100 == 0:
                print(f"  judged {i}/{len(preds)}", file=sys.stderr)

    report = aggregate(judged)
    out = {
        "judge_version": JUDGE_VERSION,
        "judge_model": args.judge_model,
        "reasoning_effort": args.reasoning_effort,
        "n_predictions": len(preds),
        "n_judged": len(judged),
        "report": report.to_dict(),
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2, default=str))
    print(f"\nWrote {out_path}", file=sys.stderr)
    print(f"Overall Accuracy: {report.overall_accuracy:.1%}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(evaluate())
