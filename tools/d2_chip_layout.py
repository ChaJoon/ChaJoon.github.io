"""Render the D2 full-chip layout (cell TEAMAJ_DESIGN) as light and dark PNGs for the portfolio.

Usage: python d2_chip_layout.py <TEAMAJ_DESIGN.gds> <out-dir>
Writes p9-chip-layout.png (light, page default) and p9-chip-layout-dark.png (dark mode).
Needs gdstk and matplotlib. Layer colours are arbitrary; layer names are deliberately not shown.
"""
import sys
from pathlib import Path

import gdstk
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection

GDS = sys.argv[1]
OUT_DIR = Path(sys.argv[2])

# Lower layers first so the metals sit on top.
ORDER = [3, 6, 17, 25, 26, 51, 30, 31, 32, 210]

THEMES = {
    # Light: white like the page's cards (--surface), darker inks so thin wires stay visible.
    "p9-chip-layout.png": {
        "bg": "#FFFFFF", "alpha": 0.55,
        "colours": {3: "#9AA3AE", 6: "#2E8B57", 17: "#C0392B", 25: "#6D4FC9", 26: "#6D4FC9",
                    51: "#1F2937", 30: "#1D4ED8", 31: "#B7791F", 32: "#0F766E", 210: "#9AA3AE"},
    },
    # Dark: the original render.
    "p9-chip-layout-dark.png": {
        "bg": "#11151C", "alpha": 0.45,
        "colours": {3: "#555555", 6: "#3FA34D", 17: "#D64545", 25: "#8A6FDF", 26: "#8A6FDF",
                    51: "#E8E8E8", 30: "#3B82F6", 31: "#E0A400", 32: "#14B8A6", 210: "#888888"},
    },
}

lib = gdstk.read_gds(GDS)
top = {c.name: c for c in lib.cells}["TEAMAJ_DESIGN"]

by_layer = {}
for poly in top.get_polygons():
    by_layer.setdefault(poly.layer, []).append(poly.points)
layers = ORDER + [l for l in by_layer if l not in ORDER]

xs = [pt[0] for polys in by_layer.values() for p in polys for pt in p]
ys = [pt[1] for polys in by_layer.values() for p in polys for pt in p]

for name, theme in THEMES.items():
    fig, ax = plt.subplots(figsize=(9, 9), dpi=160)
    fig.patch.set_facecolor(theme["bg"])
    ax.set_facecolor(theme["bg"])
    for layer in layers:
        if layer in by_layer:
            ax.add_collection(PolyCollection(by_layer[layer], facecolors=theme["colours"].get(layer, "#999999"),
                                             edgecolors="none", alpha=theme["alpha"]))
    ax.set_xlim(min(xs) - 1, max(xs) + 1)
    ax.set_ylim(min(ys) - 1, max(ys) + 1)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.savefig(OUT_DIR / name, facecolor=theme["bg"], bbox_inches="tight", pad_inches=0.1)
    plt.close(fig)
    print("wrote", OUT_DIR / name)
