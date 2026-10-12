"""Three figures for the cryptanalysis entry: the statistical test behind each attack.

Reads tools/crypto_stats.json, which holds summary numbers only (no keys, ciphertext or
plaintext). The analysis that produced those numbers is deliberately not in this repository:
the cipher types are reused each year, so a working solver could help future students.

Usage: python crypto_figures.py <font_dir> <stats_json> <out_dir>
Writes p7-letter-freq.svg, p7-xor-keylength.svg and p7-transposition.svg.
"""
import json
import re
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

FONT_DIR, STATS, OUT_DIR = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
for f in FONT_DIR.glob("*.ttf"):
    font_manager.fontManager.addfont(str(f))
SANS, MONO = "IBM Plex Sans", "IBM Plex Mono"
plt.rcParams.update({"svg.fonttype": "path", "font.family": SANS})

# Site light-theme tokens (blueprint)
BG, INK, MUTED, GRID = "#FFFFFF", "#13213A", "#4E5F78", "#D9E1EA"
DATA, DATA_LIGHT, OFF = "#1B4F8A", "#A9C1DE", "#C9D2DD"

S = json.loads(STATS.read_text())
W, H = 6.4, 3.9                     # inches; shown at about 420 px wide in the Read more panel
L, R, T, B = 0.11, 0.97, 0.76, 0.17  # axes box as figure fractions


def frame(ax, ygrid=True):
    ax.set_facecolor(BG)
    ax.tick_params(axis="both", length=0, pad=6, labelsize=11, colors=MUTED)
    if ygrid:
        ax.yaxis.grid(True, color=GRID, lw=1, zorder=0)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(MUTED)


def titles(fig, title, sub):
    fig.text(L, 0.92, title, fontsize=15, weight="semibold", color=INK, ha="left")
    fig.text(L, 0.845, sub, fontsize=11, color=MUTED, ha="left")


def save(fig, name):
    svg = OUT_DIR / name
    fig.savefig(svg, facecolor=BG)
    # drop the DTD line: some hosts refuse SVGs that carry one
    svg.write_text(re.sub(r"<!DOCTYPE[^>]*>\s*", "", svg.read_text(), count=1))
    plt.close(fig)
    print("wrote", svg)


# ---------- 1. Substitution: same frequency profile as English, letters relabelled ----------
sub = S["sub"]
fig, ax = plt.subplots(figsize=(W, H), dpi=100, facecolor=BG)
fig.subplots_adjust(left=L, right=R, top=T, bottom=B)
frame(ax)
ranks = range(1, 27)
ax.bar(ranks, [v * 100 for v in sub["cipher_rank"]], width=0.62, color=DATA, zorder=2, label="Cipher 1")
ax.plot(ranks, [v * 100 for v in sub["english_rank"]], color=MUTED, lw=2, marker="o", ms=4.5, zorder=3,
        label="English")
ax.set_xlim(0.3, 26.7)
ax.set_ylim(0, 14)
ax.set_xticks([1, 5, 10, 15, 20, 26], ["1st", "5th", "10th", "15th", "20th", "26th"], family=MONO)
ax.set_yticks(range(0, 15, 4), [f"{t}%" for t in range(0, 15, 4)], family=MONO)
ax.set_xlabel("letters ranked from most to least common", fontsize=11, color=MUTED, labelpad=6)
h, lab = ax.get_legend_handles_labels()   # bars first, so the legend reads cipher, then reference
order = [lab.index("Cipher 1"), lab.index("English")]
ax.legend([h[i] for i in order], [lab[i] for i in order], loc="upper right", frameon=False, fontsize=11,
          labelcolor=INK, handlelength=1.4)
ax.text(26.4, 8.6, f"index of coincidence\ncipher {sub['ioc_cipher']:.3f}\nEnglish {sub['ioc_english']:.3f}\n"
        f"random {sub['ioc_random']:.3f}", ha="right", va="top", fontsize=10, family=MONO, color=MUTED,
        linespacing=1.5)
titles(fig, "Cipher 1 keeps the shape of English",
       f"Its {sub['n']} letters ranked by frequency; which letter is which is not shown")
save(fig, "p7-letter-freq.svg")

# ---------- 2. Repeating-key XOR: only even key lengths decode the whole file ----------
xor = S["xor"]
fig, ax = plt.subplots(figsize=(W, H), dpi=100, facecolor=BG)
fig.subplots_adjust(left=L, right=R, top=T, bottom=B)
frame(ax)
for r in xor:
    k, v = r["L"], r["printable"] * 100
    color = DATA if k == 2 else (DATA_LIGHT if k % 2 == 0 else OFF)
    ax.bar(k, v, width=0.6, color=color, zorder=2)
    ax.text(k, v + 2, f"{v:.0f}%", ha="center", va="bottom", fontsize=10, family=MONO,
            color=INK if k % 2 == 0 else MUTED)
ax.set_xlim(0.4, 10.6)
ax.set_ylim(0, 112)
ax.set_xticks(range(1, 11), [str(k) for k in range(1, 11)], family=MONO)
ax.set_yticks(range(0, 101, 25), [f"{t}%" for t in range(0, 101, 25)], family=MONO)
ax.set_xlabel("assumed key length (bytes)", fontsize=11, color=MUTED, labelpad=6)
ax.text(2.36, 84, "shortest\nthat\nworks", fontsize=10, color=INK, ha="left", va="center", linespacing=1.3)
titles(fig, "Only even key lengths decode the whole file",
       "Share of the 90 bytes that decode to readable text, best key per length")
save(fig, "p7-xor-keylength.svg")

# ---------- 3. Transposition: rail fence ruled out, one columnar arrangement reads as English ----------
tr = S["trans"]
fig, ax = plt.subplots(figsize=(W, H), dpi=100, facecolor=BG)
fig.subplots_adjust(left=0.30, right=R, top=T, bottom=B)
frame(ax, ygrid=False)
ax.xaxis.grid(True, color=GRID, lw=1, zorder=0)
ax.axvspan(tr["english_ref_min"], tr["english_ref_max"], color=DATA_LIGHT, alpha=0.45, lw=0, zorder=1)
ax.text((tr["english_ref_min"] + tr["english_ref_max"]) / 2, 1.62, "ordinary\nEnglish", ha="center",
        va="center", fontsize=10, color=DATA, linespacing=1.2)
ax.scatter([r["best"] for r in tr["rail"]], [1] * len(tr["rail"]), s=34, color=OFF, edgecolor=MUTED,
           lw=0.8, zorder=3)
for r in tr["columnar"]:
    hit = r["best"] > tr["english_ref_min"]
    ax.scatter(r["best"], 0, s=60 if hit else 34, color=DATA if hit else OFF,
               edgecolor=DATA if hit else MUTED, lw=0.8, zorder=4)
    if hit:
        ax.text(r["best"], -0.32, f"width {r['L']}", ha="center", va="top", fontsize=10, color=INK)
ax.set_xlim(-7.4, -3.5)
ax.set_ylim(-0.75, 1.9)
ax.set_yticks([1, 0], [f"Rail fence\n{tr['rail'][0]['rails']}–{tr['rail'][-1]['rails']} rails",
                        f"Keyed columnar\nwidth {tr['columnar'][0]['L']}–{tr['columnar'][-1]['L']}"],
              fontsize=11, color=INK, linespacing=1.3)
ax.set_xticks([-7, -6, -5, -4], ["−7", "−6", "−5", "−4"], family=MONO)
ax.set_xlabel("quadgram fitness (higher = more like English)", fontsize=11, color=MUTED, labelpad=6)
fig.text(L, 0.92, "One columnar arrangement reads as English", fontsize=15, weight="semibold",
         color=INK, ha="left")
fig.text(L, 0.845, "Best score for each candidate setting, mean log10 probability per four-letter group",
         fontsize=11, color=MUTED, ha="left")
save(fig, "p7-transposition.svg")
