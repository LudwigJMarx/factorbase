"""Selecting a reporting basis, averaging it, and dividing without lying."""

from __future__ import annotations

import numpy as np
import pandas as pd

from ...errors import AmbiguousPeriodError, MissingInputError

PERIODS = ("annual", "quarterly", "ttm")


def require_fields(frame: pd.DataFrame, fields: tuple[str, ...], factor_id: str) -> None:
    missing = tuple(f for f in fields if f not in frame.columns)
    if missing:
        raise MissingInputError(factor_id, missing, tuple(frame.columns))


def rows_of(frame: pd.DataFrame, period: str, factor_id: str) -> pd.DataFrame:
    """The rows on one reporting basis, in period order.

    A frame with no rows of the requested basis returns empty rather than
    falling back to another basis. A quarterly figure presented as an annual
    one is off by a factor of four and nothing in the output would say so.

    A period end appearing twice on the same basis raises. Quarterly and TTM
    rows share their period ends by design and that is fine, because they are
    different bases; a repeat inside one basis is an original filing and its
    amendment, and choosing between them is not this package's decision.
    """
    if period not in PERIODS:
        raise ValueError(f"unknown period {period!r}; expected one of {PERIODS}")
    require_fields(frame, ("period",), factor_id)
    selected = frame[frame["period"] == period].sort_index()
    repeated = selected.index[selected.index.duplicated()]
    if len(repeated):
        raise AmbiguousPeriodError(
            factor_id, period, tuple(str(d.date() if hasattr(d, "date") else d) for d in repeated)
        )
    return selected


def safe_divide(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    """Division that yields NaN where the denominator is zero.

    Not infinity, and not a large number. A price-to-earnings ratio on zero
    earnings is undefined, and every screen that sorts ascending would
    otherwise put those companies at the top.
    """
    return numerator / denominator.where(denominator != 0.0)


def ratio_is_meaningless_when_negative(
    value: pd.Series, denominator: pd.Series, allow_negative: bool
) -> pd.Series:
    """Blank out readings whose denominator went negative, unless asked not to.

    A price-to-earnings ratio computed on a loss is a negative number that
    sorts below every profitable company. Ranking ascending then rewards the
    worst losses in the universe. The default is to return NaN and let the
    caller decide what to do with a loss-making company, because that decision
    is not the ratio's to make.
    """
    if allow_negative:
        return value
    return value.where(denominator > 0.0)


def trailing_mean(series: pd.Series, years: int) -> pd.Series:
    """Mean of the last `years` observations, requiring all of them.

    A five-year average computed from three years is not a five-year average.
    Returning it anyway is how a screen ends up comparing companies on windows
    of different length without ever saying so.
    """
    return series.rolling(window=years, min_periods=years).mean()


def trailing_std(series: pd.Series, years: int) -> pd.Series:
    """Sample standard deviation over the last `years` observations."""
    return series.rolling(window=years, min_periods=years).std(ddof=1)


def dispersion_ratio(
    mean: pd.Series, deviation: pd.Series, relative_floor: float = 1e-9
) -> pd.Series:
    """Mean over dispersion, undefined where the dispersion is numerically nothing.

    Guarding only against an exact zero is not enough. A company whose margin
    is 13.5 percent every single year produces a sample deviation of about
    1e-15 rather than 0, because the values were arrived at by arithmetic. The
    ratio is then 5.9e14, and that company wins every ranking that uses it,
    for a reason that has nothing to do with its business.

    Anything below `relative_floor` times the level counts as no dispersion at
    all and yields NaN. The caller then sees a missing value, which is the
    honest answer for "perfectly steady, ratio undefined", instead of a number
    that sorts first.
    """
    floor = mean.abs() * relative_floor
    return (mean / deviation.where(deviation > floor)).where(deviation.notna())


def growth_rate(
    series: pd.Series, periods: int = 1, allow_negative_base: bool = False
) -> pd.Series:
    """Percentage change over `periods` observations.

    From a negative base the result is meaningless: a loss shrinking from -100
    to -50 computes as a 50 percent decline and reads as deterioration. The
    default blanks those out. Setting `allow_negative_base` returns the number
    anyway, for callers who have their own handling; the entry says what it
    means.
    """
    base = series.shift(periods)
    change = (series / base - 1.0) * 100.0
    if allow_negative_base:
        return change
    return change.where(base > 0.0)


def compound_growth(series: pd.Series, periods: int) -> pd.Series:
    """Compound growth rate per period, in percent, over `periods` steps.

    Undefined from a non-positive base, and undefined where the endpoint is
    negative: a root of a negative number is not a growth rate. Both cases are
    NaN rather than a complex number quietly cast to its real part.
    """
    base = series.shift(periods)
    total = safe_divide(series, base)
    valid = (base > 0.0) & (series > 0.0)
    return ((total ** (1.0 / periods) - 1.0) * 100.0).where(valid)


def stability(series: pd.Series, years: int) -> pd.Series:
    """How straight a line the series has followed, as an R squared from 0 to 1.

    Fitted in log space so that a company growing 10 percent a year scores 1
    regardless of its size. A company with the same average growth delivered in
    one jump scores lower, which is the entire point of a stability measure and
    the reason it is not simply the inverse of the standard deviation.
    """

    def fit(window: np.ndarray) -> float:
        if np.any(window <= 0.0):
            return np.nan
        y = np.log(window)
        x = np.arange(len(y), dtype="float64")
        x_centred = x - x.mean()
        y_centred = y - y.mean()
        total = float((y_centred**2).sum())
        if total == 0.0:
            return 1.0
        slope = float((x_centred * y_centred).sum() / float((x_centred**2).sum()))
        residual = float(((y_centred - slope * x_centred) ** 2).sum())
        return 1.0 - residual / total

    return series.rolling(window=years, min_periods=years).apply(fit, raw=True)
