"""Investment maths that sits underneath the charts.

Kept deliberately small and explicit: every number that ends up on a client chart should be
traceable to one of these functions, and each one states its convention in the docstring.
All functions take a DataFrame/Series of *prices or index levels* with a DatetimeIndex unless
stated otherwise.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

TRADING_DAYS = 252
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def _check(prices: pd.DataFrame | pd.Series) -> None:
    if not isinstance(prices.index, pd.DatetimeIndex):
        raise TypeError("prices must have a DatetimeIndex")
    if not prices.index.is_monotonic_increasing:
        raise ValueError("prices must be sorted oldest to newest")


def rebase(prices, base: float = 100.0, start=None):
    """Index every series to `base` at a common start date.

    The start is the first date on which *all* series have data, so no series gets a head
    start. Pass `start` to choose a later common date (for example a fund's launch).
    """
    _check(prices)
    p = prices.dropna() if isinstance(prices, pd.Series) else prices.dropna(how="any")
    if start is not None:
        p = p.loc[pd.Timestamp(start):]
    if p.empty:
        raise ValueError("No date on which every series has data")
    return p / p.iloc[0] * base


def thin(prices, rule: str = "W-FRI"):
    """Down-sample for plotting (weekly by default) while keeping the exact first and last
    observations, so the chart starts at the stated base and ends on the as-of date. Use for
    long daily histories: ten years of daily points is noise at chart size. Compute
    statistics on the original data, not on the thinned series.
    """
    _check(prices)
    sampled = prices.resample(rule).last().dropna(how="all")
    sampled = sampled[(sampled.index > prices.index[0]) & (sampled.index < prices.index[-1])]
    return pd.concat([prices.iloc[:1], sampled, prices.iloc[-1:]])


def returns(prices, periods: int = 1):
    """Simple (arithmetic) returns over `periods` rows."""
    _check(prices)
    return prices.pct_change(periods).dropna(how="all")


def total_return(prices) -> pd.Series | float:
    """Cumulative simple return, first valid point to last."""
    _check(prices)
    return prices.iloc[-1] / prices.iloc[0] - 1


def cagr(prices):
    """Annualised compound growth rate using actual calendar days / 365.25."""
    _check(prices)
    years = (prices.index[-1] - prices.index[0]).days / 365.25
    if years <= 0:
        raise ValueError("Need more than one date to annualise")
    return (prices.iloc[-1] / prices.iloc[0]) ** (1 / years) - 1


def annualised_vol(prices, periods_per_year: int = TRADING_DAYS):
    """Sample standard deviation of periodic simple returns, scaled by sqrt(time)."""
    return returns(prices).std(ddof=1) * np.sqrt(periods_per_year)


def drawdown(prices):
    """Decline from the running peak, as a negative fraction (0 at a new high)."""
    _check(prices)
    return prices / prices.cummax() - 1


def max_drawdown(prices):
    return drawdown(prices).min()


def rolling_return(prices, window: int = TRADING_DAYS, annualise: bool = False):
    """Return over a rolling window of `window` rows."""
    _check(prices)
    r = prices / prices.shift(window) - 1
    if annualise:
        r = (1 + r) ** (TRADING_DAYS / window) - 1
    return r.dropna(how="all")


def rolling_vol(prices, window: int = 63, periods_per_year: int = TRADING_DAYS):
    return (returns(prices).rolling(window).std(ddof=1) * np.sqrt(periods_per_year)).dropna(how="all")


def calendar_returns(prices: pd.Series) -> pd.DataFrame:
    """Year x month table of monthly returns plus a 'Year' column.

    Months are calendar months using the last available price in each. The first month in
    the data has no prior month-end, so it is measured from the first price and is partial.
    """
    _check(prices)
    if not isinstance(prices, pd.Series):
        raise TypeError("calendar_returns takes a single series")
    month_end = prices.resample("ME").last()
    monthly = month_end.pct_change()
    monthly.iloc[0] = month_end.iloc[0] / prices.iloc[0] - 1
    table = monthly.groupby([monthly.index.year, monthly.index.month]).first().unstack()
    table = table.reindex(columns=range(1, 13))
    table.columns = MONTHS
    year_end = prices.resample("YE").last()
    yearly = year_end.pct_change()
    yearly.iloc[0] = year_end.iloc[0] / prices.iloc[0] - 1
    table["Year"] = yearly.values
    table.index.name = None
    return table


def discrete_periods(prices, n: int = 5, months: int = 12) -> pd.DataFrame:
    """Returns for the `n` most recent complete `months`-long periods ending on the last
    date in the data, newest first. This is the 'discrete annual performance' table that
    usually accompanies a cumulative chart in client material.
    """
    _check(prices)
    p = prices.to_frame() if isinstance(prices, pd.Series) else prices
    end = p.index[-1]
    rows = {}
    for i in range(n):
        hi = end - pd.DateOffset(months=months * i)
        lo = end - pd.DateOffset(months=months * (i + 1))
        if lo < p.index[0]:
            break
        a = p.loc[:lo].iloc[-1]
        b = p.loc[:hi].iloc[-1]
        rows[f"{lo:%b %Y} to {hi:%b %Y}"] = b / a - 1
    return pd.DataFrame(rows).T


def growth_of(prices, amount: float = 10_000.0):
    """What `amount` invested on the first common date would be worth over time."""
    return rebase(prices, base=amount)


def summary(prices: pd.DataFrame) -> pd.DataFrame:
    """One row per series: the figures a risk/return scatter or a summary table needs."""
    _check(prices)
    p = prices.dropna(how="any")
    out = pd.DataFrame({
        "total_return": total_return(p),
        "cagr": cagr(p),
        "vol": annualised_vol(p),
        "max_drawdown": max_drawdown(p),
    })
    out["return_per_unit_risk"] = out["cagr"] / out["vol"]
    return out
