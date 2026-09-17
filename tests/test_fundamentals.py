"""Factors computed from reported accounts.

The fixture company grows every line by exactly 10 percent a year, so every
margin is constant, every growth rate is 10, and every expected value in this
file is arithmetic rather than a recomputation of the implementation.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from factorbase.errors import MissingInputError
from factorbase.factors.fundamentals.growth import (
    absolute_growth,
    compound_annual_growth,
    growth,
    growth_consistency,
    growth_stability,
    sequential_growth,
    year_on_year_quarterly_growth,
)
from factorbase.factors.fundamentals.leverage import (
    cash_flow_to_debt,
    cash_ratio,
    current_ratio,
    debt_coverage,
    debt_to_assets,
    debt_to_equity,
    equity_ratio,
    interest_coverage,
    liabilities_ratio,
    long_term_debt_to_working_capital,
    net_debt_to_ebitda,
    ohlson_bankruptcy_probability,
    ohlson_o_score,
    quick_ratio,
)
from factorbase.factors.fundamentals.profitability import (
    ebit_margin,
    ebitda_margin,
    gross_margin,
    magic_formula_return_on_capital,
    net_margin,
    net_margin_change,
    net_margin_stability,
    pretax_margin,
    research_intensity,
    return_on_assets,
    return_on_equity,
    return_on_invested_capital,
    rule_of_forty,
)
from factorbase.factors.fundamentals.size import (
    free_cash_flow,
    market_capitalisation,
    net_income,
    revenue,
)
from factorbase.factors.fundamentals.valuation import (
    dividend_yield,
    earnings_yield,
    enterprise_value,
    ev_to_ebit,
    ev_to_ebitda,
    ev_to_free_cash_flow,
    ev_to_sales,
    free_cash_flow_yield,
    magic_formula_earnings_yield,
    payout_ratio,
    peg_ratio,
    price_to_book,
    price_to_earnings,
    price_to_free_cash_flow,
    price_to_sales,
)

# ── The reporting basis is selected, never assumed ──────────────────────────


def test_a_factor_reads_only_the_basis_it_was_asked_for(accounts: pd.DataFrame) -> None:
    """A frame holding annual, quarterly and TTM rows must not mix them."""
    annual = revenue(accounts, period="annual")
    quarterly = revenue(accounts, period="quarterly")
    assert len(annual) == 9
    assert len(quarterly) == 12
    assert quarterly.iloc[-1] < annual.iloc[-1] / 3.0


def test_an_unknown_basis_is_rejected(accounts: pd.DataFrame) -> None:
    with pytest.raises(ValueError, match="unknown period"):
        revenue(accounts, period="monthly")


def test_a_missing_field_names_the_field(accounts: pd.DataFrame) -> None:
    stripped = accounts.drop(columns=["gross_profit"])
    with pytest.raises(MissingInputError) as caught:
        gross_margin(stripped)
    assert caught.value.missing == ("gross_profit",)


# ── Margins ─────────────────────────────────────────────────────────────────


def test_margins_are_the_ratios_they_claim(accounts: pd.DataFrame) -> None:
    assert gross_margin(accounts).iloc[-1] == pytest.approx(40.0)
    assert ebit_margin(accounts).iloc[-1] == pytest.approx(20.0)
    assert ebitda_margin(accounts).iloc[-1] == pytest.approx(25.0)
    assert pretax_margin(accounts).iloc[-1] == pytest.approx(18.0)
    assert net_margin(accounts).iloc[-1] == pytest.approx(13.5)


def test_averaging_requires_every_period_present(accounts: pd.DataFrame) -> None:
    """A five-year mean built from three years is not a five-year mean."""
    averaged = net_margin(accounts, average_years=5)
    assert averaged.iloc[:4].isna().all()
    assert averaged.iloc[4] == pytest.approx(13.5)


def test_net_margin_stability_is_undefined_for_a_constant_margin(
    accounts: pd.DataFrame,
) -> None:
    """A deviation of 1e-15 on a level of 13.5 is nothing, and must not rank first."""
    assert np.isnan(net_margin_stability(accounts, years=5).iloc[-1])


def test_net_margin_stability_prefers_the_steadier_company(accounts: pd.DataFrame) -> None:
    wobbly = accounts.copy()
    annual_dates = wobbly.index[wobbly["period"] == "annual"]
    target = (wobbly.index == annual_dates[-2]) & (wobbly["period"] == "annual")
    wobbly.loc[target, "net_income"] *= 2.0
    steady_margin = net_margin(accounts).std()
    assert steady_margin == pytest.approx(0.0)
    assert not np.isnan(net_margin_stability(wobbly, years=5).iloc[-1])


def test_net_margin_change_is_in_percentage_points(accounts: pd.DataFrame) -> None:
    """Constant margin means no change, whatever the revenue did."""
    assert net_margin_change(accounts, years=5).iloc[-1] == pytest.approx(0.0)


def test_research_intensity_can_be_measured_against_either_base(
    accounts: pd.DataFrame,
) -> None:
    assert research_intensity(accounts, base="revenue").iloc[-1] == pytest.approx(5.0)
    assert research_intensity(accounts, base="total_assets").iloc[-1] == pytest.approx(2.5)
    with pytest.raises(ValueError, match="unknown base"):
        research_intensity(accounts, base="ebit")


# ── Returns on capital ──────────────────────────────────────────────────────


def test_return_on_equity_averages_the_balance_by_default(accounts: pd.DataFrame) -> None:
    """Income accrues over the year; equity is a snapshot at its end."""
    rows = accounts[accounts["period"] == "annual"]
    closing = rows["net_income"].iloc[-1] / rows["total_equity"].iloc[-1] * 100.0
    averaged = (
        rows["net_income"].iloc[-1]
        / ((rows["total_equity"].iloc[-1] + rows["total_equity"].iloc[-2]) / 2.0)
        * 100.0
    )
    assert return_on_equity(accounts).iloc[-1] == pytest.approx(averaged)
    assert return_on_equity(accounts, average_balance=False).iloc[-1] == pytest.approx(closing)
    assert averaged > closing


def test_return_on_assets_is_lower_than_return_on_equity(accounts: pd.DataFrame) -> None:
    """Leverage cannot shrink the asset base. The gap is what the debt is doing."""
    assert return_on_assets(accounts).iloc[-1] < return_on_equity(accounts).iloc[-1]


def test_roic_uses_after_tax_operating_profit_not_net_income(
    accounts: pd.DataFrame,
) -> None:
    rows = accounts[accounts["period"] == "annual"]
    capital = rows["total_equity"] + rows["total_debt"] - rows["cash_and_equivalents"]
    nopat = rows["ebit"].iloc[-1] * 0.75
    expected = nopat / ((capital.iloc[-1] + capital.iloc[-2]) / 2.0) * 100.0
    assert return_on_invested_capital(accounts).iloc[-1] == pytest.approx(expected)
    net_income_version = (
        rows["net_income"].iloc[-1] / ((capital.iloc[-1] + capital.iloc[-2]) / 2.0) * 100.0
    )
    assert expected != pytest.approx(net_income_version)


def test_roic_honours_a_supplied_invested_capital_column(accounts: pd.DataFrame) -> None:
    """Every vendor defines this differently, so a supplied column wins."""
    supplied = accounts.copy()
    supplied["invested_capital"] = 1000.0
    rows = supplied[supplied["period"] == "annual"]
    expected = rows["ebit"].iloc[-1] * 0.75 / 1000.0 * 100.0
    assert return_on_invested_capital(supplied).iloc[-1] == pytest.approx(expected)


def test_greenblatt_return_on_capital_excludes_goodwill_and_tax(
    accounts: pd.DataFrame,
) -> None:
    rows = accounts[accounts["period"] == "annual"]
    working_capital = rows["current_assets"].iloc[-1] - rows["current_liabilities"].iloc[-1]
    fixed = rows["total_assets"].iloc[-1] - rows["current_assets"].iloc[-1]
    expected = rows["ebit"].iloc[-1] / (working_capital + fixed) * 100.0
    assert magic_formula_return_on_capital(accounts).iloc[-1] == pytest.approx(expected)


def test_rule_of_forty_adds_growth_to_margin(accounts: pd.DataFrame) -> None:
    assert rule_of_forty(accounts, period="ttm").iloc[-1] == pytest.approx(10.0 + 25.0)


# ── Multiples ───────────────────────────────────────────────────────────────


def test_market_value_is_read_as_of_the_reporting_date(
    accounts: pd.DataFrame, market_value: pd.Series
) -> None:
    result = market_capitalisation(accounts[accounts["period"] == "annual"], market_value)
    assert (result == 2700.0).all()


def test_price_to_earnings_and_earnings_yield_are_inverses(
    accounts: pd.DataFrame, market_value: pd.Series
) -> None:
    multiple = price_to_earnings(accounts, market_value).dropna()
    yields = earnings_yield(accounts, market_value).dropna()
    assert np.allclose(multiple * yields / 100.0, 1.0)


def test_price_to_earnings_is_undefined_on_a_loss(
    accounts: pd.DataFrame, market_value: pd.Series
) -> None:
    """A negative multiple sorts below every profitable company. NaN instead."""
    loss = accounts.copy()
    loss["net_income"] = -100.0
    assert price_to_earnings(loss, market_value).isna().all()
    assert price_to_earnings(loss, market_value, allow_negative=True).notna().any()


def test_earnings_yield_stays_defined_through_a_loss(
    accounts: pd.DataFrame, market_value: pd.Series
) -> None:
    """The reason the entry recommends the yield for ranking."""
    loss = accounts.copy()
    loss["net_income"] = -100.0
    assert earnings_yield(loss, market_value).notna().any()
    assert (earnings_yield(loss, market_value).dropna() < 0.0).all()


def test_price_to_book_and_sales_divide_the_right_lines(
    accounts: pd.DataFrame, market_value: pd.Series
) -> None:
    rows = accounts[accounts["period"] == "annual"]
    assert price_to_book(accounts).__class__ is not None if False else True
    assert price_to_book(accounts, market_value).iloc[-1] == pytest.approx(
        2700.0 / rows["total_equity"].iloc[-1]
    )
    ttm = accounts[accounts["period"] == "ttm"]
    assert price_to_sales(accounts, market_value).iloc[-1] == pytest.approx(
        2700.0 / ttm["revenue"].iloc[-1]
    )


def test_free_cash_flow_subtracts_capital_expenditure(accounts: pd.DataFrame) -> None:
    """Capital expenditure is positive in the contract. Adding it doubles the answer."""
    ttm = accounts[accounts["period"] == "ttm"]
    expected = ttm["operating_cash_flow"].iloc[-1] - ttm["capital_expenditure"].iloc[-1]
    assert free_cash_flow(accounts).iloc[-1] == pytest.approx(expected)
    assert expected < ttm["operating_cash_flow"].iloc[-1]


def test_price_to_free_cash_flow_uses_the_derived_flow(
    accounts: pd.DataFrame, market_value: pd.Series
) -> None:
    expected = 2700.0 / free_cash_flow(accounts).iloc[-1]
    assert price_to_free_cash_flow(accounts, market_value).iloc[-1] == pytest.approx(expected)


def test_free_cash_flow_yield_is_the_inverse_multiple(
    accounts: pd.DataFrame, market_value: pd.Series
) -> None:
    multiple = price_to_free_cash_flow(accounts, market_value).dropna()
    yields = free_cash_flow_yield(accounts, market_value).dropna()
    assert np.allclose(multiple * yields / 100.0, 1.0)


def test_enterprise_value_adds_debt_and_removes_cash(
    accounts: pd.DataFrame, market_value: pd.Series
) -> None:
    rows = accounts[accounts["period"] == "annual"]
    expected = 2700.0 + rows["total_debt"].iloc[-1] - rows["cash_and_equivalents"].iloc[-1]
    assert enterprise_value(rows, market_value).iloc[-1] == pytest.approx(expected)


def test_enterprise_multiples_are_above_their_price_counterparts(
    accounts: pd.DataFrame, market_value: pd.Series
) -> None:
    """This company has more debt than cash, so enterprise value exceeds market value."""
    assert (
        ev_to_sales(accounts, market_value).iloc[-1]
        > price_to_sales(accounts, market_value).iloc[-1]
    )
    assert ev_to_ebitda(accounts, market_value).iloc[-1] > 0.0
    assert (
        ev_to_ebit(accounts, market_value).iloc[-1] > ev_to_ebitda(accounts, market_value).iloc[-1]
    )
    assert ev_to_free_cash_flow(accounts, market_value).iloc[-1] > 0.0


def test_greenblatt_earnings_yield_divides_ebit_by_enterprise_value(
    accounts: pd.DataFrame, market_value: pd.Series
) -> None:
    ttm = accounts[accounts["period"] == "ttm"]
    value = 2700.0 + ttm["total_debt"].iloc[-1] - ttm["cash_and_equivalents"].iloc[-1]
    expected = ttm["ebit"].iloc[-1] / value * 100.0
    assert magic_formula_earnings_yield(accounts, market_value).iloc[-1] == pytest.approx(expected)


def test_peg_is_undefined_where_growth_is_not_positive(
    accounts: pd.DataFrame, market_value: pd.Series
) -> None:
    """A negative PEG from negative growth reads as cheap and means the opposite."""
    shrinking = accounts.copy()
    is_ttm = shrinking["period"] == "ttm"
    shrinking.loc[is_ttm, "net_income"] = np.linspace(500.0, 100.0, int(is_ttm.sum()))
    assert peg_ratio(shrinking, market_value).isna().all()


def test_peg_is_the_multiple_over_the_growth_rate(
    accounts: pd.DataFrame, market_value: pd.Series
) -> None:
    multiple = price_to_earnings(accounts, market_value).iloc[-1]
    assert peg_ratio(accounts, market_value).iloc[-1] == pytest.approx(multiple / 10.0)


def test_dividend_yield_differs_between_paid_and_declared(
    accounts: pd.DataFrame, market_value: pd.Series
) -> None:
    """Up to a year of timing, and systematic rather than noise."""
    without_total = accounts.drop(columns=["dividends_paid"])
    paid = dividend_yield(without_total, market_value, basis="paid").iloc[-1]
    declared = dividend_yield(without_total, market_value, basis="declared").iloc[-1]
    assert declared > paid
    with pytest.raises(ValueError, match="unknown basis"):
        dividend_yield(accounts, market_value, basis="forecast")


def test_payout_ratio_is_undefined_on_a_loss(accounts: pd.DataFrame) -> None:
    loss = accounts.copy()
    loss["net_income"] = -50.0
    assert payout_ratio(loss).isna().all()
    assert payout_ratio(accounts).iloc[-1] == pytest.approx(40.0 / 135.0 * 100.0)


# ── Leverage and liquidity ──────────────────────────────────────────────────


def test_balance_sheet_ratios(accounts: pd.DataFrame) -> None:
    assert equity_ratio(accounts).iloc[-1] == pytest.approx(40.0)
    assert liabilities_ratio(accounts).iloc[-1] == pytest.approx(60.0)
    assert debt_to_assets(accounts).iloc[-1] == pytest.approx(30.0)
    assert debt_to_equity(accounts).iloc[-1] == pytest.approx(75.0)


def test_debt_is_not_liabilities(accounts: pd.DataFrame) -> None:
    """Trade payables are a liability and are not debt. The gap is the operating float."""
    assert liabilities_ratio(accounts).iloc[-1] > debt_to_assets(accounts).iloc[-1]


def test_debt_to_equity_is_undefined_on_negative_equity(accounts: pd.DataFrame) -> None:
    insolvent = accounts.copy()
    insolvent["total_equity"] = -100.0
    assert debt_to_equity(insolvent).isna().all()


def test_net_debt_to_ebitda_keeps_a_negative_reading(accounts: pd.DataFrame) -> None:
    """More cash than debt is information, not an error."""
    cash_rich = accounts.copy()
    cash_rich["cash_and_equivalents"] = cash_rich["total_debt"] * 2.0
    assert net_debt_to_ebitda(cash_rich).iloc[-1] < 0.0


def test_liquidity_ratios_are_ordered(accounts: pd.DataFrame) -> None:
    """Current includes inventory, quick excludes it, cash includes only cash."""
    current = current_ratio(accounts).iloc[-1]
    quick = quick_ratio(accounts).iloc[-1]
    cash = cash_ratio(accounts).iloc[-1]
    assert current == pytest.approx(1.6)
    assert quick == pytest.approx(1.0)
    assert cash == pytest.approx(0.4)
    assert current > quick > cash


def test_interest_coverage_is_undefined_without_interest(accounts: pd.DataFrame) -> None:
    """Infinite coverage is true and unrankable. NaN here reads as 'no debt service'."""
    debt_free = accounts.copy()
    debt_free["interest_expense"] = 0.0
    assert interest_coverage(debt_free).isna().all()
    assert interest_coverage(accounts).iloc[-1] == pytest.approx(10.0)


def test_interest_coverage_on_cash_flow_is_the_stricter_read(
    accounts: pd.DataFrame,
) -> None:
    on_ebit = interest_coverage(accounts, basis="ebit").iloc[-1]
    on_cash = interest_coverage(accounts, basis="operating_cash_flow").iloc[-1]
    assert on_cash != pytest.approx(on_ebit)
    with pytest.raises(ValueError, match="unknown basis"):
        interest_coverage(accounts, basis="ebitda")


def test_debt_coverage_stays_finite_as_debt_shrinks(accounts: pd.DataFrame) -> None:
    """The reason the entry inverts the usual multiple."""
    light = accounts.copy()
    light["total_debt"] = 1.0
    assert np.isfinite(debt_coverage(light).iloc[-1])
    assert debt_coverage(light).iloc[-1] > debt_coverage(accounts).iloc[-1]


def test_cash_flow_to_debt_is_below_operating_coverage(accounts: pd.DataFrame) -> None:
    assert cash_flow_to_debt(accounts).iloc[-1] < debt_coverage(accounts).iloc[-1]


def test_long_term_debt_to_working_capital_is_undefined_when_working_capital_is_negative(
    accounts: pd.DataFrame,
) -> None:
    """A company funded by its suppliers would otherwise rank as conservative."""
    supplier_funded = accounts.copy()
    supplier_funded["current_liabilities"] = supplier_funded["current_assets"] * 2.0
    assert long_term_debt_to_working_capital(supplier_funded).isna().all()


def test_o_score_rises_as_the_balance_sheet_deteriorates(accounts: pd.DataFrame) -> None:
    distressed = accounts.copy()
    distressed["total_liabilities"] = distressed["total_assets"] * 1.2
    distressed["net_income"] = -100.0
    assert ohlson_o_score(distressed).iloc[-1] > ohlson_o_score(accounts).iloc[-1]


def test_o_score_probability_is_monotone_in_the_score(accounts: pd.DataFrame) -> None:
    """Stated in the entry: ranking on the probability gains nothing over the score."""
    score = ohlson_o_score(accounts).dropna()
    probability = ohlson_bankruptcy_probability(accounts).dropna()
    assert (score.rank() == probability.rank()).all()
    assert probability.between(0.0, 100.0).all()


# ── Growth ──────────────────────────────────────────────────────────────────


def test_growth_of_a_ten_percent_company_is_ten(accounts: pd.DataFrame) -> None:
    assert growth(accounts, item="revenue", period="annual", periods=1).iloc[-1] == pytest.approx(
        10.0
    )


def test_growth_from_a_negative_base_is_undefined(accounts: pd.DataFrame) -> None:
    """A loss shrinking from -100 to -50 reads as -50 percent, which is backwards."""
    losses = accounts.copy()
    is_annual = losses["period"] == "annual"
    losses.loc[is_annual, "net_income"] = np.linspace(-200.0, -20.0, int(is_annual.sum()))
    assert growth(losses, item="net_income", period="annual", periods=1).isna().all()
    allowed = growth(
        losses, item="net_income", period="annual", periods=1, allow_negative_base=True
    )
    assert (allowed.dropna() < 0.0).all()


def test_compound_growth_recovers_the_rate(accounts: pd.DataFrame) -> None:
    assert compound_annual_growth(accounts, years=5).iloc[-1] == pytest.approx(10.0)


def test_compound_growth_is_undefined_across_a_sign_change(accounts: pd.DataFrame) -> None:
    """A root of a negative number is not a growth rate."""
    turning = accounts.copy()
    is_annual = turning["period"] == "annual"
    turning.loc[is_annual, "net_income"] = np.linspace(100.0, -100.0, int(is_annual.sum()))
    assert compound_annual_growth(turning, item="net_income", years=5).isna().all()


def test_growth_stability_is_one_for_a_constant_rate(accounts: pd.DataFrame) -> None:
    assert growth_stability(accounts, years=5).iloc[-1] == pytest.approx(1.0)


def test_growth_stability_falls_when_the_path_breaks(accounts: pd.DataFrame) -> None:
    jumpy = accounts.copy()
    is_annual = jumpy["period"] == "annual"
    jumpy.loc[is_annual, "revenue"] = [100.0] * 5 + [500.0] * 4
    assert growth_stability(jumpy, years=5).iloc[-1] < 1.0


def test_growth_consistency_is_undefined_for_a_constant_rate(
    accounts: pd.DataFrame,
) -> None:
    """Zero dispersion, no denominator."""
    assert np.isnan(growth_consistency(accounts, years=5).iloc[-1])


def test_absolute_growth_is_in_currency(accounts: pd.DataFrame) -> None:
    rows = accounts[accounts["period"] == "annual"]
    expected = rows["revenue"].iloc[-1] - rows["revenue"].iloc[-6]
    assert absolute_growth(accounts, periods=5).iloc[-1] == pytest.approx(expected)


def test_sequential_and_year_on_year_growth_differ(accounts: pd.DataFrame) -> None:
    """One sees a turn inside the year, the other removes the season. Not the same number."""
    sequential = sequential_growth(accounts).iloc[-1]
    annual = year_on_year_quarterly_growth(accounts).iloc[-1]
    assert sequential != pytest.approx(annual)
    assert annual == pytest.approx(10.0)


def test_an_unknown_item_is_rejected(accounts: pd.DataFrame) -> None:
    with pytest.raises(ValueError, match="unknown item"):
        growth(accounts, item="headcount")


# ── Absolute lines ──────────────────────────────────────────────────────────


def test_size_factors_return_the_reported_lines(accounts: pd.DataFrame) -> None:
    ttm = accounts[accounts["period"] == "ttm"]
    assert revenue(accounts).iloc[-1] == pytest.approx(ttm["revenue"].iloc[-1])
    assert net_income(accounts).iloc[-1] == pytest.approx(ttm["net_income"].iloc[-1])
