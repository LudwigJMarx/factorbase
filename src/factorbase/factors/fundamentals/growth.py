"""Growth rates, compound growth and how steady the growth was."""

from __future__ import annotations

import pandas as pd

from ._common import (
    compound_growth,
    dispersion_ratio,
    growth_rate,
    require_fields,
    rows_of,
    stability,
    trailing_mean,
    trailing_std,
)
from .valuation import free_cash_flow

_LINES = {
    "revenue": "revenue",
    "net_income": "net_income",
    "eps": "eps_diluted",
    "ebit": "ebit",
    "ebitda": "ebitda",
    "equity": "total_equity",
    "operating_cash_flow": "operating_cash_flow",
    "dividend": "dividend_per_share_paid",
}


def _line(frame: pd.DataFrame, item: str, factor_id: str, period: str) -> pd.Series:
    """Pick the column a growth factor is measured on, by a short name."""
    if item == "free_cash_flow":
        return free_cash_flow(rows_of(frame, period, factor_id))
    if item not in _LINES:
        allowed = ", ".join(sorted([*_LINES, "free_cash_flow"]))
        raise ValueError(f"unknown item {item!r}; expected one of {allowed}")
    column = _LINES[item]
    require_fields(frame, (column,), factor_id)
    return rows_of(frame, period, factor_id)[column]


def growth(
    frame: pd.DataFrame,
    item: str = "revenue",
    period: str = "ttm",
    periods: int = 4,
    allow_negative_base: bool = False,
) -> pd.Series:
    """Percentage change of a reported line over n periods. Catalogue id `growth`.

    From a negative base the number is not a growth rate. A loss shrinking from
    -100 to -50 computes as -50 percent and reads as deterioration when it is
    an improvement. Those readings are NaN by default.

    `periods` counts rows of the chosen basis, not months. Four quarterly rows
    is a year; four annual rows is four years. The entry says so because the
    same argument means different things under different bases and nothing in
    the output would reveal the mistake.
    """
    series = _line(frame, item, "growth", period)
    return growth_rate(series, periods, allow_negative_base)


def compound_annual_growth(
    frame: pd.DataFrame, item: str = "revenue", period: str = "annual", years: int = 5
) -> pd.Series:
    """Compound growth per year of a reported line, in percent.

    Catalogue id `compound_annual_growth`.

    Undefined from a non-positive base and undefined where the endpoint is
    negative, because a root of a negative number is not a growth rate. Both
    are NaN rather than a complex value silently reduced to its real part.
    """
    series = _line(frame, item, "compound_annual_growth", period)
    return compound_growth(series, years)


def growth_stability(
    frame: pd.DataFrame, item: str = "revenue", period: str = "annual", years: int = 5
) -> pd.Series:
    """How straight a line the reported series has followed, from 0 to 1.

    Catalogue id `growth_stability`.

    Fitted in log space, so a company compounding at a steady 10 percent scores
    1 whatever its size. A company with the same total growth delivered in one
    jump scores lower. This is what separates it from the inverse of a standard
    deviation, which would rank the jump and a steady climb by dispersion alone.
    """
    series = _line(frame, item, "growth_stability", period)
    return stability(series, years)


def absolute_growth(
    frame: pd.DataFrame, item: str = "revenue", period: str = "annual", periods: int = 5
) -> pd.Series:
    """Change of a reported line in currency over n periods. Catalogue id `absolute_growth`.

    In currency rather than percent, which makes it useless across instruments
    and useful within one: it is the number that says whether a percentage
    growth rate was earned on a base worth caring about.
    """
    series = _line(frame, item, "absolute_growth", period)
    return series - series.shift(periods)


def growth_consistency(
    frame: pd.DataFrame, item: str = "revenue", period: str = "annual", years: int = 5
) -> pd.Series:
    """Mean growth divided by its own standard deviation. Catalogue id `growth_consistency`.

    A company growing 8 percent every year and one averaging 8 percent between
    -20 and +40 are different businesses. This says which is which; the mean
    alone does not.
    """
    series = _line(frame, item, "growth_consistency", period)
    rates = growth_rate(series, 1, allow_negative_base=False)
    return dispersion_ratio(trailing_mean(rates, years), trailing_std(rates, years))


def sequential_growth(
    frame: pd.DataFrame, item: str = "revenue", allow_negative_base: bool = False
) -> pd.Series:
    """Percentage change against the immediately preceding quarter.

    Catalogue id `sequential_growth`.

    Quarter on quarter, not against the year-ago quarter. It picks up an
    inflection a year earlier than the year-on-year figure and is worthless for
    a seasonal business, where the swing between quarters is the season and not
    the trend.
    """
    series = _line(frame, item, "sequential_growth", "quarterly")
    return growth_rate(series, 1, allow_negative_base)


def year_on_year_quarterly_growth(
    frame: pd.DataFrame, item: str = "revenue", allow_negative_base: bool = False
) -> pd.Series:
    """Percentage change against the same quarter a year earlier.

    Catalogue id `year_on_year_quarterly_growth`.

    The seasonal counterpart to sequential growth: comparing like quarters
    removes the season and, with it, the ability to see a turn inside the year.
    """
    series = _line(frame, item, "year_on_year_quarterly_growth", "quarterly")
    return growth_rate(series, 4, allow_negative_base)
