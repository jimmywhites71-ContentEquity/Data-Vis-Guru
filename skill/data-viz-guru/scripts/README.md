# vizguru toolkit

Python package behind the Data Viz Guru skill. One look (`tokens.json`), three outputs: static, interactive, animated.

```
pip install matplotlib pandas numpy pillow        # static + GIF
pip install plotly                                # interactive HTML
# ffmpeg on the PATH                              # MP4
```

Run from this folder (`cd scripts`) or add it to `PYTHONPATH`.

## Quick start

```python
import matplotlib; matplotlib.use("Agg")
from vizguru import charts, finance, export, lint, animate

prices = ...                      # DataFrame of index levels / prices, DatetimeIndex, oldest first
idx = finance.rebase(prices)      # every series = 100 on the first common date
plot = finance.thin(idx)          # weekly points for long histories (stats use the original)

fig = charts.line_chart(
    plot,
    title=f"Fund A grew {idx['Fund A'].iloc[-1]/100:.1f}x, ahead of its benchmark",   # compute, never type
    subtitle="Growth of 100, total return, GBP, net of fees",
    source="Provider, to 31 Dec 2024",
    highlight=["Fund A", "Benchmark"], baseline=100, performance=True,
    preset="slide_16x9",
)
assert lint.report(fig)           # prints findings, returns False on any error
export.save(fig, "out/fund_a", formats=("png", "svg"), alt_text="Line chart of ...")
```

## Charts (`vizguru.charts`)

| Function | Input | Job |
|---|---|---|
| `line_chart(df, …, highlight, baseline, annotations, log)` | index levels | Growth / comparison with direct labels |
| `drawdown_chart(series, …)` | one price series | Fall from peak, depth and recovery time |
| `bar_chart(series, …, highlight, signed)` | values | Ranked bars; signed ones use gain/loss colours |
| `calendar_heatmap(table, …)` | `finance.calendar_returns` | Month × year returns with printed values |
| `risk_return_scatter(stats, …)` | `finance.summary` | Return against volatility |
| `waterfall(steps, …)` | contributions | Attribution to a total |
| `allocation_bars(df, …)` | weights | 100% stacked rows (compare portfolios) |
| `small_multiples(df, …)` | index levels | One highlighted panel per series |

Common arguments: `preset=` (see `export.presets()`), `mode="light"|"dark"`, `performance=True` (adds the past-performance line and makes the linter require it), `note=`.

Annotations: `annotations=[{"date": "2020-03-23", "text": "Covid sell-off", "series": "Fund A", "above": False}]`. Keep to two or three.

## Animation (`vizguru.animate`)

```python
fig  = charts.line_chart(..., preset="video_1080p", annotations=[...])
anim = animate.reveal(fig, seconds=8, hold=2.5)      # lines draw on; annotations appear as the line reaches them
animate.save_animation(anim, "story.mp4")             # H.264, plays everywhere
animate.save_animation(anim, "story.gif")             # 960px wide, 12 fps by default
```

The animation ends on exactly the static chart you linted. Context-series labels appear only at the end so they do not fight the callouts.

## Interactive (`vizguru.interactive`)

```python
fig = interactive.line_interactive(prices, title, subtitle, source, highlight=[...], performance=True)
interactive.write_html(fig, "chart.html", offline=True)   # offline=True embeds Plotly (~4.5 MB): works as an email attachment / behind firewalls
```

1Y / 3Y / 5Y / Max buttons re-index every line to 100 at the first visible date, so ranges compare like with like.

## Finance helpers (`vizguru.finance`)

`rebase`, `thin`, `returns`, `total_return`, `cagr`, `annualised_vol`, `drawdown`, `max_drawdown`, `rolling_return`, `rolling_vol`, `calendar_returns`, `discrete_periods`, `growth_of`, `summary`. Conventions are in `references/finance-conventions.md`.

## Linter (`vizguru.lint`)

`lint.check(fig)` / `lint.report(fig)` catch: missing source, missing past-performance line, label-style titles, text under the medium's minimum size, clipped or overlapping text, low text contrast, truncated bar axes, twin axes, pies, more than four coloured lines.

`python -m vizguru.lint --palette [tokens.json]` checks a palette: neighbouring series colours must stay distinguishable under protan/deutan vision, gain/loss poles likewise, text contrast ≥ 7/4.5/3:1.

The linter finds mechanical faults. It cannot tell whether the chart is true or fair: use `references/qa-checklist.md`, and look at the picture.

## Brand-matching

Copy `vizguru/tokens.json`, change colours, fonts and (if needed) preset sizes, then `python -m vizguru.lint --palette my.json`. Pass the path to `theme.get_theme(mode, tokens_path=...)`. Chart functions currently read the default tokens; to use a brand file everywhere, replace `tokens.json` in place.

## Sample data (`vizguru.sample_data`)

Seeded **synthetic** series for demos and tests. Not market history; every example labels it as such.
