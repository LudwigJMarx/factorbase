"""Rate of change, oscillators and the MACD family."""

from __future__ import annotations

import numpy as np
import pandas as pd

from ._common import (
    exponential_moving_average,
    require_columns,
    simple_moving_average,
    wilder_smoothing,
)


def _smooth(series: pd.Series, periods: int, method: str) -> pd.Series:
    if method == "wilder":
        return wilder_smoothing(series, periods)
    if method == "sma":
        return simple_moving_average(series, periods)
    if method == "ema":
        return exponential_moving_average(series, periods)
    raise ValueError(f"unknown smoothing {method!r}; expected one of ('wilder', 'sma', 'ema')")


def rsi(prices: pd.DataFrame, periods: int = 14, method: str = "wilder") -> pd.Series:
    """Relative Strength Index. Catalogue id `rsi`.

    Computed as 100 * avg_gain / (avg_gain + avg_loss) rather than through the
    RS quotient. The two are algebraically identical, but the quotient form
    divides by zero on a stretch with no down bar, where the correct answer is
    exactly 100 and not a NaN.
    """
    require_columns(prices, ("close",), "rsi")
    change = prices["close"].diff()
    gain = change.clip(lower=0.0)
    loss = (-change).clip(lower=0.0)
    average_gain = _smooth(gain, periods, method)
    average_loss = _smooth(loss, periods, method)
    total = average_gain + average_loss
    return (average_gain / total * 100.0).where(total != 0.0, 50.0)


def rate_of_change(prices: pd.DataFrame, periods: int = 12) -> pd.Series:
    """Percentage change over n bars. Catalogue id `rate_of_change`."""
    require_columns(prices, ("close",), "rate_of_change")
    return (prices["close"] / prices["close"].shift(periods) - 1.0) * 100.0


def absolute_price_change(prices: pd.DataFrame, periods: int = 12) -> pd.Series:
    """Currency change over n bars. Catalogue id `absolute_price_change`."""
    require_columns(prices, ("close",), "absolute_price_change")
    return prices["close"] - prices["close"].shift(periods)


def macd(prices: pd.DataFrame, fast_periods: int = 12, slow_periods: int = 26) -> pd.Series:
    """Fast EMA minus slow EMA. Catalogue id `macd`."""
    require_columns(prices, ("close",), "macd")
    fast = exponential_moving_average(prices["close"], fast_periods)
    slow = exponential_moving_average(prices["close"], slow_periods)
    return fast - slow


def macd_signal(
    prices: pd.DataFrame,
    fast_periods: int = 12,
    slow_periods: int = 26,
    signal_periods: int = 9,
) -> pd.Series:
    """EMA of the MACD line. Catalogue id `macd_signal`.

    The signal average is seeded from the first `signal_periods` defined MACD
    values, not from the start of the frame, so the NaN warm-up of the MACD
    line does not leak into the seed.
    """
    line = macd(prices, fast_periods, slow_periods)
    defined = line.dropna()
    smoothed = exponential_moving_average(defined, signal_periods)
    return smoothed.reindex(line.index)


def macd_histogram(
    prices: pd.DataFrame,
    fast_periods: int = 12,
    slow_periods: int = 26,
    signal_periods: int = 9,
) -> pd.Series:
    """MACD line minus signal line. Catalogue id `macd_histogram`."""
    return macd(prices, fast_periods, slow_periods) - macd_signal(
        prices, fast_periods, slow_periods, signal_periods
    )


def macd_histogram_change(
    prices: pd.DataFrame,
    fast_periods: int = 12,
    slow_periods: int = 26,
    signal_periods: int = 9,
    lookback: int = 1,
) -> pd.Series:
    """Change in the histogram over `lookback` bars. Catalogue id `macd_histogram_change`."""
    histogram = macd_histogram(prices, fast_periods, slow_periods, signal_periods)
    return histogram - histogram.shift(lookback)


def macd_momentum(
    prices: pd.DataFrame,
    fast_periods: int = 12,
    slow_periods: int = 26,
    lookback: int = 1,
) -> pd.Series:
    """Change in the MACD line over `lookback` bars. Catalogue id `macd_momentum`."""
    line = macd(prices, fast_periods, slow_periods)
    return line - line.shift(lookback)


def typical_price(prices: pd.DataFrame) -> pd.Series:
    """Mean of high, low and close."""
    require_columns(prices, ("high", "low", "close"), "typical_price")
    return (prices["high"] + prices["low"] + prices["close"]) / 3.0


def cci(prices: pd.DataFrame, periods: int = 20) -> pd.Series:
    """Commodity Channel Index. Catalogue id `cci`.

    The mean deviation is taken around the window's own current average, which
    is what Lambert specified. Taking it around each bar's average instead, a
    common shortcut, produces a visibly different and slightly smaller
    denominator.
    """
    typical = typical_price(prices)
    average = simple_moving_average(typical, periods)

    def mean_deviation(window: np.ndarray) -> float:
        return float(np.abs(window - window.mean()).mean())

    deviation = typical.rolling(window=periods, min_periods=periods).apply(mean_deviation, raw=True)
    return (typical - average) / (0.015 * deviation)


def _range_position(prices: pd.DataFrame, periods: int, factor_id: str) -> pd.Series:
    require_columns(prices, ("high", "low", "close"), factor_id)
    highest = prices["high"].rolling(window=periods, min_periods=periods).max()
    lowest = prices["low"].rolling(window=periods, min_periods=periods).min()
    span = highest - lowest
    position = (prices["close"] - lowest) / span * 100.0
    return position.where(span != 0.0, 50.0)


def williams_percent_r(prices: pd.DataFrame, periods: int = 14) -> pd.Series:
    """Williams %R, on its native 0 to -100 scale. Catalogue id `williams_percent_r`."""
    return _range_position(prices, periods, "williams_percent_r") - 100.0


def stochastic_fast_k(prices: pd.DataFrame, periods: int = 14) -> pd.Series:
    """Raw stochastic %K. Catalogue id `stochastic_fast_k`."""
    return _range_position(prices, periods, "stochastic_fast_k")


def stochastic_fast_d(prices: pd.DataFrame, periods: int = 14, smoothing: int = 3) -> pd.Series:
    """Fast %D, i.e. %K smoothed once. Catalogue id `stochastic_fast_d`."""
    return simple_moving_average(stochastic_fast_k(prices, periods), smoothing)


def stochastic_slow_k(prices: pd.DataFrame, periods: int = 14, smoothing: int = 3) -> pd.Series:
    """Slow %K, which is the same series as fast %D. Catalogue id `stochastic_slow_k`."""
    return stochastic_fast_d(prices, periods, smoothing)


def stochastic_slow_d(
    prices: pd.DataFrame, periods: int = 14, smoothing: int = 3, second_smoothing: int = 3
) -> pd.Series:
    """Slow %D, i.e. %K smoothed twice. Catalogue id `stochastic_slow_d`."""
    return simple_moving_average(stochastic_slow_k(prices, periods, smoothing), second_smoothing)


def double_smoothed_stochastic_blau(
    prices: pd.DataFrame,
    periods: int = 10,
    first_smoothing: int = 3,
    second_smoothing: int = 3,
) -> pd.Series:
    """Blau's double smoothed stochastic. Catalogue id `double_smoothed_stochastic_blau`.

    Numerator and denominator are smoothed before the division, which is the
    whole point of the construction.
    """
    require_columns(prices, ("high", "low", "close"), "double_smoothed_stochastic_blau")
    highest = prices["high"].rolling(window=periods, min_periods=periods).max()
    lowest = prices["low"].rolling(window=periods, min_periods=periods).min()

    numerator = exponential_moving_average(
        exponential_moving_average((prices["close"] - lowest).dropna(), first_smoothing),
        second_smoothing,
    )
    denominator = exponential_moving_average(
        exponential_moving_average((highest - lowest).dropna(), first_smoothing),
        second_smoothing,
    )
    result = 100.0 * numerator / denominator
    return result.where(denominator != 0.0, 50.0).reindex(prices.index)


def double_smoothed_stochastic_bressert(
    prices: pd.DataFrame,
    periods: int = 10,
    first_smoothing: int = 3,
    second_smoothing: int = 3,
) -> pd.Series:
    """Bressert's double smoothed stochastic. Catalogue id `double_smoothed_stochastic_bressert`."""
    raw = stochastic_fast_k(prices, periods).dropna()
    smoothed = exponential_moving_average(raw, first_smoothing).dropna()
    highest = smoothed.rolling(window=periods, min_periods=periods).max()
    lowest = smoothed.rolling(window=periods, min_periods=periods).min()
    span = highest - lowest
    second = ((smoothed - lowest) / span * 100.0).where(span != 0.0, 50.0)
    result = exponential_moving_average(second.dropna(), second_smoothing)
    return result.reindex(prices.index)
