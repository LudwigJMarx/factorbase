# Engineering notes

Why this code looks the way it does. Every rule below is attached to the run
that forced it, because a rule without an incident is an opinion and this file
has none of those.

It covers the traps that bite **here** and which the source does not show.
General good practice is assumed, not repeated. Read it before changing
anything; it is the fastest way to understand decisions that look arbitrary
and are not.

[CONTRIBUTING.md](CONTRIBUTING.md) says what a change has to carry. This says
what the project has already learned.

## What this project is

A catalogue of screening factors. Each entry states its formula, the data it
consumes, its unit and which end of its scale is the good end, and names a
reference implementation that is tested against the formula rather than against
itself. The catalogue is the deliverable; the code exists to make the
catalogue checkable.

The decision everything else follows from: **the YAML under `catalog/` is the
source of truth.** The SQLite file, the docs and the registry are built from
it. Nothing is edited in two places, because two places drift and then nobody
knows which one the loader enforces.

## Rules that are not negotiable

### The trailing, annual and average readings of a ratio are parameters

Not separate entries. A catalogue with "return on equity", "return on equity
(TTM)" and "average return on equity" has three places to fix one formula and
will have two of them wrong within a year. Same for the reported line a growth
factor measures: one `growth` entry with an `item` parameter, not eight that
differ by a column name.

### A number that is undefined is NaN, never a plausible number

Price to earnings on a loss is negative and sorts below every profitable
company, so an ascending screen picks the largest losses first. Debt to equity
on negative equity, payout on a loss, PEG on negative growth, long-term debt
over negative working capital: all of them produce a number that ranks at the
attractive end for the opposite of the right reason. Each of those returns NaN
and says so in its entry.

Where the sign is genuinely information, it is kept. Net debt to EBITDA goes
negative for a company holding more cash than debt, and that is the answer.

### An exact-zero guard is not a zero guard

A margin that is 13.5 percent every year produces a sample deviation near
1e-15, because the values came out of arithmetic rather than a register. The
stability ratio then read 5.9e14 and that company won every ranking that
touched it. Anything below a relative floor counts as no dispersion at all and
yields NaN. `fundamentals/_common.py:dispersion_ratio` is where that lives, and
any new ratio of a level to a dispersion goes through it.

### A signal fires on the change, not on the state

"Price is above its average" is a filter. "Price crossed above its average
today" is a signal. Writing the first where the second belongs turns a handful
of entries a year into a position held permanently, and the backtest looks
excellent.

On 17.09.2026 `new_high`, `new_low` and `volume_peak` fired on every bar. The
code read `at_high & ~at_high.shift(1).fillna(False)`. In pandas 3 a boolean
Series shifted by one comes back as object dtype holding Python bools, and `~`
on that inverts the underlying integer: `~True` is -2, which is truthy. The
result was cast back to dtype bool at the end, so the return value looked
correct in every way except its contents. A monotone climb reported 61 new
highs in 61 bars.

`signals.py:_became` is the only place that does this now, the reason is
written above it, and the suite runs with `-W error::DeprecationWarning`
because pandas had been warning about exactly this for two commits.

### Bar size is relative to the instrument, never absolute

"A long candle" is not computable until a threshold is fixed, and a fixed
currency threshold finds only the volatile half of any universe. Every such
rule measures against the instrument's own recent bars, and the reference
average excludes the current bar so that a long bar is not measured against
itself.

### A restated period is refused, not resolved

Two rows with the same period end on the same basis are an original filing and
its amendment, and nothing in the frame says which is the truth. Picking one
would decide for the caller. Quarterly and TTM rows share their period ends by
design and that is fine, because they are different bases; a repeat inside one
basis raises `AmbiguousPeriodError` naming the basis and the date.

It used to surface as "cannot reindex on an axis with duplicate labels" from
inside pandas, with no date and no factor name, and only from the two entries
that happened to reach a reindex.

## Checkers

These four are not project-specific. They are expensive lessons and they hold
everywhere.

**A checker nobody calls is a file.** An entry in `pyproject.toml` that no
workflow starts runs as often as no entry. `scripts/check_gates_wired.py`
tracks that and is the first step in `.github/workflows/checks.yml`.

**A checker says what it looked at.** "0 findings" is also what one prints that
searched the wrong directory. Every output names its scope: *180 entries in 15
files, 180 implementations resolved, 320 parameters matched*.

**Acting and checking are two steps.** Whoever rewrites something and reports
in the same breath that it was rewritten has checked themselves.

**An exemption is named, not hidden.** `@not-in-ci <reason>` in the file's
header, and it appears in the checker's output.

### The two checkers here

`check_gates_wired.py` confirms every checker is called. It does not look at
what they check.

`check_catalog_wired.py` confirms the catalogue and the code still describe the
same thing: every implementation resolves, every declared parameter is accepted
by its function, every stable entry is named by a test, every `index` unit
declares its range. It explicitly does **not** check that an implementation
matches its formula. No checker can read LaTeX. That is what `tests/` is for,
and the script says so in its own header rather than letting a green line imply
more than it verified.

### This checker cleared entries that had no test, twice

First it searched the concatenated test files as text, and cleared `rsi` on the
strength of the letters inside the word "recursion" plus some prose in a
docstring. Then, parsing properly but counting every string literal, it cleared
`price` because an unrelated test built a frame with a column of that name.

Both are the same failure, one layer apart: a checker that clears an entry on a
coincidence produces the same output as one that verified it. String literals
now count only as arguments to `compute`, `resolve` or a catalogue subscript.
Any further narrowing goes the same way, with the run that forced it written
into the file.

## Tests

**A test recomputes the formula, never the code.** Comparing an implementation
to itself passes under any definition. The tests here recompute from the LaTeX
in the entry, in a loop, or use a series whose answer is known by construction:
beta against a copy geared exactly two to one, RSI on an unbroken advance, a
company compounding at exactly 10 percent a year.

**At least one test per family compares against something written outside
this package.** A test that recomputes the formula using the same helper the
implementation uses cannot detect a wrong helper: both halves are wrong
together and the suite is green.

On 18.09.2026 a review checked the catalogue against published worked examples
and independently written references. It found four arithmetic defects that
279 tests had not: the Wilder seed placed a bar early whenever its input began
with a missing value, a fabricated zero in the first bar's directional
movement that biased every DI reading by 1.76 points at the start and 0.06
points forty-six bars later, Aroon reading the earliest of several tied
extremes instead of the latest, and a benchmark join that discarded every
market bar falling on a day the instrument did not trade. Each of the four was
recomputed faithfully by its own test, from the same wrong premise.

The outside reference does not have to be another library. Wilder's published
example series, a company constructed to compound at exactly 10 percent, a
copy geared exactly two to one: any of those is outside the code. What does
not count is a second call to the function under test, and what counts least
is a second call to its helper.

**A claim in an entry gets a test, including the uncomfortable ones.** The
adjusted-slope entry first claimed an even climb and a single gap to the same
level share a fitted slope. The test written from that sentence failed, and the
arithmetic showed the sentence was wrong: the step fits a steeper line and wins
even after the R-squared penalty. The entry now states that, because somebody
will otherwise reach for the factor to screen out gap risk and get the opposite.

**A fixture is part of the test, and can silently be the whole of it.** The
shared price fixture put high and low the same distance either side of the
close. Close location value is therefore identically zero on it, the
accumulation line is a flat 1e-7, and every test built on where the close sits
inside its bar compared a constant to a constant. It surfaced only because one
test asserted two accumulation lines from different start points must differ,
and they did not. Bars are now built around the open and the close with unequal
wicks.

**A stand-in moves the risk into the seam.** `check_gates_wired.test.py` drives
the pure decision with made-up inputs and then runs the whole script against a
real directory, because the first block cannot see file discovery, workflow
reading or the exit code.

**Patterns are tested on constructed bars.** A candlestick pattern that fires
eleven times in four hundred random bars says nothing about whether it fired
for the right reason.

## Commands

```bash
python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"

.venv/bin/python -m pytest tests/ -W error::DeprecationWarning
.venv/bin/python scripts/check_catalog_wired.py   # catalogue against code
.venv/bin/python scripts/check_gates_wired.py     # does CI call every checker?
.venv/bin/python scripts/build_db.py --out factorbase.sqlite3
.venv/bin/python -m ruff check src tests scripts && .venv/bin/python -m mypy
```

## What a checkout cannot show

Three of the four defects in the second review were invisible from this
directory, because everything here imports from `src` and runs from the
repository root. They appeared the moment the package was built into a wheel
and installed into an empty interpreter: an entry point naming a module nobody
had written, entries that crashed on the input shape the data contract
promises, and a dependency floor that had never been exercised.

So the last check before a release is not a test run. It is:

```bash
python3 -m build --wheel
python3 -m venv /tmp/fresh && /tmp/fresh/bin/pip install dist/*.whl
/tmp/fresh/bin/factorbase list | tail -1
/tmp/fresh/bin/python -c "import factorbase; print(len(factorbase.default_catalog()))"
```

The floor is now a CI job rather than a claim in pyproject. A declared minimum
that nothing installs is a guess, and pip resolves to the newest release every
time.

## Naming

`factorbase.factors` holds the implementations, not `factorbase.compute`.
`compute` is the top-level function, and a subpackage of the same name shadows
it the moment anything imports from it: `compute("sma", frame)` raised
TypeError as soon as a second family was imported in the same process. The
collision is invisible with one family in the tree, which is the argument for
adding the second one early.

## What is not built

**No data source, ever.** Prices and accounts come from wherever the caller
already gets them. The one integration point is the vocabulary in
`catalog/inputs.yaml`. A package that also fetches data has two reasons to
break and needs credentials to test.

**No portfolio construction, no backtester.** The catalogue stops at the
factor value and the cross-sectional rank. What to do with them is a strategy,
and a strategy in a reference library is a strategy nobody can disagree with.

**No forecast data.** Every entry here is computed from what was reported. The
moment estimates enter, every number needs a vintage and a point-in-time
database, and this is not that.

**No entry without a public definition.** A factor whose rule cannot be stated
from published work does not go in with an invented rule under a borrowed name.
It stays out and is listed as a gap.
