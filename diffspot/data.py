"""Dataset loader for DiffSpot.

Wraps ``datasets.load_dataset(...)`` against the official HuggingFace release
and yields evaluation records in a stable shape so baseline runners and the
judge do not need to know the on-disk format.

Record shape (per item):
    {
        "id":             str,             # globally unique
        "split":          "easy" | "medium" | "hard" | "no_diff",
        "domain":         str,
        "operator":       str | None,      # mutation operator; None for no_diff
        "image_a":        PIL.Image,       # original screenshot
        "image_b":        PIL.Image,       # mutated (or re-rendered) screenshot
        "gt_mutations":   list[dict] | None,
        "gt_description": str | None,
    }
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator

# Replace with the published HuggingFace dataset id once the dataset is live.
HF_DATASET_ID = "TBD/DiffSpot"


@dataclass
class DiffSpotItem:
    id: str
    split: str
    domain: str
    operator: str | None
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
        split: one of ``"easy"``, ``"medium"``, ``"hard"``, ``"no_diff"``, ``"all"``.
        revision: optional dataset revision pin (commit SHA / tag) for reproducibility.
        cache_dir: optional local cache override.

    Yields:
        ``DiffSpotItem``
    """
    if HF_DATASET_ID.startswith("TBD"):
        raise RuntimeError(
            "DiffSpot dataset has not been published yet. Once it is live on "
            "HuggingFace, set diffspot.data.HF_DATASET_ID to the published id."
        )

    try:
        from datasets import load_dataset
    except ImportError as e:
        raise RuntimeError(
            "datasets is required to load DiffSpot. Install with: "
            "pip install datasets>=3.0.0"
        ) from e

    kwargs: dict = {}
    if revision is not None:
        kwargs["revision"] = revision
    if cache_dir is not None:
        kwargs["cache_dir"] = cache_dir

    ds = load_dataset(HF_DATASET_ID, **kwargs)

    if split == "all":
        rows = (row for s in ds for row in ds[s])
    else:
        rows = iter(ds[split])

    for row in rows:
        yield DiffSpotItem(
            id=row["id"],
            split=row["split"],
            domain=row.get("domain", ""),
            operator=row.get("operator"),
            image_a=row["image_a"],
            image_b=row["image_b"],
            gt_mutations=row.get("gt_mutations"),
            gt_description=row.get("gt_description"),
        )
