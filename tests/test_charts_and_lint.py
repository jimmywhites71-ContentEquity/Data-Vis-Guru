import json

import matplotlib.pyplot as plt
import pandas as pd
import pytest

from vizguru import charts, export, finance, lint, sample_data
from vizguru.theme import TOKENS_PATH, get_theme, load_tokens, preset

P = sample_data.prices("2018-01-01", "2024-12-31")
IDX = finance.thin(finance.rebase(P))
SRC = "Synthetic data for tests"


def codes(fig):
    return {f.code for f in lint.check(fig) if f.level == "error"}


def good_line(**kw):
    return charts.line_chart(IDX, "Equities outgrew bonds over the seven years", "Index, 100 = Jan 2018, GBP total return",
                             SRC, highlight=["Global equities", "Government bonds"], performance=True, **kw)


def test_good_chart_lints_clean():
    fig = good_line()
    assert codes(fig) == set()
    plt.close(fig)


@pytest.mark.parametrize("preset_name", ["slide_16x9", "slide_half", "report_full_width", "social_square",
                                         "social_portrait", "video_1080p", "video_vertical"])
def test_every_preset_exports_at_exact_size_and_lints_clean(preset_name, tmp_path):
    from PIL import Image
    fig = good_line(preset=preset_name)
    assert codes(fig) == set(), lint.check(fig)
    out = export.save(fig, tmp_path / "c", formats=("png",))
    assert Image.open(out[0]).size == preset(preset_name).px
    plt.close(fig)


def test_missing_source_and_disclosure_are_errors():
    fig = charts.line_chart(IDX, "Equities outgrew bonds over the seven years", "x", source=None)
    assert "source-missing" in codes(fig)
    fig2 = charts.line_chart(IDX, "Equities outgrew bonds over the seven years", "x", SRC, performance=True)
    assert "disclosure-missing" not in codes(fig2)
    fig3 = charts.line_chart(IDX, "Equities outgrew bonds over the seven years", "x", SRC, performance=True)
    fig3._vg["footer"] = "Source only"
    assert "disclosure-missing" in codes(fig3)
    plt.close("all")


def test_label_style_title_warns():
    fig = charts.line_chart(IDX, "Performance", "x", SRC)
    assert any(f.code == "title-label" for f in lint.check(fig))
    plt.close(fig)


def test_text_below_medium_minimum_is_an_error():
    fig = good_line()
    fig.axes[0].set_xlabel("tiny", fontsize=6)
    assert "text-small" in codes(fig)
    plt.close(fig)


def test_clipped_text_is_an_error():
    fig = good_line()
    fig.text(0.97, 0.5, "this label is far too long to fit inside", fontsize=12)
    assert "text-clipped" in codes(fig)
    plt.close(fig)


def test_truncated_bar_axis_is_an_error():
    fig = charts.bar_chart(pd.Series({"a": 90.0, "b": 95.0, "c": 99.0}), "Fund C led its peers on fees", "x", SRC)
    assert "bar-baseline" not in codes(fig)
    fig.axes[0].set_xlim(80, 100)
    assert "bar-baseline" in codes(fig)
    plt.close(fig)


def test_twin_axis_is_flagged():
    fig = good_line()
    fig.axes[0].twinx()
    assert "dual-axis" in codes(fig)
    plt.close(fig)


def test_palette_check_passes_default_and_catches_bad_palettes(tmp_path):
    assert [f for f in lint.check_palette() if f.level == "error"] == []
    bad = load_tokens()
    bad["modes"]["light"]["categorical"][1] = bad["modes"]["light"]["categorical"][0]
    bad["modes"]["light"]["diverging"] = {"negative": "#cc3333", "neutral": "#f0efec", "positive": "#2e8b2e"}
    p = tmp_path / "bad.json"
    p.write_text(json.dumps(bad))
    found = {f.code for f in lint.check_palette(p)}
    assert "palette-similar" in found and "palette-diverging" in found


def test_ninth_series_colour_is_refused():
    with pytest.raises(ValueError):
        get_theme("light").color(8)


@pytest.mark.parametrize("make", [
    lambda: charts.drawdown_chart(P["Global equities"], "Equities fell 25% from peak to trough at the worst point", "x", SRC),
    lambda: charts.calendar_heatmap(finance.calendar_returns(P["Gold"]), "Gold rose in more months than it fell", "x", SRC),
    lambda: charts.bar_chart(P.iloc[-1] / 100 - 1, "Gold led the seven years by a wide margin", "x", SRC, value_format=charts.pct(0, True)),
    lambda: charts.risk_return_scatter(finance.summary(P), "Bonds paid the least for the least risk taken", "x", SRC),
    lambda: charts.waterfall(pd.Series({"Equities": .05, "Bonds": .01, "Fees": -.004}), "Fees took back a tenth of the gross return", "x", SRC),
    lambda: charts.allocation_bars(pd.DataFrame({"Equities": [.6, .4], "Bonds": [.4, .6]}, index=["Now", "Proposed"]), "The proposal moves 20 points from equities to bonds", "x", SRC),
    lambda: charts.small_multiples(IDX, "Five asset classes took five different paths", "x", SRC),
])
def test_each_chart_type_builds_and_lints_clean(make):
    fig = make()
    assert codes(fig) == set(), lint.check(fig)
    plt.close(fig)


def test_tokens_have_both_modes_and_eight_slots():
    t = load_tokens(TOKENS_PATH)
    for m in ("light", "dark"):
        assert len(t["modes"][m]["categorical"]) == 8
