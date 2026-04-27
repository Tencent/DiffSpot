"""Dataset loader for DiffSpot.

Wraps `datasets.load_dataset(...)` against the official HuggingFace release and
yields evaluation records in a stable shape so baseline runners and the judge
do not need to know the on-disk format.

Record shape (per item):
    {
        "id":            str,             # globally unique
        "split":         "easy" | "medium" | "hard" | "no_diff",
        "domain":        str,
        "image_a":       PIL.Image,       # original screenshot
        "image_b":       PIL.Image,       # mutated (or re-rendered) screenshot
        "gt_mutations":  list[dict] | None,   # None for split == "no_diff"
        "gt_description": str | None,         # English natural-language GT
    }
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator

HF_DATASET_ID = "TBD/DiffSpot"  # populated when dataset is published


@dataclass
class DiffSpotItem:
    id: str
    split: str
    domain: str
    image_a: object  # PIL.Image
    image_b: object
    gt_mutations: list[dict] | None
    gt_description: str | None


def load(
    split: str = "all",
    revision: str | None = None,
    cache_dir: str | None = None,
) -> Iterator[DiffSpotItem]:
    """Stream DiffSpot items from HuggingFace.

    Args:
        split: one of {"easy", "medium", "hard", "no_diff", "all"}.
        revision: optional dataset revision pin (commit SHA / tag) for reproducibility.
        cache_dir: optional local cache override.

    Yields:
        DiffSpotItem
    """
    raise NotImplementedError(
        "Dataset loader not yet wired up. Will call datasets.load_dataset(HF_DATASET_ID, ...)."
    )
