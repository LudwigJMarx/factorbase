"""Shared plumbing for the factor implementations.

Two things live here and nothing else: the input check that turns a missing
column into a useful error, and the moving-average dispatch that several
families share.
"""

from __future__ import annotations

from typing import Final

import numpy as np
import pandas as pd

from ..errors import InsufficientHistoryError, MissingInputError

MA_METHODS: Final = ("sma", "ema", "wma")


def require_columns(frame: pd.DataFrame, columns: tuple[str, ...], factor_id: str) -> None:
    """Fail with the column names, not with a KeyError three frames deep."""
    missing = tuple(c for c in columns if c not in frame.columns)
    if missing:
        raise MissingInputError(factor_id, missing, tuple(frame.columns))


def require_history(frame: pd.DataFrame, needed: int, factor_id: str) -> None:
    """Refuse a series that is shorter than the warm-up the factor needs.

    A window of 200 over 40 bars does not produce a weak reading, it produces
    nothing at all. Returning an all-NaN column would let that pass as data.
    """
    if len(frame) < needed:
        raise InsufficientHistoryError(factor_id, needed, len(frame))


def _seed_position(series: pd.Series, periods: int) -> int | None:
    """Index position of the `periods`-th observation that is not missing.

    Seeding at a fixed offset of `periods - 1` is right only for a series whose
    first entry is real. RSI smooths gains and losses derived from a diff, so
    its first entry is missing, and the fixed offset then averaged n-1 values
    and placed the result a bar early - a 13-period reading labelled RSI(14).
    Returns None when the series never reaches `periods` real observations.
    """
    present = series.notna().to_numpy()
    reached = present.cumsum()
    positions = np.flatnonzero(present & (reached == periods))
    return int(positions[0]) if positions.size else None


def simple_moving_average(series: pd.Series, periods: int) -> pd.Series:
    return series.rolling(window=periods, min_periods=periods).mean()


def exponential_moving_average(series: pd.Series, periods: int) -> pd.Series:
    """Seeded with the simple average of the first `periods` values.

    pandas' own `ewm(..., adjust=True)` starts at the first observation and
    weights what little history it has. That is a different series, visibly so
    for the first few hundred bars, and it is not the convention the textbooks
    or the charting packages use. The seed is made explicit here so that a
    reader comparing two implementations knows which one this is.
    """
    if periods < 1:
        raise ValueError("periods must be at least 1")
    seeded = series.copy().astype("float64")
    start = _seed_position(series, periods)
    if start is None:
        return pd.Series(np.nan, index=series.index, dtype="float64")
    seeded.iloc[:start] = np.nan
    seeded.iloc[start] = series.iloc[: start + 1].mean()
    return seeded.ewm(span=periods, adjust=False, ignore_na=False).mean()


def weighted_moving_average(series: pd.Series, periods: int) -> pd.Series:
    weights = pd.Series(range(1, periods + 1), dtype="float64")
    divisor = weights.sum()

    def weighted(window: pd.Series) -> float:
        return float((window.to_numpy() * weights.to_numpy()).sum() / divisor)

    return series.rolling(window=periods, min_periods=periods).apply(weighted, raw=False)


def moving_average(series: pd.Series, periods: int, method: str) -> pd.Series:
    """Dispatch by name, and say what the allowed names are when it fails."""
    if method == "sma":
        return simple_moving_average(series, periods)
    if method == "ema":
        return exponential_moving_average(series, periods)
    if method == "wma":
        return weighted_moving_average(series, periods)
    raise ValueError(f"unknown moving-average method {method!r}; expected one of {MA_METHODS}")


def wilder_smoothing(series: pd.Series, periods: int) -> pd.Series:
    """Wilder's own smoothing, which is an EMA with alpha = 1/n.

    The seed is the mean of the first n observations that exist, placed at the
    position of the nth of them, so a series that begins with a missing value
    is not silently seeded from n-1 values a bar early.

    Wilder wrote his indicators before the exponential average had a standard
    name, and the constant he used is 1/n rather than 2/(n+1). An RSI(14)
    computed with a 14-period EMA is therefore not Wilder's RSI(14); it is
    roughly his RSI(27). Every indicator of his in this package uses this
    function, and says so.
    """
    if periods < 1:
        raise ValueError("periods must be at least 1")
    seeded = series.copy().astype("float64")
    start = _seed_position(series, periods)
    if start is None:
        return pd.Series(np.nan, index=series.index, dtype="float64")
    seeded.iloc[:start] = np.nan
    seeded.iloc[start] = series.iloc[: start + 1].mean()
    return seeded.ewm(alpha=1.0 / periods, adjust=False, ignore_na=False).mean()
