# Compared with TTR

The README claims that two packages hand you the same indicator name and
disagree without saying why. This is the measurement behind that claim.

23 mappings against [TTR](https://cran.r-project.org/package=TTR) 0.24.4 on R 4.6.1, run against `tests/data/reference_series.csv`.

**This file is generated** from `catalog/mappings/ttr.yaml`, and every number in
it was produced by the `ttr` job running both sides. The job fails if any of
these statements stops being true, including the traps: a difference that
quietly disappears is a note that reads as current and describes nothing.

## Agreeing outright

18 entries, within the stated tolerance over every bar where both
are defined.

| Factor | The R call that agrees | Within |
|---|---|---|
| `sma` (periods=20) | `SMA(close, 20)` | 1e-09 |
| `ema` (periods=20) | `EMA(close, 20)` | 1e-09 |
| `wma` (periods=20) | `WMA(close, 20)` | 1e-09 |
| `rsi` | `RSI(close, 14)` | 1e-09 |
| `rate_of_change` | `ROC(close, 12, type = "discrete") * 100` | 1e-09 |
| `cci` | `CCI(cbind(high, low, close), 20, c = 0.015)` | 1e-08 |
| `close_location_value` | `CLV(cbind(high, low, close))` | 1e-12 |
| `accumulation_distribution_line` | `chaikinAD(cbind(high, low, close), volume)` | 1e-06 |
| `money_flow_index` | `MFI(cbind(high, low, close), volume, 14)` | 1e-09 |
| `williams_percent_r` | `WPR(cbind(high, low, close), 14) * -100` | 1e-09 |
| `stochastic_fast_k` | `stoch(cbind(high, low, close), 14, 3, 3, smooth = 1)[, "fastK"] * 100` | 1e-09 |
| `stochastic_fast_d` | `stoch(cbind(high, low, close), 14, 3, 3, smooth = 1)[, "fastD"] * 100` | 1e-09 |
| `stochastic_slow_d` | `stoch(cbind(high, low, close), 14, 3, 3, smooth = 1)[, "slowD"] * 100` | 1e-09 |
| `macd` | `MACD(close, 12, 26, 9, maType = "EMA", percent = FALSE)[, "macd"]` | 1e-09 |
| `bollinger_percent_b` | `BBands(close, n = 20, sd = 2)[, "pctB"]` | 1e-09 |
| `aroon_up` (periods=25) | `aroon(cbind(high, low), 24)[, "aroonUp"]` | 1e-09 |
| `aroon_down` (periods=25) | `aroon(cbind(high, low), 24)[, "aroonDn"]` | 1e-09 |
| `true_range` | `ATR(cbind(high, low, close), 14)[, "tr"]` | 1e-12 |

## Agreeing once the seed has decayed

4 entries. TTR leaves the first bar's true range undefined,
having no previous close, where this catalogue uses the plain high-low range and
says so. Wilder's recursion then forgets the difference geometrically.

| Factor | Apart at the first common bar | Within tolerance from bar |
|---|---:|---:|
| `atr` | 0.137 | 267 |
| `plus_di` | 0.73 | 288 |
| `minus_di` | 0.56 | 289 |
| `adx` | 0.84 | 308 |

## The traps

The call a reader reaches for first, when it is not the one that agrees. Each of
these is a default argument nobody thinks about.

### `rsi`

- agrees: `RSI(close, 14)`
- reached for: `RSI(close, 14, maType = "EMA")`
- apart by: 17.51

Asking for an exponential average gets the 2/(n+1) constant and a reading up to 17 points away from Wilder's. This is the disagreement the README describes, in the one package most likely to be the second opinion.

### `macd`

- agrees: `MACD(close, 12, 26, 9, maType = "EMA", percent = FALSE)[, "macd"]`
- reached for: `MACD(close, 12, 26, 9, maType = "EMA")`
- apart by: 0.77

TTR's `percent` defaults to TRUE, which divides the difference by the slow average. That is a ratio and this catalogue's entry is in currency, so the two are not comparable at all rather than merely different.

### `bollinger_percent_b`

- agrees: `BBands(close, n = 20, sd = 2)[, "pctB"]`
- reached for: `BBands(cbind(high, low, close), n = 20, sd = 2)[, "pctB"]`
- apart by: 0.31

Handed a high-low-close matrix, which is how every other TTR function in this file is called, BBands computes the bands on the typical price rather than on the close. Nothing in the call says so.

### `aroon_up`

- agrees: `aroon(cbind(high, low), 24)[, "aroonUp"]`
- reached for: `aroon(cbind(high, low), 25)[, "aroonUp"]`
- apart by: 100

Passing the same number to both is the obvious thing to do, and the two then measure over windows one bar apart. The median difference is 1 point, which looks like rounding, and the maximum is the whole scale: where the older window still holds the high and the newer one has just lost it, one reads 100 and the other 0. That happens on 1.3 percent of bars on the reference series, which is often enough to matter and rare enough to go unnoticed.

## Not compared

TTR has no function that computes these. The nearest thing it offers is named
anyway, because reaching for it as an equivalent is the mistake worth naming.

### `historical_volatility`

TTR has no function that computes this catalogue's entry. `volatility(calc = "close")` is 0.26 points away on the reference series, because it uses the close-to-close estimator, which does not subtract the mean return. Written out with runSD it agrees to 1e-13, but that is R arithmetic rather than a TTR function, so there is nothing here to hold TTR to.

- nearest in TTR: `volatility(close, n = 250, calc = "close", N = 250) * 100`
- apart by: 0.25
