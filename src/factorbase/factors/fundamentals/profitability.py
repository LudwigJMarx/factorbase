"""Margins and returns on capital."""

from __future__ import annotations

import pandas as pd

from ._common import (
    dispersion_ratio,
    require_fields,
    rows_of,
    safe_divide,
    trailing_mean,
    trailing_std,
)


def _margin(
    frame: pd.DataFrame,
    line: str,
    factor_id: str,
    period: str,
    average_years: int,
) -> pd.Series:
    require_fields(frame, (line, "revenue"), factor_id)
    rows = rows_of(frame, period, factor_id)
    margin = safe_divide(rows[line], rows["revenue"]) * 100.0
    if average_years > 1:
        return trailing_mean(margin, average_years)
    return margin


def gross_margin(frame: pd.DataFrame, period: str = "annual", average_years: int = 1) -> pd.Series:
    """Gross profit over revenue, in percent. Catalogue id `gross_margin`."""
    return _margin(frame, "gross_profit", "gross_margin", period, average_years)


def ebit_margin(frame: pd.DataFrame, period: str = "annual", average_years: int = 1) -> pd.Series:
    """Operating income over revenue, in percent. Catalogue id `ebit_margin`."""
    return _margin(frame, "ebit", "ebit_margin", period, average_years)


def ebitda_margin(frame: pd.DataFrame, period: str = "annual", average_years: int = 1) -> pd.Series:
    """EBITDA over revenue, in percent. Catalogue id `ebitda_margin`."""
    return _margin(frame, "ebitda", "ebitda_margin", period, average_years)


def pretax_margin(frame: pd.DataFrame, period: str = "annual", average_years: int = 1) -> pd.Series:
    """Pretax income over revenue, in percent. Catalogue id `pretax_margin`."""
    return _margin(frame, "pretax_income", "pretax_margin", period, average_years)


def net_margin(frame: pd.DataFrame, period: str = "annual", average_years: int = 1) -> pd.Series:
    """Net income over revenue, in percent. Catalogue id `net_margin`."""
    return _margin(frame, "net_income", "net_margin", period, average_years)


def net_margin_stability(frame: pd.DataFrame, years: int = 5) -> pd.Series:
    """Mean net margin divided by its own standard deviation. Catalogue id `net_margin_stability`.

    A company at 10 percent every year and one averaging 10 percent between 2
    and 18 are not the same business. Dividing the level by the dispersion says
    so in one number; a mean on its own does not.
    """
    margin = net_margin(frame, period="annual", average_years=1)
    return dispersion_ratio(trailing_mean(margin, years), trailing_std(margin, years))


def net_margin_change(frame: pd.DataFrame, years: int = 5) -> pd.Series:
    """Change in net margin over n years, in percentage points. Catalogue id `net_margin_change`.

    Percentage points, not percent. A margin going from 2 to 4 percent has
    doubled, which is true and useless: as a percentage change it outranks a
    company going from 20 to 30, which is the larger move in every sense that
    matters to the income statement.
    """
    margin = net_margin(frame, period="annual", average_years=1)
    return margin - margin.shift(years)


def return_on_equity(
    frame: pd.DataFrame,
    period: str = "annual",
    average_years: int = 1,
    average_balance: bool = True,
) -> pd.Series:
    """Net income over equity, in percent. Catalogue id `return_on_equity`.

    The denominator is the average of this period's and last period's equity
    by default. Income accrues over a period while equity is a snapshot at its
    end; dividing a flow by a closing stock overstates the return of any
    company that raised capital during the year.
    """
    require_fields(frame, ("net_income", "total_equity"), "return_on_equity")
    rows = rows_of(frame, period, "return_on_equity")
    equity = rows["total_equity"]
    if average_balance:
        equity = (equity + equity.shift(1)) / 2.0
    result = safe_divide(rows["net_income"], equity) * 100.0
    if average_years > 1:
        return trailing_mean(result, average_years)
    return result


def return_on_assets(
    frame: pd.DataFrame,
    period: str = "annual",
    average_years: int = 1,
    average_balance: bool = True,
) -> pd.Series:
    """Net income over total assets, in percent. Catalogue id `return_on_assets`."""
    require_fields(frame, ("net_income", "total_assets"), "return_on_assets")
    rows = rows_of(frame, period, "return_on_assets")
    assets = rows["total_assets"]
    if average_balance:
        assets = (assets + assets.shift(1)) / 2.0
    result = safe_divide(rows["net_income"], assets) * 100.0
    if average_years > 1:
        return trailing_mean(result, average_years)
    return result


def invested_capital(frame: pd.DataFrame) -> pd.Series:
    """Equity plus debt less cash, derived when the source does not supply it.

    Every data vendor defines invested capital differently, which is why the
    derivation is written here instead of assumed. When the frame carries its
    own `invested_capital` column that one is used unchanged.
    """
    if "invested_capital" in frame.columns:
        return frame["invested_capital"]
    require_fields(
        frame, ("total_equity", "total_debt", "cash_and_equivalents"), "invested_capital"
    )
    return frame["total_equity"] + frame["total_debt"] - frame["cash_and_equivalents"]


def return_on_invested_capital(
    frame: pd.DataFrame,
    period: str = "annual",
    average_years: int = 1,
    tax_rate: float = 25.0,
    average_balance: bool = True,
) -> pd.Series:
    """After-tax operating profit over invested capital, in percent.

    Catalogue id `return_on_invested_capital`.

    NOPAT over capital, not net income over capital. The numerator has to be
    the return to all providers of capital, because the denominator is what
    all of them put in; using net income mixes a post-interest figure with a
    pre-interest base and flatters leveraged companies.

    The tax rate is a flat assumption, stated as a parameter. Deriving it from
    the reported tax charge is more accurate in a normal year and wildly wrong
    in a year with a one-off credit, which is exactly the year a screen would
    pick up.
    """
    require_fields(frame, ("ebit",), "return_on_invested_capital")
    rows = rows_of(frame, period, "return_on_invested_capital")
    nopat = rows["ebit"] * (1.0 - tax_rate / 100.0)
    capital = invested_capital(rows)
    if average_balance:
        capital = (capital + capital.shift(1)) / 2.0
    result = safe_divide(nopat, capital) * 100.0
    if average_years > 1:
        return trailing_mean(result, average_years)
    return result


def magic_formula_return_on_capital(frame: pd.DataFrame, period: str = "annual") -> pd.Series:
    """EBIT over net working capital plus net fixed assets, in percent.

    Catalogue id `magic_formula_return_on_capital`.

    Greenblatt's version, and deliberately not the same as return on invested
    capital. It is pretax and it excludes goodwill, so it measures what the
    operating business earns on the tangible capital it actually needs, rather
    than on what was paid for it.
    """
    require_fields(
        frame,
        ("ebit", "current_assets", "current_liabilities", "total_assets"),
        "magic_formula_return_on_capital",
    )
    rows = rows_of(frame, period, "magic_formula_return_on_capital")
    working_capital = rows["current_assets"] - rows["current_liabilities"]
    fixed_assets = rows["total_assets"] - rows["current_assets"]
    return safe_divide(rows["ebit"], working_capital + fixed_assets) * 100.0


def rule_of_forty(frame: pd.DataFrame, period: str = "ttm") -> pd.Series:
    """Revenue growth plus EBITDA margin, both in percent. Catalogue id `rule_of_forty`.

    Adding a growth rate to a margin is dimensionally odd and the measure is
    used anyway, because the trade-off it encodes is real: a software company
    may buy growth with margin or margin with growth, and forty is the line
    below which it is doing neither well. It is a heuristic for one industry
    and travels badly outside it.
    """
    require_fields(frame, ("revenue", "ebitda"), "rule_of_forty")
    rows = rows_of(frame, period, "rule_of_forty")
    growth = (rows["revenue"] / rows["revenue"].shift(4) - 1.0) * 100.0
    margin = safe_divide(rows["ebitda"], rows["revenue"]) * 100.0
    return growth + margin


def research_intensity(
    frame: pd.DataFrame, base: str = "revenue", period: str = "annual"
) -> pd.Series:
    """R&D spending over revenue or over assets, in percent. Catalogue id `research_intensity`."""
    if base not in {"revenue", "total_assets"}:
        raise ValueError(f"unknown base {base!r}; expected 'revenue' or 'total_assets'")
    require_fields(frame, ("research_and_development", base), "research_intensity")
    rows = rows_of(frame, period, "research_intensity")
    return safe_divide(rows["research_and_development"], rows[base]) * 100.0
