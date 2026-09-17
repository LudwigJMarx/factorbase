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
