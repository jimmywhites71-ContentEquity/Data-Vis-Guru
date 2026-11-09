import numpy as np
import pandas as pd
import pytest

from vizguru import finance, sample_data


def series(values, start="2020-01-01"):
    return pd.Series(values, index=pd.bdate_range(start, periods=len(values)), dtype=float)


def test_rebase_starts_at_base_and_uses_common_start():
    idx = pd.bdate_range("2020-01-01", periods=5)
    df = pd.DataFrame({"a": [10, 11, 12, 13, 14], "b": [np.nan, 20, 22, 24, 26]}, index=idx)
    out = finance.rebase(df)
    assert out.index[0] == idx[1]          # first date where every series has data
    assert (out.iloc[0] == 100).all()
    assert out["b"].iloc[-1] == pytest.approx(130)


def test_total_return_and_cagr():
    idx = pd.to_datetime(["2020-01-01", "2022-01-01"])  # 731 days
    p = pd.Series([100.0, 121.0], index=idx)
    assert finance.total_return(p) == pytest.approx(0.21)
    assert finance.cagr(p) == pytest.approx(1.21 ** (365.25 / 731) - 1)


def test_drawdown_known_path():
    p = series([100, 120, 90, 120, 130])
    dd = finance.drawdown(p)
    assert dd.iloc[1] == 0
    assert dd.iloc[2] == pytest.approx(-0.25)
    assert finance.max_drawdown(p) == pytest.approx(-0.25)
    assert dd.iloc[-1] == 0


def test_annualised_vol_zero_for_constant_growth():
    p = series(100 * 1.001 ** np.arange(300))
    assert finance.annualised_vol(p) == pytest.approx(0, abs=1e-12)


def test_unsorted_or_non_datetime_input_is_rejected():
    with pytest.raises(TypeError):
        finance.total_return(pd.Series([1.0, 2.0]))
    with pytest.raises(ValueError):
        finance.total_return(series([1, 2, 3]).iloc[::-1])


def test_calendar_returns_table_shape_and_year_column():
    p = sample_data.prices("2020-01-01", "2022-12-31")["Global equities"]
    t = finance.calendar_returns(p)
    assert list(t.columns[:3]) == ["Jan", "Feb", "Mar"] and t.columns[-1] == "Year"
    assert list(t.index) == [2020, 2021, 2022]
    # the year column is the compounded months (first month is measured from first price)
    for year in t.index:
        months = t.loc[year].drop("Year").dropna()
        assert (1 + months).prod() - 1 == pytest.approx(t.loc[year, "Year"], abs=1e-9)


def test_discrete_periods_newest_first_and_complete_only():
    p = sample_data.prices("2018-01-01", "2024-12-31")
    d = finance.discrete_periods(p, n=5)
    assert len(d) == 5
    assert d.index[0].endswith("Dec 2024")


def test_thin_keeps_first_and_last():
    p = sample_data.prices("2020-01-01", "2020-12-31")
    t = finance.thin(p)
    assert t.index[0] == p.index[0] and t.index[-1] == p.index[-1]
    assert len(t) < len(p) / 3
    assert t.iloc[-1].equals(p.iloc[-1])


def test_sample_data_is_deterministic_and_labelled_synthetic():
    a, b = sample_data.prices(), sample_data.prices()
    pd.testing.assert_frame_equal(a, b)
    assert "NOT real" in sample_data.__doc__
