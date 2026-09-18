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

CATALOGUE = ROOT / "docs" / "catalogue.md"
COMPARISON = ROOT / "docs" / "compared-with-ttr.md"
MAPPING = ROOT / "catalog" / "mappings" / "ttr.yaml"

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


def render_comparison(document: dict) -> str:
    """The TTR mapping as a table, because a YAML file is not read by anybody.

    Every number here comes from `catalog/mappings/ttr.yaml`, which the `ttr` CI
    job produces by running both sides. Nothing is computed at render time, so
    this document cannot claim an agreement the job has not confirmed.
    """
    mappings = document["mappings"]
    agreeing = [m for m in mappings if m["agreement"] == "identical"]
    converging = [m for m in mappings if m["agreement"] == "converges"]
    absent = [m for m in mappings if m["agreement"] == "not_compared"]
    # A not_compared entry has no agreeing call, so listing its trap beside the
    # others would print "agrees:" next to an expression that is not a TTR
    # function. Its trap belongs in its own section instead.
    traps = [m for m in mappings if m.get("trap") and m["agreement"] != "not_compared"]

    lines = [
        "# Compared with TTR",
        "",
        "The README claims that two packages hand you the same indicator name and",
        "disagree without saying why. This is the measurement behind that claim.",
        "",
        f"{len(mappings)} mappings against "
        f"[TTR](https://cran.r-project.org/package=TTR) "
        f"{document['measured_against']} on {document['measured_on']}, run against "
        f"`{document['series']}`.",
        "",
        "**This file is generated** from `catalog/mappings/ttr.yaml`, and every number in",
        "it was produced by the `ttr` job running both sides. The job fails if any of",
        "these statements stops being true, including the traps: a difference that",
        "quietly disappears is a note that reads as current and describes nothing.",
        "",
        "## Agreeing outright",
        "",
        f"{len(agreeing)} entries, within the stated tolerance over every bar where both",
        "are defined.",
        "",
        "| Factor | The R call that agrees | Within |",
        "|---|---|---|",
    ]
    for mapping in agreeing:
        arguments = mapping.get("arguments")
        factor = f"`{mapping['factor']}`"
        if arguments:
            shown = ", ".join(f"{k}={v!r}" for k, v in arguments.items())
            factor += f" ({shown})"
        lines.append(f"| {factor} | `{mapping['call']}` | {mapping['tolerance']:g} |")

    lines += [
        "",
        "## Agreeing once the seed has decayed",
        "",
        f"{len(converging)} entries. TTR leaves the first bar's true range undefined,",
        "having no previous close, where this catalogue uses the plain high-low range and",
        "says so. Wilder's recursion then forgets the difference geometrically.",
        "",
        "| Factor | Apart at the first common bar | Within tolerance from bar |",
        "|---|---:|---:|",
    ]
    for mapping in converging:
        lines.append(
            f"| `{mapping['factor']}` | {mapping['initial_difference']:g} | "
            f"{mapping['converged_by']} |"
        )

    lines += [
        "",
        "## The traps",
        "",
        "The call a reader reaches for first, when it is not the one that agrees. Each of",
        "these is a default argument nobody thinks about.",
        "",
    ]
    for mapping in traps:
        trap = mapping["trap"]
        lines.append(f"### `{mapping['factor']}`")
        lines.append("")
        lines.append(f"- agrees: `{mapping['call']}`")
        lines.append(f"- reached for: `{trap['call']}`")
        lines.append(f"- apart by: {trap['measured_difference']:g}")
        lines.append("")
        lines.extend(paragraphs(trap["note"]))

    if absent:
        lines += [
            "## Not compared",
            "",
            "TTR has no function that computes these. The nearest thing it offers is named",
            "anyway, because reaching for it as an equivalent is the mistake worth naming.",
            "",
        ]
        for mapping in absent:
            lines.append(f"### `{mapping['factor']}`")
            lines.append("")
            lines.extend(paragraphs(mapping["note"]))
            trap = mapping.get("trap")
            if trap:
                lines.append(f"- nearest in TTR: `{trap['call']}`")
                lines.append(f"- apart by: {trap['measured_difference']:g}")
                lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def compare(target: Path, rendered: str, write: bool) -> int:
    """Write or check one document. Returns the number of findings."""
    where = target.relative_to(ROOT)
    if write:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(rendered, encoding="utf-8")
        print(f"  wrote {where}, {rendered.count(chr(10))} lines")
        return 0

    if not target.is_file():
        print(f"  {where} does not exist; run with --write", file=sys.stderr)
        return 1

    committed = target.read_text(encoding="utf-8")
    if committed == rendered:
        print(f"  {where} is current")
        return 0

    import difflib

    diff = list(
        difflib.unified_diff(
            committed.splitlines(), rendered.splitlines(), "committed", "generated", lineterm=""
        )
    )
    print(f"\n  {where} is stale, {len(diff)} diff line(s):", file=sys.stderr)
    for line in diff[:30]:
        print(f"    {line}", file=sys.stderr)
    if len(diff) > 30:
        print(f"    ... and {len(diff) - 30} more", file=sys.stderr)
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--write", action="store_true", help="regenerate instead of checking")
    arguments = parser.parse_args()

    import yaml

    catalog = load_catalog(ROOT / "catalog")
    mapping = yaml.safe_load(MAPPING.read_text(encoding="utf-8"))

    print(
        f"check_docs_current: {len(catalog)} catalogue entries, "
        f"{len(mapping['mappings'])} TTR mappings, 2 document(s)"
    )
    findings = compare(CATALOGUE, render(catalog), arguments.write)
    findings += compare(COMPARISON, render_comparison(mapping), arguments.write)

    if findings:
        print("\n  Run: python3 scripts/check_docs_current.py --write", file=sys.stderr)
        return 1

    print("0 findings")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
