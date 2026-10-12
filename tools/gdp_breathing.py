"""Capaciflector raw output at 100 cm read range (GDP, group report Fig. 5.6 data).

Plots the raw RFID sensor values exactly as logged, plus a centred moving average
drawn on top so the breathing cycles are easy to see. The average is a display aid
only; it is labelled as such on the chart.
Usage: python gdp_breathing.py <font_dir> <sensor_csv> <out_stem>
"""
import csv
import re
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

FONT_DIR, CSV, OUT = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
for f in FONT_DIR.glob("*.ttf"):
    font_manager.fontManager.addfont(str(f))
SANS, MONO = "IBM Plex Sans", "IBM Plex Mono"
plt.rcParams.update({"svg.fonttype": "path", "font.family": SANS})

BG, INK, MUTED, GRID = "#FFFFFF", "#1B1D1F", "#63666A", "#E4E2DC"
RAW, AVG = "#9CC5AE", "#286E49"   # light and dark steps of the site's green
WINDOW = 50

rows = list(csv.reader(CSV.open(encoding="utf-8-sig")))[1:]          # skip "x0000,y0000"
n = np.array([int(r[0]) for r in rows if r and r[0].strip()])
y = np.array([float(r[1]) for r in rows if r and r[0].strip()])
avg = np.convolve(y, np.ones(WINDOW) / WINDOW, mode="valid")
avg_n = n[WINDOW // 2: WINDOW // 2 + len(avg)]

fig, ax = plt.subplots(figsize=(9, 4.2), dpi=100, facecolor=BG)
fig.subplots_adjust(left=0.08, right=0.98, top=0.76, bottom=0.15)
ax.set_facecolor(BG)
ax.plot(n, y, color=RAW, lw=1.0, zorder=2)
ax.plot(avg_n, avg, color=AVG, lw=2.0, zorder=3)

ax.set_xlim(0, n.max())
ax.set_ylim(290, 395)
ax.set_xticks(range(0, int(n.max()) + 1, 500))
ax.tick_params(axis="both", length=0, pad=6, labelsize=10, labelcolor=MUTED)
for lab in ax.get_xticklabels() + ax.get_yticklabels():
    lab.set_family(MONO)
ax.set_xlabel("sample number", fontsize=10, color=MUTED, labelpad=6)
ax.set_ylabel("sensor raw value", fontsize=10, color=MUTED, labelpad=6)
ax.yaxis.grid(True, color=GRID, lw=1, zorder=0)
ax.set_axisbelow(True)
for side in ("top", "right", "left"):
    ax.spines[side].set_visible(False)
ax.spines["bottom"].set_color(MUTED)

fig.text(0.08, 0.935, "Capaciflector output at 100 cm read range", fontsize=14, weight="semibold",
         color=INK, ha="left")
fig.text(0.08, 0.875, "Controlled breathing at 6 breaths per minute, logged wirelessly through the RFID reader.",
         fontsize=10, color=MUTED, ha="left")
# legend: two series, so one is always shown
lx, ly = 0.08, 0.81
for label, c, lw in [("raw samples", RAW, 1.4), (f"{WINDOW}-sample moving average (display aid)", AVG, 2.0)]:
    fig.add_artist(plt.Line2D([lx, lx + 0.03], [ly, ly], color=c, lw=lw, transform=fig.transFigure))
    t = fig.text(lx + 0.04, ly, label, fontsize=10, color=MUTED, va="center", ha="left")
    fig.canvas.draw()
    lx = fig.transFigure.inverted().transform(t.get_window_extent().corners()[-1])[0] + 0.04

fig.savefig(OUT.with_suffix(".svg"), facecolor=BG)
fig.savefig(OUT.with_suffix(".png"), facecolor=BG, dpi=200)
# drop the DTD line: some hosts refuse SVGs that carry one
svg = OUT.with_suffix(".svg")
svg.write_text(re.sub(r"<!DOCTYPE[^>]*>\s*", "", svg.read_text(), count=1))
print("wrote", svg, "samples:", len(y))
