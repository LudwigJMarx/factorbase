"""Absolute figures: size, and the lines other factors are built from."""

from __future__ import annotations

import pandas as pd

from ._common import require_fields, rows_of
from .valuation import as_of
from .valuation import free_cash_flow as _free_cash_flow


def market_capitalisation(frame: pd.DataFrame, market: pd.Series) -> pd.Series:
    """The market series read at each reporting date. Catalogue id `market_capitalisation`.

    Present as a factor because size is a screening criterion in its own right,
    and because a universe filtered on it needs the same as-of join every other
    market-based factor here uses.
    """
    return as_of(market, frame.index)


def revenue(frame: pd.DataFrame, period: str = "ttm") -> pd.Series:
    """Reported revenue for the period, in currency. Catalogue id `revenue`."""
    require_fields(frame, ("revenue",), "revenue")
    return rows_of(frame, period, "revenue")["revenue"]


def net_income(frame: pd.DataFrame, period: str = "ttm") -> pd.Series:
    """Reported net income for the period, in currency. Catalogue id `net_income`."""
    require_fields(frame, ("net_income",), "net_income")
    return rows_of(frame, period, "net_income")["net_income"]


def free_cash_flow(frame: pd.DataFrame, period: str = "ttm") -> pd.Series:
    """Operating cash flow less capital expenditure, in currency. Catalogue id `free_cash_flow`."""
    return _free_cash_flow(rows_of(frame, period, "free_cash_flow"))
