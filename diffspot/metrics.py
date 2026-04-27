"""Official DiffSpot metrics.

Each (image_a, image_b) pair is reduced to a binary outcome:
  - has-diff pair: TP if the model identified the GT mutation, FN otherwise
  - no-diff  pair: TN if the model reported no change,        FP otherwise

The judge labels (see `diffspot.judge`) drive these binary outcomes.

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

from dataclasses import dataclass, field


@dataclass
class TierScore:
    recall: float
    n_pairs: int


@dataclass
class DiffSpotReport:
    overall_accuracy: float                          # (TP + TN) / 4,400
    diff_overall_recall: float                        # TP / 3,900
    no_diff_specificity: float                        # TN / 500
    by_tier: dict[str, TierScore] = field(default_factory=dict)         # easy/med/hard
    by_operator: dict[str, TierScore] = field(default_factory=dict)     # 13 operators


def aggregate(judged_items: list[dict]) -> DiffSpotReport:
    """Aggregate per-item judge labels into the official DiffSpot report.

    Each `judged_items[i]` is expected to contain:
        - id, split ("easy"|"medium"|"hard"|"no_diff"), operator
        - is_true_positive: bool   (has-diff item where the GT mutation was identified)
        - is_true_negative: bool   (no-diff item where the model reported no change)
    """
    raise NotImplementedError("aggregate() not yet implemented.")
