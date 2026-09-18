"""Volume-weighted measures: accumulation, money flow, turnover."""

from __future__ import annotations

import pandas as pd

from ._common import exponential_moving_average, require_columns, simple_moving_average
from .momentum import typical_price


def close_location_value(prices: pd.DataFrame) -> pd.Series:
    """Where the close finished inside the bar, from -1 at the low to +1 at the high.

    A bar whose high equals its low has no location to report. It is treated as
    zero rather than as a division by zero: no information, not infinite
    information.
    """
    require_columns(prices, ("high", "low", "close"), "close_location_value")
    span = prices["high"] - prices["low"]
    value = ((prices["close"] - prices["low"]) - (prices["high"] - prices["close"])) / span
    return value.where(span != 0.0, 0.0)


def accumulation_distribution_line(prices: pd.DataFrame) -> pd.Series:
    """Running total of volume signed by where the close sat in its bar.

    Catalogue id `accumulation_distribution_line`.

    A cumulative sum from the first bar of the frame, so the level depends on
    where the history starts and only its direction carries meaning. Comparing
    the level between two instruments, or between two loads of the same
    instrument over different windows, compares the starting points.
    """
    require_columns(prices, ("high", "low", "close", "volume"), "accumulation_distribution_line")
    return (close_location_value(prices) * prices["volume"]).cumsum()


def chaikin_oscillator(
    prices: pd.DataFrame, fast_periods: int = 3, slow_periods: int = 10
) -> pd.Series:
    """Fast minus slow exponential average of the accumulation line.

    Catalogue id `chaikin_oscillator`.

    Taking a difference of two averages removes the arbitrary starting level
    that the line itself carries, which is what makes the oscillator comparable
    where the line is not.
    """
    line = accumulation_distribution_line(prices)
    return exponential_moving_average(line, fast_periods) - exponential_moving_average(
        line, slow_periods
    )


def money_flow_index(prices: pd.DataFrame, periods: int = 14) -> pd.Series:
    """Volume-weighted RSI on the typical price. Catalogue id `money_flow_index`.

    Same construction as the RSI, with each bar's contribution weighted by the
    money that changed hands. A quiet drift upward and a heavily traded advance
    read the same on RSI and differently here, which is the entire reason to
    prefer it.

    A bar whose typical price is unchanged counts on neither side, and the
    first bar of the frame, which has no predecessor, counts on neither either.
    Both are silently lumped into the negative side by implementations that
    test only for "not rising".
    """
    require_columns(prices, ("high", "low", "close", "volume"), "money_flow_index")
    typical = typical_price(prices)
    raw_flow = (typical * prices["volume"]).iloc[1:]
    change = typical.diff().iloc[1:]
    positive = raw_flow.where(change > 0.0, 0.0).rolling(periods, min_periods=periods).sum()
    negative = raw_flow.where(change < 0.0, 0.0).rolling(periods, min_periods=periods).sum()
    total = positive + negative
    result = (positive / total * 100.0).where(total != 0.0, 50.0)
    return result.reindex(prices.index)


def average_turnover(prices: pd.DataFrame, periods: int = 20) -> pd.Series:
    """Mean of close times volume over the window, in currency. Catalogue id `average_turnover`.

    Turnover rather than share count, because a share count is meaningless
    across instruments: a million shares of a one-euro stock and a million of a
    five-hundred-euro one are different markets. This is the figure a liquidity
    filter should use.
    """
    require_columns(prices, ("close", "volume"), "average_turnover")
    return simple_moving_average(prices["close"] * prices["volume"], periods)


def relative_volume(prices: pd.DataFrame, periods: int = 20) -> pd.Series:
    """Today's volume against its own average. Catalogue id `relative_volume`.

    The average excludes the current bar. Including it would dampen exactly the
    spike the factor exists to detect, by up to a twentieth of its own size at
    the default window.
    """
    require_columns(prices, ("volume",), "relative_volume")
    average = simple_moving_average(prices["volume"].shift(1), periods)
    return prices["volume"] / average


def volume_trend(prices: pd.DataFrame, periods: int = 20, lookback: int = 20) -> pd.Series:
    """Percentage change of average volume over `lookback` bars. Catalogue id `volume_trend`."""
    require_columns(prices, ("volume",), "volume_trend")
    average = simple_moving_average(prices["volume"], periods)
    past = average.shift(lookback)
    return (average - past) / past * 100.0


def average_volume(prices: pd.DataFrame, periods: int = 20) -> pd.Series:
    """Mean volume over the window, in shares. Catalogue id `average_volume`.

    In shares, not in currency. `average_turnover` argues that a share count
    cannot be compared across instruments, and that argument stands: a million
    shares of a one-euro stock and a million of a five-hundred-euro one are
    different markets. What a share count can do is be compared to the same
    instrument's own past, which is what a volume filter on a single name
    actually needs, and it is the figure an exchange reports.
    """
    require_columns(prices, ("volume",), "average_volume")
    return simple_moving_average(prices["volume"], periods)
