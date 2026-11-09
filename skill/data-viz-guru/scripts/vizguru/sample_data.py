"""Synthetic market data for examples and tests.

These series are generated from a seeded random process. They are NOT real market history
and must never be presented to a client as such: every example chart built from them carries
a 'Synthetic data' source line.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

ASSETS = {
    # name: (annual drift, annual vol, loading on the shared equity shock)
    "Global equities": (0.085, 0.15, 1.00),
    "UK equities": (0.060, 0.14, 0.85),
    "Government bonds": (0.025, 0.06, -0.15),
    "Gold": (0.050, 0.14, 0.05),
    "Property": (0.050, 0.12, 0.60),
}


def prices(start: str = "2014-01-01", end: str = "2024-12-31", seed: int = 34) -> pd.DataFrame:
    """Daily index levels for five illustrative asset classes, with one sharp sell-off."""
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range(start, end)
    n = len(idx)
    dt = 1 / 252
    market = rng.standard_normal(n)
    # A stylised crash and rebound roughly six years in, so drawdown charts have a story.
    crash = int(n * 0.56)
    shock = np.zeros(n)
    shock[crash:crash + 23] = -0.0105
    shock[crash + 23:crash + 110] = 0.0024
    out = {}
    for name, (mu, vol, beta) in ASSETS.items():
        own = rng.standard_normal(n)
        z = beta * market + np.sqrt(max(1 - beta**2, 0.05)) * own
        z = (z - z.mean()) / z.std()  # realised drift and vol match the table above
        r = (mu - 0.5 * vol**2) * dt + vol * np.sqrt(dt) * z + beta * shock
        out[name] = 100 * np.exp(np.cumsum(r))
    df = pd.DataFrame(out, index=idx)
    return df / df.iloc[0] * 100


def portfolio(p: pd.DataFrame, weights: dict[str, float], name: str = "Portfolio") -> pd.Series:
    """Daily-rebalanced blend of the given series (weights must sum to 1)."""
    if abs(sum(weights.values()) - 1) > 1e-9:
        raise ValueError("weights must sum to 1")
    r = p[list(weights)].pct_change().fillna(0)
    blended = (r * pd.Series(weights)).sum(axis=1)
    return (100 * (1 + blended).cumprod()).rename(name)
