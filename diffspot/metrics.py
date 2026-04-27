"""Official DiffSpot metrics.

Each (image_a, image_b) pair is reduced to a binary outcome:
  - has-diff pair: TP if the model identified the GT mutation, FN otherwise
  - no-diff  pair: TN if the model reported no change,        FP otherwise

The judge labels (see ``diffspot.judge``) drive these binary outcomes.

Headline metric:
    Overall Accuracy = (TP + TN) / 4,400

Per-tier and per-split breakdowns:
    Easy / Med / Hard Recall  -- TPs over 1,300 has-diff pairs each
    Diff Overall Recall       -- TPs over 3,900 has-diff pairs
    No-Diff Specificity       -- TNs over 500 no-diff pairs

Optional analysis breakdown:
    Per-operator Recall on the 13 mutation operators (300 pairs each).
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class TierScore:
    recall: float
    n_pairs: int
    n_tp: int


@dataclass
class OperatorScore:
    recall: float
    n_pairs: int
    n_tp: int


@dataclass
class DiffSpotReport:
    overall_accuracy: float
    diff_overall_recall: float
    no_diff_specificity: float
    n_total: int
    n_has_diff: int
    n_no_diff: int
    n_tp: int
    n_tn: int
    by_tier: dict[str, TierScore] = field(default_factory=dict)
    by_operator: dict[str, OperatorScore] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def aggregate(judged_items: list[dict]) -> DiffSpotReport:
    """Aggregate per-item judge labels into a DiffSpot report.

    Each judged item is expected to have:
        - "split":            "easy" | "medium" | "hard" | "no_diff"
        - "operator":         str | None  (operator name; None for no_diff)
        - "is_true_positive": bool
        - "is_true_negative": bool

    Canonical denominators are 1,300 per has-diff tier and 500 no-diff. The
    function does NOT enforce those; it computes from input so partial /
    sub-sampled runs still produce valid sub-set reports (which the caller
    can flag as preliminary).
    """
    n_total = len(judged_items)
    n_tp = n_tn = n_has_diff = n_no_diff = 0
    tier_tp: dict[str, int] = defaultdict(int)
    tier_n: dict[str, int] = defaultdict(int)
    op_tp: dict[str, int] = defaultdict(int)
    op_n: dict[str, int] = defaultdict(int)

    for it in judged_items:
        split = it["split"]
        is_tp = bool(it.get("is_true_positive"))
        is_tn = bool(it.get("is_true_negative"))
        if split == "no_diff":
            n_no_diff += 1
            if is_tn:
                n_tn += 1
        else:
            n_has_diff += 1
            tier_n[split] += 1
            if is_tp:
                n_tp += 1
                tier_tp[split] += 1
            op = it.get("operator")
            if op:
                op_n[op] += 1
                if is_tp:
                    op_tp[op] += 1

    by_tier = {
        tier: TierScore(
            recall=(tier_tp[tier] / tier_n[tier]) if tier_n[tier] else 0.0,
            n_pairs=tier_n[tier],
            n_tp=tier_tp[tier],
        )
        for tier in tier_n
    }
    by_operator = {
        op: OperatorScore(
            recall=(op_tp[op] / op_n[op]) if op_n[op] else 0.0,
            n_pairs=op_n[op],
            n_tp=op_tp[op],
        )
        for op in op_n
    }
    return DiffSpotReport(
        overall_accuracy=((n_tp + n_tn) / n_total) if n_total else 0.0,
        diff_overall_recall=(n_tp / n_has_diff) if n_has_diff else 0.0,
        no_diff_specificity=(n_tn / n_no_diff) if n_no_diff else 0.0,
        n_total=n_total,
        n_has_diff=n_has_diff,
        n_no_diff=n_no_diff,
        n_tp=n_tp,
        n_tn=n_tn,
        by_tier=by_tier,
        by_operator=by_operator,
    )
