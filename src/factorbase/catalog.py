"""Load the catalogue from YAML and refuse anything that does not fit.

The YAML files under `catalog/` are the source of truth. The SQLite database
and the docs are both built from them, never edited by hand, so there is one
place to change a definition and one place to review a change to one.
"""

from __future__ import annotations

import os
from collections.abc import Iterator
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from .errors import CatalogError, UnknownFactorError
from .schema import (
    Companion,
    Direction,
    Factor,
    Formula,
    Kind,
    Parameter,
    Period,
    Status,
    Unit,
)

_ENV_OVERRIDE = "FACTORBASE_CATALOG"


def catalog_dir() -> Path:
    """Where the YAML lives.

    Three places, in order: an explicit override, the copy shipped inside the
    installed package, the repository checkout. The override exists so tests
    can point at a fixture without monkeypatching module state.
    """
    override = os.environ.get(_ENV_OVERRIDE)
    if override:
        path = Path(override)
        if not path.is_dir():
            raise CatalogError(str(path), f"{_ENV_OVERRIDE} does not point at a directory")
        return path
    packaged = Path(__file__).parent / "catalog"
    if packaged.is_dir():
        return packaged
    checkout = Path(__file__).resolve().parents[2] / "catalog"
    if checkout.is_dir():
        return checkout
    raise CatalogError("catalog", "no catalogue directory found")


def _require(mapping: dict[str, Any], key: str, source: str, factor_id: str) -> Any:
    if key not in mapping:
        raise CatalogError(source, f"{factor_id or '<entry>'}: missing required key {key!r}")
    return mapping[key]


def _enum(cls: type, value: Any, source: str, factor_id: str, key: str) -> Any:
    try:
        return cls(value)
    except ValueError:
        allowed = ", ".join(member.value for member in cls)  # type: ignore[attr-defined]
        raise CatalogError(
            source, f"{factor_id}: {key}={value!r} is not one of {allowed}"
        ) from None


def _parameter_from(raw: dict[str, Any], source: str, factor_id: str) -> Parameter:
    unknown = set(raw) - {
        "id",
        "name",
        "dtype",
        "default",
        "description",
        "minimum",
        "maximum",
        "choices",
    }
    if unknown:
        raise CatalogError(source, f"{factor_id}: parameter has unknown keys {sorted(unknown)}")
    return Parameter(
        id=_require(raw, "id", source, factor_id),
        name=_require(raw, "name", source, factor_id),
        dtype=_require(raw, "dtype", source, factor_id),
        default=_require(raw, "default", source, factor_id),
        description=_require(raw, "description", source, factor_id),
        minimum=raw.get("minimum"),
        maximum=raw.get("maximum"),
        choices=tuple(raw.get("choices", ())),
    )


_FACTOR_KEYS = {
    "id",
    "name",
    "kind",
    "family",
    "summary",
    "description",
    "inputs",
    "unit",
    "direction",
    "status",
    "formulas",
    "parameters",
    "period",
    "companions",
    "output_range",
    "aliases",
    "references",
    "implementation",
    "notes",
    "tags",
}


def _factor_from(raw: dict[str, Any], source: str) -> Factor:
    factor_id = str(raw.get("id", ""))
    unknown = set(raw) - _FACTOR_KEYS
    if unknown:
        raise CatalogError(source, f"{factor_id}: unknown keys {sorted(unknown)}")

    formulas = tuple(
        Formula(latex=_require(item, "latex", source, factor_id), note=item.get("note", ""))
        for item in raw.get("formulas", [])
    )
    parameters = tuple(
        _parameter_from(item, source, factor_id) for item in raw.get("parameters", [])
    )
    output_range = raw.get("output_range", [None, None])
    if not isinstance(output_range, list) or len(output_range) != 2:
        raise CatalogError(source, f"{factor_id}: output_range must be a two-element list")

    factor = Factor(
        id=factor_id,
        name=_require(raw, "name", source, factor_id),
        kind=_enum(Kind, _require(raw, "kind", source, factor_id), source, factor_id, "kind"),
        family=_require(raw, "family", source, factor_id),
        summary=_require(raw, "summary", source, factor_id),
        description=_require(raw, "description", source, factor_id),
        inputs=tuple(_require(raw, "inputs", source, factor_id)),
        unit=_enum(Unit, _require(raw, "unit", source, factor_id), source, factor_id, "unit"),
        direction=_enum(
            Direction, _require(raw, "direction", source, factor_id), source, factor_id, "direction"
        ),
        status=_enum(
            Status, _require(raw, "status", source, factor_id), source, factor_id, "status"
        ),
        formulas=formulas,
        parameters=parameters,
        period=_enum(Period, raw.get("period", "not_applicable"), source, factor_id, "period"),
        companions=tuple(
            _enum(Companion, name, source, factor_id, "companions")
            for name in raw.get("companions", ())
        ),
        output_range=(output_range[0], output_range[1]),
        aliases=tuple(raw.get("aliases", ())),
        references=tuple(raw.get("references", ())),
        implementation=raw.get("implementation"),
        notes=raw.get("notes", ""),
        tags=tuple(raw.get("tags", ())),
    )
    factor.validate(source)
    return factor


# Directories under `catalog/` that hold something other than factor entries.
# `mappings/` records how this catalogue relates to other packages; it is data
# about the catalogue rather than part of it, and feeding it to the factor
# loader would only produce a confusing complaint about a missing key.
_NOT_FACTORS = frozenset({"mappings"})


def _yaml_files(root: Path) -> Iterator[Path]:
    for path in sorted(root.rglob("*.yaml")):
        if path.name.startswith("_") or path.name == "inputs.yaml":
            continue
        if _NOT_FACTORS & set(path.relative_to(root).parts):
            continue
        yield path


class Catalog:
    """All factors, keyed by id, with the input vocabulary they refer to."""

    def __init__(self, factors: dict[str, Factor], inputs: dict[str, Any], sources: list[Path]):
        self._factors = factors
        self.inputs = inputs
        self.sources = tuple(sources)

    def __len__(self) -> int:
        return len(self._factors)

    def __iter__(self) -> Iterator[Factor]:
        return iter(self._factors.values())

    def __contains__(self, factor_id: object) -> bool:
        return factor_id in self._factors

    def __getitem__(self, factor_id: str) -> Factor:
        try:
            return self._factors[factor_id]
        except KeyError:
            raise UnknownFactorError(f"no factor {factor_id!r} in the catalogue") from None

    def ids(self) -> tuple[str, ...]:
        return tuple(self._factors)

    def of_kind(self, kind: Kind) -> tuple[Factor, ...]:
        return tuple(f for f in self._factors.values() if f.kind is kind)

    def families(self) -> tuple[str, ...]:
        return tuple(sorted({f.family for f in self._factors.values()}))

    def known_inputs(self) -> frozenset[str]:
        names: set[str] = set()
        for group in self.inputs.values():
            if isinstance(group, dict) and "fields" in group:
                names.update(group["fields"])
        return frozenset(names)


def load_catalog(root: Path | None = None) -> Catalog:
    """Read every YAML file under `root` and validate the lot.

    Raises on the first problem rather than collecting them, because a
    catalogue with one bad entry is not usable anyway and a half-loaded one
    invites callers to work with it.
    """
    root = root or catalog_dir()
    inputs_path = root / "inputs.yaml"
    if not inputs_path.is_file():
        raise CatalogError(str(root), "inputs.yaml is missing; the data contract is not optional")
    inputs = yaml.safe_load(inputs_path.read_text(encoding="utf-8"))

    factors: dict[str, Factor] = {}
    seen_aliases: dict[str, str] = {}
    sources: list[Path] = []
    for path in _yaml_files(root):
        source = str(path.relative_to(root))
        sources.append(path)
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
        if document is None:
            raise CatalogError(source, "file is empty")
        entries = document.get("factors")
        if not isinstance(entries, list) or not entries:
            raise CatalogError(source, "file has no non-empty 'factors' list")
        for raw in entries:
            factor = _factor_from(raw, source)
            if factor.id in factors:
                raise CatalogError(source, f"duplicate factor id {factor.id!r}")
            factors[factor.id] = factor
            for alias in factor.aliases:
                if alias in seen_aliases:
                    raise CatalogError(
                        source,
                        f"alias {alias!r} claimed by {factor.id!r} and {seen_aliases[alias]!r}",
                    )
                seen_aliases[alias] = factor.id

    if not factors:
        raise CatalogError(str(root), "catalogue is empty")

    catalog = Catalog(factors, inputs, sources)
    vocabulary = catalog.known_inputs()
    for factor in catalog:
        unknown = set(factor.inputs) - vocabulary
        if unknown:
            raise CatalogError(
                "inputs.yaml", f"{factor.id}: inputs {sorted(unknown)} are not in the vocabulary"
            )
    return catalog


@lru_cache(maxsize=1)
def default_catalog() -> Catalog:
    """The catalogue shipped with this package, loaded once."""
    return load_catalog()
