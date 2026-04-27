"""Official DiffSpot metrics.

Two scoring tracks:

1. has-diff items (splits: easy / medium / hard)
   - Recall:    fraction of GT mutations identified by the model
   - Precision: fraction of model-reported diffs that match a GT mutation
   - Diff F1:   harmonic mean of Recall and Precision

2. no-diff items
   - Hallucination rate: fraction of items where the model reported any change

Mutation matching is done by the LLM judge (see `diffspot.judge`); this module
turns judge labels into aggregate numbers.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class DiffScore:
    recall: float
    precision: float
    f1: float
    n_items: int


@dataclass
class HallucinationScore:
    rate: float
    n_items: int


@dataclass
class DiffSpotReport:
    overall: DiffScore
    by_split: dict[str, DiffScore] = field(default_factory=dict)
    by_mutation_type: dict[str, DiffScore] = field(default_factory=dict)
    no_diff: HallucinationScore | None = None


def aggregate(judged_items: list[dict]) -> DiffSpotReport:
    """Aggregate per-item judge labels into the official DiffSpot report.

    Each `judged_items[i]` is expected to contain:
        - id, split, mutation_types
        - matched_gt_count, total_gt_count          (for has-diff items)
        - reported_diff_count, correct_diff_count    (for has-diff items)
        - reported_any_change                        (for no-diff items)
    """
    raise NotImplementedError("aggregate() not yet implemented.")
