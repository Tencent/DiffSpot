#!/usr/bin/env python3
"""Render the DiffSpot leaderboard as a paper-style table image."""
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

OPEN = [
    ("Kimi K2.5", "1T / 32B", "54.2", "36.4", "18.6", "36.4", "87.2", "42.2"),
    ("Qwen3.5-VL-397B", "397B / 17B", "45.1", "31.5", "13.7", "30.1", "96.6", "37.6"),
    ("Qwen3-VL-235B-Thinking", "235B / 22B", "30.1", "17.3", "10.5", "19.3", "98.8", "28.3"),
    ("GLM-4.6V-Flash", "9B", "24.5", "17.6", "9.3", "17.1", "75.8", "23.8"),
    ("GLM-4.6V", "106B / 12B", "17.0", "10.9", "5.5", "11.2", "99.6", "21.2"),
    ("Qwen3-VL-30B-Instruct", "30B / 3B", "14.5", "9.0", "4.5", "9.3", "82.0", "17.6"),
    ("Qwen3-VL-30B-Thinking", "30B / 3B", "16.5", "8.8", "3.8", "9.7", "77.8", "17.5"),
    ("Qwen3-VL-235B-Instruct", "235B / 22B", "9.6", "3.0", "2.6", "5.1", "100.0", "15.9"),
    ("InternVL3.5-30B-A3B", "30B / 3B", "4.7", "3.9", "3.8", "4.2", "100.0", "15.0"),
]
PROP = [
    ("Gemini 3.1 Pro", "—", "60.5", "38.9", "22.7", "40.7", "98.4", "47.2"),
    ("Gemini 3 Flash", "—", "52.5", "32.5", "18.2", "34.4", "91.4", "40.9"),
    ("Claude Opus 4.7", "—", "41.2", "30.5", "21.8", "31.2", "99.6", "38.9"),
    ("GPT-5.4", "—", "48.8", "30.5", "12.2", "30.5", "99.6", "38.3"),
]

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
