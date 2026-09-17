# factorbase

A catalogue of stock-screening factors. Every entry carries a written
definition, the formula it is defined by, the data it consumes, and a reference
implementation that is tested against the formula.

Three kinds of factor:

| Kind | What it eats | What it returns |
|---|---|---|
| `indicator` | price and volume history | a number per bar |
| `signal` | price and volume history | a boolean per bar |
| `fundamental` | reported accounts | a number per reporting period |
| `composite` | other factors' output | a rank or a score per instrument |

## Why it exists

Indicator libraries compute. They rarely say what they computed. Two packages
will both give you "RSI(14)" and disagree, because one smoothed with Wilder's
1/n and the other with a 2/(n+1) exponential average, and neither wrote it
down. The catalogue here states the choice for every factor, in the entry, next
to the formula, and the tests check the implementation against that statement
rather than against whatever the code happens to do.

## Bring your own data

There is no data source in this package and there will not be one. Prices and
accounts come from wherever you already get them. The one thing you do is map
your column names onto the vocabulary in [`catalog/inputs.yaml`](catalog/inputs.yaml),
once:

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

Ask a factor what it needs before you call it:

```python
from factorbase import default_catalog

factor = default_catalog()["bollinger_percent_b"]
factor.inputs            # ('close',)
factor.parameters        # periods=20, deviations=2.0
factor.formulas[0].latex
```

A missing column raises `MissingInputError` naming the column, and a history
shorter than the warm-up raises `InsufficientHistoryError` naming the shortfall.
Neither returns a column of NaN that looks like data.

## Reading the catalogue without Python

The YAML under `catalog/` is the source of truth and is meant to be read
directly. `scripts/build_db.py` renders it into a single SQLite file for
anyone who would rather query it:

```bash
python3 scripts/build_db.py --out factorbase.sqlite3
sqlite3 factorbase.sqlite3 "select id, name, unit from factor where family = 'momentum'"
```

The database is a build artefact. It is not committed, and editing it changes
nothing.

## Status

Early. The catalogue is being filled family by family; every entry is either
`stable`, meaning formula and tested implementation are both in place, or
`draft`, meaning the definition is written and the implementation is not. Draft
entries stay in the catalogue on purpose, so that what is missing is countable
instead of invisible.

```bash
python3 scripts/check_catalog_wired.py    # what is covered, what is not
```

## Licence

MIT. See [LICENSE](LICENSE).
