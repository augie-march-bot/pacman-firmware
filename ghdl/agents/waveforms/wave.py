"""wave.py:  timing diagrams from a GHDL VCD, for the firmware description (pacman_docs/agents).

A diagram is a list of rows, top to bottom.  Each row is one signal of the VCD:

    bit(name, label)                         a single bit
    bus(name, label, fmt=..., show=...)      a vector:  a box per value, labelled with fmt(value)
                                             (show(value) False:  box drawn, no label)
    strobe(name, label)                      a single bit drawn as ticks (for dense one-clock pulses)

    plot("out.pdf", "file.vcd", rows, t0, t1, marks={time: text}, notes=[(t0, t1, label, text)],
         arrows=[(t, label, level, text, dx, dy)], unit="ns")

marks:  a dashed vertical line across all rows, with its text on top.  notes:  text centred on the span t0-t1
in the row with that label, just above its low level.  arrows:  an arrow to time t at the level (0 or 1) of
that row, from its text dx, dy points away.  bit(..., count=True):  each high period numbered below the row.

Names are full VCD names ("tb.uut.sig[7:0]"); a vector can also be cut with bits=(hi, lo).  Times in ns.

The figures are drawn at their printed size (the text width of firmware.tex, 6.9 in) and typeset by LaTeX
(pgf) in the document's font:  include them unscaled.
"""
import matplotlib
matplotlib.use("pgf")
import matplotlib.pyplot as plt
plt.rcParams.update({
    "pgf.texsystem": "pdflatex",
    "pgf.rcfonts": False,
    "pgf.preamble": r"\usepackage{lmodern}\usepackage[T1]{fontenc}",
    "font.family": "serif",
    "font.size": 10,
})
from vcdvcd import VCDVCD

_cache = {}
WIDTH = 6.9         # in:  \textwidth of firmware.tex
LW = 1.0            # pt
LABEL = 10          # row labels and the axis label (pt)
SMALL = 9           # ticks, marks, notes, arrows (pt)


def _tex(s):
    return "".join("\\" + c if c in "_%&#$" else c for c in s)


def _vcd(path):
    if path not in _cache:
        _cache[path] = VCDVCD(path)
    return _cache[path]


def _series(vcd, name, t0, t1, bits=None):
    """(times_ns, values) of the changes in [t0, t1], starting with the value at t0."""
    tv = vcd[name].tv
    width = int(vcd[name].size)
    out = []
    for t_fs, v in tv:
        t = t_fs / 1e6
        if bits is not None:                # only the selected bits decide (others may be U)
            v = v.rjust(width, v[0] if v[0] in "xXzZuU" else "0")
            hi, lo = bits
            v = v[width - 1 - hi:width - lo]
        if any(c not in "01" for c in v):
            val = None                      # U / X / Z:  shown as unknown
        else:
            val = int(v, 2)
        if t <= t0:
            out = [(t0, val)]
        elif t <= t1:
            if out and out[-1][1] == val:
                continue
            out.append((t, val))
        else:
            break
    return out


class bit:
    def __init__(self, name, label, bits=None, count=False):
        self.name, self.label, self.bits, self.count, self.h = name, label, bits, count, 1.0


class strobe(bit):
    pass


class bus:
    def __init__(self, name, label, fmt=lambda v: "%X" % v, show=lambda v: True, bits=None, size=8):
        self.name, self.label, self.fmt, self.show, self.bits, self.size, self.h = name, label, fmt, show, bits, size, 1.0


def plot(out, vcd_path, rows, t0, t1, marks=None, notes=None, arrows=None, unit="ns", width=WIDTH, row_h=0.26,
         slope=None):
    vcd = _vcd(vcd_path)
    scale = 1000.0 if unit == "us" else 1.0
    slope = (t1 - t0) / 400.0 if slope is None else slope
    n = len(rows)
    fig, ax = plt.subplots(figsize=(width, 0.5 + row_h * n * 1.6))
    yt, yl = [], []
    for i, r in enumerate(rows):
        y = (n - 1 - i) * 1.6
        yt.append(y + 0.5)
        yl.append(_tex(r.label))
        s = _series(vcd, r.name, t0, t1, getattr(r, "bits", None))
        if isinstance(r, strobe):
            ax.plot([t0 / scale, t1 / scale], [y, y], "k-", lw=LW)
            for k, (t, v) in enumerate(s):
                if v == 1:
                    te = s[k + 1][0] if k + 1 < len(s) else t1
                    ax.plot([t / scale, t / scale, te / scale, te / scale], [y, y + 1, y + 1, y], "k-", lw=LW)
        elif isinstance(r, bit):
            xs, ys = [], []
            for k, (t, v) in enumerate(s):
                level = 0.5 if v is None else v
                if k:
                    xs.append(t / scale)
                    ys.append(ys[-1])
                xs.append(t / scale)
                ys.append(y + level)
            xs.append(t1 / scale)
            ys.append(ys[-1])
            ax.plot(xs, ys, "k-", lw=LW)
            if r.count:
                ones = [(t, s[k + 1][0] if k + 1 < len(s) else t1) for k, (t, v) in enumerate(s) if v == 1]
                for j, (a, b) in enumerate(ones):
                    ax.text((a + b) / 2 / scale, y - 0.1, "%d" % (j + 1), ha="center", va="top", fontsize=SMALL)
        else:
            for k, (t, v) in enumerate(s):
                te = s[k + 1][0] if k + 1 < len(s) else t1
                a = t + (slope / 2 if k else 0)
                b = te - (slope / 2 if k + 1 < len(s) else 0)
                if v is None:
                    ax.fill_between([a / scale, b / scale], y, y + 1, color="0.85", lw=0)
                ax.plot([a / scale, b / scale], [y + 1, y + 1], "k-", lw=LW)
                ax.plot([a / scale, b / scale], [y, y], "k-", lw=LW)
                if k + 1 < len(s):                       # the crossing to the next value
                    c0, c1 = (te - slope / 2) / scale, (te + slope / 2) / scale
                    ax.plot([c0, c1], [y, y + 1], "k-", lw=LW)
                    ax.plot([c0, c1], [y + 1, y], "k-", lw=LW)
                if v is not None and r.show(v):
                    ax.text((a + b) / 2 / scale, y + 0.5, _tex(r.fmt(v)), ha="center", va="center",
                            fontsize=r.size, clip_on=True)
    row_y = lambda label: (n - 1 - [r.label for r in rows].index(label)) * 1.6
    for a, b, label, txt in (notes or []):
        ax.text((a + b) / 2 / scale, row_y(label) + 0.12, _tex(txt), ha="center", va="bottom", fontsize=SMALL)
    for t, label, level, txt, dx, dy in (arrows or []):
        ax.annotate(_tex(txt), xy=(t / scale, row_y(label) + level), xytext=(dx, dy), textcoords="offset points",
                    ha="right" if dx < 0 else "left", va="center", fontsize=SMALL,
                    arrowprops=dict(arrowstyle="-|>", color="k", lw=0.6, shrinkA=1, shrinkB=1,
                                    mutation_scale=7))
    for t, txt in (marks or {}).items():
        ax.axvline(t / scale, color="0.5", ls="--", lw=0.8)
        ax.text(t / scale, n * 1.6 - 0.35, _tex(txt), ha="center", va="bottom", fontsize=SMALL)
    ax.set_yticks(yt)
    ax.set_yticklabels(yl, fontsize=LABEL)
    ax.tick_params(axis="y", length=0)
    ax.tick_params(axis="x", labelsize=SMALL)
    bottom = -0.75 if any(getattr(r, "count", False) for r in rows[-1:]) else -0.4
    ax.set_ylim(bottom, n * 1.6 + (0.4 if marks else -0.2))
    ax.set_xlim(t0 / scale, t1 / scale)
    ax.set_xlabel(r"Time ($\mu$s)" if unit == "us" else "Time (%s)" % unit, fontsize=LABEL)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)
