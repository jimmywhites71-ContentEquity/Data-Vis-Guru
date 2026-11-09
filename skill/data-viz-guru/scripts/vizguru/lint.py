"""Automated pre-flight checks for a chart, and a colour-blindness check for a palette.

    from vizguru import lint
    for f in lint.check(fig):
        print(f)

    python -m vizguru.lint --palette            # check tokens.json, both modes
    python -m vizguru.lint --palette my.json    # check a client's brand tokens

`check` catches the mechanical failures (missing source, clipped or overlapping text, a
truncated bar axis, type too small for the medium, a second y-axis, a missing performance
disclosure). It cannot tell whether the chart is true, fair or interesting: that is what
references/qa-checklist.md and a human reviewer are for.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from itertools import combinations

import numpy as np
from matplotlib.colors import to_hex, to_rgb
from matplotlib.patches import Rectangle, Wedge
from matplotlib.text import Annotation

from .theme import get_theme, load_tokens, preset as get_preset


@dataclass(frozen=True)
class Finding:
    level: str  # "error" must be fixed before the chart ships; "warn" needs a decision
    code: str
    message: str

    def __str__(self) -> str:
        return f"[{self.level.upper():5}] {self.code}: {self.message}"


# ------------------------------------------------------------------ colour maths

def _linear(hex_color) -> np.ndarray:
    c = np.array(to_rgb(hex_color))
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def contrast(a, b) -> float:
    """WCAG 2 contrast ratio between two colours."""
    la, lb = (float(_linear(x) @ [0.2126, 0.7152, 0.0722]) for x in (a, b))
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


# Machado, Oliveira & Fernandes (2009) simulation matrices, severity 1.0, linear RGB.
_CVD = {
    "protan": [[0.152286, 1.052583, -0.204868], [0.114503, 0.786281, 0.099216], [-0.003882, -0.048116, 1.051998]],
    "deutan": [[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413], [-0.011820, 0.042940, 0.968881]],
    "tritan": [[1.255528, -0.076749, -0.178779], [-0.078411, 0.930809, 0.147602], [0.004733, 0.691367, 0.303900]],
}


def _oklab(lin: np.ndarray) -> np.ndarray:
    m1 = np.array([[0.4122214708, 0.5363325363, 0.0514459929], [0.2119034982, 0.6806995451, 0.1073969566],
                   [0.0883024619, 0.2817188376, 0.6299787005]])
    m2 = np.array([[0.2104542553, 0.7936177850, -0.0040720468], [1.9779984951, -2.4285922050, 0.4505937099],
                   [0.0259040371, 0.7827717662, -0.8086757660]])
    return m2 @ np.cbrt(m1 @ np.clip(lin, 0, 1))


def delta_e(a, b, cvd: str | None = None) -> float:
    """Colour difference in OKLab x 100, optionally as seen with a colour-vision deficiency."""
    la, lb = _linear(a), _linear(b)
    if cvd:
        m = np.array(_CVD[cvd])
        la, lb = m @ la, m @ lb
    return float(np.linalg.norm(_oklab(la) - _oklab(lb)) * 100)


def check_palette(tokens_path=None, min_cvd: float = 8.0, min_normal: float = 15.0) -> list[Finding]:
    """Check each mode's categorical palette: neighbouring slots must stay distinguishable
    for the common colour-vision deficiencies, the two diverging poles must too, and text
    colours must meet WCAG contrast on the surface."""
    out: list[Finding] = []
    for mode, m in load_tokens(tokens_path)["modes"].items():
        cat = m["categorical"]
        for i in range(len(cat) - 1):
            a, b = cat[i], cat[i + 1]
            if delta_e(a, b) < min_normal:
                out.append(Finding("error", "palette-similar", f"{mode}: slots {i + 1} and {i + 2} ({a}, {b}) are too close for anyone (dE {delta_e(a, b):.1f} < {min_normal})"))
            worst = min((delta_e(a, b, k), k) for k in ("protan", "deutan"))
            if worst[0] < min_cvd:
                out.append(Finding("error", "palette-cvd", f"{mode}: slots {i + 1} and {i + 2} ({a}, {b}) merge under {worst[1]} vision (dE {worst[0]:.1f} < {min_cvd}); reorder or re-step"))
        d = m["diverging"]
        worst = min((delta_e(d["negative"], d["positive"], k), k) for k in ("protan", "deutan"))
        if worst[0] < min_normal:
            out.append(Finding("error", "palette-diverging", f"{mode}: gain and loss colours merge under {worst[1]} vision (dE {worst[0]:.1f}); red/green pairs usually fail this"))
        for role, need in (("text_primary", 7.0), ("text_secondary", 4.5), ("text_muted", 3.0)):
            c = contrast(m[role], m["surface"])
            if c < need:
                out.append(Finding("error", "palette-contrast", f"{mode}: {role} is {c:.1f}:1 on the surface, needs {need}:1"))
        low = [c for c in cat if contrast(c, m["surface"]) < 3]
        if low:
            out.append(Finding("warn", "palette-faint", f"{mode}: {', '.join(low)} are under 3:1 on the surface; fine for lines and bars that carry a direct label, not for text or thin unlabeled marks"))
    return out


# ------------------------------------------------------------------ figure checks

def _texts(fig):
    for t in fig.findobj(lambda a: hasattr(a, "get_text") and hasattr(a, "get_fontsize")):
        if t.get_visible() and t.get_text().strip() and (t.get_alpha() is None or t.get_alpha() > 0):
            if t.axes is not None and not t.axes.get_visible():
                continue
            yield t


def check(fig, strict_title: bool = True) -> list[Finding]:
    """Run every mechanical check on a figure built with `vizguru.charts`."""
    out: list[Finding] = []
    meta = getattr(fig, "_vg", None)
    if meta is None:
        return [Finding("error", "not-framed", "Figure was not built with vizguru.charts.new_figure, so it has no title/source frame to check")]
    theme = get_theme(meta["mode"])
    ps = get_preset(meta["preset"])
    add = lambda level, code, msg: out.append(Finding(level, code, msg))

    title = (meta.get("title") or "").strip()
    if not title:
        add("error", "title-missing", "No title. The title should state the finding in a sentence")
    elif strict_title and len(title.split()) < 4:
        add("warn", "title-label", f"Title {title!r} reads as a label. Say what the reader should conclude, and put the measure in the subtitle")
    if not (meta.get("subtitle") or "").strip():
        add("warn", "subtitle-missing", "No subtitle. State what is measured, the units and the period")
    if not (meta.get("source") or "").strip():
        add("error", "source-missing", "No source line. Every client chart names where the data came from and its as-of date")
    if meta.get("performance") and "past performance" not in meta.get("footer", "").lower():
        add("error", "disclosure-missing", "Chart shows performance but the footer carries no past-performance statement")

    # One y-scale per plot.
    seen = {}
    for ax in fig.axes:
        key = tuple(np.round(ax.get_position().bounds, 4))
        if key in seen and ax.get_visible():
            add("error", "dual-axis", "Two axes share one plot area (twin axis). Index both series to a common base or use two stacked panels")
        seen[key] = ax

    for ax in fig.axes:
        if any(isinstance(p, Wedge) for p in ax.patches):
            add("warn", "pie", "Pie or donut found. A ranked bar or a single stacked bar is easier to compare unless there are two or three parts")
        bars = [p for p in ax.patches if isinstance(p, Rectangle) and p.get_width() and p.get_height()]
        if meta["kind"] in ("bar", "waterfall") and bars:
            horizontal = meta["kind"] == "bar"
            lo, hi = ax.get_xlim() if horizontal else ax.get_ylim()
            if not (min(lo, hi) <= 0 <= max(lo, hi)):
                add("error", "bar-baseline", "Bar axis does not include zero, so bar lengths misstate the differences")
        n_colors = len({to_hex(l.get_color()) for l in ax.lines if len(l.get_xdata()) > 2} - {to_hex(theme.context), to_hex(theme.axis)})
        if n_colors > 4:
            add("warn", "too-many-series", f"{n_colors} coloured lines in one plot. Highlight up to four and grey the rest, or use small multiples")

    fig.canvas.draw()  # axis labels only take their final position at draw time
    renderer = fig.canvas.get_renderer()
    fw, fh = fig.bbox.width, fig.bbox.height
    boxes = []
    for t in _texts(fig):
        floor = ps.min_pt * (0.85 if t.get_gid() == "footer" else 1)  # footnotes may sit one step smaller
        if t.get_fontsize() < floor - 0.01:
            add("error", "text-small", f"{t.get_text()[:40]!r} is {t.get_fontsize():.1f}pt; the minimum for {ps.name} is {floor:.1f}pt")
        bb = t.get_window_extent(renderer)
        if bb.x0 < -1 or bb.y0 < -1 or bb.x1 > fw + 1 or bb.y1 > fh + 1:
            add("error", "text-clipped", f"{t.get_text()[:40]!r} runs off the edge of the image")
        need = 3.0 if t.get_fontsize() * meta["scale"] >= 14 else 4.5
        col = to_hex(t.get_color())
        if t.axes is None or not any(isinstance(p, Rectangle) for p in t.axes.patches):
            if contrast(col, theme.surface) < need - 0.01:
                add("error", "text-contrast", f"{t.get_text()[:40]!r} is {contrast(col, theme.surface):.1f}:1 against the background, needs {need}:1")
        boxes.append((t, bb))
    hits = set()
    for (ta, a), (tb, b) in combinations(boxes, 2):
        if isinstance(ta, Annotation) is False and isinstance(tb, Annotation) is False and ta.axes is None and tb.axes is None:
            continue  # header and footer lines are laid out by new_figure
        pad = 1
        if a.x0 + pad < b.x1 and b.x0 + pad < a.x1 and a.y0 + pad < b.y1 and b.y0 + pad < a.y1:
            hits.add(tuple(sorted((ta.get_text()[:30], tb.get_text()[:30]))))
    for a, b in sorted(hits):
        add("warn", "text-overlap", f"Labels overlap: {a!r} and {b!r}")
    return out


def report(fig) -> bool:
    """Print findings; return True when there are no errors."""
    findings = check(fig)
    for f in findings:
        print(f)
    if not findings:
        print("lint: clean")
    return not any(f.level == "error" for f in findings)


if __name__ == "__main__":
    if "--palette" in sys.argv:
        rest = [a for a in sys.argv[1:] if a != "--palette"]
        found = check_palette(rest[0] if rest else None)
        for f in found:
            print(f)
        print("palette: " + ("FAIL" if any(f.level == "error" for f in found) else "ok"))
        sys.exit(1 if any(f.level == "error" for f in found) else 0)
    print(__doc__)
