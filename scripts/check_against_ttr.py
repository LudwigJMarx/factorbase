#!/usr/bin/env python3
"""Hold this catalogue against TTR, the R package that computes much of the same set.

── WHY THIS EXISTS ─────────────────────────────────────────────────────────

Every other check here compares this package to itself. This one compares it to
somebody else's arithmetic, in a package a great many people already have
installed, and it is the only check that can catch a formula that is wrong in
the entry and in the test at once.

It is also what turns the README's central claim into a measurement. The claim
is that two packages hand you the same indicator name and disagree without
saying why. `catalog/mappings/ttr.yaml` names the call that agrees, and the
call a reader reaches for first when that is not the same one.

── WHAT IT ASSERTS ─────────────────────────────────────────────────────────

For each mapping, in both directions:

  identical     the two agree within the stated tolerance over their common
                range
  converges     they differ at the start by roughly the stated amount, and
                agree within tolerance from the stated bar onward
  not_compared  TTR has no equivalent; only the trap is checked

Traps are asserted to *still differ*. A note describing a difference that has
quietly gone away is worse than no note, because it reads as current.

It also asserts that every column the R script emits is named by a mapping and
that every mapping names a column that exists, so neither side can grow one the
other ignores.

── REQUIREMENTS ────────────────────────────────────────────────────────────

R with TTR. If Rscript is missing this fails rather than skipping: a check that
passes because it did not run is the invented zero this project's whole
apparatus exists to prevent. Contributors without R leave it to the `ttr` job
in CI, which is why it is a separate job there.

Usage:  python3 scripts/check_against_ttr.py [--keep <dir>]
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from factorbase import compute  # noqa: E402

MAPPING = ROOT / "catalog" / "mappings" / "ttr.yaml"
R_SCRIPT = ROOT / "scripts" / "ttr_reference.R"


def load_series(relative: str) -> pd.DataFrame:
    frame = pd.read_csv(ROOT / relative, parse_dates=["date"]).set_index("date")
    return frame


def run_r(series: Path, destination: Path) -> str:
    rscript = shutil.which("Rscript")
    if rscript is None:
        print(
            "check_against_ttr: Rscript not found.\n"
            "  This check compares against R's TTR and cannot run without it.\n"
            "  Install R and TTR, or leave it to the `ttr` job in CI.",
            file=sys.stderr,
        )
        raise SystemExit(2)
    finished = subprocess.run(
        [rscript, str(R_SCRIPT), str(series), str(destination)],
        capture_output=True,
        text=True,
    )
    if finished.returncode != 0:
        print(finished.stdout, file=sys.stderr)
        print(finished.stderr, file=sys.stderr)
        raise SystemExit("check_against_ttr: the R side failed")
    return finished.stdout.strip()


def compared(mine: pd.Series, theirs: pd.Series) -> tuple[np.ndarray, np.ndarray]:
    ours = np.asarray(mine, dtype="float64")
    other = np.asarray(theirs, dtype="float64")
    both = ~np.isnan(ours) & ~np.isnan(other)
    return ours[both], other[both]


def first_common_bar(mine: pd.Series, theirs: pd.Series) -> int:
    ours = np.asarray(mine, dtype="float64")
    other = np.asarray(theirs, dtype="float64")
    both = ~np.isnan(ours) & ~np.isnan(other)
    positions = np.flatnonzero(both)
    return int(positions[0]) if positions.size else -1


def check_mapping(
    mapping: dict[str, Any], prices: pd.DataFrame, reference: pd.DataFrame
) -> tuple[list[str], str]:
    """Return any findings, plus one line of measurement for the report."""
    factor = mapping["factor"]
    agreement = mapping["agreement"]
    findings: list[str] = []

    if agreement == "not_compared":
        return findings, f"  {factor:<32} not compared, TTR has no equivalent"

    column = mapping["column"]
    mine = compute(factor, prices, **mapping.get("arguments", {}))
    theirs = reference[column]
    ours, other = compared(mine, theirs)
    if ours.size == 0:
        findings.append(f"{factor}: no bar where both sides are defined")
        return findings, f"  {factor:<32} nothing to compare"

    difference = np.abs(ours - other)
    tolerance = float(mapping["tolerance"])

    if agreement == "identical":
        worst = float(difference.max())
        if worst > tolerance:
            findings.append(
                f"{factor}: declared identical within {tolerance:g}, "
                f"worst difference is {worst:.3e} over {ours.size} bars"
            )
        return findings, f"  {factor:<32} identical, worst {worst:.2e} over {ours.size} bars"

    if agreement == "converges":
        start = first_common_bar(mine, theirs)
        settles = int(mapping["converged_by"])
        full_mine = np.asarray(mine, dtype="float64")
        full_theirs = np.asarray(theirs, dtype="float64")
        tail = np.abs(full_mine[settles:] - full_theirs[settles:])
        tail = tail[~np.isnan(tail)]
        worst_tail = float(tail.max()) if tail.size else float("nan")
        opening = float(abs(full_mine[start] - full_theirs[start]))
        claimed = float(mapping["initial_difference"])

        if worst_tail > tolerance:
            findings.append(
                f"{factor}: declared converged by bar {settles} within {tolerance:g}, "
                f"worst difference after it is {worst_tail:.3e}"
            )
        # The other direction. If the seeds ever agree, the note is describing
        # something that no longer happens, and a stale note reads as current.
        if not claimed / 2.0 <= opening <= claimed * 3.0:
            findings.append(
                f"{factor}: declares an opening difference near {claimed:g}, "
                f"measured {opening:.3e}. The note is stale in one direction or "
                "the other."
            )
        return findings, (
            f"  {factor:<32} opens {opening:.3f} apart, "
            f"within {tolerance:g} from bar {settles} (worst after: {worst_tail:.1e})"
        )

    findings.append(f"{factor}: unknown agreement {agreement!r}")
    return findings, f"  {factor:<32} unknown agreement"


def check_trap(
    mapping: dict[str, Any], prices: pd.DataFrame, reference: pd.DataFrame
) -> tuple[list[str], str]:
    trap = mapping["trap"]
    factor = mapping["factor"]
    mine = compute(factor, prices, **mapping.get("arguments", {}))
    ours, other = compared(mine, reference[trap["column"]])
    if ours.size == 0:
        return (
            [f"{factor} trap: no bar where both sides are defined"],
            f"  {factor + ' (trap)':<32} nothing to compare",
        )
    worst = float(np.abs(ours - other).max())
    claimed = float(trap["measured_difference"])
    findings: list[str] = []
    if worst < claimed / 2.0:
        findings.append(
            f"{factor} trap: the note describes a difference near {claimed:g}, "
            f"measured {worst:.3e}. Either the note is stale or the trap is gone."
        )
    # And the other way. An understated number reads as a rounding difference
    # when it is a hundred points, which is how the aroon trap was first
    # written: measured from the opening bars rather than over the series.
    if worst > claimed * 3.0:
        findings.append(
            f"{factor} trap: the note says about {claimed:g}, measured {worst:.3g}. "
            "The note understates it."
        )
    return findings, f"  {factor + ' (trap)':<32} differs by {worst:.3f}, note says ~{claimed:g}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--keep", type=Path, help="write the R output here instead of a temp file")
    arguments = parser.parse_args()

    document = yaml.safe_load(MAPPING.read_text(encoding="utf-8"))
    mappings = document["mappings"]
    prices = load_series(document["series"])

    with tempfile.TemporaryDirectory() as temporary:
        destination = arguments.keep or (Path(temporary) / "ttr.csv")
        banner = run_r(ROOT / document["series"], destination)
        reference = pd.read_csv(destination)

    findings: list[str] = []
    lines: list[str] = []

    named = {m["column"] for m in mappings if m.get("column")}
    named |= {m["trap"]["column"] for m in mappings if m.get("trap")}
    emitted = set(reference.columns) - {"row"}
    for missing in sorted(named - emitted):
        findings.append(f"mapping names column {missing!r}, which the R script does not emit")
    for unused in sorted(emitted - named):
        findings.append(f"the R script emits column {unused!r}, which no mapping names")

    compared_count = 0
    for mapping in mappings:
        if mapping["agreement"] != "not_compared":
            compared_count += 1
        found, line = check_mapping(mapping, prices, reference)
        findings.extend(found)
        lines.append(line)
        if mapping.get("trap"):
            found, line = check_trap(mapping, prices, reference)
            findings.extend(found)
            lines.append(line)

    traps = sum(1 for m in mappings if m.get("trap"))
    print(banner)
    print(
        f"check_against_ttr: {len(mappings)} mapping(s), {compared_count} compared, "
        f"{traps} trap(s), against {document['package']} {document['measured_against']} "
        f"as declared"
    )
    for line in lines:
        print(line)

    if findings:
        print(f"\n{len(findings)} finding(s):", file=sys.stderr)
        for finding in findings:
            print(f"  - {finding}", file=sys.stderr)
        return 1

    print("0 findings")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
