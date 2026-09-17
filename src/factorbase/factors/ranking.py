"""Cross-sectional transforms: turning factor values into ranks and scores.

── WHAT MAKES THESE DIFFERENT ──────────────────────────────────────────────

Everything else in this package looks at one instrument through time. These
look at every instrument at one moment. That is the whole difference between a
factor and a ranking, and it is why a rank cannot be computed from a single
price series no matter how much history it has.

── THE THREE RULES ─────────────────────────────────────────────────────────

Rank within a comparable set, at one point in time. Ranking a bank against a
software company on price-to-book produces a number and not a comparison; the
package cannot enforce the comparability of the universe it is handed, so the
entries say so and the caller does the grouping.

A missing value is not a bad value. Instruments whose factor is NaN are left
out of the ranking rather than placed last. Ranking them last is the most
common way a screen ends up systematically buying whatever its data vendor
failed to cover.

A score built from fewer factors than it claims is a different score. When an
instrument is missing some of the inputs to a composite, the weights of the
rest no longer sum to one, and renormalising them quietly changes the strategy
per instrument. `min_coverage` says how much of the weight has to be present;
below it the score is NaN.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ..schema import Direction

_ASCENDING = {Direction.HIGHER: False, Direction.LOWER: True}


def _as_frame(values: pd.Series | pd.DataFrame) -> tuple[pd.DataFrame, bool]:
    """Accept one cross-section or a panel, and remember which it was."""
    if isinstance(values, pd.Series):
        return values.to_frame().T, True
    return values, False


def _restore(result: pd.DataFrame, was_series: bool) -> pd.Series | pd.DataFrame:
    return result.iloc[0] if was_series else result


def rank(
    values: pd.Series | pd.DataFrame,
    direction: str = "higher",
    method: str = "average",
) -> pd.Series | pd.DataFrame:
    """Position within the cross-section, 1 being best. Catalogue id `factor_rank`.

    `direction` decides which end is best, and it is the same field the
    catalogue entry of the underlying factor carries. Passing it wrong inverts
    the strategy and produces a perfectly plausible-looking result, which is
    why the entry insists it be read from the catalogue rather than typed.

    Ties share the average of the positions they span, so a universe where
    half the instruments report the same value does not get an arbitrary
    ordering imposed on it.
    """
    frame, was_series = _as_frame(values)
    try:
        ascending = _ASCENDING[Direction(direction)]
    except (ValueError, KeyError):
        raise ValueError(
            f"direction must be 'higher' or 'lower', not {direction!r}; "
            "'undefined' cannot be ranked"
        ) from None
    ranked = frame.rank(axis=1, method=method, ascending=ascending, na_option="keep")
    return _restore(ranked, was_series)


def percentile(
    values: pd.Series | pd.DataFrame, direction: str = "higher"
) -> pd.Series | pd.DataFrame:
    """Position as a percentage of the cross-section, 100 being best. Catalogue id `factor_percentile`.

    Comparable across dates and across factors in a way a raw rank is not: a
    rank of 40 means something different in a universe of 50 and one of 3000,
    and a percentile does not.
    """
    frame, was_series = _as_frame(values)
    ranked = rank(frame, direction)
    counted = frame.notna().sum(axis=1)
    spread = (counted - 1).where(counted > 1)
    result = ranked.rsub(counted, axis=0).div(spread, axis=0) * 100.0
    lonely = frame.notna().mul(counted == 1, axis=0)
    return _restore(result.mask(lonely, 50.0), was_series)


def z_score(
    values: pd.Series | pd.DataFrame,
    direction: str = "higher",
    winsorise: float = 0.0,
) -> pd.Series | pd.DataFrame:
    """Standardised distance from the cross-sectional mean. Catalogue id `factor_z_score`.

    Keeps the spacing that a rank throws away: the gap between the best and
    second-best instrument is visible here and is not in a rank. That is an
    advantage when the distribution is well behaved and a liability when it is
    not, since one extreme value moves both the mean and the deviation.

    `winsorise` clips each tail to the given percentile before standardising,
    which is the usual defence. Clipping at 1 percent is common; clipping is
    not free, and at 0 the raw values are used.
    """
    frame, was_series = _as_frame(values)
    working = frame.astype("float64")
    if winsorise > 0.0:
        lower = working.quantile(winsorise / 100.0, axis=1)
        upper = working.quantile(1.0 - winsorise / 100.0, axis=1)
        working = working.clip(lower=lower, upper=upper, axis=0)
    centred = working.sub(working.mean(axis=1), axis=0)
    deviation = working.std(axis=1, ddof=1)
    scored = centred.div(deviation.where(deviation > 0.0), axis=0)
    if Direction(direction) is Direction.LOWER:
        scored = -scored
    return _restore(scored, was_series)


def composite_score(
    components: dict[str, pd.Series | pd.DataFrame],
    weights: dict[str, float],
    directions: dict[str, str],
    min_coverage: float = 1.0,
) -> pd.Series | pd.DataFrame:
    """Weighted mean of the components' percentiles, 0 to 100. Catalogue id `composite_score`.

    Percentiles rather than raw values, because the components are in different
    units and adding a price-to-earnings ratio to a margin is meaningless
    otherwise. Percentiles rather than z-scores because one extreme instrument
    should not move everybody else's score.

    Weights are used as given and are not renormalised per instrument. An
    instrument missing a component whose weight is 30 percent has 70 percent of
    the strategy applied to it, and calling that the same score as everyone
    else's is how a screen ends up ranking on a different rule for every row.
    `min_coverage` is the share of weight that must be present; below it the
    score is NaN, which the caller can see.
    """
    if not components:
        raise ValueError("composite_score needs at least one component")
    missing_weight = set(components) - set(weights)
    if missing_weight:
        raise ValueError(f"no weight given for {sorted(missing_weight)}")
    missing_direction = set(components) - set(directions)
    if missing_direction:
        raise ValueError(f"no direction given for {sorted(missing_direction)}")
    total_weight = sum(weights[name] for name in components)
    if total_weight <= 0.0:
        raise ValueError("the weights of the given components sum to zero or less")

    was_series = isinstance(next(iter(components.values())), pd.Series)
    scored: dict[str, pd.DataFrame] = {}
    for name, values in components.items():
        frame, _ = _as_frame(values)
        scored[name] = percentile(frame, directions[name])

    weighted = None
    present = None
    for name, frame in scored.items():
        weight = weights[name]
        contribution = frame.fillna(0.0) * weight
        available = frame.notna().astype("float64") * weight
        weighted = contribution if weighted is None else weighted + contribution
        present = available if present is None else present + available

    assert weighted is not None and present is not None
    coverage = present / total_weight
    result = (weighted / present.where(present > 0.0)).where(coverage >= min_coverage)
    return _restore(result, was_series)


def coverage(components: dict[str, pd.Series | pd.DataFrame], weights: dict[str, float]):
    """What share of the weight each instrument actually had a value for.

    Reported separately so a caller can tell a score of NaN caused by thin data
    apart from one caused by a genuinely missing instrument. A composite that
    only returns numbers cannot make that distinction, and a screen that cannot
    make it does not know what it excluded.
    """
    total_weight = sum(weights[name] for name in components)
    was_series = isinstance(next(iter(components.values())), pd.Series)
    present = None
    for name, values in components.items():
        frame, _ = _as_frame(values)
        available = frame.notna().astype("float64") * weights[name]
        present = available if present is None else present + available
    assert present is not None
    return _restore(present / total_weight, was_series)


def top_n(
    values: pd.Series | pd.DataFrame, count: int, direction: str = "higher"
) -> pd.Series | pd.DataFrame:
    """Boolean mask of the best `count` instruments in each cross-section. Catalogue id `top_n`.

    Ties at the boundary are all included, so the mask can select more than
    `count` instruments. Cutting the tie arbitrarily would make the selection
    depend on column order, which is not a property of the data.
    """
    frame, was_series = _as_frame(values)
    ranked = rank(frame, direction, method="min")
    selected = (ranked <= count) & ranked.notna()
    return _restore(selected, was_series)


def quantile_bucket(
    values: pd.Series | pd.DataFrame, buckets: int = 5, direction: str = "higher"
) -> pd.Series | pd.DataFrame:
    """Which fifth, tenth or other slice of the cross-section each instrument is in. Catalogue id `quantile_bucket`.

    Bucket 1 is the best. Built from percentiles rather than from the values
    themselves, so the buckets hold equal numbers of instruments rather than
    equal ranges of value, which is what a factor study means by a quintile.
    """
    if buckets < 2:
        raise ValueError("buckets must be at least 2")
    frame, was_series = _as_frame(values)
    scored = percentile(frame, direction)
    edges = np.ceil((100.0 - scored.to_numpy()) / (100.0 / buckets))
    result = pd.DataFrame(edges, index=frame.index, columns=frame.columns).clip(1, buckets)
    return _restore(result.where(scored.notna()), was_series)
