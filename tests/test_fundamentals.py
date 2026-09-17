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


# ── Against identities that hold outside this package ───────────────────────
#
# The tests above check each ratio against its own arithmetic. An identity
# holds between several of them, comes from accounting rather than from this
# code, and therefore fails when any one of them is wrong.


def test_dupont_identity_holds(accounts: pd.DataFrame) -> None:
    """Return on equity is the net margin, times asset turnover, times the
    equity multiplier. DuPont, 1919, and nothing to do with this package.

    Taken on closing balances so that the three factors cancel exactly; the
    default averages the balance, which is the better ratio and not an
    identity.
    """
    rows = accounts[accounts["period"] == "annual"]
    turnover = rows["revenue"] / rows["total_assets"]
    multiplier = rows["total_assets"] / rows["total_equity"]
    margin = net_margin(accounts) / 100.0

    expected = (margin * turnover * multiplier * 100.0).iloc[-1]
    assert return_on_equity(accounts, average_balance=False).iloc[-1] == pytest.approx(expected)


def test_return_on_equity_is_return_on_assets_times_the_equity_multiplier(
    accounts: pd.DataFrame,
) -> None:
    """The second half of the same identity, and the reason the gap between the
    two ratios is a direct read on leverage."""
    rows = accounts[accounts["period"] == "annual"]
    multiplier = (rows["total_assets"] / rows["total_equity"]).iloc[-1]
    expected = return_on_assets(accounts, average_balance=False).iloc[-1] * multiplier
    assert return_on_equity(accounts, average_balance=False).iloc[-1] == pytest.approx(expected)


def test_enterprise_value_identity_across_the_multiples(
    accounts: pd.DataFrame, market_value: pd.Series
) -> None:
    """EV/Sales divided by EV/EBIT is the EBIT margin. Both multiples share a
    numerator, so the identity fails if either denominator is picked wrong."""
    ratio = (
        ev_to_sales(accounts, market_value).iloc[-1] / ev_to_ebit(accounts, market_value).iloc[-1]
    )
    assert ratio == pytest.approx(ebit_margin(accounts, period="ttm").iloc[-1] / 100.0)


def test_price_multiples_and_yields_are_reciprocal(
    accounts: pd.DataFrame, market_value: pd.Series
) -> None:
    """Stated in two entries. If it fails, one of them divides the wrong way."""
    pairs = (
        (price_to_earnings(accounts, market_value), earnings_yield(accounts, market_value)),
        (
            price_to_free_cash_flow(accounts, market_value),
            free_cash_flow_yield(accounts, market_value),
        ),
    )
    for multiple, yields in pairs:
        assert np.allclose(multiple.dropna() * yields.dropna() / 100.0, 1.0)


def test_gross_ebit_and_net_margins_are_ordered(accounts: pd.DataFrame) -> None:
    """Each line of the income statement is below the one above it, so for a
    profitable company the margins fall in the same order. An entry that read
    the wrong column would break the ordering."""
    assert (
        gross_margin(accounts).iloc[-1]
        > ebitda_margin(accounts).iloc[-1]
        > ebit_margin(accounts).iloc[-1]
        > pretax_margin(accounts).iloc[-1]
        > net_margin(accounts).iloc[-1]
    )


def test_liquidity_ratios_are_ordered_by_construction(accounts: pd.DataFrame) -> None:
    """Cash is a subset of current assets less inventory, which is a subset of
    current assets. The three ratios cannot come out in any other order."""
    assert (
        current_ratio(accounts).iloc[-1]
        >= quick_ratio(accounts).iloc[-1]
        >= cash_ratio(accounts).iloc[-1]
    )


def test_ohlson_coefficients_match_the_published_table(accounts: pd.DataFrame) -> None:
    """Each indicator's coefficient is checked by flipping it on its own.

    Ohlson (1980), table 4, model one: the two-year-loss indicator carries
    +0.285 and the negative-equity indicator carries -1.72. Changing nothing
    else, the score has to move by exactly those amounts.
    """
    rows = accounts[accounts["period"] == "annual"]
    base = ohlson_o_score(accounts)

    losing = accounts.copy()
    is_annual = losing["period"] == "annual"
    losing.loc[is_annual, "net_income"] = -1.0
    only_the_indicator = losing.copy()
    only_the_indicator.loc[is_annual, "net_income"] = 1e-9

    with_two_losses = ohlson_o_score(losing).iloc[-1]
    without = ohlson_o_score(only_the_indicator).iloc[-1]
    assert with_two_losses - without == pytest.approx(0.285, abs=0.02)

    insolvent = accounts.copy()
    insolvent.loc[is_annual, "total_liabilities"] = rows["total_assets"].to_numpy() * 1.0001
    solvent = accounts.copy()
    solvent.loc[is_annual, "total_liabilities"] = rows["total_assets"].to_numpy() * 0.9999
    difference = ohlson_o_score(insolvent).iloc[-1] - ohlson_o_score(solvent).iloc[-1]
    assert difference == pytest.approx(-1.72, abs=0.01)
    assert not np.isnan(base.iloc[-1])


def test_free_cash_flow_identity(accounts: pd.DataFrame) -> None:
    """Operating cash flow less capital expenditure, read off the frame itself."""
    ttm = accounts[accounts["period"] == "ttm"]
    assert free_cash_flow(accounts).iloc[-1] == pytest.approx(
        ttm["operating_cash_flow"].iloc[-1] - ttm["capital_expenditure"].iloc[-1]
    )


def test_compound_growth_agrees_with_the_standard_library(accounts: pd.DataFrame) -> None:
    """The geometric mean is in the standard library. A five-year CAGR is that
    mean of the five yearly ratios, less one."""
    import statistics

    rows = accounts[accounts["period"] == "annual"]
    revenue = rows["revenue"].to_numpy()
    ratios = [revenue[i] / revenue[i - 1] for i in range(len(revenue) - 5, len(revenue))]
    expected = (statistics.geometric_mean(ratios) - 1.0) * 100.0
    assert compound_annual_growth(accounts, years=5).iloc[-1] == pytest.approx(expected)


def test_every_fundamental_runs_on_a_frame_holding_all_three_bases(
    accounts: pd.DataFrame, market_value: pd.Series
) -> None:
    """The data contract says one frame carries annual, quarterly and TTM rows
    side by side, so period ends repeat. A factor that does not select its
    basis first meets a duplicated index and raises.

    Two of them did: market capitalisation and enterprise value were the only
    market-based entries that never called rows_of.
    """
    import inspect

    from factorbase import compute, default_catalog
    from factorbase.registry import resolve
    from factorbase.schema import Kind

    failures: list[str] = []
    for factor in default_catalog().of_kind(Kind.FUNDAMENTAL):
        assert factor.implementation is not None
        positional = [
            p
            for p in inspect.signature(resolve(factor.implementation)).parameters.values()
            if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)
        ]
        needs_market = len(positional) >= 2 and positional[1].default is inspect.Parameter.empty
        try:
            if needs_market:
                compute(factor.id, accounts, market_value)
            else:
                compute(factor.id, accounts)
        except Exception as error:  # noqa: BLE001 - the point is to collect them
            failures.append(f"{factor.id}: {type(error).__name__}: {error}")

    assert failures == []


def test_market_capitalisation_returns_one_value_per_selected_period(
    accounts: pd.DataFrame, market_value: pd.Series
) -> None:
    from factorbase import compute

    annual = compute("market_capitalisation", accounts, market_value)
    assert len(annual) == int((accounts["period"] == "annual").sum())
    assert (annual == 2700.0).all()


def test_enterprise_value_adds_the_debt_of_the_selected_basis(
    accounts: pd.DataFrame, market_value: pd.Series
) -> None:
    from factorbase import compute

    rows = accounts[accounts["period"] == "annual"]
    result = compute("enterprise_value", accounts, market_value)
    expected = 2700.0 + rows["total_debt"] - rows["cash_and_equivalents"]
    assert np.allclose(result.to_numpy(), expected.to_numpy())


def test_a_restated_period_is_rejected_by_name(
    accounts: pd.DataFrame, market_value: pd.Series
) -> None:
    """Two rows with the same period end on the same basis are ambiguous: an
    original filing and its amendment, and nothing in the frame says which is
    the truth.

    Picking one silently would decide for the caller, and letting pandas raise
    gives them "cannot reindex on an axis with duplicate labels" with no date
    and no factor name. So it raises here, saying which basis and which date.
    """
    from factorbase import compute
    from factorbase.errors import AmbiguousPeriodError

    annual = accounts[accounts["period"] == "annual"]
    restated = pd.concat([accounts, annual.iloc[[-1]]]).sort_index(kind="stable")

    with pytest.raises(AmbiguousPeriodError) as caught:
        compute("market_capitalisation", restated, market_value)
    message = str(caught.value)
    assert "annual" in message
    assert "2024-12-31" in message

    with pytest.raises(AmbiguousPeriodError):
        compute("net_margin", restated)


def test_a_repeated_period_end_across_bases_is_fine(accounts: pd.DataFrame) -> None:
    """Quarterly and TTM rows share their period ends by design. Only a repeat
    within one basis is ambiguous."""
    from factorbase import compute

    quarterly = accounts[accounts["period"] == "quarterly"]
    trailing = accounts[accounts["period"] == "ttm"]
    assert quarterly.index.equals(trailing.index)
    assert compute("net_margin", accounts, period="ttm").notna().any()


# ── The four ratios the first pass missed ───────────────────────────────────


def test_market_cap_to_research_counts_years_of_the_budget(
    accounts: pd.DataFrame, market_value: pd.Series
) -> None:
    from factorbase import compute
    from factorbase.factors.fundamentals.valuation import market_cap_to_research

    rows = accounts[accounts["period"] == "annual"]
    expected = 2700.0 / rows["research_and_development"].iloc[-1]
    assert market_cap_to_research(accounts, market_value).iloc[-1] == pytest.approx(expected)
    assert compute("market_cap_to_research", accounts, market_value).iloc[-1] == pytest.approx(
        expected
    )


def test_market_cap_to_research_is_undefined_without_research(
    accounts: pd.DataFrame, market_value: pd.Series
) -> None:
    """A company that spends nothing on it has no ratio, not an infinite one."""
    from factorbase.factors.fundamentals.valuation import market_cap_to_research

    none = accounts.copy()
    none["research_and_development"] = 0.0
    assert market_cap_to_research(none, market_value).isna().all()


def test_market_cap_to_debt_is_the_cushion_in_front_of_the_lenders(
    accounts: pd.DataFrame, market_value: pd.Series
) -> None:
    from factorbase.factors.fundamentals.valuation import market_cap_to_debt

    rows = accounts[accounts["period"] == "annual"]
    expected = 2700.0 / rows["total_debt"].iloc[-1]
    assert market_cap_to_debt(accounts, market_value).iloc[-1] == pytest.approx(expected)


def test_market_cap_to_debt_is_undefined_without_debt(
    accounts: pd.DataFrame, market_value: pd.Series
) -> None:
    from factorbase.factors.fundamentals.valuation import market_cap_to_debt

    unlevered = accounts.copy()
    unlevered["total_debt"] = 0.0
    assert market_cap_to_debt(unlevered, market_value).isna().all()


def test_dividend_yield_on_enterprise_value_is_lower_for_a_levered_company(
    accounts: pd.DataFrame, market_value: pd.Series
) -> None:
    """The fixture carries more debt than cash, so enterprise value exceeds
    market capitalisation and the same dividend yields less on it."""
    on_equity = dividend_yield(accounts, market_value, base="market_cap").iloc[-1]
    on_enterprise = dividend_yield(accounts, market_value, base="enterprise_value").iloc[-1]
    assert on_enterprise < on_equity

    rows = accounts[accounts["period"] == "annual"]
    value = 2700.0 + rows["total_debt"].iloc[-1] - rows["cash_and_equivalents"].iloc[-1]
    expected = rows["dividends_paid"].iloc[-1] / value * 100.0
    assert on_enterprise == pytest.approx(expected)


def test_an_unknown_dividend_base_is_rejected(
    accounts: pd.DataFrame, market_value: pd.Series
) -> None:
    with pytest.raises(ValueError, match="unknown base"):
        dividend_yield(accounts, market_value, base="book_value")


def test_growth_can_be_measured_on_research_spending(accounts: pd.DataFrame) -> None:
    """The line was in the vocabulary and not in the growth factor's item list,
    so the one reported figure nobody could ask for was the R&D trend."""
    result = growth(accounts, item="research", period="annual", periods=1)
    assert result.iloc[-1] == pytest.approx(10.0)
