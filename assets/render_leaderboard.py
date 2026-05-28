#!/usr/bin/env python3
"""Render the DiffSpot leaderboard as a paper-style table image.

Single source of truth: ../leaderboard/leaderboard.json. To update the figure
after a new submission, edit leaderboard.json and re-run this script.
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

WEBLUE = "#E8F2FA"
ROWGRAY = "#EEEEEE"
INK = "#141414"
ACCENT = "#FF4438"

# columns: label, x-center (0..1), align
COLS = [
    ("Model",   0.030, "left"),
    ("Params",  0.355, "center"),
    ("Easy",    0.495, "center"),
    ("Med",     0.575, "center"),
    ("Hard",    0.655, "center"),
    ("Diff",    0.745, "center"),
    ("No-Diff", 0.855, "center"),
    ("Overall", 0.955, "center"),
]

# ---- Data: read from leaderboard.json (single source of truth) ----
LEADERBOARD_JSON = Path(__file__).resolve().parents[1] / "leaderboard" / "leaderboard.json"


def _row(e: dict) -> tuple:
    f = lambda k: f"{float(e[k]):.1f}"
    return (
        e["display_name"], e.get("params") or "—",
        f("easy_recall"), f("med_recall"), f("hard_recall"),
        f("diff_overall_recall"), f("no_diff_specificity"), f("overall_accuracy"),
    )


_entries = json.loads(LEADERBOARD_JSON.read_text())["entries"]
OPEN = [_row(e) for e in sorted(
    (x for x in _entries if x.get("family") == "open-weight"),
    key=lambda x: x["overall_accuracy"], reverse=True)]
PROP = [_row(e) for e in sorted(
    (x for x in _entries if x.get("family") == "proprietary"),
    key=lambda x: x["overall_accuracy"], reverse=True)]

# value-column indices into a row tuple (2..7) -> bold if == column max
NUMCOL = [2, 3, 4, 5, 6, 7]
allrows = OPEN + PROP
colmax = {c: max(float(r[c]) for r in allrows) for c in NUMCOL}
# best open-weight (for underline): Diff(5) and Overall(7)
open_best = {5: max(float(r[5]) for r in OPEN), 7: max(float(r[7]) for r in OPEN)}

fig_w, fig_h = 12.6, 6.0
fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=200)
ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")

n_body = len(allrows) + 2  # +2 group header rows
top = 0.93       # y of top rule
header_h = 0.085
bottom = 0.03
body_top = top - header_h
row_h = (body_top - bottom) / n_body
left, right = 0.012, 0.988

def y_of(i):  # body row index 0..n_body-1
    return body_top - (i + 0.5) * row_h

# --- Overall column highlight band (behind everything) ---
ax.add_patch(Rectangle((0.905, bottom), 0.083, (top + 0.02) - bottom,
                        facecolor=WEBLUE, edgecolor="none", zorder=0))

# --- Header ---
hy = top - header_h * 0.42
# "Diff" group label + underline spanning Easy..Diff... actually Easy/Med/Hard/Diff
ax.text((0.495 + 0.745) / 2, top - 0.016, "Diff", ha="center", va="center",
        fontsize=15, fontweight="bold", color=INK)
ax.plot([0.470, 0.792], [top - 0.038, top - 0.038], color=INK, lw=1.1)
for label, x, align in COLS:
    if label == "Diff":
        ax.text(x, hy - 0.028, label, ha="center", va="center",
                fontsize=14.5, fontweight="bold", color=INK)
    else:
        ax.text(x, hy - 0.028, label, ha=align, va="center",
                fontsize=14.5, fontweight="bold", color=INK)

# --- rules ---
def rule(y, lw=1.6):
    ax.plot([left, right], [y, y], color=INK, lw=lw, zorder=3)
rule(top + 0.02, lw=2.2)            # top rule
rule(top - header_h, lw=1.4)        # under header

# --- body rows ---
def draw_group(label, y):
    ax.add_patch(Rectangle((left, y - row_h / 2), right - left, row_h,
                           facecolor=ROWGRAY, edgecolor="none", zorder=1))
    ax.text(0.5, y, label, ha="center", va="center", fontsize=13.5,
            fontstyle="italic", fontweight="bold", color=INK, zorder=2)

def draw_row(r, y):
    # model name (left), params
    ax.text(COLS[0][1], y, r[0], ha="left", va="center", fontsize=13.5, color=INK, zorder=2)
    ax.text(COLS[1][1], y, r[1], ha="center", va="center", fontsize=12.5, color="#555", zorder=2)
    for ci in NUMCOL:
        val = r[ci]
        x = COLS[ci][1]
        is_max = float(val) == colmax[ci]
        fw = "bold" if is_max else "normal"
        col = INK
        ax.text(x, y, val, ha="center", va="center", fontsize=13.5,
                fontweight=fw, color=col, zorder=2)
        # underline best open-weight in Diff / Overall
        if ci in open_best and float(val) == open_best[ci] and not is_max:
            ax.plot([x - 0.020, x + 0.020], [y - row_h * 0.28, y - row_h * 0.28],
                    color=INK, lw=1.0, zorder=2)

i = 0
draw_group("Open-weight models", y_of(i)); i += 1
for r in OPEN:
    draw_row(r, y_of(i)); i += 1
draw_group("Proprietary models", y_of(i)); i += 1
for r in PROP:
    draw_row(r, y_of(i)); i += 1

rule(bottom, lw=2.2)  # bottom rule

plt.subplots_adjust(left=0.005, right=0.995, top=0.995, bottom=0.005)
out = "diffspot-leaderboard.png"
fig.savefig(out, dpi=200, bbox_inches="tight", pad_inches=0.06, facecolor="white")
print("wrote", out)
