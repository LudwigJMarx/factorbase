"""Factors measured against a benchmark, plus Levy's self-referential one.

Every function here except `relative_strength_levy` takes a second argument:
the benchmark close, as a Series. It is aligned to the price frame's index
before anything else happens, and a benchmark that does not overlap the prices
raises rather than producing a column of NaN.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ..errors import InsufficientHistoryError
from ._common import require_columns, simple_moving_average


def _aligned_benchmark(prices: pd.DataFrame, benchmark: pd.Series, factor_id: str) -> pd.Series:
    """Benchmark closes on the price frame's own dates.

    Missing benchmark dates are carried forward, which is right for a holiday
    on one exchange and not the other. What is not tolerated is no overlap at
    all: that is a wiring mistake, and a column of NaN looks like a quiet
    instrument rather than a wrong argument.
    """
    aligned = benchmark.reindex(prices.index).ffill()
    overlap = int(aligned.notna().sum())
    if overlap == 0:
        raise InsufficientHistoryError(factor_id, 1, 0)
    return aligned


def relative_strength_levy(prices: pd.DataFrame, periods: int = 130) -> pd.Series:
    """Close divided by its own moving average. Catalogue id `relative_strength_levy`.

    Levy's measure needs no benchmark: the instrument is compared to its own
    past. Above 1 the price sits above its average. It is in this module
    because screeners file it under relative strength, which is where readers
    look for it, not because it references anything external.
    """
    require_columns(prices, ("close",), "relative_strength_levy")
    return prices["close"] / simple_moving_average(prices["close"], periods)


def relative_strength_line(prices: pd.DataFrame, benchmark: pd.Series) -> pd.Series:
    """Price divided by benchmark, rebased to 100 at the first common bar.

    Catalogue id `relative_strength_line`.

    Rebasing matters. The raw ratio carries the arbitrary level of both series,
    so two instruments cannot be compared on it and the same instrument cannot
    be compared across two loads. Rebasing at the first bar of the loaded window
    at least makes the series readable; it still cannot be ranked across
    instruments, and the entry says so.
    """
    require_columns(prices, ("close",), "relative_strength_line")
    aligned = _aligned_benchmark(prices, benchmark, "relative_strength_line")
    ratio = prices["close"] / aligned
    first = ratio.first_valid_index()
    if first is None:
        raise InsufficientHistoryError("relative_strength_line", 1, 0)
    return ratio / ratio.loc[first] * 100.0


def outperformance(prices: pd.DataFrame, benchmark: pd.Series, periods: int = 250) -> pd.Series:
    """Instrument return minus benchmark return over n bars, in percentage points.

    Catalogue id `outperformance`.

    A difference of two percentage returns, not a ratio of them. The difference
    is what a reader expects from "outperformance" and is additive across
    instruments; the ratio is neither.
    """
    require_columns(prices, ("close",), "outperformance")
    aligned = _aligned_benchmark(prices, benchmark, "outperformance")
    own = (prices["close"] / prices["close"].shift(periods) - 1.0) * 100.0
    market = (aligned / aligned.shift(periods) - 1.0) * 100.0
    return own - market


def beta(prices: pd.DataFrame, benchmark: pd.Series, periods: int = 250) -> pd.Series:
    """Ordinary least squares beta of daily returns against the benchmark. Catalogue id `beta`.

    Simple returns, not log returns. Beta enters portfolio arithmetic through
    weighted sums of simple returns, and estimating it on log returns quietly
    changes what the number means.
    """
    require_columns(prices, ("close",), "beta")
    aligned = _aligned_benchmark(prices, benchmark, "beta")
    own = prices["close"].pct_change()
    market = aligned.pct_change()
    covariance = own.rolling(periods, min_periods=periods).cov(market)
    variance = market.rolling(periods, min_periods=periods).var()
    return covariance / variance


def shrunk_beta(
    prices: pd.DataFrame,
    benchmark: pd.Series,
    volatility_periods: int = 250,
    correlation_periods: int = 1250,
    correlation_horizon: int = 3,
    weight: float = 0.6,
) -> pd.Series:
    """Beta from separate volatility and correlation estimates, shrunk towards one.

    Catalogue id `shrunk_beta`.

    Frazzini and Pedersen estimate the two halves of beta over different
    windows: volatility over a year of daily returns, correlation over five
    years of overlapping multi-day returns, because daily correlations are
    depressed by non-synchronous trading. The estimate is then pulled towards
    one, which is where a randomly chosen stock's beta sits.
    """
    require_columns(prices, ("close",), "shrunk_beta")
    aligned = _aligned_benchmark(prices, benchmark, "shrunk_beta")
    own = np.log(prices["close"]).diff()
    market = np.log(aligned).diff()

    own_volatility = own.rolling(volatility_periods, min_periods=volatility_periods).std(ddof=1)
    market_volatility = market.rolling(volatility_periods, min_periods=volatility_periods).std(
        ddof=1
    )

    own_horizon = own.rolling(correlation_horizon).sum()
    market_horizon = market.rolling(correlation_horizon).sum()
    correlation = own_horizon.rolling(correlation_periods, min_periods=correlation_periods).corr(
        market_horizon
    )

    estimate = correlation * own_volatility / market_volatility
    return weight * estimate + (1.0 - weight) * 1.0


def return_correlation(prices: pd.DataFrame, benchmark: pd.Series, periods: int = 250) -> pd.Series:
    """Rolling correlation of daily returns with the benchmark.

    Catalogue id `return_correlation`.
    """
    require_columns(prices, ("close",), "return_correlation")
    aligned = _aligned_benchmark(prices, benchmark, "return_correlation")
    return (
        prices["close"]
        .pct_change()
        .rolling(periods, min_periods=periods)
        .corr(aligned.pct_change())
    )


def downside_correlation(
    prices: pd.DataFrame, benchmark: pd.Series, periods: int = 250, minimum_days: int = 20
) -> pd.Series:
    """Correlation computed only on bars where the benchmark fell.

    Catalogue id `downside_correlation`.

    The correlation that matters for diversification is the one that holds when
    the market falls, and it is routinely higher than the all-weather figure.
    Windows with fewer than `minimum_days` down bars return NaN rather than a
    correlation estimated from a handful of points.
    """
    require_columns(prices, ("close",), "downside_correlation")
    aligned = _aligned_benchmark(prices, benchmark, "downside_correlation")
    own = prices["close"].pct_change()
    market = aligned.pct_change()
    down = market < 0.0
    own_down = own.where(down)
    market_down = market.where(down)
    count = down.rolling(periods, min_periods=periods).sum()
    correlation = own_down.rolling(periods, min_periods=minimum_days).corr(market_down)
    return correlation.where(count >= minimum_days)


def downside_outperformance(
    prices: pd.DataFrame, benchmark: pd.Series, periods: int = 250, minimum_days: int = 20
) -> pd.Series:
    """Mean excess return on the bars where the benchmark fell, in percentage points.

    Catalogue id `downside_outperformance`.

    Answers how the instrument behaves on the market's bad days, which is a
    different question from how it behaves on average. Positive means it fell
    less than the market did, or rose while the market fell.
    """
    require_columns(prices, ("close",), "downside_outperformance")
    aligned = _aligned_benchmark(prices, benchmark, "downside_outperformance")
    own = prices["close"].pct_change()
    market = aligned.pct_change()
    down = market < 0.0
    excess = (own - market).where(down) * 100.0
    count = down.rolling(periods, min_periods=periods).sum()
    mean = excess.rolling(periods, min_periods=minimum_days).mean()
    return mean.where(count >= minimum_days)


def jensen_alpha(
    prices: pd.DataFrame,
    benchmark: pd.Series,
    periods: int = 250,
    trading_days: int = 250,
    risk_free_rate: float = 0.0,
) -> pd.Series:
    """Annualised intercept of the return regression, in percent. Catalogue id `jensen_alpha`.

    The part of the return the benchmark does not explain. The risk-free rate
    is a constant annual figure here rather than a series, which is a
    simplification the entry states: with a varying rate the intercept would
    also absorb the variation in it.
    """
    require_columns(prices, ("close",), "jensen_alpha")
    aligned = _aligned_benchmark(prices, benchmark, "jensen_alpha")
    daily_free = (1.0 + risk_free_rate / 100.0) ** (1.0 / trading_days) - 1.0
    own = prices["close"].pct_change() - daily_free
    market = aligned.pct_change() - daily_free
    estimated_beta = (
        own.rolling(periods, min_periods=periods).cov(market)
        / market.rolling(periods, min_periods=periods).var()
    )
    intercept = (
        own.rolling(periods, min_periods=periods).mean()
        - estimated_beta * market.rolling(periods, min_periods=periods).mean()
    )
    return ((1.0 + intercept) ** trading_days - 1.0) * 100.0
