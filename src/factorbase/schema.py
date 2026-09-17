"""The shape of a catalogue entry.

These dataclasses are the schema. There is no second copy of it in a JSON
schema file or in prose, because two copies drift and then nobody knows which
one the loader actually enforces.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from .errors import CatalogError


class Kind(StrEnum):
    """What sort of thing a factor is.

    The distinction is not cosmetic: it decides what data the factor consumes
    and what its output means. An INDICATOR eats prices and returns a number,
    a SIGNAL eats prices and returns a boolean, a FUNDAMENTAL eats reported
    accounts, a COMPOSITE eats other factors' outputs.
    """

    INDICATOR = "indicator"
    FUNDAMENTAL = "fundamental"
    SIGNAL = "signal"
    COMPOSITE = "composite"


class Unit(StrEnum):
    """What the number is in.

    Needed because "50" means nothing on its own: bounded oscillator, percent,
    or a currency amount are three different things to rank, plot and filter.
    """

    INDEX = "index"  # bounded oscillator, e.g. 0..100
    PERCENT = "percent"  # 0.07 is seven percent
    RATIO = "ratio"  # dimensionless, unbounded, e.g. P/E
    CURRENCY = "currency"  # amount in the instrument's currency
    PRICE = "price"  # same scale as the price series
    COUNT = "count"  # a number of bars, days, occurrences
    DAYS = "days"
    BOOLEAN = "boolean"  # signals, and the selection masks among the composites


class Direction(StrEnum):
    """Which end of the scale is the good end, when ranking.

    UNDEFINED is a real answer, not a gap: for an oscillator neither extreme is
    "better" without a strategy around it. Writing HIGHER there to avoid an
    empty field would put a false claim in the catalogue.
    """

    HIGHER = "higher"
    LOWER = "lower"
    UNDEFINED = "undefined"


class Period(StrEnum):
    """The reporting basis of a fundamental figure."""

    ANNUAL = "annual"
    TTM = "ttm"
    QUARTERLY = "quarterly"
    POINT_IN_TIME = "point_in_time"
    NOT_APPLICABLE = "not_applicable"


class Status(StrEnum):
    """How far an entry has been taken.

    DRAFT means the definition is written but the implementation or its test is
    not in place yet. It is in the catalogue so the gap is countable, which is
    the opposite of leaving it out and calling the catalogue complete.
    """

    STABLE = "stable"
    DRAFT = "draft"


@dataclass(frozen=True, slots=True)
class Parameter:
    """One knob on a factor."""

    id: str
    name: str
    dtype: str  # int | float | str | bool
    default: Any
    description: str
    minimum: float | None = None
    maximum: float | None = None
    choices: tuple[str, ...] = ()

    def validate(self, source: str) -> None:
        if self.dtype not in {"int", "float", "str", "bool"}:
            raise CatalogError(source, f"parameter {self.id!r}: unknown dtype {self.dtype!r}")
        if self.dtype == "int" and not isinstance(self.default, int):
            raise CatalogError(source, f"parameter {self.id!r}: default is not an int")
        if self.dtype == "float" and not isinstance(self.default, (int, float)):
            raise CatalogError(source, f"parameter {self.id!r}: default is not a number")
        if self.choices and self.default not in self.choices:
            raise CatalogError(
                source, f"parameter {self.id!r}: default {self.default!r} is not among choices"
            )
        if self.minimum is not None and self.maximum is not None and self.minimum > self.maximum:
            raise CatalogError(source, f"parameter {self.id!r}: minimum above maximum")


@dataclass(frozen=True, slots=True)
class Formula:
    """One line of the definition, as LaTeX, plus what its symbols mean.

    `latex` is written for a reader, not for a renderer: it is the statement
    the implementation is checked against. When the two disagree, the formula
    wins and the code is wrong.
    """

    latex: str
    note: str = ""


@dataclass(frozen=True, slots=True)
class Factor:
    """A single catalogue entry."""

    id: str
    name: str
    kind: Kind
    family: str
    summary: str
    description: str
    inputs: tuple[str, ...]
    unit: Unit
    direction: Direction
    status: Status
    formulas: tuple[Formula, ...] = ()
    parameters: tuple[Parameter, ...] = ()
    period: Period = Period.NOT_APPLICABLE
    requires_benchmark: bool = False
    output_range: tuple[float | None, float | None] = (None, None)
    aliases: tuple[str, ...] = ()
    references: tuple[str, ...] = ()
    implementation: str | None = None
    notes: str = ""
    tags: tuple[str, ...] = field(default_factory=tuple)

    def validate(self, source: str) -> None:
        if not self.id or not self.id.replace("_", "").isalnum() or self.id != self.id.lower():
            raise CatalogError(source, f"id {self.id!r} is not lowercase snake_case")
        if not self.name:
            raise CatalogError(source, f"{self.id}: name is empty")
        if not self.summary:
            raise CatalogError(source, f"{self.id}: summary is empty")
        if not self.description:
            raise CatalogError(source, f"{self.id}: description is empty")
        if not self.family:
            raise CatalogError(source, f"{self.id}: family is empty")
        if not self.inputs:
            raise CatalogError(source, f"{self.id}: inputs is empty")
        if self.kind is Kind.SIGNAL and self.unit is not Unit.BOOLEAN:
            raise CatalogError(source, f"{self.id}: a signal must have unit 'boolean'")
        if self.kind in {Kind.INDICATOR, Kind.FUNDAMENTAL} and self.unit is Unit.BOOLEAN:
            raise CatalogError(
                source, f"{self.id}: an {self.kind.value} must return a number, not a boolean"
            )
        if self.kind is Kind.FUNDAMENTAL and self.period is Period.NOT_APPLICABLE:
            raise CatalogError(source, f"{self.id}: a fundamental must state its period")
        if self.status is Status.STABLE and not self.implementation:
            raise CatalogError(source, f"{self.id}: stable entries need an implementation")
        if self.status is Status.STABLE and not self.formulas:
            raise CatalogError(source, f"{self.id}: stable entries need at least one formula")
        low, high = self.output_range
        if low is not None and high is not None and low > high:
            raise CatalogError(source, f"{self.id}: output range is inverted")
        seen: set[str] = set()
        for parameter in self.parameters:
            if parameter.id in seen:
                raise CatalogError(source, f"{self.id}: duplicate parameter {parameter.id!r}")
            seen.add(parameter.id)
            parameter.validate(source)
