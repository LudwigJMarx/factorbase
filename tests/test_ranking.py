"""Cross-sectional transforms.

These are the only factors in the package that need more than one instrument,
so the fixtures here are cross-sections rather than price series.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from factorbase.factors.ranking import (
    composite_score,
    coverage,
    percentile,
    quantile_bucket,
    rank,
    top_n,
    z_score,
)


@pytest.fixture
def cross_section() -> pd.Series:
    """Five instruments, one date, with a tie and a gap."""
    return pd.Series(
        {"AAA": 10.0, "BBB": 30.0, "CCC": 30.0, "DDD": 5.0, "EEE": np.nan},
        name=pd.Timestamp("2024-06-28"),
    )


def test_rank_puts_the_best_first(cross_section: pd.Series) -> None:
    ranked = rank(cross_section, direction="higher")
    assert ranked["DDD"] == 4.0
    assert ranked["AAA"] == 3.0


def test_direction_inverts_the_ranking(cross_section: pd.Series) -> None:
    """Passing it wrong inverts the strategy and looks entirely reasonable."""
    high = rank(cross_section, direction="higher")
    low = rank(cross_section, direction="lower")
    assert high["DDD"] == 4.0
    assert low["DDD"] == 1.0


def test_ties_share_the_average_position(cross_section: pd.Series) -> None:
    ranked = rank(cross_section, direction="higher")
    assert ranked["BBB"] == ranked["CCC"] == 1.5


def test_a_missing_value_is_not_ranked_last(cross_section: pd.Series) -> None:
    """Ranking it last is how a screen buys whatever its vendor failed to cover."""
    ranked = rank(cross_section, direction="higher")
    assert np.isnan(ranked["EEE"])
    assert ranked.max() == 4.0


def test_an_undefined_direction_is_rejected(cross_section: pd.Series) -> None:
    with pytest.raises(ValueError, match="cannot be ranked"):
        rank(cross_section, direction="undefined")


def test_percentile_is_comparable_across_universe_sizes() -> None:
    """A rank of 40 means two different things in a set of 50 and one of 3000."""
    small = pd.Series({f"S{i}": float(i) for i in range(50)})
    large = pd.Series({f"L{i}": float(i) for i in range(3000)})
    assert percentile(small).max() == pytest.approx(100.0)
    assert percentile(large).max() == pytest.approx(100.0)
    assert percentile(small).min() == pytest.approx(0.0)


def test_percentile_of_a_single_instrument_is_the_middle() -> None:
    lonely = pd.Series({"AAA": 7.0})
    assert percentile(lonely)["AAA"] == pytest.approx(50.0)


def test_z_score_keeps_the_spacing_a_rank_discards() -> None:
    values = pd.Series({"A": 1.0, "B": 2.0, "C": 100.0})
    ranked = rank(values)
    scored = z_score(values)
    assert ranked["A"] - ranked["B"] == pytest.approx(ranked["B"] - ranked["C"])
    assert abs(scored["C"] - scored["B"]) > abs(scored["B"] - scored["A"])


def test_winsorising_pulls_in_the_outlier() -> None:
    """One extreme value moves the mean and the deviation, and so moves everybody else."""
    values = pd.Series({f"N{i}": float(i) for i in range(100)} | {"OUT": 10_000.0})
    raw = z_score(values, winsorise=0.0)
    clipped = z_score(values, winsorise=5.0)
    assert clipped["OUT"] < raw["OUT"]
    assert abs(raw["N0"]) < 0.2
    assert abs(clipped["N0"]) > 1.0


def test_z_score_flips_sign_for_a_lower_is_better_factor() -> None:
    values = pd.Series({"A": 1.0, "B": 5.0, "C": 9.0})
    assert z_score(values, "higher")["C"] == pytest.approx(-z_score(values, "lower")["C"])


# ── Composite ───────────────────────────────────────────────────────────────


@pytest.fixture
def components() -> dict[str, pd.Series]:
    return {
        "value": pd.Series({"AAA": 5.0, "BBB": 10.0, "CCC": 20.0, "DDD": 40.0}),
        "quality": pd.Series({"AAA": 40.0, "BBB": 30.0, "CCC": 20.0, "DDD": 10.0}),
    }


def test_composite_combines_percentiles_not_raw_values(components: dict[str, pd.Series]) -> None:
    """The two components are an order of magnitude apart. Raw sums would be one factor."""
    score = composite_score(
        components,
        weights={"value": 0.5, "quality": 0.5},
        directions={"value": "higher", "quality": "higher"},
    )
    assert score["AAA"] == pytest.approx(50.0)
    assert score["DDD"] == pytest.approx(50.0)


def test_composite_respects_the_weights(components: dict[str, pd.Series]) -> None:
    score = composite_score(
        components,
        weights={"value": 0.9, "quality": 0.1},
        directions={"value": "higher", "quality": "higher"},
    )
    assert score["DDD"] > score["AAA"]


def test_composite_refuses_to_score_an_instrument_missing_a_component(
    components: dict[str, pd.Series],
) -> None:
    """Renormalising the rest would apply a different strategy to that one row."""
    thin = {
        "value": components["value"],
        "quality": components["quality"].copy(),
    }
    thin["quality"]["BBB"] = np.nan
    score = composite_score(
        thin,
        weights={"value": 0.5, "quality": 0.5},
        directions={"value": "higher", "quality": "higher"},
    )
    assert np.isnan(score["BBB"])
    assert score.notna().sum() == 3


def test_a_lower_minimum_coverage_admits_the_thin_row(components: dict[str, pd.Series]) -> None:
    thin = {"value": components["value"], "quality": components["quality"].copy()}
    thin["quality"]["BBB"] = np.nan
    score = composite_score(
        thin,
        weights={"value": 0.5, "quality": 0.5},
        directions={"value": "higher", "quality": "higher"},
        min_coverage=0.5,
    )
    assert not np.isnan(score["BBB"])


def test_coverage_tells_thin_data_from_a_missing_instrument(
    components: dict[str, pd.Series],
) -> None:
    """A composite that only returns numbers cannot make this distinction."""
    thin = {"value": components["value"], "quality": components["quality"].copy()}
    thin["quality"]["BBB"] = np.nan
    share = coverage(thin, weights={"value": 0.5, "quality": 0.5})
    assert share["BBB"] == pytest.approx(0.5)
    assert share["AAA"] == pytest.approx(1.0)


def test_composite_requires_a_weight_and_a_direction_for_every_component(
    components: dict[str, pd.Series],
) -> None:
    with pytest.raises(ValueError, match="no weight given"):
        composite_score(components, {"value": 1.0}, {"value": "higher", "quality": "higher"})
    with pytest.raises(ValueError, match="no direction given"):
        composite_score(components, {"value": 0.5, "quality": 0.5}, {"value": "higher"})


def test_composite_rejects_an_empty_component_set() -> None:
    with pytest.raises(ValueError, match="at least one component"):
        composite_score({}, {}, {})


# ── Selection ───────────────────────────────────────────────────────────────


def test_top_n_includes_every_instrument_tied_at_the_boundary() -> None:
    """Cutting the tie would make selection depend on column order."""
    values = pd.Series({"A": 10.0, "B": 10.0, "C": 5.0, "D": 1.0})
    selected = top_n(values, count=1)
    assert selected["A"] and selected["B"]
    assert not selected["C"]
    assert int(selected.sum()) == 2


def test_quantile_buckets_hold_equal_counts_not_equal_ranges() -> None:
    """A skewed universe would otherwise put nine tenths of itself in one bucket."""
    values = pd.Series({f"N{i}": float(i) ** 4 for i in range(100)})
    buckets = quantile_bucket(values, buckets=5)
    counts = buckets.value_counts()
    assert set(counts.index) == {1.0, 2.0, 3.0, 4.0, 5.0}
    assert counts.min() >= 19
    assert counts.max() <= 21


def test_the_best_instrument_lands_in_the_first_bucket() -> None:
    values = pd.Series({f"N{i}": float(i) for i in range(50)})
    assert quantile_bucket(values, buckets=5)["N49"] == 1.0


def test_buckets_below_two_are_rejected() -> None:
    with pytest.raises(ValueError, match="at least 2"):
        quantile_bucket(pd.Series({"A": 1.0, "B": 2.0}), buckets=1)


# ── Panels ──────────────────────────────────────────────────────────────────


def test_a_panel_is_ranked_within_each_date_not_across_them() -> None:
    """Ranking across dates would compare an instrument today with another last year."""
    panel = pd.DataFrame(
        {"AAA": [1.0, 100.0], "BBB": [2.0, 50.0]},
        index=pd.to_datetime(["2024-01-31", "2024-02-29"]),
    )
    ranked = rank(panel)
    assert ranked.loc[pd.Timestamp("2024-01-31"), "BBB"] == 1.0
    assert ranked.loc[pd.Timestamp("2024-02-29"), "AAA"] == 1.0


def test_a_series_returns_a_series_and_a_frame_returns_a_frame(
    cross_section: pd.Series,
) -> None:
    assert isinstance(rank(cross_section), pd.Series)
    assert isinstance(rank(cross_section.to_frame().T), pd.DataFrame)


# ── Through the catalogue ───────────────────────────────────────────────────


def test_every_cross_sectional_entry_runs_from_the_catalogue(
    cross_section: pd.Series,
) -> None:
    """The catalogue's declared defaults, not the functions' own.

    `composite_score` is left out: it takes a mapping of components rather than
    one cross-section, so it cannot be driven from a single positional
    argument. Its own tests above cover it.
    """
    from factorbase import compute, default_catalog
    from factorbase.schema import Kind

    composites = default_catalog().of_kind(Kind.COMPOSITE)
    assert len(composites) == 6
    driven = 0
    for factor in composites:
        if factor.id == "composite_score":
            continue
        result = compute(factor.id, cross_section)
        assert isinstance(result, pd.Series), factor.id
        assert set(result.index) == set(cross_section.index), factor.id
        driven += 1
    assert driven == 5


def test_factor_rank_from_the_catalogue_uses_its_declared_default(
    cross_section: pd.Series,
) -> None:
    from factorbase import compute

    assert compute("factor_rank", cross_section).equals(rank(cross_section, "higher"))


def test_factor_percentile_and_factor_z_score_are_reachable_by_id(
    cross_section: pd.Series,
) -> None:
    from factorbase import compute

    assert compute("factor_percentile", cross_section).equals(percentile(cross_section))
    assert compute("factor_z_score", cross_section).equals(z_score(cross_section))
