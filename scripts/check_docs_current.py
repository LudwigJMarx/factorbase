#!/usr/bin/env python3
"""Render the catalogue to docs/ and confirm the committed copy still matches.

── WHY IT IS GENERATED ─────────────────────────────────────────────────────

A reference of 192 entries maintained by hand is a reference that is wrong. The
YAML is the source of truth, so the prose version is built from it and checked
rather than edited: `--write` regenerates, and the default compares and fails
on any difference. That makes a stale document a red build instead of a thing
somebody notices a year later.

── WHY IT IS A CHECKER AND NOT A BUILD SCRIPT ──────────────────────────────

Because the failure it prevents is silent. `build_db.py` produces an artefact
nobody commits, so it cannot go stale. This one produces a file that is
committed and read, and a committed file that no longer matches its source is
exactly the sort of quiet wrongness the rest of this repository is built to
catch.

Usage:  python3 scripts/check_docs_current.py [--write]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from factorbase.catalog import Catalog, load_catalog  # noqa: E402
from factorbase.schema import Factor, Kind  # noqa: E402

TARGET = ROOT / "docs" / "catalogue.md"

KIND_TITLES = {
    Kind.INDICATOR: "Indicators",
    Kind.SIGNAL: "Signals",
    Kind.FUNDAMENTAL: "Fundamentals",
    Kind.COMPOSITE: "Composites",
}

KIND_BLURBS = {
    Kind.INDICATOR: "A number per bar, from price and volume history.",
    Kind.SIGNAL: "A boolean per bar, from price and volume history.",
    Kind.FUNDAMENTAL: "A number per reporting period, from the reported accounts.",
    Kind.COMPOSITE: "A rank or a score per instrument, across a universe at one date.",
}


def anchor(heading: str) -> str:
    """GitHub's own slug rule, applied to a heading.

    Lowercase, drop everything that is not a letter, digit, space, hyphen or
    underscore, then turn spaces into hyphens. Underscores survive, which is
    the part that matters here: an id like `rate_of_change` keeps them, and a
    generator that helpfully converts them produces links that go nowhere.
    """
    kept = re.sub(r"[^\w\s-]", "", heading.lower(), flags=re.UNICODE)
    return re.sub(r"\s+", "-", kept.strip())


def heading_for(factor: Factor) -> str:
    return f"`{factor.id}` - {factor.name}"


def paragraphs(text: str) -> list[str]:
    """Split a folded YAML block back into paragraphs.

    A folded scalar keeps a blank line between paragraphs and collapses every
    other newline into a space. Emitting the string as-is gives markdown one
    paragraph where the entry meant several, so the blank lines are restored
    explicitly rather than trusted to survive the join.
    """
    out: list[str] = []
    for block in text.strip().split("\n\n"):
        collapsed = " ".join(block.split())
        if collapsed:
            out.extend([collapsed, ""])
    return out


def render_factor(factor: Factor) -> list[str]:
    lines = [f"#### {heading_for(factor)}", ""]
    lines.append(f"{factor.summary}")
    lines.append("")

    facts = [f"unit `{factor.unit.value}`", f"better when `{factor.direction.value}`"]
    if factor.period.value != "not_applicable":
        facts.append(f"basis `{factor.period.value}`")
    low, high = factor.output_range
    if low is not None or high is not None:
        facts.append(f"range {low} to {high}")
    for companion in factor.companions:
        facts.append(f"needs a `{companion.value}` series")
    if factor.aliases:
        facts.append("also known as " + ", ".join(f"`{a}`" for a in factor.aliases))
    lines.append(" · ".join(facts))
    lines.append("")

    lines.extend(paragraphs(factor.description))

    if factor.formulas:
        for formula in factor.formulas:
            lines.append("```latex")
            lines.append(formula.latex)
            lines.append("```")
            if formula.note:
                lines.extend(paragraphs(formula.note))
            else:
                lines.append("")

    if factor.parameters:
        lines.append("| Parameter | Default | Type | What it does |")
        lines.append("|---|---|---|---|")
        for parameter in factor.parameters:
            choices = ""
            if parameter.choices:
                choices = " One of " + ", ".join(f"`{c}`" for c in parameter.choices) + "."
            description = " ".join(parameter.description.split())
            lines.append(
                f"| `{parameter.id}` | `{parameter.default!r}` | {parameter.dtype} | "
                f"{description}{choices} |"
            )
        lines.append("")

    lines.append(f"Consumes: {', '.join(f'`{i}`' for i in factor.inputs)}")
    lines.append("")
    if factor.implementation:
        lines.append(f"Implemented by `{factor.implementation}`")
        lines.append("")
    if factor.notes:
        note = paragraphs(factor.notes)
        note[0] = f"**Note.** {note[0]}"
        lines.extend(note)
    for citation in factor.references:
        lines.append(f"Reference: {citation}")
    if factor.references:
        lines.append("")
    return lines


def render(catalog: Catalog) -> str:
    lines = [
        "# The catalogue",
        "",
        "Every entry, with the formula it is defined by, the data it consumes and the",
        "implementation it is tested against.",
        "",
        "**This file is generated.** `catalog/*.yaml` is the source of truth and this is",
        "built from it by `scripts/check_docs_current.py`, which also fails the build when",
        "the two drift apart. Editing it here changes nothing.",
        "",
        f"{len(catalog)} entries.",
        "",
        "## Index",
        "",
    ]

    for kind in (Kind.INDICATOR, Kind.SIGNAL, Kind.FUNDAMENTAL, Kind.COMPOSITE):
        factors = catalog.of_kind(kind)
        if not factors:
            continue
        lines.append(f"**{KIND_TITLES[kind]}** ({len(factors)})")
        lines.append("")
        for family in sorted({f.family for f in factors}):
            in_family = [f for f in factors if f.family == family]
            links = ", ".join(f"[`{f.id}`](#{anchor(heading_for(f))})" for f in in_family)
            lines.append(f"- *{family.replace('_', ' ')}*: {links}")
        lines.append("")

    for kind in (Kind.INDICATOR, Kind.SIGNAL, Kind.FUNDAMENTAL, Kind.COMPOSITE):
        factors = catalog.of_kind(kind)
        if not factors:
            continue
        lines.append(f"## {KIND_TITLES[kind]}")
        lines.append("")
        lines.append(KIND_BLURBS[kind])
        lines.append("")
        for family in sorted({f.family for f in factors}):
            in_family = [f for f in factors if f.family == family]
            lines.append(f"### {family.replace('_', ' ').title()}")
            lines.append("")
            for factor in in_family:
                lines.extend(render_factor(factor))

    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--write", action="store_true", help="regenerate instead of checking")
    arguments = parser.parse_args()

    catalog = load_catalog(ROOT / "catalog")
    rendered = render(catalog)

    if arguments.write:
        TARGET.parent.mkdir(parents=True, exist_ok=True)
        TARGET.write_text(rendered, encoding="utf-8")
        where = TARGET.relative_to(ROOT)
        print(
            f"check_docs_current: wrote {where}, {len(catalog)} entries, "
            f"{rendered.count(chr(10))} lines"
        )
        return 0

    if not TARGET.is_file():
        print(f"check_docs_current: {TARGET.relative_to(ROOT)} does not exist.", file=sys.stderr)
        print("  Run with --write to generate it.", file=sys.stderr)
        return 1

    committed = TARGET.read_text(encoding="utf-8")
    print(
        f"check_docs_current: compared {TARGET.relative_to(ROOT)} against "
        f"{len(catalog)} catalogue entries"
    )
    if committed != rendered:
        import difflib

        diff = list(
            difflib.unified_diff(
                committed.splitlines(), rendered.splitlines(), "committed", "generated", lineterm=""
            )
        )
        print(f"\nthe committed copy is stale, {len(diff)} diff line(s):", file=sys.stderr)
        for line in diff[:40]:
            print(f"  {line}", file=sys.stderr)
        if len(diff) > 40:
            print(f"  ... and {len(diff) - 40} more", file=sys.stderr)
        print("\n  Run: python3 scripts/check_docs_current.py --write", file=sys.stderr)
        return 1

    print("0 findings")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
