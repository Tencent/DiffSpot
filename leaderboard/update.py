"""Regenerate the leaderboard table in README.md from leaderboard.json.

Usage:
    python leaderboard/update.py

Reads `leaderboard/leaderboard.json` and rewrites the section between the
markers `<!-- LEADERBOARD START -->` and `<!-- LEADERBOARD END -->` in
`README.md`.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEADERBOARD_JSON = ROOT / "leaderboard" / "leaderboard.json"
README = ROOT / "README.md"

START = "<!-- LEADERBOARD START -->"
END = "<!-- LEADERBOARD END -->"


def main() -> int:
    raise NotImplementedError(
        "TODO: read leaderboard.json, render markdown table, splice between markers."
    )


if __name__ == "__main__":
    main()
