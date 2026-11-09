"""Static charts for investment communication.

Every function returns a matplotlib Figure laid out the same way:

    Title      - the finding, as a sentence
    Subtitle   - what is measured, the units, the period
    [ plot ]   - direct labels instead of a legend wherever there is room
    Footer     - source, as-of date, basis, and the performance disclosure when relevant

Save with `vizguru.export.save(fig, "name")` and check with `vizguru.lint.check(fig)`.
"""
from __future__ import annotations

import textwrap
from typing import Iterable, Sequence

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import matplotlib.patheffects as pe
from matplotlib.colors import LinearSegmentedColormap, to_rgb
from matplotlib.ticker import FuncFormatter

from . import finance
from .theme import Theme, get_theme, preset as get_preset

PAST_PERFORMANCE = "Past performance is not a reliable indicator of future results."


# --------------------------------------------------------------------------- layout

def new_figure(title: str, subtitle: str | None = None, source: str | None = None,
               note: str | None = None, *, preset: str = "slide_16x9", mode: str = "light",
               kind: str = "chart", performance: bool = False, disclosure: str | None = PAST_PERFORMANCE,
               left_pad: float = 0.55, right_pad: float = 0.1, bottom_pad: float = 0.32,
               nrows: int = 1, ncols: int = 1, hspace: float = 0.5, wspace: float = 0.25,
               sharey: bool = False):
    """Create the standard frame. Returns (fig, axes, theme, scale).

    `performance=True` marks the chart as showing investment performance, which appends the
    `disclosure` line to the footer and makes the linter insist that it is there.
    Pads are in inches at text scale 1 and are scaled with the preset.
    """
    theme = get_theme(mode)
    ps = get_preset(preset)
    s = ps.text_scale
    W, H = ps.inches
    fig = plt.figure(figsize=(W, H), dpi=ps.dpi)
    size = lambda k: theme.sizes[k] * s
    M = 0.5 * s
    usable_pt = (W - 2 * M) * 72

    def wrap(text, pt, weight=1.0, balance=False):
        if not text:
            return []
        width = max(20, int(usable_pt / (pt * 0.5 * weight)))
        lines = textwrap.wrap(text, width)
        if balance and len(lines) > 1:  # even out the lines so a title never ends on an orphan word
            for w in range(int(np.ceil(len(text) / len(lines))), width + 1):
                even = textwrap.wrap(text, w)
                if len(even) == len(lines):
                    return even
        return lines

    y = H - M
    for line in wrap(title, size("title"), 1.06, balance=True):
        fig.text(M / W, y / H, line, fontsize=size("title"), fontweight=theme.title_weight,
                 color=theme.text_primary, va="top", ha="left", gid="title")
        y -= size("title") * 1.25 / 72
    y -= 0.05 * s
    for line in wrap(subtitle, size("subtitle")):
        fig.text(M / W, y / H, line, fontsize=size("subtitle"), color=theme.text_secondary,
                 va="top", ha="left", gid="subtitle")
        y -= size("subtitle") * 1.35 / 72
    top = y - 0.25 * s

    foot = []
    if source:
        foot += wrap(f"Source: {source}", size("footer"))
    extra = " ".join(x for x in [note, disclosure if performance else None] if x)
    foot += wrap(extra, size("footer"))
    fy = M * 0.7 + (len(foot) - 1) * size("footer") * 1.4 / 72
    for line in foot:
        fig.text(M / W, fy / H, line, fontsize=size("footer"), color=theme.text_muted,
                 va="bottom", ha="left", gid="footer")
        fy -= size("footer") * 1.4 / 72
    bottom = M * 0.7 + len(foot) * size("footer") * 1.4 / 72 + (0.18 + bottom_pad) * s

    gs = fig.add_gridspec(nrows, ncols, left=(M + left_pad * s) / W, right=1 - (M + right_pad * s) / W,
                          top=top / H, bottom=bottom / H, hspace=hspace, wspace=wspace)
    axes = gs.subplots(sharey=sharey, squeeze=False)
    for ax in axes.ravel():
        ax.tick_params(labelsize=size("tick"))
    fig._vg = dict(title=title, subtitle=subtitle, source=source, note=note, kind=kind,
                   performance=performance, footer=" ".join(foot), preset=preset, mode=mode,
                   scale=s, artists={})
    return fig, (axes[0, 0] if nrows * ncols == 1 else axes), theme, s


def _label_width(labels: Iterable[str], pt: float) -> float:
    """Rough width in inches of the longest label - used to reserve room for direct labels."""
    return max((len(str(x)) for x in labels), default=0) * pt * 0.55 / 72 + 0.2


def _date_axis(ax, index: pd.DatetimeIndex) -> None:
    years = (index[-1] - index[0]).days / 365.25
    if years > 2.5:
        step = max(1, int(np.ceil(years / 8)))
        ax.xaxis.set_major_locator(mdates.YearLocator(step))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    else:
        ax.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=4, maxticks=7))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.set_xlim(index[0], index[-1])
    ax.spines["bottom"].set_visible(True)


def pct(decimals: int = 0, sign: bool = False):
    """Formatter for fractions shown as percentages (0.123 -> '12%'), with a true minus."""
    def f(v, _=None):
        txt = f"{v * 100:+.{decimals}f}%" if sign else f"{v * 100:.{decimals}f}%"
        return txt.replace("-", "−")
    return f


def num(decimals: int = 0, prefix: str = "", suffix: str = ""):
    def f(v, _=None):
        return f"{prefix}{v:,.{decimals}f}{suffix}".replace("-", "−")
    return f


def spread_labels(ax, ys: Sequence[float], min_gap_px: float) -> list[float]:
    """Nudge label y-positions (data coords) apart so end-of-line labels never overlap."""
    if len(ys) == 0:
        return []
    disp = np.array([ax.transData.transform((0, y))[1] for y in ys])
    order = np.argsort(disp)
    pos = disp[order].copy()
    for _ in range(100):
        moved = False
        for i in range(1, len(pos)):
            gap = pos[i] - pos[i - 1]
            if gap < min_gap_px:
                shift = (min_gap_px - gap) / 2
                pos[i - 1] -= shift
                pos[i] += shift
                moved = True
        if not moved:
            break
    lo, hi = ax.get_window_extent().y0, ax.get_window_extent().y1
    over = pos[-1] - hi
    if over > 0:
        pos -= over
    under = lo - pos[0]
    if under > 0:
        pos += under
    out = np.empty_like(pos)
    out[order] = pos
    inv = ax.transData.inverted()
    return [inv.transform((0, p))[1] for p in out]


def _ink_on(fill: str, theme: Theme) -> str:
    """Black or white text, whichever reads better on `fill`."""
    r, g, b = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in to_rgb(fill)]
    lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return "#0b0b0b" if lum > 0.36 else "#ffffff"


# --------------------------------------------------------------------------- charts

def line_chart(data: pd.DataFrame, title: str, subtitle: str | None = None, source: str | None = None,
               *, highlight: Sequence[str] | None = None, value_format=None, log: bool = False,
               baseline: float | None = None, annotations: Sequence[dict] = (),
               note: str | None = None, performance: bool = False, preset: str = "slide_16x9",
               mode: str = "light"):
    """Time series with direct end-of-line labels.

    `highlight` names the series that carry the story (max 4 reads well); every other column
    is drawn as thin grey context. `baseline` draws a reference line (100 for an indexed
    chart, 0 for returns). `annotations` is a list of {"date", "text", "series"?, "above"?}
    marking the moments the story turns on - keep to two or three.
    """
    if isinstance(data, pd.Series):
        data = data.to_frame()
    value_format = value_format or num(0)
    highlight = list(highlight) if highlight is not None else list(data.columns)
    context = [c for c in data.columns if c not in highlight]
    theme = get_theme(mode)
    s = get_preset(preset).text_scale
    labels = [f"{c}  {value_format(data[c].dropna().iloc[-1])}" for c in data.columns]
    fig, ax, theme, s = new_figure(title, subtitle, source, note, preset=preset, mode=mode,
                                   kind="line", performance=performance,
                                   right_pad=_label_width(labels, theme.sizes["label"] * s))
    if log:
        ax.set_yscale("log")
    arts = fig._vg["artists"]
    for c in context:
        ser = data[c].dropna()
        (ln,) = ax.plot(ser.index, ser.values, color=theme.context, lw=1.2, zorder=2)
        arts[c] = dict(line=ln, series=ser, role="context")
    for i, c in enumerate(highlight):
        ser = data[c].dropna()
        (ln,) = ax.plot(ser.index, ser.values, color=theme.color(i), lw=2.2, zorder=3 + i)
        (dot,) = ax.plot(ser.index[-1:], ser.values[-1:], "o", color=theme.color(i), ms=6.5,
                         mec=theme.surface, mew=1.5, zorder=10, clip_on=False)
        arts[c] = dict(line=ln, dot=dot, series=ser, role="highlight")
    if baseline is not None:
        ax.axhline(baseline, color=theme.axis, lw=1, zorder=1)
    _date_axis(ax, data.index)
    ax.yaxis.set_major_formatter(FuncFormatter(value_format))
    if log:
        ax.yaxis.set_minor_formatter(FuncFormatter(lambda v, _: ""))
    ax.margins(y=0.06)
    fig.canvas.draw()
    ys = spread_labels(ax, [arts[c]["series"].iloc[-1] for c in data.columns],
                       theme.sizes["label"] * s * 1.35 * fig.dpi / 72)
    for c, y, lab in zip(data.columns, ys, labels):
        hi = arts[c]["role"] == "highlight"
        arts[c]["label"] = ax.annotate(
            lab, (data.index[-1], y), xytext=(9 * s, 0), textcoords="offset points", va="center",
            fontsize=theme.sizes["label"] * s, fontweight="medium" if hi else "normal",
            color=theme.text_primary if hi else theme.text_muted, annotation_clip=False)
        arts[c]["format"] = value_format
    notes = []
    for a in annotations:
        name = a.get("series", highlight[0])
        ser = arts[name]["series"]
        d = ser.index[ser.index.get_indexer([pd.Timestamp(a["date"])], method="nearest")[0]]
        above = a.get("above", True)
        (mk,) = ax.plot([d], [ser[d]], "o", ms=5.5, color=theme.surface, mec=theme.text_primary,
                        mew=1.3, zorder=11)
        txt = ax.annotate(a["text"], (d, ser[d]), xytext=(0, (34 if above else -34) * s),
                          textcoords="offset points", ha=a.get("ha", "center"),
                          va="bottom" if above else "top",
                          fontsize=theme.sizes["annotation"] * s, color=theme.text_primary,
                          arrowprops=dict(arrowstyle="-", color=theme.text_muted, lw=0.8,
                                          shrinkA=2, shrinkB=5), zorder=12)
        # A halo in the background colour keeps the note legible where it crosses a line.
        txt.set_path_effects([pe.withStroke(linewidth=4 * s, foreground=theme.surface)])
        fig.canvas.draw()
        box, frame = txt.get_window_extent(), ax.get_window_extent()
        if box.y0 < frame.y0 or box.y1 > frame.y1:  # no room on that side of the line: flip it
            above = not above
            txt.set_position((0, (34 if above else -34) * s))
            txt.set_va("bottom" if above else "top")
        notes.append(dict(date=d, marker=mk, text=txt))
    fig._vg["annotations"] = notes
    return fig


def drawdown_chart(prices: pd.Series, title: str, subtitle: str | None = None, source: str | None = None,
                   *, note: str | None = None, preset: str = "slide_16x9", mode: str = "light"):
    """Underwater chart: how far below its previous peak a series sat, and for how long."""
    dd = finance.drawdown(prices.dropna())
    fig, ax, theme, s = new_figure(title, subtitle, source, note, preset=preset, mode=mode,
                                   kind="drawdown", performance=True)
    neg = theme.diverging["negative"]
    ax.fill_between(dd.index, dd.values, 0, color=neg, alpha=0.22, lw=0)
    ax.plot(dd.index, dd.values, color=neg, lw=1.6)
    ax.axhline(0, color=theme.axis, lw=1)
    _date_axis(ax, dd.index)
    ax.spines["bottom"].set_visible(False)
    ax.set_ylim(min(dd.min() * 1.22, -0.05), 0)
    ax.yaxis.set_major_formatter(FuncFormatter(pct(0)))
    trough = dd.idxmin()
    peak = prices.loc[:trough].idxmax()
    after = prices.loc[trough:]
    recovered = after[after >= prices[peak]]
    text = f"{pct(1)(dd.min())} at the low, {trough:%b %Y}"
    if len(recovered):
        months = round((recovered.index[0] - peak).days / 30.44)
        text += f"\n{months} months from peak to full recovery"
    else:
        text += "\nnot yet recovered"
    right = (trough - dd.index[0]) / (dd.index[-1] - dd.index[0]) > 0.6
    ax.plot([trough], [dd.min()], "o", ms=5.5, color=theme.surface, mec=theme.text_primary, mew=1.3, zorder=5)
    ax.annotate(text, (trough, dd.min()), xytext=((-12 if right else 12) * s, -4 * s),
                textcoords="offset points", ha="right" if right else "left", va="top",
                fontsize=theme.sizes["annotation"] * s, color=theme.text_primary, linespacing=1.4)
    return fig


def bar_chart(values: pd.Series, title: str, subtitle: str | None = None, source: str | None = None,
              *, value_format=None, sort: bool = True, highlight: Sequence[str] = (),
              signed: bool | None = None, note: str | None = None, performance: bool = False,
              preset: str = "slide_16x9", mode: str = "light"):
    """Horizontal ranked bars with the value at the end of each bar. The axis always starts
    at zero. With `signed` (default: on when any value is negative) gains and losses take
    the two diverging colours; otherwise bars are one colour and `highlight` picks out the
    ones the title is about.
    """
    values = values.dropna()
    if sort:
        values = values.sort_values()
    signed = bool((values < 0).any()) if signed is None else signed
    value_format = value_format or num(1)
    theme = get_theme(mode)
    s = get_preset(preset).text_scale
    fig, ax, theme, s = new_figure(title, subtitle, source, note, preset=preset, mode=mode,
                                   kind="bar", performance=performance, bottom_pad=0.0,
                                   left_pad=_label_width(values.index, theme.sizes["label"] * s),
                                   right_pad=_label_width([value_format(v) for v in values], theme.sizes["label"] * s))
    if signed:
        colors = [theme.diverging["positive"] if v >= 0 else theme.diverging["negative"] for v in values]
    elif highlight:
        colors = [theme.color(0) if k in highlight else theme.context for k in values.index]
    else:
        colors = [theme.color(0)] * len(values)
    ypos = np.arange(len(values))
    ax.barh(ypos, values.values, color=colors, height=0.62, zorder=3)
    ax.axvline(0, color=theme.text_secondary, lw=1, zorder=4)
    ax.set_yticks(ypos, values.index, fontsize=theme.sizes["label"] * s, color=theme.text_primary)
    ax.tick_params(axis="y", length=0, pad=6 * s)
    ax.grid(False)
    ax.set_xticks([])
    ax.spines["bottom"].set_visible(False)
    lo, hi = min(values.min(), 0), max(values.max(), 0)
    span = hi - lo or 1
    ax.set_xlim(lo - (span * 0.16 if lo < 0 else 0), hi + (span * 0.02 if hi > 0 else 0))
    for yy, v in zip(ypos, values.values):
        ax.annotate(value_format(v), (v, yy), xytext=((6 if v >= 0 else -6) * s, 0),
                    textcoords="offset points", ha="left" if v >= 0 else "right", va="center",
                    fontsize=theme.sizes["label"] * s, color=theme.text_primary, annotation_clip=False)
    if signed and lo < 0:  # category names sit left of the plot, so keep them clear of negative bars
        ax.tick_params(axis="y", pad=8 * s)
    return fig


def calendar_heatmap(table: pd.DataFrame, title: str, subtitle: str | None = None, source: str | None = None,
                     *, note: str | None = None, limit: float | None = None,
                     preset: str = "slide_16x9", mode: str = "light"):
    """Monthly returns as a year x month grid (from `finance.calendar_returns`). Colour is a
    symmetric diverging scale centred on zero and every cell is also printed as a number, so
    the chart still works in greyscale and for colour-blind readers.
    """
    months = table.drop(columns=[c for c in ["Year"] if c in table.columns])
    limit = limit or float(np.nanpercentile(np.abs(months.values), 95))
    theme = get_theme(mode)
    fig, ax, theme, s = new_figure(title, subtitle, source, note, preset=preset, mode=mode,
                                   kind="heatmap", performance=True, left_pad=0.45, bottom_pad=-0.1)
    d = theme.diverging
    cmap = LinearSegmentedColormap.from_list("vg_div", [d["negative"], d["neutral"], d["positive"]])
    ny, nm = months.shape
    f = pct(1)
    cell = theme.sizes["tick"] * s
    for i in range(ny):
        for j in range(nm):
            v = months.iat[i, j]
            if np.isnan(v):
                continue
            col = cmap(0.5 + 0.5 * np.clip(v / limit, -1, 1))
            ax.add_patch(plt.Rectangle((j + 0.04, i + 0.06), 0.92, 0.88, color=col, lw=0))
            ax.text(j + 0.5, i + 0.5, f(v), ha="center", va="center", fontsize=cell,
                    color=_ink_on(col, theme))
        if "Year" in table.columns and not np.isnan(table["Year"].iat[i]):
            ax.text(nm + 0.75, i + 0.5, pct(1, sign=True)(table["Year"].iat[i]), ha="center", va="center",
                    fontsize=cell, fontweight="medium", color=theme.text_primary)
    extra = 1.5 if "Year" in table.columns else 0
    ax.set_xlim(0, nm + extra)
    ax.set_ylim(ny, 0)
    ax.set_xticks(np.arange(nm) + 0.5, months.columns)
    if extra:
        ax.set_xticks(list(np.arange(nm) + 0.5) + [nm + 0.75], list(months.columns) + ["Year"])
    ax.set_yticks(np.arange(ny) + 0.5, table.index)
    ax.xaxis.tick_top()
    ax.tick_params(length=0, labelsize=theme.sizes["tick"] * s)
    ax.grid(False)
    for sp in ax.spines.values():
        sp.set_visible(False)
    return fig


def risk_return_scatter(stats: pd.DataFrame, title: str, subtitle: str | None = None, source: str | None = None,
                        *, x: str = "vol", y: str = "cagr", highlight: Sequence[str] = (),
                        note: str | None = None, preset: str = "slide_16x9", mode: str = "light"):
    """Annualised return against volatility, one labelled dot per asset or portfolio."""
    fig, ax, theme, s = new_figure(title, subtitle, source, note, preset=preset, mode=mode,
                                   kind="scatter", performance=True, bottom_pad=0.6, left_pad=0.8)
    highlight = list(highlight)
    for name, row in stats.iterrows():
        hi = name in highlight or not highlight
        ax.plot(row[x], row[y], "o", ms=11 if hi else 9, color=theme.color(0) if hi else theme.context,
                mec=theme.surface, mew=1.5, zorder=3 if hi else 2)
        ax.annotate(name, (row[x], row[y]), xytext=(9 * s, 0), textcoords="offset points", va="center",
                    fontsize=theme.sizes["label"] * s, fontweight="medium" if name in highlight else "normal",
                    color=theme.text_primary if hi else theme.text_secondary)
    ax.set_xlim(0, stats[x].max() * 1.3)
    ax.set_ylim(min(0, stats[y].min() * 1.2), stats[y].max() * 1.2)
    ax.grid(True, axis="both")
    ax.spines["bottom"].set_visible(True)
    ax.xaxis.set_major_formatter(FuncFormatter(pct(0)))
    ax.yaxis.set_major_formatter(FuncFormatter(pct(0)))
    ax.set_xlabel("Risk: annualised volatility  →", fontsize=theme.sizes["label"] * s, loc="left", labelpad=8 * s)
    ax.set_ylabel("Return: annualised  →", fontsize=theme.sizes["label"] * s, loc="bottom", labelpad=8 * s)
    return fig


def waterfall(steps: pd.Series, title: str, subtitle: str | None = None, source: str | None = None,
              *, total_label: str = "Total", value_format=None, note: str | None = None,
              performance: bool = False, preset: str = "slide_16x9", mode: str = "light"):
    """Contribution / attribution waterfall: each step floats from the running total and the
    final bar (drawn from zero) is the sum."""
    value_format = value_format or pct(1, sign=True)
    fig, ax, theme, s = new_figure(title, subtitle, source, note, preset=preset, mode=mode,
                                   kind="waterfall", performance=performance, bottom_pad=0.45)
    running = np.concatenate([[0], np.cumsum(steps.values)])
    names = list(steps.index) + [total_label]
    d = theme.diverging
    for i, v in enumerate(steps.values):
        ax.bar(i, v, bottom=running[i], width=0.6, color=d["positive"] if v >= 0 else d["negative"], zorder=3)
        ax.plot([i + 0.3, i + 1 - 0.3], [running[i + 1]] * 2, color=theme.axis, lw=1, zorder=2)
        top = max(running[i], running[i + 1])
        ax.annotate(value_format(v), (i, top), xytext=(0, 5 * s), textcoords="offset points", ha="center",
                    fontsize=theme.sizes["label"] * s, color=theme.text_primary)
    total = running[-1]
    ax.bar(len(steps), total, width=0.6, color=theme.text_secondary, zorder=3)
    ax.annotate(value_format(total), (len(steps), max(total, 0)), xytext=(0, 5 * s), textcoords="offset points",
                ha="center", fontsize=theme.sizes["label"] * s, fontweight="medium", color=theme.text_primary)
    ax.axhline(0, color=theme.text_secondary, lw=1, zorder=4)
    width_chars = max(8, int(110 / len(names)))
    ax.set_xticks(range(len(names)), ["\n".join(textwrap.wrap(n, width_chars)) for n in names],
                  fontsize=theme.sizes["label"] * s, color=theme.text_primary)
    ax.tick_params(axis="x", length=0)
    ax.yaxis.set_major_formatter(FuncFormatter(value_format))
    lo, hi = min(running.min(), 0), max(running.max(), 0)
    ax.set_ylim(lo - (hi - lo) * (0.08 if lo < 0 else 0), hi + (hi - lo) * 0.12)
    return fig


def allocation_bars(weights: pd.DataFrame | pd.Series, title: str, subtitle: str | None = None,
                    source: str | None = None, *, note: str | None = None, min_label: float = 0.04,
                    preset: str = "slide_16x9", mode: str = "light"):
    """Asset allocation as 100% stacked horizontal bars: one row per portfolio, one column
    per asset class. Used instead of a pie because two portfolios can be compared
    segment by segment and labels sit inside the marks.
    """
    if isinstance(weights, pd.Series):
        weights = weights.to_frame("").T
    weights = weights.div(weights.sum(axis=1), axis=0)
    theme = get_theme(mode)
    s = get_preset(preset).text_scale
    fig, ax, theme, s = new_figure(title, subtitle, source, note, preset=preset, mode=mode,
                                   kind="allocation", bottom_pad=0.0,
                                   left_pad=_label_width(weights.index, theme.sizes["label"] * s) if weights.index[0] != "" else 0.0)
    f = pct(0)
    rows = np.arange(len(weights))[::-1]
    for r, (name, w) in zip(rows, weights.iterrows()):
        left = 0.0
        for i, (asset, v) in enumerate(w.items()):
            if v <= 0:
                continue
            col = theme.color(i)
            ax.barh(r, v, left=left, height=0.5, color=col, edgecolor=theme.surface, lw=2, zorder=3)
            if v >= min_label:
                ax.text(left + v / 2, r, f(v), ha="center", va="center", fontsize=theme.sizes["label"] * s,
                        color=_ink_on(col, theme), fontweight="medium", zorder=4)
            left += v
    # Each asset class is named once, directly above the first bar it appears in, so the
    # names do the job of a legend without sending the eye away from the marks.
    named = set()
    for r, (name, w) in zip(rows, weights.iterrows()):
        left = 0.0
        for asset, v in w.items():
            if v > 0 and asset not in named:
                named.add(asset)
                ax.text(left + 0.004, r + 0.31, "\n".join(textwrap.wrap(asset, max(8, int(v * 95)))),
                        ha="left", va="bottom", fontsize=theme.sizes["tick"] * s, color=theme.text_secondary,
                        linespacing=1.15)
            left += v
    ax.set_xlim(0, 1)
    ax.set_ylim(-0.45, len(weights) - 0.05)
    ax.set_yticks(rows, weights.index, fontsize=theme.sizes["label"] * s, color=theme.text_primary)
    ax.tick_params(length=0)
    ax.set_xticks([])
    ax.grid(False)
    for sp in ax.spines.values():
        sp.set_visible(False)
    return fig


def small_multiples(data: pd.DataFrame, title: str, subtitle: str | None = None, source: str | None = None,
                    *, ncols: int = 3, value_format=None, baseline: float | None = None,
                    note: str | None = None, performance: bool = False,
                    preset: str = "slide_16x9", mode: str = "light"):
    """One small panel per series, each highlighted against all the others in grey, on a
    shared y-axis. The answer to 'too many lines on one chart'."""
    value_format = value_format or num(0)
    n = data.shape[1]
    nrows = int(np.ceil(n / ncols))
    fig, axes, theme, s = new_figure(title, subtitle, source, note, preset=preset, mode=mode,
                                     kind="small_multiples", performance=performance, nrows=nrows,
                                     ncols=ncols, sharey=True, hspace=0.45, wspace=0.08)
    axes = np.atleast_2d(axes)
    for k, ax in enumerate(axes.ravel()):
        if k >= n:
            ax.set_visible(False)
            continue
        name = data.columns[k]
        for other in data.columns:
            if other != name:
                ax.plot(data.index, data[other], color=theme.context, lw=0.8, zorder=1)
        ax.plot(data.index, data[name], color=theme.color(0), lw=2, zorder=3)
        if baseline is not None:
            ax.axhline(baseline, color=theme.axis, lw=1, zorder=0)
        last = data[name].dropna().iloc[-1]
        ax.set_title(f"{name}   {value_format(last)}", loc="left", fontsize=theme.sizes["label"] * s,
                     fontweight="medium", color=theme.text_primary, pad=6 * s)
        ax.set_xlim(data.index[0], data.index[-1])
        ax.set_xticks([data.index[0], data.index[-1]], [f"{data.index[0]:%Y}", f"{data.index[-1]:%Y}"])
        lab = ax.get_xticklabels()
        lab[0].set_ha("left")
        lab[-1].set_ha("right")
        ax.tick_params(axis="x", length=0)
        ax.yaxis.set_major_formatter(FuncFormatter(value_format))
        ax.yaxis.set_major_locator(plt.MaxNLocator(4))
    return fig
