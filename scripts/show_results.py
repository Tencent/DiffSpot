"""Pretty-print a DiffSpot scores JSON in the official paper-table format.

Usage:
    python scripts/show_results.py results/<model>/scores.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("scores_json", type=Path)
    args = parser.parse_args()

    data = json.loads(args.scores_json.read_text())
    print(json.dumps(data, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
