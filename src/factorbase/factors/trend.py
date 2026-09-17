"""Directional movement, Aroon, regression trend and the trend template."""

from __future__ import annotations

import numpy as np
import pandas as pd

from ._common import require_columns, simple_moving_average, wilder_smoothing
from .volatility import true_range


def directional_movement(prices: pd.DataFrame) -> pd.DataFrame:
    """Wilder's raw +DM and -DM, before any smoothing.

    Only one of the two can be non-zero on a bar. An inside bar, where today's
    high is lower and today's low is higher, produces zero for both, which is
    the intended answer: no directional movement happened.
    """
    require_columns(prices, ("high", "low"), "directional_movement")
    up_move = prices["high"].diff()
    down_move = -prices["low"].diff()
    # The `.where(..., 0.0)` below turns every unsatisfied condition into a
    # zero, and a NaN never satisfies a comparison. The first bar, which has no
    # predecessor, would therefore report a movement of zero rather than none.
    # That zero is an observation: it is averaged into Wilder's seed, and the
    # smoothed range it is divided by is seeded correctly, so the two halves of
    # every directional indicator start out misaligned. The second `.where`
    # puts the missing value back.
    rose = (up_move > down_move) & (up_move > 0.0)
    fell = (down_move > up_move) & (down_move > 0.0)
    plus = up_move.where(rose, 0.0).where(up_move.notna())
    minus = down_move.where(fell, 0.0).where(down_move.notna())
    return pd.DataFrame({"plus_dm": plus, "minus_dm": minus}, index=prices.index)


def _directional_indicators(prices: pd.DataFrame, periods: int) -> pd.DataFrame:
    movement = directional_movement(prices)
    smoothed_range = wilder_smoothing(true_range(prices), periods)
    plus = 100.0 * wilder_smoothing(movement["plus_dm"], periods) / smoothed_range
    minus = 100.0 * wilder_smoothing(movement["minus_dm"], periods) / smoothed_range
    return pd.DataFrame({"plus_di": plus, "minus_di": minus}, index=prices.index)


def plus_di(prices: pd.DataFrame, periods: int = 14) -> pd.Series:
    """Positive Directional Indicator. Catalogue id `plus_di`."""
    require_columns(prices, ("high", "low", "close"), "plus_di")
    return _directional_indicators(prices, periods)["plus_di"]


def minus_di(prices: pd.DataFrame, periods: int = 14) -> pd.Series:
    """Negative Directional Indicator. Catalogue id `minus_di`."""
    require_columns(prices, ("high", "low", "close"), "minus_di")
    return _directional_indicators(prices, periods)["minus_di"]


def adx(prices: pd.DataFrame, periods: int = 14) -> pd.Series:
    """Average Directional Index. Catalogue id `adx`.

    Two rounds of Wilder smoothing: once on the directional movement, once on
    the DX built from it. The second round is why ADX lags the price turn by
    roughly the period length, and why an ADX reading is a statement about the
    recent past rather than about today.
    """
    require_columns(prices, ("high", "low", "close"), "adx")
    indicators = _directional_indicators(prices, periods)
    total = indicators["plus_di"] + indicators["minus_di"]
    dx = 100.0 * (indicators["plus_di"] - indicators["minus_di"]).abs() / total
    dx = dx.where(total != 0.0, 0.0)
    return wilder_smoothing(dx.dropna(), periods).reindex(prices.index)


def _bars_since_last(window: np.ndarray, want_max: bool) -> float:
    """Position of the LAST occurrence of the extreme inside the window.

    np.argmax and np.argmin return the first occurrence. Aroon asks how long
    ago the extreme happened, so with two equal highs the answer is the later
    one. Taking the first turns a high that is one bar old into a high that is
    six bars old, and a bar that merely matches the window high - which is what
    a price does at a round-number resistance - reads low instead of 100.
    """
    reversed_window = window[::-1]
    offset = int(np.argmax(reversed_window) if want_max else np.argmin(reversed_window))
    return float(len(window) - 1 - offset)


def aroon_up(prices: pd.DataFrame, periods: int = 25) -> pd.Series:
    """Aroon Up. Catalogue id `aroon_up`."""
    require_columns(prices, ("high",), "aroon_up")
    position = (
        prices["high"]
        .rolling(window=periods, min_periods=periods)
        .apply(lambda window: _bars_since_last(window, want_max=True), raw=True)
    )
    return position / (periods - 1) * 100.0


def aroon_down(prices: pd.DataFrame, periods: int = 25) -> pd.Series:
    """Aroon Down. Catalogue id `aroon_down`."""
    require_columns(prices, ("low",), "aroon_down")
    position = (
        prices["low"]
        .rolling(window=periods, min_periods=periods)
        .apply(lambda window: _bars_since_last(window, want_max=False), raw=True)
    )
    return position / (periods - 1) * 100.0


def aroon_oscillator(prices: pd.DataFrame, periods: int = 25) -> pd.Series:
    """Aroon Up minus Aroon Down. Catalogue id `aroon_oscillator`."""
    return aroon_up(prices, periods) - aroon_down(prices, periods)


def _regression(values: np.ndarray) -> tuple[float, float]:
    """Ordinary least squares of `values` on 0..n-1. Returns slope and r squared."""
    n = len(values)
    x = np.arange(n, dtype="float64")
    x_mean = x.mean()
    y_mean = values.mean()
    x_centred = x - x_mean
    y_centred = values - y_mean
    denominator = float((x_centred**2).sum())
    if denominator == 0.0:
        return 0.0, 0.0
    slope = float((x_centred * y_centred).sum() / denominator)
    total = float((y_centred**2).sum())
    if total == 0.0:
        return slope, 1.0
    residual = float(((y_centred - slope * x_centred) ** 2).sum())
    return slope, 1.0 - residual / total


def regression_slope_annualised(
    prices: pd.DataFrame, periods: int = 90, trading_days: int = 250
) -> pd.Series:
    """Annualised slope of a log-price regression, in percent.

    Catalogue id `regression_slope_annualised`.

    The regression runs on the logarithm of the close, so the slope is a daily
    compounding rate and annualising it means compounding, not multiplying.
    """
    require_columns(prices, ("close",), "regression_slope_annualised")
    log_close = np.log(prices["close"])
    slope = log_close.rolling(window=periods, min_periods=periods).apply(
        lambda window: _regression(window)[0], raw=True
    )
    return (np.exp(slope) ** trading_days - 1.0) * 100.0


def trend_stability(prices: pd.DataFrame, periods: int = 90) -> pd.Series:
    """Coefficient of determination of the log-price regression. Catalogue id `trend_stability`."""
    require_columns(prices, ("close",), "trend_stability")
    log_close = np.log(prices["close"])
    return log_close.rolling(window=periods, min_periods=periods).apply(
        lambda window: _regression(window)[1], raw=True
    )


def adjusted_slope(prices: pd.DataFrame, periods: int = 90, trading_days: int = 250) -> pd.Series:
    """Annualised slope scaled by how well the line fits. Catalogue id `adjusted_slope`."""
    return regression_slope_annualised(prices, periods, trading_days) * trend_stability(
        prices, periods
    )


_TEMPLATE_CONDITIONS = (
    "close_above_150_and_200",
    "ma150_above_ma200",
    "ma200_rising",
    "ma50_above_both",
    "close_above_ma50",
    "well_above_52w_low",
    "near_52w_high",
)


def trend_template_conditions(
    prices: pd.DataFrame,
    low_margin: float = 25.0,
    high_margin: float = 25.0,
    ma200_rising_days: int = 22,
    weeks: int = 52,
) -> pd.DataFrame:
    """The seven price conditions of the trend template, one boolean column each.

    Returned as columns rather than as a verdict so that a caller can see which
    condition failed. A single boolean answers "no" without saying why, and
    "why" is the only part that is actionable.

    The published template has an eighth condition on relative strength against
    the wider market. It is not here because it needs a universe, not a price
    series; `relative.relative_strength_rank` is the piece that supplies it.
    """
    require_columns(prices, ("close",), "trend_template_conditions")
    close = prices["close"]
    ma50 = simple_moving_average(close, 50)
    ma150 = simple_moving_average(close, 150)
    ma200 = simple_moving_average(close, 200)
    window = weeks * 5
    low_52w = close.rolling(window=window, min_periods=window).min()
    high_52w = close.rolling(window=window, min_periods=window).max()

    return pd.DataFrame(
        {
            "close_above_150_and_200": (close > ma150) & (close > ma200),
            "ma150_above_ma200": ma150 > ma200,
            "ma200_rising": ma200 > ma200.shift(ma200_rising_days),
            "ma50_above_both": (ma50 > ma150) & (ma50 > ma200),
            "close_above_ma50": close > ma50,
            "well_above_52w_low": close >= low_52w * (1.0 + low_margin / 100.0),
            "near_52w_high": close >= high_52w * (1.0 - high_margin / 100.0),
        },
        index=prices.index,
    )


def trend_template_score(
    prices: pd.DataFrame,
    low_margin: float = 25.0,
    high_margin: float = 25.0,
    ma200_rising_days: int = 22,
    weeks: int = 52,
) -> pd.Series:
    """How many of the seven conditions hold, 0 to 7. Catalogue id `trend_template_score`.

    NaN until every moving average in the template is defined, which takes a
    year of history. Counting an undefined condition as failed would report 4
    of 7 for an instrument that has simply not traded long enough.
    """
    conditions = trend_template_conditions(
        prices, low_margin, high_margin, ma200_rising_days, weeks
    )
    window = weeks * 5
    warm_up = max(200 + ma200_rising_days, window)
    score = conditions.sum(axis=1).astype("float64")
    score.iloc[: warm_up - 1] = np.nan
    return score
