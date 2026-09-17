"""Momentum factors, checked against the formulas in the catalogue entries."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from factorbase.factors._common import (
    exponential_moving_average,
    simple_moving_average,
    wilder_smoothing,
)
from factorbase.factors.momentum import (
    absolute_price_change,
    cci,
    double_smoothed_stochastic_blau,
    double_smoothed_stochastic_bressert,
    macd,
    macd_histogram,
    macd_histogram_change,
    macd_momentum,
    macd_signal,
    rate_of_change,
    rsi,
    stochastic_fast_d,
    stochastic_fast_k,
    stochastic_slow_d,
    stochastic_slow_k,
    typical_price,
    williams_percent_r,
)

# ── RSI ─────────────────────────────────────────────────────────────────────


def test_rsi_matches_wilders_recursion(wobble: pd.DataFrame) -> None:
    """Recomputed in a loop straight from the entry's second and fourth formula."""
    periods = 14
    close = wobble["close"].to_numpy()
    gains = np.maximum(np.diff(close), 0.0)
    losses = np.maximum(-np.diff(close), 0.0)

    expected = np.full(len(close), np.nan)
    average_gain = gains[:periods].mean()
    average_loss = losses[:periods].mean()
    expected[periods] = 100.0 - 100.0 / (1.0 + average_gain / average_loss)
    for i in range(periods, len(gains)):
        average_gain = ((periods - 1) * average_gain + gains[i]) / periods
        average_loss = ((periods - 1) * average_loss + losses[i]) / periods
        expected[i + 1] = 100.0 - 100.0 / (1.0 + average_gain / average_loss)

    result = rsi(wobble, periods=periods).to_numpy()
    assert np.allclose(result[periods:], expected[periods:])


def test_rsi_of_an_unbroken_advance_is_one_hundred(ramp: pd.DataFrame) -> None:
    """The quotient form divides by zero here; the entry says the answer is 100."""
    assert rsi(ramp, periods=14).iloc[100] == pytest.approx(100.0)


def test_rsi_of_a_flat_series_is_fifty() -> None:
    flat = pd.DataFrame({"close": pd.Series([25.0] * 60)})
    assert rsi(flat, periods=14).iloc[-1] == pytest.approx(50.0)


def test_rsi_stays_inside_its_stated_range(wobble: pd.DataFrame) -> None:
    values = rsi(wobble, periods=14).dropna()
    assert values.min() >= 0.0
    assert values.max() <= 100.0


def test_wilder_and_ema_smoothing_differ(wobble: pd.DataFrame) -> None:
    """If these agreed, the parameter would be decoration."""
    wilder = rsi(wobble, periods=14, method="wilder")
    ema_based = rsi(wobble, periods=14, method="ema")
    assert not np.allclose(wilder.dropna().to_numpy()[-50:], ema_based.dropna().to_numpy()[-50:])


def test_unknown_smoothing_is_rejected(wobble: pd.DataFrame) -> None:
    with pytest.raises(ValueError, match="unknown smoothing"):
        rsi(wobble, method="kaufman")


# ── Rate of change ──────────────────────────────────────────────────────────


def test_rate_of_change_is_a_percentage(ramp: pd.DataFrame) -> None:
    result = rate_of_change(ramp, periods=10)
    before, now = ramp["close"].iloc[90], ramp["close"].iloc[100]
    assert result.iloc[100] == pytest.approx((now / before - 1.0) * 100.0)


def test_absolute_price_change_is_in_currency(ramp: pd.DataFrame) -> None:
    """On a 1-per-bar ramp the 10-bar change is exactly 10, at every point."""
    result = absolute_price_change(ramp, periods=10).dropna()
    assert np.allclose(result.to_numpy(), 10.0)


# ── MACD family ─────────────────────────────────────────────────────────────


def test_macd_is_the_difference_of_two_exponential_averages(wobble: pd.DataFrame) -> None:
    expected = exponential_moving_average(wobble["close"], 12) - exponential_moving_average(
        wobble["close"], 26
    )
    assert np.allclose(macd(wobble).dropna(), expected.dropna())


def test_macd_signal_does_not_inherit_the_warmup_nans(wobble: pd.DataFrame) -> None:
    """Seeding from the frame's start would put NaN into the seed and poison the line."""
    line = macd(wobble)
    signal = macd_signal(wobble)
    first_defined_line = line.first_valid_index()
    first_defined_signal = signal.first_valid_index()
    assert first_defined_signal is not None
    assert first_defined_signal > first_defined_line
    assert signal.loc[first_defined_signal:].notna().all()


def test_macd_histogram_is_line_minus_signal(wobble: pd.DataFrame) -> None:
    expected = macd(wobble) - macd_signal(wobble)
    assert np.allclose(macd_histogram(wobble).dropna(), expected.dropna())


def test_macd_histogram_change_is_a_difference(wobble: pd.DataFrame) -> None:
    histogram = macd_histogram(wobble)
    expected = histogram - histogram.shift(3)
    assert np.allclose(macd_histogram_change(wobble, lookback=3).dropna(), expected.dropna())


def test_macd_momentum_reads_the_line_not_the_histogram(wobble: pd.DataFrame) -> None:
    """The two are different series. Conflating them is the error the entry warns about."""
    momentum = macd_momentum(wobble, lookback=5).dropna()
    histogram_change = macd_histogram_change(wobble, lookback=5).dropna()
    common = momentum.index.intersection(histogram_change.index)
    assert not np.allclose(momentum.loc[common], histogram_change.loc[common])


# ── CCI ─────────────────────────────────────────────────────────────────────


def test_cci_matches_a_hand_computed_window(wobble: pd.DataFrame) -> None:
    periods, position = 20, 120
    typical = typical_price(wobble)
    window = typical.iloc[position - periods + 1 : position + 1]
    average = window.mean()
    deviation = (window - average).abs().mean()
    expected = (typical.iloc[position] - average) / (0.015 * deviation)
    assert cci(wobble, periods=periods).iloc[position] == pytest.approx(expected)


def test_cci_uses_mean_absolute_not_standard_deviation(wobble: pd.DataFrame) -> None:
    """Swapping the two is a silent, plausible-looking error, so it gets its own test."""
    periods, position = 20, 120
    typical = typical_price(wobble)
    window = typical.iloc[position - periods + 1 : position + 1]
    with_std = (typical.iloc[position] - window.mean()) / (0.015 * window.std(ddof=0))
    assert cci(wobble, periods=periods).iloc[position] != pytest.approx(with_std)


# ── Stochastics and Williams %R ─────────────────────────────────────────────


def test_fast_k_places_the_close_in_the_range(wobble: pd.DataFrame) -> None:
    periods, position = 14, 200
    highest = wobble["high"].iloc[position - periods + 1 : position + 1].max()
    lowest = wobble["low"].iloc[position - periods + 1 : position + 1].min()
    expected = (wobble["close"].iloc[position] - lowest) / (highest - lowest) * 100.0
    assert stochastic_fast_k(wobble, periods=periods).iloc[position] == pytest.approx(expected)


def test_fast_k_is_one_hundred_at_the_top_of_the_range(ramp: pd.DataFrame) -> None:
    """On a ramp the close is always the highest close, but the high sits one above it."""
    value = stochastic_fast_k(ramp, periods=10).iloc[100]
    assert 0.0 <= value <= 100.0
    assert value > 80.0


def test_williams_r_is_fast_k_shifted_by_one_hundred(wobble: pd.DataFrame) -> None:
    """The entry says they are the same quantity on a different scale. This holds them to it."""
    difference = williams_percent_r(wobble, periods=14) - stochastic_fast_k(wobble, periods=14)
    assert np.allclose(difference.dropna(), -100.0)


def test_slow_k_is_fast_d(wobble: pd.DataFrame) -> None:
    """Stated in the entry as a naming accident, not a different calculation."""
    assert np.allclose(stochastic_slow_k(wobble).dropna(), stochastic_fast_d(wobble).dropna())


def test_slow_d_is_fast_k_smoothed_twice(wobble: pd.DataFrame) -> None:
    expected = simple_moving_average(simple_moving_average(stochastic_fast_k(wobble, 14), 3), 3)
    assert np.allclose(stochastic_slow_d(wobble).dropna(), expected.dropna())


def test_flat_range_does_not_divide_by_zero() -> None:
    flat = pd.DataFrame({"high": [10.0] * 30, "low": [10.0] * 30, "close": [10.0] * 30})
    assert stochastic_fast_k(flat, periods=14).iloc[-1] == pytest.approx(50.0)


# ── Double smoothed stochastics ─────────────────────────────────────────────


def test_blau_smooths_before_dividing(wobble: pd.DataFrame) -> None:
    """Recomputed from the entry's three formulas, in order."""
    periods, first, second = 10, 3, 3
    highest = wobble["high"].rolling(periods, min_periods=periods).max()
    lowest = wobble["low"].rolling(periods, min_periods=periods).min()
    numerator = exponential_moving_average(
        exponential_moving_average((wobble["close"] - lowest).dropna(), first), second
    )
    denominator = exponential_moving_average(
        exponential_moving_average((highest - lowest).dropna(), first), second
    )
    expected = (100.0 * numerator / denominator).dropna()
    result = double_smoothed_stochastic_blau(wobble).dropna()
    assert np.allclose(result.loc[expected.index], expected)


def test_blau_differs_from_smoothing_the_quotient(wobble: pd.DataFrame) -> None:
    """The order of division and smoothing is the indicator.

    If it did not matter, it would not be an indicator.
    """
    naive = exponential_moving_average(
        exponential_moving_average(stochastic_fast_k(wobble, 10).dropna(), 3), 3
    ).dropna()
    result = double_smoothed_stochastic_blau(wobble).dropna()
    common = naive.index.intersection(result.index)
    assert not np.allclose(naive.loc[common], result.loc[common])


def test_both_double_smoothed_variants_stay_in_range(wobble: pd.DataFrame) -> None:
    for series in (
        double_smoothed_stochastic_blau(wobble),
        double_smoothed_stochastic_bressert(wobble),
    ):
        values = series.dropna()
        assert len(values) > 0
        assert values.min() >= 0.0
        assert values.max() <= 100.0


def test_bressert_rescales_further_than_blau(wobble: pd.DataFrame) -> None:
    """The second stochastic pass restores the full range; that is the stated difference."""
    blau = double_smoothed_stochastic_blau(wobble).dropna()
    bressert = double_smoothed_stochastic_bressert(wobble).dropna()
    assert bressert.max() - bressert.min() > blau.max() - blau.min()


# ── Where the smoothing starts ──────────────────────────────────────────────

# fmt: off
WILDER_EXAMPLE = [
    44.34, 44.09, 44.15, 43.61, 44.33, 44.83, 45.10, 45.42, 45.84, 46.08, 45.89,
    46.03, 45.61, 46.28, 46.28, 46.00, 46.03, 46.41, 46.22, 45.64, 46.21, 46.25,
    45.71, 46.45, 45.78, 45.35, 44.03, 44.18, 44.22, 44.57, 43.42, 42.66, 43.13,
]
# fmt: on


def test_wilder_smoothing_seeds_on_the_first_n_real_observations() -> None:
    """The seed is the mean of n values, at the position of the nth of them.

    A series whose first entry is missing has its nth real observation at
    index n, not at n-1. Placing the seed at a fixed offset instead averages
    n-1 values and calls the result an n-period reading.
    """
    values = pd.Series([np.nan] + [2.0] * 5 + [8.0] * 10)
    smoothed = wilder_smoothing(values, 5)
    assert smoothed.first_valid_index() == 5
    assert smoothed.iloc[5] == pytest.approx(2.0)
    assert smoothed.iloc[:5].isna().all()


def test_rsi_emits_exactly_the_readings_wilder_defines() -> None:
    """33 closes give 32 changes, so RSI(14) has 19 readings, starting at index 14."""
    frame = pd.DataFrame({"close": WILDER_EXAMPLE})
    result = rsi(frame, periods=14)
    assert result.first_valid_index() == 14
    assert int(result.notna().sum()) == len(WILDER_EXAMPLE) - 14


def test_rsi_first_reading_matches_the_hand_computed_seed() -> None:
    """Checked against Wilder's definition, not against this implementation."""
    changes = np.diff(np.array(WILDER_EXAMPLE))
    average_gain = np.maximum(changes, 0.0)[:14].mean()
    average_loss = np.maximum(-changes, 0.0)[:14].mean()
    expected = 100.0 - 100.0 / (1.0 + average_gain / average_loss)

    frame = pd.DataFrame({"close": WILDER_EXAMPLE})
    assert rsi(frame, periods=14).iloc[14] == pytest.approx(expected)
    assert expected == pytest.approx(70.4641, abs=1e-4)
