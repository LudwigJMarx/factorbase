"""Resolve a catalogue entry's `implementation` string to a callable.

The catalogue names its implementation as text, `module:function`, rather than
importing it. That keeps the YAML readable by things that are not Python, and
it makes the wiring checkable: a name that does not resolve is a finding, not
an ImportError at some user's call site.
"""

from __future__ import annotations

import importlib
import inspect
from collections.abc import Callable
from typing import Any

from .catalog import Catalog, default_catalog
from .errors import CatalogError
from .schema import Factor


def resolve(reference: str) -> Callable[..., Any]:
    """Turn 'factorbase.compute.momentum:rsi' into the function itself."""
    if ":" not in reference:
        raise CatalogError(reference, "implementation must be written as 'module:function'")
    module_name, _, function_name = reference.partition(":")
    try:
        module = importlib.import_module(module_name)
    except ImportError as error:
        raise CatalogError(reference, f"module {module_name!r} does not import: {error}") from None
    try:
        function = getattr(module, function_name)
    except AttributeError:
        raise CatalogError(
            reference, f"module {module_name!r} has no attribute {function_name!r}"
        ) from None
    if not callable(function):
        raise CatalogError(reference, f"{function_name!r} is not callable")
    return function


def implementation_of(factor: Factor) -> Callable[..., Any]:
    if factor.implementation is None:
        raise CatalogError(factor.id, "entry has no implementation")
    return resolve(factor.implementation)


def parameter_mismatch(factor: Factor) -> tuple[str, ...]:
    """Which catalogue parameters the implementation does not accept.

    Declaring a parameter nobody reads is the quiet failure mode here: the
    catalogue promises a knob, a caller sets it, and the number does not move.
    The check runs in CI for exactly that reason.
    """
    if factor.implementation is None:
        return ()
    signature = inspect.signature(resolve(factor.implementation))
    accepted = set(signature.parameters)
    takes_kwargs = any(
        p.kind is inspect.Parameter.VAR_KEYWORD for p in signature.parameters.values()
    )
    if takes_kwargs:
        return ()
    return tuple(p.id for p in factor.parameters if p.id not in accepted)


def compute(factor_id: str, *args: Any, catalog: Catalog | None = None, **kwargs: Any) -> Any:
    """Look a factor up and run it.

    Parameters the caller does not pass fall back to the catalogue's defaults,
    not to the function's own, so that the documented default and the effective
    one cannot drift apart.
    """
    catalog = catalog or default_catalog()
    factor = catalog[factor_id]
    function = implementation_of(factor)
    defaults = {p.id: p.default for p in factor.parameters}
    defaults.update(kwargs)
    return function(*args, **defaults)
