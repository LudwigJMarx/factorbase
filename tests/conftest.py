"""Fixtures shared by the factor tests.

The price series here is generated, not sampled from a real instrument. A real
series would make the expected values unverifiable by a reader: nobody can tell
whether 63.41 is the right RSI for a particular Tuesday in 2019. A generated
series with a stated rule can be recomputed by hand, and the formula in the
catalogue is what recomputes it.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest


def _business_days(count: int) -> pd.DatetimeIndex:
    return pd.bdate_range("2020-01-01", periods=count, name="date")


@pytest.fixture
def ramp() -> pd.DataFrame:
    """Close rising by exactly 1 per bar, from 100. Range is 2 wide, no gaps.

    Every rolling mean over this series is computable in the head, which is the
    point: a test whose expected value needs the implementation to produce it
    tests nothing.
    """
    n = 300
    close = pd.Series(np.arange(100.0, 100.0 + n), index=_business_days(n), name="close")
    return pd.DataFrame(
        {
            "open": close - 0.5,
            "high": close + 1.0,
            "low": close - 1.0,
            "close": close,
            "volume": pd.Series(1_000_000.0, index=close.index),
        }
    )


@pytest.fixture
def wobble() -> pd.DataFrame:
    """A deterministic series that actually goes up and down.

    Seeded random walk. Used where a monotone ramp would hide a sign error,
    for instance in anything that separates gains from losses.

    The close is deliberately not the midpoint of its bar. An earlier version
    of this fixture put the high and the low the same distance either side of
    the close, which made the close location value identically zero and the
    accumulation line a flat line at 1e-7. Every test built on where the close
    sits inside its bar passed against a constant. The bar is now built around
    the open and the close, with the wicks added outside them at unequal
    lengths.
    """
    n = 400
    rng = np.random.default_rng(20260917)
    steps = rng.normal(loc=0.05, scale=1.5, size=n)
    close = pd.Series(100.0 + np.cumsum(steps), index=_business_days(n), name="close")
    open_ = close.shift(1).fillna(close.iloc[0])
    body_high = pd.concat([open_, close], axis=1).max(axis=1)
    body_low = pd.concat([open_, close], axis=1).min(axis=1)
    upper_wick = pd.Series(rng.uniform(0.05, 1.8, size=n), index=close.index)
    lower_wick = pd.Series(rng.uniform(0.05, 1.8, size=n), index=close.index)
    return pd.DataFrame(
        {
            "open": open_,
            "high": body_high + upper_wick,
            "low": body_low - lower_wick,
            "close": close,
            "volume": pd.Series(rng.uniform(5e5, 5e6, size=n), index=close.index),
        }
    )
