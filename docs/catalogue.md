# The catalogue

Every entry, with the formula it is defined by, the data it consumes and the
implementation it is tested against.

**This file is generated.** `catalog/*.yaml` is the source of truth and this is
built from it by `scripts/check_docs_current.py`, which also fails the build when
the two drift apart. Editing it here changes nothing.

192 entries.

## Index

**Indicators** (74)

- *momentum*: [`rsi`](#rsi---relative-strength-index), [`rate_of_change`](#rate_of_change---rate-of-change), [`absolute_price_change`](#absolute_price_change---absolute-price-change), [`macd`](#macd---macd-line), [`macd_signal`](#macd_signal---macd-signal-line), [`macd_histogram`](#macd_histogram---macd-histogram), [`macd_histogram_change`](#macd_histogram_change---macd-histogram-change), [`macd_momentum`](#macd_momentum---macd-momentum), [`cci`](#cci---commodity-channel-index), [`williams_percent_r`](#williams_percent_r---williams-r), [`stochastic_fast_k`](#stochastic_fast_k---fast-stochastic-k), [`stochastic_fast_d`](#stochastic_fast_d---fast-stochastic-d), [`stochastic_slow_k`](#stochastic_slow_k---slow-stochastic-k), [`stochastic_slow_d`](#stochastic_slow_d---slow-stochastic-d), [`double_smoothed_stochastic_blau`](#double_smoothed_stochastic_blau---double-smoothed-stochastic-blau), [`double_smoothed_stochastic_bressert`](#double_smoothed_stochastic_bressert---double-smoothed-stochastic-bressert)
- *moving average*: [`sma`](#sma---simple-moving-average), [`ema`](#ema---exponential-moving-average), [`wma`](#wma---weighted-moving-average), [`price_to_ma_distance`](#price_to_ma_distance---distance-from-moving-average), [`ma_to_ma_distance`](#ma_to_ma_distance---distance-between-two-moving-averages), [`ma_slope`](#ma_slope---moving-average-slope), [`ma_slope_normalized`](#ma_slope_normalized---normalised-moving-average-slope)
- *performance*: [`price`](#price---price), [`performance`](#performance---performance), [`daily_performance`](#daily_performance---daily-performance), [`annualised_performance`](#annualised_performance---annualised-performance), [`winning_days`](#winning_days---winning-days), [`distance_to_high`](#distance_to_high---distance-to-the-high), [`distance_to_low`](#distance_to_low---distance-to-the-low), [`inside_bars`](#inside_bars---inside-bars), [`bars_of_history`](#bars_of_history---bars-of-history)
- *relative*: [`relative_strength_levy`](#relative_strength_levy---relative-strength-levy), [`relative_strength_line`](#relative_strength_line---relative-strength-line), [`outperformance`](#outperformance---outperformance), [`beta`](#beta---beta), [`shrunk_beta`](#shrunk_beta---shrunk-beta), [`return_correlation`](#return_correlation---return-correlation), [`downside_correlation`](#downside_correlation---downside-correlation), [`downside_outperformance`](#downside_outperformance---downside-outperformance), [`jensen_alpha`](#jensen_alpha---jensens-alpha)
- *seasonality*: [`seasonal_strength`](#seasonal_strength---seasonal-strength), [`seasonal_hit_rate`](#seasonal_hit_rate---seasonal-hit-rate)
- *trend*: [`plus_di`](#plus_di---positive-directional-indicator), [`minus_di`](#minus_di---negative-directional-indicator), [`adx`](#adx---average-directional-index), [`aroon_up`](#aroon_up---aroon-up), [`aroon_down`](#aroon_down---aroon-down), [`aroon_oscillator`](#aroon_oscillator---aroon-oscillator), [`regression_slope_annualised`](#regression_slope_annualised---annualised-regression-slope), [`trend_stability`](#trend_stability---trend-stability), [`adjusted_slope`](#adjusted_slope---adjusted-slope), [`trend_template_score`](#trend_template_score---trend-template-score), [`random_trade_win_rate`](#random_trade_win_rate---random-trade-win-rate)
- *volatility*: [`true_range`](#true_range---true-range), [`atr`](#atr---average-true-range), [`atr_percent`](#atr_percent---average-true-range-relative), [`historical_volatility`](#historical_volatility---historical-volatility-daily), [`historical_volatility_weekly`](#historical_volatility_weekly---historical-volatility-weekly), [`average_drawdown`](#average_drawdown---average-drawdown), [`max_drawdown`](#max_drawdown---maximum-drawdown), [`trading_range`](#trading_range---trading-range), [`bollinger_percent_b`](#bollinger_percent_b---percent-b), [`bollinger_band_width`](#bollinger_band_width---bollinger-band-width), [`distance_to_upper_band`](#distance_to_upper_band---distance-to-upper-bollinger-band), [`distance_to_lower_band`](#distance_to_lower_band---distance-to-lower-bollinger-band)
- *volume*: [`close_location_value`](#close_location_value---close-location-value), [`accumulation_distribution_line`](#accumulation_distribution_line---accumulationdistribution-line), [`chaikin_oscillator`](#chaikin_oscillator---chaikin-oscillator), [`money_flow_index`](#money_flow_index---money-flow-index), [`average_turnover`](#average_turnover---average-turnover), [`relative_volume`](#relative_volume---relative-volume), [`volume_trend`](#volume_trend---volume-trend), [`average_volume`](#average_volume---average-volume)

**Signals** (57)

- *breakout*: [`new_high`](#new_high---new-high), [`new_low`](#new_low---new-low), [`gap_up`](#gap_up---gap-up), [`gap_down`](#gap_down---gap-down), [`expansion_breakout`](#expansion_breakout---range-expansion-breakout), [`expansion_breakdown`](#expansion_breakdown---range-expansion-breakdown), [`darvas_breakout`](#darvas_breakout---darvas-box-breakout), [`pivot_breakout`](#pivot_breakout---pivot-breakout), [`gilligans_island_buy`](#gilligans_island_buy---gilligans-island-buy-setup), [`gilligans_island_sell`](#gilligans_island_sell---gilligans-island-sell-setup)
- *candlestick*: [`cs_doji`](#cs_doji---doji), [`cs_dragonfly_doji`](#cs_dragonfly_doji---dragonfly-doji), [`cs_gravestone_doji`](#cs_gravestone_doji---gravestone-doji), [`cs_spinning_top`](#cs_spinning_top---spinning-top), [`cs_big_white_candle`](#cs_big_white_candle---big-white-candle), [`cs_big_black_candle`](#cs_big_black_candle---big-black-candle), [`cs_white_marubozu`](#cs_white_marubozu---white-marubozu), [`cs_black_marubozu`](#cs_black_marubozu---black-marubozu), [`cs_hammer`](#cs_hammer---hammer), [`cs_shooting_star`](#cs_shooting_star---shooting-star), [`cs_bullish_belt_hold`](#cs_bullish_belt_hold---bullish-belt-hold), [`cs_bearish_belt_hold`](#cs_bearish_belt_hold---bearish-belt-hold), [`cs_bullish_engulfing`](#cs_bullish_engulfing---bullish-engulfing), [`cs_bearish_engulfing`](#cs_bearish_engulfing---bearish-engulfing), [`cs_bullish_harami`](#cs_bullish_harami---bullish-harami), [`cs_bearish_harami`](#cs_bearish_harami---bearish-harami), [`cs_above_the_stomach`](#cs_above_the_stomach---above-the-stomach), [`cs_below_the_stomach`](#cs_below_the_stomach---below-the-stomach), [`cs_morning_star`](#cs_morning_star---morning-star), [`cs_evening_star`](#cs_evening_star---evening-star), [`cs_three_white_soldiers`](#cs_three_white_soldiers---three-white-soldiers), [`cs_three_black_crows`](#cs_three_black_crows---three-black-crows), [`cs_bullish_popgun`](#cs_bullish_popgun---bullish-popgun), [`cs_bearish_popgun`](#cs_bearish_popgun---bearish-popgun)
- *crossing*: [`price_crosses_above_ma`](#price_crosses_above_ma---price-crosses-above-moving-average), [`price_crosses_below_ma`](#price_crosses_below_ma---price-crosses-below-moving-average), [`golden_cross`](#golden_cross---golden-cross), [`death_cross`](#death_cross---death-cross), [`ma_support`](#ma_support---moving-average-held-as-support), [`ma_resistance`](#ma_resistance---moving-average-held-as-resistance), [`bollinger_support`](#bollinger_support---lower-bollinger-band-held), [`bollinger_resistance`](#bollinger_resistance---upper-bollinger-band-held), [`macd_cross_up`](#macd_cross_up---macd-crosses-above-signal), [`macd_cross_down`](#macd_cross_down---macd-crosses-below-signal), [`stochastic_cross_up`](#stochastic_cross_up---stochastic-crosses-up-from-low), [`stochastic_cross_down`](#stochastic_cross_down---stochastic-crosses-down-from-high), [`bollinger_band_outlier_long`](#bollinger_band_outlier_long---bollinger-band-outlier-long), [`bollinger_band_outlier_short`](#bollinger_band_outlier_short---bollinger-band-outlier-short), [`holy_grail_pullback`](#holy_grail_pullback---holy-grail-pullback)
- *structure*: [`pivot_high`](#pivot_high---pivot-high), [`pivot_low`](#pivot_low---pivot-low)
- *volume event*: [`accumulation_day`](#accumulation_day---accumulation-day), [`distribution_day`](#distribution_day---distribution-day), [`volume_peak`](#volume_peak---volume-peak), [`buying_climax`](#buying_climax---buying-climax), [`selling_climax`](#selling_climax---selling-climax), [`capitulation_bar`](#capitulation_bar---capitulation-bar)

**Fundamentals** (55)

- *distress*: [`ohlson_o_score`](#ohlson_o_score---ohlson-o-score), [`ohlson_bankruptcy_probability`](#ohlson_bankruptcy_probability---ohlson-bankruptcy-probability)
- *growth*: [`growth`](#growth---growth), [`compound_annual_growth`](#compound_annual_growth---compound-annual-growth), [`growth_stability`](#growth_stability---growth-stability), [`growth_consistency`](#growth_consistency---growth-consistency), [`absolute_growth`](#absolute_growth---absolute-growth), [`sequential_growth`](#sequential_growth---sequential-growth), [`year_on_year_quarterly_growth`](#year_on_year_quarterly_growth---year-on-year-quarterly-growth)
- *leverage*: [`equity_ratio`](#equity_ratio---equity-ratio), [`liabilities_ratio`](#liabilities_ratio---liabilities-ratio), [`debt_to_assets`](#debt_to_assets---debt-to-assets), [`debt_to_equity`](#debt_to_equity---debt-to-equity), [`net_debt_to_ebitda`](#net_debt_to_ebitda---net-debt-to-ebitda), [`interest_coverage`](#interest_coverage---interest-coverage), [`debt_coverage`](#debt_coverage---debt-coverage), [`cash_flow_to_debt`](#cash_flow_to_debt---free-cash-flow-to-debt), [`long_term_debt_to_working_capital`](#long_term_debt_to_working_capital---long-term-debt-to-working-capital), [`market_cap_to_debt`](#market_cap_to_debt---market-cap-to-debt)
- *liquidity*: [`current_ratio`](#current_ratio---current-ratio), [`quick_ratio`](#quick_ratio---quick-ratio), [`cash_ratio`](#cash_ratio---cash-ratio)
- *profitability*: [`gross_margin`](#gross_margin---gross-margin), [`ebit_margin`](#ebit_margin---ebit-margin), [`ebitda_margin`](#ebitda_margin---ebitda-margin), [`pretax_margin`](#pretax_margin---pretax-margin), [`net_margin`](#net_margin---net-margin), [`net_margin_stability`](#net_margin_stability---net-margin-stability), [`net_margin_change`](#net_margin_change---net-margin-change), [`return_on_equity`](#return_on_equity---return-on-equity), [`return_on_assets`](#return_on_assets---return-on-assets), [`return_on_invested_capital`](#return_on_invested_capital---return-on-invested-capital), [`magic_formula_return_on_capital`](#magic_formula_return_on_capital---return-on-capital-greenblatt), [`rule_of_forty`](#rule_of_forty---rule-of-40), [`research_intensity`](#research_intensity---research-intensity)
- *size*: [`revenue`](#revenue---revenue), [`net_income`](#net_income---net-income), [`free_cash_flow`](#free_cash_flow---free-cash-flow), [`market_capitalisation`](#market_capitalisation---market-capitalisation), [`enterprise_value`](#enterprise_value---enterprise-value)
- *valuation*: [`price_to_earnings`](#price_to_earnings---price-to-earnings), [`price_to_book`](#price_to_book---price-to-book), [`price_to_sales`](#price_to_sales---price-to-sales), [`price_to_free_cash_flow`](#price_to_free_cash_flow---price-to-free-cash-flow), [`earnings_yield`](#earnings_yield---earnings-yield), [`free_cash_flow_yield`](#free_cash_flow_yield---free-cash-flow-yield), [`ev_to_ebit`](#ev_to_ebit---ev-to-ebit), [`ev_to_ebitda`](#ev_to_ebitda---ev-to-ebitda), [`ev_to_sales`](#ev_to_sales---ev-to-sales), [`ev_to_free_cash_flow`](#ev_to_free_cash_flow---ev-to-free-cash-flow), [`magic_formula_earnings_yield`](#magic_formula_earnings_yield---earnings-yield-greenblatt), [`peg_ratio`](#peg_ratio---peg-ratio), [`dividend_yield`](#dividend_yield---dividend-yield), [`payout_ratio`](#payout_ratio---payout-ratio), [`market_cap_to_research`](#market_cap_to_research---market-cap-to-rd)

**Composites** (6)

- *ranking*: [`factor_rank`](#factor_rank---factor-rank), [`factor_percentile`](#factor_percentile---factor-percentile), [`factor_z_score`](#factor_z_score---factor-z-score), [`composite_score`](#composite_score---composite-score), [`top_n`](#top_n---top-n), [`quantile_bucket`](#quantile_bucket---quantile-bucket)

## Indicators

A number per bar, from price and volume history.

### Momentum

#### `rsi` - Relative Strength Index

Share of the recent move that was upward, mapped onto 0 to 100.

unit `index` · better when `undefined` · range 0 to 100 · also known as `relative_strength_index`

Splits each bar-to-bar change into a gain or a loss, smooths the two separately, and reports the gains as a proportion of total movement. A reading of 70 says roughly seven of every ten points travelled in the window were travelled upward. It says nothing about how far the price went in total, which is why a quiet drift and a violent rally can both read 70. The smoothing is the whole argument. Wilder smoothed with a constant of 1/n; an ordinary exponential average of the same period length uses 2/(n+1) and reacts roughly twice as fast. An RSI(14) built on a 14-period exponential average is not Wilder's RSI(14), it is closer to his RSI(27). This entry defaults to Wilder and offers the other two as parameters rather than pretending the choice does not exist.

```latex
U_t = \max(C_t - C_{t-1},\, 0), \qquad D_t = \max(C_{t-1} - C_t,\, 0)
```
Gain and loss of a single bar, both non-negative.

```latex
\overline{U}_t = \frac{(n-1)\overline{U}_{t-1} + U_t}{n}, \qquad \overline{D}_t = \frac{(n-1)\overline{D}_{t-1} + D_t}{n}
```
Wilder smoothing, seeded with the mean of the first n values that exist. Gains and losses come from a difference, so the first entry is missing; seeding at a fixed offset instead averages n-1 of them and places the reading a bar early.

```latex
RS_t = \frac{\overline{U}_t}{\overline{D}_t}
```

```latex
RSI_t = 100 - \frac{100}{1 + RS_t}
```
Equivalently 100 \cdot \overline{U} / (\overline{U} + \overline{D}), which is defined when the average loss is zero.

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `14` | int | Length of the smoothing window. |
| `method` | `'wilder'` | str | Which average smooths the gains and losses. One of `wilder`, `sma`, `ema`. |

Consumes: `close`

Implemented by `factorbase.factors.momentum:rsi`

Reference: Wilder, J. W. (1978). New Concepts in Technical Trading Systems, ch. 6.

#### `rate_of_change` - Rate of Change

Percentage change of the close over n bars.

unit `percent` · better when `higher` · also known as `roc`, `price_rate_of_change`

The plainest momentum measure there is: where the price stands now against where it stood n bars ago. Because it is a ratio it compares directly across instruments, which is what makes it the usual building block for cross-sectional momentum ranking.

```latex
ROC_t(n) = \left( \frac{C_t}{C_{t-n}} - 1 \right) \cdot 100
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `12` | int | How many bars back the comparison point sits. |

Consumes: `close`

Implemented by `factorbase.factors.momentum:rate_of_change`

Reference: Kirkpatrick, C. D. and Dahlquist, J. R. (2010). Technical Analysis, 2nd ed., ch. 14.

#### `absolute_price_change` - Absolute Price Change

Close minus the close n bars ago, in currency.

unit `currency` · better when `higher`

The same comparison as rate of change, left in currency instead of turned into a percentage. Not comparable across instruments, and included for the cases where that is the point: position sizing and stop placement work in currency, not in percent.

```latex
\Delta_t(n) = C_t - C_{t-n}
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `12` | int | How many bars back the comparison point sits. |

Consumes: `close`

Implemented by `factorbase.factors.momentum:absolute_price_change`

Reference: Kirkpatrick, C. D. and Dahlquist, J. R. (2010). Technical Analysis, 2nd ed., ch. 14.

#### `macd` - MACD Line

Fast exponential average minus slow exponential average.

unit `currency` · better when `undefined`

The difference between two exponential averages of the same series. Above zero the fast average leads, which is a compressed way of saying the recent price level sits above the older one. Its unit is currency, so readings are not comparable between a twenty-euro stock and a two-thousand-euro one, a limitation that trips up every attempt to rank a universe on raw MACD.

```latex
MACD_t = EMA_t(n_{fast}) - EMA_t(n_{slow})
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `fast_periods` | `12` | int | Period length of the faster exponential average. |
| `slow_periods` | `26` | int | Period length of the slower exponential average. |

Consumes: `close`

Implemented by `factorbase.factors.momentum:macd`

Reference: Appel, G. (2005). Technical Analysis: Power Tools for Active Investors, ch. 6.

#### `macd_signal` - MACD Signal Line

Exponential average of the MACD line.

unit `currency` · better when `undefined`

A smoothed copy of the MACD line, used as the thing the line is compared against. On its own it carries no information the MACD line does not; its purpose is to define the crossover.

```latex
Signal_t = EMA_t(MACD, n_{signal})
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `fast_periods` | `12` | int | Period length of the faster exponential average. |
| `slow_periods` | `26` | int | Period length of the slower exponential average. |
| `signal_periods` | `9` | int | Period length of the average applied to the MACD line. |

Consumes: `close`

Implemented by `factorbase.factors.momentum:macd_signal`

Reference: Appel, G. (2005). Technical Analysis: Power Tools for Active Investors, ch. 6.

#### `macd_histogram` - MACD Histogram

MACD line minus its signal line.

unit `currency` · better when `undefined`

The gap between the line and its own average. It crosses zero exactly where the two lines cross, and its height says how decisively. Reading the histogram turning before it crosses is the common use, and the common mistake: a turn in the histogram is a second derivative of price and is correspondingly noisy.

```latex
H_t = MACD_t - Signal_t
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `fast_periods` | `12` | int | Period length of the faster exponential average. |
| `slow_periods` | `26` | int | Period length of the slower exponential average. |
| `signal_periods` | `9` | int | Period length of the average applied to the MACD line. |

Consumes: `close`

Implemented by `factorbase.factors.momentum:macd_histogram`

Reference: Appel, G. (2005). Technical Analysis: Power Tools for Active Investors, ch. 6.

#### `macd_histogram_change` - MACD Histogram Change

Change in the MACD histogram over the last m bars, in currency.

unit `currency` · better when `higher`

Whether the gap between line and signal is widening or closing, stated as a difference rather than a direction. Left in currency deliberately: as a percentage it would divide by a quantity that crosses zero, which produces arbitrarily large readings exactly where the histogram is least informative.

```latex
\Delta H_t(m) = H_t - H_{t-m}
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `fast_periods` | `12` | int | Period length of the faster exponential average. |
| `slow_periods` | `26` | int | Period length of the slower exponential average. |
| `signal_periods` | `9` | int | Period length of the average applied to the MACD line. |
| `lookback` | `1` | int | How many bars back the comparison point sits. |

Consumes: `close`

Implemented by `factorbase.factors.momentum:macd_histogram_change`

Reference: Appel, G. (2005). Technical Analysis: Power Tools for Active Investors, ch. 6.

#### `macd_momentum` - MACD Momentum

Change in the MACD line itself over the last m bars.

unit `currency` · better when `higher`

The MACD line's own rate of change, not the histogram's. The two are often confused: the histogram measures the line against its average, this measures the line against its own past. A line far below zero but rising steeply has negative MACD and positive MACD momentum, and that combination is the case the distinction exists for.

```latex
\Delta MACD_t(m) = MACD_t - MACD_{t-m}
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `fast_periods` | `12` | int | Period length of the faster exponential average. |
| `slow_periods` | `26` | int | Period length of the slower exponential average. |
| `lookback` | `1` | int | How many bars back the comparison point sits. |

Consumes: `close`

Implemented by `factorbase.factors.momentum:macd_momentum`

Reference: Appel, G. (2005). Technical Analysis: Power Tools for Active Investors, ch. 6.

#### `cci` - Commodity Channel Index

Distance of the typical price from its average, in units of mean deviation.

unit `ratio` · better when `undefined` · also known as `commodity_channel_index`

Measures how unusual the current price is against its own recent behaviour, scaled by how much that behaviour normally varies. The constant 0.015 is not derived from anything; Lambert chose it so that roughly three readings in four land between -100 and +100. Three in four, not all: the measure is unbounded and readings beyond 300 happen. It is filed as a ratio rather than as a bounded oscillator for that reason, which is what distinguishes it from the RSI and the stochastics it is usually shelved next to. Mean absolute deviation is used rather than standard deviation, which is what separates this from a plain z-score and makes it less sensitive to one outlier bar.

```latex
TP_t = \frac{H_t + L_t + C_t}{3}
```
The typical price.

```latex
MD_t = \frac{1}{n} \sum_{i=0}^{n-1} \left| TP_{t-i} - SMA_t(TP, n) \right|
```
Mean absolute deviation around the current average, not around each bar own average.

```latex
CCI_t = \frac{TP_t - SMA_t(TP, n)}{0.015 \cdot MD_t}
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `20` | int | Window for both the average and the mean deviation. |

Consumes: `high`, `low`, `close`

Implemented by `factorbase.factors.momentum:cci`

Reference: Lambert, D. R. (1980). Commodity Channel Index. Commodities Magazine, October.

#### `williams_percent_r` - Williams %R

Where the close sits in the n-bar range, from 0 at the high to -100 at the low.

unit `index` · better when `undefined` · range -100 to 0 · also known as `williams_r`

The same quantity as the fast stochastic, on an inverted scale running from 0 down to -100. Reading it as an overbought gauge is the usual treatment and the usual error: in a strong trend it pins near its extreme for weeks, because pinning near the extreme is what a strong trend is.

```latex
\%R_t = \frac{HH_t(n) - C_t}{HH_t(n) - LL_t(n)} \cdot (-100)
```
HH and LL are the highest high and lowest low over the last n bars.

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `14` | int | Length of the range window. |

Consumes: `high`, `low`, `close`

Implemented by `factorbase.factors.momentum:williams_percent_r`

Reference: Williams, L. (1979). How I Made One Million Dollars Last Year Trading Commodities.

#### `stochastic_fast_k` - Fast Stochastic %K

Position of the close within the n-bar range, 0 to 100.

unit `index` · better when `undefined` · range 0 to 100

Lane's original question: is the close finishing near the top or the bottom of the range it has been trading in. Unsmoothed, so it is jumpy; the smoothed variants below exist because the raw line is difficult to use directly.

```latex
\%K_t = \frac{C_t - LL_t(n)}{HH_t(n) - LL_t(n)} \cdot 100
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `14` | int | Length of the range window. |

Consumes: `high`, `low`, `close`

Implemented by `factorbase.factors.momentum:stochastic_fast_k`

Reference: Lane, G. C. (1984). Lane on Stochastics. Technical Analysis of Stocks and Commodities 2(3).

#### `stochastic_fast_d` - Fast Stochastic %D

Short moving average of fast %K.

unit `index` · better when `undefined` · range 0 to 100

Three-bar average of the raw line. It is also, by definition, the slow %K: the naming is historical and confuses everyone once. What one package calls fast %D another calls slow %K, and they are the same series.

```latex
\%D_t = SMA_t(\%K, d)
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `14` | int | Length of the range window. |
| `smoothing` | `3` | int | Length of the average applied to %K. |

Consumes: `high`, `low`, `close`

Implemented by `factorbase.factors.momentum:stochastic_fast_d`

Reference: Lane, G. C. (1984). Lane on Stochastics. Technical Analysis of Stocks and Commodities 2(3).

#### `stochastic_slow_k` - Slow Stochastic %K

Fast %K smoothed once. Identical to fast %D.

unit `index` · better when `undefined` · range 0 to 100

Listed separately because screeners ask for it by this name, and because leaving it out would make the pair slow %K and slow %D look like they had different ancestry. They do not: slow %K is fast %D, and slow %D is that smoothed again.

```latex
\%K^{slow}_t = SMA_t(\%K, d_1)
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `14` | int | Length of the range window. |
| `smoothing` | `3` | int | Length of the first average. |

Consumes: `high`, `low`, `close`

Implemented by `factorbase.factors.momentum:stochastic_slow_k`

Reference: Lane, G. C. (1984). Lane on Stochastics. Technical Analysis of Stocks and Commodities 2(3).

#### `stochastic_slow_d` - Slow Stochastic %D

Fast %K smoothed twice.

unit `index` · better when `undefined` · range 0 to 100

The line most charting packages draw as the dotted one. Two passes of a three-bar average over the raw stochastic, which is enough smoothing that its crossings lag visibly, and few enough that it still moves.

```latex
\%D^{slow}_t = SMA_t\!\left( SMA(\%K, d_1),\, d_2 \right)
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `14` | int | Length of the range window. |
| `smoothing` | `3` | int | Length of the first average. |
| `second_smoothing` | `3` | int | Length of the second average. |

Consumes: `high`, `low`, `close`

Implemented by `factorbase.factors.momentum:stochastic_slow_d`

Reference: Lane, G. C. (1984). Lane on Stochastics. Technical Analysis of Stocks and Commodities 2(3).

#### `double_smoothed_stochastic_blau` - Double Smoothed Stochastic (Blau)

Stochastic whose numerator and denominator are each smoothed twice before dividing.

unit `index` · better when `undefined` · range 0 to 100

Blau's construction smooths the two halves of the stochastic ratio separately and divides only at the end. The ordinary approach divides first and smooths the quotient, which lets a single narrow-range bar, where the denominator is near zero, dominate the smoothed result. Dividing last removes that failure mode, and is the reason this variant is noticeably steadier than a doubly smoothed plain stochastic.

```latex
N_t = EMA_t\!\left( EMA(C - LL(n),\, r),\, s \right)
```

```latex
D_t = EMA_t\!\left( EMA(HH(n) - LL(n),\, r),\, s \right)
```

```latex
DSS_t = 100 \cdot \frac{N_t}{D_t}
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `10` | int | Length of the range window. |
| `first_smoothing` | `3` | int | Period of the inner exponential average. |
| `second_smoothing` | `3` | int | Period of the outer exponential average. |

Consumes: `high`, `low`, `close`

Implemented by `factorbase.factors.momentum:double_smoothed_stochastic_blau`

**Note.** The defaults here are this package's, not a quoted standard. Published charts of this indicator use several different triples and rarely say which.

Reference: Blau, W. (1995). Momentum, Direction and Divergence, ch. 4.

#### `double_smoothed_stochastic_bressert` - Double Smoothed Stochastic (Bressert)

Stochastic of a smoothed stochastic, smoothed again.

unit `index` · better when `undefined` · range 0 to 100

A different route to the same goal as Blau's. Bressert takes the ordinary stochastic, smooths it, then takes the stochastic of that smoothed line and smooths once more. Because the second stochastic rescales to the full 0 to 100 range, the result reaches its extremes more readily than Blau's version does, which is the practical difference between the two.

```latex
\%K_t = \frac{C_t - LL_t(n)}{HH_t(n) - LL_t(n)} \cdot 100
```

```latex
S_t = EMA_t(\%K, r)
```

```latex
\%K^{(2)}_t = \frac{S_t - LL_t(S, n)}{HH_t(S, n) - LL_t(S, n)} \cdot 100
```

```latex
DSS_t = EMA_t\!\left( \%K^{(2)}, s \right)
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `10` | int | Length of both range windows. |
| `first_smoothing` | `3` | int | Period of the average applied to the first stochastic. |
| `second_smoothing` | `3` | int | Period of the average applied to the second stochastic. |

Consumes: `high`, `low`, `close`

Implemented by `factorbase.factors.momentum:double_smoothed_stochastic_bressert`

**Note.** The defaults here are this package's, not a quoted standard.

Reference: Bressert, W. (1991). The Power of Oscillator/Cycle Combinations.

### Moving Average

#### `sma` - Simple Moving Average

Unweighted mean of the last n closes.

unit `price` · better when `undefined` · range 0 to None · also known as `simple_moving_average`

Adds the last n closing prices and divides by n. Every price in the window counts the same, and a price leaving the window at the back end moves the average as much as the new price entering at the front. That second effect is the one most readers forget: an SMA can turn down on a day the price rose, purely because a high value dropped out of the window.

```latex
SMA_t(n) = \frac{1}{n} \sum_{i=0}^{n-1} C_{t-i}
```
C is the close, n the window length in bars.

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `200` | int | Number of bars in the window. |

Consumes: `close`

Implemented by `factorbase.factors.moving_averages:sma`

Reference: Kirkpatrick, C. D. and Dahlquist, J. R. (2010). Technical Analysis, 2nd ed., ch. 14.

#### `ema` - Exponential Moving Average

Weighted mean of all past closes, weights decaying geometrically.

unit `price` · better when `undefined` · range 0 to None · also known as `exponential_moving_average`

Each new close gets weight alpha, everything before it keeps 1 - alpha of what it had. No price ever leaves the average entirely, so the drop-out effect of the simple average does not occur. The warm-up matters: the series is seeded with the simple average of the first n closes, which is the common convention and the reason two implementations of "the same" EMA can differ for the first few hundred bars.

```latex
\alpha = \frac{2}{n + 1}
```
The smoothing constant implied by a period length n.

```latex
EMA_t = \alpha C_t + (1 - \alpha) EMA_{t-1}
```

```latex
EMA_{n-1} = \frac{1}{n} \sum_{i=0}^{n-1} C_i
```
Seed value. Bars before this are undefined, not zero.

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `200` | int | Period length the smoothing constant is derived from. |

Consumes: `close`

Implemented by `factorbase.factors.moving_averages:ema`

Reference: Kirkpatrick, C. D. and Dahlquist, J. R. (2010). Technical Analysis, 2nd ed., ch. 14.

#### `wma` - Weighted Moving Average

Mean of the last n closes with linearly falling weights.

unit `price` · better when `undefined` · range 0 to None · also known as `weighted_moving_average`

The newest close is weighted n, the one before it n-1, down to 1 for the oldest. It reacts faster than the simple average and, unlike the exponential one, forgets a price completely once it leaves the window.

```latex
WMA_t(n) = \frac{\sum_{i=0}^{n-1} (n - i) \, C_{t-i}}{\sum_{i=1}^{n} i}
```

```latex
\sum_{i=1}^{n} i = \frac{n(n+1)}{2}
```
The normalising divisor, written out.

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `200` | int | Number of bars in the window. |

Consumes: `close`

Implemented by `factorbase.factors.moving_averages:wma`

Reference: Kirkpatrick, C. D. and Dahlquist, J. R. (2010). Technical Analysis, 2nd ed., ch. 14.

#### `price_to_ma_distance` - Distance From Moving Average

How far the close sits above or below its own moving average, in percent.

unit `percent` · better when `undefined` · also known as `ma_distance`

Expresses the gap between price and average as a share of the average, so readings compare across instruments of any price level. Positive means the close is above the average. This is the factor that answers "extended" or "stretched" with a number instead of an adjective.

```latex
D_t = \frac{C_t - MA_t(n)}{MA_t(n)} \cdot 100
```
MA is whichever average `method` selects.

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `200` | int | Window of the average the price is measured against. |
| `method` | `'sma'` | str | Which of the three averages to use. One of `sma`, `ema`, `wma`. |

Consumes: `close`

Implemented by `factorbase.factors.moving_averages:price_to_ma_distance`

Reference: Kirkpatrick, C. D. and Dahlquist, J. R. (2010). Technical Analysis, 2nd ed., ch. 14.

#### `ma_to_ma_distance` - Distance Between Two Moving Averages

Gap between a fast and a slow moving average, in percent of the slow one.

unit `percent` · better when `undefined` · also known as `ma_ma_distance`

The continuous version of a crossover. A crossover only tells you the sign changed; this tells you how far apart the two averages are, which is what distinguishes a decisive trend from two lines grazing each other.

```latex
D_t = \frac{MA_t(n_{fast}) - MA_t(n_{slow})}{MA_t(n_{slow})} \cdot 100
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `fast_periods` | `50` | int | Window of the faster average. |
| `slow_periods` | `200` | int | Window of the slower average. |
| `method` | `'sma'` | str | Which average both windows use. One of `sma`, `ema`, `wma`. |

Consumes: `close`

Implemented by `factorbase.factors.moving_averages:ma_to_ma_distance`

Reference: Kirkpatrick, C. D. and Dahlquist, J. R. (2010). Technical Analysis, 2nd ed., ch. 14.

#### `ma_slope` - Moving Average Slope

Percentage change of a moving average over the last m bars.

unit `percent` · better when `higher`

Measures whether the average is rising and how steeply, without reference to where the price currently is. A long-term average that is still falling is a different situation from one that has turned up, even when the price is above both.

```latex
S_t = \frac{MA_t(n) - MA_{t-m}(n)}{MA_{t-m}(n)} \cdot 100
```
m is the lookback over which the slope is measured, not the average's own window.

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `200` | int | Window of the average whose slope is taken. |
| `lookback` | `20` | int | How many bars back the comparison point sits. |
| `method` | `'sma'` | str | Which average to take the slope of. One of `sma`, `ema`, `wma`. |

Consumes: `close`

Implemented by `factorbase.factors.moving_averages:ma_slope`

Reference: Kirkpatrick, C. D. and Dahlquist, J. R. (2010). Technical Analysis, 2nd ed., ch. 14.

#### `ma_slope_normalized` - Normalised Moving Average Slope

Slope of a moving average divided by the instrument's volatility.

unit `ratio` · better when `higher`

The plain slope favours volatile instruments: a two percent weekly rise means something different for a utility than for a biotech. Dividing by average true range over the same window puts both on the same scale, which is what makes the factor rankable across a mixed universe.

```latex
S^{norm}_t = \frac{MA_t(n) - MA_{t-m}(n)}{ATR_t(n)}
```
Result is in units of average daily range, not percent.

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `200` | int | Window of the average whose slope is taken. |
| `lookback` | `20` | int | How many bars back the comparison point sits. |
| `method` | `'sma'` | str | Which average to take the slope of. One of `sma`, `ema`, `wma`. |

Consumes: `high`, `low`, `close`

Implemented by `factorbase.factors.moving_averages:ma_slope_normalized`

Reference: Wilder, J. W. (1978). New Concepts in Technical Trading Systems, ch. 3.

### Performance

#### `price` - Price

The close.

unit `price` · better when `undefined` · range 0 to None

Listed as a factor because screens filter on price level directly, and because leaving it out would push callers to reach around the factor interface for the one column everything else is built on.

```latex
P_t = C_t
```

Consumes: `close`

Implemented by `factorbase.factors.performance:price`

Reference: No reference. It is the close.

#### `performance` - Performance

Percentage return over n bars.

unit `percent` · better when `higher`

Return between two points, nothing more. Set `adjusted` to read it off the adjusted close and get a total return including dividends; leave it off for a price return. The switch raises rather than falling back when the frame has no adjusted column, because a total-return factor quietly reporting a price return is a difference of several percent a year that nothing in the output would reveal.

```latex
R_t(n) = \left( \frac{P_t}{P_{t-n}} - 1 \right) \cdot 100
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `250` | int | How many bars back the comparison point sits. |
| `adjusted` | `False` | bool | Read the return off the adjusted close instead of the close. |

Consumes: `close`, `adjusted_close`

Implemented by `factorbase.factors.performance:performance`

Reference: Bacon, C. R. (2008). Practical Portfolio Performance Measurement and Attribution, 2nd ed., ch. 2.

#### `daily_performance` - Daily Performance

Percentage return of the latest bar.

unit `percent` · better when `higher`

One bar's return. Its use in a catalogue of ranking factors is as an input to other things rather than as a ranking on its own; ranking a universe on yesterday's move ranks it on noise.

```latex
r_t = \left( \frac{P_t}{P_{t-1}} - 1 \right) \cdot 100
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `adjusted` | `False` | bool | Read the return off the adjusted close instead of the close. |

Consumes: `close`, `adjusted_close`

Implemented by `factorbase.factors.performance:daily_performance`

Reference: Bacon, C. R. (2008). Practical Portfolio Performance Measurement and Attribution, 2nd ed., ch. 2.

#### `annualised_performance` - Annualised Performance

Compound annual growth rate over the window.

unit `percent` · better when `higher` · also known as `cagr`, `geometric_performance`

The geometric rate, which is what the account shows, not the arithmetic mean of the returns. The gap between them is larger than most readers expect: a year of +50 percent followed by a year of -50 percent averages zero arithmetically and -13.4 percent a year geometrically.

```latex
y = \frac{n}{T}
```
Window length in years. T is trading days per year.

```latex
CAGR_t = \left( \left( \frac{P_t}{P_{t-n}} \right)^{1/y} - 1 \right) \cdot 100
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `750` | int | Length of the window in bars. |
| `trading_days` | `250` | int | How many bars make a year. |
| `adjusted` | `False` | bool | Read the return off the adjusted close instead of the close. |

Consumes: `close`, `adjusted_close`

Implemented by `factorbase.factors.performance:annualised_performance`

Reference: Bacon, C. R. (2008). Practical Portfolio Performance Measurement and Attribution, 2nd ed., ch. 2.

#### `winning_days` - Winning Days

Share of bars in the window that closed up, in percent.

unit `percent` · better when `higher` · range 0 to 100

How often, rather than how much. A high reading with a poor return means the losses were large and rare; a low reading with a good return means the gains were. Unchanged bars count as losses, matching the usual convention, which moves the reading by several points on thin instruments where unchanged closes are common.

```latex
W_t = \frac{1}{n} \sum_{i=0}^{n-1} \mathbb{1}\left[ C_{t-i} > C_{t-i-1} \right] \cdot 100
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `250` | int | Length of the window. |

Consumes: `close`

Implemented by `factorbase.factors.performance:winning_days`

Reference: Bacon, C. R. (2008). Practical Portfolio Performance Measurement and Attribution, 2nd ed., ch. 4.

#### `distance_to_high` - Distance to the High

How far the close sits below the window's highest close, in percent.

unit `percent` · better when `higher` · range None to 0

Zero at a new high and negative everywhere else. Measured close against highest close, not against highest intraday high: a single spike on one bad print would otherwise hold the reading down for a year, and data errors in intraday highs are the most common kind.

```latex
D^{high}_t = \left( \frac{C_t}{\max_{0 \le i < n} C_{t-i}} - 1 \right) \cdot 100
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `250` | int | Length of the window. |

Consumes: `close`

Implemented by `factorbase.factors.performance:distance_to_high`

Reference: Kirkpatrick, C. D. and Dahlquist, J. R. (2010). Technical Analysis, 2nd ed., ch. 12.

#### `distance_to_low` - Distance to the Low

How far the close sits above the window's lowest close, in percent.

unit `percent` · better when `higher` · range 0 to None

The mirror of the previous entry, and one of the conditions in the trend template. Zero at a new low.

```latex
D^{low}_t = \left( \frac{C_t}{\min_{0 \le i < n} C_{t-i}} - 1 \right) \cdot 100
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `250` | int | Length of the window. |

Consumes: `close`

Implemented by `factorbase.factors.performance:distance_to_low`

Reference: Kirkpatrick, C. D. and Dahlquist, J. R. (2010). Technical Analysis, 2nd ed., ch. 12.

#### `inside_bars` - Inside Bars

How many bars in the window traded entirely inside their predecessor's range.

unit `count` · better when `undefined` · range 0 to None

An inside bar has a lower high and a higher low than the bar before it: the whole session happened within yesterday's range. A cluster of them is compression, which is the state that precedes expansion, and counting them finds it more cheaply than fitting a range does.

```latex
I_t = \sum_{i=0}^{n-1} \mathbb{1}\left[ H_{t-i} < H_{t-i-1} \;\wedge\; L_{t-i} > L_{t-i-1} \right]
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `20` | int | Length of the window. |

Consumes: `high`, `low`

Implemented by `factorbase.factors.performance:inside_bars`

Reference: Crabel, T. (1990). Day Trading with Short Term Price Patterns and Opening Range Breakout.

#### `bars_of_history` - Bars of History

How many bars the instrument has traded up to and including this one.

unit `days` · better when `higher` · range 0 to None

A gate, not a signal. Most factors here need a year or more of history, and a universe assembled without checking this fills up with recent listings whose readings are either NaN or, worse, computed from a window that happens to be just long enough to return a number.

```latex
B_t = \sum_{i=0}^{t} \mathbb{1}\left[ C_i \text{ exists} \right]
```

Consumes: `close`

Implemented by `factorbase.factors.performance:bars_of_history`

Reference: No reference. It counts rows.

### Relative

#### `relative_strength_levy` - Relative Strength (Levy)

Close divided by its own moving average.

unit `ratio` · better when `higher` · range 0 to None · also known as `rsl`

Levy's measure compares the instrument to its own past, not to anything external, despite the name it is filed under. Above 1 the price sits above its average. It is here because screeners list it under relative strength and that is where readers look for it. The usual window is 27 weeks, which is 130 trading days, and that is the default. Levy's own work used weekly data over 26 weeks; the daily equivalent is not identical, and nobody who quotes "RSL" says which they mean.

```latex
RSL_t = \frac{C_t}{SMA_t(C, n)}
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `130` | int | Window of the average, in bars. |

Consumes: `close`

Implemented by `factorbase.factors.relative:relative_strength_levy`

Reference: Levy, R. A. (1967). Relative Strength as a Criterion for Investment Selection. Journal of Finance 22(4).

#### `relative_strength_line` - Relative Strength Line

Price divided by benchmark, rebased to 100 at the first common bar.

unit `index` · better when `higher` · range 0 to None · needs a `benchmark` series

The line that rises when the instrument beats the market, whichever way the market went. Rebasing at the start of the loaded window makes it readable, but the level still depends on where the window starts, so it cannot be ranked across instruments. Rank on outperformance instead, or on the line's distance from its own high.

```latex
RS_t = \frac{C_t / B_t}{C_{t_0} / B_{t_0}} \cdot 100
```
B is the benchmark close, t0 the first bar where both exist.

Consumes: `close`

Implemented by `factorbase.factors.relative:relative_strength_line`

**Note.** Level depends on the loaded window. Not comparable across instruments.

Reference: O'Neil, W. J. (2009). How to Make Money in Stocks, 4th ed., ch. 6.

#### `outperformance` - Outperformance

Instrument return minus benchmark return over n bars, in percentage points.

unit `percent` · better when `higher` · needs a `benchmark` series

A difference of two percentage returns, not a ratio of them. The difference is what a reader expects from the word and it adds across instruments; the ratio does neither, and is what a naive division produces.

```latex
O_t(n) = \left( \frac{C_t}{C_{t-n}} - 1 \right) \cdot 100 - \left( \frac{B_t}{B_{t-n}} - 1 \right) \cdot 100
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `250` | int | How many bars back the comparison point sits. |

Consumes: `close`

Implemented by `factorbase.factors.relative:outperformance`

Reference: Levy, R. A. (1967). Relative Strength as a Criterion for Investment Selection. Journal of Finance 22(4).

#### `beta` - Beta

Least-squares slope of the instrument's daily returns on the benchmark's.

unit `ratio` · better when `undefined` · needs a `benchmark` series

How much the instrument has moved for a one-point move in the market, on average, over the window. Estimated on simple returns rather than log returns: beta enters portfolio arithmetic through weighted sums of simple returns, and estimating it on logs quietly changes what the number means. It is a backward-looking regression coefficient and nothing more. Its standard error is large on a year of daily data, which is why the shrunk estimate below exists.

```latex
r_t = \frac{C_t}{C_{t-1}} - 1, \qquad m_t = \frac{B_t}{B_{t-1}} - 1
```

```latex
\beta_t = \frac{\operatorname{Cov}(r, m)}{\operatorname{Var}(m)}
```
Both moments taken over the last n bars.

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `250` | int | Length of the estimation window. |

Consumes: `close`

Implemented by `factorbase.factors.relative:beta`

Reference: Sharpe, W. F. (1964). Capital Asset Prices. Journal of Finance 19(3).

#### `shrunk_beta` - Shrunk Beta

Beta from separate volatility and correlation windows, pulled towards one.

unit `ratio` · better when `undefined` · needs a `benchmark` series

Frazzini and Pedersen split beta into the ratio of volatilities and the correlation, and estimate the two over different windows. Volatility is measured over a year of daily returns; correlation over five years of overlapping three-day returns, because daily correlations are depressed by non-synchronous trading and that depression biases beta downward for smaller instruments. The estimate is then shrunk towards 1, the beta of a randomly chosen stock. The weight of 0.6 is theirs and is not derived from the data; it is a prior, and the entry calls it one.

```latex
\hat{\beta}_t = \hat{\rho}_t \cdot \frac{\hat{\sigma}_t}{\hat{\sigma}^{m}_t}
```

```latex
\beta^{shrunk}_t = w \hat{\beta}_t + (1 - w) \cdot 1
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `volatility_periods` | `250` | int | Bars of daily returns for the two volatilities. |
| `correlation_periods` | `1250` | int | Bars of overlapping returns for the correlation. |
| `correlation_horizon` | `3` | int | How many days each overlapping return spans. |
| `weight` | `0.6` | float | Weight on the estimate; the remainder goes to 1. |

Consumes: `close`

Implemented by `factorbase.factors.relative:shrunk_beta`

**Note.** Needs five years of history at the default correlation window. On shorter series it is NaN throughout, which is the honest answer.

Reference: Frazzini, A. and Pedersen, L. H. (2014). Betting Against Beta. Journal of Financial Economics 111(1).

#### `return_correlation` - Return Correlation

Rolling correlation of daily returns with the benchmark.

unit `ratio` · better when `undefined` · range -1 to 1 · needs a `benchmark` series

How closely the instrument tracks the market, on a scale from -1 to 1, independent of how far it moves. Correlation and beta answer different questions: a high-volatility stock can have beta 2 and correlation 0.5, and a low-volatility one beta 0.5 and correlation 0.9.

```latex
\rho_t = \frac{\operatorname{Cov}(r, m)}{\sigma_r \, \sigma_m}
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `250` | int | Length of the estimation window. |

Consumes: `close`

Implemented by `factorbase.factors.relative:return_correlation`

Reference: Elton, E. J. et al. (2014). Modern Portfolio Theory and Investment Analysis, 9th ed., ch. 7.

#### `downside_correlation` - Downside Correlation

Correlation computed only on the bars where the benchmark fell.

unit `ratio` · better when `lower` · range -1 to 1 · needs a `benchmark` series

The correlation that decides whether a position actually diversifies is the one that holds when the market falls, and it is routinely higher than the all-weather number. An instrument advertised as uncorrelated at 0.2 overall can sit at 0.8 on down days, which is the reading that matters. Windows containing fewer than `minimum_days` down bars return NaN. A correlation from eight observations is not a weak estimate, it is noise wearing the costume of an estimate.

```latex
\rho^{-}_t = \operatorname{Corr}\left( r_i, m_i \;\middle|\; m_i < 0,\; t-n < i \le t \right)
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `250` | int | Length of the window the down bars are drawn from. |
| `minimum_days` | `20` | int | Below this many down bars in the window, the result is undefined. |

Consumes: `close`

Implemented by `factorbase.factors.relative:downside_correlation`

Reference: Ang, A., Chen, J. and Xing, Y. (2006). Downside Risk. Review of Financial Studies 19(4).

#### `downside_outperformance` - Downside Outperformance

Mean excess return on the bars where the benchmark fell.

unit `percent` · better when `higher` · needs a `benchmark` series

How the instrument behaves on the market's bad days, which is a different question from how it behaves on average. Positive means it fell less than the market, or rose while the market fell. Subject to the same minimum count as the downside correlation and for the same reason.

```latex
O^{-}_t = \operatorname{mean}\left( (r_i - m_i) \cdot 100 \;\middle|\; m_i < 0,\; t-n < i \le t \right)
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `250` | int | Length of the window the down bars are drawn from. |
| `minimum_days` | `20` | int | Below this many down bars in the window, the result is undefined. |

Consumes: `close`

Implemented by `factorbase.factors.relative:downside_outperformance`

Reference: Ang, A., Chen, J. and Xing, Y. (2006). Downside Risk. Review of Financial Studies 19(4).

#### `jensen_alpha` - Jensen's Alpha

Annualised intercept of the return regression against the benchmark.

unit `percent` · better when `higher` · needs a `benchmark` series

The part of the return the benchmark does not explain, annualised. Unlike outperformance it adjusts for how much market exposure the instrument carried: a stock with beta 2 in a market that rose 10 percent is expected to rise 20, and only the remainder counts here. The risk-free rate is a single annual constant rather than a series. With a varying rate the intercept would also absorb its variation, which is a different quantity from the one this entry names.

```latex
r^{e}_t = r_t - r_f, \qquad m^{e}_t = m_t - r_f
```

```latex
\alpha_t = \overline{r^{e}} - \beta_t \, \overline{m^{e}}
```

```latex
\alpha^{ann}_t = \left( (1 + \alpha_t)^{T} - 1 \right) \cdot 100
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `250` | int | Length of the estimation window. |
| `trading_days` | `250` | int | Annualisation factor. |
| `risk_free_rate` | `0.0` | float | Annual risk-free rate in percent, held constant across the window. |

Consumes: `close`

Implemented by `factorbase.factors.relative:jensen_alpha`

Reference: Jensen, M. C. (1968). The Performance of Mutual Funds in the Period 1945-1964. Journal of Finance 23(2).

### Seasonality

#### `seasonal_strength` - Seasonal Strength

Mean past return at this point of the calendar, in percent.

unit `percent` · better when `higher`

For each bar, the daily returns of every earlier bar within the lookback that falls in the same bucket are averaged. Only earlier bars: including the current one lets today's return feed its own seasonal reading, which is a small effect on a five-year window and an enormous one on a short series. `detrend` subtracts the mean daily return over the same lookback, so the figure is the excess over the instrument's own drift. Leave it off and anything that rose over the period reads positive in every bucket: the factor then ranks the universe on drift while appearing to rank it on seasonality, and every reading is the same number plus noise. The honest caveat, which the readings do not carry and the reader has to: with five years of history a weekday bucket holds around 260 observations and a quarter around 315, but a five-day calendar window holds roughly 55. The standard error on a mean of 55 daily returns is about a fifth of a percent, so most of what this factor reports is indistinguishable from zero. It gives the mean and not a significance, because what counts as significant is the caller's decision, and nothing here accounts for a screen testing thousands of buckets at once.

```latex
r_i = \left( \frac{C_i}{C_{i-1}} - 1 \right) \cdot 100
```

```latex
W_t = \{ i : t - y \text{ years} \le d_i < d_t \}
```
Strictly earlier bars inside the lookback. The current bar is excluded.

```latex
B_t = \{ i \in W_t : b(d_i) = b(d_t) \}
```
b is the bucket. For a calendar window it is the day of the year, matched within w days and measured circularly so that late December sits beside early January.

```latex
S_t = \frac{1}{|B_t|} \sum_{i \in B_t} r_i \;-\; \delta \cdot \frac{1}{|W_t|} \sum_{i \in W_t} r_i
```
The second term is subtracted only when detrend is set.

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `bucket` | `'calendar_window'` | str | What counts as the same point of the calendar: a window of days around the same day of the year, the same calendar month, the same weekday, or the same quarter. One of `calendar_window`, `month`, `day_of_week`, `quarter`. |
| `years` | `5` | int | How far back the lookback reaches. |
| `window_days` | `5` | int | Half-width of the calendar window, in days of the year. Ignored by the other two buckets. |
| `detrend` | `True` | bool | Report the excess over the mean daily return of the same lookback rather than the raw mean. |

Consumes: `close`

Implemented by `factorbase.factors.seasonality:seasonal_strength`

**Note.** Needs a date index. One of three entries in this catalogue that does, with the hit rate below and the weekly volatility. Given any other index it raises UnsupportedIndexError naming itself.

Reference: Bouman, S. and Jacobsen, B. (2002). The Halloween Indicator. American Economic Review 92(5).
Reference: Lakonishok, J. and Smidt, S. (1988). Are Seasonal Anomalies Real? Review of Financial Studies 1(4).

#### `seasonal_hit_rate` - Seasonal Hit Rate

Share of past bars in this bucket that closed up, in percent.

unit `percent` · better when `higher` · range 0 to 100

The companion to the mean, and it answers a different question. A bucket whose mean is carried by one enormous day reads high there and near 50 here, which is what a seasonal claim usually turns out to be once the single day is found. Reading the two together is the point; reading either alone is how a seasonal screen convinces itself. No drift adjustment, deliberately. A share of up days is already free of the size of the drift, and subtracting a mean from a proportion would not mean anything.

```latex
H_t = \frac{\left| \{ i \in B_t : r_i > 0 \} \right|}{|B_t|} \cdot 100
```
Same bucket and lookback as the entry above. An unchanged bar counts as not up.

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `bucket` | `'calendar_window'` | str | What counts as the same point of the calendar. One of `calendar_window`, `month`, `day_of_week`, `quarter`. |
| `years` | `5` | int | How far back the lookback reaches. |
| `window_days` | `5` | int | Half-width of the calendar window, in days of the year. |

Consumes: `close`

Implemented by `factorbase.factors.seasonality:seasonal_hit_rate`

**Note.** Needs a date index, like the entry above.

Reference: Lakonishok, J. and Smidt, S. (1988). Are Seasonal Anomalies Real? Review of Financial Studies 1(4).

### Trend

#### `plus_di` - Positive Directional Indicator

Share of recent range travelled by rising highs.

unit `index` · better when `higher` · range 0 to 100

Counts how much of the bar-to-bar movement went into new highs, expressed against the average true range so that it is comparable across instruments. Only one of the two directional indicators can rise on a given bar; an inside bar contributes to neither.

```latex
+DM_t = \begin{cases} H_t - H_{t-1} & \text{if } H_t - H_{t-1} > L_{t-1} - L_t \text{ and } H_t > H_{t-1} \\ 0 & \text{otherwise} \end{cases}
```

```latex
+DI_t = 100 \cdot \frac{\overline{+DM}_t}{\overline{TR}_t}
```
Both averages are Wilder smoothings over n bars. The first bar has no predecessor and so contributes no directional movement at all, which is not the same as contributing zero: a zero would be averaged into the seed while the true range it is divided by is seeded from a full n bars, and the two halves would start out misaligned.

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `14` | int | Length of the smoothing window. |

Consumes: `high`, `low`, `close`

Implemented by `factorbase.factors.trend:plus_di`

Reference: Wilder, J. W. (1978). New Concepts in Technical Trading Systems, ch. 4.

#### `minus_di` - Negative Directional Indicator

Share of recent range travelled by falling lows.

unit `index` · better when `lower` · range 0 to 100

The mirror of the positive indicator. Its value on its own is less useful than its distance from the positive one, which is what the DX and then the ADX are built from.

```latex
-DM_t = \begin{cases} L_{t-1} - L_t & \text{if } L_{t-1} - L_t > H_t - H_{t-1} \text{ and } L_t < L_{t-1} \\ 0 & \text{otherwise} \end{cases}
```

```latex
-DI_t = 100 \cdot \frac{\overline{-DM}_t}{\overline{TR}_t}
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `14` | int | Length of the smoothing window. |

Consumes: `high`, `low`, `close`

Implemented by `factorbase.factors.trend:minus_di`

Reference: Wilder, J. W. (1978). New Concepts in Technical Trading Systems, ch. 4.

#### `adx` - Average Directional Index

How one-sided the movement has been, regardless of direction.

unit `index` · better when `undefined` · range 0 to 100

Measures trend strength without saying which way. A rising ADX during a collapse reads exactly like a rising ADX during a rally; the sign lives in the two directional indicators, not here. It is smoothed twice, once on the directional movement and again on the DX. That is why the reading lags the turn in price by roughly the period length and why an ADX crossing 25 describes what has already happened.

```latex
DX_t = 100 \cdot \frac{\left| +DI_t - (-DI_t) \right|}{+DI_t + (-DI_t)}
```

```latex
ADX_t = \frac{(n-1) \, ADX_{t-1} + DX_t}{n}
```
Wilder smoothing again, seeded with the mean of the first n DX values.

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `14` | int | Length of both smoothing windows. |

Consumes: `high`, `low`, `close`

Implemented by `factorbase.factors.trend:adx`

Reference: Wilder, J. W. (1978). New Concepts in Technical Trading Systems, ch. 4.

#### `aroon_up` - Aroon Up

How recently the highest high of the window occurred, as a percentage.

unit `index` · better when `higher` · range 0 to 100

100 when today is the highest high of the window, falling towards 0 as that high recedes into the past. It reads the timing of an extreme rather than its size, which makes it insensitive to how violent the move was and sensitive to whether it is still going on.

```latex
AroonUp_t = \frac{n - 1 - b_t}{n - 1} \cdot 100
```
b is the number of bars since the highest high inside the window of n bars, counted from the most recent bar that attains it.

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `25` | int | Length of the window. |

Consumes: `high`

Implemented by `factorbase.factors.trend:aroon_up`

**Note.** Measured over a window of n bars, so a fresh high reads 100 and the oldest bar in the window reads 0. Implementations that use n+1 bars produce slightly different intermediate values. Where several bars share the highest high, the most recent of them counts. The measure asks how long ago the high happened, and with two equal highs that is the later one. Taking the first, which is what argmax returns, reports a high that is one bar old as six bars old, and makes a bar that merely matches the window high read low instead of 100 - the ordinary situation at a round-number resistance.

Reference: Chande, T. S. (1995). The Time Price Oscillator. Technical Analysis of Stocks and Commodities 13(9).

#### `aroon_down` - Aroon Down

How recently the lowest low of the window occurred, as a percentage.

unit `index` · better when `lower` · range 0 to 100

The mirror of Aroon Up. High readings mean the low is fresh, which is a bearish condition, so the direction field says lower is better.

```latex
AroonDown_t = \frac{n - 1 - b_t}{n - 1} \cdot 100
```
b is the number of bars since the lowest low inside the window, counted from the most recent bar that attains it.

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `25` | int | Length of the window. |

Consumes: `low`

Implemented by `factorbase.factors.trend:aroon_down`

Reference: Chande, T. S. (1995). The Time Price Oscillator. Technical Analysis of Stocks and Commodities 13(9).

#### `aroon_oscillator` - Aroon Oscillator

Aroon Up minus Aroon Down.

unit `index` · better when `higher` · range -100 to 100

One line instead of two, running from -100 to +100. Positive means the recent high is fresher than the recent low. It loses the information that both extremes are old, which is the signature of a range and is visible only in the two lines separately.

```latex
AroonOsc_t = AroonUp_t - AroonDown_t
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `25` | int | Length of the window. |

Consumes: `high`, `low`

Implemented by `factorbase.factors.trend:aroon_oscillator`

Reference: Chande, T. S. (1995). The Time Price Oscillator. Technical Analysis of Stocks and Commodities 13(9).

#### `regression_slope_annualised` - Annualised Regression Slope

Compounding rate implied by a least-squares line through log prices.

unit `percent` · better when `higher` · also known as `linear_regression_slope`

Fits a straight line to the logarithm of the close over n bars and reports its slope as an annual rate. Running the regression on log prices rather than prices is what makes the slope a growth rate instead of a currency amount, and therefore comparable across a universe. Annualising compounds the daily rate; multiplying it by the number of trading days is the common shortcut and overstates any slope worth noticing.

```latex
y_i = \ln C_{t-n+1+i}, \qquad i = 0 \dots n-1
```

```latex
b = \frac{\sum_i (i - \bar{\imath})(y_i - \bar{y})}{\sum_i (i - \bar{\imath})^2}
```

```latex
g = \left( e^{b \cdot T} - 1 \right) \cdot 100
```
T is trading days per year. Compounding, not multiplication.

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `90` | int | Number of bars the line is fitted through. |
| `trading_days` | `250` | int | Annualisation factor. |

Consumes: `close`

Implemented by `factorbase.factors.trend:regression_slope_annualised`

Reference: Clenow, A. (2015). Stocks on the Move, ch. 6.

#### `trend_stability` - Trend Stability

Coefficient of determination of the log-price regression, 0 to 1.

unit `ratio` · better when `higher` · range 0 to 1 · also known as `r_squared`

How well a straight line describes the last n bars. Near 1 the instrument has moved in something close to a straight line in log space; near 0 it has gone nowhere in particular. It says nothing about direction or speed: a steady decline scores as high as a steady advance.

```latex
R^2 = 1 - \frac{\sum_i \left( y_i - \hat{y}_i \right)^2}{\sum_i \left( y_i - \bar{y} \right)^2}
```
y is the log close, y-hat the fitted line.

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `90` | int | Number of bars the line is fitted through. |

Consumes: `close`

Implemented by `factorbase.factors.trend:trend_stability`

Reference: Clenow, A. (2015). Stocks on the Move, ch. 6.

#### `adjusted_slope` - Adjusted Slope

Annualised regression slope multiplied by its coefficient of determination.

unit `percent` · better when `higher`

Combines how fast with how steadily. Between two instruments whose fitted slopes are equal, the one whose path hugged the line ranks ahead. That is the intended effect and it holds: noise around a given slope lowers R squared and so lowers the product. What it does not do is penalise a single large jump, and the arithmetic says so plainly. Over a 90-bar window, an even climb of 80 percent fits a line with slope 0.00660 and R squared 1.00, giving 0.00660. The same 80 percent arriving as one step in the middle of the window fits a steeper line, slope 0.00980, with R squared 0.75, giving 0.00735. The step ranks ahead. Anyone reaching for this factor to screen out gap risk is reaching for the wrong one.

```latex
AS_t = g_t \cdot R^2_t
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `90` | int | Number of bars the line is fitted through. |
| `trading_days` | `250` | int | Annualisation factor. |

Consumes: `close`

Implemented by `factorbase.factors.trend:adjusted_slope`

**Note.** A step inside the window raises the fitted slope by more than the fall in R squared takes away. Use a gap or range filter for that, not this.

Reference: Clenow, A. (2015). Stocks on the Move, ch. 6.

#### `trend_template_score` - Trend Template Score

How many of the seven price conditions of the trend template hold, 0 to 7.

unit `count` · better when `higher` · range 0 to 7

A count rather than a verdict. The template is usually applied as a gate, all conditions or nothing, which throws away the difference between an instrument failing one condition and one failing five. Scoring it keeps that difference and makes the template rankable. The published template has an eighth condition, on relative strength against the wider market. It is not counted here because it needs a universe rather than a price series; the factor that supplies it lives in the relative-strength family. The score is undefined until every average in it exists, which takes a year of history. Treating an undefined condition as failed would report a low score for an instrument that has merely not traded long enough, and that reading is indistinguishable from a genuine one.

```latex
c_1 = C_t > SMA_t(150) \;\wedge\; C_t > SMA_t(200)
```

```latex
c_2 = SMA_t(150) > SMA_t(200)
```

```latex
c_3 = SMA_t(200) > SMA_{t-m}(200)
```
m defaults to 22 bars, about one month.

```latex
c_4 = SMA_t(50) > SMA_t(150) \;\wedge\; SMA_t(50) > SMA_t(200)
```

```latex
c_5 = C_t > SMA_t(50)
```

```latex
c_6 = C_t \ge LL_t(52w) \cdot \left(1 + \frac{p_{low}}{100}\right)
```

```latex
c_7 = C_t \ge HH_t(52w) \cdot \left(1 - \frac{p_{high}}{100}\right)
```

```latex
Score_t = \sum_{k=1}^{7} \mathbb{1}[c_k]
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `low_margin` | `25.0` | float | How far above the low the close must sit, in percent. |
| `high_margin` | `25.0` | float | How far below the high the close may sit, in percent. |
| `ma200_rising_days` | `22` | int | Over how many bars the 200-day average must have risen. |
| `weeks` | `52` | int | Length of the high and low window, in weeks of five bars. |

Consumes: `close`

Implemented by `factorbase.factors.trend:trend_template_score`

Reference: Minervini, M. (2013). Trade Like a Stock Market Wizard, ch. 5.

#### `random_trade_win_rate` - Random Trade Win Rate

Share of all buy-day and sell-day pairs in the window that ended up.

unit `percent` · better when `higher` · range 0 to 100

Every bar in the window is treated as a possible purchase and every later bar as the sale. Over 260 bars that is 33,670 pairs, and the reading is the percentage of them that closed higher than they opened. It asks what a buyer with no timing skill would have found, which is a property of the price path rather than of any rule applied to it. A high reading does not mean the instrument rose, and this is the part worth understanding before ranking on it. A series that doubles in a single gap and drifts sideways either side of it scores far below one that climbs steadily to the same level, because most pairs in the first case both start and end on the same plateau. The measure is how reliably time in the position paid, not how much it paid. `hold_days` restricts the pairs to a fixed holding period, so 10 asks what a buyer who always sold ten bars later would have found. At 0 every pair counts.

```latex
P_t = \left\{ (i, j) : t - n < i < j \le t \right\}, \qquad |P_t| = \frac{n(n-1)}{2}
```

```latex
W_t = \frac{\left| \{ (i,j) \in P_t : C_j > C_i \} \right|}{|P_t|} \cdot 100
```

```latex
W^{h}_t = \frac{\left| \{ i : t - n < i \le t - h,\; C_{i+h} > C_i \} \right|}{n - h} \cdot 100
```
The fixed-holding form, used when hold_days is above zero.

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `260` | int | Length of the window, in bars. |
| `hold_days` | `0` | int | Count only pairs this many bars apart. 0 counts every pair, which is the usual form. |

Consumes: `close`

Implemented by `factorbase.factors.trend:random_trade_win_rate`

**Note.** Compares every pair in the window, so the cost grows with the square of `periods`. About 20 ms per thousand bars at the default, which is the most expensive entry in this catalogue by an order of magnitude.

Reference: Bachelier, L. (1900). Theorie de la speculation. Annales scientifiques de l'Ecole Normale Superieure 17.

### Volatility

#### `true_range` - True Range

The bar's range, extended to cover any gap from the previous close.

unit `currency` · better when `undefined` · range 0 to None

The plain high-low range misses movement that happened while the market was shut. Wilder's fix is to take the widest of three spans, two of which reach back to yesterday's close. On the first bar there is no previous close, so the plain range is used; discarding that bar instead would shift every subsequent average by one observation.

```latex
TR_t = \max\left( H_t - L_t,\; \left| H_t - C_{t-1} \right|,\; \left| L_t - C_{t-1} \right| \right)
```

Consumes: `high`, `low`, `close`

Implemented by `factorbase.factors.volatility:true_range`

Reference: Wilder, J. W. (1978). New Concepts in Technical Trading Systems, ch. 3.

#### `atr` - Average True Range

True range, smoothed with Wilder's constant.

unit `currency` · better when `undefined` · range 0 to None · also known as `average_true_range`

How far the instrument typically travels in a bar, gaps included. Used for position sizing and stop distance far more than as a signal, because it has no direction: a violent fall and a violent rally read the same. The smoothing constant is 1/n, not 2/(n+1). An ATR(14) built on an ordinary 14-period exponential average is a faster series than Wilder's, and the two are frequently compared as though they were the same.

```latex
ATR_t = \frac{(n-1) \, ATR_{t-1} + TR_t}{n}
```
Seeded with the simple mean of the first n true ranges.

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `14` | int | Length of the smoothing window. |

Consumes: `high`, `low`, `close`

Implemented by `factorbase.factors.volatility:atr`

Reference: Wilder, J. W. (1978). New Concepts in Technical Trading Systems, ch. 3.

#### `atr_percent` - Average True Range, Relative

ATR as a percentage of the close.

unit `percent` · better when `undefined` · range 0 to None

The same measure divided by the price, which is what makes it comparable across a universe. A two-euro average range is wide for a ten-euro stock and negligible for a thousand-euro one; ranking on raw ATR ranks by price level, not by volatility.

```latex
ATR\%_t = \frac{ATR_t(n)}{C_t} \cdot 100
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `14` | int | Length of the smoothing window. |

Consumes: `high`, `low`, `close`

Implemented by `factorbase.factors.volatility:atr_percent`

Reference: Wilder, J. W. (1978). New Concepts in Technical Trading Systems, ch. 3.

#### `historical_volatility` - Historical Volatility (Daily)

Annualised standard deviation of daily logarithmic returns.

unit `percent` · better when `undefined` · range 0 to None · also known as `volatility_daily`

The textbook volatility figure, and the one an option model expects. Logarithmic returns rather than simple ones, because they add across time, which is the assumption behind annualising with the square root of the number of periods. The sample standard deviation is used, dividing by n-1.

```latex
r_t = \ln \frac{C_t}{C_{t-1}}
```

```latex
\sigma_t = \sqrt{ \frac{1}{n-1} \sum_{i=0}^{n-1} \left( r_{t-i} - \bar{r} \right)^2 }
```

```latex
\sigma^{ann}_t = \sigma_t \sqrt{T} \cdot 100
```
T is the number of trading periods in a year.

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `250` | int | Number of daily returns in the window. |
| `trading_days` | `250` | int | Annualisation factor. |

Consumes: `close`

Implemented by `factorbase.factors.volatility:historical_volatility`

Reference: Hull, J. C. (2018). Options, Futures, and Other Derivatives, 10th ed., ch. 15.

#### `historical_volatility_weekly` - Historical Volatility (Weekly)

Annualised standard deviation of weekly logarithmic returns.

unit `percent` · better when `undefined` · range 0 to None · also known as `volatility_weekly`

Sampled Friday to Friday and annualised over 52 periods. Not a smoothed version of the daily figure: it is blind to everything inside the week, so an instrument that swings hard mid-week and closes each Friday near the last one reads calm here and volatile daily. Both are in the catalogue for that reason rather than as one entry with a switch.

```latex
r^{w}_k = \ln \frac{C^{Fri}_k}{C^{Fri}_{k-1}}
```

```latex
\sigma^{ann}_t = \sqrt{ \frac{1}{n-1} \sum_{i=0}^{n-1} \left( r^{w}_{k-i} - \bar{r}^{w} \right)^2 } \cdot \sqrt{52} \cdot 100
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `52` | int | Number of weekly returns in the window. |
| `weeks_per_year` | `52` | int | Annualisation factor. |

Consumes: `close`

Implemented by `factorbase.factors.volatility:historical_volatility_weekly`

**Note.** The weekly series is carried forward onto daily bars so it can be joined to daily factors. A reading therefore repeats within a week and changes only after a Friday close. The only entry in this catalogue that requires the frame to be indexed by date. Everything else works on any index. Given another one it raises UnsupportedIndexError naming itself, rather than letting the resampler complain about an index without saying which factor wanted it.

Reference: Hull, J. C. (2018). Options, Futures, and Other Derivatives, 10th ed., ch. 15.

#### `average_drawdown` - Average Drawdown

Mean distance below the running peak over the window, in percent.

unit `percent` · better when `higher` · range None to 0

Not the maximum drawdown. The maximum is one bad day out of the whole window; the mean says how far underwater the instrument sat on an average day, which is the quantity a holder actually experiences. Two instruments with the same worst fall can differ by a factor of three here.

```latex
P_t = \max_{0 \le i < n} C_{t-i}
```
The running peak inside the window.

```latex
DD_t = \left( \frac{C_t}{P_t} - 1 \right) \cdot 100
```

```latex
\overline{DD}_t = \frac{1}{n} \sum_{i=0}^{n-1} DD_{t-i}
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `250` | int | Length of the window. |

Consumes: `close`

Implemented by `factorbase.factors.volatility:average_drawdown`

Reference: Bacon, C. R. (2008). Practical Portfolio Performance Measurement and Attribution, 2nd ed., ch. 4.

#### `max_drawdown` - Maximum Drawdown

Worst peak-to-trough fall inside the window, in percent.

unit `percent` · better when `higher` · range None to 0

The single worst stretch in the window, as a negative number. It is a minimum over a path, not an average, so it does not shrink when the rest of the window is calm, and one bad week fixes the reading for as long as it stays in the window.

```latex
MDD_t = \min_{0 \le j < n} \left( \frac{C_{t-j}}{\max_{j \le i < n} C_{t-i}} - 1 \right) \cdot 100
```
The inner maximum runs over the bars at or before the bar being measured.

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `250` | int | Length of the window. |

Consumes: `close`

Implemented by `factorbase.factors.volatility:max_drawdown`

Reference: Bacon, C. R. (2008). Practical Portfolio Performance Measurement and Attribution, 2nd ed., ch. 4.

#### `trading_range` - Trading Range

Highest high to lowest low over the window, as a percentage of the low.

unit `percent` · better when `undefined` · range 0 to None

A compression measure. A narrow reading says the instrument has gone nowhere for n bars, which is the precondition every breakout method looks for and the state in which a breakout is worth noticing. Unlike ATR it ignores the path: a straight line from low to high and a series of violent reversals between the same two prices read identically.

```latex
TR^{\%}_t = \frac{HH_t(n) - LL_t(n)}{LL_t(n)} \cdot 100
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `20` | int | Length of the window. |

Consumes: `high`, `low`

Implemented by `factorbase.factors.volatility:trading_range`

Reference: Kirkpatrick, C. D. and Dahlquist, J. R. (2010). Technical Analysis, 2nd ed., ch. 12.

#### `bollinger_percent_b` - Percent B

Where the close sits between the Bollinger bands. 0 at the lower, 1 at the upper.

unit `ratio` · better when `undefined` · also known as `percent_b`

Turns the bands into a number. Readings outside 0 to 1 are normal and informative rather than errors: they say the close is beyond the band, which in a trend is where it spends much of its time. The band spread uses the population standard deviation, dividing by n. Bollinger specified it that way and charting packages draw it that way; the sample deviation widens the bands slightly and is a standing source of two implementations disagreeing in the third decimal.

```latex
M_t = SMA_t(C, n), \qquad s_t = \sqrt{ \frac{1}{n} \sum_{i=0}^{n-1} \left( C_{t-i} - M_t \right)^2 }
```

```latex
U_t = M_t + k s_t, \qquad L_t = M_t - k s_t
```

```latex
\%B_t = \frac{C_t - L_t}{U_t - L_t}
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `20` | int | Length of the window for the average and the deviation. |
| `deviations` | `2.0` | float | How many standard deviations the bands sit from the middle. |

Consumes: `close`

Implemented by `factorbase.factors.volatility:bollinger_percent_b`

Reference: Bollinger, J. (2001). Bollinger on Bollinger Bands, ch. 6.

#### `bollinger_band_width` - Bollinger Band Width

Distance between the bands as a percentage of the middle band.

unit `percent` · better when `undefined` · range 0 to None · also known as `bollinger_width`

The measure behind the squeeze: band width at a multi-month low says volatility has contracted, which historically precedes expansion more often than continued quiet. It says nothing about the direction of the expansion, and reading it as bullish is the standard misuse.

```latex
BW_t = \frac{U_t - L_t}{M_t} \cdot 100
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `20` | int | Length of the window. |
| `deviations` | `2.0` | float | How many standard deviations the bands sit from the middle. |

Consumes: `close`

Implemented by `factorbase.factors.volatility:bollinger_band_width`

Reference: Bollinger, J. (2001). Bollinger on Bollinger Bands, ch. 7.

#### `distance_to_upper_band` - Distance to Upper Bollinger Band

Gap from the close up to the upper band, in percent of the close.

unit `percent` · better when `undefined`

How much room is left before the close reaches the upper band. Negative once the close is above it. Expressed against the close rather than against the band so that the reading answers the question a position holder asks: how far can this move before it is extended.

```latex
D^{up}_t = \frac{U_t - C_t}{C_t} \cdot 100
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `20` | int | Length of the window. |
| `deviations` | `2.0` | float | How many standard deviations the bands sit from the middle. |

Consumes: `close`

Implemented by `factorbase.factors.volatility:distance_to_upper_band`

Reference: Bollinger, J. (2001). Bollinger on Bollinger Bands, ch. 6.

#### `distance_to_lower_band` - Distance to Lower Bollinger Band

Gap from the close down to the lower band, in percent of the close.

unit `percent` · better when `undefined`

The mirror of the previous entry. Negative once the close is below the lower band.

```latex
D^{low}_t = \frac{C_t - L_t}{C_t} \cdot 100
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `20` | int | Length of the window. |
| `deviations` | `2.0` | float | How many standard deviations the bands sit from the middle. |

Consumes: `close`

Implemented by `factorbase.factors.volatility:distance_to_lower_band`

Reference: Bollinger, J. (2001). Bollinger on Bollinger Bands, ch. 6.

### Volume

#### `close_location_value` - Close Location Value

Where the close finished inside its own bar, from -1 at the low to +1 at the high.

unit `ratio` · better when `higher` · range -1 to 1

The building block the accumulation line is made of. It asks a narrow question: given everywhere the price went today, where did it stop. A bar with no range has no location to report and reads zero, which is no information rather than infinite information.

```latex
CLV_t = \frac{(C_t - L_t) - (H_t - C_t)}{H_t - L_t}
```

Consumes: `high`, `low`, `close`

Implemented by `factorbase.factors.volume:close_location_value`

Reference: Chaikin, M., in Kirkpatrick, C. D. and Dahlquist, J. R. (2010). Technical Analysis, 2nd ed., ch. 16.

#### `accumulation_distribution_line` - Accumulation/Distribution Line

Running total of volume signed by where the close sat in its bar.

unit `count` · better when `higher` · also known as `adl`

Adds up each bar's volume, multiplied by how high in its range the bar closed. The reading is a cumulative sum from the first bar of whatever history was loaded, so its level is arbitrary and only its direction means anything. Two instruments cannot be compared on it, and neither can the same instrument loaded over two different windows.

```latex
ADL_t = ADL_{t-1} + CLV_t \cdot V_t
```

Consumes: `high`, `low`, `close`, `volume`

Implemented by `factorbase.factors.volume:accumulation_distribution_line`

**Note.** Level depends on where the loaded history starts. Rank on the Chaikin oscillator instead, which differences the level away.

Reference: Chaikin, M., in Kirkpatrick, C. D. and Dahlquist, J. R. (2010). Technical Analysis, 2nd ed., ch. 16.

#### `chaikin_oscillator` - Chaikin Oscillator

Fast minus slow exponential average of the accumulation line.

unit `count` · better when `higher`

Differencing two averages of the accumulation line removes the arbitrary starting level the line carries, which is what makes this comparable across instruments where the line itself is not. What remains is whether accumulation has been speeding up or slowing down.

```latex
CO_t = EMA_t(ADL, n_{fast}) - EMA_t(ADL, n_{slow})
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `fast_periods` | `3` | int | Period of the faster average. |
| `slow_periods` | `10` | int | Period of the slower average. |

Consumes: `high`, `low`, `close`, `volume`

Implemented by `factorbase.factors.volume:chaikin_oscillator`

Reference: Chaikin, M., in Kirkpatrick, C. D. and Dahlquist, J. R. (2010). Technical Analysis, 2nd ed., ch. 16.

#### `money_flow_index` - Money Flow Index

RSI on the typical price, with each bar weighted by the money traded.

unit `index` · better when `undefined` · range 0 to 100 · also known as `mfi`

Shaped like the RSI and weighted differently, and the difference is larger than the usual one-line description admits. The RSI weights each bar by how far the price moved. This weights it by the money that changed hands, which is a level, and the size of the move never enters at all - only its sign. Two up bars with the same turnover contribute equally whether the price rose by a tick or by half. The consequence is worth stating plainly: on constant volume the reading reduces to the share of summed price levels standing on up bars, which is close to a count of up days and nothing like an RSI. It earns its keep where volume actually varies, and says little where it does not. Two bars count on neither side: one whose typical price is unchanged, and the first bar of the frame, which has no predecessor. Implementations that test only for "not rising" lump both into the negative side and read low on thin instruments.

```latex
MF_t = TP_t \cdot V_t
```

```latex
MF^{+}_t = \sum_{i=0}^{n-1} MF_{t-i} \cdot \mathbb{1}[TP_{t-i} > TP_{t-i-1}]
```

```latex
MF^{-}_t = \sum_{i=0}^{n-1} MF_{t-i} \cdot \mathbb{1}[TP_{t-i} < TP_{t-i-1}]
```

```latex
MFI_t = 100 \cdot \frac{MF^{+}_t}{MF^{+}_t + MF^{-}_t}
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `14` | int | Length of the window. |

Consumes: `high`, `low`, `close`, `volume`

Implemented by `factorbase.factors.volume:money_flow_index`

Reference: Quong, G. and Soudack, A. (1989). Volume-Weighted RSI. Technical Analysis of Stocks and Commodities 7(3).

#### `average_turnover` - Average Turnover

Mean of close times volume over the window, in currency.

unit `currency` · better when `higher` · range 0 to None

The figure a liquidity filter should use. A share count means nothing across instruments: a million shares of a one-euro stock and a million of a five-hundred-euro one are different markets by three orders of magnitude. Multiplying by price makes the comparison valid.

```latex
T_t = \frac{1}{n} \sum_{i=0}^{n-1} C_{t-i} \cdot V_{t-i}
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `20` | int | Length of the window. |

Consumes: `close`, `volume`

Implemented by `factorbase.factors.volume:average_turnover`

Reference: Kirkpatrick, C. D. and Dahlquist, J. R. (2010). Technical Analysis, 2nd ed., ch. 16.

#### `relative_volume` - Relative Volume

Today's volume as a multiple of its own recent average.

unit `ratio` · better when `higher` · range 0 to None · also known as `volume_spike`

A reading of 3 says today traded three times the usual. The average excludes the current bar on purpose: including it lets the spike dampen its own measurement, by up to a twentieth of its size at the default window, which is exactly the wrong direction for a factor whose job is to find spikes.

```latex
RV_t = \frac{V_t}{\frac{1}{n} \sum_{i=1}^{n} V_{t-i}}
```
The sum starts at i=1, so the current bar is not in its own average.

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `20` | int | Length of the comparison window. |

Consumes: `volume`

Implemented by `factorbase.factors.volume:relative_volume`

Reference: Kirkpatrick, C. D. and Dahlquist, J. R. (2010). Technical Analysis, 2nd ed., ch. 16.

#### `volume_trend` - Volume Trend

Percentage change in average volume over the lookback.

unit `percent` · better when `higher`

Whether participation is growing or draining away, measured on the average rather than on single bars so that one heavy session does not define it. A trend advancing on shrinking volume is the classic divergence, and this is the number that states it.

```latex
VT_t = \frac{\overline{V}_t(n) - \overline{V}_{t-m}(n)}{\overline{V}_{t-m}(n)} \cdot 100
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `20` | int | Window of the volume average. |
| `lookback` | `20` | int | How many bars back the comparison point sits. |

Consumes: `volume`

Implemented by `factorbase.factors.volume:volume_trend`

Reference: Kirkpatrick, C. D. and Dahlquist, J. R. (2010). Technical Analysis, 2nd ed., ch. 16.

#### `average_volume` - Average Volume

Mean volume over the window, in shares.

unit `count` · better when `higher` · range 0 to None

In shares, not in currency. The turnover entry above argues that a share count cannot be compared across instruments, and that argument stands: a million shares of a one-euro stock and a million of a five-hundred-euro one are different markets by three orders of magnitude. What a share count can do is be compared against the same instrument's own past, which is what a volume filter on a single name actually needs, and it is the figure an exchange reports. Both are here because a screen ranking a universe wants the first and a rule watching one name wants the second.

```latex
\overline{V}_t = \frac{1}{n} \sum_{i=0}^{n-1} V_{t-i}
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `20` | int | Length of the window. |

Consumes: `volume`

Implemented by `factorbase.factors.volume:average_volume`

Reference: Kirkpatrick, C. D. and Dahlquist, J. R. (2010). Technical Analysis, 2nd ed., ch. 16.

## Signals

A boolean per bar, from price and volume history.

### Breakout

#### `new_high` - New High

The close is the highest of the last n bars, and was not yesterday.

unit `boolean` · better when `higher`

The second clause is what makes it an event rather than a state. Without it, a stock in a steady advance reports a new high on most bars, and a backtest reading that as an entry is in the position permanently.

```latex
High_t = \left( C_t \ge \max_{0 \le i < n} C_{t-i} \right) \wedge \neg \left( C_{t-1} \ge \max_{0 \le i < n} C_{t-1-i} \right)
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `250` | int | Length of the lookback window. |

Consumes: `close`

Implemented by `factorbase.factors.signals:new_high`

Reference: O'Neil, W. J. (2009). How to Make Money in Stocks, 4th ed., ch. 3.

#### `new_low` - New Low

The close is the lowest of the last n bars, and was not yesterday.

unit `boolean` · better when `lower`

The mirror of the previous entry.

```latex
Low_t = \left( C_t \le \min_{0 \le i < n} C_{t-i} \right) \wedge \neg \left( C_{t-1} \le \min_{0 \le i < n} C_{t-1-i} \right)
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `250` | int | Length of the lookback window. |

Consumes: `close`

Implemented by `factorbase.factors.signals:new_low`

Reference: O'Neil, W. J. (2009). How to Make Money in Stocks, 4th ed., ch. 3.

#### `gap_up` - Gap Up

Opened above the previous bar's high by at least the stated margin.

unit `boolean` · better when `higher`

Measured open against previous high, not open against previous close. An open above the previous close but inside its range is not a gap: the price traded there yesterday, and there is no untraded space to fill.

```latex
Gap_t = O_t > H_{t-1} \cdot \left( 1 + \frac{g}{100} \right)
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `minimum_percent` | `1.0` | float | How far above the previous high the open must be, in percent. |

Consumes: `open`, `high`

Implemented by `factorbase.factors.signals:gap_up`

Reference: Bulkowski, T. N. (2005). Encyclopedia of Chart Patterns, 2nd ed., ch. 21.

#### `gap_down` - Gap Down

Opened below the previous bar's low by at least the stated margin.

unit `boolean` · better when `lower`

The mirror of the gap up, measured against the previous low for the same reason.

```latex
Gap_t = O_t < L_{t-1} \cdot \left( 1 - \frac{g}{100} \right)
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `minimum_percent` | `1.0` | float | How far below the previous low the open must be, in percent. |

Consumes: `open`, `low`

Implemented by `factorbase.factors.signals:gap_down`

Reference: Bulkowski, T. N. (2005). Encyclopedia of Chart Patterns, 2nd ed., ch. 21.

#### `expansion_breakout` - Range Expansion Breakout

Closed above the n-bar high on a bar wider than usual.

unit `boolean` · better when `higher`

The width requirement is the filter and the only reason to prefer this over a plain new high. A close a tick above a prior high on a narrow bar is noise; the same close on a bar one and a half times the average true range is a different event.

```latex
Wide_t = \left( H_t - L_t \right) \ge k \cdot ATR_t(m)
```

```latex
Breakout_t = \left( C_t > \max_{1 \le i \le n} H_{t-i} \right) \wedge Wide_t
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `20` | int | Length of the prior-high window. |
| `atr_periods` | `14` | int | Window of the average true range. |
| `range_multiple` | `1.5` | float | How many average true ranges wide the bar must be. |

Consumes: `high`, `low`, `close`

Implemented by `factorbase.factors.signals:expansion_breakout`

Reference: Crabel, T. (1990). Day Trading with Short Term Price Patterns and Opening Range Breakout.

#### `expansion_breakdown` - Range Expansion Breakdown

Closed below the n-bar low on a bar wider than usual.

unit `boolean` · better when `lower`

The mirror of the breakout, with the same width filter.

```latex
Breakdown_t = \left( C_t < \min_{1 \le i \le n} L_{t-i} \right) \wedge Wide_t
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `20` | int | Length of the prior-low window. |
| `atr_periods` | `14` | int | Window of the average true range. |
| `range_multiple` | `1.5` | float | How many average true ranges wide the bar must be. |

Consumes: `high`, `low`, `close`

Implemented by `factorbase.factors.signals:expansion_breakdown`

Reference: Crabel, T. (1990). Day Trading with Short Term Price Patterns and Opening Range Breakout.

#### `darvas_breakout` - Darvas Box Breakout

Closed out of a box the price had actually been confined to.

unit `boolean` · better when `higher`

The box test is the substance. Requiring only a close above an n-bar high admits the last bar of a vertical advance, where there was no box at all. Here the window's high and low must sit within a stated percentage of each other first, which is what "the price went nowhere" means in a number. The box is taken as a fixed-length window rather than by Darvas's own rule, which grows the box until a new high and a new low have both held. The fixed window is cruder, reproducible and stated; the entry does not pretend it is the original.

```latex
BoxHigh_t = \max_{1 \le i \le n} H_{t-i}, \qquad BoxLow_t = \min_{1 \le i \le n} L_{t-i}
```

```latex
IsBox_t = \frac{BoxHigh_t - BoxLow_t}{BoxLow_t} \cdot 100 \le \beta
```

```latex
Breakout_t = \left( C_t > BoxHigh_t \right) \wedge IsBox_t
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `20` | int | Length of the box window. |
| `box_tolerance` | `3.0` | float | How wide the box may be, in percent, and still count as a box. |

Consumes: `high`, `low`, `close`

Implemented by `factorbase.factors.signals:darvas_breakout`

Reference: Darvas, N. (1960). How I Made $2,000,000 in the Stock Market.

#### `pivot_breakout` - Pivot Breakout

Closed above the most recent already-confirmed pivot high.

unit `boolean` · better when `higher`

Uses only pivots that had been confirmed by the time the bar closed, so the level it breaks is `right` bars stale by construction. That staleness is the price of not reading ahead, and it is the whole difference between this entry and `pivot_high`.

```latex
Level_t = H_{s}, \quad s = \max\left\{ u \le t - r : Pivot_u \right\}
```

```latex
Breakout_t = \left( C_t > Level_t \right) \wedge \left( C_{t-1} \le Level_{t-1} \right)
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `left` | `5` | int | How many bars before the pivot must be lower. |
| `right` | `5` | int | How many bars after must be lower, and the confirmation lag. |

Consumes: `high`, `close`

Implemented by `factorbase.factors.signals:pivot_breakout`

Reference: Livermore, J. (1940). How to Trade in Stocks, ch. 5.

#### `gilligans_island_buy` - Gilligan's Island Buy Setup

Gap down to a new low, then a close back at or above the open.

unit `boolean` · better when `higher`

Two halves, and the pattern is the pair. The open has to be below the prior window's low, so the gap reaches a price nobody traded at in two months. The close has to be at or above that open while still sitting in the lower part of the bar: the day fell away from everyone who sold into the gap and recovered only part of it. A bar that gaps down and keeps falling is not this. A bar that gaps down and closes at its high is a different and far more obvious event, and the closing-position condition is what keeps it out. Two months is 40 bars here. Sources describing this pattern give the window in weeks and do not agree on the number, so it is a parameter with a stated default rather than an implied standard.

```latex
Gap_t = O_t < \min_{1 \le i \le n} L_{t-i}
```

```latex
pos_t = \frac{C_t - L_t}{H_t - L_t}
```

```latex
Buy_t = Gap_t \wedge \left( C_t \ge O_t \right) \wedge \left( pos_t \le p \right)
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `40` | int | Length of the window the gap has to clear, in bars. |
| `close_position` | `0.5` | float | How low in its range the bar must still close. |

Consumes: `open`, `high`, `low`, `close`

Implemented by `factorbase.factors.signals:gilligans_island_buy`

**Note.** Often attributed to Larry Williams. The description this entry is built from is Cooper's.

Reference: Cooper, J. (1996). Hit and Run Trading: The Short-Term Stock Traders' Bible.

#### `gilligans_island_sell` - Gilligan's Island Sell Setup

Gap up to a new high, then a close back at or below the open.

unit `boolean` · better when `lower`

The mirror of the buy setup, with the closing position measured from the top of the bar.

```latex
Gap_t = O_t > \max_{1 \le i \le n} H_{t-i}
```

```latex
Sell_t = Gap_t \wedge \left( C_t \le O_t \right) \wedge \left( pos_t \ge 1 - p \right)
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `40` | int | Length of the window the gap has to clear, in bars. |
| `close_position` | `0.5` | float | How high in its range the bar must still close. |

Consumes: `open`, `high`, `low`, `close`

Implemented by `factorbase.factors.signals:gilligans_island_sell`

Reference: Cooper, J. (1996). Hit and Run Trading: The Short-Term Stock Traders' Bible.

### Candlestick

#### `cs_doji` - Doji

Open and close within a small fraction of the bar's range.

unit `boolean` · better when `undefined`

The session ended where it began after travelling in both directions. Read as indecision, which is a description of the bar rather than a forecast: a doji in a quiet range and a doji at the end of a long advance are the same shape and different information.

```latex
Doji_t = \frac{B_t}{S_t} \le \theta
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `max_body_ratio` | `0.05` | float | Largest body, as a share of the range, that still counts. |

Consumes: `open`, `high`, `low`, `close`

Implemented by `factorbase.factors.candles:doji`

Reference: Nison, S. (2001). Japanese Candlestick Charting Techniques, 2nd ed., ch. 3.

#### `cs_dragonfly_doji` - Dragonfly Doji

A doji whose entire range lies below the open and close.

unit `boolean` · better when `undefined`

Price fell hard through the session and came all the way back to the open. The absence of an upper shadow is what separates it from an ordinary doji and is the whole content of the pattern.

```latex
Dragonfly_t = \left( \frac{B_t}{S_t} \le \theta \right) \wedge \left( \frac{U_t}{S_t} \le \upsilon \right)
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `max_body_ratio` | `0.05` | float | Largest body, as a share of the range, that still counts. |
| `max_upper_ratio` | `0.1` | float | Largest upper shadow, as a share of the range. |

Consumes: `open`, `high`, `low`, `close`

Implemented by `factorbase.factors.candles:dragonfly_doji`

Reference: Nison, S. (2001). Japanese Candlestick Charting Techniques, 2nd ed., ch. 3.

#### `cs_gravestone_doji` - Gravestone Doji

A doji whose entire range lies above the open and close.

unit `boolean` · better when `undefined`

The mirror of the dragonfly. Price ran up through the session and gave it all back by the close.

```latex
Gravestone_t = \left( \frac{B_t}{S_t} \le \theta \right) \wedge \left( \frac{D_t}{S_t} \le \delta \right)
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `max_body_ratio` | `0.05` | float | Largest body, as a share of the range, that still counts. |
| `max_lower_ratio` | `0.1` | float | Largest lower shadow, as a share of the range. |

Consumes: `open`, `high`, `low`, `close`

Implemented by `factorbase.factors.candles:gravestone_doji`

Reference: Nison, S. (2001). Japanese Candlestick Charting Techniques, 2nd ed., ch. 3.

#### `cs_spinning_top` - Spinning Top

Small body with a shadow of its own on both sides.

unit `boolean` · better when `undefined`

Wider than a doji and looser in its requirement, so it fires far more often. At the default thresholds it appears on roughly one bar in five of an ordinary series, which is worth knowing before using it as a filter.

```latex
Top_t = \left( \frac{B_t}{S_t} \le \theta \right) \wedge \left( \frac{U_t}{S_t} \ge \mu \right) \wedge \left( \frac{D_t}{S_t} \ge \mu \right)
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `max_body_ratio` | `0.3` | float | Largest body, as a share of the range. |
| `min_shadow_ratio` | `0.25` | float | Smallest each shadow may be, as a share of the range. |

Consumes: `open`, `high`, `low`, `close`

Implemented by `factorbase.factors.candles:spinning_top`

Reference: Nison, S. (2001). Japanese Candlestick Charting Techniques, 2nd ed., ch. 3.

#### `cs_big_white_candle` - Big White Candle

A long up bar that closed near its high.

unit `boolean` · better when `higher`

Long is measured against this instrument's own recent bodies, not against an absolute size. A two-euro body is long for a utility and nothing for a biotech, and a scanner using a fixed threshold finds only the volatile half of any universe.

```latex
\overline{B}_t = \frac{1}{n} \sum_{i=1}^{n} B_{t-i}
```
The average excludes the current bar, so a long bar is not measured against itself.

```latex
BigWhite_t = \left( C_t > O_t \right) \wedge \left( B_t \ge k \overline{B}_t \right) \wedge \left( \frac{B_t}{S_t} \ge \beta \right)
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `20` | int | Window of the average body length. |
| `multiple` | `1.5` | float | How many average bodies long the bar must be. |
| `min_body_ratio` | `0.6` | float | Smallest share of the range the body may occupy. |

Consumes: `open`, `high`, `low`, `close`

Implemented by `factorbase.factors.candles:big_white_candle`

Reference: Nison, S. (2001). Japanese Candlestick Charting Techniques, 2nd ed., ch. 3.

#### `cs_big_black_candle` - Big Black Candle

A long down bar that closed near its low.

unit `boolean` · better when `lower`

The mirror of the previous entry, with the same relative measure of length.

```latex
BigBlack_t = \left( C_t < O_t \right) \wedge \left( B_t \ge k \overline{B}_t \right) \wedge \left( \frac{B_t}{S_t} \ge \beta \right)
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `20` | int | Window of the average body length. |
| `multiple` | `1.5` | float | How many average bodies long the bar must be. |
| `min_body_ratio` | `0.6` | float | Smallest share of the range the body may occupy. |

Consumes: `open`, `high`, `low`, `close`

Implemented by `factorbase.factors.candles:big_black_candle`

Reference: Nison, S. (2001). Japanese Candlestick Charting Techniques, 2nd ed., ch. 3.

#### `cs_white_marubozu` - White Marubozu

An up bar with effectively no shadows.

unit `boolean` · better when `higher`

Opened at the low, closed at the high, never traded outside the body. On daily data with real tick sizes it is rare; on a series where it fires often, the data is probably synthetic or thinly traded.

```latex
WhiteMarubozu_t = \left( C_t > O_t \right) \wedge \left( \frac{U_t}{S_t} \le \sigma \right) \wedge \left( \frac{D_t}{S_t} \le \sigma \right)
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `max_shadow_ratio` | `0.03` | float | Largest either shadow may be, as a share of the range. |

Consumes: `open`, `high`, `low`, `close`

Implemented by `factorbase.factors.candles:white_marubozu`

Reference: Nison, S. (2001). Japanese Candlestick Charting Techniques, 2nd ed., ch. 3.

#### `cs_black_marubozu` - Black Marubozu

A down bar with effectively no shadows.

unit `boolean` · better when `lower`

The mirror of the white one, and as rare.

```latex
BlackMarubozu_t = \left( C_t < O_t \right) \wedge \left( \frac{U_t}{S_t} \le \sigma \right) \wedge \left( \frac{D_t}{S_t} \le \sigma \right)
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `max_shadow_ratio` | `0.03` | float | Largest either shadow may be, as a share of the range. |

Consumes: `open`, `high`, `low`, `close`

Implemented by `factorbase.factors.candles:black_marubozu`

Reference: Nison, S. (2001). Japanese Candlestick Charting Techniques, 2nd ed., ch. 3.

#### `cs_hammer` - Hammer

Small body at the top of the range with a long lower shadow, after a decline.

unit `boolean` · better when `higher`

The preceding decline is part of the definition and is the part pattern scanners routinely drop. Without it the same shape found mid-advance counts, and that is a different bar carrying different information. The trend test here is a simple one, the close n bars ago against the close before the hammer, which is coarse and stated rather than hidden.

```latex
Hammer_t = \left( \frac{B_t}{S_t} \le \theta \right) \wedge \left( \frac{D_t}{S_t} \ge \delta \right) \wedge \left( \frac{U_t}{S_t} \le \upsilon \right) \wedge \left( C_{t-1} < C_{t-1-m} \right)
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `max_body_ratio` | `0.3` | float | Largest body, as a share of the range. |
| `min_lower_ratio` | `0.5` | float | Smallest lower shadow, as a share of the range. |
| `max_upper_ratio` | `0.15` | float | Largest upper shadow, as a share of the range. |
| `trend_periods` | `10` | int | Over how many bars the preceding decline is measured. |

Consumes: `open`, `high`, `low`, `close`

Implemented by `factorbase.factors.candles:hammer`

Reference: Nison, S. (2001). Japanese Candlestick Charting Techniques, 2nd ed., ch. 4.

#### `cs_shooting_star` - Shooting Star

Small body at the bottom of the range with a long upper shadow, after an advance.

unit `boolean` · better when `lower`

The mirror of the hammer, and it carries the same requirement on what came before it.

```latex
Star_t = \left( \frac{B_t}{S_t} \le \theta \right) \wedge \left( \frac{U_t}{S_t} \ge \upsilon \right) \wedge \left( \frac{D_t}{S_t} \le \delta \right) \wedge \left( C_{t-1} > C_{t-1-m} \right)
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `max_body_ratio` | `0.3` | float | Largest body, as a share of the range. |
| `min_upper_ratio` | `0.5` | float | Smallest upper shadow, as a share of the range. |
| `max_lower_ratio` | `0.15` | float | Largest lower shadow, as a share of the range. |
| `trend_periods` | `10` | int | Over how many bars the preceding advance is measured. |

Consumes: `open`, `high`, `low`, `close`

Implemented by `factorbase.factors.candles:shooting_star`

Reference: Nison, S. (2001). Japanese Candlestick Charting Techniques, 2nd ed., ch. 4.

#### `cs_bullish_belt_hold` - Bullish Belt Hold

Opens at its low and closes well up.

unit `boolean` · better when `higher`

A long up bar with no lower shadow: the low of the session was the first print. Distinguished from a white marubozu only by tolerating an upper shadow.

```latex
BeltHold_t = \left( C_t > O_t \right) \wedge \left( \frac{D_t}{S_t} \le \delta \right) \wedge \left( \frac{B_t}{S_t} \ge \beta \right)
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `max_lower_ratio` | `0.03` | float | Largest lower shadow, as a share of the range. |
| `min_body_ratio` | `0.6` | float | Smallest share of the range the body must occupy. |

Consumes: `open`, `high`, `low`, `close`

Implemented by `factorbase.factors.candles:bullish_belt_hold`

Reference: Nison, S. (2001). Japanese Candlestick Charting Techniques, 2nd ed., ch. 5.

#### `cs_bearish_belt_hold` - Bearish Belt Hold

Opens at its high and closes well down.

unit `boolean` · better when `lower`

The mirror: the high of the session was the first print.

```latex
BeltHold_t = \left( C_t < O_t \right) \wedge \left( \frac{U_t}{S_t} \le \upsilon \right) \wedge \left( \frac{B_t}{S_t} \ge \beta \right)
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `max_upper_ratio` | `0.03` | float | Largest upper shadow, as a share of the range. |
| `min_body_ratio` | `0.6` | float | Smallest share of the range the body must occupy. |

Consumes: `open`, `high`, `low`, `close`

Implemented by `factorbase.factors.candles:bearish_belt_hold`

Reference: Nison, S. (2001). Japanese Candlestick Charting Techniques, 2nd ed., ch. 5.

#### `cs_bullish_engulfing` - Bullish Engulfing

An up bar whose body covers the previous down bar's body.

unit `boolean` · better when `higher`

Body against body. The shadows are deliberately not part of the pattern, which is the point most implementations get wrong by comparing highs and lows instead. A bar that engulfs the previous range but not its body is a different event with a different name.

```latex
top_t = \max(O_t, C_t), \qquad bot_t = \min(O_t, C_t)
```

```latex
Engulf_t = \left( C_t > O_t \right) \wedge \left( C_{t-1} < O_{t-1} \right) \wedge \left( bot_t \le bot_{t-1} \right) \wedge \left( top_t \ge top_{t-1} \right) \wedge \left( B_t > B_{t-1} \right)
```

Consumes: `open`, `high`, `low`, `close`

Implemented by `factorbase.factors.candles:bullish_engulfing`

Reference: Nison, S. (2001). Japanese Candlestick Charting Techniques, 2nd ed., ch. 4.

#### `cs_bearish_engulfing` - Bearish Engulfing

A down bar whose body covers the previous up bar's body.

unit `boolean` · better when `lower`

The mirror, with the same body-against-body rule.

```latex
Engulf_t = \left( C_t < O_t \right) \wedge \left( C_{t-1} > O_{t-1} \right) \wedge \left( bot_t \le bot_{t-1} \right) \wedge \left( top_t \ge top_{t-1} \right) \wedge \left( B_t > B_{t-1} \right)
```

Consumes: `open`, `high`, `low`, `close`

Implemented by `factorbase.factors.candles:bearish_engulfing`

Reference: Nison, S. (2001). Japanese Candlestick Charting Techniques, 2nd ed., ch. 4.

#### `cs_bullish_harami` - Bullish Harami

A small up body contained inside the previous long down body.

unit `boolean` · better when `higher`

The reverse containment of the engulfing pattern: here the earlier bar is the large one. The order matters and the two are routinely confused because both compare two consecutive bodies.

```latex
Harami_t = \left( C_t > O_t \right) \wedge \left( C_{t-1} < O_{t-1} \right) \wedge \left( top_t \le top_{t-1} \right) \wedge \left( bot_t \ge bot_{t-1} \right) \wedge \left( B_t < B_{t-1} \right)
```

Consumes: `open`, `high`, `low`, `close`

Implemented by `factorbase.factors.candles:bullish_harami`

Reference: Nison, S. (2001). Japanese Candlestick Charting Techniques, 2nd ed., ch. 4.

#### `cs_bearish_harami` - Bearish Harami

A small down body contained inside the previous long up body.

unit `boolean` · better when `lower`

The mirror of the bullish harami.

```latex
Harami_t = \left( C_t < O_t \right) \wedge \left( C_{t-1} > O_{t-1} \right) \wedge \left( top_t \le top_{t-1} \right) \wedge \left( bot_t \ge bot_{t-1} \right) \wedge \left( B_t < B_{t-1} \right)
```

Consumes: `open`, `high`, `low`, `close`

Implemented by `factorbase.factors.candles:bearish_harami`

Reference: Nison, S. (2001). Japanese Candlestick Charting Techniques, 2nd ed., ch. 4.

#### `cs_above_the_stomach` - Above the Stomach

An up bar opening and closing above the midpoint of the previous down bar's body.

unit `boolean` · better when `higher`

A weaker cousin of the engulfing pattern: the new bar need only clear the middle of the old body, not all of it. It therefore fires more often, and is worth separating from the engulfing entry rather than folding into it.

```latex
mid_{t-1} = \frac{top_{t-1} + bot_{t-1}}{2}
```

```latex
Above_t = \left( C_t > O_t \right) \wedge \left( C_{t-1} < O_{t-1} \right) \wedge \left( O_t \ge mid_{t-1} \right) \wedge \left( C_t \ge mid_{t-1} \right)
```

Consumes: `open`, `high`, `low`, `close`

Implemented by `factorbase.factors.candles:above_the_stomach`

Reference: Bulkowski, T. N. (2008). Encyclopedia of Candlestick Charts.

#### `cs_below_the_stomach` - Below the Stomach

A down bar opening and closing below the midpoint of the previous up bar's body.

unit `boolean` · better when `lower`

The mirror of the previous entry.

```latex
Below_t = \left( C_t < O_t \right) \wedge \left( C_{t-1} > O_{t-1} \right) \wedge \left( O_t \le mid_{t-1} \right) \wedge \left( C_t \le mid_{t-1} \right)
```

Consumes: `open`, `high`, `low`, `close`

Implemented by `factorbase.factors.candles:below_the_stomach`

Reference: Bulkowski, T. N. (2008). Encyclopedia of Candlestick Charts.

#### `cs_morning_star` - Morning Star

Long down bar, small-bodied bar, then an up bar well into the first body.

unit `boolean` · better when `higher`

The third bar has to close a stated fraction of the way up the first bar's body. Scanners that drop the penetration requirement turn the pattern into "any small bar between two others", and it then fires on several percent of all bars.

```latex
pen_t = \frac{C_t - bot_{t-2}}{top_{t-2} - bot_{t-2}}
```

```latex
Morning_t = \left( C_{t-2} < O_{t-2} \right) \wedge \left( \frac{B_{t-1}}{S_{t-1}} \le \theta \right) \wedge \left( C_t > O_t \right) \wedge \left( pen_t \ge p \right)
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `max_star_body_ratio` | `0.3` | float | Largest body the middle bar may have, as a share of its range. |
| `min_penetration` | `0.5` | float | How far into the first body the third bar must close. |

Consumes: `open`, `high`, `low`, `close`

Implemented by `factorbase.factors.candles:morning_star`

Reference: Nison, S. (2001). Japanese Candlestick Charting Techniques, 2nd ed., ch. 4.

#### `cs_evening_star` - Evening Star

Long up bar, small-bodied bar, then a down bar well into the first body.

unit `boolean` · better when `lower`

The mirror of the morning star, with the same penetration requirement.

```latex
pen_t = \frac{top_{t-2} - C_t}{top_{t-2} - bot_{t-2}}
```

```latex
Evening_t = \left( C_{t-2} > O_{t-2} \right) \wedge \left( \frac{B_{t-1}}{S_{t-1}} \le \theta \right) \wedge \left( C_t < O_t \right) \wedge \left( pen_t \ge p \right)
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `max_star_body_ratio` | `0.3` | float | Largest body the middle bar may have, as a share of its range. |
| `min_penetration` | `0.5` | float | How far into the first body the third bar must close. |

Consumes: `open`, `high`, `low`, `close`

Implemented by `factorbase.factors.candles:evening_star`

Reference: Nison, S. (2001). Japanese Candlestick Charting Techniques, 2nd ed., ch. 4.

#### `cs_three_white_soldiers` - Three White Soldiers

Three long up bars, each closing above the last and opening inside its body.

unit `boolean` · better when `higher`

The opening-inside requirement is what separates the pattern from three consecutive gaps up. Without it, a series of gap openings qualifies, and that is a different formation with a different resolution.

```latex
Soldiers_t = \bigwedge_{j=0}^{2} \left[ \left( C_{t-j} > O_{t-j} \right) \wedge \left( B_{t-j} \ge k \overline{B}_{t-j} \right) \wedge \left( \frac{U_{t-j}}{S_{t-j}} \le \upsilon \right) \right]
```

```latex
\wedge \; \left( C_t > C_{t-1} > C_{t-2} \right) \wedge \bigwedge_{j=0}^{1} \left( bot_{t-j-1} \le O_{t-j} \le top_{t-j-1} \right)
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `20` | int | Window of the average body length. |
| `multiple` | `1.0` | float | How many average bodies long each bar must be. |
| `max_upper_ratio` | `0.25` | float | Largest upper shadow each bar may have. |

Consumes: `open`, `high`, `low`, `close`

Implemented by `factorbase.factors.candles:three_white_soldiers`

Reference: Nison, S. (2001). Japanese Candlestick Charting Techniques, 2nd ed., ch. 6.

#### `cs_three_black_crows` - Three Black Crows

Three long down bars, each closing below the last and opening inside its body.

unit `boolean` · better when `lower`

The mirror of the soldiers, with the same opening-inside requirement and the same reason for it.

```latex
Crows_t = \bigwedge_{j=0}^{2} \left[ \left( C_{t-j} < O_{t-j} \right) \wedge \left( B_{t-j} \ge k \overline{B}_{t-j} \right) \wedge \left( \frac{D_{t-j}}{S_{t-j}} \le \delta \right) \right]
```

```latex
\wedge \; \left( C_t < C_{t-1} < C_{t-2} \right) \wedge \bigwedge_{j=0}^{1} \left( bot_{t-j-1} \le O_{t-j} \le top_{t-j-1} \right)
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `20` | int | Window of the average body length. |
| `multiple` | `1.0` | float | How many average bodies long each bar must be. |
| `max_lower_ratio` | `0.25` | float | Largest lower shadow each bar may have. |

Consumes: `open`, `high`, `low`, `close`

Implemented by `factorbase.factors.candles:three_black_crows`

Reference: Nison, S. (2001). Japanese Candlestick Charting Techniques, 2nd ed., ch. 6.

#### `cs_bullish_popgun` - Bullish Popgun

An inside bar followed by an up bar that engulfs its whole range.

unit `boolean` · better when `higher`

Range against range here, unlike the engulfing patterns, and on purpose: the pattern is about a compressed bar being overrun, and compression is a property of the range, not of the body.

```latex
Inside_{t-1} = \left( H_{t-1} < H_{t-2} \right) \wedge \left( L_{t-1} > L_{t-2} \right)
```

```latex
Popgun_t = Inside_{t-1} \wedge \left( H_t > H_{t-1} \right) \wedge \left( L_t < L_{t-1} \right) \wedge \left( C_t > O_t \right)
```

Consumes: `open`, `high`, `low`, `close`

Implemented by `factorbase.factors.candles:bullish_popgun`

Reference: Bulkowski, T. N. (2008). Encyclopedia of Candlestick Charts.

#### `cs_bearish_popgun` - Bearish Popgun

An inside bar followed by a down bar that engulfs its whole range.

unit `boolean` · better when `lower`

The mirror of the bullish popgun.

```latex
Popgun_t = Inside_{t-1} \wedge \left( H_t > H_{t-1} \right) \wedge \left( L_t < L_{t-1} \right) \wedge \left( C_t < O_t \right)
```

Consumes: `open`, `high`, `low`, `close`

Implemented by `factorbase.factors.candles:bearish_popgun`

Reference: Bulkowski, T. N. (2008). Encyclopedia of Candlestick Charts.

### Crossing

#### `price_crosses_above_ma` - Price Crosses Above Moving Average

The close moved from at or below its moving average to above it.

unit `boolean` · better when `higher`

Fires once, on the bar of the change. The bar before must have closed at or below the average, which is why a series that opens above its average never fires on its first bar.

```latex
Cross_t = \left( C_t > MA_t(n) \right) \wedge \left( C_{t-1} \le MA_{t-1}(n) \right)
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `200` | int | Window of the average. |
| `method` | `'sma'` | str | Which average the close is compared against. One of `sma`, `ema`, `wma`. |

Consumes: `close`

Implemented by `factorbase.factors.signals:price_crosses_above_ma`

Reference: Kirkpatrick, C. D. and Dahlquist, J. R. (2010). Technical Analysis, 2nd ed., ch. 14.

#### `price_crosses_below_ma` - Price Crosses Below Moving Average

The close moved from at or above its moving average to below it.

unit `boolean` · better when `lower`

The mirror of the previous entry.

```latex
Cross_t = \left( C_t < MA_t(n) \right) \wedge \left( C_{t-1} \ge MA_{t-1}(n) \right)
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `200` | int | Window of the average. |
| `method` | `'sma'` | str | Which average the close is compared against. One of `sma`, `ema`, `wma`. |

Consumes: `close`

Implemented by `factorbase.factors.signals:price_crosses_below_ma`

Reference: Kirkpatrick, C. D. and Dahlquist, J. R. (2010). Technical Analysis, 2nd ed., ch. 14.

#### `golden_cross` - Golden Cross

The fast moving average moved above the slow one.

unit `boolean` · better when `higher`

Two averages crossing, not price crossing an average. It fires rarely, a handful of times a decade at the usual 50 and 200, which is worth knowing before building a strategy that assumes a steady stream of entries.

```latex
Golden_t = \left( MA_t(n_f) > MA_t(n_s) \right) \wedge \left( MA_{t-1}(n_f) \le MA_{t-1}(n_s) \right)
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `fast_periods` | `50` | int | Window of the faster average. |
| `slow_periods` | `200` | int | Window of the slower average. |
| `method` | `'sma'` | str | Which average both windows use. One of `sma`, `ema`, `wma`. |

Consumes: `close`

Implemented by `factorbase.factors.signals:golden_cross`

Reference: Kirkpatrick, C. D. and Dahlquist, J. R. (2010). Technical Analysis, 2nd ed., ch. 14.

#### `death_cross` - Death Cross

The fast moving average moved below the slow one.

unit `boolean` · better when `lower`

The mirror of the golden cross, and as rare.

```latex
Death_t = \left( MA_t(n_f) < MA_t(n_s) \right) \wedge \left( MA_{t-1}(n_f) \ge MA_{t-1}(n_s) \right)
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `fast_periods` | `50` | int | Window of the faster average. |
| `slow_periods` | `200` | int | Window of the slower average. |
| `method` | `'sma'` | str | Which average both windows use. One of `sma`, `ema`, `wma`. |

Consumes: `close`

Implemented by `factorbase.factors.signals:death_cross`

Reference: Kirkpatrick, C. D. and Dahlquist, J. R. (2010). Technical Analysis, 2nd ed., ch. 14.

#### `ma_support` - Moving Average Held as Support

Traded down to the average and closed back above it.

unit `boolean` · better when `higher`

Both halves are required and both are often dropped. A bar that merely closes above the average is not a test of support; a bar that closes below it is a break, not a hold. The event is the pair: the low reached the average and the close did not stay there.

```latex
Support_t = \left( L_t \le MA_t(n) \cdot \left(1 + \frac{\tau}{100}\right) \right) \wedge \left( C_t > MA_t(n) \right)
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `50` | int | Window of the average. |
| `method` | `'sma'` | str | Which average acts as the level. One of `sma`, `ema`, `wma`. |
| `tolerance` | `1.0` | float | How close to the average the low must come, in percent. |

Consumes: `low`, `close`

Implemented by `factorbase.factors.signals:ma_support`

Reference: Kirkpatrick, C. D. and Dahlquist, J. R. (2010). Technical Analysis, 2nd ed., ch. 14.

#### `ma_resistance` - Moving Average Held as Resistance

Traded up to the average and closed back below it.

unit `boolean` · better when `lower`

The mirror of the support entry, with the same two-part requirement.

```latex
Resistance_t = \left( H_t \ge MA_t(n) \cdot \left(1 - \frac{\tau}{100}\right) \right) \wedge \left( C_t < MA_t(n) \right)
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `50` | int | Window of the average. |
| `method` | `'sma'` | str | Which average acts as the level. One of `sma`, `ema`, `wma`. |
| `tolerance` | `1.0` | float | How close to the average the high must come, in percent. |

Consumes: `high`, `close`

Implemented by `factorbase.factors.signals:ma_resistance`

Reference: Kirkpatrick, C. D. and Dahlquist, J. R. (2010). Technical Analysis, 2nd ed., ch. 14.

#### `bollinger_support` - Lower Bollinger Band Held

Traded below the lower band and closed back inside it.

unit `boolean` · better when `higher`

A rejection at the band rather than a stay outside it. Closing outside the band is common in a trend and is not this event.

```latex
Support_t = \left( L_t \le L^{band}_t \right) \wedge \left( C_t > L^{band}_t \right)
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `20` | int | Window of the bands. |
| `deviations` | `2.0` | float | Band distance in standard deviations. |

Consumes: `low`, `close`

Implemented by `factorbase.factors.signals:bollinger_support`

Reference: Bollinger, J. (2001). Bollinger on Bollinger Bands, ch. 8.

#### `bollinger_resistance` - Upper Bollinger Band Held

Traded above the upper band and closed back inside it.

unit `boolean` · better when `lower`

The mirror of the support entry.

```latex
Resistance_t = \left( H_t \ge U^{band}_t \right) \wedge \left( C_t < U^{band}_t \right)
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `20` | int | Window of the bands. |
| `deviations` | `2.0` | float | Band distance in standard deviations. |

Consumes: `high`, `close`

Implemented by `factorbase.factors.signals:bollinger_resistance`

Reference: Bollinger, J. (2001). Bollinger on Bollinger Bands, ch. 8.

#### `macd_cross_up` - MACD Crosses Above Signal

The MACD line moved above its signal line.

unit `boolean` · better when `higher`

The crossing itself, not the state of being above. Both lines are in currency, so the size of the gap is not comparable between instruments, but the crossing is.

```latex
Cross_t = \left( MACD_t > Signal_t \right) \wedge \left( MACD_{t-1} \le Signal_{t-1} \right)
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `fast_periods` | `12` | int | Faster exponential average. |
| `slow_periods` | `26` | int | Slower exponential average. |
| `signal_periods` | `9` | int | Average applied to the MACD line. |

Consumes: `close`

Implemented by `factorbase.factors.signals:macd_cross_up`

Reference: Appel, G. (2005). Technical Analysis: Power Tools for Active Investors, ch. 6.

#### `macd_cross_down` - MACD Crosses Below Signal

The MACD line moved below its signal line.

unit `boolean` · better when `lower`

The mirror of the previous entry.

```latex
Cross_t = \left( MACD_t < Signal_t \right) \wedge \left( MACD_{t-1} \ge Signal_{t-1} \right)
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `fast_periods` | `12` | int | Faster exponential average. |
| `slow_periods` | `26` | int | Slower exponential average. |
| `signal_periods` | `9` | int | Average applied to the MACD line. |

Consumes: `close`

Implemented by `factorbase.factors.signals:macd_cross_down`

Reference: Appel, G. (2005). Technical Analysis: Power Tools for Active Investors, ch. 6.

#### `stochastic_cross_up` - Stochastic Crosses Up From Low

Slow %K crossed above %D while both were still below the threshold.

unit `boolean` · better when `higher`

The threshold is the point of the entry. A crossing at 70 is a crossing; a crossing below 20 is the one the method is about. Leaving the threshold out produces several times as many firings, most of them mid-range and meaningless.

```latex
Cross_t = \left( \%K_t > \%D_t \right) \wedge \left( \%K_{t-1} \le \%D_{t-1} \right) \wedge \left( \%D_t < \theta \right)
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `14` | int | Range window of the stochastic. |
| `smoothing` | `3` | int | Smoothing applied at each stage. |
| `threshold` | `20.0` | float | The %D line must be below this for the crossing to count. |

Consumes: `high`, `low`, `close`

Implemented by `factorbase.factors.signals:stochastic_cross_up`

Reference: Lane, G. C. (1984). Lane on Stochastics. Technical Analysis of Stocks and Commodities 2(3).

#### `stochastic_cross_down` - Stochastic Crosses Down From High

Slow %K crossed below %D while both were still above the threshold.

unit `boolean` · better when `lower`

The mirror of the previous entry, with the threshold at the other end.

```latex
Cross_t = \left( \%K_t < \%D_t \right) \wedge \left( \%K_{t-1} \ge \%D_{t-1} \right) \wedge \left( \%D_t > \theta \right)
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `14` | int | Range window of the stochastic. |
| `smoothing` | `3` | int | Smoothing applied at each stage. |
| `threshold` | `80.0` | float | The %D line must be above this for the crossing to count. |

Consumes: `high`, `low`, `close`

Implemented by `factorbase.factors.signals:stochastic_cross_down`

Reference: Lane, G. C. (1984). Lane on Stochastics. Technical Analysis of Stocks and Commodities 2(3).

#### `bollinger_band_outlier_long` - Bollinger Band Outlier, Long

A candle wholly below the lower band, or reaching it on a wide day.

unit `boolean` · better when `higher`

Two ways to qualify. Either the close is below the lower band outright, or the day is wide, high over low above the stated ratio, and its low comes within a tenth of the day's range of the band. The second half is the interesting one: a bar can trade a long way outside the band at its worst and close back inside, and that bar has still been where nothing traded for twenty sessions. The bands here use the sample standard deviation, dividing by n-1. The catalogue's own Bollinger entries use the population one, which is what Bollinger specified and what TTR computes. At twenty periods the sample figure is larger by a factor of sqrt(20/19), so these bands sit about 2.6 percent wider and a candle just outside one of them can be inside the other. `sample_deviation` switches it, and the default follows the rule this entry states rather than the rest of the catalogue.

```latex
s = \sqrt{\frac{1}{n-1} \sum_{i=1}^{n} \left( C_i - \bar{C} \right)^2}, \qquad L^{band} = SMA(C, n) - k s
```

```latex
Outlier_t = \left( C_t < L^{band}_t \right) \;\vee\; \left( \frac{H_t}{L_t} > \rho \;\wedge\; L_t - (H_t - L_t) \, r < L^{band}_t \right)
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `20` | int | Window of the bands. |
| `deviations` | `2.0` | float | Band distance in standard deviations. |
| `minimum_range` | `1.03` | float | How wide the bar must be, as high over low. |
| `reach` | `0.1` | float | How far past the bar's extreme the band may sit, as a share of the range. |
| `sample_deviation` | `True` | bool | Divide by n-1 rather than by n. True follows this entry's own rule; false matches the other Bollinger entries in this catalogue. |

Consumes: `high`, `low`, `close`

Implemented by `factorbase.factors.signals:bollinger_band_outlier_long`

**Note.** The long and short forms are not mirror images, and the asymmetry is in the rule rather than in this implementation. It lives in the second clause, because both forms measure the reach from the bar's LOW. Long asks that the low come down to the lower band, which a bar that merely dips there satisfies while closing well above it. Short asks that the low come up past the upper band, which needs the whole candle above it. A bar that dips to the lower band therefore fires the long form, and its exact mirror image does not fire the short one. The first clause, close against band, is symmetric and does not carry the difference. How often each fires on real data depends on the shape of the bars, so no ratio is quoted here.

Reference: Bollinger, J. (2001). Bollinger on Bollinger Bands, ch. 6.

#### `bollinger_band_outlier_short` - Bollinger Band Outlier, Short

A candle wholly above the upper band, or reaching it on a wide day.

unit `boolean` · better when `lower`

The counterpart of the long form and, as the note on that entry says, not its mirror. The reach condition is measured from the bar's low in both cases, so here it demands that even the low of the bar sits near or above the upper band.

```latex
Outlier_t = \left( C_t > U^{band}_t \right) \;\vee\; \left( \frac{H_t}{L_t} > \rho \;\wedge\; L_t + (H_t - L_t) \, r > U^{band}_t \right)
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `20` | int | Window of the bands. |
| `deviations` | `2.0` | float | Band distance in standard deviations. |
| `minimum_range` | `1.03` | float | How wide the bar must be, as high over low. |
| `reach` | `0.1` | float | How far past the bar's extreme the band may sit, as a share of the range. |
| `sample_deviation` | `True` | bool | Divide by n-1 rather than by n. True follows this entry's own rule; false matches the other Bollinger entries in this catalogue. |

Consumes: `high`, `low`, `close`

Implemented by `factorbase.factors.signals:bollinger_band_outlier_short`

Reference: Bollinger, J. (2001). Bollinger on Bollinger Bands, ch. 6.

#### `holy_grail_pullback` - Holy Grail Pullback

A pullback to the 20-period average inside a strong trend, taken out the next bar.

unit `boolean` · better when `higher`

Raschke's setup, in three parts. The trend has to be strong, which an ADX above 30 stands in for. The previous bar has to have pulled back far enough to touch the exponential average. Today has to take out that bar's extreme, which is the resting stop order the method places rather than a condition on the bar itself. Encoding the entry as "yesterday touched, today broke yesterday's high" is a choice and a strict one. The method waits for a touch and then leaves an order that may fill several bars later; this fires only on the bar immediately after. That makes the signal a function of two bars rather than of an open-ended state, which is what a screen can evaluate, and it will miss fills the method would have taken.

```latex
Trend_t = ADX_t(n) > \theta
```

```latex
Touch_{t-1} = L_{t-1} \le EMA_{t-1}(m)
```

```latex
Grail_t = Trend_t \wedge \left( +DI_t > -DI_t \right) \wedge Touch_{t-1} \wedge \left( H_t > H_{t-1} \right)
```
The short form mirrors every term, including the direction of the DI comparison.

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `adx_periods` | `14` | int | Window of the trend-strength reading. |
| `adx_threshold` | `30.0` | float | How strong the trend must be. |
| `ema_periods` | `20` | int | Window of the exponential average the pullback must reach. |
| `direction` | `'long'` | str | Whether the pullback is into an uptrend or a downtrend. One of `long`, `short`. |

Consumes: `high`, `low`, `close`

Implemented by `factorbase.factors.signals:holy_grail_pullback`

**Note.** Described for intraday charts as often as for daily ones. Nothing here is specific to a bar length, and the ADX threshold of 30 was chosen against daily data.

Reference: Raschke, L. B. and Connors, L. (1995). Street Smarts: High Probability Short-Term Trading Strategies.

### Structure

#### `pivot_high` - Pivot High

A bar whose high exceeds the bars either side of it.

unit `boolean` · better when `undefined`

A local high, confirmed by what came after it. The confirmation is the catch: the value marked True on a bar is not knowable until `right` bars later, so anything reading this Series in a backtest must shift it by `right` or it is reading the future. The entry keeps it in this form, with the warning, rather than shifting it silently. A pivot shifted by default would be right for backtests and wrong for drawing the chart, and a reader would have no way to tell which they had.

```latex
Pivot_t = H_t \ge \max_{-r \le j \le l} H_{t+j}
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `left` | `5` | int | How many bars before must be lower. |
| `right` | `5` | int | How many bars after must be lower. Also the confirmation lag. |

Consumes: `high`

Implemented by `factorbase.factors.signals:pivot_high`

**Note.** Reads `right` bars ahead by construction. Shift by `right` before using it as a trading rule.

Reference: Livermore, J. (1940). How to Trade in Stocks, ch. 5.

#### `pivot_low` - Pivot Low

A bar whose low undercuts the bars either side of it.

unit `boolean` · better when `undefined`

The mirror of the pivot high, and it reads ahead in the same way and to the same extent.

```latex
Pivot_t = L_t \le \min_{-r \le j \le l} L_{t+j}
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `left` | `5` | int | How many bars before must be higher. |
| `right` | `5` | int | How many bars after must be higher. Also the confirmation lag. |

Consumes: `low`

Implemented by `factorbase.factors.signals:pivot_low`

**Note.** Reads `right` bars ahead by construction. Shift by `right` before using it as a trading rule.

Reference: Livermore, J. (1940). How to Trade in Stocks, ch. 5.

### Volume Event

#### `accumulation_day` - Accumulation Day

Up day on above-average volume that closed in the upper part of its range.

unit `boolean` · better when `higher`

The closing position is the part usually left out. A bar that rises on heavy volume and gives most of it back before the close is not accumulation; without the position test it counts as one, and a tally of such days then measures activity rather than demand.

```latex
pos_t = \frac{C_t - L_t}{H_t - L_t}
```

```latex
Accum_t = \left( C_t > C_{t-1} \right) \wedge \left( V_t \ge k \overline{V}_t(n) \right) \wedge \left( pos_t \ge p \right)
```
The volume average excludes the current bar.

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `50` | int | Window of the volume average. |
| `volume_multiple` | `1.0` | float | How many average volumes the bar must trade. |
| `close_position` | `0.6` | float | How high in its range the bar must close. |

Consumes: `high`, `low`, `close`, `volume`

Implemented by `factorbase.factors.signals:accumulation_day`

Reference: O'Neil, W. J. (2009). How to Make Money in Stocks, 4th ed., ch. 3.

#### `distribution_day` - Distribution Day

Down day of at least the stated size on volume above the previous bar's.

unit `boolean` · better when `lower`

Volume against the previous bar, not against an average, which is the convention the term comes from and is deliberately easy to satisfy. Counting distribution days is a tally over weeks; the individual bar is allowed to be a weak signal, and making it a strong one would defeat the count.

```latex
Dist_t = \left( \left( \frac{C_t}{C_{t-1}} - 1 \right) \cdot 100 \le -f \right) \wedge \left( V_t > V_{t-1} \right)
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `minimum_fall` | `0.2` | float | How far the close must fall, in percent. |

Consumes: `close`, `volume`

Implemented by `factorbase.factors.signals:distribution_day`

Reference: O'Neil, W. J. (2009). How to Make Money in Stocks, 4th ed., ch. 9.

#### `volume_peak` - Volume Peak

Volume is the highest of the last n bars, and was not yesterday.

unit `boolean` · better when `undefined`

Same event-not-state construction as the new high. A single heavy day inside a heavy week would otherwise fire on every bar of that week.

```latex
Peak_t = \left( V_t \ge \max_{0 \le i < n} V_{t-i} \right) \wedge \neg \left( V_{t-1} \ge \max_{0 \le i < n} V_{t-1-i} \right)
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `periods` | `250` | int | Length of the lookback window. |

Consumes: `volume`

Implemented by `factorbase.factors.signals:volume_peak`

Reference: Kirkpatrick, C. D. and Dahlquist, J. R. (2010). Technical Analysis, 2nd ed., ch. 16.

#### `buying_climax` - Buying Climax

An extended advance ending in a wide, heavy bar that closed poorly.

unit `boolean` · better when `lower`

Four conditions, all required: the advance happened, the bar is unusually wide, the volume is unusually heavy, and the close gave most of the bar's gain back. The last one is what makes it a climax rather than a strong day, and it is the one most often dropped. At the default thresholds it is rare. On a random walk it never fires, which is the intended behaviour: the pattern describes a specific exhaustion, not a busy session.

```latex
Adv_t = \left( \frac{C_t}{C_{t-n}} - 1 \right) \cdot 100 \ge a
```

```latex
Heavy_t = V_t \ge k_v \overline{V}_t(m), \qquad Wide_t = \left( H_t - L_t \right) \ge k_r ATR_t
```

```latex
Climax_t = Adv_t \wedge Heavy_t \wedge Wide_t \wedge \left( \frac{C_t - L_t}{H_t - L_t} \le p \right)
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `advance_periods` | `50` | int | Window the preceding advance is measured over. |
| `minimum_advance` | `25.0` | float | How far the price must have risen, in percent. |
| `volume_periods` | `50` | int | Window of the volume average. |
| `volume_multiple` | `2.0` | float | How many average volumes the bar must trade. |
| `atr_periods` | `14` | int | Window of the average true range. |
| `range_multiple` | `2.0` | float | How many average true ranges wide the bar must be. |
| `close_position` | `0.4` | float | How low in its range the bar must close. |

Consumes: `high`, `low`, `close`, `volume`

Implemented by `factorbase.factors.signals:buying_climax`

Reference: Wyckoff, R. D., in Pruden, H. (2007). The Three Skills of Top Trading, ch. 3.

#### `selling_climax` - Selling Climax

An extended decline ending in a wide, heavy bar that closed well.

unit `boolean` · better when `higher`

The mirror of the buying climax, with the closing position at the other end of the bar.

```latex
Dec_t = \left( \frac{C_t}{C_{t-n}} - 1 \right) \cdot 100 \le -d
```

```latex
Climax_t = Dec_t \wedge Heavy_t \wedge Wide_t \wedge \left( \frac{C_t - L_t}{H_t - L_t} \ge p \right)
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `decline_periods` | `50` | int | Window the preceding decline is measured over. |
| `minimum_decline` | `25.0` | float | How far the price must have fallen, in percent. |
| `volume_periods` | `50` | int | Window of the volume average. |
| `volume_multiple` | `2.0` | float | How many average volumes the bar must trade. |
| `atr_periods` | `14` | int | Window of the average true range. |
| `range_multiple` | `2.0` | float | How many average true ranges wide the bar must be. |
| `close_position` | `0.6` | float | How high in its range the bar must close. |

Consumes: `high`, `low`, `close`, `volume`

Implemented by `factorbase.factors.signals:selling_climax`

Reference: Wyckoff, R. D., in Pruden, H. (2007). The Three Skills of Top Trading, ch. 3.

#### `capitulation_bar` - Capitulation Bar

Five conditions that together describe a day of forced selling.

unit `boolean` · better when `higher`

All five hold at once: a low below every low of the past quarter, a close in the lower half of the day's range, a fall of at least five percent against the previous close, a price at least a quarter below the quarter's high, and volume at least double the four-week average. Any one of them is ordinary. The combination is not: on a random walk it never fires. That is the intended behaviour and it is worth saying, because a signal that never fires on noise and rarely on data is easy to mistake for a broken one. Two of the three windows include the current bar and one does not. The new low compares against the previous 65 bars only, while the quarter's high and the four-week volume average both include today. The volume one matters: a bar's own volume sits inside the average it is measured against, so a spike damps its own reading by a twenty-first of itself. `relative_volume` in this catalogue excludes the current bar for exactly that reason, and the two therefore disagree by design rather than by oversight.

```latex
c_1 = L_t < \min_{1 \le i \le n} L_{t-i}
```

```latex
c_2 = C_t < \frac{H_t + L_t}{2}
```

```latex
c_3 = \frac{C_t}{C_{t-1}} \le 1 - \frac{f}{100}
```

```latex
c_4 = \frac{C_t}{\max_{0 \le i \le n} H_{t-i}} \le 1 - \frac{d}{100}
```
This window includes the current bar, unlike the one in c1.

```latex
c_5 = \frac{V_t}{\frac{1}{m} \sum_{i=0}^{m-1} V_{t-i}} \ge k
```
This average includes the current bar too.

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `low_periods` | `65` | int | Length of the window the new low has to clear, about a quarter. |
| `minimum_fall` | `5.0` | float | How far the close must fall against the previous one, in percent. |
| `minimum_off_high` | `25.0` | float | How far below the window's high the close must sit, in percent. |
| `volume_periods` | `21` | int | Length of the volume average, about four weeks, current bar included. |
| `volume_multiple` | `2.0` | float | How many average volumes the bar must trade. |

Consumes: `high`, `low`, `close`, `volume`

Implemented by `factorbase.factors.signals:capitulation_bar`

**Note.** Related to `selling_climax` in this catalogue and not the same rule. That one asks for an extended decline and a strong close; this one asks for a new low and a weak close. A bar can satisfy either without the other.

Reference: Wyckoff, R. D., in Pruden, H. (2007). The Three Skills of Top Trading, ch. 3.

## Fundamentals

A number per reporting period, from the reported accounts.

### Distress

#### `ohlson_o_score` - Ohlson O-Score

A nine-term bankruptcy score. Higher means more distressed.

unit `ratio` · better when `lower` · basis `annual`

The coefficients are Ohlson's, fitted on US filings between 1970 and 1976, and they have not been refitted since. Treat the output as an ordering of relative distress inside a comparable universe, not as a calibrated statement about any individual company. The size term divides total assets by a price-index level. The parameter defaults to 1, which leaves assets in nominal currency and makes that term comparable only within one point in time. Supplying a real deflator is the caller's job; the alternative was to bury a constant in the code and let the score drift silently with inflation.

```latex
O_t = -1.32 - 0.407 \ln\!\frac{Assets_t}{d} + 6.03 \frac{Liab_t}{Assets_t} - 1.43 \frac{NWC_t}{Assets_t} + 0.0757 \frac{CL_t}{CA_t}
```

```latex
\quad - 1.72 \, \mathbb{1}[Liab_t > Assets_t] - 2.37 \frac{NI_t}{Assets_t} - 1.83 \frac{OCF_t}{Liab_t}
```

```latex
\quad + 0.285 \, \mathbb{1}[NI_t < 0 \wedge NI_{t-1} < 0] - 0.521 \frac{NI_t - NI_{t-1}}{|NI_t| + |NI_{t-1}|}
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `period` | `'annual'` | str | Which reported rows the factor is computed on. One of `annual`, `quarterly`, `ttm`. |
| `gnp_deflator` | `1.0` | float | Divides total assets in the size term. The default of 1 leaves assets nominal, which is comparable within a date and not across dates. |

Consumes: `total_assets`, `total_liabilities`, `current_assets`, `current_liabilities`, `net_income`, `operating_cash_flow`

Implemented by `factorbase.factors.fundamentals.leverage:ohlson_o_score`

Reference: Ohlson, J. A. (1980). Financial Ratios and the Probabilistic Prediction of Bankruptcy. Journal of Accounting Research 18(1).

#### `ohlson_bankruptcy_probability` - Ohlson Bankruptcy Probability

The O-score put through a logistic function, in percent.

unit `percent` · better when `lower` · basis `annual` · range 0 to 100

Reported because the original paper reports it, and carrying the same warning: the calibration is from a 1970s US sample, so the number is not a probability anyone should act on as one. The logistic transform is monotone, so the ordering is identical to the score's and nothing is gained by ranking on this instead.

```latex
P_t = \frac{1}{1 + e^{-O_t}} \cdot 100
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `period` | `'annual'` | str | Which reported rows the factor is computed on. One of `annual`, `quarterly`, `ttm`. |
| `gnp_deflator` | `1.0` | float | Passed through to the score. |

Consumes: `total_assets`, `total_liabilities`, `current_assets`, `current_liabilities`, `net_income`, `operating_cash_flow`

Implemented by `factorbase.factors.fundamentals.leverage:ohlson_bankruptcy_probability`

Reference: Ohlson, J. A. (1980). Financial Ratios and the Probabilistic Prediction of Bankruptcy. Journal of Accounting Research 18(1).

### Growth

#### `growth` - Growth

Percentage change of a reported line over n periods.

unit `percent` · better when `higher` · basis `ttm`

From a negative base the number is not a growth rate. A loss shrinking from -100 to -50 computes as -50 percent and reads as deterioration when it is an improvement. Those readings are NaN by default, and `allow_negative_base` returns them for callers who handle it themselves. `periods` counts rows of the chosen basis, not months. Four quarterly rows is a year; four annual rows is four years. The same argument means different things under different bases and nothing in the output would reveal the mistake, which is why it is stated here.

```latex
g_t(n) = \left( \frac{X_t}{X_{t-n}} - 1 \right) \cdot 100, \qquad X_{t-n} > 0
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `item` | `'revenue'` | str | Which line of the accounts the growth is measured on. One of `revenue`, `net_income`, `eps`, `ebit`, `ebitda`, `equity`, `operating_cash_flow`, `free_cash_flow`, `dividend`, `research`. |
| `period` | `'ttm'` | str | Which reported rows the factor is computed on. One of `annual`, `quarterly`, `ttm`. |
| `periods` | `4` | int | How many rows of that basis back the comparison point sits. |
| `allow_negative_base` | `False` | bool | Return the number even where the starting value was not positive. |

Consumes: `revenue`, `net_income`, `eps_diluted`, `ebit`, `ebitda`, `total_equity`, `operating_cash_flow`, `capital_expenditure`, `free_cash_flow`, `dividend_per_share_paid`, `research_and_development`

Implemented by `factorbase.factors.fundamentals.growth:growth`

Reference: Penman, S. H. (2012). Financial Statement Analysis and Security Valuation, 5th ed., ch. 13.

#### `compound_annual_growth` - Compound Annual Growth

Compound growth per period of a reported line, in percent.

unit `percent` · better when `higher` · basis `annual` · also known as `geometric_growth`

Undefined from a non-positive base and undefined where the endpoint is negative, because a root of a negative number is not a growth rate. Both are NaN here rather than a complex value quietly reduced to its real part, which is what a naive implementation produces and what nobody notices.

```latex
CAGR_t = \left( \left( \frac{X_t}{X_{t-n}} \right)^{1/n} - 1 \right) \cdot 100, \qquad X_t > 0,\; X_{t-n} > 0
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `item` | `'revenue'` | str | Which line of the accounts the growth is measured on. One of `revenue`, `net_income`, `eps`, `ebit`, `ebitda`, `equity`, `operating_cash_flow`, `free_cash_flow`, `dividend`, `research`. |
| `period` | `'annual'` | str | Which reported rows the factor is computed on. One of `annual`, `quarterly`, `ttm`. |
| `years` | `5` | int | How many rows of that basis the growth compounds over. |

Consumes: `revenue`, `net_income`, `eps_diluted`, `ebit`, `ebitda`, `total_equity`, `operating_cash_flow`, `capital_expenditure`, `free_cash_flow`, `dividend_per_share_paid`, `research_and_development`

Implemented by `factorbase.factors.fundamentals.growth:compound_annual_growth`

Reference: Penman, S. H. (2012). Financial Statement Analysis and Security Valuation, 5th ed., ch. 13.

#### `growth_stability` - Growth Stability

How straight a line the reported series has followed, from 0 to 1.

unit `ratio` · better when `higher` · basis `annual` · range 0 to 1

Fitted in log space, so a company compounding at a steady 10 percent scores 1 whatever its size. A company with the same total growth delivered in one jump scores lower. That is what separates this from the inverse of a standard deviation, which would rank a jump and a steady climb by dispersion alone and miss which of the two is a business.

```latex
y_i = \ln X_{t-n+1+i}, \qquad R^2 = 1 - \frac{\sum_i (y_i - \hat{y}_i)^2}{\sum_i (y_i - \bar{y})^2}
```
Undefined where any value in the window is not positive.

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `item` | `'revenue'` | str | Which line of the accounts the stability is measured on. One of `revenue`, `net_income`, `eps`, `ebit`, `ebitda`, `equity`, `operating_cash_flow`, `free_cash_flow`, `dividend`, `research`. |
| `period` | `'annual'` | str | Which reported rows the factor is computed on. One of `annual`, `quarterly`, `ttm`. |
| `years` | `5` | int | How many rows the line is fitted through. |

Consumes: `revenue`, `net_income`, `eps_diluted`, `ebit`, `ebitda`, `total_equity`, `operating_cash_flow`, `capital_expenditure`, `free_cash_flow`, `dividend_per_share_paid`, `research_and_development`

Implemented by `factorbase.factors.fundamentals.growth:growth_stability`

Reference: Penman, S. H. (2012). Financial Statement Analysis and Security Valuation, 5th ed., ch. 13.

#### `growth_consistency` - Growth Consistency

Mean growth rate divided by its own standard deviation.

unit `ratio` · better when `higher` · basis `annual`

A company growing 8 percent every year and one averaging 8 percent between -20 and +40 are different businesses. This says which is which; the mean on its own never does. Dimensionless, so it ranks across industries.

```latex
GC_t = \frac{\overline{g}_t(n)}{s\left( g_t(n) \right)}
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `item` | `'revenue'` | str | Which line of the accounts the growth is measured on. One of `revenue`, `net_income`, `eps`, `ebit`, `ebitda`, `equity`, `operating_cash_flow`, `free_cash_flow`, `dividend`, `research`. |
| `period` | `'annual'` | str | Which reported rows the factor is computed on. One of `annual`, `quarterly`, `ttm`. |
| `years` | `5` | int | How many growth rates the mean and dispersion span. |

Consumes: `revenue`, `net_income`, `eps_diluted`, `ebit`, `ebitda`, `total_equity`, `operating_cash_flow`, `capital_expenditure`, `free_cash_flow`, `dividend_per_share_paid`, `research_and_development`

Implemented by `factorbase.factors.fundamentals.growth:growth_consistency`

Reference: Penman, S. H. (2012). Financial Statement Analysis and Security Valuation, 5th ed., ch. 13.

#### `absolute_growth` - Absolute Growth

Change of a reported line in currency over n periods.

unit `currency` · better when `higher` · basis `annual`

In currency rather than percent, which makes it useless across instruments and useful within one: it is the number that says whether a percentage growth rate was earned on a base worth caring about. Thirty percent on two million and three percent on two billion rank the other way round here, and both orderings are right for different questions.

```latex
\Delta X_t(n) = X_t - X_{t-n}
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `item` | `'revenue'` | str | Which line of the accounts the change is measured on. One of `revenue`, `net_income`, `eps`, `ebit`, `ebitda`, `equity`, `operating_cash_flow`, `free_cash_flow`, `dividend`, `research`. |
| `period` | `'annual'` | str | Which reported rows the factor is computed on. One of `annual`, `quarterly`, `ttm`. |
| `periods` | `5` | int | How many rows back the comparison point sits. |

Consumes: `revenue`, `net_income`, `eps_diluted`, `ebit`, `ebitda`, `total_equity`, `operating_cash_flow`, `capital_expenditure`, `free_cash_flow`, `dividend_per_share_paid`, `research_and_development`

Implemented by `factorbase.factors.fundamentals.growth:absolute_growth`

Reference: Penman, S. H. (2012). Financial Statement Analysis and Security Valuation, 5th ed., ch. 13.

#### `sequential_growth` - Sequential Growth

Percentage change against the immediately preceding quarter.

unit `percent` · better when `higher` · basis `quarterly`

Quarter on quarter, not against the year-ago quarter. It picks up an inflection roughly a year before the year-on-year figure does, and it is worthless for a seasonal business, where the swing between quarters is the season rather than the trend.

```latex
sg_t = \left( \frac{X_t}{X_{t-1}} - 1 \right) \cdot 100
```
Quarterly rows only.

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `item` | `'revenue'` | str | Which line of the accounts the growth is measured on. One of `revenue`, `net_income`, `eps`, `ebit`, `ebitda`, `equity`, `operating_cash_flow`, `free_cash_flow`, `dividend`, `research`. |
| `allow_negative_base` | `False` | bool | Return the number even where the starting value was not positive. |

Consumes: `revenue`, `net_income`, `eps_diluted`, `ebit`, `ebitda`, `total_equity`, `operating_cash_flow`, `capital_expenditure`, `free_cash_flow`, `dividend_per_share_paid`, `research_and_development`

Implemented by `factorbase.factors.fundamentals.growth:sequential_growth`

Reference: Penman, S. H. (2012). Financial Statement Analysis and Security Valuation, 5th ed., ch. 13.

#### `year_on_year_quarterly_growth` - Year-on-Year Quarterly Growth

Percentage change against the same quarter a year earlier.

unit `percent` · better when `higher` · basis `quarterly`

The seasonal counterpart to sequential growth. Comparing like quarters removes the season and, with it, the ability to see a turn inside the year. The two entries exist because reading only one of them is how a seasonal business gets mistaken for a growing one and back again.

```latex
yg_t = \left( \frac{X_t}{X_{t-4}} - 1 \right) \cdot 100
```
Quarterly rows only.

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `item` | `'revenue'` | str | Which line of the accounts the growth is measured on. One of `revenue`, `net_income`, `eps`, `ebit`, `ebitda`, `equity`, `operating_cash_flow`, `free_cash_flow`, `dividend`, `research`. |
| `allow_negative_base` | `False` | bool | Return the number even where the starting value was not positive. |

Consumes: `revenue`, `net_income`, `eps_diluted`, `ebit`, `ebitda`, `total_equity`, `operating_cash_flow`, `capital_expenditure`, `free_cash_flow`, `dividend_per_share_paid`, `research_and_development`

Implemented by `factorbase.factors.fundamentals.growth:year_on_year_quarterly_growth`

Reference: Penman, S. H. (2012). Financial Statement Analysis and Security Valuation, 5th ed., ch. 13.

### Leverage

#### `equity_ratio` - Equity Ratio

Shareholders' equity over total assets, in percent.

unit `percent` · better when `higher` · basis `annual`

How much of the balance sheet belongs to the owners. The single most informative leverage number because it needs no earnings, no cash flow and no judgement about what counts as debt.

```latex
ER_t = \frac{Equity_t}{Assets_t} \cdot 100
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `period` | `'annual'` | str | Which reported rows the factor is computed on. One of `annual`, `quarterly`, `ttm`. |

Consumes: `total_equity`, `total_assets`

Implemented by `factorbase.factors.fundamentals.leverage:equity_ratio`

Reference: Penman, S. H. (2012). Financial Statement Analysis and Security Valuation, 5th ed., ch. 9.

#### `liabilities_ratio` - Liabilities Ratio

Total liabilities over total assets, in percent.

unit `percent` · better when `lower` · basis `annual`

The complement of the equity ratio wherever there are no minority interests, and worth having separately because the two stop summing to 100 exactly where a group structure gets interesting.

```latex
LR_t = \frac{Liabilities_t}{Assets_t} \cdot 100
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `period` | `'annual'` | str | Which reported rows the factor is computed on. One of `annual`, `quarterly`, `ttm`. |

Consumes: `total_liabilities`, `total_assets`

Implemented by `factorbase.factors.fundamentals.leverage:liabilities_ratio`

Reference: Penman, S. H. (2012). Financial Statement Analysis and Security Valuation, 5th ed., ch. 9.

#### `debt_to_assets` - Debt to Assets

Interest-bearing debt over total assets, in percent.

unit `percent` · better when `lower` · basis `annual`

Debt, not liabilities. Trade payables are a liability and are not debt; conflating the two makes a retailer with fast supplier turnover look leveraged when its position is the opposite. The gap between this and the liabilities ratio is the operating float the business runs on.

```latex
DA_t = \frac{Debt_t}{Assets_t} \cdot 100
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `period` | `'annual'` | str | Which reported rows the factor is computed on. One of `annual`, `quarterly`, `ttm`. |

Consumes: `total_debt`, `total_assets`

Implemented by `factorbase.factors.fundamentals.leverage:debt_to_assets`

Reference: Penman, S. H. (2012). Financial Statement Analysis and Security Valuation, 5th ed., ch. 9.

#### `debt_to_equity` - Debt to Equity

Interest-bearing debt over equity, in percent.

unit `percent` · better when `lower` · basis `annual` · also known as `financial_leverage`

Undefined on negative equity rather than negative. A company with more liabilities than assets is not conservatively financed, which is exactly how the negative reading would sort.

```latex
DE_t = \frac{Debt_t}{Equity_t} \cdot 100, \qquad Equity_t > 0
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `period` | `'annual'` | str | Which reported rows the factor is computed on. One of `annual`, `quarterly`, `ttm`. |

Consumes: `total_debt`, `total_equity`

Implemented by `factorbase.factors.fundamentals.leverage:debt_to_equity`

Reference: Penman, S. H. (2012). Financial Statement Analysis and Security Valuation, 5th ed., ch. 9.

#### `net_debt_to_ebitda` - Net Debt to EBITDA

Debt less cash over EBITDA, as a multiple.

unit `ratio` · better when `lower` · basis `annual`

The covenant measure, and the one a lender actually watches. Negative readings are kept here rather than blanked: a company holding more cash than debt has negative net debt, and that is information, not an error. The denominator still has to be positive, because a multiple of a loss is not a multiple.

```latex
NDE_t = \frac{Debt_t - Cash_t}{EBITDA_t}, \qquad EBITDA_t > 0
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `period` | `'annual'` | str | Which reported rows the factor is computed on. One of `annual`, `quarterly`, `ttm`. |

Consumes: `total_debt`, `cash_and_equivalents`, `ebitda`

Implemented by `factorbase.factors.fundamentals.leverage:net_debt_to_ebitda`

Reference: Koller, T., Goedhart, M. and Wessels, D. (2020). Valuation, 7th ed., ch. 22.

#### `interest_coverage` - Interest Coverage

Operating profit or operating cash flow over interest expense.

unit `ratio` · better when `higher` · basis `annual`

How many times over the business earns what it owes its lenders each year. A company with no interest expense has infinite coverage, which is true and unrankable; it returns NaN here, and a NaN in this column reads as "no debt service", not as missing data. The cash-flow basis is the stricter of the two and the one that catches a company whose operating profit is accounting rather than cash.

```latex
IC_t = \frac{Base_t}{InterestExpense_t}
```
Base is EBIT or operating cash flow, whichever the parameter selects.

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `period` | `'annual'` | str | Which reported rows the factor is computed on. One of `annual`, `quarterly`, `ttm`. |
| `basis` | `'ebit'` | str | What the interest is covered out of. One of `ebit`, `operating_cash_flow`. |

Consumes: `ebit`, `operating_cash_flow`, `interest_expense`

Implemented by `factorbase.factors.fundamentals.leverage:interest_coverage`

Reference: Koller, T., Goedhart, M. and Wessels, D. (2020). Valuation, 7th ed., ch. 22.

#### `debt_coverage` - Debt Coverage

Cash flow, operating profit or revenue over total debt, in percent.

unit `percent` · better when `higher` · basis `annual`

How much of the debt a year of the business would repay. Deliberately the inverse of the usual debt-to-cash-flow multiple, because it stays finite as debt approaches zero and the multiple does not: a debt-free company gets a very large number here and an undefined one there, and only the first can be ranked.

```latex
DC_t = \frac{Base_t}{Debt_t} \cdot 100
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `period` | `'annual'` | str | Which reported rows the factor is computed on. One of `annual`, `quarterly`, `ttm`. |
| `basis` | `'operating_cash_flow'` | str | What the debt is covered out of. One of `operating_cash_flow`, `ebit`, `revenue`. |

Consumes: `operating_cash_flow`, `ebit`, `revenue`, `total_debt`

Implemented by `factorbase.factors.fundamentals.leverage:debt_coverage`

Reference: Koller, T., Goedhart, M. and Wessels, D. (2020). Valuation, 7th ed., ch. 22.

#### `cash_flow_to_debt` - Free Cash Flow to Debt

Free cash flow over total debt, in percent.

unit `percent` · better when `higher` · basis `annual`

The same question as debt coverage, asked of the cash that is genuinely free rather than of the cash from operations. Lower by construction for any business that has to keep investing, which is the distinction worth having.

```latex
FCFD_t = \frac{FCF_t}{Debt_t} \cdot 100
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `period` | `'annual'` | str | Which reported rows the factor is computed on. One of `annual`, `quarterly`, `ttm`. |

Consumes: `operating_cash_flow`, `capital_expenditure`, `free_cash_flow`, `total_debt`

Implemented by `factorbase.factors.fundamentals.leverage:cash_flow_to_debt`

Reference: Penman, S. H. (2012). Financial Statement Analysis and Security Valuation, 5th ed., ch. 10.

#### `long_term_debt_to_working_capital` - Long-Term Debt to Working Capital

Long-term debt over net working capital, as a multiple.

unit `ratio` · better when `lower` · basis `annual`

Undefined on negative working capital rather than negative. A company funding itself on its suppliers runs negative working capital by design, and the negative ratio would rank it as conservatively financed, which is the opposite of what the number is for.

```latex
LTDWC_t = \frac{LongTermDebt_t}{CurrentAssets_t - CurrentLiabilities_t}, \qquad NWC_t > 0
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `period` | `'annual'` | str | Which reported rows the factor is computed on. One of `annual`, `quarterly`, `ttm`. |

Consumes: `long_term_debt`, `current_assets`, `current_liabilities`

Implemented by `factorbase.factors.fundamentals.leverage:long_term_debt_to_working_capital`

Reference: Graham, B. and Dodd, D. (1934). Security Analysis, ch. 40.

#### `market_cap_to_debt` - Market Cap to Debt

Market capitalisation over interest-bearing debt.

unit `ratio` · better when `higher` · basis `annual` · needs a `market` series

How much equity cushion stands in front of the lenders, at market prices rather than at book. It moves with the share price, where every balance-sheet leverage ratio moves only when the accounts are published. That is what makes it worth having beside them and useless as a substitute for them: it falls fastest exactly when the market is already worried, which is information about the market and not about the accounts. A debt-free company has no ratio. NaN rather than infinity, and it reads as nothing to cover.

```latex
MCD_t = \frac{MC_t}{Debt_t}, \qquad Debt_t > 0
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `period` | `'annual'` | str | Which reported rows the debt is taken from. One of `annual`, `quarterly`, `ttm`. |

Consumes: `market_cap`, `total_debt`

Implemented by `factorbase.factors.fundamentals.valuation:market_cap_to_debt`

Reference: Merton, R. C. (1974). On the Pricing of Corporate Debt. Journal of Finance 29(2).

### Liquidity

#### `current_ratio` - Current Ratio

Current assets over current liabilities, as a multiple.

unit `ratio` · better when `higher` · basis `annual` · range 0 to None

Whether the next twelve months of obligations are covered by the next twelve months of assets. Crude, and crude in a known direction: it counts inventory that may not sell at book value as though it were cash.

```latex
CR_t = \frac{CurrentAssets_t}{CurrentLiabilities_t}
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `period` | `'annual'` | str | Which reported rows the factor is computed on. One of `annual`, `quarterly`, `ttm`. |

Consumes: `current_assets`, `current_liabilities`

Implemented by `factorbase.factors.fundamentals.leverage:current_ratio`

Reference: Penman, S. H. (2012). Financial Statement Analysis and Security Valuation, 5th ed., ch. 9.

#### `quick_ratio` - Quick Ratio

Current assets less inventory, over current liabilities.

unit `ratio` · better when `higher` · basis `annual` · range 0 to None

The current ratio with the inventory taken out, which is the whole point of having both. For a business whose stock turns in days the two are nearly identical; for one whose stock sits for a year they are not, and the gap is the measure.

```latex
QR_t = \frac{CurrentAssets_t - Inventory_t}{CurrentLiabilities_t}
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `period` | `'annual'` | str | Which reported rows the factor is computed on. One of `annual`, `quarterly`, `ttm`. |

Consumes: `current_assets`, `inventory`, `current_liabilities`

Implemented by `factorbase.factors.fundamentals.leverage:quick_ratio`

Reference: Penman, S. H. (2012). Financial Statement Analysis and Security Valuation, 5th ed., ch. 9.

#### `cash_ratio` - Cash Ratio

Cash over current liabilities, as a multiple.

unit `ratio` · better when `higher` · basis `annual` · range 0 to None

The strictest of the three: only what is already cash counts. A reading above 1 says the company could settle a year of obligations this afternoon, which for most businesses is a sign of an idle balance sheet rather than of prudence.

```latex
CashR_t = \frac{Cash_t}{CurrentLiabilities_t}
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `period` | `'annual'` | str | Which reported rows the factor is computed on. One of `annual`, `quarterly`, `ttm`. |

Consumes: `cash_and_equivalents`, `current_liabilities`

Implemented by `factorbase.factors.fundamentals.leverage:cash_ratio`

Reference: Penman, S. H. (2012). Financial Statement Analysis and Security Valuation, 5th ed., ch. 9.

### Profitability

#### `gross_margin` - Gross Margin

Gross profit over revenue, in percent.

unit `percent` · better when `higher` · basis `annual`

What is left of a sale after the direct cost of producing it. The cleanest read on pricing power there is, because it sits above every discretionary cost: a company can cut research or advertising to defend an operating margin for a year or two, and it cannot do the same here.

```latex
GM_t = \frac{GrossProfit_t}{Revenue_t} \cdot 100
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `period` | `'annual'` | str | Which reported rows the factor is computed on. One of `annual`, `quarterly`, `ttm`. |
| `average_years` | `1` | int | Mean over this many consecutive periods. One is the single-period reading. The average requires every period to be present, so a five-year mean is never computed from three years and passed off as one. |

Consumes: `gross_profit`, `revenue`

Implemented by `factorbase.factors.fundamentals.profitability:gross_margin`

Reference: Penman, S. H. (2012). Financial Statement Analysis and Security Valuation, 5th ed., ch. 11.

#### `ebit_margin` - EBIT Margin

Operating income over revenue, in percent.

unit `percent` · better when `higher` · basis `annual`

Profitability of the operating business, before financing and tax. The margin to use when comparing companies with different capital structures, because neither half of it depends on how the business was funded.

```latex
EBITM_t = \frac{EBIT_t}{Revenue_t} \cdot 100
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `period` | `'annual'` | str | Which reported rows the factor is computed on. One of `annual`, `quarterly`, `ttm`. |
| `average_years` | `1` | int | Mean over this many consecutive periods. One is the single-period reading. The average requires every period to be present, so a five-year mean is never computed from three years and passed off as one. |

Consumes: `ebit`, `revenue`

Implemented by `factorbase.factors.fundamentals.profitability:ebit_margin`

Reference: Penman, S. H. (2012). Financial Statement Analysis and Security Valuation, 5th ed., ch. 11.

#### `ebitda_margin` - EBITDA Margin

EBITDA over revenue, in percent.

unit `percent` · better when `higher` · basis `annual`

The operating margin with depreciation added back. Useful for comparing businesses whose assets were bought at very different times, and misleading as a proxy for cash: the depreciation being added back is a real cost that falls due again when the assets are replaced.

```latex
EBITDAM_t = \frac{EBITDA_t}{Revenue_t} \cdot 100
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `period` | `'annual'` | str | Which reported rows the factor is computed on. One of `annual`, `quarterly`, `ttm`. |
| `average_years` | `1` | int | Mean over this many consecutive periods. One is the single-period reading. The average requires every period to be present, so a five-year mean is never computed from three years and passed off as one. |

Consumes: `ebitda`, `revenue`

Implemented by `factorbase.factors.fundamentals.profitability:ebitda_margin`

Reference: Penman, S. H. (2012). Financial Statement Analysis and Security Valuation, 5th ed., ch. 11.

#### `pretax_margin` - Pretax Margin

Pretax income over revenue, in percent.

unit `percent` · better when `higher` · basis `annual`

After financing, before tax. The gap between this and the EBIT margin is what the debt costs; the gap between this and the net margin is what the tax authority takes. Both gaps are more stable than either margin, which is what makes the three worth reading together.

```latex
PTM_t = \frac{PretaxIncome_t}{Revenue_t} \cdot 100
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `period` | `'annual'` | str | Which reported rows the factor is computed on. One of `annual`, `quarterly`, `ttm`. |
| `average_years` | `1` | int | Mean over this many consecutive periods. One is the single-period reading. The average requires every period to be present, so a five-year mean is never computed from three years and passed off as one. |

Consumes: `pretax_income`, `revenue`

Implemented by `factorbase.factors.fundamentals.profitability:pretax_margin`

Reference: Penman, S. H. (2012). Financial Statement Analysis and Security Valuation, 5th ed., ch. 11.

#### `net_margin` - Net Margin

Net income over revenue, in percent.

unit `percent` · better when `higher` · basis `annual`

What reaches the shareholder per unit of sales. The most quoted margin and the least comparable: it carries the tax rate, the capital structure and every one-off item of the period, so two companies running the same business can differ by half on it for reasons that have nothing to do with the business.

```latex
NM_t = \frac{NetIncome_t}{Revenue_t} \cdot 100
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `period` | `'annual'` | str | Which reported rows the factor is computed on. One of `annual`, `quarterly`, `ttm`. |
| `average_years` | `1` | int | Mean over this many consecutive periods. One is the single-period reading. The average requires every period to be present, so a five-year mean is never computed from three years and passed off as one. |

Consumes: `net_income`, `revenue`

Implemented by `factorbase.factors.fundamentals.profitability:net_margin`

Reference: Penman, S. H. (2012). Financial Statement Analysis and Security Valuation, 5th ed., ch. 11.

#### `net_margin_stability` - Net Margin Stability

Mean net margin divided by its own standard deviation.

unit `ratio` · better when `higher` · basis `annual`

A company at 10 percent every year and one averaging 10 percent between 2 and 18 are not the same business. Dividing the level by the dispersion says which is which in one number, and a mean on its own never does. Dimensionless, so it compares across industries, and undefined for a company whose margin never moved, where the dispersion is zero.

```latex
NMS_t = \frac{\overline{NM}_t(n)}{s\left(NM_t(n)\right)}
```
Both taken over n annual periods; s is the sample standard deviation.

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `years` | `5` | int | How many annual periods the mean and dispersion span. |

Consumes: `net_income`, `revenue`

Implemented by `factorbase.factors.fundamentals.profitability:net_margin_stability`

Reference: Penman, S. H. (2012). Financial Statement Analysis and Security Valuation, 5th ed., ch. 13.

#### `net_margin_change` - Net Margin Change

Change in net margin over n years, in percentage points.

unit `percent` · better when `higher` · basis `annual`

Percentage points, not percent, and the distinction decides the ranking. A margin going from 2 to 4 percent has doubled, which is true and useless: as a percentage change it outranks a company going from 20 to 30, which is the larger move by every measure the income statement cares about.

```latex
\Delta NM_t(n) = NM_t - NM_{t-n}
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `years` | `5` | int | How many annual periods back the comparison point sits. |

Consumes: `net_income`, `revenue`

Implemented by `factorbase.factors.fundamentals.profitability:net_margin_change`

Reference: Penman, S. H. (2012). Financial Statement Analysis and Security Valuation, 5th ed., ch. 13.

#### `return_on_equity` - Return on Equity

Net income over shareholders' equity, in percent.

unit `percent` · better when `higher` · basis `annual`

What the business earns on the money shareholders left in it. High readings come from two very different places, and the ratio does not distinguish them: a genuinely profitable business, and a heavily leveraged one with a small equity base. Read it next to the equity ratio or not at all. The denominator averages this period's and last period's equity by default. Income accrues over a period while equity is a snapshot at its end, and dividing a flow by a closing stock overstates the return of any company that raised capital during the year.

```latex
ROE_t = \frac{NetIncome_t}{\frac{1}{2}\left( Equity_t + Equity_{t-1} \right)} \cdot 100
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `period` | `'annual'` | str | Which reported rows the factor is computed on. One of `annual`, `quarterly`, `ttm`. |
| `average_years` | `1` | int | Mean over this many consecutive periods. |
| `average_balance` | `True` | bool | Divide by the mean of the opening and closing equity rather than by the closing figure alone. |

Consumes: `net_income`, `total_equity`

Implemented by `factorbase.factors.fundamentals.profitability:return_on_equity`

Reference: Penman, S. H. (2012). Financial Statement Analysis and Security Valuation, 5th ed., ch. 12.

#### `return_on_assets` - Return on Assets

Net income over total assets, in percent.

unit `percent` · better when `higher` · basis `annual`

The same numerator as return on equity over a denominator that leverage cannot shrink. It is therefore the blunter and the more comparable of the two, and the gap between them is a direct read on how much debt is doing the work.

```latex
ROA_t = \frac{NetIncome_t}{\frac{1}{2}\left( Assets_t + Assets_{t-1} \right)} \cdot 100
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `period` | `'annual'` | str | Which reported rows the factor is computed on. One of `annual`, `quarterly`, `ttm`. |
| `average_years` | `1` | int | Mean over this many consecutive periods. |
| `average_balance` | `True` | bool | Divide by the mean of the opening and closing assets. |

Consumes: `net_income`, `total_assets`

Implemented by `factorbase.factors.fundamentals.profitability:return_on_assets`

Reference: Penman, S. H. (2012). Financial Statement Analysis and Security Valuation, 5th ed., ch. 12.

#### `return_on_invested_capital` - Return on Invested Capital

After-tax operating profit over invested capital, in percent.

unit `percent` · better when `higher` · basis `annual` · also known as `roic`

NOPAT over capital, not net income over capital. The numerator has to be the return to everyone who put capital in, because the denominator is what all of them put in. Using net income mixes a figure measured after interest with a base measured before it, and flatters leveraged companies for exactly the wrong reason. Invested capital is derived as equity plus debt less cash when the source does not supply its own. Every data vendor defines it differently, so the derivation is written down rather than assumed. The tax rate is a flat assumption and a parameter. Deriving it from the reported charge is more accurate in an ordinary year and badly wrong in a year with a one-off credit, which is precisely the year a screen picks up.

```latex
NOPAT_t = EBIT_t \cdot (1 - \tau)
```

```latex
IC_t = Equity_t + Debt_t - Cash_t
```
Used only when the source frame has no invested_capital column of its own.

```latex
ROIC_t = \frac{NOPAT_t}{\frac{1}{2}\left( IC_t + IC_{t-1} \right)} \cdot 100
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `period` | `'annual'` | str | Which reported rows the factor is computed on. One of `annual`, `quarterly`, `ttm`. |
| `average_years` | `1` | int | Mean over this many consecutive periods. |
| `tax_rate` | `25.0` | float | Flat rate applied to operating profit, in percent. |
| `average_balance` | `True` | bool | Divide by the mean of the opening and closing capital. |

Consumes: `ebit`, `total_equity`, `total_debt`, `cash_and_equivalents`, `invested_capital`

Implemented by `factorbase.factors.fundamentals.profitability:return_on_invested_capital`

Reference: Koller, T., Goedhart, M. and Wessels, D. (2020). Valuation, 7th ed., ch. 8.

#### `magic_formula_return_on_capital` - Return on Capital (Greenblatt)

EBIT over net working capital plus net fixed assets, in percent.

unit `percent` · better when `higher` · basis `annual`

Greenblatt's version, and deliberately not the same thing as return on invested capital. It is pretax and it leaves out goodwill, so it measures what the operating business earns on the tangible capital it actually needs, rather than on what a previous owner paid for it. A serial acquirer therefore scores far higher here than on ROIC, and the gap between the two is the acquisition premium.

```latex
NWC_t = CurrentAssets_t - CurrentLiabilities_t
```

```latex
NFA_t = Assets_t - CurrentAssets_t
```

```latex
ROC_t = \frac{EBIT_t}{NWC_t + NFA_t} \cdot 100
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `period` | `'annual'` | str | Which reported rows the factor is computed on. One of `annual`, `quarterly`, `ttm`. |

Consumes: `ebit`, `current_assets`, `current_liabilities`, `total_assets`

Implemented by `factorbase.factors.fundamentals.profitability:magic_formula_return_on_capital`

Reference: Greenblatt, J. (2006). The Little Book That Beats the Market, appendix.

#### `rule_of_forty` - Rule of 40

Revenue growth plus EBITDA margin, both in percent.

unit `percent` · better when `higher` · basis `ttm`

Adding a growth rate to a margin is dimensionally odd and the measure is used anyway, because the trade-off it encodes is real: a software company can buy growth with margin or margin with growth, and forty is the line below which it is doing neither well. It is a heuristic for one industry at one stage of its life and travels badly. Applied to a utility it says nothing; applied to a company whose growth came from an acquisition it says the wrong thing.

```latex
R40_t = \left( \frac{Revenue_t}{Revenue_{t-4}} - 1 \right) \cdot 100 + \frac{EBITDA_t}{Revenue_t} \cdot 100
```
The growth term steps back four rows of the chosen basis, i.e. a year of quarters.

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `period` | `'ttm'` | str | Which reported rows the factor is computed on. One of `annual`, `quarterly`, `ttm`. |

Consumes: `revenue`, `ebitda`

Implemented by `factorbase.factors.fundamentals.profitability:rule_of_forty`

Reference: Feld, B. (2015). The Rule of 40% For a Healthy SaaS Company.

#### `research_intensity` - Research Intensity

R&D spending over revenue or over assets, in percent.

unit `percent` · better when `undefined` · basis `annual`

How much of the business is spent on renewing it. High intensity depresses every margin in this file while it is being spent, which is why a screen that ranks on margin alone systematically ranks down companies investing in their own future.

```latex
RI_t = \frac{R\&D_t}{Base_t} \cdot 100
```
Base is revenue or total assets, whichever the parameter selects.

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `base` | `'revenue'` | str | What the spending is measured against. One of `revenue`, `total_assets`. |
| `period` | `'annual'` | str | Which reported rows the factor is computed on. One of `annual`, `quarterly`, `ttm`. |

Consumes: `research_and_development`, `revenue`, `total_assets`

Implemented by `factorbase.factors.fundamentals.profitability:research_intensity`

Reference: Penman, S. H. (2012). Financial Statement Analysis and Security Valuation, 5th ed., ch. 17.

### Size

#### `revenue` - Revenue

Reported revenue for the period, in currency.

unit `currency` · better when `higher` · basis `ttm` · range 0 to None

Net sales as reported, on whichever basis the parameter selects. Not comparable across currencies without a conversion the caller has to do first; nothing here converts anything.

```latex
R_t = Revenue_t
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `period` | `'ttm'` | str | Which reported rows the factor is computed on. One of `annual`, `quarterly`, `ttm`. |

Consumes: `revenue`

Implemented by `factorbase.factors.fundamentals.size:revenue`

Reference: Penman, S. H. (2012). Financial Statement Analysis and Security Valuation, 5th ed., ch. 2.

#### `net_income` - Net Income

Reported net income for the period, in currency.

unit `currency` · better when `higher` · basis `ttm`

Profit attributable to shareholders, as reported. The line every earnings multiple divides, exposed so that a screen can filter on its sign before it ever reaches a ratio that is undefined there.

```latex
NI_t = NetIncome_t
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `period` | `'ttm'` | str | Which reported rows the factor is computed on. One of `annual`, `quarterly`, `ttm`. |

Consumes: `net_income`

Implemented by `factorbase.factors.fundamentals.size:net_income`

Reference: Penman, S. H. (2012). Financial Statement Analysis and Security Valuation, 5th ed., ch. 2.

#### `free_cash_flow` - Free Cash Flow

Operating cash flow less capital expenditure, in currency.

unit `currency` · better when `higher` · basis `ttm`

Used as reported when the source supplies it, derived otherwise. The derivation treats capital expenditure as a positive number, as the data contract states: a source that reports it negative would have it added instead of subtracted, and free cash flow would come out at roughly twice the truth for any capital-intensive business.

```latex
FCF_t = OperatingCashFlow_t - CapEx_t
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `period` | `'ttm'` | str | Which reported rows the factor is computed on. One of `annual`, `quarterly`, `ttm`. |

Consumes: `operating_cash_flow`, `capital_expenditure`, `free_cash_flow`

Implemented by `factorbase.factors.fundamentals.size:free_cash_flow`

Reference: Penman, S. H. (2012). Financial Statement Analysis and Security Valuation, 5th ed., ch. 10.

#### `market_capitalisation` - Market Capitalisation

The market series read at each reporting date.

unit `currency` · better when `undefined` · basis `point_in_time` · range 0 to None · needs a `market` series

Size as a factor in its own right, and the as-of join every other market-based entry here uses, exposed so that a universe filter and a valuation ratio cannot disagree about which market value they meant.

```latex
MC_t = Market_{s}, \quad s = \max\{ u \le t : Market_u \text{ exists} \}
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `period` | `'annual'` | str | Which reported rows the dates are taken from. A frame carrying more than one basis has repeated period ends, and the as-of join cannot reindex onto them, so the basis is selected first here as everywhere else. One of `annual`, `quarterly`, `ttm`. |

Consumes: `market_cap`

Implemented by `factorbase.factors.fundamentals.size:market_capitalisation`

Reference: Fama, E. F. and French, K. R. (1992). The Cross-Section of Expected Stock Returns. Journal of Finance 47(2).

#### `enterprise_value` - Enterprise Value

Market capitalisation plus total debt less cash.

unit `currency` · better when `undefined` · basis `point_in_time` · needs a `market` series

What it would cost to buy the whole business free of its financing. The figure the enterprise multiples divide, and the reason they can be compared across companies with different amounts of debt.

```latex
EV_t = MC_t + Debt_t - Cash_t
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `period` | `'annual'` | str | Which reported rows the debt and cash are taken from. One of `annual`, `quarterly`, `ttm`. |

Consumes: `market_cap`, `total_debt`, `cash_and_equivalents`

Implemented by `factorbase.factors.fundamentals.valuation:enterprise_value`

Reference: Koller, T., Goedhart, M. and Wessels, D. (2020). Valuation, 7th ed., ch. 18.

### Valuation

#### `price_to_earnings` - Price to Earnings

Market capitalisation over net income.

unit `ratio` · better when `lower` · basis `ttm` · needs a `market` series · also known as `pe_ratio`

The multiple everyone quotes and the one that behaves worst. It is undefined at zero earnings, explodes either side of it, and goes negative on a loss, where it sorts below every profitable company in the universe. A screen ranking ascending on it and not handling that picks the biggest losses first. The default returns NaN on a loss. `allow_negative` returns the number for callers who have their own handling, and the entry names what they are taking on. Where the ratio is only needed for ranking, the earnings yield is the same information without any of this.

```latex
PE_t = \frac{MC_t}{NetIncome_t}, \qquad NetIncome_t > 0
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `period` | `'ttm'` | str | Which reported rows the factor is computed on. One of `annual`, `quarterly`, `ttm`. |
| `average_years` | `1` | int | Mean over this many consecutive periods. |

Consumes: `market_cap`, `net_income`

Implemented by `factorbase.factors.fundamentals.valuation:price_to_earnings`

Reference: Penman, S. H. (2012). Financial Statement Analysis and Security Valuation, 5th ed., ch. 6.

#### `price_to_book` - Price to Book

Market capitalisation over shareholders' equity.

unit `ratio` · better when `lower` · basis `annual` · needs a `market` series · also known as `pb_ratio`

The oldest value factor and the one most damaged by how accounting has changed. Book value counts factories and not brands, and treats research as an expense rather than an asset, so a software company can trade at twenty times book while owning something more durable than a steel mill at one.

```latex
PB_t = \frac{MC_t}{Equity_t}, \qquad Equity_t > 0
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `period` | `'annual'` | str | Which reported rows the factor is computed on. One of `annual`, `quarterly`, `ttm`. |
| `average_years` | `1` | int | Mean over this many consecutive periods. |

Consumes: `market_cap`, `total_equity`

Implemented by `factorbase.factors.fundamentals.valuation:price_to_book`

Reference: Fama, E. F. and French, K. R. (1992). The Cross-Section of Expected Stock Returns. Journal of Finance 47(2).

#### `price_to_sales` - Price to Sales

Market capitalisation over revenue.

unit `ratio` · better when `lower` · basis `ttm` · needs a `market` series · also known as `ps_ratio`

The one multiple that is almost always defined, because revenue is rarely negative. That is its use and its weakness in the same sentence: it ranks a company with no profits identically whether the absence is a bad year or the business model.

```latex
PS_t = \frac{MC_t}{Revenue_t}
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `period` | `'ttm'` | str | Which reported rows the factor is computed on. One of `annual`, `quarterly`, `ttm`. |
| `average_years` | `1` | int | Mean over this many consecutive periods. |

Consumes: `market_cap`, `revenue`

Implemented by `factorbase.factors.fundamentals.valuation:price_to_sales`

Reference: O'Shaughnessy, J. P. (2011). What Works on Wall Street, 4th ed., ch. 6.

#### `price_to_free_cash_flow` - Price to Free Cash Flow

Market capitalisation over free cash flow.

unit `ratio` · better when `lower` · basis `ttm` · needs a `market` series

Harder to manage than earnings and therefore harder to flatter, at the cost of being far noisier: a single year of heavy capital spending halves free cash flow without telling you anything about the business. Read it averaged, or read it next to the earnings multiple.

```latex
FCF_t = OperatingCashFlow_t - CapEx_t
```
Capital expenditure is a positive number, per the data contract.

```latex
PFCF_t = \frac{MC_t}{FCF_t}, \qquad FCF_t > 0
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `period` | `'ttm'` | str | Which reported rows the factor is computed on. One of `annual`, `quarterly`, `ttm`. |
| `average_years` | `1` | int | Mean over this many consecutive periods. |

Consumes: `market_cap`, `operating_cash_flow`, `capital_expenditure`, `free_cash_flow`

Implemented by `factorbase.factors.fundamentals.valuation:price_to_free_cash_flow`

Reference: Penman, S. H. (2012). Financial Statement Analysis and Security Valuation, 5th ed., ch. 10.

#### `earnings_yield` - Earnings Yield

Net income over market capitalisation, in percent.

unit `percent` · better when `higher` · basis `ttm` · needs a `market` series

The inverse of the price-to-earnings ratio and the better behaved of the pair. It passes through zero smoothly where the multiple goes to infinity, so it can be averaged, ranked and combined with other factors without a single special case. Anywhere a screen only needs an ordering, this is the one to use.

```latex
EY_t = \frac{NetIncome_t}{MC_t} \cdot 100
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `period` | `'ttm'` | str | Which reported rows the factor is computed on. One of `annual`, `quarterly`, `ttm`. |
| `average_years` | `1` | int | Mean over this many consecutive periods. |

Consumes: `market_cap`, `net_income`

Implemented by `factorbase.factors.fundamentals.valuation:earnings_yield`

Reference: Penman, S. H. (2012). Financial Statement Analysis and Security Valuation, 5th ed., ch. 6.

#### `free_cash_flow_yield` - Free Cash Flow Yield

Free cash flow over market capitalisation, in percent.

unit `percent` · better when `higher` · basis `ttm` · needs a `market` series

What the business would pay out if it paid out everything it did not need to reinvest. Well behaved around zero for the same reason the earnings yield is, and subject to the same capital-spending noise as the price-to-free-cash-flow multiple.

```latex
FCFY_t = \frac{FCF_t}{MC_t} \cdot 100
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `period` | `'ttm'` | str | Which reported rows the factor is computed on. One of `annual`, `quarterly`, `ttm`. |
| `average_years` | `1` | int | Mean over this many consecutive periods. |

Consumes: `market_cap`, `operating_cash_flow`, `capital_expenditure`, `free_cash_flow`

Implemented by `factorbase.factors.fundamentals.valuation:free_cash_flow_yield`

Reference: Penman, S. H. (2012). Financial Statement Analysis and Security Valuation, 5th ed., ch. 10.

#### `ev_to_ebit` - EV to EBIT

Enterprise value over operating income.

unit `ratio` · better when `lower` · basis `ttm` · needs a `market` series

Preferred over price-to-earnings when leverage differs across the comparison set: numerator and denominator both sit before financing, so the capital structure cancels instead of distorting. Two identical businesses, one funded with debt and one without, get the same reading here and very different ones on a price multiple.

```latex
EVEBIT_t = \frac{EV_t}{EBIT_t}, \qquad EBIT_t > 0
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `period` | `'ttm'` | str | Which reported rows the factor is computed on. One of `annual`, `quarterly`, `ttm`. |

Consumes: `market_cap`, `total_debt`, `cash_and_equivalents`, `ebit`

Implemented by `factorbase.factors.fundamentals.valuation:ev_to_ebit`

Reference: Koller, T., Goedhart, M. and Wessels, D. (2020). Valuation, 7th ed., ch. 18.

#### `ev_to_ebitda` - EV to EBITDA

Enterprise value over EBITDA.

unit `ratio` · better when `lower` · basis `ttm` · needs a `market` series

The multiple most used in transactions, because it is the one least affected by accounting choices about depreciation. That same property makes it flatter capital-intensive businesses, whose real cost of staying in business is precisely the depreciation it ignores.

```latex
EVEBITDA_t = \frac{EV_t}{EBITDA_t}, \qquad EBITDA_t > 0
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `period` | `'ttm'` | str | Which reported rows the factor is computed on. One of `annual`, `quarterly`, `ttm`. |

Consumes: `market_cap`, `total_debt`, `cash_and_equivalents`, `ebitda`

Implemented by `factorbase.factors.fundamentals.valuation:ev_to_ebitda`

Reference: Koller, T., Goedhart, M. and Wessels, D. (2020). Valuation, 7th ed., ch. 18.

#### `ev_to_sales` - EV to Sales

Enterprise value over revenue.

unit `ratio` · better when `lower` · basis `ttm` · needs a `market` series

The enterprise counterpart of price-to-sales, and the version to use when the comparison set includes companies carrying real debt. Almost always defined, and almost always in need of a margin alongside it.

```latex
EVS_t = \frac{EV_t}{Revenue_t}
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `period` | `'ttm'` | str | Which reported rows the factor is computed on. One of `annual`, `quarterly`, `ttm`. |

Consumes: `market_cap`, `total_debt`, `cash_and_equivalents`, `revenue`

Implemented by `factorbase.factors.fundamentals.valuation:ev_to_sales`

Reference: Koller, T., Goedhart, M. and Wessels, D. (2020). Valuation, 7th ed., ch. 18.

#### `ev_to_free_cash_flow` - EV to Free Cash Flow

Enterprise value over free cash flow.

unit `ratio` · better when `lower` · basis `ttm` · needs a `market` series

Cash against the whole capital structure. The strictest of the multiples here and the noisiest, since it combines the capital-spending swings of free cash flow with a denominator that must be positive to mean anything.

```latex
EVFCF_t = \frac{EV_t}{FCF_t}, \qquad FCF_t > 0
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `period` | `'ttm'` | str | Which reported rows the factor is computed on. One of `annual`, `quarterly`, `ttm`. |

Consumes: `market_cap`, `total_debt`, `cash_and_equivalents`, `operating_cash_flow`, `capital_expenditure`, `free_cash_flow`

Implemented by `factorbase.factors.fundamentals.valuation:ev_to_free_cash_flow`

Reference: Koller, T., Goedhart, M. and Wessels, D. (2020). Valuation, 7th ed., ch. 18.

#### `magic_formula_earnings_yield` - Earnings Yield (Greenblatt)

Operating income over enterprise value, in percent.

unit `percent` · better when `higher` · basis `ttm` · needs a `market` series

Greenblatt's earnings yield: EBIT over enterprise value, not net income over market capitalisation. Both halves sit before financing, so two companies with identical operations and different debt loads rank together instead of apart. The other half of his pair is the return on capital in the profitability family.

```latex
MFEY_t = \frac{EBIT_t}{EV_t} \cdot 100
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `period` | `'ttm'` | str | Which reported rows the factor is computed on. One of `annual`, `quarterly`, `ttm`. |

Consumes: `market_cap`, `total_debt`, `cash_and_equivalents`, `ebit`

Implemented by `factorbase.factors.fundamentals.valuation:magic_formula_earnings_yield`

Reference: Greenblatt, J. (2006). The Little Book That Beats the Market, appendix.

#### `peg_ratio` - PEG Ratio

Price-to-earnings divided by the earnings growth rate.

unit `ratio` · better when `lower` · basis `ttm` · needs a `market` series

Undefined wherever growth is not positive, which is most of the time for most companies and is why the measure is far quieter in practice than its reputation suggests. A negative PEG, from a negative growth rate, reads as cheap and means the opposite, so those readings are blanked out here rather than ranked. The growth rate is historical. Using a forecast, as the original does, replaces one problem with a larger one.

```latex
g_t = \left( \frac{NetIncome_t}{NetIncome_{t-k}} - 1 \right) \cdot 100, \qquad g_t > 0
```

```latex
PEG_t = \frac{PE_t}{g_t}
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `period` | `'ttm'` | str | Which reported rows the factor is computed on. One of `annual`, `quarterly`, `ttm`. |
| `growth_periods` | `4` | int | How many rows back the growth comparison point sits. |

Consumes: `market_cap`, `net_income`

Implemented by `factorbase.factors.fundamentals.valuation:peg_ratio`

Reference: Lynch, P. (1989). One Up On Wall Street, ch. 13.

#### `dividend_yield` - Dividend Yield

Dividends over market capitalisation, in percent.

unit `percent` · better when `higher` · basis `annual` · range 0 to None · needs a `market` series

`basis` picks between what was paid over the period and what has been declared for it. The difference is up to a year of timing and it is systematic rather than noise: a company that has already announced a cut still shows the old yield on the paid basis, which is exactly the situation a yield screen is most likely to walk into. `base` divides by enterprise value instead of market capitalisation, so a leveraged company's yield falls towards what the dividend costs on the whole business rather than on its equity sliver. The two readings diverge exactly where the leverage is, which is where a yield screen is most likely to be picking up risk and calling it income.

```latex
DY_t = \frac{Dividends_t}{MC_t} \cdot 100
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `period` | `'annual'` | str | Which reported rows the factor is computed on. One of `annual`, `quarterly`, `ttm`. |
| `average_years` | `1` | int | Mean over this many consecutive periods. |
| `basis` | `'paid'` | str | Dividends actually paid in the period, or announced for it. One of `paid`, `declared`. |
| `base` | `'market_cap'` | str | What the dividend is measured against. Enterprise value asks what it yields on the whole capital structure rather than on the equity alone. One of `market_cap`, `enterprise_value`. |

Consumes: `market_cap`, `total_debt`, `cash_and_equivalents`, `dividends_paid`, `dividend_per_share_paid`, `dividend_per_share_declared`, `shares_outstanding`

Implemented by `factorbase.factors.fundamentals.valuation:dividend_yield`

Reference: Penman, S. H. (2012). Financial Statement Analysis and Security Valuation, 5th ed., ch. 4.

#### `payout_ratio` - Payout Ratio

Dividends over net income, in percent.

unit `percent` · better when `undefined` · basis `annual`

How much of what was earned was handed out. Undefined on a loss rather than negative: a company paying a dividend out of reserves in a loss year has a payout ratio that is not meaningfully a number, and the negative reading it would otherwise produce sorts as though it were retaining everything.

```latex
PR_t = \frac{Dividends_t}{NetIncome_t} \cdot 100, \qquad NetIncome_t > 0
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `period` | `'annual'` | str | Which reported rows the factor is computed on. One of `annual`, `quarterly`, `ttm`. |
| `average_years` | `1` | int | Mean over this many consecutive periods. |

Consumes: `dividends_paid`, `net_income`

Implemented by `factorbase.factors.fundamentals.valuation:payout_ratio`

Reference: Penman, S. H. (2012). Financial Statement Analysis and Security Valuation, 5th ed., ch. 4.

#### `market_cap_to_research` - Market Cap to R&D

Market capitalisation over annual research spending.

unit `ratio` · better when `lower` · basis `annual` · needs a `market` series

How many years of the current research budget the market is paying for. Low readings are cheap only if the research is worth something, which this says nothing about: a company that has cut R&D to nothing reads as spectacularly cheap right up to the point its pipeline empties. Read it next to research intensity, which says how much is being spent, or not at all.

```latex
MCRD_t = \frac{MC_t}{R\&D_t}, \qquad R\&D_t > 0
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `period` | `'annual'` | str | Which reported rows the spending is taken from. One of `annual`, `quarterly`, `ttm`. |

Consumes: `market_cap`, `research_and_development`

Implemented by `factorbase.factors.fundamentals.valuation:market_cap_to_research`

Reference: Chan, L. K. C., Lakonishok, J. and Sougiannis, T. (2001). The Stock Market Valuation of Research and Development Expenditures. Journal of Finance 56(6).

## Composites

A rank or a score per instrument, across a universe at one date.

### Ranking

#### `factor_rank` - Factor Rank

Position within the cross-section, 1 being best.

unit `count` · better when `lower` · range 1 to None

`direction` decides which end is best and is the same field the underlying factor's own entry carries. Read it from the catalogue rather than typing it: passing it the wrong way round inverts the strategy and produces a result that looks entirely reasonable. Ties share the average of the positions they span, so a universe where many instruments report the same value does not get an arbitrary order imposed on it. `undefined` is not an acceptable direction and raises; there is no correct way to rank an oscillator without a strategy around it.

```latex
r_i = \left| \{ j : x_j \succ x_i \} \right| + 1
```
The ordering depends on direction. NaN values are excluded from the set.

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `direction` | `'higher'` | str | Which end of the scale ranks first. One of `higher`, `lower`. |
| `method` | `'average'` | str | How instruments with equal values share their positions. One of `average`, `min`, `max`, `first`, `dense`. |

Consumes: `factor_value`

Implemented by `factorbase.factors.ranking:rank`

Reference: Grinold, R. C. and Kahn, R. N. (2000). Active Portfolio Management, 2nd ed., ch. 4.

#### `factor_percentile` - Factor Percentile

Position as a percentage of the cross-section, 100 being best.

unit `percent` · better when `higher` · range 0 to 100

Comparable across dates and across factors in a way a raw rank is not. A rank of 40 means something very different in a universe of 50 and one of 3000; a percentile of 80 does not. This is the form the composite score combines, for that reason.

```latex
p_i = \frac{n - r_i}{n - 1} \cdot 100
```
n counts only the instruments with a value. A single-instrument set reads 50.

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `direction` | `'higher'` | str | Which end of the scale scores 100. One of `higher`, `lower`. |

Consumes: `factor_value`

Implemented by `factorbase.factors.ranking:percentile`

Reference: Grinold, R. C. and Kahn, R. N. (2000). Active Portfolio Management, 2nd ed., ch. 4.

#### `factor_z_score` - Factor Z-Score

Standardised distance from the cross-sectional mean.

unit `ratio` · better when `higher`

Keeps the spacing a rank throws away: the gap between the best and the second-best instrument is visible here and invisible in a rank. That is an advantage when the distribution behaves and a liability when it does not, because one extreme value moves the mean and the deviation at once, and therefore moves everybody else's score. `winsorise` clips each tail before standardising, which is the usual defence. One percent is the common choice. At 0 the raw values are used and the entry makes no promises about what one bad print will do.

```latex
z_i = \frac{x_i - \bar{x}}{s}
```
s is the sample deviation across the set. The sign is flipped when lower is better.

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `direction` | `'higher'` | str | Which end of the scale scores positive. One of `higher`, `lower`. |
| `winsorise` | `0.0` | float | Percentile clipped from each tail before standardising. 0 disables it. |

Consumes: `factor_value`

Implemented by `factorbase.factors.ranking:z_score`

Reference: Grinold, R. C. and Kahn, R. N. (2000). Active Portfolio Management, 2nd ed., ch. 4.

#### `composite_score` - Composite Score

Weighted mean of several factors' percentiles, 0 to 100.

unit `percent` · better when `higher` · range 0 to 100

Percentiles rather than raw values, because the components are in different units and adding a price-to-earnings ratio to a margin is meaningless. Percentiles rather than z-scores, because one extreme instrument should not move everybody else's score. Weights are used as given and are never renormalised per instrument. An instrument missing a component carrying 30 percent of the weight has 70 percent of the strategy applied to it, and reporting that as the same score as everyone else's is how a screen ends up ranking on a different rule for every row. `min_coverage` is the share of weight that has to be present; below it the score is NaN. The `coverage` function reports the share directly, so a caller can tell thin data from a missing instrument.

```latex
S_i = \frac{\sum_k w_k \, p_{k,i} \, \mathbb{1}[p_{k,i} \text{ exists}]}{\sum_k w_k \, \mathbb{1}[p_{k,i} \text{ exists}]}
```

```latex
c_i = \frac{\sum_k w_k \, \mathbb{1}[p_{k,i} \text{ exists}]}{\sum_k w_k}, \qquad S_i \text{ undefined where } c_i < c_{min}
```

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `min_coverage` | `1.0` | float | Share of the total weight that must have a value. The default of 1 requires every component, which is the only setting under which every instrument was scored by the same rule. |

Consumes: `factor_values`

Implemented by `factorbase.factors.ranking:composite_score`

Reference: Grinold, R. C. and Kahn, R. N. (2000). Active Portfolio Management, 2nd ed., ch. 4.

#### `top_n` - Top N

Boolean mask of the best n instruments in each cross-section.

unit `boolean` · better when `higher`

Ties at the boundary are all included, so the mask can select more than n instruments. Cutting the tie arbitrarily would make the selection depend on the order of the columns, which is a property of the frame and not of the data.

```latex
Top_i = r_i \le n
```
Rank taken with min tie handling, so tied instruments share the lower position.

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `count` | `20` | int | How many instruments to select. |
| `direction` | `'higher'` | str | Which end of the scale is selected from. One of `higher`, `lower`. |

Consumes: `factor_value`

Implemented by `factorbase.factors.ranking:top_n`

**Note.** Boolean, but a composite rather than a signal: it needs a cross-section, not a price history. A signal answers "did this happen to this instrument"; this answers "was this instrument among the best", which no amount of its own history can decide.

Reference: Grinold, R. C. and Kahn, R. N. (2000). Active Portfolio Management, 2nd ed., ch. 14.

#### `quantile_bucket` - Quantile Bucket

Which fifth, tenth or other slice of the cross-section each instrument sits in.

unit `count` · better when `lower` · range 1 to None

Bucket 1 is the best. Built from percentiles rather than from the values, so the buckets hold equal numbers of instruments rather than equal ranges of value. That is what a factor study means by a quintile, and building it the other way puts nine tenths of a skewed universe into one bucket.

```latex
b_i = \left\lceil \frac{100 - p_i}{100 / q} \right\rceil
```
Clipped to the range 1 to q, so the single best instrument lands in bucket 1.

| Parameter | Default | Type | What it does |
|---|---|---|---|
| `buckets` | `5` | int | How many slices the cross-section is cut into. |
| `direction` | `'higher'` | str | Which end of the scale lands in bucket 1. One of `higher`, `lower`. |

Consumes: `factor_value`

Implemented by `factorbase.factors.ranking:quantile_bucket`

Reference: Fama, E. F. and French, K. R. (1992). The Cross-Section of Expected Stock Returns. Journal of Finance 47(2).
