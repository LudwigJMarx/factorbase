"""Multiples and yields.

Every function here takes two arguments: the accounts and a market series. The
market series is whatever the caller has, daily or otherwise; it is read as of
each reporting date, carrying the last value forward. That is the only sound
join between a series that changes every day and one that changes four times a
year, and doing it here rather than leaving it to the caller is what stops a
ratio being computed from a market value that post-dates the accounts by a
quarter in one place and a day in another.
"""

from __future__ import annotations

import pandas as pd

from ._common import (
    ratio_is_meaningless_when_negative,
    require_fields,
    rows_of,
    safe_divide,
    trailing_mean,
)


def as_of(market: pd.Series, index: pd.Index) -> pd.Series:
    """The market series read at each date in `index`, last value carried forward."""
    combined = market.reindex(market.index.union(index)).ffill()
    return combined.reindex(index)


def _multiple(
    frame: pd.DataFrame,
    market: pd.Series,
    line: str,
    factor_id: str,
    period: str,
    average_years: int,
    allow_negative: bool,
) -> pd.Series:
    require_fields(frame, (line,), factor_id)
    rows = rows_of(frame, period, factor_id)
    value = as_of(market, rows.index)
    multiple = safe_divide(value, rows[line])
    multiple = ratio_is_meaningless_when_negative(multiple, rows[line], allow_negative)
    if average_years > 1:
        return trailing_mean(multiple, average_years)
    return multiple


def price_to_earnings(
    frame: pd.DataFrame,
    market: pd.Series,
    period: str = "ttm",
    average_years: int = 1,
    allow_negative: bool = False,
) -> pd.Series:
    """Market capitalisation over net income. Catalogue id `price_to_earnings`.

    A loss gives a negative multiple, which sorts below every profitable
    company and would be picked first by any screen ranking ascending. The
    default is NaN there, and the entry says so; `allow_negative` returns the
    number for callers who handle it themselves.
    """
    return _multiple(
        frame, market, "net_income", "price_to_earnings", period, average_years, allow_negative
    )


def price_to_book(
    frame: pd.DataFrame, market: pd.Series, period: str = "annual", average_years: int = 1
) -> pd.Series:
    """Market capitalisation over shareholders' equity. Catalogue id `price_to_book`."""
    return _multiple(frame, market, "total_equity", "price_to_book", period, average_years, False)


def price_to_sales(
    frame: pd.DataFrame, market: pd.Series, period: str = "ttm", average_years: int = 1
) -> pd.Series:
    """Market capitalisation over revenue. Catalogue id `price_to_sales`.

    The one multiple that is always defined, because revenue is rarely
    negative. That is its use and its weakness: it ranks a company with no
    profits identically whether the absence is temporary or structural.
    """
    return _multiple(frame, market, "revenue", "price_to_sales", period, average_years, False)


def price_to_free_cash_flow(
    frame: pd.DataFrame, market: pd.Series, period: str = "ttm", average_years: int = 1
) -> pd.Series:
    """Market capitalisation over free cash flow. Catalogue id `price_to_free_cash_flow`."""
    rows = rows_of(frame, period, "price_to_free_cash_flow")
    flow = free_cash_flow(rows)
    value = as_of(market, rows.index)
    multiple = ratio_is_meaningless_when_negative(safe_divide(value, flow), flow, False)
    if average_years > 1:
        return trailing_mean(multiple, average_years)
    return multiple


def free_cash_flow(frame: pd.DataFrame) -> pd.Series:
    """Operating cash flow less capital expenditure, derived when absent.

    Capital expenditure is taken as a positive number, as `inputs.yaml` states.
    Sources that report it negative would otherwise have it added instead of
    subtracted, and the resulting free cash flow would be roughly twice the
    truth for any capital-intensive business.
    """
    if "free_cash_flow" in frame.columns:
        return frame["free_cash_flow"]
    require_fields(frame, ("operating_cash_flow", "capital_expenditure"), "free_cash_flow")
    return frame["operating_cash_flow"] - frame["capital_expenditure"]


def earnings_yield(
    frame: pd.DataFrame, market: pd.Series, period: str = "ttm", average_years: int = 1
) -> pd.Series:
    """Net income over market capitalisation, in percent. Catalogue id `earnings_yield`.

    The inverse of the price-to-earnings ratio, and better behaved. It passes
    through zero smoothly where the multiple goes to infinity, so it can be
    averaged, ranked and combined with other factors without special cases.
    """
    require_fields(frame, ("net_income",), "earnings_yield")
    rows = rows_of(frame, period, "earnings_yield")
    value = as_of(market, rows.index)
    result = safe_divide(rows["net_income"], value) * 100.0
    if average_years > 1:
        return trailing_mean(result, average_years)
    return result


def free_cash_flow_yield(
    frame: pd.DataFrame, market: pd.Series, period: str = "ttm", average_years: int = 1
) -> pd.Series:
    """Free cash flow over market capitalisation, in percent.

    Catalogue id `free_cash_flow_yield`.
    """
    rows = rows_of(frame, period, "free_cash_flow_yield")
    value = as_of(market, rows.index)
    result = safe_divide(free_cash_flow(rows), value) * 100.0
    if average_years > 1:
        return trailing_mean(result, average_years)
    return result


def enterprise_value(frame: pd.DataFrame, market: pd.Series, period: str = "annual") -> pd.Series:
    """Market capitalisation plus total debt less cash.

    Catalogue id `enterprise_value`.

    Selects its reporting basis, for the same reason market capitalisation
    does: a frame carrying annual, quarterly and TTM rows together has repeated
    period ends, and the as-of join cannot reindex onto a duplicated index. The
    enterprise multiples call `_enterprise_value_of` on rows they have already
    selected.
    """
    require_fields(frame, ("total_debt", "cash_and_equivalents"), "enterprise_value")
    return _enterprise_value_of(rows_of(frame, period, "enterprise_value"), market)


def _enterprise_value_of(rows: pd.DataFrame, market: pd.Series) -> pd.Series:
    """Enterprise value for rows already narrowed to one reporting basis."""
    value = as_of(market, rows.index)
    return value + rows["total_debt"] - rows["cash_and_equivalents"]


def _enterprise_multiple(
    frame: pd.DataFrame,
    market: pd.Series,
    line: str,
    factor_id: str,
    period: str,
    allow_negative: bool = False,
) -> pd.Series:
    require_fields(frame, (line,), factor_id)
    rows = rows_of(frame, period, factor_id)
    value = _enterprise_value_of(rows, market)
    return ratio_is_meaningless_when_negative(
        safe_divide(value, rows[line]), rows[line], allow_negative
    )


def ev_to_ebit(frame: pd.DataFrame, market: pd.Series, period: str = "ttm") -> pd.Series:
    """Enterprise value over operating income. Catalogue id `ev_to_ebit`.

    Preferred over price-to-earnings when comparing companies with different
    leverage: both numerator and denominator are before financing, so the
    capital structure cancels instead of distorting.
    """
    return _enterprise_multiple(frame, market, "ebit", "ev_to_ebit", period)


def ev_to_ebitda(frame: pd.DataFrame, market: pd.Series, period: str = "ttm") -> pd.Series:
    """Enterprise value over EBITDA. Catalogue id `ev_to_ebitda`."""
    return _enterprise_multiple(frame, market, "ebitda", "ev_to_ebitda", period)


def ev_to_sales(frame: pd.DataFrame, market: pd.Series, period: str = "ttm") -> pd.Series:
    """Enterprise value over revenue. Catalogue id `ev_to_sales`."""
    return _enterprise_multiple(frame, market, "revenue", "ev_to_sales", period)


def ev_to_free_cash_flow(frame: pd.DataFrame, market: pd.Series, period: str = "ttm") -> pd.Series:
    """Enterprise value over free cash flow. Catalogue id `ev_to_free_cash_flow`."""
    rows = rows_of(frame, period, "ev_to_free_cash_flow")
    flow = free_cash_flow(rows)
    value = _enterprise_value_of(rows, market)
    return ratio_is_meaningless_when_negative(safe_divide(value, flow), flow, False)


def magic_formula_earnings_yield(
    frame: pd.DataFrame, market: pd.Series, period: str = "ttm"
) -> pd.Series:
    """Operating income over enterprise value, in percent.

    Catalogue id `magic_formula_earnings_yield`.

    Greenblatt's earnings yield, which is EBIT over enterprise value rather
    than net income over market capitalisation. Both halves sit before
    financing, so two companies with the same operations and different debt
    rank together instead of apart.
    """
    require_fields(frame, ("ebit",), "magic_formula_earnings_yield")
    rows = rows_of(frame, period, "magic_formula_earnings_yield")
    return safe_divide(rows["ebit"], _enterprise_value_of(rows, market)) * 100.0


def peg_ratio(
    frame: pd.DataFrame, market: pd.Series, period: str = "ttm", growth_periods: int = 4
) -> pd.Series:
    """Price-to-earnings divided by the earnings growth rate. Catalogue id `peg_ratio`.

    Undefined where growth is not positive, which is most of the time for most
    companies and is the reason the measure is quieter than its reputation. A
    negative PEG from a negative growth rate reads as cheap and means the
    opposite.
    """
    require_fields(frame, ("net_income",), "peg_ratio")
    rows = rows_of(frame, period, "peg_ratio")
    value = as_of(market, rows.index)
    multiple = ratio_is_meaningless_when_negative(
        safe_divide(value, rows["net_income"]), rows["net_income"], False
    )
    base = rows["net_income"].shift(growth_periods)
    growth = ((rows["net_income"] / base - 1.0) * 100.0).where(base > 0.0)
    return safe_divide(multiple, growth.where(growth > 0.0))


def dividend_yield(
    frame: pd.DataFrame,
    market: pd.Series,
    period: str = "annual",
    average_years: int = 1,
    basis: str = "paid",
    base: str = "market_cap",
) -> pd.Series:
    """Dividends over market capitalisation, in percent. Catalogue id `dividend_yield`.

    `basis` picks between what was paid over the period and what has been
    declared for it. The two differ by up to a year in timing and the
    difference is systematic, not noise: a company that has announced a cut
    still shows the old yield on the paid basis.

    `base` divides by enterprise value instead of market capitalisation. That
    asks what the dividend yields on the whole capital structure rather than on
    the equity alone, so a leveraged company's yield falls towards what it
    actually costs to own the business free of its debt. The two readings
    diverge exactly where the leverage is, which is where a yield screen is
    most likely to be picking up risk and calling it income.
    """
    if basis not in {"paid", "declared"}:
        raise ValueError(f"unknown basis {basis!r}; expected 'paid' or 'declared'")
    if base not in {"market_cap", "enterprise_value"}:
        raise ValueError(f"unknown base {base!r}; expected 'market_cap' or 'enterprise_value'")
    rows = rows_of(frame, period, "dividend_yield")
    if base == "enterprise_value":
        value = _enterprise_value_of(rows, market)
    else:
        value = as_of(market, rows.index)
    if basis == "paid" and "dividends_paid" in rows.columns:
        total = rows["dividends_paid"]
    else:
        field = "dividend_per_share_paid" if basis == "paid" else "dividend_per_share_declared"
        require_fields(rows, (field, "shares_outstanding"), "dividend_yield")
        total = rows[field] * rows["shares_outstanding"]
    result = safe_divide(total, value) * 100.0
    if average_years > 1:
        return trailing_mean(result, average_years)
    return result


def payout_ratio(frame: pd.DataFrame, period: str = "annual", average_years: int = 1) -> pd.Series:
    """Dividends over net income, in percent. Catalogue id `payout_ratio`.

    Undefined on a loss rather than negative. A company paying a dividend out
    of reserves in a loss year has a payout ratio that is not meaningfully a
    number, and the negative reading it would otherwise produce sorts as though
    the company were retaining everything.
    """
    require_fields(frame, ("dividends_paid", "net_income"), "payout_ratio")
    rows = rows_of(frame, period, "payout_ratio")
    result = safe_divide(rows["dividends_paid"], rows["net_income"]) * 100.0
    result = result.where(rows["net_income"] > 0.0)
    if average_years > 1:
        return trailing_mean(result, average_years)
    return result


def market_cap_to_research(
    frame: pd.DataFrame, market: pd.Series, period: str = "annual"
) -> pd.Series:
    """Market capitalisation over annual R&D spending.

    Catalogue id `market_cap_to_research`.

    How many years of the current research budget the market is paying for.
    Low readings are cheap only if the research is worth anything, which this
    says nothing about: a company that has cut R&D to nothing reads as
    spectacularly cheap right up to the point the pipeline empties.
    """
    require_fields(frame, ("research_and_development",), "market_cap_to_research")
    rows = rows_of(frame, period, "market_cap_to_research")
    spending = rows["research_and_development"]
    value = as_of(market, rows.index)
    return ratio_is_meaningless_when_negative(safe_divide(value, spending), spending, False)


def market_cap_to_debt(frame: pd.DataFrame, market: pd.Series, period: str = "annual") -> pd.Series:
    """Market capitalisation over interest-bearing debt.

    Catalogue id `market_cap_to_debt`.

    How much equity cushion stands in front of the lenders, at market prices
    rather than at book. It moves with the share price where every
    balance-sheet leverage ratio moves only when the accounts are published,
    which is what makes it worth having alongside them and useless as a
    substitute for them.

    A company with no debt has no ratio. That is NaN here rather than infinity,
    and reads as "nothing to cover".
    """
    require_fields(frame, ("total_debt",), "market_cap_to_debt")
    rows = rows_of(frame, period, "market_cap_to_debt")
    debt = rows["total_debt"]
    value = as_of(market, rows.index)
    return ratio_is_meaningless_when_negative(safe_divide(value, debt), debt, False)
