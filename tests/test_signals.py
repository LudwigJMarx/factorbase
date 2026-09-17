"""Crossings, breakouts and volume events.

The recurring assertion in this file is that a signal fires once, on the bar
where something changed, and not on every bar where the resulting state holds.
That distinction is what separates a handful of entries a year from a position
held permanently, and it is the easiest thing in this package to get wrong.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from factorbase import compute
from factorbase.factors.signals import (
    accumulation_day,
    bollinger_resistance,
    bollinger_support,
    buying_climax,
    darvas_breakout,
    death_cross,
    distribution_day,
    expansion_breakdown,
    expansion_breakout,
    gap_down,
    gap_up,
    golden_cross,
    ma_resistance,
    ma_support,
    macd_cross_down,
    macd_cross_up,
    new_high,
    new_low,
    pivot_breakout,
    pivot_high,
    pivot_low,
    price_crosses_above_ma,
    price_crosses_below_ma,
    selling_climax,
    stochastic_cross_down,
    stochastic_cross_up,
    volume_peak,
)


def series_frame(close: list[float]) -> pd.DataFrame:
    """A frame whose bars have a small symmetric range around each close."""
    values = pd.Series(close, index=pd.bdate_range("2020-01-01", periods=len(close)))
    return pd.DataFrame(
        {
            "open": values.shift(1).fillna(values.iloc[0]),
            "high": values + 0.5,
            "low": values - 0.5,
            "close": values,
            "volume": pd.Series(1_000_000.0, index=values.index),
        }
    )


# ── Events fire once ────────────────────────────────────────────────────────


def test_price_cross_fires_once_not_every_bar_above() -> None:
    frame = series_frame([100.0] * 30 + [110.0] * 30)
    fired = price_crosses_above_ma(frame, periods=20, method="sma")
    assert fired.sum() == 1


def test_price_cross_down_fires_once() -> None:
    frame = series_frame([110.0] * 30 + [100.0] * 30)
    assert price_crosses_below_ma(frame, periods=20, method="sma").sum() == 1


def test_new_high_fires_once_per_advance_not_on_every_bar() -> None:
    """A steady climb is at a new high every bar. The event is the first of them."""
    climbing = series_frame(list(np.linspace(100.0, 200.0, 120)))
    at_high = climbing["close"] >= climbing["close"].rolling(60, min_periods=60).max()
    assert at_high.sum() > 50
    assert new_high(climbing, periods=60).sum() == 1


def test_new_low_fires_once_per_decline() -> None:
    falling = series_frame(list(np.linspace(200.0, 100.0, 120)))
    assert new_low(falling, periods=60).sum() == 1


def test_volume_peak_fires_once_inside_a_heavy_stretch() -> None:
    frame = series_frame([100.0] * 80)
    frame.loc[frame.index[60:70], "volume"] = 9_000_000.0
    assert volume_peak(frame, periods=50).sum() == 1


# ── Moving-average crossings ────────────────────────────────────────────────


def test_golden_cross_and_death_cross_are_mirrors() -> None:
    up = series_frame([100.0] * 60 + list(np.linspace(100.0, 200.0, 120)))
    down = series_frame([200.0] * 60 + list(np.linspace(200.0, 100.0, 120)))
    assert golden_cross(up, 20, 50).sum() == 1
    assert death_cross(up, 20, 50).sum() == 0
    assert death_cross(down, 20, 50).sum() == 1


def test_ma_support_needs_both_the_touch_and_the_hold() -> None:
    """Closing above the average is not a test of support; closing below is a break."""
    base = [100.0] * 60
    frame = series_frame(base + [101.0])
    average = frame["close"].rolling(50, min_periods=50).mean()
    untouched = frame.copy()
    untouched.loc[untouched.index[-1], "low"] = float(average.iloc[-1]) + 5.0
    assert not bool(ma_support(untouched, periods=50).iloc[-1])

    touched = frame.copy()
    touched.loc[touched.index[-1], "low"] = float(average.iloc[-1]) - 1.0
    assert bool(ma_support(touched, periods=50).iloc[-1])

    broken = touched.copy()
    broken.loc[broken.index[-1], "close"] = float(average.iloc[-1]) - 0.5
    assert not bool(ma_support(broken, periods=50).iloc[-1])


def test_ma_resistance_is_the_mirror_of_support() -> None:
    frame = series_frame([100.0] * 60 + [99.0])
    average = frame["close"].rolling(50, min_periods=50).mean()
    frame.loc[frame.index[-1], "high"] = float(average.iloc[-1]) + 1.0
    assert bool(ma_resistance(frame, periods=50).iloc[-1])


# ── Bollinger ───────────────────────────────────────────────────────────────


def test_bollinger_support_needs_a_recovery_into_the_band(wobble: pd.DataFrame) -> None:
    from factorbase.factors.volatility import bollinger_bands

    bands = bollinger_bands(wobble, 20, 2.0)
    fired = bollinger_support(wobble, 20, 2.0)
    assert fired.sum() > 0
    assert (wobble["close"][fired] > bands["lower"][fired]).all()
    assert (wobble["low"][fired] <= bands["lower"][fired]).all()


def test_bollinger_resistance_needs_a_rejection(wobble: pd.DataFrame) -> None:
    from factorbase.factors.volatility import bollinger_bands

    bands = bollinger_bands(wobble, 20, 2.0)
    fired = bollinger_resistance(wobble, 20, 2.0)
    assert fired.sum() > 0
    assert (wobble["close"][fired] < bands["upper"][fired]).all()


# ── Gaps ────────────────────────────────────────────────────────────────────


def test_gap_up_measures_against_the_previous_high_not_close() -> None:
    """An open above yesterday's close but inside its range is not a gap."""
    frame = pd.DataFrame(
        {
            "open": [100.0, 103.0],
            "high": [105.0, 106.0],
            "low": [99.0, 102.0],
            "close": [100.0, 105.0],
        },
        index=pd.bdate_range("2024-01-01", periods=2),
    )
    assert frame["open"].iloc[1] > frame["close"].iloc[0]
    assert not bool(gap_up(frame, minimum_percent=1.0).iloc[-1])

    frame.loc[frame.index[1], "open"] = 110.0
    assert bool(gap_up(frame, minimum_percent=1.0).iloc[-1])


def test_gap_down_measures_against_the_previous_low() -> None:
    frame = pd.DataFrame(
        {
            "open": [100.0, 90.0],
            "high": [105.0, 92.0],
            "low": [99.0, 88.0],
            "close": [100.0, 89.0],
        },
        index=pd.bdate_range("2024-01-01", periods=2),
    )
    assert bool(gap_down(frame, minimum_percent=1.0).iloc[-1])


# ── Breakouts ───────────────────────────────────────────────────────────────


def test_expansion_breakout_rejects_a_narrow_bar_over_the_high() -> None:
    """Same close above the same prior high. Only the bar's width differs."""
    base = series_frame([100.0] * 40 + [101.0])
    narrow = base.copy()
    narrow.loc[narrow.index[-1], ["high", "low"]] = [101.1, 100.9]
    assert not bool(expansion_breakout(narrow, periods=20).iloc[-1])

    wide = base.copy()
    wide.loc[wide.index[-1], ["high", "low"]] = [101.5, 95.0]
    assert bool(expansion_breakout(wide, periods=20).iloc[-1])


def test_expansion_breakdown_is_the_mirror() -> None:
    base = series_frame([100.0] * 40 + [99.0])
    base.loc[base.index[-1], ["high", "low"]] = [105.0, 98.5]
    assert bool(expansion_breakdown(base, periods=20).iloc[-1])


def test_darvas_breakout_requires_an_actual_box() -> None:
    """A close above a 20-bar high at the end of a vertical run is not a box breakout."""
    boxed = series_frame([100.0] * 30 + [102.0])
    assert bool(darvas_breakout(boxed, periods=20, box_tolerance=3.0).iloc[-1])

    vertical = series_frame(list(np.linspace(100.0, 200.0, 30)) + [205.0])
    assert not bool(darvas_breakout(vertical, periods=20, box_tolerance=3.0).iloc[-1])


# ── Pivots ──────────────────────────────────────────────────────────────────


def test_pivot_high_marks_the_local_extreme() -> None:
    frame = series_frame(
        [100.0, 101.0, 102.0, 103.0, 104.0, 110.0, 104.0, 103.0, 102.0, 101.0, 100.0]
    )
    assert bool(pivot_high(frame, left=5, right=5).iloc[5])


def test_pivot_low_marks_the_local_extreme() -> None:
    frame = series_frame(
        [110.0, 109.0, 108.0, 107.0, 106.0, 100.0, 106.0, 107.0, 108.0, 109.0, 110.0]
    )
    assert bool(pivot_low(frame, left=5, right=5).iloc[5])


def test_pivot_high_reads_ahead_and_the_entry_says_so() -> None:
    """Truncating the series after the pivot bar removes the pivot. That is the look-ahead."""
    full = series_frame(
        [100.0, 101.0, 102.0, 103.0, 104.0, 110.0, 104.0, 103.0, 102.0, 101.0, 100.0]
    )
    truncated = full.iloc[:6]
    assert bool(pivot_high(full, 5, 5).iloc[5])
    assert pivot_high(truncated, 5, 5).sum() == 0


def test_pivot_breakout_uses_only_confirmed_pivots() -> None:
    closes = [100.0, 101.0, 102.0, 103.0, 104.0, 110.0] + [104.0] * 8 + [115.0]
    frame = series_frame(closes)
    fired = pivot_breakout(frame, left=5, right=5)
    assert fired.sum() == 1
    assert fired.iloc[-1]


# ── Oscillator crossings ────────────────────────────────────────────────────


def test_macd_crossings_are_events_and_are_mutually_exclusive(wobble: pd.DataFrame) -> None:
    up = macd_cross_up(wobble)
    down = macd_cross_down(wobble)
    assert up.sum() > 0 and down.sum() > 0
    assert not (up & down).any()


def test_stochastic_cross_up_respects_its_threshold(wobble: pd.DataFrame) -> None:
    """Without the threshold the same rule fires several times as often."""
    gated = stochastic_cross_up(wobble, threshold=20.0)
    ungated = stochastic_cross_up(wobble, threshold=100.0)
    assert gated.sum() < ungated.sum()
    assert (gated <= ungated).all()


def test_stochastic_cross_down_respects_its_threshold(wobble: pd.DataFrame) -> None:
    gated = stochastic_cross_down(wobble, threshold=80.0)
    ungated = stochastic_cross_down(wobble, threshold=0.0)
    assert gated.sum() < ungated.sum()


# ── Volume events ───────────────────────────────────────────────────────────


def test_accumulation_day_requires_a_strong_close() -> None:
    """Up on heavy volume, but giving it back before the close, is not accumulation."""
    frame = series_frame([100.0] * 60 + [102.0])
    last = frame.index[-1]
    frame.loc[last, "volume"] = 5_000_000.0
    frame.loc[last, ["high", "low"]] = [105.0, 99.0]

    frame.loc[last, "close"] = 104.5
    assert bool(accumulation_day(frame, periods=50).iloc[-1])

    frame.loc[last, "close"] = 100.5
    assert not bool(accumulation_day(frame, periods=50).iloc[-1])


def test_distribution_day_compares_volume_with_the_previous_bar() -> None:
    frame = series_frame([100.0] * 10 + [99.0])
    frame.loc[frame.index[-1], "volume"] = 1_500_000.0
    assert bool(distribution_day(frame).iloc[-1])

    frame.loc[frame.index[-1], "volume"] = 500_000.0
    assert not bool(distribution_day(frame).iloc[-1])


def test_a_small_fall_is_not_a_distribution_day() -> None:
    frame = series_frame([100.0] * 10 + [99.95])
    frame.loc[frame.index[-1], "volume"] = 1_500_000.0
    assert not bool(distribution_day(frame, minimum_fall=0.2).iloc[-1])


def test_buying_climax_needs_all_four_conditions() -> None:
    closes = list(np.linspace(100.0, 160.0, 60)) + [170.0]
    frame = series_frame(closes)
    last = frame.index[-1]
    frame.loc[last, "volume"] = 9_000_000.0
    frame.loc[last, ["high", "low"]] = [185.0, 165.0]

    frame.loc[last, "close"] = 168.0
    assert bool(buying_climax(frame).iloc[-1])

    frame.loc[last, "close"] = 184.0
    assert not bool(buying_climax(frame).iloc[-1])


def test_selling_climax_is_the_mirror() -> None:
    closes = list(np.linspace(200.0, 130.0, 60)) + [120.0]
    frame = series_frame(closes)
    last = frame.index[-1]
    frame.loc[last, "volume"] = 9_000_000.0
    frame.loc[last, ["high", "low"]] = [128.0, 108.0]
    frame.loc[last, "close"] = 126.0
    assert bool(selling_climax(frame).iloc[-1])


def test_a_random_walk_produces_no_climax(wobble: pd.DataFrame) -> None:
    """Stated in the entry. A busy session is not an exhaustion."""
    assert buying_climax(wobble).sum() == 0


def test_every_signal_entry_returns_booleans(wobble: pd.DataFrame) -> None:
    from factorbase import default_catalog
    from factorbase.schema import Kind

    signals = default_catalog().of_kind(Kind.SIGNAL)
    assert len(signals) == 51
    for factor in signals:
        result = compute(factor.id, wobble)
        assert result.dtype == bool, factor.id
        assert len(result) == len(wobble), factor.id
