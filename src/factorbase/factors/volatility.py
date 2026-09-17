"""Range, deviation and drawdown."""

from __future__ import annotations

import numpy as np
import pandas as pd

from ._common import require_columns, simple_moving_average, wilder_smoothing


def true_range(prices: pd.DataFrame) -> pd.Series:
    """The larger of today's range and the gap to yesterday's close.

    Wilder's point was that a gap is movement the plain high-low range does not
    see. On the first bar there is no previous close, so the plain range is
    used rather than a NaN: dropping the first bar would shift every subsequent
    average by one observation.
    """
    require_columns(prices, ("high", "low", "close"), "true_range")
    previous_close = prices["close"].shift(1)
    spans = pd.concat(
        [
            prices["high"] - prices["low"],
            (prices["high"] - previous_close).abs(),
            (prices["low"] - previous_close).abs(),
        ],
        axis=1,
    )
    return spans.max(axis=1)


def atr(prices: pd.DataFrame, periods: int = 14) -> pd.Series:
    """Average True Range, smoothed the way Wilder smoothed it."""
    require_columns(prices, ("high", "low", "close"), "atr")
    return wilder_smoothing(true_range(prices), periods)


def atr_percent(prices: pd.DataFrame, periods: int = 14) -> pd.Series:
    """ATR as a share of the close, so it compares across price levels."""
    require_columns(prices, ("high", "low", "close"), "atr_percent")
    return atr(prices, periods) / prices["close"] * 100.0


def historical_volatility(
    prices: pd.DataFrame, periods: int = 250, trading_days: int = 250
) -> pd.Series:
    """Annualised standard deviation of logarithmic daily returns.

    Log returns rather than simple ones, because they add across time, which is
    what annualising by the square root of the period count assumes.
    """
    require_columns(prices, ("close",), "historical_volatility")
    log_returns = np.log(prices["close"] / prices["close"].shift(1))
    deviation = log_returns.rolling(window=periods, min_periods=periods).std(ddof=1)
    return deviation * np.sqrt(trading_days) * 100.0


def average_drawdown(prices: pd.DataFrame, periods: int = 250) -> pd.Series:
    """Mean distance below the running peak over the window, in percent.

    Not the maximum drawdown. The maximum is one bad day out of the window; the
    mean says how much of the time the instrument spent underwater, which is
    the property an allocator actually lives with.
    """
    require_columns(prices, ("close",), "average_drawdown")
    close = prices["close"]
    running_peak = close.rolling(window=periods, min_periods=periods).max()
    underwater = (close / running_peak - 1.0) * 100.0
    return underwater.rolling(window=periods, min_periods=periods).mean()


def max_drawdown(prices: pd.DataFrame, periods: int = 250) -> pd.Series:
    """Worst peak-to-trough fall inside the window, in percent, as a negative number."""
    require_columns(prices, ("close",), "max_drawdown")
    close = prices["close"]

    def worst(window: np.ndarray) -> float:
        peaks = np.maximum.accumulate(window)
        return float(((window / peaks - 1.0) * 100.0).min())

    return close.rolling(window=periods, min_periods=periods).apply(worst, raw=True)


def trading_range(prices: pd.DataFrame, periods: int = 20) -> pd.Series:
    """Highest high to lowest low over the window, as a percentage of the low.

    A compression measure: a narrow reading says the instrument has gone
    nowhere, which is the precondition every breakout method looks for.
    """
    require_columns(prices, ("high", "low"), "trading_range")
    highest = prices["high"].rolling(window=periods, min_periods=periods).max()
    lowest = prices["low"].rolling(window=periods, min_periods=periods).min()
    return (highest - lowest) / lowest * 100.0


def bollinger_bands(
    prices: pd.DataFrame, periods: int = 20, deviations: float = 2.0
) -> pd.DataFrame:
    """Middle, upper and lower band as three columns.

    The deviation is the population standard deviation (ddof=0), which is what
    Bollinger specified and what charting packages draw. Using the sample
    deviation widens the bands slightly and is a common source of two
    implementations disagreeing in the third decimal.
    """
    require_columns(prices, ("close",), "bollinger_bands")
    middle = simple_moving_average(prices["close"], periods)
    spread = prices["close"].rolling(window=periods, min_periods=periods).std(ddof=0) * deviations
    return pd.DataFrame(
        {"middle": middle, "upper": middle + spread, "lower": middle - spread},
        index=prices.index,
    )


def bollinger_percent_b(
    prices: pd.DataFrame, periods: int = 20, deviations: float = 2.0
) -> pd.Series:
    """Where the close sits between the bands: 0 at the lower, 1 at the upper.

    Values outside [0, 1] are normal and meaningful, not errors: they say the
    close is beyond the band.
    """
    bands = bollinger_bands(prices, periods, deviations)
    return (prices["close"] - bands["lower"]) / (bands["upper"] - bands["lower"])


def bollinger_band_width(
    prices: pd.DataFrame, periods: int = 20, deviations: float = 2.0
) -> pd.Series:
    """Band separation as a share of the middle band, in percent."""
    bands = bollinger_bands(prices, periods, deviations)
    return (bands["upper"] - bands["lower"]) / bands["middle"] * 100.0


def distance_to_upper_band(
    prices: pd.DataFrame, periods: int = 20, deviations: float = 2.0
) -> pd.Series:
    """Percentage gap from the close up to the upper band; negative once above it."""
    bands = bollinger_bands(prices, periods, deviations)
    return (bands["upper"] - prices["close"]) / prices["close"] * 100.0


def distance_to_lower_band(
    prices: pd.DataFrame, periods: int = 20, deviations: float = 2.0
) -> pd.Series:
    """Percentage gap from the close down to the lower band; negative once below it."""
    bands = bollinger_bands(prices, periods, deviations)
    return (prices["close"] - bands["lower"]) / prices["close"] * 100.0
