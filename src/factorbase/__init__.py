"""factorbase: screening factors with a stated formula and a reference implementation.

The catalogue under `catalog/` is the source of truth. Everything else in the
package either validates it, builds something from it, or computes it.
"""

from __future__ import annotations

from .catalog import Catalog, default_catalog, load_catalog
from .errors import (
    CatalogError,
    FactorbaseError,
    InsufficientHistoryError,
    MissingInputError,
    UnknownFactorError,
)
from .registry import compute, implementation_of, resolve
from .schema import Direction, Factor, Formula, Kind, Parameter, Period, Status, Unit

__version__ = "0.1.0"

__all__ = [
    "Catalog",
    "CatalogError",
    "Direction",
    "Factor",
    "FactorbaseError",
    "Formula",
    "InsufficientHistoryError",
    "Kind",
    "MissingInputError",
    "Parameter",
    "Period",
    "Status",
    "Unit",
    "UnknownFactorError",
    "__version__",
    "compute",
    "default_catalog",
    "implementation_of",
    "load_catalog",
    "resolve",
]
