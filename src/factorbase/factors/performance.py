"""Return, position in the range, and bar-counting measures."""

from __future__ import annotations

import numpy as np
import pandas as pd

from ._common import require_columns


def _price_column(prices: pd.DataFrame, adjusted: bool, factor_id: str) -> pd.Series:
    """Adjusted close where asked for and available, plain close otherwise.

    Falling back silently would let a total-return factor quietly report a
    price return, so the fallback raises instead when the caller asked for
    adjusted prices and the frame has none.
    """
    if adjusted:
        require_columns(prices, ("adjusted_close",), factor_id)
        return prices["adjusted_close"]
    require_columns(prices, ("close",), factor_id)
    return prices["close"]


def price(prices: pd.DataFrame) -> pd.Series:
    """The close itself. Catalogue id `price`.

    In the catalogue because a screen frequently wants to filter on price level
    directly, and because leaving it out would force callers to reach past the
    factor interface for the one column everything else is built on.
    """
    require_columns(prices, ("close",), "price")
    return prices["close"]


def performance(prices: pd.DataFrame, periods: int = 250, adjusted: bool = False) -> pd.Series:
    """Percentage return over n bars. Catalogue id `performance`."""
    series = _price_column(prices, adjusted, "performance")
    return (series / series.shift(periods) - 1.0) * 100.0


def daily_performance(prices: pd.DataFrame, adjusted: bool = False) -> pd.Series:
    """Percentage return of the latest bar. Catalogue id `daily_performance`."""
    series = _price_column(prices, adjusted, "daily_performance")
    return series.pct_change() * 100.0


def annualised_performance(
    prices: pd.DataFrame, periods: int = 750, trading_days: int = 250, adjusted: bool = False
) -> pd.Series:
    """Compound annual growth rate over the window, in percent. Catalogue id `annualised_performance`.

    The geometric rate, not the arithmetic mean of returns. The two differ by
    more than most readers expect: a year of +50 percent followed by a year of
    -50 percent averages zero arithmetically and -13.4 percent a year here, and
    the second number is the one the account shows.
    """
    series = _price_column(prices, adjusted, "annualised_performance")
    total = series / series.shift(periods)
    years = periods / trading_days
    return (total ** (1.0 / years) - 1.0) * 100.0


def winning_days(prices: pd.DataFrame, periods: int = 250) -> pd.Series:
    """Share of bars in the window that closed up, in percent. Catalogue id `winning_days`.

    Unchanged bars count as losses, matching the usual convention. It matters
    on thin instruments, where unchanged closes are common enough to move the
    reading by several points.
    """
    require_columns(prices, ("close",), "winning_days")
    up = (prices["close"].diff() > 0.0).astype("float64")
    up.iloc[0] = np.nan
    return up.rolling(window=periods, min_periods=periods).mean() * 100.0


def distance_to_high(prices: pd.DataFrame, periods: int = 250) -> pd.Series:
    """How far the close sits below the window's highest close, in percent. Catalogue id `distance_to_high`.

    Zero at a new high, negative everywhere else. Measured close to close
    rather than close to intraday high, so a single spike does not hold the
    reading down for a year.
    """
    require_columns(prices, ("close",), "distance_to_high")
    highest = prices["close"].rolling(window=periods, min_periods=periods).max()
    return (prices["close"] / highest - 1.0) * 100.0


def distance_to_low(prices: pd.DataFrame, periods: int = 250) -> pd.Series:
    """How far the close sits above the window's lowest close, in percent. Catalogue id `distance_to_low`."""
    require_columns(prices, ("close",), "distance_to_low")
    lowest = prices["close"].rolling(window=periods, min_periods=periods).min()
    return (prices["close"] / lowest - 1.0) * 100.0


def inside_bars(prices: pd.DataFrame, periods: int = 20) -> pd.Series:
    """Count of inside bars in the window. Catalogue id `inside_bars`.

    An inside bar has a lower high and a higher low than the bar before it:
    the whole session happened inside yesterday's range. A cluster of them is
    the compression that precedes an expansion, and counting them is a cheaper
    way to find that state than fitting a range.
    """
    require_columns(prices, ("high", "low"), "inside_bars")
    inside = (prices["high"] < prices["high"].shift(1)) & (prices["low"] > prices["low"].shift(1))
    counted = inside.astype("float64")
    counted.iloc[0] = np.nan
    return counted.rolling(window=periods, min_periods=periods).sum()


def bars_of_history(prices: pd.DataFrame) -> pd.Series:
    """How many bars the instrument has traded up to and including this one. Catalogue id `bars_of_history`.

    A gate, not a signal. Most factors need a year or more of history, and a
    universe assembled without checking this quietly fills with recent listings
    whose readings are NaN or, worse, computed from a short window that happens
    to be long enough to return a number.
    """
    require_columns(prices, ("close",), "bars_of_history")
    traded = prices["close"].notna().cumsum().astype("float64")
    return traded.where(prices["close"].notna())
