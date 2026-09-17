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


@pytest.fixture
def market() -> pd.Series:
    """A benchmark series on the same dates as `wobble`, correlated but not identical."""
    n = 400
    rng = np.random.default_rng(31415)
    steps = rng.normal(loc=0.03, scale=1.0, size=n)
    return pd.Series(1000.0 + np.cumsum(steps), index=_business_days(n), name="close")


@pytest.fixture
def geared(market: pd.Series) -> pd.DataFrame:
    """A price frame that is exactly twice the benchmark's move, with no noise.

    Beta against it is 2 by construction and correlation is 1, so a test can
    state the answer instead of recomputing the implementation.
    """
    returns = market.pct_change().fillna(0.0)
    close = 100.0 * (1.0 + 2.0 * returns).cumprod()
    return pd.DataFrame(
        {
            "open": close,
            "high": close * 1.01,
            "low": close * 0.99,
            "close": close,
            "volume": pd.Series(1_000_000.0, index=close.index),
        }
    )


def _annual_row(year: int, scale: float) -> dict[str, float | str]:
    """One year of a synthetic company, every line a round multiple of `scale`.

    Round numbers on purpose. A ratio whose expected value has to be computed
    by running the implementation is not a test of the implementation.
    """
    revenue = 1000.0 * scale
    return {
        "period": "annual",
        "revenue": revenue,
        "cost_of_revenue": 600.0 * scale,
        "gross_profit": 400.0 * scale,
        "research_and_development": 50.0 * scale,
        "ebit": 200.0 * scale,
        "ebitda": 250.0 * scale,
        "depreciation_amortisation": 50.0 * scale,
        "interest_expense": 20.0 * scale,
        "pretax_income": 180.0 * scale,
        "tax_expense": 45.0 * scale,
        "net_income": 135.0 * scale,
        "eps_diluted": 1.35 * scale,
        "operating_cash_flow": 210.0 * scale,
        "capital_expenditure": 60.0 * scale,
        "dividends_paid": 40.0 * scale,
        "dividend_per_share_paid": 0.40 * scale,
        "dividend_per_share_declared": 0.44 * scale,
        "total_assets": 2000.0 * scale,
        "current_assets": 800.0 * scale,
        "inventory": 300.0 * scale,
        "cash_and_equivalents": 200.0 * scale,
        "total_liabilities": 1200.0 * scale,
        "current_liabilities": 500.0 * scale,
        "total_debt": 600.0 * scale,
        "long_term_debt": 400.0 * scale,
        "total_equity": 800.0 * scale,
        "shares_outstanding": 100.0,
    }


@pytest.fixture
def accounts() -> pd.DataFrame:
    """Nine annual years compounding at exactly 10 percent, plus quarters and TTM rows.

    Every line grows by the same factor each year, so every margin is constant
    and every growth rate is 10 percent. A test that expects 10 and gets 10.3
    has found something.
    """
    rows: list[dict[str, float | str]] = []
    index: list[pd.Timestamp] = []
    for offset in range(9):
        year = 2016 + offset
        rows.append(_annual_row(year, 1.1**offset))
        index.append(pd.Timestamp(f"{year}-12-31"))

    for offset in range(12):
        year = 2022 + offset // 4
        quarter_end = pd.Timestamp(f"{year}-{3 * (offset % 4) + 3:02d}-28")
        scale = 1.1 ** (6 + offset / 4.0) / 4.0
        quarterly = _annual_row(year, scale)
        quarterly["period"] = "quarterly"
        rows.append(quarterly)
        index.append(quarter_end)

        trailing = _annual_row(year, 1.1 ** (6 + offset / 4.0))
        trailing["period"] = "ttm"
        rows.append(trailing)
        index.append(quarter_end)

    frame = pd.DataFrame(rows, index=pd.DatetimeIndex(index, name="period_end"))
    return frame.sort_index(kind="stable")


@pytest.fixture
def market_value() -> pd.Series:
    """A market capitalisation series worth exactly 20 times the 2016 net income.

    Flat, so an as-of join cannot be confused with an interpolation, and every
    multiple has an arithmetic answer.
    """
    dates = pd.date_range("2015-01-01", "2025-12-31", freq="D", name="date")
    return pd.Series(2700.0, index=dates, name="market_cap")
