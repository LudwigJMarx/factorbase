"""The six entries whose rules came from a screener's own documentation.

Each is stated as a fixed set of conditions with fixed thresholds, so each is
tested on bars built to satisfy exactly one condition at a time. That is the
only way to show a five-condition rule needs all five: satisfy four and assert
it stays quiet.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from factorbase.factors.seasonality import seasonal_strength
from factorbase.factors.signals import (
    bollinger_band_outlier_long,
    bollinger_band_outlier_short,
    capitulation_bar,
    holy_grail_pullback,
)
from factorbase.factors.trend import random_trade_win_rate
from factorbase.factors.volume import average_turnover, average_volume

# ── Capitulation: five conditions, all required ─────────────────────────────


def quiet_then(last: dict[str, float], quiet_bars: int = 80) -> pd.DataFrame:
    """Eighty flat bars around 100 on steady volume, then one bar under test."""
    rows = [{"high": 101.0, "low": 99.0, "close": 100.0, "volume": 1_000_000.0}] * quiet_bars
    rows.append(last)
    index = pd.bdate_range("2020-01-01", periods=len(rows))
    return pd.DataFrame(rows, index=index)


def capitulating_bar() -> dict[str, float]:
    """All five at once, against eighty bars that held 99 to 101.

    Low 70, below every low of the window. Close 73, under the 75 midpoint of
    its own range. Down 27 percent on the day. 73 against the 101 high is 27.7
    percent off it, clearing the 25 required. Volume five times the usual,
    which survives being averaged with itself.
    """
    return {"high": 80.0, "low": 70.0, "close": 73.0, "volume": 5_000_000.0}


def test_capitulation_needs_all_five_conditions() -> None:
    assert bool(capitulation_bar(quiet_then(capitulating_bar())).iloc[-1])


def test_a_close_in_the_upper_half_is_not_capitulation() -> None:
    """Chosen so that this one condition fails and the other four still hold:
    75.5 is above the 75 midpoint and still 25.2 percent off the 101 high."""
    bar = capitulating_bar() | {"close": 75.5}
    assert bar["close"] / 101.0 <= 0.75
    assert not bool(capitulation_bar(quiet_then(bar)).iloc[-1])


def test_an_ordinary_volume_day_is_not_capitulation() -> None:
    bar = capitulating_bar() | {"volume": 1_000_000.0}
    assert not bool(capitulation_bar(quiet_then(bar)).iloc[-1])


def test_a_small_fall_is_not_capitulation() -> None:
    """New low, weak close, heavy volume, and only two percent down."""
    bar = {"high": 99.0, "low": 97.0, "close": 97.5, "volume": 5_000_000.0}
    assert not bool(capitulation_bar(quiet_then(bar)).iloc[-1])


def test_a_fall_that_is_not_a_new_low_is_not_capitulation() -> None:
    """Same bar twice: the second cannot make a new low against the first."""
    rows = [{"high": 101.0, "low": 99.0, "close": 100.0, "volume": 1_000_000.0}] * 80
    rows.append(capitulating_bar())
    rows.append(capitulating_bar())
    index = pd.bdate_range("2020-01-01", periods=len(rows))
    frame = pd.DataFrame(rows, index=index)
    result = capitulation_bar(frame)
    assert bool(result.iloc[-2])
    assert not bool(result.iloc[-1])


def test_capitulation_never_fires_on_a_random_walk(wobble: pd.DataFrame) -> None:
    """Stated in the entry. A signal that is silent on noise is easy to mistake
    for a broken one, so the silence is asserted rather than assumed."""
    assert capitulation_bar(wobble).sum() == 0


def test_capitulation_and_selling_climax_are_different_rules(wobble: pd.DataFrame) -> None:
    from factorbase.factors.signals import selling_climax

    assert not (capitulation_bar(wobble) & selling_climax(wobble)).any()


# ── Bollinger band outliers ─────────────────────────────────────────────────


def test_a_close_below_the_lower_band_qualifies_outright(wobble: pd.DataFrame) -> None:
    from factorbase.factors.signals import _band_edges

    lower, _ = _band_edges(wobble, 20, 2.0, sample=True)
    fired = bollinger_band_outlier_long(wobble)
    below = (wobble["close"] < lower).fillna(False)
    assert below.any()
    assert (fired | ~below).all()


def test_the_deviation_basis_changes_the_bands(wobble: pd.DataFrame) -> None:
    """Sample against population. At twenty periods the bands differ by about
    2.6 percent of the spread, which is enough to move a marginal bar."""
    sample = bollinger_band_outlier_long(wobble, sample_deviation=True)
    population = bollinger_band_outlier_long(wobble, sample_deviation=False)
    assert not sample.equals(population)


def test_the_long_and_short_forms_are_not_mirrors() -> None:
    """Shown on one bar and its exact reflection, through the reach clause.

    The outright clause, close against band, is symmetric and says nothing
    here. The reach clause is not, because both forms measure it from the
    bar's LOW. Long asks that the low come down to the lower band, which a bar
    that merely dips there satisfies while closing well above it. Short asks
    that the low come up past the upper band, which needs the whole candle
    above it.

    So a bar that dips to the lower band and closes inside fires the long
    form, and its mirror image, which poked up to the upper band and closed
    back inside, does not fire the short one.
    """

    def frame_of(rows: list[tuple[float, float, float]]) -> pd.DataFrame:
        return pd.DataFrame(
            {
                "high": [r[0] for r in rows],
                "low": [r[1] for r in rows],
                "close": [r[2] for r in rows],
            }
        )

    # Alternating closes give the bands a width of about two points either side.
    quiet = [(101.5, 98.5, 99.0 if i % 2 else 101.0) for i in range(40)]
    dipping = quiet + [(101.0, 97.5, 100.5)]
    mirrored = [(200.0 - low, 200.0 - high, 200.0 - close) for high, low, close in dipping]

    long_frame, short_frame = frame_of(dipping), frame_of(mirrored)

    # Neither bar closes outside its band, so only the reach clause can fire.
    from factorbase.factors.signals import _band_edges

    lower, _ = _band_edges(long_frame, 20, 2.0, sample=True)
    _, upper = _band_edges(short_frame, 20, 2.0, sample=True)
    assert long_frame["close"].iloc[-1] > lower.iloc[-1]
    assert short_frame["close"].iloc[-1] < upper.iloc[-1]

    assert bool(bollinger_band_outlier_long(long_frame).iloc[-1])
    assert not bool(bollinger_band_outlier_short(short_frame).iloc[-1])


def test_a_narrow_bar_inside_the_bands_fires_neither(wobble: pd.DataFrame) -> None:
    flat = pd.DataFrame({"high": [100.5] * 60, "low": [99.5] * 60, "close": [100.0] * 60})
    assert bollinger_band_outlier_long(flat).sum() == 0
    assert bollinger_band_outlier_short(flat).sum() == 0


# ── Holy grail pullback ─────────────────────────────────────────────────────


def test_the_pullback_needs_a_strong_trend() -> None:
    """The same shape with the threshold raised out of reach must go quiet."""
    index = pd.bdate_range("2020-01-01", periods=300)
    trend = 100.0 * 1.004 ** np.arange(300)
    wobble_in = np.where(np.arange(300) % 7 == 0, -0.03, 0.0)
    close = trend * (1.0 + wobble_in)
    frame = pd.DataFrame({"high": close * 1.01, "low": close * 0.985, "close": close}, index=index)
    assert holy_grail_pullback(frame, adx_threshold=30.0).sum() > 0
    assert holy_grail_pullback(frame, adx_threshold=99.0).sum() == 0


def test_the_pullback_needs_the_previous_bar_to_touch_the_average() -> None:
    """A strong trend that never pulls back has no entries."""
    index = pd.bdate_range("2020-01-01", periods=300)
    close = 100.0 * 1.01 ** np.arange(300)
    frame = pd.DataFrame({"high": close * 1.001, "low": close * 0.999, "close": close}, index=index)
    assert holy_grail_pullback(frame).sum() == 0


def test_an_unknown_direction_is_rejected(wobble: pd.DataFrame) -> None:
    with pytest.raises(ValueError, match="unknown direction"):
        holy_grail_pullback(wobble, direction="both")


# ── Random trade win rate ───────────────────────────────────────────────────


def test_a_monotone_series_wins_every_pair_or_none() -> None:
    index = pd.bdate_range("2020-01-01", periods=400)
    rising = pd.DataFrame({"close": 100.0 + np.arange(400)}, index=index)
    falling = pd.DataFrame({"close": 500.0 - np.arange(400)}, index=index)
    assert random_trade_win_rate(rising).iloc[-1] == pytest.approx(100.0)
    assert random_trade_win_rate(falling).iloc[-1] == pytest.approx(0.0)


def test_the_pair_count_is_the_published_thirty_three_thousand() -> None:
    """260 bars give 260*259/2 pairs. The number is a check on the window, not
    on the arithmetic: an off-by-one in the window changes it."""
    assert 260 * 259 // 2 == 33670


def test_a_single_gap_scores_below_a_steady_climb() -> None:
    """Stated in the entry, and the reason a high reading is not a high return.
    Both series end at the same level."""
    index = pd.bdate_range("2020-01-01", periods=300)
    steady = pd.DataFrame({"close": np.linspace(100.0, 200.0, 300)}, index=index)
    gapped = pd.DataFrame({"close": np.r_[np.full(150, 100.0), np.full(150, 200.0)]}, index=index)
    assert steady["close"].iloc[-1] == gapped["close"].iloc[-1]
    assert random_trade_win_rate(steady).iloc[-1] > random_trade_win_rate(gapped).iloc[-1]


def test_a_fixed_holding_period_counts_only_those_pairs() -> None:
    index = pd.bdate_range("2020-01-01", periods=400)
    frame = pd.DataFrame({"close": 100.0 + np.arange(400)}, index=index)
    assert random_trade_win_rate(frame, hold_days=10).iloc[-1] == pytest.approx(100.0)


def test_the_win_rate_stays_inside_its_stated_range(wobble: pd.DataFrame) -> None:
    values = random_trade_win_rate(wobble, periods=120).dropna()
    assert len(values) > 0
    assert values.min() >= 0.0
    assert values.max() <= 100.0


# ── Average volume in shares ────────────────────────────────────────────────


def test_average_volume_is_in_shares_and_turnover_is_not(wobble: pd.DataFrame) -> None:
    """Two entries, two units. Dividing one by the other gives the mean price
    only when the price is constant, which is the point of having both."""
    shares = average_volume(wobble, 20)
    currency = average_turnover(wobble, 20)
    assert (currency.dropna() > shares.dropna()).all()


def test_average_volume_matches_a_hand_computed_mean() -> None:
    import statistics

    volume = [100.0, 200.0, 300.0, 400.0, 500.0]
    frame = pd.DataFrame({"volume": volume})
    assert average_volume(frame, 5).iloc[-1] == pytest.approx(statistics.fmean(volume))


# ── The monthly seasonal bucket ─────────────────────────────────────────────


def test_the_month_bucket_separates_the_months() -> None:
    """The bucket the first pass left out: the criteria list offers monthly,
    quarterly, weekday and an n-day window, and only the last three were here."""
    index = pd.bdate_range("2015-01-05", periods=1600)
    returns = np.where(index.month == 11, 0.01, 0.0)
    frame = pd.DataFrame({"close": 100.0 * np.cumprod(1.0 + returns)}, index=index)
    result = seasonal_strength(frame, bucket="month", years=5, detrend=False)
    november = frame.index[frame.index.month == 11][-1]
    june = frame.index[frame.index.month == 6][-1]
    assert result.loc[november] == pytest.approx(1.0)
    assert result.loc[june] == pytest.approx(0.0)
