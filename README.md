# factorbase

A catalogue of stock-screening factors. Every entry carries a written
definition, the formula it is defined by, the data it consumes, and a reference
implementation that is tested against the formula.

180 entries, in four kinds:

| Kind | What it consumes | What it returns | Count |
|---|---|---|---:|
| `indicator` | price and volume history | a number per bar | 70 |
| `signal` | price and volume history | a boolean per bar | 51 |
| `fundamental` | reported accounts | a number per reporting period | 53 |
| `composite` | other factors' output, across a universe | a rank or a score per instrument | 6 |

By family:

| Kind | Families |
|---|---|
| indicator | momentum (16), volatility (12), trend (10), performance (9), relative (9), moving average (7), volume (7) |
| signal | candlestick (24), crossing (12), breakout (8), volume event (5), structure (2) |
| fundamental | valuation (14), profitability (13), leverage (9), growth (7), size (5), liquidity (3), distress (2) |
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
factor.formulas[0].latex
```

A missing column raises `MissingInputError` naming the column. A history
shorter than the warm-up raises `InsufficientHistoryError` naming the
shortfall. A benchmark that does not overlap the prices raises rather than
producing a column of NaN, because a NaN column looks like a quiet instrument
and is a wiring mistake.

## Reading the catalogue without Python

The YAML under `catalog/` is the source of truth and is meant to be read
directly. `scripts/build_db.py` renders it into a single SQLite file for
anyone who would rather ask a question:

```bash
python3 scripts/build_db.py --out factorbase.sqlite3
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
```

[AGENTS.md](AGENTS.md) has the rules this project works under, each one
attached to the run that forced it.

## Licence

MIT. See [LICENSE](LICENSE).
