"""Directional movement, Aroon, regression trend and the trend template."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from factorbase.factors._common import simple_moving_average, wilder_smoothing
from factorbase.factors.trend import (
    adjusted_slope,
    adx,
    aroon_down,
    aroon_oscillator,
    aroon_up,
    directional_movement,
    minus_di,
    plus_di,
    regression_slope_annualised,
    trend_stability,
    trend_template_conditions,
    trend_template_score,
)
from factorbase.factors.volatility import true_range


# ── Directional movement ────────────────────────────────────────────────────

def test_only_one_direction_registers_per_bar() -> None:
    frame = pd.DataFrame({"high": [10.0, 12.0, 11.0], "low": [9.0, 10.0, 7.0]})
    movement = directional_movement(frame)
    assert (movement["plus_dm"] * movement["minus_dm"] == 0.0).all()
    assert movement["plus_dm"].iloc[1] == pytest.approx(2.0)
    assert movement["minus_dm"].iloc[2] == pytest.approx(3.0)


def test_an_inside_bar_registers_no_movement() -> None:
    """Lower high and higher low: nothing moved outward, so both are zero."""
    frame = pd.DataFrame({"high": [10.0, 9.5], "low": [8.0, 8.5]})
    movement = directional_movement(frame)
    assert movement["plus_dm"].iloc[1] == 0.0
    assert movement["minus_dm"].iloc[1] == 0.0


def test_plus_di_matches_the_written_ratio(wobble: pd.DataFrame) -> None:
    periods = 14
    movement = directional_movement(wobble)
    expected = (
        100.0
        * wilder_smoothing(movement["plus_dm"], periods)
        / wilder_smoothing(true_range(wobble), periods)
    )
    assert np.allclose(plus_di(wobble, periods).dropna(), expected.dropna())


def test_an_unbroken_advance_pins_plus_di_and_empties_minus_di(ramp: pd.DataFrame) -> None:
    assert minus_di(ramp, 14).iloc[100] == pytest.approx(0.0)
    assert plus_di(ramp, 14).iloc[100] > 0.0


# ── ADX ─────────────────────────────────────────────────────────────────────

def test_adx_is_direction_blind(wobble: pd.DataFrame) -> None:
    """Mirroring the series about a horizontal line leaves trend strength unchanged."""
    mirrored = pd.DataFrame(
        {
            "high": 1000.0 - wobble["low"],
            "low": 1000.0 - wobble["high"],
            "close": 1000.0 - wobble["close"],
        },
        index=wobble.index,
    )
    original = adx(wobble, 14).dropna()
    flipped = adx(mirrored, 14).dropna()
    assert np.allclose(original.to_numpy(), flipped.to_numpy())


def test_adx_stays_inside_its_stated_range(wobble: pd.DataFrame) -> None:
    values = adx(wobble, 14).dropna()
    assert len(values) > 0
    assert values.min() >= 0.0
    assert values.max() <= 100.0


def test_adx_is_smoothed_twice_and_therefore_starts_later(wobble: pd.DataFrame) -> None:
    """Stated in the entry: the second smoothing costs another n bars of warm-up."""
    first_di = plus_di(wobble, 14).first_valid_index()
    first_adx = adx(wobble, 14).first_valid_index()
    assert first_adx is not None and first_di is not None
    assert first_adx > first_di


def test_adx_of_a_straight_advance_approaches_one_hundred(ramp: pd.DataFrame) -> None:
    assert adx(ramp, 14).iloc[-1] == pytest.approx(100.0, abs=1e-6)


# ── Aroon ───────────────────────────────────────────────────────────────────

def test_aroon_up_is_one_hundred_on_a_fresh_high(ramp: pd.DataFrame) -> None:
    assert aroon_up(ramp, periods=25).iloc[100] == pytest.approx(100.0)


def test_aroon_down_is_one_hundred_on_a_fresh_low() -> None:
    falling = pd.DataFrame({"low": np.arange(200.0, 100.0, -1.0), "high": np.arange(202.0, 102.0, -1.0)})
    assert aroon_down(falling, periods=25).iloc[80] == pytest.approx(100.0)


def test_aroon_reads_timing_not_size() -> None:
    """A violent spike and a gentle one at the same position give the same reading."""
    gentle = pd.DataFrame({"high": [1.0] * 20 + [1.1] + [1.0] * 4})
    violent = pd.DataFrame({"high": [1.0] * 20 + [9.0] + [1.0] * 4})
    assert aroon_up(gentle, 25).iloc[-1] == pytest.approx(aroon_up(violent, 25).iloc[-1])


def test_aroon_oscillator_is_the_difference(wobble: pd.DataFrame) -> None:
    expected = aroon_up(wobble, 25) - aroon_down(wobble, 25)
    assert np.allclose(aroon_oscillator(wobble, 25).dropna(), expected.dropna())


# ── Regression trend ────────────────────────────────────────────────────────

def test_regression_slope_recovers_a_known_growth_rate() -> None:
    """A series compounding at 0.1 percent a day annualises to 1.001**250 - 1."""
    dates = pd.bdate_range("2020-01-01", periods=200)
    frame = pd.DataFrame({"close": 100.0 * 1.001 ** np.arange(200)}, index=dates)
    expected = (1.001**250 - 1.0) * 100.0
    assert regression_slope_annualised(frame, periods=90).iloc[-1] == pytest.approx(expected)


def test_annualising_compounds_rather_than_multiplies() -> None:
    """The shortcut, slope times 250, overstates. The entry says so; this holds it."""
    dates = pd.bdate_range("2020-01-01", periods=200)
    frame = pd.DataFrame({"close": 100.0 * 1.001 ** np.arange(200)}, index=dates)
    multiplied = np.log(1.001) * 250 * 100.0
    assert regression_slope_annualised(frame, periods=90).iloc[-1] > multiplied


def test_trend_stability_is_one_on_a_perfect_exponential() -> None:
    dates = pd.bdate_range("2020-01-01", periods=200)
    frame = pd.DataFrame({"close": 100.0 * 1.001 ** np.arange(200)}, index=dates)
    assert trend_stability(frame, periods=90).iloc[-1] == pytest.approx(1.0)


def test_trend_stability_ignores_direction() -> None:
    dates = pd.bdate_range("2020-01-01", periods=200)
    up = pd.DataFrame({"close": 100.0 * 1.001 ** np.arange(200)}, index=dates)
    down = pd.DataFrame({"close": 100.0 * 0.999 ** np.arange(200)}, index=dates)
    assert trend_stability(up, 90).iloc[-1] == pytest.approx(trend_stability(down, 90).iloc[-1])


def test_trend_stability_stays_between_zero_and_one(wobble: pd.DataFrame) -> None:
    values = trend_stability(wobble, periods=90).dropna()
    assert values.min() >= 0.0
    assert values.max() <= 1.0


def test_adjusted_slope_penalises_noise_around_the_same_slope() -> None:
    """The intended effect: same drift, more scatter, lower score."""
    dates = pd.bdate_range("2020-01-01", periods=120)
    drift = np.log(100.0) + np.log(1.005) * np.arange(120)
    noise = np.random.default_rng(7).normal(0.0, 0.05, 120)
    noise -= np.polyval(np.polyfit(np.arange(120), noise, 1), np.arange(120))
    clean = pd.DataFrame({"close": np.exp(drift)}, index=dates)
    noisy = pd.DataFrame({"close": np.exp(drift + noise)}, index=dates)
    assert adjusted_slope(clean, 90).iloc[-1] > adjusted_slope(noisy, 90).iloc[-1]


def test_adjusted_slope_does_not_punish_a_single_step() -> None:
    """The entry states this outright, against the intuition. It is arithmetic, so it is tested.

    Same 80 percent gain across the window. Delivered evenly the fit is perfect
    but the line is shallow; delivered as one step the line is steeper by more
    than the loss in R squared costs.
    """
    dates = pd.bdate_range("2020-01-01", periods=90)
    target = 1.8
    even = pd.DataFrame({"close": 100.0 * target ** (np.arange(90) / 89.0)}, index=dates)
    step = pd.DataFrame(
        {"close": np.r_[np.full(45, 100.0), np.full(45, 100.0 * target)]}, index=dates
    )
    assert trend_stability(step, 90).iloc[-1] < trend_stability(even, 90).iloc[-1]
    assert adjusted_slope(step, 90).iloc[-1] > adjusted_slope(even, 90).iloc[-1]


def test_adjusted_slope_is_the_product(wobble: pd.DataFrame) -> None:
    expected = regression_slope_annualised(wobble, 90) * trend_stability(wobble, 90)
    assert np.allclose(adjusted_slope(wobble, 90).dropna(), expected.dropna())


# ── Trend template ──────────────────────────────────────────────────────────

def test_template_reports_each_condition_separately(wobble: pd.DataFrame) -> None:
    """A verdict says no without saying why. The columns are the why."""
    conditions = trend_template_conditions(wobble)
    assert list(conditions.columns) == [
        "close_above_150_and_200",
        "ma150_above_ma200",
        "ma200_rising",
        "ma50_above_both",
        "close_above_ma50",
        "well_above_52w_low",
        "near_52w_high",
    ]


def test_template_scores_seven_on_a_clean_uptrend() -> None:
    dates = pd.bdate_range("2015-01-01", periods=600)
    frame = pd.DataFrame({"close": 100.0 * 1.002 ** np.arange(600)}, index=dates)
    assert trend_template_score(frame).iloc[-1] == 7.0


def test_template_scores_low_on_a_downtrend() -> None:
    dates = pd.bdate_range("2015-01-01", periods=600)
    frame = pd.DataFrame({"close": 100.0 * 0.998 ** np.arange(600)}, index=dates)
    assert trend_template_score(frame).iloc[-1] <= 2.0


def test_template_is_undefined_before_a_year_of_history() -> None:
    """The alternative, counting undefined conditions as failed, invents a low score."""
    dates = pd.bdate_range("2020-01-01", periods=400)
    frame = pd.DataFrame({"close": 100.0 * 1.002 ** np.arange(400)}, index=dates)
    score = trend_template_score(frame)
    assert score.iloc[220].__class__ is np.float64
    assert np.isnan(score.iloc[220])
    assert not np.isnan(score.iloc[-1])


def test_template_condition_three_reads_the_average_not_the_price() -> None:
    """A price that has turned down can still sit on a rising 200-day average."""
    dates = pd.bdate_range("2015-01-01", periods=600)
    rising = 100.0 * 1.002 ** np.arange(600)
    rising[-5:] = rising[-6] * 0.97
    frame = pd.DataFrame({"close": rising}, index=dates)
    conditions = trend_template_conditions(frame)
    ma200 = simple_moving_average(frame["close"], 200)
    assert conditions["ma200_rising"].iloc[-1] == bool(ma200.iloc[-1] > ma200.iloc[-23])
