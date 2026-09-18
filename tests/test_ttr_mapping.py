"""The TTR mapping file, checked without needing R.

`scripts/check_against_ttr.py` runs both sides and is the real check, but it
needs R and runs in its own CI job. Everything structural about the file can be
checked here, in the job everyone runs: that it names factors that exist, that
its columns line up with the R script's, and that every number it states is
stated in a form the checker will hold it to.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
MAPPING = ROOT / "catalog" / "mappings" / "ttr.yaml"
R_SCRIPT = ROOT / "scripts" / "ttr_reference.R"

AGREEMENTS = {"identical", "converges", "not_compared"}


@pytest.fixture(scope="module")
def document() -> dict:
    return yaml.safe_load(MAPPING.read_text(encoding="utf-8"))


def test_every_mapping_names_a_factor_that_exists(document: dict) -> None:
    from factorbase import default_catalog

    catalog = default_catalog()
    for mapping in document["mappings"]:
        assert mapping["factor"] in catalog, mapping["factor"]


def test_every_mapping_declares_a_known_agreement(document: dict) -> None:
    for mapping in document["mappings"]:
        assert mapping["agreement"] in AGREEMENTS, mapping["factor"]


def test_a_compared_mapping_states_a_tolerance_and_a_column(document: dict) -> None:
    for mapping in document["mappings"]:
        if mapping["agreement"] == "not_compared":
            continue
        assert mapping.get("column"), mapping["factor"]
        assert isinstance(mapping.get("tolerance"), float), mapping["factor"]


def test_a_converging_mapping_states_both_ends(document: dict) -> None:
    """The bar it settles by and how far apart it starts. The second is what
    stops the note going stale: if the seeds ever agree, the checker says so."""
    for mapping in document["mappings"]:
        if mapping["agreement"] != "converges":
            continue
        assert isinstance(mapping["converged_by"], int), mapping["factor"]
        assert float(mapping["initial_difference"]) > 0.0, mapping["factor"]


def test_every_trap_states_a_measured_difference_and_a_reason(document: dict) -> None:
    """A trap without a number cannot be held to anything, and a trap without a
    reason is a complaint."""
    traps = [m for m in document["mappings"] if m.get("trap")]
    assert len(traps) >= 4
    for mapping in traps:
        trap = mapping["trap"]
        assert float(trap["measured_difference"]) > 0.0, mapping["factor"]
        assert trap.get("note"), mapping["factor"]
        assert trap.get("call"), mapping["factor"]
        assert trap.get("column"), mapping["factor"]


def test_the_columns_line_up_with_the_r_script(document: dict) -> None:
    """Neither side may grow a column the other ignores. The R script is read as
    text rather than run, so this holds in the job that has no R."""
    source = R_SCRIPT.read_text(encoding="utf-8")
    emitted = set(re.findall(r"^out\$(\w+)\s*<-", source, flags=re.MULTILINE))

    named = {m["column"] for m in document["mappings"] if m.get("column")}
    named |= {m["trap"]["column"] for m in document["mappings"] if m.get("trap")}

    assert named - emitted == set(), "mapping names columns the R script does not emit"
    assert emitted - named == set(), "the R script emits columns no mapping names"


def test_the_series_it_measures_against_is_committed(document: dict) -> None:
    series = ROOT / document["series"]
    assert series.is_file()
    assert series.stat().st_size > 10_000


def test_the_versions_it_was_measured_against_are_recorded(document: dict) -> None:
    """A difference without a version is not reproducible."""
    assert re.fullmatch(r"\d+\.\d+\.\d+", document["measured_against"])
    assert document["measured_on"].startswith("R ")


def test_the_checker_is_named_in_a_workflow() -> None:
    """It needs R, so it lives in its own job. That is exactly the arrangement
    check_gates_wired.py exists to confirm is not an excuse for not running."""
    workflows = (ROOT / ".github" / "workflows").glob("*.yml")
    text = "\n".join(path.read_text(encoding="utf-8") for path in workflows)
    assert "scripts/check_against_ttr.py" in text
    assert "r-lib/actions/setup-r" in text


def test_the_rendered_comparison_states_every_mapping(document: dict) -> None:
    """The document exists to be read instead of the YAML, so nothing may be
    lost on the way. Each factor named once, and every trap's measured
    difference carried across."""
    text = (ROOT / "docs" / "compared-with-ttr.md").read_text(encoding="utf-8")

    for mapping in document["mappings"]:
        assert f"`{mapping['factor']}`" in text, mapping["factor"]
        trap = mapping.get("trap")
        if trap:
            assert trap["call"] in text, f"{mapping['factor']}: trap call missing"
            assert f"{trap['measured_difference']:g}" in text, mapping["factor"]


def test_a_factor_appears_in_exactly_one_section(document: dict) -> None:
    """historical_volatility was listed both as a trap and as not compared, the
    trap entry claiming an agreeing call that is not a TTR function at all."""
    import re

    text = (ROOT / "docs" / "compared-with-ttr.md").read_text(encoding="utf-8")
    for mapping in document["mappings"]:
        headings = re.findall(rf"^### `{re.escape(mapping['factor'])}`$", text, re.M)
        assert len(headings) <= 1, f"{mapping['factor']} has {len(headings)} sections"
