"""Crossings, breakouts and volume events.

Every function returns a boolean Series. Two conventions hold throughout and
are the difference between a signal that can be backtested and one that cannot:

A crossing fires on the bar where the relation changed, not on every bar where
it holds. "Price is above its average" is a state and belongs in a filter;
"price crossed above its average today" is an event and belongs here. Mixing
the two turns a handful of entries a year into a position held permanently.

Everything is evaluated on the bar's own close, using data available at that
close. Nothing reads a future bar.
"""

from __future__ import annotations

import pandas as pd

from ._common import moving_average, require_columns, simple_moving_average
from .momentum import macd as macd_line
from .momentum import macd_signal, stochastic_slow_d, stochastic_slow_k
from .volatility import atr, bollinger_bands


def _crossed_above(series: pd.Series, reference: pd.Series) -> pd.Series:
    """True on the bar where `series` moved from at-or-below to above `reference`."""
    now = series > reference
    before = (series.shift(1) <= reference.shift(1)) & series.shift(1).notna()
    return (now & before).fillna(False).astype("bool")


def _crossed_below(series: pd.Series, reference: pd.Series) -> pd.Series:
    now = series < reference
    before = (series.shift(1) >= reference.shift(1)) & series.shift(1).notna()
    return (now & before).fillna(False).astype("bool")


def _became(condition: pd.Series) -> pd.Series:
    """True on the bar where `condition` turned from false to true.

    The cast to a real boolean dtype before shifting is not decoration. In
    pandas 3 a boolean Series shifted by one becomes object dtype, holding
    Python bools, and `~` on that inverts the underlying integer: ~True is -2,
    which is truthy. Every "is this new" signal then fires on every bar, and
    the result still has dtype bool at the end, so nothing downstream notices.
    """
    now = condition.fillna(False).astype("bool")
    before = now.shift(1, fill_value=False).astype("bool")
    return now & ~before


# ── Moving-average events ───────────────────────────────────────────────────


def price_crosses_above_ma(
    prices: pd.DataFrame, periods: int = 200, method: str = "sma"
) -> pd.Series:
    """Close moved above its own moving average today. Catalogue id `price_crosses_above_ma`."""
    require_columns(prices, ("close",), "price_crosses_above_ma")
    return _crossed_above(prices["close"], moving_average(prices["close"], periods, method))


def price_crosses_below_ma(
    prices: pd.DataFrame, periods: int = 200, method: str = "sma"
) -> pd.Series:
    """Close moved below its own moving average today. Catalogue id `price_crosses_below_ma`."""
    require_columns(prices, ("close",), "price_crosses_below_ma")
    return _crossed_below(prices["close"], moving_average(prices["close"], periods, method))


def golden_cross(
    prices: pd.DataFrame, fast_periods: int = 50, slow_periods: int = 200, method: str = "sma"
) -> pd.Series:
    """Fast average moved above the slow one today. Catalogue id `golden_cross`."""
    require_columns(prices, ("close",), "golden_cross")
    fast = moving_average(prices["close"], fast_periods, method)
    slow = moving_average(prices["close"], slow_periods, method)
    return _crossed_above(fast, slow)


def death_cross(
    prices: pd.DataFrame, fast_periods: int = 50, slow_periods: int = 200, method: str = "sma"
) -> pd.Series:
    """Fast average moved below the slow one today. Catalogue id `death_cross`."""
    require_columns(prices, ("close",), "death_cross")
    fast = moving_average(prices["close"], fast_periods, method)
    slow = moving_average(prices["close"], slow_periods, method)
    return _crossed_below(fast, slow)


def ma_support(
    prices: pd.DataFrame, periods: int = 50, method: str = "sma", tolerance: float = 1.0
) -> pd.Series:
    """Traded down to the average and closed back above it. Catalogue id `ma_support`.

    Both halves are required. A bar that merely closes above the average is not
    a test of support, and a bar that closes below it is a break, not a hold.
    """
    require_columns(prices, ("low", "close"), "ma_support")
    average = moving_average(prices["close"], periods, method)
    touched = prices["low"] <= average * (1.0 + tolerance / 100.0)
    held = prices["close"] > average
    return (touched & held).fillna(False).astype("bool")


def ma_resistance(
    prices: pd.DataFrame, periods: int = 50, method: str = "sma", tolerance: float = 1.0
) -> pd.Series:
    """Traded up to the average and closed back below it. Catalogue id `ma_resistance`."""
    require_columns(prices, ("high", "close"), "ma_resistance")
    average = moving_average(prices["close"], periods, method)
    touched = prices["high"] >= average * (1.0 - tolerance / 100.0)
    rejected = prices["close"] < average
    return (touched & rejected).fillna(False).astype("bool")


# ── Bollinger events ────────────────────────────────────────────────────────


def bollinger_support(
    prices: pd.DataFrame, periods: int = 20, deviations: float = 2.0
) -> pd.Series:
    """Traded below the lower band and closed back inside. Catalogue id `bollinger_support`."""
    bands = bollinger_bands(prices, periods, deviations)
    pierced = prices["low"] <= bands["lower"]
    recovered = prices["close"] > bands["lower"]
    return (pierced & recovered).fillna(False).astype("bool")


def bollinger_resistance(
    prices: pd.DataFrame, periods: int = 20, deviations: float = 2.0
) -> pd.Series:
    """Traded above the upper band and closed back inside. Catalogue id `bollinger_resistance`."""
    bands = bollinger_bands(prices, periods, deviations)
    pierced = prices["high"] >= bands["upper"]
    rejected = prices["close"] < bands["upper"]
    return (pierced & rejected).fillna(False).astype("bool")


# ── Range events ────────────────────────────────────────────────────────────


def new_high(prices: pd.DataFrame, periods: int = 250) -> pd.Series:
    """Close is the highest of the last n bars, and was not yesterday. Catalogue id `new_high`.

    The second half is what makes it an event. Without it a stock in a steady
    advance reports a new high on most bars, and a backtest reading that as an
    entry is permanently in the position.
    """
    require_columns(prices, ("close",), "new_high")
    highest = prices["close"].rolling(periods, min_periods=periods).max()
    return _became((prices["close"] >= highest) & highest.notna())


def new_low(prices: pd.DataFrame, periods: int = 250) -> pd.Series:
    """Close is the lowest of the last n bars, and was not yesterday. Catalogue id `new_low`."""
    require_columns(prices, ("close",), "new_low")
    lowest = prices["close"].rolling(periods, min_periods=periods).min()
    return _became((prices["close"] <= lowest) & lowest.notna())


def gap_up(prices: pd.DataFrame, minimum_percent: float = 1.0) -> pd.Series:
    """Opened above the previous bar's high by at least the stated margin. Catalogue id `gap_up`.

    Measured open against previous high, not open against previous close. An
    open above the previous close but inside its range is not a gap: the price
    traded there yesterday.
    """
    require_columns(prices, ("open", "high"), "gap_up")
    threshold = prices["high"].shift(1) * (1.0 + minimum_percent / 100.0)
    return (prices["open"] > threshold).fillna(False).astype("bool")


def gap_down(prices: pd.DataFrame, minimum_percent: float = 1.0) -> pd.Series:
    """Opened below the previous bar's low by at least the stated margin.

    Catalogue id `gap_down`.
    """
    require_columns(prices, ("open", "low"), "gap_down")
    threshold = prices["low"].shift(1) * (1.0 - minimum_percent / 100.0)
    return (prices["open"] < threshold).fillna(False).astype("bool")


def expansion_breakout(
    prices: pd.DataFrame, periods: int = 20, atr_periods: int = 14, range_multiple: float = 1.5
) -> pd.Series:
    """Closed above the n-bar high on a bar wider than usual. Catalogue id `expansion_breakout`.

    The width requirement is the filter. A close a tick above a prior high on a
    narrow bar is noise; the same close on a bar one and a half times the
    average true range is a different event, and separating them is the only
    reason to prefer this over a plain new high.
    """
    require_columns(prices, ("high", "low", "close"), "expansion_breakout")
    prior_high = prices["high"].shift(1).rolling(periods, min_periods=periods).max()
    wide = (prices["high"] - prices["low"]) >= range_multiple * atr(prices, atr_periods)
    return ((prices["close"] > prior_high) & wide).fillna(False).astype("bool")


def expansion_breakdown(
    prices: pd.DataFrame, periods: int = 20, atr_periods: int = 14, range_multiple: float = 1.5
) -> pd.Series:
    """Closed below the n-bar low on a bar wider than usual. Catalogue id `expansion_breakdown`."""
    require_columns(prices, ("high", "low", "close"), "expansion_breakdown")
    prior_low = prices["low"].shift(1).rolling(periods, min_periods=periods).min()
    wide = (prices["high"] - prices["low"]) >= range_multiple * atr(prices, atr_periods)
    return ((prices["close"] < prior_low) & wide).fillna(False).astype("bool")


def darvas_breakout(
    prices: pd.DataFrame, periods: int = 20, box_tolerance: float = 3.0
) -> pd.Series:
    """Closed out of a box the price had been confined to. Catalogue id `darvas_breakout`.

    The box is the last n bars' high and low, and it only counts as a box if the
    two are within `box_tolerance` percent of each other, i.e. the price has
    actually been going nowhere. Without that check every close above an n-bar
    high qualifies, including one at the end of a vertical advance, where there
    was no box at all.
    """
    require_columns(prices, ("high", "low", "close"), "darvas_breakout")
    box_high = prices["high"].shift(1).rolling(periods, min_periods=periods).max()
    box_low = prices["low"].shift(1).rolling(periods, min_periods=periods).min()
    is_box = (box_high - box_low) / box_low * 100.0 <= box_tolerance
    return ((prices["close"] > box_high) & is_box).fillna(False).astype("bool")


def pivot_high(prices: pd.DataFrame, left: int = 5, right: int = 5) -> pd.Series:
    """A bar whose high exceeds the `left` bars before and `right` bars after it.

    Catalogue id `pivot_high`.

    Confirmed only once the bars to its right exist, so the Series is marked
    True on the pivot bar itself and that value is not knowable until `right`
    bars later. Anything backtesting on it must shift by `right`, and the entry
    says so rather than leaving a look-ahead in place for the reader to find.
    """
    require_columns(prices, ("high",), "pivot_high")
    window = left + right + 1
    rolling_max = prices["high"].rolling(window, min_periods=window).max()
    centred = rolling_max.shift(-right)
    return (prices["high"] >= centred).fillna(False).astype("bool")


def pivot_low(prices: pd.DataFrame, left: int = 5, right: int = 5) -> pd.Series:
    """A bar whose low undercuts the `left` bars before and `right` bars after it.

    Catalogue id `pivot_low`.
    """
    require_columns(prices, ("low",), "pivot_low")
    window = left + right + 1
    rolling_min = prices["low"].rolling(window, min_periods=window).min()
    centred = rolling_min.shift(-right)
    return (prices["low"] <= centred).fillna(False).astype("bool")


def pivot_breakout(prices: pd.DataFrame, left: int = 5, right: int = 5) -> pd.Series:
    """Closed above the most recent confirmed pivot high. Catalogue id `pivot_breakout`.

    Uses only pivots that were already confirmed, which means the level is
    `right` bars stale by construction. That staleness is the price of not
    looking ahead, and it is what separates this from `pivot_high`.
    """
    require_columns(prices, ("high", "close"), "pivot_breakout")
    confirmed = pivot_high(prices, left, right).shift(right).fillna(False)
    # Both the flag and the high are shifted. The flag says "a pivot was
    # confirmed `right` bars ago"; the level has to be that pivot's own high,
    # not the high of the bar on which it became knowable. Shifting only the
    # flag produces a breakout over a price the pivot never reached.
    level = prices["high"].shift(right).where(confirmed).ffill()
    crossed = (prices["close"] > level) & (prices["close"].shift(1) <= level.shift(1))
    return crossed.fillna(False).astype("bool")


# ── Oscillator events ───────────────────────────────────────────────────────


def macd_cross_up(
    prices: pd.DataFrame,
    fast_periods: int = 12,
    slow_periods: int = 26,
    signal_periods: int = 9,
) -> pd.Series:
    """MACD line crossed above its signal line today. Catalogue id `macd_cross_up`."""
    line = macd_line(prices, fast_periods, slow_periods)
    signal = macd_signal(prices, fast_periods, slow_periods, signal_periods)
    return _crossed_above(line, signal)


def macd_cross_down(
    prices: pd.DataFrame,
    fast_periods: int = 12,
    slow_periods: int = 26,
    signal_periods: int = 9,
) -> pd.Series:
    """MACD line crossed below its signal line today. Catalogue id `macd_cross_down`."""
    line = macd_line(prices, fast_periods, slow_periods)
    signal = macd_signal(prices, fast_periods, slow_periods, signal_periods)
    return _crossed_below(line, signal)


def stochastic_cross_up(
    prices: pd.DataFrame, periods: int = 14, smoothing: int = 3, threshold: float = 20.0
) -> pd.Series:
    """Slow %K crossed above %D while both were still low. Catalogue id `stochastic_cross_up`.

    The threshold is the point. A crossing at 70 is a crossing; a crossing
    below 20 is the one the method is about, and leaving the threshold out
    produces several times as many firings, most of them mid-range.
    """
    percent_k = stochastic_slow_k(prices, periods, smoothing)
    percent_d = stochastic_slow_d(prices, periods, smoothing, smoothing)
    return (_crossed_above(percent_k, percent_d) & (percent_d < threshold)).fillna(False)


def stochastic_cross_down(
    prices: pd.DataFrame, periods: int = 14, smoothing: int = 3, threshold: float = 80.0
) -> pd.Series:
    """Slow %K crossed below %D while both were still high. Catalogue id `stochastic_cross_down`."""
    percent_k = stochastic_slow_k(prices, periods, smoothing)
    percent_d = stochastic_slow_d(prices, periods, smoothing, smoothing)
    return (_crossed_below(percent_k, percent_d) & (percent_d > threshold)).fillna(False)


# ── Volume events ───────────────────────────────────────────────────────────


def accumulation_day(
    prices: pd.DataFrame,
    periods: int = 50,
    volume_multiple: float = 1.0,
    close_position: float = 0.6,
) -> pd.Series:
    """Up day on above-average volume that closed in the upper part of its range.

    Catalogue id `accumulation_day`.

    The closing position is the part usually left out. A bar that rises on
    heavy volume and then gives most of it back before the close is not
    accumulation, and without the position test it counts as one.
    """
    require_columns(prices, ("high", "low", "close", "volume"), "accumulation_day")
    average_volume = simple_moving_average(prices["volume"].shift(1), periods)
    span = (prices["high"] - prices["low"]).where(prices["high"] != prices["low"])
    position = (prices["close"] - prices["low"]) / span
    return (
        (
            (prices["close"] > prices["close"].shift(1))
            & (prices["volume"] >= volume_multiple * average_volume)
            & (position >= close_position)
        )
        .fillna(False)
        .astype("bool")
    )


def distribution_day(prices: pd.DataFrame, minimum_fall: float = 0.2) -> pd.Series:
    """Down day of at least the stated size on volume above the previous bar's.

    Catalogue id `distribution_day`.

    Volume against the previous bar, not against an average. That is the
    convention the term comes from, and it is deliberately easier to satisfy:
    counting distribution days is a tally over weeks, so the individual bar is
    allowed to be a weak signal.
    """
    require_columns(prices, ("close", "volume"), "distribution_day")
    fall = (prices["close"] / prices["close"].shift(1) - 1.0) * 100.0
    return (
        ((fall <= -minimum_fall) & (prices["volume"] > prices["volume"].shift(1)))
        .fillna(False)
        .astype("bool")
    )


def volume_peak(prices: pd.DataFrame, periods: int = 250) -> pd.Series:
    """Volume is the highest of the last n bars, and was not yesterday.

    Catalogue id `volume_peak`.
    """
    require_columns(prices, ("volume",), "volume_peak")
    highest = prices["volume"].rolling(periods, min_periods=periods).max()
    return _became((prices["volume"] >= highest) & highest.notna())


def buying_climax(
    prices: pd.DataFrame,
    advance_periods: int = 50,
    minimum_advance: float = 25.0,
    volume_periods: int = 50,
    volume_multiple: float = 2.0,
    atr_periods: int = 14,
    range_multiple: float = 2.0,
    close_position: float = 0.4,
) -> pd.Series:
    """An extended advance ending in a wide, heavy bar that closed poorly.

    Catalogue id `buying_climax`.

    Four conditions, all required: the advance happened, the bar is unusually
    wide, the volume is unusually heavy, and the close gave most of the bar's
    gain back. The last one is what makes it a climax rather than a strong day.
    """
    require_columns(prices, ("high", "low", "close", "volume"), "buying_climax")
    advanced = (
        prices["close"] / prices["close"].shift(advance_periods) - 1.0
    ) * 100.0 >= minimum_advance
    heavy = prices["volume"] >= volume_multiple * simple_moving_average(
        prices["volume"].shift(1), volume_periods
    )
    span = (prices["high"] - prices["low"]).where(prices["high"] != prices["low"])
    wide = span >= range_multiple * atr(prices, atr_periods)
    poor_close = (prices["close"] - prices["low"]) / span <= close_position
    return (advanced & heavy & wide & poor_close).fillna(False).astype("bool")


def selling_climax(
    prices: pd.DataFrame,
    decline_periods: int = 50,
    minimum_decline: float = 25.0,
    volume_periods: int = 50,
    volume_multiple: float = 2.0,
    atr_periods: int = 14,
    range_multiple: float = 2.0,
    close_position: float = 0.6,
) -> pd.Series:
    """An extended decline ending in a wide, heavy bar that closed well.

    Catalogue id `selling_climax`.
    """
    require_columns(prices, ("high", "low", "close", "volume"), "selling_climax")
    declined = (
        prices["close"] / prices["close"].shift(decline_periods) - 1.0
    ) * 100.0 <= -minimum_decline
    heavy = prices["volume"] >= volume_multiple * simple_moving_average(
        prices["volume"].shift(1), volume_periods
    )
    span = (prices["high"] - prices["low"]).where(prices["high"] != prices["low"])
    wide = span >= range_multiple * atr(prices, atr_periods)
    strong_close = (prices["close"] - prices["low"]) / span >= close_position
    return (declined & heavy & wide & strong_close).fillna(False).astype("bool")


def gilligans_island_buy(
    prices: pd.DataFrame, periods: int = 40, close_position: float = 0.5
) -> pd.Series:
    """Gap down to a new low, then a close back above the open.

    Catalogue id `gilligans_island_buy`.

    Cooper's setup, and the two halves are what make it one: the open has to
    be below the prior window's low, so the gap reaches a price nobody traded
    at in two months, and the close has to be at or above that open while
    still sitting in the lower part of the bar. A bar that gaps down and keeps
    falling is not this; a bar that gaps down and closes at its high is a
    different and more obvious event.
    """
    require_columns(prices, ("open", "high", "low", "close"), "gilligans_island_buy")
    prior_low = prices["low"].shift(1).rolling(periods, min_periods=periods).min()
    span = (prices["high"] - prices["low"]).where(prices["high"] != prices["low"])
    position = (prices["close"] - prices["low"]) / span
    gapped = prices["open"] < prior_low
    held = prices["close"] >= prices["open"]
    return (gapped & held & (position <= close_position)).fillna(False).astype("bool")


def gilligans_island_sell(
    prices: pd.DataFrame, periods: int = 40, close_position: float = 0.5
) -> pd.Series:
    """Gap up to a new high, then a close back below the open.

    Catalogue id `gilligans_island_sell`.

    The mirror of the buy setup.
    """
    require_columns(prices, ("open", "high", "low", "close"), "gilligans_island_sell")
    prior_high = prices["high"].shift(1).rolling(periods, min_periods=periods).max()
    span = (prices["high"] - prices["low"]).where(prices["high"] != prices["low"])
    position = (prices["close"] - prices["low"]) / span
    gapped = prices["open"] > prior_high
    rejected = prices["close"] <= prices["open"]
    return (gapped & rejected & (position >= 1.0 - close_position)).fillna(False).astype("bool")
