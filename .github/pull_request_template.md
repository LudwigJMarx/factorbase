## What this changes

<!-- One or two sentences. The body of your commit already carries the argument. -->

## Evidence

<!--
For a fix or a new factor: the failing test before, and the passing test after.
Paste both runs. A test written after the fix passes for reasons nobody has
checked.
-->

```
before:

after:
```

## Checklist

- [ ] The failing test was written first, and both runs are pasted above
- [ ] The test recomputes the formula, not the code
- [ ] `pytest tests/ -W error::DeprecationWarning`
- [ ] `python3 scripts/check_catalog_wired.py`
- [ ] `python3 scripts/check_gates_wired.py`
- [ ] `ruff check`, `ruff format --check`, `mypy`

For a new or changed catalogue entry:

- [ ] The description says what the factor is **not**, and where implementations
      of it disagree
- [ ] Defaults that are this package's own choice say so
- [ ] `unit: index` only for a bounded oscillator, and the range is stated
- [ ] `references` names where the definition comes from

For a changed number:

- [ ] The pull request says what moves and by how much, at the first reading and
      once the difference has decayed
