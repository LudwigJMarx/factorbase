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
    from factorbase.cli import main

    assert main(["list"]) == 0
    listed = capsys.readouterr().out
    assert "rsi" in listed
    assert "180" in listed


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
    from factorbase.cli import main

    destination = tmp_path / "out.sqlite3"
    assert main(["build-db", "--out", str(destination)]) == 0
    assert destination.exists()
    assert "180" in capsys.readouterr().out


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

    assert "price_to_earnings" in with_market
    assert "market_capitalisation" in with_market
    assert len(with_market) == 15
    assert "beta" in with_benchmark
    assert "relative_strength_levy" not in with_benchmark
    assert len(with_benchmark) == 8
    assert not (with_market & with_benchmark)
