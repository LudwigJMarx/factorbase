"""Moving averages and the factors read directly off them."""

from __future__ import annotations

import pandas as pd

from ._common import (
    exponential_moving_average,
    moving_average,
    require_columns,
    simple_moving_average,
    weighted_moving_average,
)
from .volatility import atr


def sma(prices: pd.DataFrame, periods: int = 200) -> pd.Series:
    """Simple moving average of the close. Catalogue id `sma`."""
    require_columns(prices, ("close",), "sma")
    return simple_moving_average(prices["close"], periods)


def ema(prices: pd.DataFrame, periods: int = 200) -> pd.Series:
    """Exponential moving average of the close, seeded with an SMA. Catalogue id `ema`."""
    require_columns(prices, ("close",), "ema")
    return exponential_moving_average(prices["close"], periods)


def wma(prices: pd.DataFrame, periods: int = 200) -> pd.Series:
    """Linearly weighted moving average of the close. Catalogue id `wma`."""
    require_columns(prices, ("close",), "wma")
    return weighted_moving_average(prices["close"], periods)


def price_to_ma_distance(
    prices: pd.DataFrame, periods: int = 200, method: str = "sma"
) -> pd.Series:
    """Close against its own average, in percent of the average. Catalogue id `price_to_ma_distance`."""
    require_columns(prices, ("close",), "price_to_ma_distance")
    average = moving_average(prices["close"], periods, method)
    return (prices["close"] - average) / average * 100.0


def ma_to_ma_distance(
    prices: pd.DataFrame, fast_periods: int = 50, slow_periods: int = 200, method: str = "sma"
) -> pd.Series:
    """Fast average against slow average, in percent of the slow one. Catalogue id `ma_to_ma_distance`."""
    require_columns(prices, ("close",), "ma_to_ma_distance")
    fast = moving_average(prices["close"], fast_periods, method)
    slow = moving_average(prices["close"], slow_periods, method)
    return (fast - slow) / slow * 100.0


def ma_slope(
    prices: pd.DataFrame, periods: int = 200, lookback: int = 20, method: str = "sma"
) -> pd.Series:
    """Percentage change of the average over `lookback` bars. Catalogue id `ma_slope`."""
    require_columns(prices, ("close",), "ma_slope")
    average = moving_average(prices["close"], periods, method)
    past = average.shift(lookback)
    return (average - past) / past * 100.0


def ma_slope_normalized(
    prices: pd.DataFrame, periods: int = 200, lookback: int = 20, method: str = "sma"
) -> pd.Series:
    """Average's change over `lookback` bars, divided by ATR. Catalogue id `ma_slope_normalized`."""
    require_columns(prices, ("high", "low", "close"), "ma_slope_normalized")
    average = moving_average(prices["close"], periods, method)
    return (average - average.shift(lookback)) / atr(prices, periods)
