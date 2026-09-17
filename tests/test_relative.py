"""Factors measured against a benchmark."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from factorbase.errors import InsufficientHistoryError
from factorbase.factors._common import simple_moving_average
from factorbase.factors.relative import (
    beta,
    downside_correlation,
    downside_outperformance,
    jensen_alpha,
    outperformance,
    relative_strength_levy,
    relative_strength_line,
    return_correlation,
    shrunk_beta,
)


def test_levy_needs_no_benchmark(wobble: pd.DataFrame) -> None:
    expected = wobble["close"] / simple_moving_average(wobble["close"], 130)
    assert np.allclose(relative_strength_levy(wobble, 130).dropna(), expected.dropna())


def test_levy_is_one_when_price_sits_on_its_average() -> None:
    flat = pd.DataFrame({"close": pd.Series([40.0] * 200)})
    assert relative_strength_levy(flat, 130).iloc[-1] == pytest.approx(1.0)


def test_relative_strength_line_starts_at_one_hundred(
    wobble: pd.DataFrame, market: pd.Series
) -> None:
    line = relative_strength_line(wobble, market)
    assert line.iloc[0] == pytest.approx(100.0)


def test_relative_strength_line_rises_when_the_instrument_leads(market: pd.Series) -> None:
    leading = pd.DataFrame({"close": market * 1.002 ** np.arange(len(market))})
    leading.index = market.index
    line = relative_strength_line(leading, market)
    assert line.iloc[-1] > line.iloc[0]


def test_a_benchmark_that_does_not_overlap_raises(wobble: pd.DataFrame) -> None:
    """A column of NaN would look like a quiet instrument rather than a wiring mistake."""
    elsewhere = pd.Series(
        [1.0, 2.0], index=pd.DatetimeIndex(["1990-01-01", "1990-01-02"], name="date")
    )
    with pytest.raises(InsufficientHistoryError):
        outperformance(wobble, elsewhere, periods=10)


def test_outperformance_is_a_difference_not_a_ratio(
    wobble: pd.DataFrame, market: pd.Series
) -> None:
    periods = 100
    own = (wobble["close"].iloc[-1] / wobble["close"].iloc[-1 - periods] - 1.0) * 100.0
    ref = (market.iloc[-1] / market.iloc[-1 - periods] - 1.0) * 100.0
    assert outperformance(wobble, market, periods).iloc[-1] == pytest.approx(own - ref)


def test_outperformance_against_itself_is_zero(wobble: pd.DataFrame) -> None:
    result = outperformance(wobble, wobble["close"], periods=50).dropna()
    assert np.allclose(result, 0.0)


def test_beta_of_a_doubled_series_is_two(geared: pd.DataFrame, market: pd.Series) -> None:
    """Constructed so the answer is known, rather than recomputed from the implementation."""
    assert beta(geared, market, periods=250).iloc[-1] == pytest.approx(2.0)


def test_beta_against_itself_is_one(wobble: pd.DataFrame) -> None:
    assert beta(wobble, wobble["close"], periods=250).iloc[-1] == pytest.approx(1.0)


def test_correlation_of_a_geared_copy_is_one(geared: pd.DataFrame, market: pd.Series) -> None:
    assert return_correlation(geared, market, periods=250).iloc[-1] == pytest.approx(1.0)


def test_correlation_and_beta_answer_different_questions(
    wobble: pd.DataFrame, market: pd.Series
) -> None:
    """Stated in the entry. If they moved together, one of the two would be redundant."""
    correlation = return_correlation(wobble, market, 250).iloc[-1]
    estimated = beta(wobble, market, 250).iloc[-1]
    assert correlation != pytest.approx(estimated)


def test_shrunk_beta_is_pulled_towards_one(geared: pd.DataFrame, market: pd.Series) -> None:
    """Beta is 2 by construction; shrinking with weight 0.6 must land at 1.6."""
    long_market = pd.concat([market] * 4, ignore_index=False)
    long_market.index = pd.bdate_range("2015-01-01", periods=len(long_market))
    returns = long_market.pct_change().fillna(0.0)
    close = 100.0 * (1.0 + 2.0 * returns).cumprod()
    long_geared = pd.DataFrame({"close": close}, index=long_market.index)
    result = shrunk_beta(long_geared, long_market).dropna()
    assert len(result) > 0
    assert result.iloc[-1] == pytest.approx(1.6, abs=0.05)


def test_shrunk_beta_is_undefined_without_five_years(
    geared: pd.DataFrame, market: pd.Series
) -> None:
    """The entry says so. NaN throughout is the honest answer on a short series."""
    assert shrunk_beta(geared, market).notna().sum() == 0


def test_downside_correlation_uses_only_down_bars(wobble: pd.DataFrame, market: pd.Series) -> None:
    periods = 250
    own = wobble["close"].pct_change()
    reference = market.pct_change()
    down = reference < 0.0
    window = slice(len(wobble) - periods, len(wobble))
    expected = own.iloc[window][down.iloc[window]].corr(reference.iloc[window][down.iloc[window]])
    assert downside_correlation(wobble, market, periods).iloc[-1] == pytest.approx(expected)


def test_downside_correlation_is_undefined_on_too_few_down_bars(market: pd.Series) -> None:
    """Eight observations do not make a weak estimate. They make noise in a costume."""
    rising = pd.Series(100.0 * 1.001 ** np.arange(len(market)), index=market.index, name="close")
    frame = pd.DataFrame({"close": rising})
    assert downside_correlation(frame, rising, periods=250, minimum_days=20).isna().all()


def test_downside_outperformance_is_positive_for_a_defensive_instrument(
    market: pd.Series,
) -> None:
    """Half the market's move: on down days it falls half as far, so the excess is positive."""
    returns = market.pct_change().fillna(0.0)
    defensive = pd.DataFrame({"close": 100.0 * (1.0 + 0.5 * returns).cumprod()}, index=market.index)
    assert downside_outperformance(defensive, market, periods=250).iloc[-1] > 0.0


def test_jensen_alpha_of_a_pure_geared_copy_is_zero(
    geared: pd.DataFrame, market: pd.Series
) -> None:
    """All of the return is explained by beta, so nothing is left for alpha."""
    assert jensen_alpha(geared, market, periods=250).iloc[-1] == pytest.approx(0.0, abs=1e-6)


def test_jensen_alpha_differs_from_outperformance(geared: pd.DataFrame, market: pd.Series) -> None:
    """Outperformance credits the geared copy with beating the market. Alpha does not."""
    assert outperformance(geared, market, periods=250).iloc[-1] != pytest.approx(0.0, abs=1e-6)
