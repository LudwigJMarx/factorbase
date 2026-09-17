"""Every failure in this package is loud.

A catalogue that silently drops a malformed entry and a catalogue that is
complete produce the same output: a list of factors. The difference only shows
up later, as a missing column in somebody's backtest. So loading raises.
"""

from __future__ import annotations


class FactorbaseError(Exception):
    """Base class, so callers can catch everything this package raises."""


class CatalogError(FactorbaseError):
    """The catalogue on disk does not satisfy the schema."""

    def __init__(self, source: str, message: str) -> None:
        super().__init__(f"{source}: {message}")
        self.source = source
        self.message = message


class UnknownFactorError(FactorbaseError):
    """A factor id was requested that the catalogue does not define."""


class MissingInputError(FactorbaseError):
    """The data handed in lacks a column the factor needs.

    Carries the concrete column names rather than a generic message: the point
    of the error is to tell the caller which column to add to their loader.
    """

    def __init__(
        self, factor_id: str, missing: tuple[str, ...], available: tuple[str, ...]
    ) -> None:
        super().__init__(
            f"factor {factor_id!r} needs {', '.join(missing)}; "
            f"the frame has {', '.join(available) or '<no columns>'}"
        )
        self.factor_id = factor_id
        self.missing = missing
        self.available = available


class InsufficientHistoryError(FactorbaseError):
    """Fewer observations than the factor's warm-up period requires.

    Raised instead of returning NaN when the shortfall is structural, i.e. the
    whole series is shorter than the window. A partial warm-up at the start of
    a long series yields NaN, which is the normal, documented behaviour.
    """

    def __init__(self, factor_id: str, needed: int, given: int) -> None:
        super().__init__(f"factor {factor_id!r} needs at least {needed} observations, got {given}")
        self.factor_id = factor_id
        self.needed = needed
        self.given = given


class UnsupportedIndexError(FactorbaseError):
    """The frame's index cannot carry the operation the factor needs.

    One factor in this package resamples, and resampling needs dates. Every
    other one works on any index at all, which is why letting pandas raise here
    was wrong: the caller got "Only valid with DatetimeIndex" with no way to
    tell which of the fifty factors in their screen had said it.
    """

    def __init__(self, factor_id: str, required: str, given: str) -> None:
        super().__init__(f"factor {factor_id!r} needs a {required}; the frame has a {given}")
        self.factor_id = factor_id
        self.required = required
        self.given = given
