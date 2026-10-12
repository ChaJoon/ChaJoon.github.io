"""NEM resonator: in-phase lock-in current vs frequency at five drive powers (Vbg = 1 V).

Traces are the raw LabVIEW .lvm files from the lab (column 4 = in-phase part X).
The resonance markers are the Lorentzian-fit f0 values from Table II of the CW2 report,
not refitted here. Traces are stacked with just enough offset that none overlap.
Usage: python nem_ac_sweep.py <data_dir> <font_dir> <out_stem>
"""
import re
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

DATA_DIR, FONT_DIR, OUT = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
for f in FONT_DIR.glob("*.ttf"):
    font_manager.fontManager.addfont(str(f))
SANS, MONO = "IBM Plex Sans", "IBM Plex Mono"
plt.rcParams.update({"svg.fonttype": "path", "font.family": SANS})

BG, INK, MUTED, GRID, DATA, MARK = "#FFFFFF", "#13213A", "#4E5F78", "#D9E1EA", "#1B4F8A", "#A3271F"

# (label, file, fitted f0 in MHz from report Table II)
RUNS = [("0 dB", "AC_0dB.lvm", 100.33), ("−2 dB", "AC_-2dB.lvm", 99.14), ("−4 dB", "AC_-4dB.lvm", 98.16),
        ("−6 dB", "AC_-6dB.lvm", 97.68), ("−8 dB", "AC_-8dB.lvm", 97.26)]
GAP = 0.08    # nA of clear space between neighbouring traces


def read_lvm(path):
    """Return frequency (MHz) and in-phase current X (nA) from a LabVIEW .lvm file."""
    lines = path.read_text().splitlines()
    ends = [i for i, ln in enumerate(lines) if ln.startswith("***End_of_Header***")]
    f, x = [], []
    for ln in lines[ends[1] + 2:]:
        parts = [p for p in ln.split("\t") if p.strip()]
        if len(parts) >= 5:
            f.append(float(parts[0]))
            x.append(float(parts[3]))
    return np.array(f) / 1e6, np.array(x) * 1e9


fig, ax = plt.subplots(figsize=(8, 5.6), dpi=100, facecolor=BG)
fig.subplots_adjust(left=0.04, right=0.89, top=0.85, bottom=0.12)
ax.set_facecolor(BG)

marker_xy = []
off, prev_min = 0.0, None
for label, fname, f0 in RUNS:
    f, x = read_lvm(DATA_DIR / fname)
    y = x - np.median(x)                # each trace on its own zero baseline
    if prev_min is not None:            # sit just below the trace above
        off = prev_min - y.max() - GAP
    y = y + off
    prev_min = y.min()
    ax.plot(f, y, color=DATA, lw=1.4, zorder=3, solid_joinstyle="round")
    ax.text(101.12, off, label, fontsize=11, family=MONO, color=INK, ha="left", va="center")
    marker_xy.append((f0, float(np.interp(f0, f, y))))
bottom = prev_min

# fitted resonance on each trace, joined to show the drift
mx, my = zip(*marker_xy)
ax.plot(mx, my, color=MARK, lw=1.2, ls=(0, (3, 3)), zorder=4)
ax.scatter(mx, my, s=64, color=MARK, edgecolor=BG, linewidth=2, zorder=5)
ax.annotate("fitted resonance f₀", xy=(mx[0], my[0]), xytext=(mx[0] - 0.12, my[0]),
            fontsize=10, color=MARK, ha="right", va="center", family=SANS)

ax.set_xlim(95.9, 101.1)
ax.set_ylim(bottom - 0.06, 0.2)
ax.set_xticks(range(96, 102), [str(t) for t in range(96, 102)], fontsize=10, color=MUTED, family=MONO)
ax.set_yticks([])
ax.set_xlabel("Frequency (MHz)", fontsize=11, color=INK, labelpad=8)
ax.tick_params(axis="x", length=0, pad=8)
ax.xaxis.grid(True, color=GRID, lw=1, zorder=0)
ax.set_axisbelow(True)
for side in ("top", "right", "left"):
    ax.spines[side].set_visible(False)
ax.spines["bottom"].set_color(MUTED)

fig.text(0.04, 0.94, "Resonance moves up 3 MHz as drive power rises", fontsize=14,
         weight="semibold", color=INK, ha="left")
fig.text(0.04, 0.895, "In-phase lock-in current at five drive powers (right), back gate 1 V. Traces offset for clarity.",
         fontsize=10, color=MUTED, ha="left")

fig.savefig(OUT.with_suffix(".svg"), facecolor=BG)
svg = OUT.with_suffix(".svg"); svg.write_text(re.sub(r"<!DOCTYPE[^>]*>\s*", "", svg.read_text(), count=1))
fig.savefig(OUT.with_suffix(".png"), facecolor=BG, dpi=200)
print("wrote", OUT.with_suffix(".svg"))
