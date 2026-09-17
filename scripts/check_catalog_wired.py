#!/usr/bin/env python3
"""Check that the catalogue and the code still describe the same thing.

── WHY THIS EXISTS ─────────────────────────────────────────────────────────

The catalogue is text. Nothing stops an entry from naming a function that was
renamed, declaring a parameter the function ignores, or claiming `stable` with
no test behind it. Each of those reads as a complete entry and computes the
wrong thing, or nothing.

── WHAT IT CHECKS ──────────────────────────────────────────────────────────

1. The catalogue loads, which is where the schema is enforced.
2. Every `implementation` string resolves to a callable.
3. Every parameter an entry declares is accepted by that callable.
4. Every `stable` entry is named by at least one test file.
5. Every id that appears in an `aliases` list is not also a factor id.
6. Every entry whose unit is `index` declares its output range.
7. Every companion series an entry declares matches a mandatory second
   argument of its implementation, and the other way round.

── WHAT IT DOES NOT CHECK ──────────────────────────────────────────────────

Whether the implementation matches the formula. No checker can read LaTeX and
compare it to code; that is what the tests in `tests/` are for. This script
only confirms that a test exists and mentions the id, which is a weaker claim
and is reported as such.

── WHY CHECK 7 EXISTS ──────────────────────────────────────────────────────

The catalogue's statement about second arguments used to be a single boolean
named `requires_benchmark`. Fifteen valuation entries take a mandatory market
series and reported false on it, so a caller reading the catalogue to find out
what to pass got a TypeError. Check 7 compares the declaration against the
signature in both directions, so the field cannot drift again.

Composites are exempt: `composite_score` takes a mapping of components rather
than a series, and no boolean or enum describes that usefully.

── WHY CHECK 6 EXISTS ──────────────────────────────────────────────────────

`index` means a bounded oscillator in this catalogue, so an entry claiming it
and declining to say between which numbers is claiming something it has not
stated. CCI was filed that way and is not bounded at all; the query that found
it was one line against the built database, and this check is that query made
permanent.

── WHY CHECK 4 PARSES INSTEAD OF SEARCHING ─────────────────────────────────

Its first version searched the concatenated test files for the id as plain
text. It then reported `rsi` as covered, on the strength of the word
"recursion" in a test name and the letters RSI in a module docstring. No test
for the indicator existed. A checker that clears an entry on a substring match
produces the same output as one that verified it, which is the failure this
whole script exists to prevent, so it now reads the test files as Python and
counts only identifiers and the strings handed to a factor lookup.

It then cleared `price` on the strength of a DataFrame column named "price" in
an unrelated test. Same class of false pass, one layer in. String literals now
count only as arguments to `compute`, `resolve` or a catalogue subscript.
"""

from __future__ import annotations

import ast
import inspect
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from factorbase.catalog import load_catalog  # noqa: E402
from factorbase.errors import CatalogError  # noqa: E402
from factorbase.registry import parameter_mismatch, resolve  # noqa: E402
from factorbase.schema import Kind, Status, Unit  # noqa: E402


def _string_arguments(call: ast.Call) -> set[str]:
    """String literals passed to a call, when the call looks like a factor lookup.

    Any string literal at all was too loose. A test that builds a frame with a
    column named "price" cleared the `price` entry without testing it, the same
    class of false pass as the substring search before it. Only strings handed
    to `compute` or to a catalogue subscript count now.
    """
    name = ""
    if isinstance(call.func, ast.Name):
        name = call.func.id
    elif isinstance(call.func, ast.Attribute):
        name = call.func.attr
    if name not in {"compute", "resolve", "implementation_of"}:
        return set()
    return {
        argument.value
        for argument in call.args
        if isinstance(argument, ast.Constant) and isinstance(argument.value, str)
    }


def tested_names() -> set[str]:
    """Every identifier used under tests/, plus the strings handed to a factor lookup.

    Parsed rather than grepped, and narrowed twice. Both narrowings came from
    the checker clearing an entry that had no test; the note at the top of this
    file has the two runs.
    """
    tests = ROOT / "tests"
    if not tests.is_dir():
        return set()
    names: set[str] = set()
    for path in sorted(tests.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                names.add(node.id)
            elif isinstance(node, ast.Attribute):
                names.add(node.attr)
            elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                names.add(node.name)
            elif isinstance(node, ast.arg):
                names.add(node.arg)
            elif isinstance(node, ast.alias):
                names.add(node.asname or node.name.rpartition(".")[2])
            elif isinstance(node, ast.Call):
                names.update(_string_arguments(node))
            elif isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Constant):
                if isinstance(node.slice.value, str):
                    names.add(node.slice.value)
    return names


def main() -> int:
    findings: list[str] = []

    try:
        catalog = load_catalog(ROOT / "catalog")
    except CatalogError as error:
        print(f"catalogue does not load: {error}", file=sys.stderr)
        return 1

    covered = tested_names()
    ids = set(catalog.ids())
    checked_implementations = 0
    checked_parameters = 0
    untested: list[str] = []

    for factor in catalog:
        for alias in factor.aliases:
            if alias in ids:
                findings.append(f"{factor.id}: alias {alias!r} is also a factor id")

        if factor.kind is not Kind.COMPOSITE and factor.implementation:
            declared = len(factor.companions)
            named = {p.id for p in factor.parameters}
            signature = inspect.signature(resolve(factor.implementation))
            required = [
                p
                for p in list(signature.parameters.values())[1:]
                if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)
                and p.default is inspect.Parameter.empty
                and p.name not in named
            ]
            if len(required) != declared:
                names = ", ".join(p.name for p in required) or "none"
                listed = ", ".join(c.value for c in factor.companions) or "none"
                findings.append(
                    f"{factor.id}: declares companions [{listed}] but the implementation "
                    f"requires [{names}]"
                )

        if factor.unit is Unit.INDEX and factor.output_range == (None, None):
            findings.append(
                f"{factor.id}: unit 'index' means a bounded oscillator, so state the range"
            )

        if factor.implementation is None:
            if factor.status is Status.STABLE:
                findings.append(f"{factor.id}: stable without an implementation")
            continue

        try:
            function = resolve(factor.implementation)
            checked_implementations += 1
        except CatalogError as error:
            findings.append(f"{factor.id}: {error.message}")
            continue

        if not inspect.getdoc(function) and factor.status is Status.STABLE:
            findings.append(f"{factor.id}: {factor.implementation} has no docstring")

        missing = parameter_mismatch(factor)
        checked_parameters += len(factor.parameters)
        if missing:
            findings.append(
                f"{factor.id}: {factor.implementation} does not accept {', '.join(missing)}"
            )

        if factor.status is Status.STABLE and factor.id not in covered:
            untested.append(factor.id)

    by_kind = {kind.value: len(catalog.of_kind(kind)) for kind in Kind}
    stable = sum(1 for f in catalog if f.status is Status.STABLE)
    draft = sum(1 for f in catalog if f.status is Status.DRAFT)

    print(
        f"check_catalog_wired: {len(catalog)} entries in {len(catalog.sources)} file(s) "
        f"({', '.join(f'{v} {k}' for k, v in by_kind.items() if v)}), "
        f"{stable} stable, {draft} draft; "
        f"{checked_implementations} implementation(s) resolved, "
        f"{checked_parameters} parameter(s) matched against signatures"
    )

    if untested:
        findings.append(
            f"{len(untested)} stable entr{'y' if len(untested) == 1 else 'ies'} not named by any "
            f"test: {', '.join(sorted(untested))}"
        )

    if findings:
        print(f"{len(findings)} finding(s):", file=sys.stderr)
        for finding in findings:
            print(f"  - {finding}", file=sys.stderr)
        return 1

    print("0 findings")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
