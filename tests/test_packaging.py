"""What an installed copy of this package offers, as opposed to a checkout.

Nothing else here runs against the installed shape. The catalogue is loaded
from a path, the checkers run from the repository root, and the tests import
from src. A declaration in pyproject.toml that is wrong therefore breaks only
for people who installed the package, which is everyone who is not the author.
"""

from __future__ import annotations

import importlib
import tomllib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def declared_scripts() -> dict[str, str]:
    with (ROOT / "pyproject.toml").open("rb") as handle:
        return tomllib.load(handle).get("project", {}).get("scripts", {})


def test_every_declared_console_script_resolves() -> None:
    """pip creates an executable for each of these. One that points at a module
    nobody wrote crashes with ImportError the first time it is run, and the
    package's own test suite never touches it."""
    scripts = declared_scripts()
    assert scripts, "no console scripts declared; drop this test if that is intended"

    for name, target in scripts.items():
        module_name, _, function_name = target.partition(":")
        module = importlib.import_module(module_name)
        function = getattr(module, function_name, None)
        assert callable(function), f"console script {name!r} points at {target!r}"


def test_the_command_line_runs_and_reports_its_scope(capsys: pytest.CaptureFixture[str]) -> None:
    from factorbase import default_catalog
    from factorbase.cli import main

    assert main(["list"]) == 0
    listed = capsys.readouterr().out
    assert "rsi" in listed
    # Against the catalogue, not against a number written here. A test that
    # fails whenever an entry is added reports growth as a defect.
    assert str(len(default_catalog())) in listed


def test_the_command_line_can_narrow_by_kind(capsys: pytest.CaptureFixture[str]) -> None:
    from factorbase.cli import main

    assert main(["list", "--kind", "composite"]) == 0
    output = capsys.readouterr().out
    assert "factor_rank" in output
    assert "rsi" not in output


def test_the_command_line_shows_one_entry_with_its_formula(
    capsys: pytest.CaptureFixture[str],
) -> None:
    from factorbase.cli import main

    assert main(["show", "rsi"]) == 0
    output = capsys.readouterr().out
    assert "Relative Strength Index" in output
    assert "RSI_t" in output
    assert "Wilder" in output


def test_an_unknown_id_fails_loudly(capsys: pytest.CaptureFixture[str]) -> None:
    from factorbase.cli import main

    assert main(["show", "no_such_factor"]) == 1
    assert "no_such_factor" in capsys.readouterr().err


def test_the_command_line_builds_the_database(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The README tells a reader to build the SQLite file. From an installed
    copy there is no scripts/ directory to run, so the command has to do it."""
    from factorbase import default_catalog
    from factorbase.cli import main

    destination = tmp_path / "out.sqlite3"
    assert main(["build-db", "--out", str(destination)]) == 0
    assert destination.exists()
    assert str(len(default_catalog())) in capsys.readouterr().out


def test_the_catalogue_states_every_second_series_a_factor_needs() -> None:
    """The field is the only machine-readable answer to "what do I pass".

    It was a single boolean called requires_benchmark, and the fifteen
    valuation entries that need a market series reported false on it, so a
    caller reading the catalogue got a TypeError. check_catalog_wired.py now
    gates this in both directions; this test states the expectation in the
    suite as well, because the gate is a script and scripts get skipped.
    """
    from factorbase import default_catalog
    from factorbase.schema import Companion

    catalog = default_catalog()
    with_market = {f.id for f in catalog if Companion.MARKET in f.companions}
    with_benchmark = {f.id for f in catalog if Companion.BENCHMARK in f.companions}

    # Named rather than counted. A count turns every new entry into a failure
    # and says nothing about which ones need what.
    assert {"price_to_earnings", "market_capitalisation", "market_cap_to_debt"} <= with_market
    assert "beta" in with_benchmark
    assert "relative_strength_levy" not in with_benchmark
    assert "rsi" not in with_market and "rsi" not in with_benchmark
    assert not (with_market & with_benchmark)

    # Every entry that declares one is a fundamental or a relative indicator.
    # Nothing else should acquire a companion without a deliberate decision.
    for factor in catalog:
        if factor.companions:
            assert factor.kind.value in {"fundamental", "indicator"}, factor.id


def test_the_generated_reference_is_current() -> None:
    """The committed docs/catalogue.md must match what the catalogue renders to.

    The check is a CI gate as well; this is here so that the suite everyone runs
    fails too, rather than leaving a stale reference to the one job somebody
    might skip.
    """
    import subprocess
    import sys

    finished = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "check_docs_current.py")],
        capture_output=True,
        text=True,
    )
    assert finished.returncode == 0, finished.stdout + finished.stderr


def test_every_index_link_resolves() -> None:
    """192 links into one file. One broken anchor is invisible until somebody
    clicks it, and nobody clicks 192 of them."""
    import re

    text = (ROOT / "docs" / "catalogue.md").read_text(encoding="utf-8")

    def slug(heading: str) -> str:
        kept = re.sub(r"[^\w\s-]", "", heading.lower())
        return re.sub(r"\s+", "-", kept.strip())

    anchors = {slug(m.group(1)) for m in re.finditer(r"^#{2,4} (.+)$", text, re.M)}
    links = re.findall(r"\]\(#([^)]+)\)", text)

    assert len(links) >= 190
    assert [link for link in links if link not in anchors] == []


def test_the_reference_carries_a_formula_for_every_entry() -> None:
    """The document exists to be read instead of the YAML, so anything the YAML
    states has to survive the rendering."""
    from factorbase import default_catalog

    text = (ROOT / "docs" / "catalogue.md").read_text(encoding="utf-8")
    for factor in default_catalog():
        assert f"`{factor.id}` - {factor.name}" in text, factor.id
        for formula in factor.formulas:
            assert formula.latex in text, f"{factor.id}: formula missing from the reference"


def test_the_package_ships_its_type_marker() -> None:
    """Without py.typed a consumer gets no types, however strict this package is.

    mypy runs here in strict mode over all of src/factorbase, and every public
    function is annotated. None of that reaches anyone who installs the package:
    PEP 561 says a type checker ignores an installed package's annotations
    unless the package ships the marker. mesura, the first consumer, works
    around it with `ignore_missing_imports = true` for `factorbase.*`, which
    also silences a genuinely wrong call.

    The marker has to be inside the installed package, not merely in the
    checkout, so this asserts against the imported module's own directory.
    """
    import factorbase

    package = Path(factorbase.__file__).parent
    assert (package / "py.typed").is_file(), (
        f"no py.typed in {package}; annotations will not reach any consumer"
    )


def test_the_edgar_mapping_covers_the_data_contract() -> None:
    """Every fundamental field is mapped, derived, or the mapping is incomplete.

    The gate script says the same thing and runs in CI. This states it in the
    suite as well: a field added to inputs.yaml without a line in the mapping
    leaves a consumer finding nothing for it, which reads exactly like a
    company that does not report it.
    """
    import json

    import yaml

    mapping = yaml.safe_load(
        (ROOT / "catalog" / "mappings" / "edgar.yaml").read_text(encoding="utf-8")
    )
    inputs = yaml.safe_load((ROOT / "catalog" / "inputs.yaml").read_text(encoding="utf-8"))
    evidence = json.loads((ROOT / mapping["evidence"]).read_text(encoding="utf-8"))

    contract = set(inputs["fundamental"]["fields"]) - {"period"}
    covered = {e["field"] for e in mapping["fields"]} | {e["field"] for e in mapping["derived"]}
    assert contract == covered, f"not covered: {sorted(contract ^ covered)}"

    # Every filer measured in every field, so a dash in the generated table
    # means "never used this tag" and never "nobody looked".
    filers = set(evidence["filers"])
    for field, per_filer in evidence["fields"].items():
        assert set(per_filer) == filers, f"{field}: measured for {sorted(per_filer)}"


def test_the_edgar_mapping_names_no_concept_nobody_found() -> None:
    """The rule that caught two tags written from memory.

    CostOfGoodsSold had not been used by any measured filer since 2017, and
    InterestExpenseNonoperating turned out to be the current tag for three of
    them, which reordered the entry it belongs to.
    """
    import json

    import yaml

    mapping = yaml.safe_load(
        (ROOT / "catalog" / "mappings" / "edgar.yaml").read_text(encoding="utf-8")
    )
    evidence = json.loads((ROOT / mapping["evidence"]).read_text(encoding="utf-8"))

    measured = {
        row["tag"]
        for per_filer in evidence["fields"].values()
        for rows in per_filer.values()
        for row in rows
    }
    named = {
        concept
        for entry in mapping["fields"]
        for concept in list(entry["concepts"]) + list(entry.get("historical", ()))
    }
    assert named <= measured, f"named without evidence: {sorted(named - measured)}"
