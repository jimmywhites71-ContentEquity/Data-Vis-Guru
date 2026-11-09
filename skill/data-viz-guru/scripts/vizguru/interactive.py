"""Interactive charts as single self-contained HTML files (Plotly), themed from the same
tokens as the static charts so a client sees one visual language everywhere.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go

from .charts import PAST_PERFORMANCE
from .theme import get_theme

# When the reader zooms or picks a range, re-index every line to 100 at the first visible
# date. Without this a '3Y' button shows three years of a ten-year index, and the gaps
# between lines reflect history the reader can no longer see.
_REBASE_JS = """
(function () {
  var gd = document.getElementById('{plot_id}');
  var X = __X__.map(function (d) { return new Date(d).getTime(); });
  var RAW = __RAW__;          // trace index -> plain list of index levels
  var busy = false;
  function rebase() {
    if (busy) { return; }
    var r = gd.layout.xaxis.range;
    var start = r ? new Date(r[0]).getTime() : -Infinity;
    var k = 0;
    while (k < X.length - 1 && X[k] < start) { k++; }
    var ys = [], idx = [];
    Object.keys(RAW).forEach(function (i) {
      var base = RAW[i][k];
      ys.push(RAW[i].map(function (v) { return v / base * 100; }));
      idx.push(Number(i));
    });
    busy = true;
    Plotly.restyle(gd, {y: ys}, idx)
      .then(function () { return Plotly.relayout(gd, {'yaxis.autorange': true}); })
      .then(function () { busy = false; });
  }
  gd.on('plotly_relayout', function (e) {
    if (Object.keys(e).some(function (key) { return key.indexOf('xaxis') === 0; })) { rebase(); }
  });
})();
"""

def _template(theme) -> go.layout.Template:
    font = dict(family=f"{theme.font_family[0]}, Helvetica Neue, Arial, sans-serif",
                color=theme.text_primary, size=13)
    axis = dict(gridcolor=theme.grid, linecolor=theme.axis, zeroline=False,
                tickfont=dict(color=theme.text_secondary, size=12), title=dict(text=""))
    return go.layout.Template(layout=dict(
        font=font, paper_bgcolor=theme.surface, plot_bgcolor=theme.surface,
        colorway=list(theme.categorical),
        xaxis={**axis, "showgrid": False, "ticks": "outside", "tickcolor": theme.axis},
        yaxis={**axis, "side": "left"},
        hoverlabel=dict(bgcolor=theme.surface, bordercolor=theme.axis, font=font),
        legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="left", x=0,
                    font=dict(color=theme.text_secondary, size=12)),
        margin=dict(l=56, r=24, t=128, b=96),
    ))


def line_interactive(data: pd.DataFrame, title: str, subtitle: str | None = None,
                     source: str | None = None, *, highlight=None, indexed: bool = True,
                     performance: bool = False, note: str | None = None, mode: str = "light",
                     height: int = 620) -> go.Figure:
    """Hover-to-read line chart with 1Y / 3Y / 5Y / Max range buttons.

    With `indexed=True` the data is treated as index levels: it is rebased to 100 at the
    start, and rebased again to the first visible date whenever the reader changes the range
    (see `write_html`, which carries the script that does this).
    """
    theme = get_theme(mode)
    data = data.dropna(how="any")
    if indexed:
        data = data / data.iloc[0] * 100
    highlight = list(highlight) if highlight is not None else list(data.columns)
    fig = go.Figure()
    order = [c for c in data.columns if c not in highlight] + highlight
    for c in order:
        hi = c in highlight
        fig.add_trace(go.Scatter(
            x=data.index, y=data[c], name=c, mode="lines",
            line=dict(width=2.4 if hi else 1.3, color=theme.color(highlight.index(c)) if hi else theme.context),
            hovertemplate="%{y:,.1f}<extra>" + c + "</extra>"))
    foot = "  ·  ".join(x for x in [f"Source: {source}" if source else None, note,
                                    PAST_PERFORMANCE if performance else None] if x)
    years = (data.index[-1] - data.index[0]).days / 365.25
    buttons = [dict(count=n, label=f"{n}Y", step="year", stepmode="backward") for n in (1, 3, 5) if n < years]
    fig.update_layout(
        template=_template(theme), height=height, hovermode="x unified",
        title=dict(text=f"<b>{title}</b>" + (f"<br><span style='font-size:14px;color:{theme.text_secondary}'>{subtitle}</span>" if subtitle else ""),
                   x=0, xref="paper", xanchor="left", y=0.96, yanchor="top", font=dict(size=20)),
        annotations=[dict(text=foot, xref="paper", yref="paper", x=0, y=-0.17, xanchor="left", yanchor="top",
                          showarrow=False, align="left", font=dict(size=11, color=theme.text_muted))] if foot else [],
        xaxis=dict(rangeselector=dict(buttons=buttons + [dict(step="all", label="Max")],
                                      bgcolor=theme.surface, activecolor=theme.grid, bordercolor=theme.axis,
                                      borderwidth=1, font=dict(color=theme.text_secondary, size=12),
                                      x=1, xanchor="right", y=1.0, yanchor="bottom")),
    )
    fig._vg_data = (data, order) if indexed else None
    return fig


def _rebase_script(fig):
    stash = getattr(fig, "_vg_data", None)
    if stash is None:
        return None
    data, order = stash
    raw = {i: [round(float(v), 6) for v in data[c].values] for i, c in enumerate(order)}
    x = [d.strftime("%Y-%m-%d") for d in data.index]
    return _REBASE_JS.replace("__X__", json.dumps(x)).replace("__RAW__", json.dumps(raw))


def write_html(fig: go.Figure, path: str | Path, offline: bool = True) -> Path:
    """Write one HTML file that opens anywhere. `offline=True` embeds Plotly (about 4.5 MB)
    so the chart works behind a client firewall and as an email attachment; `offline=False`
    loads it from the CDN for a file of a few hundred KB.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(path, include_plotlyjs=True if offline else "cdn", full_html=True,
                   config=dict(displaylogo=False, responsive=True,
                               modeBarButtonsToRemove=["lasso2d", "select2d", "autoScale2d"]),
                   post_script=_rebase_script(fig))
    return path
