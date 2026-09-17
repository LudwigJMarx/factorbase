"""The `factorbase` command.

── WHY IT EXISTS ───────────────────────────────────────────────────────────

pyproject.toml declared this entry point before anything implemented it, so
every `pip install` produced a `factorbase` executable that raised ImportError
on its first run. The package's own suite never touched it, because the suite
imports from `src` and never looks at the installed shape.

The command is also the answer to a promise the README makes. It tells a
reader to build the SQLite file with `scripts/build_db.py`, and an installed
copy has no `scripts/` directory. `factorbase build-db` is the same thing from
a wheel.

── WHAT IT DOES NOT DO ─────────────────────────────────────────────────────

It does not compute anything. Feeding price data through a command line means
choosing a file format, a column mapping and a date parser, and all three are
decisions this package leaves to the caller on purpose. The command reads the
catalogue and renders it; computing is what the Python API is for.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from .catalog import Catalog, default_catalog
from .errors import UnknownFactorError
from .schema import Factor, Kind


def _list(catalog: Catalog, kind: str | None, family: str | None) -> int:
    factors = list(catalog)
    if kind:
        try:
            wanted = Kind(kind)
        except ValueError:
            allowed = ", ".join(member.value for member in Kind)
            print(f"unknown kind {kind!r}; expected one of {allowed}", file=sys.stderr)
            return 1
        factors = [f for f in factors if f.kind is wanted]
    if family:
        factors = [f for f in factors if f.family == family]

    for factor in factors:
        print(f"{factor.id:<38} {factor.kind.value:<12} {factor.family:<16} {factor.summary}")

    # The scope, not just the rows. A filter that matched nothing and a
    # catalogue that is empty otherwise print the same thing.
    scope = f"{len(factors)} of {len(catalog)} entries"
    if kind or family:
        narrowed = ", ".join(part for part in (kind, family) if part)
        scope += f" (narrowed by {narrowed})"
    print(scope)
    return 0


def _show(catalog: Catalog, factor_id: str) -> int:
    try:
        factor: Factor = catalog[factor_id]
    except UnknownFactorError as error:
        print(str(error), file=sys.stderr)
        return 1

    print(f"{factor.id}  -  {factor.name}")
    print(f"{factor.kind.value}, family {factor.family}, status {factor.status.value}")
    print(f"unit {factor.unit.value}, better when {factor.direction.value}")
    if factor.period.value != "not_applicable":
        print(f"reporting basis {factor.period.value}")
    low, high = factor.output_range
    if low is not None or high is not None:
        print(f"range {low} to {high}")
    for companion in factor.companions:
        print(f"needs a {companion.value} series alongside the frame")
    print()
    print(factor.summary)
    print()
    print(factor.description)
    if factor.formulas:
        print()
        for formula in factor.formulas:
            print(f"    {formula.latex}")
            if formula.note:
                print(f"      {formula.note}")
    if factor.parameters:
        print()
        print("parameters:")
        for parameter in factor.parameters:
            choices = f" one of {', '.join(parameter.choices)}" if parameter.choices else ""
            print(f"    {parameter.id} = {parameter.default!r} ({parameter.dtype}){choices}")
            print(f"        {parameter.description}")
    print()
    print(f"inputs: {', '.join(factor.inputs)}")
    if factor.implementation:
        print(f"implementation: {factor.implementation}")
    for citation in factor.references:
        print(f"reference: {citation}")
    if factor.notes:
        print()
        print(f"note: {factor.notes}")
    return 0


def _build_db(catalog: Catalog, out: Path) -> int:
    from .db import build

    written = build(out, catalog)
    print(f"wrote {out} ({out.stat().st_size:,} bytes)")
    for table, count in written.items():
        print(f"  {table:<14} {count:>5}")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="factorbase", description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)

    listing = commands.add_parser("list", help="list catalogue entries")
    listing.add_argument("--kind", help="indicator, signal, fundamental or composite")
    listing.add_argument("--family", help="restrict to one family")

    showing = commands.add_parser("show", help="print one entry in full")
    showing.add_argument("factor_id")

    building = commands.add_parser("build-db", help="render the catalogue to SQLite")
    building.add_argument("--out", type=Path, default=Path("factorbase.sqlite3"))

    arguments = parser.parse_args(argv)
    catalog = default_catalog()

    if arguments.command == "list":
        return _list(catalog, arguments.kind, arguments.family)
    if arguments.command == "show":
        return _show(catalog, arguments.factor_id)
    return _build_db(catalog, arguments.out)


if __name__ == "__main__":
    raise SystemExit(main())
