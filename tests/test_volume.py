"""Volume-weighted measures."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from factorbase.factors._common import exponential_moving_average, simple_moving_average
from factorbase.factors.momentum import typical_price
from factorbase.factors.volume import (
    accumulation_distribution_line,
    average_turnover,
    chaikin_oscillator,
    close_location_value,
    money_flow_index,
    relative_volume,
    volume_trend,
)


def test_close_location_value_at_the_extremes() -> None:
    frame = pd.DataFrame(
        {"high": [10.0, 10.0, 10.0], "low": [8.0, 8.0, 8.0], "close": [10.0, 8.0, 9.0]}
    )
    result = close_location_value(frame)
    assert result.iloc[0] == pytest.approx(1.0)
    assert result.iloc[1] == pytest.approx(-1.0)
    assert result.iloc[2] == pytest.approx(0.0)


def test_close_location_value_of_a_rangeless_bar_is_zero() -> None:
    """No range means no location. Zero, not a division by zero."""
    frame = pd.DataFrame({"high": [10.0], "low": [10.0], "close": [10.0]})
    assert close_location_value(frame).iloc[0] == 0.0


def test_accumulation_line_is_a_running_total(wobble: pd.DataFrame) -> None:
    expected = (close_location_value(wobble) * wobble["volume"]).cumsum()
    assert np.allclose(accumulation_distribution_line(wobble), expected)


def test_accumulation_line_level_depends_on_where_history_starts(wobble: pd.DataFrame) -> None:
    """The entry warns about this. If it were not true, the warning would be noise."""
    full = accumulation_distribution_line(wobble)
    truncated = accumulation_distribution_line(wobble.iloc[100:])
    assert full.iloc[-1] != pytest.approx(truncated.iloc[-1])


def test_chaikin_oscillator_removes_the_starting_level(wobble: pd.DataFrame) -> None:
    """Differencing two averages of the line is what makes it comparable."""
    shifted = wobble.copy()
    line = accumulation_distribution_line(wobble)
    expected = exponential_moving_average(line, 3) - exponential_moving_average(line, 10)
    assert np.allclose(chaikin_oscillator(shifted).dropna(), expected.dropna())


def test_money_flow_index_weights_by_money_not_by_bar(wobble: pd.DataFrame) -> None:
    """Doubling the volume on the up bars must move the reading; on RSI it would not."""
    typical = typical_price(wobble)
    heavier = wobble.copy()
    heavier.loc[typical > typical.shift(1), "volume"] *= 3.0
    assert money_flow_index(heavier, 14).iloc[-1] > money_flow_index(wobble, 14).iloc[-1]


def test_money_flow_index_matches_the_written_sums(wobble: pd.DataFrame) -> None:
    periods, position = 14, 200
    typical = typical_price(wobble)
    flow = typical * wobble["volume"]
    change = typical.diff()
    window = slice(position - periods + 1, position + 1)
    positive = flow.iloc[window].where(change.iloc[window] > 0.0, 0.0).sum()
    negative = flow.iloc[window].where(change.iloc[window] < 0.0, 0.0).sum()
    expected = 100.0 * positive / (positive + negative)
    assert money_flow_index(wobble, periods).iloc[position] == pytest.approx(expected)


def test_unchanged_bars_count_on_neither_side() -> None:
    """A flat series has no positive and no negative flow, so the reading is 50."""
    flat = pd.DataFrame(
        {
            "high": [10.0] * 30,
            "low": [10.0] * 30,
            "close": [10.0] * 30,
            "volume": [1000.0] * 30,
        }
    )
    assert money_flow_index(flat, 14).iloc[-1] == pytest.approx(50.0)


def test_money_flow_index_stays_in_range(wobble: pd.DataFrame) -> None:
    values = money_flow_index(wobble, 14).dropna()
    assert values.min() >= 0.0
    assert values.max() <= 100.0


def test_average_turnover_is_in_currency(wobble: pd.DataFrame) -> None:
    expected = simple_moving_average(wobble["close"] * wobble["volume"], 20)
    assert np.allclose(average_turnover(wobble, 20).dropna(), expected.dropna())


def test_relative_volume_excludes_the_current_bar() -> None:
    """A spike must not dampen its own measurement. Twenty flat bars, then ten times the volume."""
    volume = pd.Series([100.0] * 20 + [1000.0])
    frame = pd.DataFrame({"volume": volume})
    assert relative_volume(frame, periods=20).iloc[-1] == pytest.approx(10.0)


def test_relative_volume_of_steady_volume_is_one(wobble: pd.DataFrame) -> None:
    steady = pd.DataFrame({"volume": pd.Series([500.0] * 60)})
    assert relative_volume(steady, 20).iloc[-1] == pytest.approx(1.0)


def test_volume_trend_reads_the_average_not_one_bar() -> None:
    """One heavy session inside a quiet stretch must not define the trend."""
    quiet = pd.DataFrame({"volume": pd.Series([100.0] * 80)})
    spiked = quiet.copy()
    spiked.iloc[-1, 0] = 10_000.0
    assert volume_trend(quiet, 20, 20).iloc[-1] == pytest.approx(0.0)
    assert volume_trend(spiked, 20, 20).iloc[-1] < 500.0


# ── Against references written outside this package ─────────────────────────


def test_money_flow_index_matches_a_hand_walked_window() -> None:
    """Five bars, arithmetic done by hand from the published definition.

    Typical prices 10, 11, 10, 12, 12 on volumes 100, 200, 300, 400, 500.
    Changes: up, down, up, unchanged.
    Positive flow over the last four bars: 11*200 + 12*400 = 7000.
    Negative flow:                          10*300         = 3000.
    MFI = 100 * 7000 / 10000 = 70.
    """
    frame = pd.DataFrame(
        {
            "high": [10.0, 11.0, 10.0, 12.0, 12.0],
            "low": [10.0, 11.0, 10.0, 12.0, 12.0],
            "close": [10.0, 11.0, 10.0, 12.0, 12.0],
            "volume": [100.0, 200.0, 300.0, 400.0, 500.0],
        }
    )
    assert money_flow_index(frame, periods=4).iloc[-1] == pytest.approx(70.0)


def test_money_flow_index_weights_a_level_not_the_size_of_the_move() -> None:
    """Two frames whose final two bars are identical in typical price, volume
    and direction, and wildly different in how far the price travelled to get
    there. The measure has to return the same number for both.

    This is the property that separates it from the RSI and the one the word
    "same construction" hides: a bar's contribution is its turnover, and the
    size of its move never enters at all, only the sign.
    """

    def frame_of(typical: list[float]) -> pd.DataFrame:
        series = pd.Series(typical)
        return pd.DataFrame(
            {
                "high": series,
                "low": series,
                "close": series,
                "volume": pd.Series(1.0, index=series.index),
            }
        )

    crawled = frame_of([99.99, 100.0, 99.0])  # rose by 0.01, then fell
    leapt = frame_of([50.0, 100.0, 99.0])  # rose by 50.00, then fell

    assert money_flow_index(crawled, periods=2).iloc[-1] == pytest.approx(
        money_flow_index(leapt, periods=2).iloc[-1]
    )
    # Positive flow 100 on the middle bar, negative flow 99 on the last.
    assert money_flow_index(crawled, periods=2).iloc[-1] == pytest.approx(
        100.0 * 100.0 / (100.0 + 99.0)
    )


def test_money_flow_index_on_flat_volume_is_a_share_of_price_levels() -> None:
    """With constant volume the turnover weight reduces to the typical price
    itself, so the reading is the share of summed price levels standing on up
    bars. Computed here from the typical prices directly."""
    rng = np.random.default_rng(5)
    n = 60
    close = pd.Series(100.0 + np.cumsum(rng.normal(0, 1.0, n)))
    frame = pd.DataFrame(
        {"high": close, "low": close, "close": close, "volume": pd.Series(1.0, index=close.index)}
    )
    periods, position = 14, 40
    window = slice(position - periods + 1, position + 1)
    levels = close.iloc[window]
    changes = close.diff().iloc[window]
    up = float(levels[changes > 0].sum())
    down = float(levels[changes < 0].sum())
    assert money_flow_index(frame, periods).iloc[position] == pytest.approx(
        100.0 * up / (up + down)
    )


def test_accumulation_line_matches_a_hand_walked_sum() -> None:
    """Three bars. CLV of the first is +1, of the second -1, of the third 0.
    Volumes 100, 200, 300, so the running total is 100, -100, -100."""
    frame = pd.DataFrame(
        {
            "high": [10.0, 10.0, 10.0],
            "low": [8.0, 8.0, 8.0],
            "close": [10.0, 8.0, 9.0],
            "volume": [100.0, 200.0, 300.0],
        }
    )
    line = accumulation_distribution_line(frame)
    assert line.tolist() == pytest.approx([100.0, -100.0, -100.0])
