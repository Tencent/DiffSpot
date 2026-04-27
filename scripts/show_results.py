"""Pretty-print a DiffSpot scores JSON in the official paper-table format.

Usage:
    python scripts/show_results.py results/<model>/scores.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

TIERS = [("easy", "Easy"), ("medium", "Med"), ("hard", "Hard")]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("scores_json", type=Path)
    args = parser.parse_args()

    data = json.loads(args.scores_json.read_text())
    report = data["report"]

    print(
        f"DiffSpot Scores  (judge: {data['judge_model']}, "
        f"prompt: {data['judge_version']})"
    )
    print("=" * 60)
    print(f"  Predictions judged:  {data['n_judged']:5d} / {data['n_predictions']:5d}")
    print(f"  Has-diff pairs:      {report['n_has_diff']:5d}    TP: {report['n_tp']}")
    print(f"  No-diff pairs:       {report['n_no_diff']:5d}    TN: {report['n_tn']}")
    print()
    print("  Recall by difficulty:")
    for key, name in TIERS:
        tier = report["by_tier"].get(key)
        if tier:
            print(f"    {name:5s}  {tier['recall']:6.1%}    ({tier['n_tp']}/{tier['n_pairs']})")
    print(
        f"    {'Diff':5s}  {report['diff_overall_recall']:6.1%}    "
        f"({report['n_tp']}/{report['n_has_diff']})"
    )
    print()
    print(
        f"  No-Diff Specificity: {report['no_diff_specificity']:6.1%}    "
        f"({report['n_tn']}/{report['n_no_diff']})"
    )
    print()
    print(
        f"  Overall Accuracy:    {report['overall_accuracy']:6.1%}    "
        f"({report['n_tp'] + report['n_tn']}/{report['n_total']})"
    )

    if report.get("by_operator"):
        print()
        print("  Recall by operator:")
        ops = sorted(
            report["by_operator"].items(),
            key=lambda kv: kv[1]["recall"],
            reverse=True,
        )
        for op, score in ops:
            print(
                f"    {op:18s}  {score['recall']:6.1%}    "
                f"({score['n_tp']}/{score['n_pairs']})"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
