"""Return, position in the range, and bar-counting measures."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from factorbase.errors import MissingInputError
from factorbase.factors.performance import (
    annualised_performance,
    bars_of_history,
    daily_performance,
    distance_to_high,
    distance_to_low,
    inside_bars,
    performance,
    price,
    winning_days,
)


def test_price_is_the_close(wobble: pd.DataFrame) -> None:
    assert price(wobble).equals(wobble["close"])


def test_performance_is_a_percentage(ramp: pd.DataFrame) -> None:
    before, now = ramp["close"].iloc[150], ramp["close"].iloc[250]
    assert performance(ramp, periods=100).iloc[250] == pytest.approx((now / before - 1.0) * 100.0)


def test_adjusted_performance_raises_rather_than_falling_back(wobble: pd.DataFrame) -> None:
    """A total-return factor quietly reporting a price return is a silent several percent a year."""
    with pytest.raises(MissingInputError) as caught:
        performance(wobble, periods=10, adjusted=True)
    assert caught.value.missing == ("adjusted_close",)


def test_adjusted_performance_uses_the_adjusted_column(wobble: pd.DataFrame) -> None:
    frame = wobble.copy()
    frame["adjusted_close"] = frame["close"] * 0.9 ** (np.arange(len(frame)) / 250.0)
    plain = performance(frame, periods=250, adjusted=False).iloc[-1]
    adjusted = performance(frame, periods=250, adjusted=True).iloc[-1]
    assert plain != pytest.approx(adjusted)


def test_daily_performance_is_the_one_bar_return(wobble: pd.DataFrame) -> None:
    expected = (wobble["close"].iloc[-1] / wobble["close"].iloc[-2] - 1.0) * 100.0
    assert daily_performance(wobble).iloc[-1] == pytest.approx(expected)


def test_annualised_performance_is_geometric_not_arithmetic() -> None:
    """Plus fifty then minus fifty: zero on average, -13.4 percent a year compounded."""
    dates = pd.bdate_range("2020-01-01", periods=501)
    values = np.r_[
        100.0 * 1.5 ** (np.arange(251) / 250.0),
        150.0 * 0.5 ** (np.arange(1, 251) / 250.0),
    ]
    frame = pd.DataFrame({"close": values}, index=dates)
    result = annualised_performance(frame, periods=500, trading_days=250).iloc[-1]
    assert result == pytest.approx((0.75**0.5 - 1.0) * 100.0)
    assert result == pytest.approx(-13.397, abs=0.01)


def test_annualised_performance_of_a_known_rate() -> None:
    dates = pd.bdate_range("2015-01-01", periods=800)
    frame = pd.DataFrame({"close": 100.0 * 1.10 ** (np.arange(800) / 250.0)}, index=dates)
    assert annualised_performance(frame, periods=750).iloc[-1] == pytest.approx(10.0)


def test_winning_days_counts_unchanged_bars_as_losses() -> None:
    """Stated in the entry. On thin instruments it moves the reading by several points."""
    close = pd.Series([10.0, 11.0, 11.0, 12.0, 12.0, 12.0])
    frame = pd.DataFrame({"close": close})
    assert winning_days(frame, periods=5).iloc[-1] == pytest.approx(40.0)


def test_winning_days_of_an_unbroken_advance_is_one_hundred(ramp: pd.DataFrame) -> None:
    assert winning_days(ramp, periods=100).iloc[-1] == pytest.approx(100.0)


def test_distance_to_high_is_zero_at_a_new_high(ramp: pd.DataFrame) -> None:
    assert distance_to_high(ramp, periods=250).iloc[-1] == pytest.approx(0.0)


def test_distance_to_high_reads_closes_not_intraday_highs() -> None:
    """One bad print in the high column must not hold the reading down for a year."""
    close = pd.Series([100.0] * 60)
    frame = pd.DataFrame({"close": close, "high": close.copy()})
    frame.loc[10, "high"] = 500.0
    assert distance_to_high(frame, periods=50).iloc[-1] == pytest.approx(0.0)


def test_distance_to_low_is_never_negative(wobble: pd.DataFrame) -> None:
    values = distance_to_low(wobble, periods=100).dropna()
    assert values.min() >= 0.0


def test_inside_bars_finds_the_contained_sessions() -> None:
    frame = pd.DataFrame(
        {"high": [10.0, 9.5, 9.4, 12.0, 11.0], "low": [8.0, 8.5, 8.6, 7.0, 7.5]}
    )
    assert inside_bars(frame, periods=4).iloc[-1] == pytest.approx(3.0)


def test_a_wider_bar_is_not_an_inside_bar() -> None:
    frame = pd.DataFrame({"high": [10.0, 11.0, 12.0], "low": [8.0, 7.0, 6.0]})
    assert inside_bars(frame, periods=2).iloc[-1] == pytest.approx(0.0)


def test_bars_of_history_counts_traded_rows(wobble: pd.DataFrame) -> None:
    assert bars_of_history(wobble).iloc[-1] == float(len(wobble))
    assert bars_of_history(wobble).iloc[0] == 1.0


def test_bars_of_history_skips_gaps(wobble: pd.DataFrame) -> None:
    """A row with no close is not a traded bar, and must not be counted as one."""
    holed = wobble.copy()
    holed.iloc[5:15, holed.columns.get_loc("close")] = np.nan
    assert bars_of_history(holed).iloc[-1] == float(len(holed) - 10)
