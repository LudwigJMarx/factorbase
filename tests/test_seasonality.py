"""Seasonal strength and hit rate.

Both are tested on series whose seasonal structure was put there on purpose, so
every expected value is arithmetic rather than a recomputation of the code.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from factorbase.errors import UnsupportedIndexError
from factorbase.factors.seasonality import seasonal_hit_rate, seasonal_strength


def weekday_series(monday_return: float = 0.01, length: int = 1600) -> pd.DataFrame:
    """Every Monday returns exactly `monday_return`, every other day nothing."""
    index = pd.bdate_range("2015-01-05", periods=length)
    returns = np.where(index.dayofweek == 0, monday_return, 0.0)
    return pd.DataFrame({"close": 100.0 * np.cumprod(1.0 + returns)}, index=index)


def test_the_weekday_bucket_recovers_the_return_that_was_planted() -> None:
    frame = weekday_series()
    result = seasonal_strength(frame, bucket="day_of_week", years=5, detrend=False)
    last_monday = frame.index[frame.index.dayofweek == 0][-1]
    last_tuesday = frame.index[frame.index.dayofweek == 1][-1]
    assert result.loc[last_monday] == pytest.approx(1.0)
    assert result.loc[last_tuesday] == pytest.approx(0.0)


def test_detrending_removes_the_drift_the_season_itself_creates() -> None:
    """One day in five carries a one percent return, so the drift is 0.2 percent
    a day and the Monday excess is 0.8 rather than 1.0."""
    frame = weekday_series()
    result = seasonal_strength(frame, bucket="day_of_week", years=5, detrend=True)
    last_monday = frame.index[frame.index.dayofweek == 0][-1]
    assert result.loc[last_monday] == pytest.approx(0.8, abs=0.01)


def test_without_detrending_a_rising_instrument_reads_positive_everywhere() -> None:
    """The failure mode the switch exists for: the factor ranks on drift while
    appearing to rank on seasonality."""
    index = pd.bdate_range("2015-01-05", periods=1600)
    frame = pd.DataFrame({"close": 100.0 * 1.0004 ** np.arange(len(index))}, index=index)
    raw = seasonal_strength(frame, bucket="day_of_week", years=5, detrend=False).dropna()
    adjusted = seasonal_strength(frame, bucket="day_of_week", years=5, detrend=True).dropna()
    assert (raw > 0.0).all()
    assert np.allclose(adjusted.to_numpy(), 0.0, atol=1e-9)


def test_the_current_bar_never_feeds_its_own_reading() -> None:
    """Truncating the series after a bar must not change that bar's value."""
    frame = weekday_series()
    cut = 1200
    full = seasonal_strength(frame, bucket="day_of_week", years=5, detrend=False)
    partial = seasonal_strength(frame.iloc[: cut + 1], bucket="day_of_week", years=5, detrend=False)
    assert full.iloc[cut] == pytest.approx(partial.iloc[cut])


def test_the_calendar_window_wraps_around_the_turn_of_the_year() -> None:
    """Late December and early January are days apart, not three hundred."""
    index = pd.bdate_range("2015-01-01", periods=1600)
    frame = pd.DataFrame({"close": 100.0 + np.arange(len(index)) * 0.01}, index=index)
    late = pd.Timestamp("2019-12-30")
    assert late in frame.index
    result = seasonal_strength(frame, bucket="calendar_window", years=4, window_days=5)
    assert not np.isnan(result.loc[late])


def test_the_quarter_bucket_separates_the_quarters() -> None:
    index = pd.bdate_range("2015-01-05", periods=1600)
    returns = np.where(index.quarter == 4, 0.01, 0.0)
    frame = pd.DataFrame({"close": 100.0 * np.cumprod(1.0 + returns)}, index=index)
    result = seasonal_strength(frame, bucket="quarter", years=5, detrend=False)
    fourth = frame.index[frame.index.quarter == 4][-1]
    first = frame.index[frame.index.quarter == 1][-1]
    assert result.loc[fourth] > result.loc[first]
    assert result.loc[first] == pytest.approx(0.0)


def test_the_hit_rate_and_the_mean_disagree_where_one_day_carries_the_bucket() -> None:
    """The case a seasonal claim usually turns out to be: a high mean on a
    coin-flip hit rate."""
    index = pd.bdate_range("2015-01-05", periods=1600)
    rng = np.random.default_rng(3)
    returns = rng.choice([-0.002, 0.002], size=len(index))
    mondays = index.dayofweek == 0
    # One Monday in ten is enormous; the rest stay a coin flip.
    returns[mondays & (np.arange(len(index)) % 50 == 0)] = 0.30
    frame = pd.DataFrame({"close": 100.0 * np.cumprod(1.0 + returns)}, index=index)

    last_monday = index[mondays][-1]
    mean = seasonal_strength(frame, bucket="day_of_week", years=5, detrend=False)
    rate = seasonal_hit_rate(frame, bucket="day_of_week", years=5)
    assert mean.loc[last_monday] > 0.5
    assert 35.0 < rate.loc[last_monday] < 65.0


def test_the_hit_rate_is_one_hundred_where_every_bar_rose() -> None:
    frame = weekday_series()
    result = seasonal_hit_rate(frame, bucket="day_of_week", years=5)
    last_monday = frame.index[frame.index.dayofweek == 0][-1]
    assert result.loc[last_monday] == pytest.approx(100.0)


def test_an_unknown_bucket_is_rejected() -> None:
    frame = weekday_series(length=300)
    for factor in (seasonal_strength, seasonal_hit_rate):
        with pytest.raises(ValueError, match="unknown bucket"):
            factor(frame, bucket="fortnight")


def test_both_say_what_index_they_need() -> None:
    frame = pd.DataFrame({"close": [100.0 + i for i in range(300)]})
    for factor in (seasonal_strength, seasonal_hit_rate):
        with pytest.raises(UnsupportedIndexError) as caught:
            factor(frame)
        assert "DatetimeIndex" in str(caught.value)


def test_a_bucket_with_no_past_observations_is_undefined() -> None:
    """The first year has nothing to compare against. NaN, not zero: zero is a
    measurement and this is the absence of one."""
    frame = weekday_series(length=300)
    result = seasonal_strength(frame, bucket="quarter", years=5)
    assert np.isnan(result.iloc[0])
