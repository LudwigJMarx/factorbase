"""Candlestick patterns.

Every pattern here is a rule over one, two or three bars. The rules are written
out rather than taken from a chart-reading tradition, because "a long body"
and "a short shadow" are not computable until somebody fixes a threshold. Those
thresholds are parameters with stated defaults, and the defaults are this
package's choices, not quoted standards. Two charting packages will disagree on
what counts as a hammer; at least this one says what it counted.

Each function returns a boolean Series aligned to the input index. Bars where
the pattern cannot be evaluated, at the start of the frame, are False rather
than NaN: a pattern that cannot be evaluated has not occurred.
"""

from __future__ import annotations

import pandas as pd

from ._common import require_columns, simple_moving_average

_OHLC = ("open", "high", "low", "close")


def anatomy(prices: pd.DataFrame) -> pd.DataFrame:
    """Body, shadows and range of each bar, as columns.

    A zero-range bar, which happens on halted or untraded instruments, would
    divide by zero in every ratio built on it. Its range is treated as NaN, so
    every ratio derived from it is NaN and every pattern test on it is False.
    """
    require_columns(prices, _OHLC, "anatomy")
    open_, high, low, close = (prices[c] for c in _OHLC)
    body_top = pd.concat([open_, close], axis=1).max(axis=1)
    body_bottom = pd.concat([open_, close], axis=1).min(axis=1)
    span = (high - low).where(high != low)
    return pd.DataFrame(
        {
            "body": (close - open_).abs(),
            "signed_body": close - open_,
            "body_top": body_top,
            "body_bottom": body_bottom,
            "upper_shadow": high - body_top,
            "lower_shadow": body_bottom - low,
            "span": span,
            "body_ratio": (close - open_).abs() / span,
            "upper_ratio": (high - body_top) / span,
            "lower_ratio": (body_bottom - low) / span,
            "bullish": close > open_,
            "bearish": close < open_,
        },
        index=prices.index,
    )


def _clean(condition: pd.Series, prices: pd.DataFrame) -> pd.Series:
    """NaN means the pattern could not be evaluated, which is not an occurrence."""
    return condition.fillna(False).astype("bool").reindex(prices.index, fill_value=False)


# ── Single-bar patterns ─────────────────────────────────────────────────────

def doji(prices: pd.DataFrame, max_body_ratio: float = 0.05) -> pd.Series:
    """Open and close within a fraction of the bar's range. Catalogue id `cs_doji`."""
    return _clean(anatomy(prices)["body_ratio"] <= max_body_ratio, prices)


def dragonfly_doji(
    prices: pd.DataFrame, max_body_ratio: float = 0.05, max_upper_ratio: float = 0.1
) -> pd.Series:
    """A doji whose whole range lies below the open and close. Catalogue id `cs_dragonfly_doji`."""
    shape = anatomy(prices)
    return _clean(
        (shape["body_ratio"] <= max_body_ratio) & (shape["upper_ratio"] <= max_upper_ratio),
        prices,
    )


def gravestone_doji(
    prices: pd.DataFrame, max_body_ratio: float = 0.05, max_lower_ratio: float = 0.1
) -> pd.Series:
    """A doji whose whole range lies above the open and close. Catalogue id `cs_gravestone_doji`."""
    shape = anatomy(prices)
    return _clean(
        (shape["body_ratio"] <= max_body_ratio) & (shape["lower_ratio"] <= max_lower_ratio),
        prices,
    )


def spinning_top(
    prices: pd.DataFrame, max_body_ratio: float = 0.3, min_shadow_ratio: float = 0.25
) -> pd.Series:
    """Small body with a shadow of its own on each side. Catalogue id `cs_spinning_top`."""
    shape = anatomy(prices)
    return _clean(
        (shape["body_ratio"] <= max_body_ratio)
        & (shape["upper_ratio"] >= min_shadow_ratio)
        & (shape["lower_ratio"] >= min_shadow_ratio),
        prices,
    )


def _long_body(prices: pd.DataFrame, periods: int, multiple: float) -> pd.Series:
    """A body larger than `multiple` times the recent average body.

    Measured against this instrument's own recent bars, not against an absolute
    size. "Long" on a utility and on a biotech are different lengths.
    """
    body = anatomy(prices)["body"]
    reference = simple_moving_average(body.shift(1), periods)
    return body >= multiple * reference


def big_white_candle(
    prices: pd.DataFrame, periods: int = 20, multiple: float = 1.5, min_body_ratio: float = 0.6
) -> pd.Series:
    """A long up bar that closed near its high. Catalogue id `cs_big_white_candle`."""
    shape = anatomy(prices)
    return _clean(
        shape["bullish"]
        & _long_body(prices, periods, multiple)
        & (shape["body_ratio"] >= min_body_ratio),
        prices,
    )


def big_black_candle(
    prices: pd.DataFrame, periods: int = 20, multiple: float = 1.5, min_body_ratio: float = 0.6
) -> pd.Series:
    """A long down bar that closed near its low. Catalogue id `cs_big_black_candle`."""
    shape = anatomy(prices)
    return _clean(
        shape["bearish"]
        & _long_body(prices, periods, multiple)
        & (shape["body_ratio"] >= min_body_ratio),
        prices,
    )


def white_marubozu(prices: pd.DataFrame, max_shadow_ratio: float = 0.03) -> pd.Series:
    """An up bar with effectively no shadows. Catalogue id `cs_white_marubozu`."""
    shape = anatomy(prices)
    return _clean(
        shape["bullish"]
        & (shape["upper_ratio"] <= max_shadow_ratio)
        & (shape["lower_ratio"] <= max_shadow_ratio),
        prices,
    )


def black_marubozu(prices: pd.DataFrame, max_shadow_ratio: float = 0.03) -> pd.Series:
    """A down bar with effectively no shadows. Catalogue id `cs_black_marubozu`."""
    shape = anatomy(prices)
    return _clean(
        shape["bearish"]
        & (shape["upper_ratio"] <= max_shadow_ratio)
        & (shape["lower_ratio"] <= max_shadow_ratio),
        prices,
    )


def hammer(
    prices: pd.DataFrame,
    max_body_ratio: float = 0.3,
    min_lower_ratio: float = 0.5,
    max_upper_ratio: float = 0.15,
    trend_periods: int = 10,
) -> pd.Series:
    """Small body at the top of the range, long lower shadow, after a decline. Catalogue id `cs_hammer`.

    The preceding decline is part of the definition and is usually dropped by
    pattern scanners. Without it the same shape appearing mid-advance is
    counted, which is a different bar with a different meaning.
    """
    shape = anatomy(prices)
    declining = prices["close"].shift(1) < prices["close"].shift(trend_periods + 1)
    return _clean(
        (shape["body_ratio"] <= max_body_ratio)
        & (shape["lower_ratio"] >= min_lower_ratio)
        & (shape["upper_ratio"] <= max_upper_ratio)
        & declining,
        prices,
    )


def shooting_star(
    prices: pd.DataFrame,
    max_body_ratio: float = 0.3,
    min_upper_ratio: float = 0.5,
    max_lower_ratio: float = 0.15,
    trend_periods: int = 10,
) -> pd.Series:
    """Small body at the bottom of the range, long upper shadow, after an advance. Catalogue id `cs_shooting_star`."""
    shape = anatomy(prices)
    advancing = prices["close"].shift(1) > prices["close"].shift(trend_periods + 1)
    return _clean(
        (shape["body_ratio"] <= max_body_ratio)
        & (shape["upper_ratio"] >= min_upper_ratio)
        & (shape["lower_ratio"] <= max_lower_ratio)
        & advancing,
        prices,
    )


def bullish_belt_hold(
    prices: pd.DataFrame, max_lower_ratio: float = 0.03, min_body_ratio: float = 0.6
) -> pd.Series:
    """Opens at its low and closes well up. Catalogue id `cs_bullish_belt_hold`."""
    shape = anatomy(prices)
    return _clean(
        shape["bullish"]
        & (shape["lower_ratio"] <= max_lower_ratio)
        & (shape["body_ratio"] >= min_body_ratio),
        prices,
    )


def bearish_belt_hold(
    prices: pd.DataFrame, max_upper_ratio: float = 0.03, min_body_ratio: float = 0.6
) -> pd.Series:
    """Opens at its high and closes well down. Catalogue id `cs_bearish_belt_hold`."""
    shape = anatomy(prices)
    return _clean(
        shape["bearish"]
        & (shape["upper_ratio"] <= max_upper_ratio)
        & (shape["body_ratio"] >= min_body_ratio),
        prices,
    )


# ── Two-bar patterns ────────────────────────────────────────────────────────

def bullish_engulfing(prices: pd.DataFrame) -> pd.Series:
    """An up bar whose body covers the previous down bar's body. Catalogue id `cs_bullish_engulfing`.

    Body against body, not range against range. The shadows are explicitly not
    part of the pattern, which is the point most implementations get wrong by
    comparing highs and lows.
    """
    shape = anatomy(prices)
    return _clean(
        shape["bullish"]
        & shape["bearish"].shift(1).astype("boolean")
        & (shape["body_bottom"] <= shape["body_bottom"].shift(1))
        & (shape["body_top"] >= shape["body_top"].shift(1))
        & (shape["body"] > shape["body"].shift(1)),
        prices,
    )


def bearish_engulfing(prices: pd.DataFrame) -> pd.Series:
    """A down bar whose body covers the previous up bar's body. Catalogue id `cs_bearish_engulfing`."""
    shape = anatomy(prices)
    return _clean(
        shape["bearish"]
        & shape["bullish"].shift(1).astype("boolean")
        & (shape["body_bottom"] <= shape["body_bottom"].shift(1))
        & (shape["body_top"] >= shape["body_top"].shift(1))
        & (shape["body"] > shape["body"].shift(1)),
        prices,
    )


def bullish_harami(prices: pd.DataFrame) -> pd.Series:
    """A small up body contained inside the previous long down body. Catalogue id `cs_bullish_harami`."""
    shape = anatomy(prices)
    return _clean(
        shape["bullish"]
        & shape["bearish"].shift(1).astype("boolean")
        & (shape["body_top"] <= shape["body_top"].shift(1))
        & (shape["body_bottom"] >= shape["body_bottom"].shift(1))
        & (shape["body"] < shape["body"].shift(1)),
        prices,
    )


def bearish_harami(prices: pd.DataFrame) -> pd.Series:
    """A small down body contained inside the previous long up body. Catalogue id `cs_bearish_harami`."""
    shape = anatomy(prices)
    return _clean(
        shape["bearish"]
        & shape["bullish"].shift(1).astype("boolean")
        & (shape["body_top"] <= shape["body_top"].shift(1))
        & (shape["body_bottom"] >= shape["body_bottom"].shift(1))
        & (shape["body"] < shape["body"].shift(1)),
        prices,
    )


def above_the_stomach(prices: pd.DataFrame) -> pd.Series:
    """An up bar opening and closing above the midpoint of the previous down bar's body. Catalogue id `cs_above_the_stomach`."""
    shape = anatomy(prices)
    midpoint = (shape["body_top"].shift(1) + shape["body_bottom"].shift(1)) / 2.0
    return _clean(
        shape["bullish"]
        & shape["bearish"].shift(1).astype("boolean")
        & (prices["open"] >= midpoint)
        & (prices["close"] >= midpoint),
        prices,
    )


def below_the_stomach(prices: pd.DataFrame) -> pd.Series:
    """A down bar opening and closing below the midpoint of the previous up bar's body. Catalogue id `cs_below_the_stomach`."""
    shape = anatomy(prices)
    midpoint = (shape["body_top"].shift(1) + shape["body_bottom"].shift(1)) / 2.0
    return _clean(
        shape["bearish"]
        & shape["bullish"].shift(1).astype("boolean")
        & (prices["open"] <= midpoint)
        & (prices["close"] <= midpoint),
        prices,
    )


# ── Three-bar patterns ──────────────────────────────────────────────────────

def morning_star(
    prices: pd.DataFrame, max_star_body_ratio: float = 0.3, min_penetration: float = 0.5
) -> pd.Series:
    """Long down bar, small-bodied bar, then an up bar well into the first body. Catalogue id `cs_morning_star`.

    The third bar has to close at least `min_penetration` of the way up the
    first bar's body. Dropping that requirement, as many scanners do, turns the
    pattern into "any small bar between two others" and it fires constantly.
    """
    shape = anatomy(prices)
    first_bearish = shape["bearish"].shift(2).astype("boolean")
    star_small = (shape["body_ratio"].shift(1) <= max_star_body_ratio).astype("boolean")
    third_bullish = shape["bullish"]
    first_top = shape["body_top"].shift(2)
    first_bottom = shape["body_bottom"].shift(2)
    penetration = (prices["close"] - first_bottom) / (first_top - first_bottom)
    return _clean(
        first_bearish & star_small & third_bullish & (penetration >= min_penetration), prices
    )


def evening_star(
    prices: pd.DataFrame, max_star_body_ratio: float = 0.3, min_penetration: float = 0.5
) -> pd.Series:
    """Long up bar, small-bodied bar, then a down bar well into the first body. Catalogue id `cs_evening_star`."""
    shape = anatomy(prices)
    first_bullish = shape["bullish"].shift(2).astype("boolean")
    star_small = (shape["body_ratio"].shift(1) <= max_star_body_ratio).astype("boolean")
    third_bearish = shape["bearish"]
    first_top = shape["body_top"].shift(2)
    first_bottom = shape["body_bottom"].shift(2)
    penetration = (first_top - prices["close"]) / (first_top - first_bottom)
    return _clean(
        first_bullish & star_small & third_bearish & (penetration >= min_penetration), prices
    )


def three_white_soldiers(
    prices: pd.DataFrame, periods: int = 20, multiple: float = 1.0, max_upper_ratio: float = 0.25
) -> pd.Series:
    """Three long up bars, each closing above the last and opening inside its body. Catalogue id `cs_three_white_soldiers`."""
    shape = anatomy(prices)
    long_body = _long_body(prices, periods, multiple)
    condition = pd.Series(True, index=prices.index)
    for lag in (0, 1, 2):
        condition &= shape["bullish"].shift(lag).fillna(False).astype("bool")
        condition &= long_body.shift(lag).fillna(False).astype("bool")
        condition &= (shape["upper_ratio"].shift(lag) <= max_upper_ratio).fillna(False)
    rising = (prices["close"] > prices["close"].shift(1)) & (
        prices["close"].shift(1) > prices["close"].shift(2)
    )
    inside = (prices["open"] <= shape["body_top"].shift(1)) & (
        prices["open"] >= shape["body_bottom"].shift(1)
    )
    inside &= (prices["open"].shift(1) <= shape["body_top"].shift(2)) & (
        prices["open"].shift(1) >= shape["body_bottom"].shift(2)
    )
    return _clean(condition & rising & inside, prices)


def three_black_crows(
    prices: pd.DataFrame, periods: int = 20, multiple: float = 1.0, max_lower_ratio: float = 0.25
) -> pd.Series:
    """Three long down bars, each closing below the last and opening inside its body. Catalogue id `cs_three_black_crows`."""
    shape = anatomy(prices)
    long_body = _long_body(prices, periods, multiple)
    condition = pd.Series(True, index=prices.index)
    for lag in (0, 1, 2):
        condition &= shape["bearish"].shift(lag).fillna(False).astype("bool")
        condition &= long_body.shift(lag).fillna(False).astype("bool")
        condition &= (shape["lower_ratio"].shift(lag) <= max_lower_ratio).fillna(False)
    falling = (prices["close"] < prices["close"].shift(1)) & (
        prices["close"].shift(1) < prices["close"].shift(2)
    )
    inside = (prices["open"] <= shape["body_top"].shift(1)) & (
        prices["open"] >= shape["body_bottom"].shift(1)
    )
    inside &= (prices["open"].shift(1) <= shape["body_top"].shift(2)) & (
        prices["open"].shift(1) >= shape["body_bottom"].shift(2)
    )
    return _clean(condition & falling & inside, prices)


def bullish_popgun(prices: pd.DataFrame) -> pd.Series:
    """An inside bar followed by an up bar that engulfs its whole range. Catalogue id `cs_bullish_popgun`.

    Range against range here, unlike the engulfing patterns, because the
    pattern is about a compressed bar being overrun rather than about bodies.
    """
    inside = (prices["high"].shift(1) < prices["high"].shift(2)) & (
        prices["low"].shift(1) > prices["low"].shift(2)
    )
    outside = (prices["high"] > prices["high"].shift(1)) & (prices["low"] < prices["low"].shift(1))
    return _clean(inside & outside & (prices["close"] > prices["open"]), prices)


def bearish_popgun(prices: pd.DataFrame) -> pd.Series:
    """An inside bar followed by a down bar that engulfs its whole range. Catalogue id `cs_bearish_popgun`."""
    inside = (prices["high"].shift(1) < prices["high"].shift(2)) & (
        prices["low"].shift(1) > prices["low"].shift(2)
    )
    outside = (prices["high"] > prices["high"].shift(1)) & (prices["low"] < prices["low"].shift(1))
    return _clean(inside & outside & (prices["close"] < prices["open"]), prices)
