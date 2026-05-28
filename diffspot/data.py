"""Dataset loader for DiffSpot.

Wraps ``datasets.load_dataset(...)`` against the official HuggingFace release
and yields evaluation records in a stable shape so baseline runners and the
judge do not need to know the on-disk format.

The loader exposes a stable ``DiffSpotItem`` shape that is decoupled from the
on-disk parquet column names — the parquet stores ``image_before`` /
``image_after`` / ``difficulty`` / ``ground_truth_diff`` etc., and the loader
maps those into the canonical ``image_a`` / ``image_b`` / ``split`` /
``gt_description`` fields below.

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

import json
from dataclasses import dataclass
from typing import Iterator

# Published HuggingFace dataset id.
HF_DATASET_ID = "tencent/DiffSpot"

# Parquet ships 28 records with difficulty="unknown" (all task_type="no_diff"
# — an artefact of build_release.py mapping source None -> "unknown"). Treat
# them as no_diff for split routing.
_DIFFICULTY_ALIASES = {"unknown": "no_diff"}

_VALID_SPLITS = {"easy", "medium", "hard", "no_diff"}


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


def _row_to_item(row: dict) -> DiffSpotItem:
    """Map one parquet row into the canonical DiffSpotItem shape."""
    difficulty = row.get("difficulty")
    task_type = row.get("task_type")
    split = _DIFFICULTY_ALIASES.get(difficulty, difficulty)
    if task_type == "no_diff":
        split = "no_diff"
    if split not in _VALID_SPLITS:
        raise ValueError(
            f"Unexpected split for id={row.get('id')}: difficulty={difficulty!r} "
            f"task_type={task_type!r}"
        )

    raw_mutations = row.get("mutation_dicts_json") or []
    gt_mutations: list[dict] | None
    if raw_mutations:
        gt_mutations = [json.loads(s) for s in raw_mutations]
    else:
        gt_mutations = None

    # ``mutation_dicts[*].type`` carries bare operator names (``text``,
    # ``line_height``, ...) matching the README / leaderboard taxonomy.
    # ``mutation_types`` carries the ``mutate_*``-prefixed Python function
    # names which are an internal detail.
    operator: str | None = None
    if gt_mutations:
        operator = gt_mutations[0].get("type")

    return DiffSpotItem(
        id=row["id"],
        split=split,
        domain=row.get("domain") or "",
        operator=operator,
        image_a=row["image_before"],
        image_b=row["image_after"],
        gt_mutations=gt_mutations,
        gt_description=row.get("ground_truth_diff") or None,
    )


def load(
    split: str = "all",
    revision: str | None = None,
    cache_dir: str | None = None,
    dataset_path: str | None = None,
) -> Iterator[DiffSpotItem]:
    """Stream DiffSpot items from HuggingFace.

    Args:
        split: one of ``"easy"``, ``"medium"``, ``"hard"``, ``"no_diff"``, ``"all"``.
        revision: optional dataset revision pin (commit SHA / tag) for reproducibility.
        cache_dir: optional local cache override.
        dataset_path: optional local parquet path (single file or glob). When set,
            bypasses ``HF_DATASET_ID`` and loads from disk — useful for testing
            before the dataset is published.

    Yields:
        ``DiffSpotItem``
    """
    try:
        from datasets import load_dataset
    except ImportError as e:
        raise RuntimeError(
            "datasets is required to load DiffSpot. Install with: "
            "pip install datasets>=3.0.0"
        ) from e

    if dataset_path is not None:
        ds_dict = load_dataset("parquet", data_files={"test": dataset_path})
        ds_dict = {"test": ds_dict["test"]}
    else:
        if HF_DATASET_ID.startswith("TBD"):
            raise RuntimeError(
                "DiffSpot dataset has not been published yet. Either set "
                "diffspot.data.HF_DATASET_ID to the published id, or pass "
                "dataset_path=<local parquet> to load(...)."
            )
        kwargs: dict = {}
        if revision is not None:
            kwargs["revision"] = revision
        if cache_dir is not None:
            kwargs["cache_dir"] = cache_dir
        ds_dict = load_dataset(HF_DATASET_ID, **kwargs)

    # The parquet release ships every record under a single dataset (no
    # native HF splits) and uses the row-level ``difficulty`` column for
    # split routing. We iterate every row and filter in-Python.
    rows = (row for s in ds_dict for row in ds_dict[s])

    for row in rows:
        item = _row_to_item(row)
        if split != "all" and item.split != split:
            continue
        yield item
