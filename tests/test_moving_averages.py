"""Moving averages, checked against the formulas the catalogue states.

Each test recomputes the formula independently, in a loop, from the LaTeX in
the catalogue entry. Comparing the implementation to itself would pass on any
definition; comparing it to a second reading of the formula is the only way the
test can fail for the right reason.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from factorbase import compute, default_catalog
from factorbase.errors import MissingInputError
from factorbase.factors._common import moving_average
from factorbase.factors.moving_averages import (
    ema,
    ma_slope,
    ma_slope_normalized,
    ma_to_ma_distance,
    price_to_ma_distance,
    sma,
    wma,
)
from factorbase.factors.volatility import atr


def test_sma_equals_the_written_mean(ramp: pd.DataFrame) -> None:
    result = sma(ramp, periods=10)
    for position in (9, 50, 299):
        window = ramp["close"].iloc[position - 9 : position + 1]
        assert result.iloc[position] == pytest.approx(window.sum() / 10)


def test_sma_of_a_ramp_is_the_midpoint(ramp: pd.DataFrame) -> None:
    """On a series rising by 1 a bar, the n-mean sits (n-1)/2 below the close."""
    result = sma(ramp, periods=21)
    assert result.iloc[100] == pytest.approx(ramp["close"].iloc[100] - 10.0)


def test_sma_warmup_is_nan_not_partial(ramp: pd.DataFrame) -> None:
    result = sma(ramp, periods=10)
    assert result.iloc[:9].isna().all()
    assert not np.isnan(result.iloc[9])


def test_ema_is_seeded_with_the_simple_average(wobble: pd.DataFrame) -> None:
    """The seed convention is part of the definition, so it is part of the test."""
    periods = 20
    result = ema(wobble, periods=periods)
    assert result.iloc[: periods - 1].isna().all()
    assert result.iloc[periods - 1] == pytest.approx(wobble["close"].iloc[:periods].mean())


def test_ema_recursion_matches_a_hand_loop(wobble: pd.DataFrame) -> None:
    periods = 20
    alpha = 2.0 / (periods + 1)
    close = wobble["close"].to_numpy()
    expected = np.full(len(close), np.nan)
    expected[periods - 1] = close[:periods].mean()
    for i in range(periods, len(close)):
        expected[i] = alpha * close[i] + (1 - alpha) * expected[i - 1]
    result = ema(wobble, periods=periods).to_numpy()
    assert np.allclose(result[periods - 1 :], expected[periods - 1 :])


def test_wma_weights_the_newest_bar_most(ramp: pd.DataFrame) -> None:
    periods = 5
    result = wma(ramp, periods=periods)
    window = ramp["close"].iloc[96:101].to_numpy()
    expected = float((window * np.arange(1, periods + 1)).sum() / 15)
    assert result.iloc[100] == pytest.approx(expected)


def test_wma_sits_above_sma_on_a_rising_series(ramp: pd.DataFrame) -> None:
    assert wma(ramp, periods=50).iloc[200] > sma(ramp, periods=50).iloc[200]


def test_price_to_ma_distance_is_percent_of_the_average(wobble: pd.DataFrame) -> None:
    result = price_to_ma_distance(wobble, periods=50, method="sma")
    average = moving_average(wobble["close"], 50, "sma")
    expected = (wobble["close"] - average) / average * 100.0
    assert np.allclose(result.dropna(), expected.dropna())


def test_price_to_ma_distance_is_zero_when_price_equals_average() -> None:
    flat = pd.DataFrame({"close": pd.Series([50.0] * 40)})
    assert price_to_ma_distance(flat, periods=20).iloc[-1] == pytest.approx(0.0)


def test_ma_to_ma_distance_is_positive_when_fast_leads(ramp: pd.DataFrame) -> None:
    result = ma_to_ma_distance(ramp, fast_periods=20, slow_periods=100)
    assert result.iloc[250] > 0


def test_ma_slope_of_a_ramp_is_the_ramp(ramp: pd.DataFrame) -> None:
    """A 1-per-bar ramp moves its 50-mean by exactly 20 over 20 bars."""
    result = ma_slope(ramp, periods=50, lookback=20)
    average = sma(ramp, periods=50)
    expected = 20.0 / average.iloc[180] * 100.0
    assert result.iloc[200] == pytest.approx(expected)


def test_ma_slope_normalized_is_in_units_of_atr(wobble: pd.DataFrame) -> None:
    periods, lookback = 50, 20
    result = ma_slope_normalized(wobble, periods=periods, lookback=lookback)
    average = sma(wobble, periods=periods)
    expected = (average - average.shift(lookback)) / atr(wobble, periods)
    assert np.allclose(result.dropna(), expected.dropna())


def test_missing_column_names_the_column() -> None:
    frame = pd.DataFrame({"price": [1.0, 2.0, 3.0]})
    with pytest.raises(MissingInputError) as caught:
        sma(frame, periods=2)
    assert "close" in str(caught.value)
    assert caught.value.missing == ("close",)


def test_compute_uses_catalogue_defaults_not_function_defaults(ramp: pd.DataFrame) -> None:
    """The documented default is the effective one. That is the whole contract."""
    catalogue_default = next(
        p.default for p in default_catalog()["sma"].parameters if p.id == "periods"
    )
    assert compute("sma", ramp).equals(sma(ramp, periods=catalogue_default))


def test_every_moving_average_method_is_reachable(wobble: pd.DataFrame) -> None:
    for method in ("sma", "ema", "wma"):
        result = price_to_ma_distance(wobble, periods=30, method=method)
        assert result.notna().sum() > 0


def test_unknown_method_is_rejected(wobble: pd.DataFrame) -> None:
    with pytest.raises(ValueError, match="unknown moving-average method"):
        price_to_ma_distance(wobble, periods=30, method="hull")


# ── Against references written outside this package ─────────────────────────


def test_sma_agrees_with_the_standard_library(wobble: pd.DataFrame) -> None:
    """statistics.fmean, not a second call to pandas' rolling mean."""
    import statistics

    periods = 30
    closes = wobble["close"].tolist()
    result = sma(wobble, periods)
    for position in (29, 100, 250, len(closes) - 1):
        window = closes[position - periods + 1 : position + 1]
        assert result.iloc[position] == pytest.approx(statistics.fmean(window))


def test_wma_agrees_with_a_hand_written_weighted_sum(wobble: pd.DataFrame) -> None:
    periods = 10
    closes = wobble["close"].tolist()
    result = wma(wobble, periods)
    for position in (9, 120, 399):
        window = closes[position - periods + 1 : position + 1]
        numerator = sum(value * (index + 1) for index, value in enumerate(window))
        assert result.iloc[position] == pytest.approx(numerator / (periods * (periods + 1) / 2))


def test_the_three_averages_coincide_on_a_flat_series() -> None:
    """Any weighting of identical numbers is that number. A weighting bug that
    keeps the weights summing to one survives this; one that does not, does not."""
    flat = pd.DataFrame({"close": [42.0] * 100})
    for average in (sma, ema, wma):
        assert average(flat, periods=20).iloc[-1] == pytest.approx(42.0)


def test_ema_alpha_is_two_over_n_plus_one(wobble: pd.DataFrame) -> None:
    """Derived from the published relation between a span and its smoothing
    constant, then applied by hand to two consecutive readings."""
    periods = 20
    alpha = 2.0 / (periods + 1)
    result = ema(wobble, periods)
    close = wobble["close"]
    for position in (100, 200, 399):
        recovered = (result.iloc[position] - (1 - alpha) * result.iloc[position - 1]) / alpha
        assert recovered == pytest.approx(close.iloc[position])
