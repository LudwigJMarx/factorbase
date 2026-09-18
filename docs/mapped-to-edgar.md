# Mapped to EDGAR

Which XBRL concept holds which field of this catalogue's data contract, and
which one a filer actually uses. **This file is generated** from
`catalog/mappings/edgar.yaml` and `tests/data/edgar_coverage.json`.

This package fetches nothing. It has no HTTP dependency and will not grow one:
a downloader means rate limiting, caching and a contact address under the SEC's
fair-access policy, and anyone with a data pipeline already has those. What
they do not have is the answer to which tag holds gross profit.

Measured on 2026-09-18 against 7 filers, chosen for
different shapes rather than for size:

| Ticker | CIK | Shape |
|---|---|---|
| AAPL | `0000320193` | classified balance sheet, one class, no NCI |
| JPM | `0000019617` | bank, unclassified balance sheet |
| WMT | `0000104169` | retailer, NCI, no total liabilities tagged |
| BRKB | `0001067983` | conglomerate, unclassified, two share classes |
| F | `0000037996` | manufacturer with a captive finance arm |
| TGT | `0000027419` | retailer |
| KO | `0000021344` | consumer goods, long tagging history |

## The trap this is mostly about

A concept that exists is not a concept in use. `Revenues` sits in Apple's
company facts and has not appeared on a 10-K since FY2018. Code that takes the
first tag it finds reads a seven-year-old figure and returns it as current.

So each row below carries the last fiscal year each filer reported that concept
on an annual filing. Pick by that, not by presence. A dash means the filer has
never used the tag.

## Fields

### `revenue`

Unit: `USD`. Try in this order:

| Concept | AAPL | JPM | WMT | BRKB | F | TGT | KO |
|---|---|---|---|---|---|---|---|
| `RevenueFromContractWithCustomerExcludingAssessedTax` | 2025 | - | 2026 | 2025 | 2025 | 2025 | - |
| `Revenues` | 2018 | 2025 | 2026 | 2025 | 2024 | 2014 | 2025 |
| `SalesRevenueNet` | 2017 | - | 2018 | 2017 | 2015 | 2017 | - |

The order matters and is the clearest case in the file. ASC 606 moved most filers to the first tag from 2018. `Revenues` stayed current for banks and for anything that never adopted the contract-revenue presentation, so it cannot simply be dropped. `SalesRevenueNet` is the pre-2018 tag and is dead everywhere measured: AAPL FY2017, WMT FY2018.



### `cost_of_revenue`

Unit: `USD`. Try in this order:

| Concept | AAPL | JPM | WMT | BRKB | F | TGT | KO |
|---|---|---|---|---|---|---|---|
| `CostOfGoodsAndServicesSold` | 2025 | - | - | - | 2025 | 2025 | 2025 |
| `CostOfRevenue` | - | - | 2026 | - | - | - | - |
| `CostOfGoodsSold` *(historical)* | - | - | - | - | - | - | 2017 |

`CostOfGoodsAndServicesSold` is current for four of the seven filers measured (AAPL, F, TGT, KO). WMT uses `CostOfRevenue` and tags nothing else. `CostOfGoodsSold` is the old name and is dead: the only filer measured that ever used it is KO, last in FY2017. A consumer that knows one of the two current tags covers part of the market and silently misses the rest. Banks report no cost of revenue at all.



### `gross_profit`

Unit: `USD`. Try in this order:

| Concept | AAPL | JPM | WMT | BRKB | F | TGT | KO |
|---|---|---|---|---|---|---|---|
| `GrossProfit` | 2025 | - | - | - | - | 2017 | 2025 |

If absent: `revenue - cost_of_revenue`

Current for AAPL and KO, stale for TGT since FY2017, and never tagged by WMT, JPM, BRK or F. WMT gives revenue and cost of revenue and leaves the subtraction to the reader. Deriving it is exact where both inputs come from the same statement, which is why the fallback is stated rather than left to guesswork.



### `research_and_development`

Unit: `USD`. Try in this order:

| Concept | AAPL | JPM | WMT | BRKB | F | TGT | KO |
|---|---|---|---|---|---|---|---|
| `ResearchAndDevelopmentExpense` | 2025 | - | - | - | 2025 | - | - |

Present only where the filer has the line. Absent is absent, not zero: a retailer and a bank do not report it, and treating that as zero R&D spending makes any intensity ratio meaningless.



### `ebit`

Unit: `USD`. Try in this order:

| Concept | AAPL | JPM | WMT | BRKB | F | TGT | KO |
|---|---|---|---|---|---|---|---|
| `OperatingIncomeLoss` | 2025 | - | 2026 | 2012 | 2025 | 2025 | 2025 |

This is an approximation and the entry says so. Operating income is not EBIT wherever non-operating income sits between them, which is most large filers. Worse, it is unavailable for the shapes that need care: absent for JPM entirely, last reported by BRK in FY2012. Every factor built on it inherits both problems.



### `depreciation_amortisation`

Unit: `USD`. Try in this order:

| Concept | AAPL | JPM | WMT | BRKB | F | TGT | KO |
|---|---|---|---|---|---|---|---|
| `DepreciationDepletionAndAmortization` | 2025 | - | 2019 | 2025 | 2025 | 2025 | 2025 |
| `DepreciationAmortizationAndAccretionNet` | 2017 | 2025 | 2026 | - | - | - | - |
| `DepreciationAndAmortization` | 2016 | - | 2019 | - | - | 2025 | - |

Three tags, and the current one differs by filer: AAPL and BRK on the first, JPM and WMT on the second. WMT used the first until FY2019 and then switched, which is the same trap as `Revenues` inside one company.



### `interest_expense`

Unit: `USD`. Try in this order:

| Concept | AAPL | JPM | WMT | BRKB | F | TGT | KO |
|---|---|---|---|---|---|---|---|
| `InterestExpenseNonoperating` | - | - | - | - | 2025 | 2025 | 2025 |
| `InterestExpenseDebt` | 2021 | - | 2026 | - | 2020 | - | - |
| `InterestExpense` | 2023 | 2023 | - | 2025 | 2023 | 2023 | 2025 |

The messiest field here, and the one where no tag is current everywhere. Measured across seven filers: `InterestExpenseNonoperating` is current for F, TGT and KO and absent for the other four. `InterestExpenseDebt` is current for WMT and stale for AAPL (FY2021) and F (FY2020). `InterestExpense`, the obvious first guess, is stale for AAPL, JPM, F and TGT (all FY2023) and current only for BRK and KO. Any single choice is wrong for most of this sample, which is why the order above puts the obvious guess last rather than first. For a bank the concept also means something different in kind: interest expense is a cost of goods, not a financing charge, so interest-coverage ratios built on it do not carry over.



### `pretax_income`

Unit: `USD`. Try in this order:

| Concept | AAPL | JPM | WMT | BRKB | F | TGT | KO |
|---|---|---|---|---|---|---|---|
| `IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest` | 2025 | 2025 | 2026 | 2025 | 2025 | 2025 | 2025 |
| `IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments` | 2012 | 2020 | 2021 | 2025 | 2016 | 2020 | - |

The first is current for all four filers. The second differs by including equity-method income and is the older presentation; it survives at BRK, where equity-method holdings are the business.



### `tax_expense`

Unit: `USD`. Try in this order:

| Concept | AAPL | JPM | WMT | BRKB | F | TGT | KO |
|---|---|---|---|---|---|---|---|
| `IncomeTaxExpenseBenefit` | 2025 | 2025 | 2026 | 2025 | 2025 | 2025 | 2025 |

One tag, current for all four. One of the few fields with no choice to make.



### `net_income`

Unit: `USD`. Try in this order:

| Concept | AAPL | JPM | WMT | BRKB | F | TGT | KO |
|---|---|---|---|---|---|---|---|
| `NetIncomeLoss` | 2025 | 2025 | 2026 | 2025 | 2024 | 2025 | 2025 |
| `ProfitLoss` | - | 2013 | 2026 | 2025 | 2025 | 2011 | 2025 |

Not interchangeable. `NetIncomeLoss` is attributable to the parent; `ProfitLoss` includes noncontrolling interests. AAPL has no NCI and therefore no `ProfitLoss` at all. The order above is not a ranking by recency, and Ford is why: its `NetIncomeLoss` stops at FY2024 while `ProfitLoss` is current to FY2025. Preferring the first tag there returns a year-old figure. Preferring the newer one returns a different measure. There is no rule that gets both right, which is the point: pick the definition you want and accept what it costs, rather than letting whichever tag is present decide. The difference lands directly in EPS, ROE and every margin.



### `eps_diluted`

Unit: `USD/shares`. Try in this order:

| Concept | AAPL | JPM | WMT | BRKB | F | TGT | KO |
|---|---|---|---|---|---|---|---|
| `EarningsPerShareDiluted` | 2025 | 2025 | 2026 | - | 2025 | 2025 | 2025 |
| `IncomeLossFromContinuingOperationsPerDilutedShare` | - | - | 2019 | - | 2020 | 2021 | 2018 |

Absent for BRK, which reports per Class A and per Class B separately and has no single diluted figure. A multi-class filer needs a decision this table cannot make for it.



### `operating_cash_flow`

Unit: `USD`. Try in this order:

| Concept | AAPL | JPM | WMT | BRKB | F | TGT | KO |
|---|---|---|---|---|---|---|---|
| `NetCashProvidedByUsedInOperatingActivities` | 2025 | 2025 | 2026 | 2025 | 2025 | 2025 | 2025 |
| `NetCashProvidedByUsedInOperatingActivitiesContinuingOperations` | 2016 | - | - | 2016 | 2018 | 2021 | no 10-K |

Current for all four on the first tag. The second appears where discontinued operations were separated and is stale everywhere measured.



### `capital_expenditure`

Unit: `USD`. Try in this order:

| Concept | AAPL | JPM | WMT | BRKB | F | TGT | KO |
|---|---|---|---|---|---|---|---|
| `PaymentsToAcquirePropertyPlantAndEquipment` | 2025 | - | 2026 | 2025 | - | 2025 | 2025 |
| `PaymentsToAcquireProductiveAssets` | 2014 | - | - | - | 2025 | - | - |

Absent for JPM. A bank's capital spending is not a separate investing line in the same sense, so free cash flow as this catalogue defines it does not exist for it. `PaymentsToAcquireProductiveAssets` is not the historical spelling it looks like: it is stale for AAPL (FY2014) and the only tag Ford uses, to FY2025. Both belong in the chain. The sign is positive in the filing: it is a payment. Whoever maps it has to negate or subtract, and getting that wrong flips free cash flow rather than merely shifting it.



### `dividends_paid`

Unit: `USD`. Try in this order:

| Concept | AAPL | JPM | WMT | BRKB | F | TGT | KO |
|---|---|---|---|---|---|---|---|
| `PaymentsOfDividendsCommonStock` | 2017 | - | 2026 | - | 2025 | 2025 | - |
| `PaymentsOfDividends` | 2025 | 2025 | 2020 | - | - | - | 2025 |

The two are current for different filers, WMT on the first and AAPL and JPM on the second, and they are not the same thing: the second includes preferred dividends. BRK pays none and tags neither. Positive in the filing, as with capital expenditure.



### `dividend_per_share_paid`

Unit: `USD/shares`. Try in this order:

| Concept | AAPL | JPM | WMT | BRKB | F | TGT | KO |
|---|---|---|---|---|---|---|---|
| `CommonStockDividendsPerShareCashPaid` | no 10-K | 2017 | 2012 | - | 2013 | - | 2025 |

Effectively dead. The latest annual use measured is JPM FY2017 and WMT FY2012; AAPL carries the tag but has never reported it on a 10-K. Prefer the declared figure below and say which one you used.



### `dividend_per_share_declared`

Unit: `USD/shares`. Try in this order:

| Concept | AAPL | JPM | WMT | BRKB | F | TGT | KO |
|---|---|---|---|---|---|---|---|
| `CommonStockDividendsPerShareDeclared` | 2025 | 2025 | 2026 | - | 2025 | 2025 | no 10-K |

Current for the three filers that pay a dividend. Declared and paid differ by timing, and a yield computed from one and compared against the other is wrong by a quarter.



### `total_assets`

Unit: `USD`. Try in this order:

| Concept | AAPL | JPM | WMT | BRKB | F | TGT | KO |
|---|---|---|---|---|---|---|---|
| `Assets` | 2025 | 2025 | 2026 | 2025 | 2025 | 2025 | 2025 |

One tag, current for all four.



### `current_assets`

Unit: `USD`. Try in this order:

| Concept | AAPL | JPM | WMT | BRKB | F | TGT | KO |
|---|---|---|---|---|---|---|---|
| `AssetsCurrent` | 2025 | - | 2026 | - | 2025 | 2025 | 2025 |

AAPL and WMT only. JPM and BRK present unclassified balance sheets, where the concept does not exist because the split has no meaning for them.



### `inventory`

Unit: `USD`. Try in this order:

| Concept | AAPL | JPM | WMT | BRKB | F | TGT | KO |
|---|---|---|---|---|---|---|---|
| `InventoryNet` | 2025 | - | 2026 | 2025 | 2025 | 2025 | 2025 |

Absent for JPM, as it is for any filer without physical stock.



### `cash_and_equivalents`

Unit: `USD`. Try in this order:

| Concept | AAPL | JPM | WMT | BRKB | F | TGT | KO |
|---|---|---|---|---|---|---|---|
| `CashAndCashEquivalentsAtCarryingValue` | 2025 | 2018 | 2026 | 2017 | 2025 | no 10-K | 2025 |
| `CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents` | 2025 | 2025 | 2026 | 2025 | 2025 | 2025 | 2025 |

The second includes restricted cash and is therefore the larger number. It is the current tag for JPM and BRK, whose first-tag use ended in FY2018 and FY2017. Mixing the two across a universe compares cash a company can spend against cash it cannot.



### `total_liabilities`

Unit: `USD`. Try in this order:

| Concept | AAPL | JPM | WMT | BRKB | F | TGT | KO |
|---|---|---|---|---|---|---|---|
| `Liabilities` | 2025 | 2025 | - | 2025 | 2025 | - | - |

If absent: `total_assets - total_equity`

Missing more often than it is present among consumer filers: WMT, TGT and KO never tag the subtotal, while AAPL, JPM, BRK and F do. The derivation is therefore the normal path, not the fallback. It is exact by the accounting identity, provided total_equity includes noncontrolling interests. With common equity instead it is wrong by the NCI.



### `current_liabilities`

Unit: `USD`. Try in this order:

| Concept | AAPL | JPM | WMT | BRKB | F | TGT | KO |
|---|---|---|---|---|---|---|---|
| `LiabilitiesCurrent` | 2025 | - | 2026 | - | 2025 | 2025 | 2025 |

AAPL and WMT only, for the same reason as current_assets.



### `long_term_debt`

Unit: `USD`. Try in this order:

| Concept | AAPL | JPM | WMT | BRKB | F | TGT | KO |
|---|---|---|---|---|---|---|---|
| `LongTermDebtNoncurrent` | 2025 | - | 2026 | - | 2020 | 2012 | 2023 |
| `LongTermDebt` | 2025 | 2013 | 2026 | - | - | 2025 | 2023 |

`LongTermDebt` is the total including the current portion; `LongTermDebtNoncurrent` excludes it. They differ by the amount due within a year, which is exactly the amount a leverage ratio is sensitive to. Absent for BRK, and JPM last used one in FY2013.



### `total_equity`

Unit: `USD`. Try in this order:

| Concept | AAPL | JPM | WMT | BRKB | F | TGT | KO |
|---|---|---|---|---|---|---|---|
| `StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest` | - | 2015 | 2026 | 2025 | 2025 | 2010 | 2025 |
| `StockholdersEquity` | 2025 | 2025 | 2026 | 2025 | 2025 | 2025 | 2025 |

The first is the one this field means. AAPL has no NCI and tags only the second, where the two coincide. For WMT and BRK they differ, and using the second as total equity understates the balance sheet by the minority interest.



### `common_equity`

Unit: `USD`. Try in this order:

| Concept | AAPL | JPM | WMT | BRKB | F | TGT | KO |
|---|---|---|---|---|---|---|---|
| `StockholdersEquity` | 2025 | 2025 | 2026 | 2025 | 2025 | 2025 | 2025 |

Deliberately the parent-only figure, which is what book value per common share is built on. It is the same tag as the fallback above, used with a different intent, and that is why the catalogue carries both fields.



### `shares_outstanding`

Unit: `shares`. Try in this order:

| Concept | AAPL | JPM | WMT | BRKB | F | TGT | KO |
|---|---|---|---|---|---|---|---|
| `EntityCommonStockSharesOutstanding` | 2025 | 2025 | 2026 | 2010 | 2010 | 2025 | 2025 |
| `CommonStockSharesOutstanding` | 2025 | 2025 | 2011 | - | - | 2025 | - |
| `WeightedAverageNumberOfDilutedSharesOutstanding` | 2025 | 2025 | 2026 | - | 2025 | 2025 | 2025 |

EntityCommonStockSharesOutstanding is in the dei taxonomy, not us-gaap.

Three tags meaning three things: the count on the cover page at filing date, the count at the balance sheet date, and the weighted average used for EPS. WMT's `CommonStockSharesOutstanding` stops at FY2011 while the cover-page figure is current. BRK's cover-page figure stops at FY2010 because it reports per class. Per-share factors are sensitive to which one is chosen, and a market capitalisation built on the weighted average is wrong by every buyback in the year.



## Not in EDGAR at all

No filer tags these, because they are not GAAP line items. The catalogue
computes them, and the form it uses is stated so a reader can tell whether
their own number should match.

| Field | Computed as |
|---|---|
| `ebitda` | `ebit + depreciation_amortisation` |
| `free_cash_flow` | `operating_cash_flow - capital_expenditure` |
| `total_debt` | `long_term_debt + short-term borrowings` |
| `invested_capital` | `total_debt + total_equity - cash_and_equivalents` |

**`ebitda`.** No EDGAR concept. It is not GAAP, so no filer tags it, and every vendor figure called EBITDA is somebody's reconstruction. This one inherits the operating-income approximation above.

**`free_cash_flow`.** No concept. Note the sign: capital expenditure is a positive payment in the filing, so it is subtracted, not added. Undefined for a filer with no capital expenditure line, JPM among those measured.

**`total_debt`.** No single concept, and the second half has no stable tag across filers: DebtCurrent, ShortTermBorrowings, CommercialPaper and LongTermDebtCurrent all appear. This is the least reliable field here and is left explicitly incomplete rather than given a tag that would be wrong for most of the market.

**`invested_capital`.** No concept, and definitions differ between practitioners over whether cash is netted and which liabilities count as debt. The form above is the one the catalogue's ROIC entry uses, stated so a reader can tell whether their number should match.

## What an unclassified balance sheet costs

Banks and some conglomerates do not split current from non-current. The
inputs below are not missing for them, they are undefined, and so is every
factor that needs one.

Two different things happen, and lumping them together would overstate the
damage. An entry that needs all of its inputs is undefined for that filer. An
entry of the `growth` family is a transformation over one chosen series and
lists all eleven it accepts, so it loses that series and keeps working on the
others. The split below rests on that reading of the growth family, which is
stated here rather than buried in the generator.

**unclassified balance sheet: no AssetsCurrent or LiabilitiesCurrent**

Filers: JPM, BRKB. Inputs: `current_assets`, `current_liabilities`.

Undefined for those filers, 7 entries: `cash_ratio`, `current_ratio`, `long_term_debt_to_working_capital`, `magic_formula_return_on_capital`, `ohlson_bankruptcy_probability`, `ohlson_o_score`, `quick_ratio`.

**no operating income reported**

Filers: JPM. Inputs: `ebit`.

Undefined for those filers, 7 entries: `debt_coverage`, `ebit_margin`, `ev_to_ebit`, `interest_coverage`, `magic_formula_earnings_yield`, `magic_formula_return_on_capital`, `return_on_invested_capital`.

Still usable on the remaining series, 7 entries of the growth family: `absolute_growth`, `compound_annual_growth`, `growth`, `growth_consistency`, `growth_stability`, `sequential_growth`, `year_on_year_quarterly_growth`.

**no capital expenditure line**

Filers: JPM. Inputs: `capital_expenditure`.

Undefined for those filers, 5 entries: `cash_flow_to_debt`, `ev_to_free_cash_flow`, `free_cash_flow`, `free_cash_flow_yield`, `price_to_free_cash_flow`.

Still usable on the remaining series, 7 entries of the growth family: `absolute_growth`, `compound_annual_growth`, `growth`, `growth_consistency`, `growth_stability`, `sequential_growth`, `year_on_year_quarterly_growth`.

**multiple share classes, no single diluted EPS**

Filers: BRKB. Inputs: `eps_diluted`.

No entry becomes undefined.

Still usable on the remaining series, 7 entries of the growth family: `absolute_growth`, `compound_annual_growth`, `growth`, `growth_consistency`, `growth_stability`, `sequential_growth`, `year_on_year_quarterly_growth`.
