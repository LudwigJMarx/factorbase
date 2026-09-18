# factorbase

[![Checks](https://github.com/LudwigJMarx/factorbase/actions/workflows/checks.yml/badge.svg)](https://github.com/LudwigJMarx/factorbase/actions/workflows/checks.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/downloads/)
[![Licence: MIT](https://img.shields.io/badge/licence-MIT-green)](LICENSE)

A catalogue of stock-screening factors. Every entry carries a written
definition, the formula it is defined by, the data it consumes, and a reference
implementation that is tested against the formula.

192 entries, in four kinds:

| Kind | What it consumes | What it returns | Count |
|---|---|---|---:|
| `indicator` | price and volume history | a number per bar | 74 |
| `signal` | price and volume history | a boolean per bar | 57 |
| `fundamental` | reported accounts | a number per reporting period | 55 |
| `composite` | other factors' output, across a universe | a rank or a score per instrument | 6 |

By family:

| Kind | Families |
|---|---|
| indicator | momentum (16), volatility (12), trend (11), performance (9), relative (9), volume (8), moving average (7), seasonality (2) |
| signal | candlestick (24), crossing (15), breakout (10), volume event (6), structure (2) |
| fundamental | valuation (15), profitability (13), leverage (10), growth (7), size (5), liquidity (3), distress (2) |
| composite | ranking (6) |

## Why it exists

Indicator libraries compute. They rarely say what they computed. Two packages
will both hand you "RSI(14)" and disagree, because one smoothed with Wilder's
1/n and the other with a 2/(n+1) exponential average, and neither wrote it
down. Every such choice here is stated in the entry, next to the formula, and
the tests check the implementation against that statement rather than against
whatever the code happens to do.

A few of the things the entries say out loud:

- ATR smooths with 1/n; historical volatility uses the sample deviation;
  the Bollinger spread uses the population deviation. Those three sit in one
  file and disagree on purpose.
- CCI takes the mean absolute deviation, not the standard deviation. The
  substitute produces a plausible series that is not CCI.
- Blau's double smoothed stochastic smooths numerator and denominator before
  dividing. Smoothing the quotient instead is a different indicator.
- Engulfing patterns compare body against body. Comparing highs and lows admits
  a different formation.
- Price to earnings returns NaN on a loss rather than a negative number, which
  would sort below every profitable company.
- `adjusted_slope` does **not** filter out gap risk. A single step inside the
  window fits a steeper line than an even climb to the same level, by more than
  the R-squared penalty takes away. The entry shows the arithmetic.

## Measured against R's TTR

The claim above, that two packages disagree without saying why, is not left as
an argument. [`catalog/mappings/ttr.yaml`](catalog/mappings/ttr.yaml) holds 23
mappings against [TTR](https://cran.r-project.org/package=TTR), and a CI job
installs R, runs both sides on a committed price series and fails if any of
them stops being true.

Eighteen agree to floating-point noise. Four more agree once Wilder's seed has
decayed: TTR leaves the first bar's true range undefined and this catalogue
uses the plain high-low range there, so ATR opens 0.137 apart and is within
1e-9 from bar 267.

The useful half is the traps: the call a reader reaches for first, when it is
not the one that agrees.

| Factor | What agrees | What a reader reaches for | Apart by |
|---|---|---|---:|
| `rsi` | `RSI(close, 14)` | `RSI(close, 14, maType = "EMA")` | 17.5 points |
| `bollinger_percent_b` | `BBands(close, 20, sd = 2)` | `BBands(cbind(high, low, close), ...)` | 0.31 |
| `macd` | `MACD(..., percent = FALSE)` | `MACD(...)` | not comparable |
| `aroon_up` | `aroon(hl, 24)` against `periods=25` | `aroon(hl, 25)` | up to 100 points |

TTR's RSI default turns out to **be** Wilder's smoothing, which is the opposite
of what this file's author assumed before running it. `BBands` handed a
high-low-close matrix computes on the typical price and nothing in the call
says so. `MACD` returns a percentage unless told otherwise. `aroon` counts the
lookback interval where this catalogue counts the window, and passing the same
number to both is off by a bar: usually one point, and on 1.3 percent of bars
the difference between 100 and 0.

The traps are checked in both directions. If a difference this file describes
ever disappears, the job fails, because a note that reads as current and
describes something that no longer happens is worse than no note.

The table above in full, with the traps and the convergence figures, is in
[`docs/compared-with-ttr.md`](docs/compared-with-ttr.md).

```bash
python3 scripts/check_against_ttr.py    # needs R with TTR
```

## Bring your own data

There is no data source in this package and there will not be one. Prices and
accounts come from wherever you already get them. The one thing you do is map
your column names onto the vocabulary in
[`catalog/inputs.yaml`](catalog/inputs.yaml), once.

```python
import pandas as pd
from factorbase import compute

prices = pd.DataFrame(
    {"open": ..., "high": ..., "low": ..., "close": ..., "volume": ...},
    index=pd.DatetimeIndex([...], name="date"),
)

rsi = compute("rsi", prices)                 # catalogue defaults
rsi_5 = compute("rsi", prices, periods=5)    # overridden
```

Fundamentals take one frame per instrument, indexed by period end, with a
`period` column saying which basis each row is on. Every factor selects the
basis it needs rather than assuming you filtered first:

```python
from factorbase import compute

roe = compute("return_on_equity", accounts)                  # annual
roe_ttm = compute("return_on_equity", accounts, period="ttm")
pe = compute("price_to_earnings", accounts, market_cap)      # market series too
```

Cross-sectional factors take one value per instrument at one date:

```python
from factorbase.factors.ranking import composite_score

score = composite_score(
    {"value": earnings_yields, "quality": returns_on_capital},
    weights={"value": 0.6, "quality": 0.4},
    directions={"value": "higher", "quality": "higher"},
)
```

Ask a factor what it needs before you call it:

```python
from factorbase import default_catalog

factor = default_catalog()["bollinger_percent_b"]
factor.inputs            # ('close',)
factor.parameters        # periods=20, deviations=2.0
factor.direction         # which end is the good end, when ranking
factor.companions        # () - no second series needed
factor.formulas[0].latex

default_catalog()["price_to_earnings"].companions   # (Companion.MARKET,)
default_catalog()["beta"].companions                # (Companion.BENCHMARK,)
```

`companions` is the catalogue's answer to "what else do I pass". Eight entries
need a benchmark price series, fifteen need a market-capitalisation series, and
a checker holds the field to the implementations' signatures in both
directions.

Or from a shell, without writing any Python:

```bash
factorbase list --kind fundamental --family valuation
factorbase show rsi
factorbase build-db --out factorbase.sqlite3
```

A missing column raises `MissingInputError` naming the column. A history
shorter than the warm-up raises `InsufficientHistoryError` naming the
shortfall. A benchmark that does not overlap the prices raises rather than
producing a column of NaN, because a NaN column looks like a quiet instrument
and is a wiring mistake.

## Reading the catalogue

[`docs/catalogue.md`](docs/catalogue.md) is every entry in one file, with its
formula, its parameters and what it consumes.
[`docs/compared-with-ttr.md`](docs/compared-with-ttr.md) is the measurement
behind the claim above, as a table.

Both are generated from the YAML, and a CI gate fails when either drifts apart
from it, so neither can quietly go stale.

## Reading the catalogue without Python

The YAML under `catalog/` is the source of truth and is meant to be read
directly. `scripts/build_db.py` renders it into a single SQLite file for
anyone who would rather ask a question:

```bash
factorbase build-db --out factorbase.sqlite3          # from an installed copy
python3 scripts/build_db.py --out factorbase.sqlite3  # from a checkout

sqlite3 factorbase.sqlite3 "select id, name, unit from factor where family = 'momentum'"
sqlite3 factorbase.sqlite3 "select count(*) from factor_input where field = 'volume'"
```

That second kind of query earned its keep on the first run: one line found an
entry claiming a bounded range and declining to state it, and it is now a
permanent check.

The database is a build artefact. It is not committed, and editing it changes
nothing.

## What is not here

- **No data source.** Ever. See above.
- **No portfolio construction and no backtester.** The catalogue stops at the
  factor value and the cross-sectional rank.
- **No forecast or estimate data.** Everything is computed from what was
  reported. Estimates need a vintage and a point-in-time database, and this is
  not that.
- **No factor whose definition cannot be stated from published work.** A rule
  that has to be invented does not go in under a borrowed name.

## Development

```bash
python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"
.venv/bin/python -m pytest tests/ -W error::DeprecationWarning
.venv/bin/python scripts/check_catalog_wired.py
.venv/bin/python scripts/check_docs_current.py --write   # after changing an entry
```

[CONTRIBUTING.md](CONTRIBUTING.md) says what an entry has to state and what
evidence a change needs. [ENGINEERING.md](ENGINEERING.md) has the rules this project
works under, each one attached to the run that forced it.

## Licence

MIT. See [LICENSE](LICENSE).
