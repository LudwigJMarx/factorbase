#!/usr/bin/env python3
"""Hold `catalog/mappings/edgar.yaml` against the data contract and the evidence.

── WHY THIS IS A GATE AND NOT A README ─────────────────────────────────────

A mapping table is the easiest thing in this repository to get wrong without
anybody noticing. Nothing imports it, no test computes with it, and a tag that
was renamed in the taxonomy reads exactly like one that was never right. The
same argument produced `check_against_ttr.py`, and it applies harder here,
because the TTR comparison at least runs both sides.

So this checks three things that can be checked without a network:

1. Every field the mapping names is a field the data contract has, and every
   field the contract has is either mapped or derived. A field that quietly
   falls out of the table is the failure mode: the consumer finds nothing for
   it and concludes the company does not report it.

2. Every concept the mapping names appears in `tests/data/edgar_coverage.json`,
   which holds what was actually found in filings. This is the rule that caught
   two tags written from memory: `CostOfGoodsSold`, which no measured filer has
   used since 2017, and `InterestExpenseNonoperating`, which turned out to be
   the current tag for three filers and reordered the entry.

3. Every filer named in an `unavailable` entry was actually measured, and the
   inputs it names exist. Otherwise the file can claim a limitation nobody
   checked.

── WHAT IT CANNOT CHECK ────────────────────────────────────────────────────

Whether the mapping is still true today. Filers change tags, and the taxonomy
changes under them. That needs a request to data.sec.gov, which needs a
declared contact under the SEC's fair-access policy and does not belong in a
CI job. `scripts/check_edgar_drift.py` does it on demand, and this file's
`measured_on` is how a reader knows how old the answer is.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
MAPPING = ROOT / "catalog" / "mappings" / "edgar.yaml"
INPUTS = ROOT / "catalog" / "inputs.yaml"


def load() -> tuple[dict, dict, dict]:
    mapping = yaml.safe_load(MAPPING.read_text(encoding="utf-8"))
    inputs = yaml.safe_load(INPUTS.read_text(encoding="utf-8"))
    evidence = json.loads((ROOT / mapping["evidence"]).read_text(encoding="utf-8"))
    return mapping, inputs, evidence


def check(mapping: dict, inputs: dict, evidence: dict) -> list[str]:
    problems: list[str] = []

    # `period` is the key of a reporting period, not a reported figure.
    contract = set(inputs["fundamental"]["fields"]) - {"period"}
    mapped = {entry["field"] for entry in mapping["fields"]}
    derived = {entry["field"] for entry in mapping["derived"]}

    for field in sorted(contract - mapped - derived):
        problems.append(f"{field}: in the data contract, absent from the mapping")
    for field in sorted((mapped | derived) - contract):
        problems.append(f"{field}: mapped, but no such field in the data contract")
    for field in sorted(mapped & derived):
        problems.append(f"{field}: both mapped to a concept and declared derived")

    measured_tags = {
        tag["tag"]
        for per_filer in evidence["fields"].values()
        for rows in per_filer.values()
        for tag in rows
    }
    for entry in mapping["fields"]:
        named = list(entry["concepts"]) + list(entry.get("historical", ()))
        if not named:
            problems.append(f"{entry['field']}: names no concept at all")
        for concept in named:
            if concept not in measured_tags:
                problems.append(
                    f"{entry['field']}: {concept} is named but appears in no measurement"
                )
        if not entry.get("note"):
            problems.append(f"{entry['field']}: no note saying what a reader has to watch")
        if not entry.get("unit"):
            problems.append(f"{entry['field']}: no unit declared")

    for entry in mapping["derived"]:
        if not entry.get("from"):
            problems.append(f"{entry['field']}: declared derived without saying from what")

    filers = set(evidence["filers"])
    declared = {f["ticker"] for f in mapping["filers_measured"]}
    for ticker in sorted(declared - filers):
        problems.append(f"{ticker}: listed as measured, but absent from the evidence")
    for ticker in sorted(filers - declared):
        problems.append(f"{ticker}: measured, but not listed in the mapping")

    for entry in mapping.get("unavailable", []):
        for ticker in entry.get("filers_affected", ()):
            if ticker not in filers:
                problems.append(f"unavailable: {ticker} was never measured")
        for field in entry.get("inputs", ()):
            if field not in contract:
                problems.append(f"unavailable: {field} is not a field of the data contract")
        if not entry.get("reason"):
            problems.append("unavailable: an entry without a reason")

    return problems


def main() -> int:
    mapping, inputs, evidence = load()
    problems = check(mapping, inputs, evidence)

    contract = len(set(inputs["fundamental"]["fields"]) - {"period"})
    concepts = sum(len(e["concepts"]) + len(e.get("historical", ())) for e in mapping["fields"])
    # A checker that says how much it looked at. "0 problems" from one that
    # examined nothing reads the same as from one that examined everything.
    print(
        f"check_edgar_mapping: {contract} contract fields, "
        f"{len(mapping['fields'])} mapped and {len(mapping['derived'])} derived, "
        f"{concepts} concepts, {len(evidence['filers'])} filers measured "
        f"on {mapping['measured_on']}"
    )

    if problems:
        for problem in problems:
            print(f"  {problem}", file=sys.stderr)
        print(f"{len(problems)} problem(s).", file=sys.stderr)
        return 1
    print("  no problems")
    return 0


if __name__ == "__main__":
    sys.exit(main())
