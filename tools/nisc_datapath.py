"""NISC picoMIPS datapath, redrawn from picoMIPS.sv for the portfolio site.

Every block, field and bus width below follows the SystemVerilog source:
  pc.sv, prog.sv (16-bit control word), addr_reg.sv, wave_rom.sv, alu.sv.
Control signals are shown as net labels (red tags) rather than wires: each
tag names the control-word field that drives that pin directly, with no decoder.

Usage: python nisc_datapath.py <font_dir> <out_stem>
Writes <out_stem>.svg and <out_stem>.png.
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch, Polygon, Circle, Rectangle

FONT_DIR, OUT = Path(sys.argv[1]), Path(sys.argv[2])
for f in FONT_DIR.glob("*.ttf"):
    font_manager.fontManager.addfont(str(f))
SANS, MONO = "IBM Plex Sans", "IBM Plex Mono"
plt.rcParams.update({"svg.fonttype": "path", "font.family": SANS})

# ---------- Palette: the site's light-theme tokens ----------
BG      = "#FFFFFF"
INK     = "#13213A"
MUTED   = "#4E5F78"
FILL    = "#F2F5F9"   # block fill, a step off the background
DATA    = "#1B4F8A"   # sample / arithmetic values
ADDR    = "#286E49"   # addresses (PC -> program ROM, ADDR -> waveform ROM)
CTRL    = "#A3271F"   # control-word fields
CTRL_BG = "#F8E6E4"

W, H = 100, 64                 # drawing units; 1 unit = 0.1 inch
fig = plt.figure(figsize=(W / 10, H / 10), dpi=100, facecolor=BG)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis("off"); ax.set_facecolor(BG)

LW = 1.4


def text(x, y, s, size=10, color=INK, family=SANS, weight="regular", ha="center", va="center", **kw):
    ax.text(x, y, s, fontsize=size, color=color, family=family, weight=weight, ha=ha, va=va, **kw)


def block(x0, y0, w, h, title, sub=None, detail=None):
    ax.add_patch(FancyBboxPatch((x0, y0), w, h, boxstyle="round,pad=0,rounding_size=0.8",
                                fc=FILL, ec=INK, lw=LW, zorder=2))
    cx = x0 + w / 2
    if sub is None and detail is None:
        text(cx, y0 + h / 2, title, size=12, weight="semibold", zorder=3)
        return
    lines = [(title, 12, INK, SANS, "semibold")]
    if sub:
        lines.append((sub, 9, MUTED, MONO, "regular"))
    if detail:
        lines.append((detail, 9, MUTED, MONO, "regular"))
    step = 2.6
    top = y0 + h / 2 + step * (len(lines) - 1) / 2
    for i, (s, size, c, fam, wt) in enumerate(lines):
        text(cx, top - i * step, s, size=size, color=c, family=fam, weight=wt, zorder=3)


def wire(points, color, arrow=True, lw=LW):
    xs, ys = zip(*points)
    ax.plot(xs, ys, color=color, lw=lw, solid_capstyle="butt", solid_joinstyle="miter", zorder=1)
    if arrow:
        (x1, y1), (x2, y2) = points[-2], points[-1]
        ax.annotate("", xy=(x2, y2), xytext=(x1 + (x2 - x1) * 0.999, y1 + (y2 - y1) * 0.999),
                    arrowprops=dict(arrowstyle="-|>,head_length=0.55,head_width=0.28",
                                    color=color, lw=lw, shrinkA=0, shrinkB=0), zorder=4)


def bus_width(x, y, n, color, vertical=False, flip=False):
    """Schematic bus-width mark: a short slash with the bit count beside it."""
    d = 0.9
    if vertical:
        ax.plot([x - d, x + d], [y - d * 0.6, y + d * 0.6], color=color, lw=1.1, zorder=3)
        text(x - 1.4 if flip else x + 1.4, y, str(n), size=8.5, color=color, family=MONO,
             ha="right" if flip else "left")
    else:
        ax.plot([x - d * 0.6, x + d * 0.6], [y - d, y + d], color=color, lw=1.1, zorder=3)
        text(x, y - 2.0 if flip else y + 2.0, str(n), size=8.5, color=color, family=MONO)


def tag(x, y, name, ha="center"):
    """Control-field net label sitting on a pin."""
    t = ax.text(x, y, name, fontsize=8.5, family=MONO, color=CTRL, ha=ha, va="center", zorder=5,
                bbox=dict(boxstyle="round,pad=0.28,rounding_size=0.25", fc=CTRL_BG, ec=CTRL, lw=0.9))
    return t


def pin_down(x, y_tag, y_block, name):
    """Tag above a block with a short red stub into the block's top edge."""
    wire([(x, y_tag - 1.4), (x, y_block)], CTRL, lw=1.1)
    tag(x, y_tag, name)


# =====================================================================
# Section labels
# =====================================================================
text(2, 63.2, "CONTROL PATH", size=8.5, color=MUTED, family=MONO, weight="medium", ha="left")
text(2, 27.5, "DATAPATH", size=8.5, color=MUTED, family=MONO, weight="medium", ha="left")

# =====================================================================
# Control path (pc.sv, prog.sv)
# =====================================================================
CY = 52                                      # control row centre line
block(6, CY - 5, 22, 10, "Next-PC logic", "PC+1 or target")
block(34, CY - 5, 12, 10, "PC", "4-bit reg")
block(54, CY - 5, 22, 10, "Control word store", "16 × 16-bit ROM")

# SW[8] into the branch condition
text(0.3, CY + 2.6, "SW[8]", size=8.5, family=MONO, ha="left", color=INK)
wire([(0.3, CY), (6, CY)], INK, lw=1.1)
# branch fields onto the next-PC logic
pin_down(11, 59.4, CY + 5, "branch_type")
pin_down(22.4, 59.4, CY + 5, "branch_target")
# next PC -> PC register
wire([(28, CY), (34, CY)], ADDR); bus_width(31, CY, 4, ADDR)
# PC -> program ROM address
wire([(46, CY), (54, CY)], ADDR); bus_width(50, CY, 4, ADDR)
# PC fed back for PC+1
wire([(40, CY - 5), (40, CY - 8.2), (17, CY - 8.2), (17, CY - 5)], ADDR); bus_width(28.5, CY - 8.2, 4, ADDR, flip=True)

# ---------- 16-bit control word, as a bit-field strip ----------
SX, SY, CW, CH = 16, 36, 4.6, 4.2           # strip origin, cell width/height
FIELDS = [  # (name, msb, lsb) straight from prog.sv
    ("acc_we", 15, 15), ("acc_clear", 14, 14), ("addr_load", 13, 13), ("addr_inc", 12, 12),
    ("branch_type", 11, 10), ("branch_target", 9, 6), ("kernel_value", 5, 0),
]
col = lambda bit: SX + (15 - bit) * CW     # left edge of a bit's cell
# ROM output -> strip
wire([(65, CY - 5), (65, SY + CH)], CTRL); bus_width(65, 43.7, 16, CTRL, vertical=True)
text(SX + 16 * CW + 1.2, SY + CH / 2, "control word", size=9, color=MUTED, ha="left")
for bit in range(16):
    ax.add_patch(Rectangle((col(bit), SY), CW, CH, fc=CTRL_BG, ec=CTRL, lw=0.6, zorder=2))
    text(col(bit) + CW / 2, SY + CH / 2, str(bit), size=8, color=CTRL, family=MONO, zorder=3)
# heavier rules on field boundaries
for name, msb, lsb in FIELDS:
    ax.add_patch(Rectangle((col(msb), SY), (msb - lsb + 1) * CW, CH, fc="none", ec=CTRL, lw=1.6, zorder=3))
# field names under the strip; single-bit fields staggered on two rows so each name gets room
LABEL_Y = {"acc_we": 33.2, "acc_clear": 30.4, "addr_load": 33.2, "addr_inc": 30.4,
           "branch_type": 33.2, "branch_target": 33.2, "kernel_value": 33.2}
for name, msb, lsb in FIELDS:
    cx = col(msb) + (msb - lsb + 1) * CW / 2
    y = LABEL_Y[name]
    ax.plot([cx, cx], [SY, y + 0.9], color=CTRL, lw=0.8, zorder=1)
    text(cx, y, name, size=8.5, color=CTRL, family=MONO)

# =====================================================================
# Datapath (addr_reg.sv, wave_rom.sv, alu.sv)
# =====================================================================
DY = 15                                      # datapath centre line
BH = 10
block(6, DY - BH / 2, 12, BH, "ADDR", "8-bit reg", "SW−2 or +1")
block(23, DY - BH / 2, 14, BH, "Waveform ROM", "256 × 8-bit")
block(42, DY - BH / 2, 12, BH, "Multiply", "8×8→16 DSP")
block(58, DY - BH / 2, 8, BH, "[14:7]", "÷128")
ax.add_patch(Circle((71.5, DY), 2.6, fc=FILL, ec=INK, lw=LW, zorder=2))
text(71.5, DY + 0.15, "+", size=15, weight="medium", zorder=3)
# 2:1 mux (acc_clear ? 0 : sum)
MX0, MX1 = 77.5, 81
ax.add_patch(Polygon([(MX0, DY - 5.5), (MX0, DY + 5.5), (MX1, DY + 3.6), (MX1, DY - 3.6)],
                     closed=True, fc=FILL, ec=INK, lw=LW, zorder=2))
text(MX0 + 0.9, DY + 2.6, "0", size=8, color=MUTED, family=MONO, ha="left", zorder=3)
text(MX0 + 0.9, DY - 2.6, "1", size=8, color=MUTED, family=MONO, ha="left", zorder=3)
block(85, DY - BH / 2, 10, BH, "ACC", "8-bit reg")

# SW[7:0] into ADDR
text(0.3, DY + 4.6, "SW[7:0]", size=8.5, family=MONO, ha="left")
wire([(0.8, DY), (6, DY)], INK, lw=1.1); bus_width(3.4, DY, 8, INK, flip=True)
# control pins on the datapath
pin_down(9.2, DY + 9.6, DY + BH / 2, "addr_load")
pin_down(14.8, DY + 12.4, DY + BH / 2, "addr_inc")
pin_down(48, DY + 9.6, DY + BH / 2, "kernel_value")
text(48.8, DY + BH / 2 + 1.5, "6-bit, zero-extended", size=8, color=MUTED, ha="left")
pin_down(79.25, DY + 12.4, DY + 4.6, "acc_clear")
pin_down(90, DY + 9.6, DY + BH / 2, "acc_we")

# address and data buses
wire([(18, DY), (23, DY)], ADDR); bus_width(20.5, DY, 8, ADDR)
wire([(37, DY), (42, DY)], DATA); bus_width(39.5, DY, 8, DATA)
wire([(54, DY), (58, DY)], DATA); bus_width(56, DY, 16, DATA)
wire([(66, DY), (68.9, DY)], DATA)
# sum -> mux input 0 (top); constant zero -> mux input 1 (bottom)
wire([(74.1, DY), (75.6, DY), (75.6, DY + 2.6), (MX0, DY + 2.6)], DATA)
text(75.3, DY - 2.6, "0", size=9, family=MONO, ha="right", color=DATA)
wire([(75.8, DY - 2.6), (MX0, DY - 2.6)], DATA, lw=1.1)
wire([(MX1, DY), (85, DY)], DATA)
# ACC output: LEDs and feedback to the adder
wire([(95, DY), (97.5, DY), (97.5, 3.2)], DATA)
ax.add_patch(Circle((97.5, 6.5), 0.45, fc=DATA, ec="none", zorder=4))
wire([(97.5, 6.5), (71.5, 6.5), (71.5, DY - 2.6)], DATA)
text(96.6, 1.6, "LED[7:0]", size=9, family=MONO, ha="right")
bus_width(97.5, 10.5, 8, DATA, vertical=True, flip=True)

# =====================================================================
# Legend and reset note
# =====================================================================
LX, LY = 6, 3.6
for i, (label, c) in enumerate([("data", DATA), ("address", ADDR)]):
    x = LX + i * 13
    ax.plot([x, x + 4], [LY, LY], color=c, lw=LW)
    text(x + 5, LY, label, size=8.5, color=MUTED, ha="left")
tag(LX + 28, LY, "field")
text(LX + 31.6, LY, "control-word field wired straight to the pin", size=8.5, color=MUTED, ha="left")
text(LX, LY - 2.6, "SW[9]: synchronous active-low reset for PC, ADDR and ACC", size=8.5, color=MUTED, ha="left")

fig.savefig(OUT.with_suffix(".svg"), facecolor=BG)
# drop the DTD line: some hosts refuse SVGs that carry one
svg = OUT.with_suffix(".svg"); svg.write_text(__import__("re").sub(r"<!DOCTYPE[^>]*>\s*", "", svg.read_text(), count=1))
fig.savefig(OUT.with_suffix(".png"), facecolor=BG, dpi=200)
print("wrote", OUT.with_suffix(".svg"), OUT.with_suffix(".png"))
