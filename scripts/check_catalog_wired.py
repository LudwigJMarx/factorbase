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
"""

from __future__ import annotations

import inspect
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from factorbase.catalog import load_catalog  # noqa: E402
from factorbase.errors import CatalogError  # noqa: E402
from factorbase.registry import parameter_mismatch, resolve  # noqa: E402
from factorbase.schema import Kind, Status  # noqa: E402


def test_corpus() -> str:
    """Everything under tests/, concatenated, lowercased."""
    tests = ROOT / "tests"
    if not tests.is_dir():
        return ""
    return "\n".join(p.read_text(encoding="utf-8") for p in tests.rglob("*.py")).lower()


def main() -> int:
    findings: list[str] = []

    try:
        catalog = load_catalog(ROOT / "catalog")
    except CatalogError as error:
        print(f"catalogue does not load: {error}", file=sys.stderr)
        return 1

    corpus = test_corpus()
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

        if factor.status is Status.STABLE and factor.id not in corpus:
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
