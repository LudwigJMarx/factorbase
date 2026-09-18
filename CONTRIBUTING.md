# Contributing

The catalogue is the deliverable. The code exists so that the catalogue can be
checked, which is why most of what follows is about what an entry has to say
rather than about how the code is written.

## Before anything else

```bash
python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"
.venv/bin/python -m pytest tests/ -W error::DeprecationWarning
.venv/bin/python scripts/check_catalog_wired.py
.venv/bin/python scripts/check_gates_wired.py
```

All three are gates in CI, along with ruff, mypy and a build of the SQLite
file. Two further jobs run there and not here: one installs the declared
dependency floor rather than the newest release, because a minimum nothing
exercises is a guess, and one installs R and holds the catalogue against TTR.

`scripts/check_against_ttr.py` needs R with TTR. Without it the script fails
rather than skipping, which is why it has its own job: a contributor without R
is not blocked from running everything else, and nothing passes by not having
run. If your change touches a factor that
[`catalog/mappings/ttr.yaml`](catalog/mappings/ttr.yaml) maps, expect that job
to have an opinion about it.

## Adding a factor

A factor is a YAML entry under `catalog/` and a function under
`src/factorbase/factors/`. Both, or neither. The entry needs:

| Field | What it has to be |
|---|---|
| `id` | lowercase snake_case, stable, never renamed after release |
| `summary` | one sentence |
| `description` | how it works, and what it is not. See below. |
| `formulas` | at least one, as LaTeX, for a reader rather than a renderer |
| `inputs` | names from [`catalog/inputs.yaml`](catalog/inputs.yaml) |
| `unit` | `index` only for a bounded oscillator, and then state the range |
| `direction` | `undefined` is a real answer, not a gap |
| `companions` | `benchmark` or `market` if a second series is required |
| `references` | where the definition comes from |
| `implementation` | `module:function`, checked by CI |

After changing any entry, regenerate the reference:

```bash
python3 scripts/check_docs_current.py --write
```

`docs/catalogue.md` is built from the YAML, never edited, and a CI gate fails
when the committed copy no longer matches.

**The description says what the factor is not.** Every entry here that is worth
reading twice does. Where two implementations of the same name disagree, say
which one this is: Wilder's 1/n against 2/(n+1), the sample deviation against
the population one, body against body rather than range against range. Where
the factor is routinely reached for to do something it does not do, say that
too - `adjusted_slope` has a paragraph on why it will not screen out gap risk,
with the arithmetic.

**State the defaults you chose.** Several entries carry a note saying the
defaults are this package's and not a quoted standard. That is better than
implying an authority that does not exist.

## Tests

**Write the failing test first, and run it.** Red before, green after, and
both runs go in the pull request. A test written after the fix passes for
reasons nobody has checked.

**A test recomputes the formula, never the code.** Comparing an implementation
to itself passes under any definition.

**At least one test per family compares against something written outside this
package.** The standard library, a published worked example, an accounting
identity, a series whose answer is known by construction. This rule is not
taste: four arithmetic defects once survived 279 tests because every test
recomputed them faithfully from the same wrong premise, and an outside
reference found all four in an afternoon. What does not count is a second call
to the function under test, and what counts least is a second call to its
helper.

**A claim in an entry gets a test, including the uncomfortable ones.** If the
test refuses the claim, the claim was wrong; fix the entry, not the test.

## Changing an existing factor

Changing a number people may already depend on needs the same evidence as a
new one, plus a statement of what moves and by how much. "Off by 1.76 points
at the first reading and 0.06 points forty-six bars later" is the useful form.

Renaming an `id` breaks every caller silently, because a screen configured
with the old name simply stops finding it. Add an alias instead.

## What will not be merged

- **A data source.** Prices and accounts come from wherever the caller already
  gets them, and the one integration point is the vocabulary in
  `catalog/inputs.yaml`. A package that also fetches has two reasons to break
  and needs credentials to test.
- **Portfolio construction or a backtester.** The catalogue stops at the factor
  value and the cross-sectional rank.
- **Forecast or estimate data.** Everything here is computed from what was
  reported. Estimates need a vintage and a point-in-time database.
- **A factor whose definition cannot be stated from published work.** An
  invented rule under a borrowed name is worse than an absent entry, because
  the absence is visible.

## Commits and pull requests

Conventional Commits: `type(scope): subject`, subject under 72 characters and
lowercase. The body is the contribution: what was claimed, what the evidence
shows, why this way and which obvious alternative does not work. Not a list of
changed files; that is the diff.

One concern per pull request. A reformatting bundled with a fix hides the fix.

## Rules this project works under

[ENGINEERING.md](ENGINEERING.md) carries them, each attached to the run that forced it.
A rule without an incident is an opinion, and that file has none of those.
Reading it is the fastest way to understand why the code looks as it does.
