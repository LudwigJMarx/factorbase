#!/usr/bin/env python3
"""Self-test for `check_edgar_mapping.py`.

Each case breaks the mapping in one way and asserts the checker says so. A
checker nobody has watched fail is an assertion that it works, and the whole
argument for having it is that assertions are what this repository distrusts.

The last case is the one that earned the file: two concepts were written from
memory and neither appeared in any measurement. The checker now refuses that,
and this test refuses a checker that stops refusing it.
"""

from __future__ import annotations

import copy
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHECKER = HERE / "check_edgar_mapping.py"


def load():
    spec = importlib.util.spec_from_file_location("check_edgar_mapping", CHECKER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_the_real_files_pass(modul) -> None:
    mapping, inputs, evidence = modul.load()
    problems = modul.check(mapping, inputs, evidence)
    assert problems == [], problems


def test_a_field_dropped_from_the_mapping_is_a_problem(modul) -> None:
    """The quiet failure: a consumer finds nothing and reads it as "not reported"."""
    mapping, inputs, evidence = modul.load()
    mapping = copy.deepcopy(mapping)
    entfernt = mapping["fields"].pop(0)["field"]
    problems = modul.check(mapping, inputs, evidence)
    assert any(entfernt in p and "absent from the mapping" in p for p in problems), problems


def test_a_field_the_contract_does_not_have_is_a_problem(modul) -> None:
    mapping, inputs, evidence = modul.load()
    mapping = copy.deepcopy(mapping)
    mapping["fields"].append(
        {"field": "ebitda_margin", "unit": "USD", "concepts": ["Assets"], "note": "x"}
    )
    problems = modul.check(mapping, inputs, evidence)
    assert any("ebitda_margin" in p and "no such field" in p for p in problems), problems


def test_a_concept_nobody_measured_is_a_problem(modul) -> None:
    """The case this checker exists for.

    `CostOfGoodsSold` and `InterestExpenseNonoperating` were both written from
    memory into the first draft of the mapping. Measuring them changed the file:
    one turned out to be dead since 2017, the other to be the current tag for
    three filers, which reordered the entry it belongs to.
    """
    mapping, inputs, evidence = modul.load()
    mapping = copy.deepcopy(mapping)
    mapping["fields"][0]["concepts"].append("RevenuesNetOfInterestExpenseIMadeThisUp")
    problems = modul.check(mapping, inputs, evidence)
    assert any("appears in no measurement" in p for p in problems), problems


def test_an_entry_without_a_note_is_a_problem(modul) -> None:
    """The note is the deliverable. A bare tag name is what a reader already guessed."""
    mapping, inputs, evidence = modul.load()
    mapping = copy.deepcopy(mapping)
    mapping["fields"][0].pop("note")
    problems = modul.check(mapping, inputs, evidence)
    assert any("no note" in p for p in problems), problems


def test_a_limitation_about_a_filer_nobody_measured_is_a_problem(modul) -> None:
    mapping, inputs, evidence = modul.load()
    mapping = copy.deepcopy(mapping)
    mapping["unavailable"][0]["filers_affected"].append("NFLX")
    problems = modul.check(mapping, inputs, evidence)
    assert any("NFLX" in p and "never measured" in p for p in problems), problems


def test_a_derived_field_without_a_formula_is_a_problem(modul) -> None:
    mapping, inputs, evidence = modul.load()
    mapping = copy.deepcopy(mapping)
    mapping["derived"][0].pop("from")
    problems = modul.check(mapping, inputs, evidence)
    assert any("without saying from what" in p for p in problems), problems


def main() -> int:
    modul = load()
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for test in tests:
        try:
            test(modul)
        except AssertionError as problem:
            failed += 1
            print(f"FAIL {test.__name__}: {problem}")
        else:
            print(f"ok   {test.__name__}")
    print(f"\n{len(tests)} test(s), {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
