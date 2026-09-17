"""Debt, coverage and liquidity."""

from __future__ import annotations

import numpy as np
import pandas as pd

from ._common import require_fields, rows_of, safe_divide
from .valuation import free_cash_flow


def _balance_ratio(
    frame: pd.DataFrame, numerator: str, denominator: str, factor_id: str, period: str
) -> pd.Series:
    require_fields(frame, (numerator, denominator), factor_id)
    rows = rows_of(frame, period, factor_id)
    return safe_divide(rows[numerator], rows[denominator]) * 100.0


def equity_ratio(frame: pd.DataFrame, period: str = "annual") -> pd.Series:
    """Equity over total assets, in percent. Catalogue id `equity_ratio`."""
    return _balance_ratio(frame, "total_equity", "total_assets", "equity_ratio", period)


def liabilities_ratio(frame: pd.DataFrame, period: str = "annual") -> pd.Series:
    """Total liabilities over total assets, in percent. Catalogue id `liabilities_ratio`."""
    return _balance_ratio(frame, "total_liabilities", "total_assets", "liabilities_ratio", period)


def debt_to_assets(frame: pd.DataFrame, period: str = "annual") -> pd.Series:
    """Interest-bearing debt over total assets, in percent. Catalogue id `debt_to_assets`.

    Debt, not liabilities. Trade payables are a liability and are not debt;
    conflating them makes a retailer with fast supplier turnover look leveraged
    when it is the opposite.
    """
    return _balance_ratio(frame, "total_debt", "total_assets", "debt_to_assets", period)


def debt_to_equity(frame: pd.DataFrame, period: str = "annual") -> pd.Series:
    """Interest-bearing debt over equity, in percent. Catalogue id `debt_to_equity`.

    Undefined on negative equity rather than negative. A company with more
    liabilities than assets is not lightly leveraged, which is what the
    negative number would sort as.
    """
    require_fields(frame, ("total_debt", "total_equity"), "debt_to_equity")
    rows = rows_of(frame, period, "debt_to_equity")
    result = safe_divide(rows["total_debt"], rows["total_equity"]) * 100.0
    return result.where(rows["total_equity"] > 0.0)


def net_debt_to_ebitda(frame: pd.DataFrame, period: str = "annual") -> pd.Series:
    """Debt less cash over EBITDA, as a multiple. Catalogue id `net_debt_to_ebitda`.

    The covenant measure. Negative readings are meaningful here and are kept: a
    company with more cash than debt has negative net debt, and that is
    information rather than an error.
    """
    require_fields(frame, ("total_debt", "cash_and_equivalents", "ebitda"), "net_debt_to_ebitda")
    rows = rows_of(frame, period, "net_debt_to_ebitda")
    net_debt = rows["total_debt"] - rows["cash_and_equivalents"]
    return safe_divide(net_debt, rows["ebitda"].where(rows["ebitda"] > 0.0))


def current_ratio(frame: pd.DataFrame, period: str = "annual") -> pd.Series:
    """Current assets over current liabilities, as a multiple. Catalogue id `current_ratio`."""
    require_fields(frame, ("current_assets", "current_liabilities"), "current_ratio")
    rows = rows_of(frame, period, "current_ratio")
    return safe_divide(rows["current_assets"], rows["current_liabilities"])


def quick_ratio(frame: pd.DataFrame, period: str = "annual") -> pd.Series:
    """Current assets less inventory, over current liabilities. Catalogue id `quick_ratio`."""
    require_fields(
        frame, ("current_assets", "inventory", "current_liabilities"), "quick_ratio"
    )
    rows = rows_of(frame, period, "quick_ratio")
    return safe_divide(rows["current_assets"] - rows["inventory"], rows["current_liabilities"])


def cash_ratio(frame: pd.DataFrame, period: str = "annual") -> pd.Series:
    """Cash over current liabilities, as a multiple. Catalogue id `cash_ratio`."""
    require_fields(frame, ("cash_and_equivalents", "current_liabilities"), "cash_ratio")
    rows = rows_of(frame, period, "cash_ratio")
    return safe_divide(rows["cash_and_equivalents"], rows["current_liabilities"])


def interest_coverage(
    frame: pd.DataFrame, period: str = "annual", basis: str = "ebit"
) -> pd.Series:
    """Operating profit or operating cash flow over interest expense. Catalogue id `interest_coverage`.

    A company with no interest expense has infinite coverage, which is true and
    unrankable. It returns NaN here, and the entry says to read a NaN as "no
    debt service" rather than as missing data.
    """
    if basis not in {"ebit", "operating_cash_flow"}:
        raise ValueError(f"unknown basis {basis!r}; expected 'ebit' or 'operating_cash_flow'")
    require_fields(frame, (basis, "interest_expense"), "interest_coverage")
    rows = rows_of(frame, period, "interest_coverage")
    return safe_divide(rows[basis], rows["interest_expense"])


def debt_coverage(
    frame: pd.DataFrame, period: str = "annual", basis: str = "operating_cash_flow"
) -> pd.Series:
    """Cash flow or operating profit over total debt, in percent. Catalogue id `debt_coverage`.

    How much of the debt a year of the business would repay. The inverse of the
    usual debt-to-cash-flow multiple, chosen because it stays finite as debt
    goes to zero and the multiple does not.
    """
    if basis not in {"operating_cash_flow", "ebit", "revenue"}:
        raise ValueError(
            f"unknown basis {basis!r}; expected 'operating_cash_flow', 'ebit' or 'revenue'"
        )
    require_fields(frame, (basis, "total_debt"), "debt_coverage")
    rows = rows_of(frame, period, "debt_coverage")
    return safe_divide(rows[basis], rows["total_debt"]) * 100.0


def long_term_debt_to_working_capital(frame: pd.DataFrame, period: str = "annual") -> pd.Series:
    """Long-term debt over net working capital, as a multiple. Catalogue id `long_term_debt_to_working_capital`.

    Undefined on negative working capital rather than negative, because a
    company funding itself on its suppliers has negative working capital by
    design and the ratio would rank it as conservatively financed.
    """
    require_fields(
        frame,
        ("long_term_debt", "current_assets", "current_liabilities"),
        "long_term_debt_to_working_capital",
    )
    rows = rows_of(frame, period, "long_term_debt_to_working_capital")
    working_capital = rows["current_assets"] - rows["current_liabilities"]
    return safe_divide(rows["long_term_debt"], working_capital.where(working_capital > 0.0))


def ohlson_o_score(frame: pd.DataFrame, period: str = "annual", gnp_deflator: float = 1.0) -> pd.Series:
    """Ohlson's nine-term bankruptcy score. Catalogue id `ohlson_o_score`.

    Higher means more distressed. The coefficients are Ohlson's, fitted on US
    filings from 1970 to 1976, and they have not been refitted since. Treat the
    score as an ordering of relative distress within a comparable universe, not
    as a probability; the probability that comes out of the logistic transform
    is calibrated to a sample nearly fifty years old.

    The size term divides total assets by a GNP price index level. The
    parameter defaults to 1, which leaves assets in nominal currency and makes
    the term comparable only within one point in time. Passing a real deflator
    is the caller's job, and the entry says so rather than hiding a constant.
    """
    required = (
        "total_assets", "total_liabilities", "current_assets", "current_liabilities",
        "net_income", "operating_cash_flow",
    )
    require_fields(frame, required, "ohlson_o_score")
    rows = rows_of(frame, period, "ohlson_o_score")

    assets = rows["total_assets"].where(rows["total_assets"] > 0.0)
    liabilities = rows["total_liabilities"]
    working_capital = rows["current_assets"] - rows["current_liabilities"]
    net_income = rows["net_income"]
    previous_income = net_income.shift(1)

    size = np.log(assets / gnp_deflator)
    leverage = safe_divide(liabilities, assets)
    working_capital_ratio = safe_divide(working_capital, assets)
    liquidity = safe_divide(rows["current_liabilities"], rows["current_assets"])
    insolvent = (liabilities > assets).astype("float64")
    profitability = safe_divide(net_income, assets)
    funds_to_liabilities = safe_divide(rows["operating_cash_flow"], liabilities)
    two_year_loss = ((net_income < 0.0) & (previous_income < 0.0)).astype("float64")
    income_change = safe_divide(
        net_income - previous_income, net_income.abs() + previous_income.abs()
    )

    return (
        -1.32
        - 0.407 * size
        + 6.03 * leverage
        - 1.43 * working_capital_ratio
        + 0.0757 * liquidity
        - 1.72 * insolvent
        - 2.37 * profitability
        - 1.83 * funds_to_liabilities
        + 0.285 * two_year_loss
        - 0.521 * income_change
    )


def ohlson_bankruptcy_probability(
    frame: pd.DataFrame, period: str = "annual", gnp_deflator: float = 1.0
) -> pd.Series:
    """The O-score put through a logistic function, in percent. Catalogue id `ohlson_bankruptcy_probability`.

    Reported because the original paper reports it, and carrying the same
    warning: the calibration is from a 1970s US sample. The ordering it
    produces is identical to the score's, since the logistic transform is
    monotone, so nothing is gained by using this one for ranking.
    """
    score = ohlson_o_score(frame, period, gnp_deflator)
    return 1.0 / (1.0 + np.exp(-score)) * 100.0


def cash_flow_to_debt(frame: pd.DataFrame, period: str = "annual") -> pd.Series:
    """Free cash flow over total debt, in percent. Catalogue id `cash_flow_to_debt`."""
    require_fields(frame, ("total_debt",), "cash_flow_to_debt")
    rows = rows_of(frame, period, "cash_flow_to_debt")
    return safe_divide(free_cash_flow(rows), rows["total_debt"]) * 100.0
