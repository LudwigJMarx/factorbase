"""The SQLite rendering of the catalogue."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from factorbase import default_catalog
from factorbase.db import build
from factorbase.schema import Kind


@pytest.fixture
def database(tmp_path: Path) -> Path:
    destination = tmp_path / "factorbase.sqlite3"
    build(destination)
    return destination


def test_build_reports_what_it_wrote(tmp_path: Path) -> None:
    """A build that produced an empty file and one that produced a full one
    otherwise print the same thing."""
    written = build(tmp_path / "out.sqlite3")
    assert written["factor"] == len(default_catalog())
    assert written["formula"] > written["factor"]
    assert written["parameter"] > 0


def test_every_factor_reaches_the_database(database: Path) -> None:
    with sqlite3.connect(database) as connection:
        stored = {row[0] for row in connection.execute("SELECT id FROM factor")}
    assert stored == set(default_catalog().ids())


def test_kind_counts_survive_the_round_trip(database: Path) -> None:
    catalog = default_catalog()
    with sqlite3.connect(database) as connection:
        counts = dict(connection.execute("SELECT kind, count(*) FROM factor GROUP BY kind"))
    for kind in Kind:
        expected = len(catalog.of_kind(kind))
        if expected:
            assert counts[kind.value] == expected


def test_a_rebuild_replaces_rather_than_appends(tmp_path: Path) -> None:
    """It is a build artefact, not a log. Appending would double every table."""
    destination = tmp_path / "twice.sqlite3"
    build(destination)
    build(destination)
    with sqlite3.connect(destination) as connection:
        (count,) = connection.execute("SELECT count(*) FROM factor").fetchone()
        (builds,) = connection.execute("SELECT count(*) FROM build").fetchone()
    assert count == len(default_catalog())
    assert builds == 1


def test_the_questions_the_database_exists_for_are_one_line(database: Path) -> None:
    with sqlite3.connect(database) as connection:
        (volume_users,) = connection.execute(
            "SELECT count(*) FROM factor_input WHERE field = 'volume'"
        ).fetchone()
        (bounded_without_range,) = connection.execute(
            "SELECT count(*) FROM factor WHERE unit = 'index' AND range_low IS NULL"
        ).fetchone()
        periods = dict(
            connection.execute(
                "SELECT default_value, count(*) FROM parameter "
                "WHERE id = 'periods' GROUP BY default_value"
            )
        )
    assert volume_users > 0
    assert bounded_without_range == 0
    assert periods["14"] > 0


def test_aliases_point_at_real_factors(database: Path) -> None:
    with sqlite3.connect(database) as connection:
        (orphans,) = connection.execute(
            "SELECT count(*) FROM alias LEFT JOIN factor ON alias.factor_id = factor.id "
            "WHERE factor.id IS NULL"
        ).fetchone()
    assert orphans == 0


def test_the_input_vocabulary_is_carried_across(database: Path) -> None:
    """Without it the factor_input rows name fields nothing defines."""
    with sqlite3.connect(database) as connection:
        (unknown,) = connection.execute(
            "SELECT count(DISTINCT field) FROM factor_input "
            "WHERE field NOT IN (SELECT field FROM input_field)"
        ).fetchone()
    assert unknown == 0
