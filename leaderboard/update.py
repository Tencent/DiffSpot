"""Regenerate the leaderboard table in README.md from leaderboard.json.

Usage:
    python leaderboard/update.py

Splices a freshly rendered markdown table between the
``<!-- LEADERBOARD START -->`` and ``<!-- LEADERBOARD END -->`` markers in
``README.md``. Sort key: overall_accuracy descending within each family.
``**bold**`` marks the column max for each numeric column.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEADERBOARD_JSON = ROOT / "leaderboard" / "leaderboard.json"
README = ROOT / "README.md"

START = "<!-- LEADERBOARD START -->"
END = "<!-- LEADERBOARD END -->"

NUM_COLS = (
    "easy_recall",
    "med_recall",
    "hard_recall",
    "diff_overall_recall",
    "no_diff_specificity",
    "overall_accuracy",
)


def render_table(entries: list[dict]) -> str:
    if not entries:
        return "_(no entries)_"

    col_max = {c: max(e[c] for e in entries) for c in NUM_COLS}

    def fmt(e: dict, c: str) -> str:
        val = f"{e[c]:.1f}"
        return f"**{val}**" if e[c] == col_max[c] else val

    def render_row(e: dict) -> str:
        name = e["display_name"]
        if e["overall_accuracy"] == col_max["overall_accuracy"]:
            name = f"**{name}**"
        return (
            f"| {name} | {e.get('params', '—')} | "
            f"{fmt(e, 'easy_recall')} | {fmt(e, 'med_recall')} | "
            f"{fmt(e, 'hard_recall')} | {fmt(e, 'diff_overall_recall')} | "
            f"{fmt(e, 'no_diff_specificity')} | {fmt(e, 'overall_accuracy')} |"
        )

    open_weight = sorted(
        (e for e in entries if e.get("family") == "open-weight"),
        key=lambda e: e["overall_accuracy"],
        reverse=True,
    )
    proprietary = sorted(
        (e for e in entries if e.get("family") == "proprietary"),
        key=lambda e: e["overall_accuracy"],
        reverse=True,
    )

    lines = [
        "| Model | Params | Easy | Med | Hard | Diff Overall | No-Diff | **Overall** |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    if open_weight:
        lines.append("| _Open-weight models_ | | | | | | | |")
        lines.extend(render_row(e) for e in open_weight)
    if proprietary:
        lines.append("| _Proprietary models_ | | | | | | | |")
        lines.extend(render_row(e) for e in proprietary)
    return "\n".join(lines)


def main() -> int:
    data = json.loads(LEADERBOARD_JSON.read_text())
    table_md = render_table(data["entries"])

    readme = README.read_text()
    if START not in readme or END not in readme:
        print(f"ERROR: README.md is missing {START!r} / {END!r} markers")
        return 1

    pre, _, rest = readme.partition(START)
    _, _, post = rest.partition(END)

    trivial = (
        data.get("trivial_baselines", {}).get("always_no_diff", {}).get("overall_accuracy")
    )
    trivial_line = (
        f"\n\nTrivial always-no-diff baseline: {trivial:.1f}% Overall." if trivial else ""
    )

    new = pre + START + "\n\n" + table_md + trivial_line + "\n\n" + END + post
    README.write_text(new)
    print(f"Updated leaderboard table in {README}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
