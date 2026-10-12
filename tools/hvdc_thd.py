"""AC-side THD of the LCC as AC filters are added (HVDC individual coursework, Table 7).

Values are copied from the report table, not re-simulated.
Usage: python hvdc_thd.py <font_dir> <out_stem>
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch

FONT_DIR, OUT = Path(sys.argv[1]), Path(sys.argv[2])
for f in FONT_DIR.glob("*.ttf"):
    font_manager.fontManager.addfont(str(f))
SANS, MONO = "IBM Plex Sans", "IBM Plex Mono"
plt.rcParams.update({"svg.fonttype": "path", "font.family": SANS})

BG, INK, MUTED, GRID, DATA = "#FFFFFF", "#13213A", "#4E5F78", "#D9E1EA", "#1B4F8A"

# Table 7: Effect of AC filters on THD
ROWS = [("No filter", 27.27), ("Tuned 5th", 16.21), ("+ tuned 7th", 7.04), ("+ damped 12th", 7.13)]

fig, ax = plt.subplots(figsize=(8, 4.6), dpi=100, facecolor=BG)
fig.subplots_adjust(left=0.09, right=0.98, top=0.84, bottom=0.13)
ax.set_facecolor(BG)

YMAX = 30
BW = 0.56
# data units per inch on each axis, so the corner radius is round on screen
ax_w_in = fig.get_figwidth() * (0.98 - 0.09)
ax_h_in = fig.get_figheight() * (0.84 - 0.13)
X_PER_IN = (len(ROWS) - 0.2) / ax_w_in
Y_PER_IN = YMAX / ax_h_in
ASPECT = Y_PER_IN / X_PER_IN
RX = 0.04 * X_PER_IN          # 4 px at 100 dpi
for i, (label, v) in enumerate(ROWS):
    # bar: 4px rounded top, square base on the axis
    ax.add_patch(FancyBboxPatch((i - BW / 2, 0), BW, v, boxstyle=f"round,pad=0,rounding_size={RX}",
                                mutation_aspect=ASPECT, fc=DATA, ec="none", zorder=2))
    ax.add_patch(plt.Rectangle((i - BW / 2 + 0.003, 0), BW - 0.006, v / 2, fc=DATA, ec="none", zorder=2, antialiased=False))
    ax.text(i, v + 0.7, f"{v:.2f}%", ha="center", va="bottom", fontsize=12, family=MONO,
            color=INK, weight="medium")

ax.set_xlim(-0.6, len(ROWS) - 0.4)
ax.set_ylim(0, YMAX)
ax.set_xticks(range(len(ROWS)), [r[0] for r in ROWS], fontsize=11, color=INK)
ax.set_yticks(range(0, YMAX + 1, 10), [f"{t}%" for t in range(0, YMAX + 1, 10)],
              fontsize=10, color=MUTED, family=MONO)
ax.tick_params(axis="both", length=0, pad=8)
ax.yaxis.grid(True, color=GRID, lw=1, zorder=0)
ax.set_axisbelow(True)
for side in ("top", "right", "left"):
    ax.spines[side].set_visible(False)
ax.spines["bottom"].set_color(MUTED)

fig.text(0.09, 0.94, "AC-side total harmonic distortion as filters are added", fontsize=14,
         weight="semibold", color=INK, ha="left")
fig.text(0.09, 0.885, "6-pulse line-commutated converter, MATLAB/Simulink. Filters are cumulative left to right.",
         fontsize=10, color=MUTED, ha="left")

fig.savefig(OUT.with_suffix(".svg"), facecolor=BG)
# drop the DTD line: some hosts refuse SVGs that carry one
svg = OUT.with_suffix(".svg"); svg.write_text(__import__("re").sub(r"<!DOCTYPE[^>]*>\s*", "", svg.read_text(), count=1))
fig.savefig(OUT.with_suffix(".png"), facecolor=BG, dpi=200)
print("wrote", OUT.with_suffix(".svg"))
