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

── WHAT IT DOES NOT CHECK ──────────────────────────────────────────────────

Whether the implementation matches the formula. No checker can read LaTeX and
compare it to code; that is what the tests in `tests/` are for. This script
only confirms that a test exists and mentions the id, which is a weaker claim
and is reported as such.

── WHY CHECK 4 PARSES INSTEAD OF SEARCHING ─────────────────────────────────

Its first version searched the concatenated test files for the id as plain
text. It then reported `rsi` as covered, on the strength of the word
"recursion" in a test name and the letters RSI in a module docstring. No test
for the indicator existed. A checker that clears an entry on a substring match
produces the same output as one that verified it, which is the failure this
whole script exists to prevent, so it now reads the test files as Python and
counts only identifiers and non-docstring string literals.
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
from factorbase.schema import Kind, Status  # noqa: E402


def _docstring_nodes(tree: ast.AST) -> set[int]:
    """Object ids of the string constants that are docstrings.

    Prose in a docstring is not a reference to a factor. Excluding it is what
    stops "the right RSI for a particular Tuesday" from counting as a test.
    """
    found: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            body = getattr(node, "body", [])
            if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
                if isinstance(body[0].value.value, str):
                    found.add(id(body[0].value))
    return found


def tested_names() -> set[str]:
    """Every identifier and non-docstring string literal used under tests/.

    Parsed rather than grepped. A substring search over the raw text reports an
    entry as covered when its id happens to occur inside an unrelated word; see
    the note at the top of this file for the run where that actually happened.
    """
    tests = ROOT / "tests"
    if not tests.is_dir():
        return set()
    names: set[str] = set()
    for path in sorted(tests.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        docstrings = _docstring_nodes(tree)
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
            elif isinstance(node, ast.Constant) and isinstance(node.value, str):
                if id(node) not in docstrings:
                    names.add(node.value)
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
