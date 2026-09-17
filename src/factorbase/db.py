"""Render the catalogue into a single SQLite file.

── WHY A DATABASE AT ALL ───────────────────────────────────────────────────

The YAML is the source of truth and is meant to be read directly. The database
exists for the people who would rather ask a question than read fifteen files:
which factors need volume, which have a parameter called periods, which claim a
bounded range and do not state it. Those are one-line queries here and a
morning's grepping there.

── WHAT IT IS NOT ──────────────────────────────────────────────────────────

Not a cache, not an editable copy, and not committed. It is built from the YAML
every time and overwritten without asking. Editing it changes nothing, which is
the only property that keeps one source of truth.
"""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from .catalog import Catalog, default_catalog

SCHEMA = """
CREATE TABLE factor (
    id           TEXT PRIMARY KEY,
    name         TEXT NOT NULL,
    kind         TEXT NOT NULL,
    family       TEXT NOT NULL,
    summary      TEXT NOT NULL,
    description  TEXT NOT NULL,
    unit         TEXT NOT NULL,
    direction    TEXT NOT NULL,
    period       TEXT NOT NULL,
    status       TEXT NOT NULL,
    requires_benchmark INTEGER NOT NULL,
    range_low    REAL,
    range_high   REAL,
    implementation TEXT,
    notes        TEXT NOT NULL
);

CREATE TABLE factor_input (
    factor_id TEXT NOT NULL REFERENCES factor(id),
    field     TEXT NOT NULL,
    PRIMARY KEY (factor_id, field)
);

CREATE TABLE parameter (
    factor_id   TEXT NOT NULL REFERENCES factor(id),
    id          TEXT NOT NULL,
    name        TEXT NOT NULL,
    dtype       TEXT NOT NULL,
    default_value TEXT NOT NULL,
    minimum     REAL,
    maximum     REAL,
    choices     TEXT NOT NULL,
    description TEXT NOT NULL,
    position    INTEGER NOT NULL,
    PRIMARY KEY (factor_id, id)
);

CREATE TABLE formula (
    factor_id TEXT NOT NULL REFERENCES factor(id),
    position  INTEGER NOT NULL,
    latex     TEXT NOT NULL,
    note      TEXT NOT NULL,
    PRIMARY KEY (factor_id, position)
);

CREATE TABLE reference (
    factor_id TEXT NOT NULL REFERENCES factor(id),
    position  INTEGER NOT NULL,
    citation  TEXT NOT NULL,
    PRIMARY KEY (factor_id, position)
);

CREATE TABLE alias (
    alias     TEXT PRIMARY KEY,
    factor_id TEXT NOT NULL REFERENCES factor(id)
);

CREATE TABLE tag (
    factor_id TEXT NOT NULL REFERENCES factor(id),
    tag       TEXT NOT NULL,
    PRIMARY KEY (factor_id, tag)
);

CREATE TABLE input_field (
    grp         TEXT NOT NULL,
    field       TEXT NOT NULL,
    dtype       TEXT NOT NULL,
    required    INTEGER NOT NULL,
    description TEXT NOT NULL,
    PRIMARY KEY (grp, field)
);

CREATE TABLE build (
    built_at    TEXT NOT NULL,
    factors     INTEGER NOT NULL,
    source_files INTEGER NOT NULL
);

CREATE INDEX factor_kind ON factor(kind);
CREATE INDEX factor_family ON factor(family);
CREATE INDEX factor_input_field ON factor_input(field);
CREATE INDEX parameter_id ON parameter(id);
"""


def build(destination: Path, catalog: Catalog | None = None) -> dict[str, int]:
    """Write the catalogue to `destination`, replacing whatever was there.

    Returns a count per table so the caller can report what it wrote rather
    than reporting that it finished. A build that silently produced an empty
    database and one that produced a full one otherwise print the same thing.
    """
    catalog = catalog or default_catalog()
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        destination.unlink()

    written = {
        "factor": 0,
        "factor_input": 0,
        "parameter": 0,
        "formula": 0,
        "reference": 0,
        "alias": 0,
        "tag": 0,
        "input_field": 0,
    }

    with sqlite3.connect(destination) as connection:
        connection.executescript(SCHEMA)
        for factor in catalog:
            low, high = factor.output_range
            connection.execute(
                "INSERT INTO factor VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    factor.id,
                    factor.name,
                    factor.kind.value,
                    factor.family,
                    factor.summary,
                    factor.description,
                    factor.unit.value,
                    factor.direction.value,
                    factor.period.value,
                    factor.status.value,
                    int(factor.requires_benchmark),
                    low,
                    high,
                    factor.implementation,
                    factor.notes,
                ),
            )
            written["factor"] += 1

            connection.executemany(
                "INSERT INTO factor_input VALUES (?,?)",
                [(factor.id, field) for field in factor.inputs],
            )
            written["factor_input"] += len(factor.inputs)

            for position, parameter in enumerate(factor.parameters):
                connection.execute(
                    "INSERT INTO parameter VALUES (?,?,?,?,?,?,?,?,?,?)",
                    (
                        factor.id,
                        parameter.id,
                        parameter.name,
                        parameter.dtype,
                        repr(parameter.default),
                        parameter.minimum,
                        parameter.maximum,
                        ",".join(parameter.choices),
                        parameter.description,
                        position,
                    ),
                )
                written["parameter"] += 1

            for position, formula in enumerate(factor.formulas):
                connection.execute(
                    "INSERT INTO formula VALUES (?,?,?,?)",
                    (factor.id, position, formula.latex, formula.note),
                )
                written["formula"] += 1

            for position, citation in enumerate(factor.references):
                connection.execute(
                    "INSERT INTO reference VALUES (?,?,?)", (factor.id, position, citation)
                )
                written["reference"] += 1

            connection.executemany(
                "INSERT INTO alias VALUES (?,?)",
                [(alias, factor.id) for alias in factor.aliases],
            )
            written["alias"] += len(factor.aliases)

            connection.executemany(
                "INSERT INTO tag VALUES (?,?)", [(factor.id, tag) for tag in factor.tags]
            )
            written["tag"] += len(factor.tags)

        for group, block in catalog.inputs.items():
            if not isinstance(block, dict) or "fields" not in block:
                continue
            for field, definition in block["fields"].items():
                connection.execute(
                    "INSERT INTO input_field VALUES (?,?,?,?,?)",
                    (
                        group,
                        field,
                        definition.get("dtype", ""),
                        int(bool(definition.get("required", False))),
                        definition.get("description", ""),
                    ),
                )
                written["input_field"] += 1

        connection.execute(
            "INSERT INTO build VALUES (?,?,?)",
            (datetime.now(UTC).isoformat(timespec="seconds"), len(catalog), len(catalog.sources)),
        )

    return written
