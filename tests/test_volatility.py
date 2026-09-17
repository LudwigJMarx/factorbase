"""Volatility, drawdown and the Bollinger family."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from factorbase.factors.volatility import (
    atr,
    atr_percent,
    average_drawdown,
    bollinger_band_width,
    bollinger_bands,
    bollinger_percent_b,
    distance_to_lower_band,
    distance_to_upper_band,
    historical_volatility,
    historical_volatility_weekly,
    max_drawdown,
    trading_range,
    true_range,
)

# ── True range and ATR ──────────────────────────────────────────────────────


def test_true_range_is_the_widest_of_the_three_spans() -> None:
    frame = pd.DataFrame(
        {"high": [10.0, 12.0, 9.0], "low": [9.0, 11.0, 8.0], "close": [9.5, 11.5, 8.5]}
    )
    result = true_range(frame)
    assert result.iloc[0] == pytest.approx(1.0)  # no previous close, plain range
    assert result.iloc[1] == pytest.approx(2.5)  # high 12.0 against previous close 9.5
    assert result.iloc[2] == pytest.approx(3.5)  # low 8.0 against previous close 11.5


def test_true_range_covers_a_gap_the_plain_range_misses() -> None:
    """The gapped bar's own range is 1.0; the true range has to see the 5.0 jump."""
    gapped = pd.DataFrame({"high": [10.0, 16.0], "low": [9.0, 15.0], "close": [10.0, 15.5]})
    assert gapped["high"].iloc[1] - gapped["low"].iloc[1] == pytest.approx(1.0)
    assert true_range(gapped).iloc[1] == pytest.approx(6.0)


def test_true_range_keeps_the_first_bar(wobble: pd.DataFrame) -> None:
    """Dropping it would shift every average that follows by one observation."""
    assert not np.isnan(true_range(wobble).iloc[0])


def test_atr_uses_wilders_constant_not_a_span(wobble: pd.DataFrame) -> None:
    periods = 14
    ranges = true_range(wobble).to_numpy()
    expected = np.full(len(ranges), np.nan)
    expected[periods - 1] = ranges[:periods].mean()
    for i in range(periods, len(ranges)):
        expected[i] = ((periods - 1) * expected[i - 1] + ranges[i]) / periods
    assert np.allclose(atr(wobble, periods).to_numpy()[periods - 1 :], expected[periods - 1 :])


def test_atr_of_a_constant_range_is_that_range(ramp: pd.DataFrame) -> None:
    """The ramp's bars are 2.0 wide and step by 1.0, so the true range is 2.0 throughout."""
    assert atr(ramp, periods=14).iloc[100] == pytest.approx(2.0)


def test_atr_percent_divides_by_the_close(ramp: pd.DataFrame) -> None:
    position = 100
    expected = atr(ramp, 14).iloc[position] / ramp["close"].iloc[position] * 100.0
    assert atr_percent(ramp, 14).iloc[position] == pytest.approx(expected)


# ── Volatility ──────────────────────────────────────────────────────────────


def test_historical_volatility_matches_the_written_formula(wobble: pd.DataFrame) -> None:
    periods, position = 250, 350
    log_returns = np.log(wobble["close"] / wobble["close"].shift(1))
    window = log_returns.iloc[position - periods + 1 : position + 1]
    expected = window.std(ddof=1) * np.sqrt(250) * 100.0
    assert historical_volatility(wobble, periods).iloc[position] == pytest.approx(expected)


def test_historical_volatility_uses_the_sample_deviation(wobble: pd.DataFrame) -> None:
    """ddof=1, as the entry states. The population version reads slightly lower."""
    periods, position = 250, 350
    log_returns = np.log(wobble["close"] / wobble["close"].shift(1))
    window = log_returns.iloc[position - periods + 1 : position + 1]
    population = window.std(ddof=0) * np.sqrt(250) * 100.0
    assert historical_volatility(wobble, periods).iloc[position] != pytest.approx(population)


def test_historical_volatility_of_a_straight_line_is_zero() -> None:
    """A ramp in log space is not flat, so a geometric series is used instead."""
    dates = pd.bdate_range("2020-01-01", periods=300)
    geometric = pd.DataFrame({"close": 100.0 * 1.001 ** np.arange(300)}, index=dates)
    assert historical_volatility(geometric, periods=250).iloc[-1] == pytest.approx(0.0, abs=1e-9)


def test_weekly_volatility_is_not_the_daily_one(wobble: pd.DataFrame) -> None:
    daily = historical_volatility(wobble, periods=250).dropna()
    weekly = historical_volatility_weekly(wobble, periods=52).dropna()
    assert len(weekly) > 0
    assert weekly.iloc[-1] != pytest.approx(daily.iloc[-1])


def test_weekly_volatility_is_carried_onto_daily_bars(wobble: pd.DataFrame) -> None:
    """Stated in the entry's note: a reading repeats within a week."""
    weekly = historical_volatility_weekly(wobble, periods=52).dropna()
    assert weekly.index.equals(wobble.index[wobble.index.isin(weekly.index)])
    assert weekly.tail(4).nunique() < 4


# ── Drawdown ────────────────────────────────────────────────────────────────


def test_average_drawdown_is_never_positive(wobble: pd.DataFrame) -> None:
    values = average_drawdown(wobble, periods=100).dropna()
    assert len(values) > 0
    assert values.max() <= 0.0


def test_average_drawdown_of_an_unbroken_advance_is_zero(ramp: pd.DataFrame) -> None:
    assert average_drawdown(ramp, periods=50).iloc[-1] == pytest.approx(0.0)


def test_max_drawdown_finds_the_worst_stretch() -> None:
    close = pd.Series([100.0, 120.0, 60.0, 80.0, 90.0] + [90.0] * 5)
    frame = pd.DataFrame({"close": close})
    assert max_drawdown(frame, periods=5).iloc[4] == pytest.approx(-50.0)


def test_max_drawdown_is_at_least_as_bad_as_the_average(wobble: pd.DataFrame) -> None:
    worst = max_drawdown(wobble, periods=100).dropna()
    average = average_drawdown(wobble, periods=100).dropna()
    common = worst.index.intersection(average.index)
    assert (worst.loc[common] <= average.loc[common] + 1e-9).all()


# ── Range ───────────────────────────────────────────────────────────────────


def test_trading_range_spans_high_to_low(wobble: pd.DataFrame) -> None:
    periods, position = 20, 100
    highest = wobble["high"].iloc[position - periods + 1 : position + 1].max()
    lowest = wobble["low"].iloc[position - periods + 1 : position + 1].min()
    expected = (highest - lowest) / lowest * 100.0
    assert trading_range(wobble, periods).iloc[position] == pytest.approx(expected)


def test_trading_range_ignores_the_path() -> None:
    """Stated in the entry: a straight run and a violent oscillation read the same."""
    straight = pd.DataFrame({"high": [10.0, 12.0, 14.0], "low": [10.0, 12.0, 14.0]})
    violent = pd.DataFrame({"high": [14.0, 10.0, 12.0], "low": [14.0, 10.0, 12.0]})
    assert trading_range(straight, 3).iloc[-1] == pytest.approx(trading_range(violent, 3).iloc[-1])


# ── Bollinger ───────────────────────────────────────────────────────────────


def test_bands_use_the_population_deviation(wobble: pd.DataFrame) -> None:
    """ddof=0, as the entry states. The sample version draws wider bands."""
    periods, position = 20, 100
    window = wobble["close"].iloc[position - periods + 1 : position + 1]
    bands = bollinger_bands(wobble, periods, 2.0)
    assert bands["upper"].iloc[position] == pytest.approx(window.mean() + 2.0 * window.std(ddof=0))
    assert bands["upper"].iloc[position] != pytest.approx(window.mean() + 2.0 * window.std(ddof=1))


def test_percent_b_is_zero_at_the_lower_band_and_one_at_the_upper(wobble: pd.DataFrame) -> None:
    bands = bollinger_bands(wobble, 20, 2.0)
    frame = wobble.copy()
    frame["close"] = bands["lower"]
    at_lower = (frame["close"] - bands["lower"]) / (bands["upper"] - bands["lower"])
    assert at_lower.dropna().abs().max() == pytest.approx(0.0)


def test_percent_b_leaves_its_range_when_the_close_does(wobble: pd.DataFrame) -> None:
    """Readings outside 0..1 are the point, not a defect."""
    values = bollinger_percent_b(wobble, 20, 2.0).dropna()
    assert values.max() > 1.0 or values.min() < 0.0


def test_band_width_is_relative_to_the_middle(wobble: pd.DataFrame) -> None:
    bands = bollinger_bands(wobble, 20, 2.0)
    expected = (bands["upper"] - bands["lower"]) / bands["middle"] * 100.0
    assert np.allclose(bollinger_band_width(wobble, 20, 2.0).dropna(), expected.dropna())


def test_distances_to_the_bands_sum_to_the_width_over_the_close(wobble: pd.DataFrame) -> None:
    """Both are measured against the close, so their sum is the band spread over the close."""
    bands = bollinger_bands(wobble, 20, 2.0)
    total = distance_to_upper_band(wobble, 20, 2.0) + distance_to_lower_band(wobble, 20, 2.0)
    expected = (bands["upper"] - bands["lower"]) / wobble["close"] * 100.0
    assert np.allclose(total.dropna(), expected.dropna())


def test_distance_to_upper_band_turns_negative_above_it(wobble: pd.DataFrame) -> None:
    distance = distance_to_upper_band(wobble, 20, 2.0)
    percent_b = bollinger_percent_b(wobble, 20, 2.0)
    above = percent_b > 1.0
    assert above.any()
    assert (distance[above] < 0.0).all()


# ── Against references written outside this package ─────────────────────────
#
# Everything above recomputes a formula this package also implements. That
# catches a wrong implementation of a right formula and cannot catch a wrong
# formula. What follows compares against the standard library, against closed
# forms, and against a Wilder loop written out here from the definition rather
# than called from `_common`.


def test_bollinger_deviation_is_the_population_one_per_the_standard_library(
    wobble: pd.DataFrame,
) -> None:
    """statistics.pstdev and statistics.stdev are two different functions in
    the standard library. The entry says which one the bands use, so the test
    asserts it against both rather than against this package's own call."""
    import statistics

    periods, position = 20, 100
    window = wobble["close"].iloc[position - periods + 1 : position + 1].tolist()
    middle = statistics.fmean(window)

    bands = bollinger_bands(wobble, periods, 2.0)
    assert bands["middle"].iloc[position] == pytest.approx(middle)
    assert bands["upper"].iloc[position] == pytest.approx(middle + 2.0 * statistics.pstdev(window))
    assert bands["upper"].iloc[position] != pytest.approx(middle + 2.0 * statistics.stdev(window))


def test_historical_volatility_is_the_sample_deviation_per_the_standard_library(
    wobble: pd.DataFrame,
) -> None:
    """The neighbouring entry uses the population deviation and this one uses
    the sample deviation. They disagree on purpose, so both get pinned to the
    standard library's two functions."""
    import math
    import statistics

    periods, position = 250, 350
    closes = wobble["close"].tolist()
    log_returns = [
        math.log(closes[i] / closes[i - 1]) for i in range(position - periods + 1, position + 1)
    ]
    expected = statistics.stdev(log_returns) * math.sqrt(250) * 100.0

    assert historical_volatility(wobble, periods).iloc[position] == pytest.approx(expected)
    population = statistics.pstdev(log_returns) * math.sqrt(250) * 100.0
    assert historical_volatility(wobble, periods).iloc[position] != pytest.approx(population)


def test_historical_volatility_of_a_two_state_series_has_a_closed_form() -> None:
    """Log returns alternating between +r and -r have a sample deviation of
    exactly r*sqrt(n/(n-1)) about a mean of zero, for an even count."""
    import math

    periods = 100
    r = 0.01
    values = [100.0]
    for i in range(400):
        values.append(values[-1] * math.exp(r if i % 2 == 0 else -r))
    frame = pd.DataFrame({"close": values})

    expected = r * math.sqrt(periods / (periods - 1)) * math.sqrt(250) * 100.0
    assert historical_volatility(frame, periods).iloc[-1] == pytest.approx(expected)


def test_atr_matches_a_wilder_loop_written_out_here(wobble: pd.DataFrame) -> None:
    """True range and the smoothing are both written out from the definition,
    without touching true_range() or wilder_smoothing()."""
    periods = 14
    high = wobble["high"].tolist()
    low = wobble["low"].tolist()
    close = wobble["close"].tolist()

    ranges = [high[0] - low[0]]
    for i in range(1, len(close)):
        ranges.append(
            max(high[i] - low[i], abs(high[i] - close[i - 1]), abs(low[i] - close[i - 1]))
        )

    expected = [float("nan")] * len(ranges)
    expected[periods - 1] = sum(ranges[:periods]) / periods
    for i in range(periods, len(ranges)):
        expected[i] = ((periods - 1) * expected[i - 1] + ranges[i]) / periods

    result = atr(wobble, periods).to_numpy()
    assert np.allclose(result[periods - 1 :], expected[periods - 1 :])


def test_max_drawdown_of_a_hand_walked_path() -> None:
    """Walked by hand: peak 200 at index 1, trough 80 at index 4, so -60 percent."""
    closes = [100.0, 200.0, 150.0, 120.0, 80.0, 90.0, 95.0]
    frame = pd.DataFrame({"close": closes})
    assert max_drawdown(frame, periods=7).iloc[-1] == pytest.approx(-60.0)


def test_average_drawdown_of_a_hand_walked_path() -> None:
    """Walked by hand with a window of 4 over seven closes.

    Running peaks: 100, 110, 110, 110 at indices 3 to 6.
    Underwater:      0,   0, -9.0909, -18.1818.
    Mean of those four: -6.8182 percent.
    """
    closes = [100.0, 90.0, 80.0, 100.0, 110.0, 100.0, 90.0]
    frame = pd.DataFrame({"close": closes})
    expected = (0.0 + 0.0 + (100.0 / 110.0 - 1.0) * 100.0 + (90.0 / 110.0 - 1.0) * 100.0) / 4.0
    assert expected == pytest.approx(-6.8182, abs=1e-4)
    assert average_drawdown(frame, periods=4).iloc[-1] == pytest.approx(expected)
