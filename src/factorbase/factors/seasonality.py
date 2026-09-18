"""How the instrument behaved at this point of the calendar, in previous years.

── THE ONE ENTRY, AND WHY ──────────────────────────────────────────────────

A screener typically offers this as half a dozen separate criteria: by calendar
window, by weekday, by quarter, each with and without a trend adjustment. They
are one measurement with two switches. Splitting them would give six places to
fix one formula, which is the arrangement this catalogue exists to avoid.

── WHAT IT IS NOT ──────────────────────────────────────────────────────────

Not a forecast, and not evidence of one. With five years of history a weekday
bucket holds about 260 observations and a quarter bucket about 315, but a
calendar window of five days holds roughly 55, and a mean of 55 daily returns
has a standard error around a fifth of a percent. Most readings this factor
produces are indistinguishable from zero, and it reports the mean rather than a
significance because deciding what counts as significant is the caller's job.

Nothing here corrects for the fact that a screen ranking a universe on it is
testing thousands of hypotheses at once.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ..errors import UnsupportedIndexError
from ._common import require_columns

BUCKETS = ("calendar_window", "month", "day_of_week", "quarter")


def _bucket_keys(index: pd.DatetimeIndex, bucket: str) -> np.ndarray:
    if bucket == "day_of_week":
        return index.dayofweek.to_numpy()
    if bucket == "month":
        return index.month.to_numpy()
    if bucket == "quarter":
        return index.quarter.to_numpy()
    if bucket == "calendar_window":
        return index.dayofyear.to_numpy()
    raise ValueError(f"unknown bucket {bucket!r}; expected one of {BUCKETS}")


def _same_bucket(keys: np.ndarray, key: int, bucket: str, window_days: int) -> np.ndarray:
    if bucket != "calendar_window":
        return keys == key
    # Circular distance in days of the year, so late December sits next to
    # early January rather than 365 days away from it.
    gap = np.abs(keys - key)
    return np.minimum(gap, 366 - gap) <= window_days


def seasonal_strength(
    prices: pd.DataFrame,
    bucket: str = "calendar_window",
    years: int = 5,
    window_days: int = 5,
    detrend: bool = True,
) -> pd.Series:
    """Mean past return at this point of the calendar, in percent.

    Catalogue id `seasonal_strength`.

    For each bar, the daily returns of every earlier bar within the lookback
    that falls in the same bucket are averaged. Only earlier bars: including the
    current one would let today's return feed its own seasonal reading.

    `detrend` subtracts the mean daily return over the same lookback, so the
    figure is the excess over the instrument's own drift. Without it, anything
    that rose over the period reads positive in every bucket, and the factor
    ranks on drift while appearing to rank on seasonality.
    """
    require_columns(prices, ("close",), "seasonal_strength")
    if bucket not in BUCKETS:
        raise ValueError(f"unknown bucket {bucket!r}; expected one of {BUCKETS}")
    if not isinstance(prices.index, pd.DatetimeIndex):
        raise UnsupportedIndexError(
            "seasonal_strength", "DatetimeIndex", type(prices.index).__name__
        )

    returns = (prices["close"].pct_change() * 100.0).to_numpy()
    dates = prices.index.to_numpy()
    keys = _bucket_keys(prices.index, bucket)
    horizon = np.timedelta64(int(round(years * 365.25)), "D")

    out = np.full(len(prices), np.nan)
    for position in range(len(prices)):
        window = (dates >= dates[position] - horizon) & (dates < dates[position])
        if not window.any():
            continue
        matching = window & _same_bucket(keys, int(keys[position]), bucket, window_days)
        chosen = returns[matching]
        chosen = chosen[~np.isnan(chosen)]
        if chosen.size == 0:
            continue
        value = float(chosen.mean())
        if detrend:
            everything = returns[window]
            everything = everything[~np.isnan(everything)]
            if everything.size == 0:
                continue
            value -= float(everything.mean())
        out[position] = value

    return pd.Series(out, index=prices.index, name="seasonal_strength")


def seasonal_hit_rate(
    prices: pd.DataFrame,
    bucket: str = "calendar_window",
    years: int = 5,
    window_days: int = 5,
) -> pd.Series:
    """Share of past bars in this bucket that closed up, in percent.

    Catalogue id `seasonal_hit_rate`.

    The companion to the mean, and it answers a different question. A bucket
    whose mean is carried by one enormous day reads high there and near 50 here,
    which is the case a seasonal claim most often turns out to be.
    """
    require_columns(prices, ("close",), "seasonal_hit_rate")
    if bucket not in BUCKETS:
        raise ValueError(f"unknown bucket {bucket!r}; expected one of {BUCKETS}")
    if not isinstance(prices.index, pd.DatetimeIndex):
        raise UnsupportedIndexError(
            "seasonal_hit_rate", "DatetimeIndex", type(prices.index).__name__
        )

    returns = prices["close"].pct_change().to_numpy()
    dates = prices.index.to_numpy()
    keys = _bucket_keys(prices.index, bucket)
    horizon = np.timedelta64(int(round(years * 365.25)), "D")

    out = np.full(len(prices), np.nan)
    for position in range(len(prices)):
        window = (dates >= dates[position] - horizon) & (dates < dates[position])
        matching = window & _same_bucket(keys, int(keys[position]), bucket, window_days)
        chosen = returns[matching]
        chosen = chosen[~np.isnan(chosen)]
        if chosen.size == 0:
            continue
        out[position] = float((chosen > 0.0).mean() * 100.0)

    return pd.Series(out, index=prices.index, name="seasonal_hit_rate")
