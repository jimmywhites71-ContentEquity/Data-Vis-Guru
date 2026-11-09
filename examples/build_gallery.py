"""Build every example in the gallery from synthetic data.

    python examples/build_gallery.py            # everything
    python examples/build_gallery.py --quick    # static charts only (no GIF/MP4/HTML)

Outputs go to examples/gallery/. Every chart is linted; the script exits non-zero if any
chart has an error, which is what CI relies on.
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skill" / "data-viz-guru" / "scripts"))
from vizguru import animate, charts, export, finance, lint, sample_data  # noqa: E402

OUT = Path(__file__).parent / "gallery"
SRC = "Synthetic data generated for illustration; not real market history. Index levels, total return, GBP, 1 Jan 2014 to 31 Dec 2024."
SRC_SHORT = "Synthetic data for illustration; not real market history."


def build(quick: bool = False) -> bool:
    p = sample_data.prices()
    p["60/40 portfolio"] = sample_data.portfolio(p, {"Global equities": 0.6, "Government bonds": 0.4})
    idx = finance.rebase(p)
    stats = finance.summary(p)
    ok = True

    def done(fig, name, alt, formats=("png", "svg")):
        nonlocal ok
        print(f"-- {name}")
        ok &= lint.report(fig)
        export.save(fig, OUT / name, formats=formats, alt_text=alt)
        plt.close(fig)

    weekly = finance.thin(idx)  # ten years of daily points is noise at chart size
    eq, pf = idx["Global equities"].iloc[-1], idx["60/40 portfolio"].iloc[-1]
    dd_eq, dd_pf = finance.max_drawdown(p["Global equities"]), finance.max_drawdown(p["60/40 portfolio"])
    trough = finance.drawdown(p["Global equities"]).idxmin()
    peak = p["Global equities"].loc[:trough].idxmax()
    weeks = round((trough - peak).days / 7)
    # Every claim in a title is computed from the data and asserted, so a data refresh can
    # never leave a headline that is no longer true.
    assert eq > 200 and pf < eq and dd_pf > dd_eq
    beats = [dict(date=trough, series="Global equities", above=False,
                  text=f"Equities fell {charts.pct(0)(abs(dd_eq))}\nin {weeks} weeks")]
    story = dict(
        title=f"Equities grew {eq / 100:.1f}x in eleven years; the 60/40 portfolio grew {pf / 100:.1f}x and its worst fall was "
              f"{charts.pct(0)(abs(dd_pf))}, not {charts.pct(0)(abs(dd_eq))}",
        subtitle="Growth of 100 invested on 1 Jan 2014, total return in GBP",
        source=SRC, highlight=["Global equities", "60/40 portfolio"], baseline=100, performance=True,
        annotations=beats)
    short_title = f"A 60/40 portfolio kept {(pf - 100) / (eq - 100):.0%} of the growth of equities with {dd_pf / dd_eq:.0%} of the worst fall"
    done(charts.line_chart(weekly, **story), "01_indexed_performance",
         f"Line chart of five asset classes and a 60/40 portfolio indexed to 100 in January 2014. Global equities end at {eq:.0f} "
         f"and the 60/40 portfolio at {pf:.0f}; equities fall sharply in 2020 and the portfolio falls less.")
    done(charts.line_chart(weekly, **{**story, "title": short_title},
                           preset="social_square", mode="dark"), "02_indexed_performance_social_dark",
         "Square dark-mode version of the indexed performance chart for social media.", formats=("png",))

    dd = finance.max_drawdown(p["Global equities"])
    done(charts.drawdown_chart(p["Global equities"],
                               f"The worst fall took equity investors {charts.pct(0)(abs(dd))} below their previous high",
                               "Global equities, decline from previous peak, total return in GBP", SRC),
         "03_drawdown", f"Area chart of the decline of global equities from their running peak; the deepest point is {dd:.1%}.")

    cal = finance.calendar_returns(p["60/40 portfolio"])
    up = (cal.drop(columns="Year") > 0).sum().sum()
    total = cal.drop(columns="Year").notna().sum().sum()
    done(charts.calendar_heatmap(cal, f"The 60/40 portfolio rose in {up} of {total} months",
                                 "Monthly total return, GBP. Blue is a gain, red a loss; the final column is the calendar year",
                                 SRC),
         "04_calendar_heatmap", f"Grid of monthly returns by year and month for the 60/40 portfolio; {up} of {total} months are positive.")

    r = stats["cagr"].drop("60/40 portfolio")
    done(charts.bar_chart(r, f"{r.idxmax()} led the decade at {charts.pct(1)(r.max())} a year",
                          "Annualised total return, GBP, 1 Jan 2014 to 31 Dec 2024", SRC,
                          value_format=charts.pct(1), highlight=[r.idxmax()], performance=True),
         "05_ranked_bars", "Horizontal bar chart ranking five asset classes by annualised return.")

    yr = finance.discrete_periods(p.drop(columns="60/40 portfolio"), n=1).iloc[0]
    done(charts.bar_chart(yr, "The last twelve months split the asset classes into winners and losers",
                          f"Total return, GBP, {finance.discrete_periods(p, n=1).index[0]}", SRC,
                          value_format=charts.pct(1, sign=True), performance=True, preset="slide_half"),
         "06_signed_bars", "Horizontal bar chart of twelve-month returns by asset class, gains in blue and losses in red.")

    done(charts.risk_return_scatter(stats, f"The 60/40 portfolio earned {stats.loc['60/40 portfolio', 'return_per_unit_risk']:.2f} of return per unit of risk; "
                                    f"equities alone earned {stats.loc['Global equities', 'return_per_unit_risk']:.2f}",
                                    "Annualised return against annualised volatility, GBP, 2014 to 2024", SRC,
                                    highlight=["60/40 portfolio"]),
         "07_risk_return", "Scatter plot of annualised return against volatility for five asset classes and a 60/40 portfolio.")

    contrib = pd.Series({"Global equities": 0.6, "Government bonds": 0.4}) * stats["cagr"]
    contrib = contrib.dropna()
    contrib["Rebalancing and compounding"] = stats.loc["60/40 portfolio", "cagr"] - contrib.sum()
    done(charts.waterfall(contrib, f"Equities supplied {contrib['Global equities'] / stats.loc['60/40 portfolio', 'cagr']:.0%} of the portfolio's annual return",
                          "Contribution to the 60/40 portfolio's annualised return, percentage points, GBP, 2014 to 2024", SRC,
                          total_label="60/40 portfolio", performance=True),
         "08_contribution_waterfall", "Waterfall chart of contributions to the portfolio's annualised return by asset class.")

    w = pd.DataFrame({"Global equities": [0.60, 0.45], "UK equities": [0.0, 0.10], "Government bonds": [0.40, 0.30],
                      "Property": [0.0, 0.08], "Gold": [0.0, 0.07]}, index=["Current", "Proposed"])
    done(charts.allocation_bars(w, "The proposal moves a quarter of the portfolio into three new diversifiers",
                                "Asset allocation, % of portfolio", "Illustrative allocations.", preset="slide_16x9"),
         "09_allocation", "Two stacked bars comparing current and proposed asset allocation.")

    done(charts.small_multiples(idx.drop(columns="60/40 portfolio"), "Five asset classes, five different decades",
                                "Growth of 100 invested on 1 Jan 2014, total return in GBP. Each panel highlights one asset class against the rest",
                                SRC, baseline=100, performance=True),
         "10_small_multiples", "Five small line charts, one per asset class, each indexed to 100 in January 2014.")

    if quick:
        return ok

    video = charts.line_chart(weekly[["Global equities", "Government bonds", "60/40 portfolio"]],
                              **{**story, "title": short_title, "source": SRC_SHORT}, preset="video_1080p")
    ok &= lint.report(video)
    anim = animate.reveal(video, seconds=7, hold=2.5)
    animate.save_animation(anim, OUT / "11_story.mp4")
    animate.save_animation(anim, OUT / "11_story.gif")
    plt.close(video)

    from vizguru import interactive
    fig = interactive.line_interactive(p, "Pick a period: every line restarts at 100 from the first date shown",
                                       "Growth of 100, total return in GBP", SRC_SHORT,
                                       highlight=["Global equities", "60/40 portfolio"], performance=True)
    interactive.write_html(fig, OUT / "12_interactive.html", offline=False)
    return ok


if __name__ == "__main__":
    sys.exit(0 if build("--quick" in sys.argv) else 1)
