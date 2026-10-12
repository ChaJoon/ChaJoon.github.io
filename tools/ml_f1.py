"""Fake news detection: micro-averaged F1 on the training and test sets for both models.

Values are copied from the coursework notebook output (MNBResult.png, SVCresult.png),
not re-run. A dumbbell per model shows the train-test gap, which is the point of the figure.
Usage: python ml_f1.py <font_dir> <out_stem>
"""
import re
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.lines import Line2D

FONT_DIR, OUT = Path(sys.argv[1]), Path(sys.argv[2])
for f in FONT_DIR.glob("*.ttf"):
    font_manager.fontManager.addfont(str(f))
SANS, MONO = "IBM Plex Sans", "IBM Plex Mono"
plt.rcParams.update({"svg.fonttype": "path", "font.family": SANS})

BG, INK, MUTED, GRID, DATA = "#FFFFFF", "#13213A", "#4E5F78", "#D9E1EA", "#1B4F8A"

# (model, train F1, test F1)
ROWS = [("Support Vector\nClassifier", 0.9843, 0.8313), ("Multinomial\nNaive Bayes", 0.9171, 0.8646)]
XMIN, XMAX = 0.78, 1.0

fig, ax = plt.subplots(figsize=(8, 3.6), dpi=100, facecolor=BG)
fig.subplots_adjust(left=0.20, right=0.96, top=0.74, bottom=0.17)
ax.set_facecolor(BG)

for i, (name, tr, te) in enumerate(ROWS):
    y = len(ROWS) - 1 - i
    ax.plot([te, tr], [y, y], color=MUTED, lw=2, zorder=2, solid_capstyle="round")
    ax.scatter([tr], [y], s=110, facecolor=BG, edgecolor=INK, linewidth=2, zorder=3)
    ax.scatter([te], [y], s=110, color=DATA, edgecolor=BG, linewidth=2, zorder=4)
    ax.text(tr, y + 0.2, f"{tr:.2f}", ha="center", va="bottom", fontsize=11, family=MONO, color=INK)
    ax.text(te, y + 0.2, f"{te:.2f}", ha="center", va="bottom", fontsize=11, family=MONO, color=INK,
            weight="medium")
    ax.text((tr + te) / 2, y - 0.2, f"gap {tr - te:.2f}", ha="center", va="top", fontsize=10,
            family=MONO, color=MUTED)

ax.set_ylim(-0.6, len(ROWS) - 0.4)
ax.set_xlim(XMIN, XMAX)
ax.set_yticks(range(len(ROWS)), [r[0] for r in reversed(ROWS)], fontsize=11, color=INK)
ticks = [0.80, 0.85, 0.90, 0.95, 1.00]
ax.set_xticks(ticks, [f"{t:.2f}" for t in ticks], fontsize=10, color=MUTED, family=MONO)
ax.set_xlabel("F1 score (micro-averaged)", fontsize=11, color=INK, labelpad=8)
ax.tick_params(axis="both", length=0, pad=8)
ax.xaxis.grid(True, color=GRID, lw=1, zorder=0)
ax.set_axisbelow(True)
for side in ("top", "right", "left"):
    ax.spines[side].set_visible(False)
ax.spines["bottom"].set_color(MUTED)

legend = [Line2D([], [], ls="", marker="o", ms=9, mfc=DATA, mec=DATA, label="Test set"),
          Line2D([], [], ls="", marker="o", ms=9, mfc=BG, mec=INK, mew=2, label="Training set")]
fig.legend(handles=legend, loc="upper right", bbox_to_anchor=(0.96, 0.86), ncol=2, frameon=False,
           fontsize=10, labelcolor=INK, handletextpad=0.3, columnspacing=1.4)

fig.text(0.02, 0.93, "The simpler model generalised better", fontsize=14, weight="semibold",
         color=INK, ha="left")
fig.text(0.02, 0.86, "Training versus held-out test F1, TF-IDF unigram features", fontsize=10,
         color=MUTED, ha="left")

fig.savefig(OUT.with_suffix(".svg"), facecolor=BG)
svg = OUT.with_suffix(".svg"); svg.write_text(re.sub(r"<!DOCTYPE[^>]*>\s*", "", svg.read_text(), count=1))
fig.savefig(OUT.with_suffix(".png"), facecolor=BG, dpi=200)
print("wrote", OUT.with_suffix(".svg"))
