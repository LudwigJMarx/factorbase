"""Candlestick patterns, each against a bar built to satisfy or break its rule.

Patterns are tested on constructed bars rather than on a generated series. A
pattern that fires eleven times in four hundred random bars tells you nothing
about whether it fired for the right reason.

Every test reaches the implementation through `compute(<catalogue id>, ...)`,
so the catalogue's declared defaults are the ones under test, not the
function's own.
"""

from __future__ import annotations

import pandas as pd

from factorbase import compute


def bars(*rows: tuple[float, float, float, float]) -> pd.DataFrame:
    """Build a price frame from (open, high, low, close) tuples."""
    index = pd.bdate_range("2024-01-01", periods=len(rows))
    return pd.DataFrame(
        {
            "open": [r[0] for r in rows],
            "high": [r[1] for r in rows],
            "low": [r[2] for r in rows],
            "close": [r[3] for r in rows],
        },
        index=index,
    )


def flat_run(count: int, level: float = 100.0, body: float = 1.0) -> list[tuple[float, ...]]:
    """A run of identical small up bars, to give body-length averages something to chew on."""
    return [(level, level + body + 0.2, level - 0.2, level + body)] * count


# ── Single bar ──────────────────────────────────────────────────────────────


def test_cs_doji_fires_when_open_and_close_coincide() -> None:
    frame = bars((100.0, 105.0, 95.0, 100.1))
    assert bool(compute("cs_doji", frame).iloc[-1])


def test_cs_doji_ignores_a_bar_with_a_real_body() -> None:
    frame = bars((100.0, 105.0, 95.0, 104.0))
    assert not bool(compute("cs_doji", frame).iloc[-1])


def test_a_bar_with_no_range_is_not_a_doji() -> None:
    """Zero range cannot be evaluated. Not evaluated is not an occurrence."""
    frame = bars((100.0, 100.0, 100.0, 100.0))
    assert not bool(compute("cs_doji", frame).iloc[-1])


def test_cs_dragonfly_doji_needs_the_upper_shadow_gone() -> None:
    dragonfly = bars((100.0, 100.2, 90.0, 100.0))
    gravestone = bars((100.0, 110.0, 99.8, 100.0))
    assert bool(compute("cs_dragonfly_doji", dragonfly).iloc[-1])
    assert not bool(compute("cs_dragonfly_doji", gravestone).iloc[-1])


def test_cs_gravestone_doji_needs_the_lower_shadow_gone() -> None:
    gravestone = bars((100.0, 110.0, 99.8, 100.0))
    assert bool(compute("cs_gravestone_doji", gravestone).iloc[-1])


def test_cs_spinning_top_wants_a_shadow_on_each_side() -> None:
    top = bars((100.0, 106.0, 94.0, 101.0))
    one_sided = bars((100.0, 112.0, 99.5, 101.0))
    assert bool(compute("cs_spinning_top", top).iloc[-1])
    assert not bool(compute("cs_spinning_top", one_sided).iloc[-1])


def test_cs_big_white_candle_is_measured_against_recent_bodies() -> None:
    """The same bar is long after quiet bars and ordinary after large ones."""
    quiet = bars(*flat_run(25, body=1.0), (100.0, 110.2, 99.8, 110.0))
    busy = bars(*flat_run(25, body=9.0), (100.0, 110.2, 99.8, 110.0))
    assert bool(compute("cs_big_white_candle", quiet).iloc[-1])
    assert not bool(compute("cs_big_white_candle", busy).iloc[-1])


def test_cs_big_black_candle_needs_a_down_bar() -> None:
    down = bars(*flat_run(25, body=1.0), (110.0, 110.2, 99.8, 100.0))
    assert bool(compute("cs_big_black_candle", down).iloc[-1])
    up = bars(*flat_run(25, body=1.0), (100.0, 110.2, 99.8, 110.0))
    assert not bool(compute("cs_big_black_candle", up).iloc[-1])


def test_cs_white_marubozu_tolerates_no_shadows() -> None:
    clean = bars((100.0, 110.0, 100.0, 110.0))
    wicked = bars((100.0, 112.0, 98.0, 110.0))
    assert bool(compute("cs_white_marubozu", clean).iloc[-1])
    assert not bool(compute("cs_white_marubozu", wicked).iloc[-1])


def test_cs_black_marubozu_tolerates_no_shadows() -> None:
    clean = bars((110.0, 110.0, 100.0, 100.0))
    assert bool(compute("cs_black_marubozu", clean).iloc[-1])


def test_cs_hammer_requires_the_decline_before_it() -> None:
    """Same shape, two contexts. The entry says the context is part of the pattern."""
    shape = (100.0, 100.5, 90.0, 100.2)
    after_fall = bars(*[(110.0 - i, 110.5 - i, 109.5 - i, 110.0 - i) for i in range(12)], shape)
    after_rise = bars(*[(100.0 + i, 100.5 + i, 99.5 + i, 100.0 + i) for i in range(12)], shape)
    assert bool(compute("cs_hammer", after_fall).iloc[-1])
    assert not bool(compute("cs_hammer", after_rise).iloc[-1])


def test_cs_shooting_star_requires_the_advance_before_it() -> None:
    shape = (100.0, 110.0, 99.5, 100.2)
    after_rise = bars(*[(90.0 + i, 90.5 + i, 89.5 + i, 90.0 + i) for i in range(12)], shape)
    assert bool(compute("cs_shooting_star", after_rise).iloc[-1])


def test_cs_bullish_belt_hold_opens_at_the_low() -> None:
    frame = bars((100.0, 112.0, 100.0, 110.0))
    assert bool(compute("cs_bullish_belt_hold", frame).iloc[-1])


def test_cs_bearish_belt_hold_opens_at_the_high() -> None:
    frame = bars((110.0, 110.0, 98.0, 100.0))
    assert bool(compute("cs_bearish_belt_hold", frame).iloc[-1])


# ── Two bars ────────────────────────────────────────────────────────────────


def test_cs_bullish_engulfing_compares_bodies_not_ranges() -> None:
    """The second bar's range does not cover the first's, but its body does."""
    frame = bars((105.0, 115.0, 100.0, 101.0), (100.5, 108.0, 100.2, 106.0))
    assert bool(compute("cs_bullish_engulfing", frame).iloc[-1])


def test_cs_bullish_engulfing_rejects_a_body_that_falls_short() -> None:
    frame = bars((105.0, 110.0, 100.0, 101.0), (102.0, 108.0, 101.5, 104.0))
    assert not bool(compute("cs_bullish_engulfing", frame).iloc[-1])


def test_cs_bearish_engulfing_needs_an_up_bar_first() -> None:
    frame = bars((101.0, 106.0, 100.0, 105.0), (106.0, 107.0, 99.0, 100.0))
    assert bool(compute("cs_bearish_engulfing", frame).iloc[-1])


def test_cs_bullish_harami_is_the_engulfing_pattern_in_reverse_order() -> None:
    """Large bar first, small bar inside it. Confusing the two is the usual error."""
    frame = bars((110.0, 111.0, 99.0, 100.0), (102.0, 106.0, 101.0, 105.0))
    assert bool(compute("cs_bullish_harami", frame).iloc[-1])
    assert not bool(compute("cs_bullish_engulfing", frame).iloc[-1])


def test_cs_bearish_harami_needs_an_up_bar_first() -> None:
    frame = bars((100.0, 111.0, 99.0, 110.0), (105.0, 106.0, 101.0, 102.0))
    assert bool(compute("cs_bearish_harami", frame).iloc[-1])


def test_cs_above_the_stomach_clears_the_midpoint_only() -> None:
    """It fires where engulfing does not, which is why it is a separate entry."""
    frame = bars((110.0, 111.0, 99.0, 100.0), (105.5, 108.0, 105.0, 107.0))
    assert bool(compute("cs_above_the_stomach", frame).iloc[-1])
    assert not bool(compute("cs_bullish_engulfing", frame).iloc[-1])


def test_cs_below_the_stomach_clears_the_midpoint_downward() -> None:
    frame = bars((100.0, 111.0, 99.0, 110.0), (104.5, 105.0, 101.0, 102.0))
    assert bool(compute("cs_below_the_stomach", frame).iloc[-1])


# ── Three bars ──────────────────────────────────────────────────────────────


def test_cs_morning_star_needs_the_third_bar_to_penetrate() -> None:
    deep = bars(
        (110.0, 111.0, 99.0, 100.0),
        (99.5, 100.5, 98.5, 99.6),
        (100.0, 107.0, 99.5, 106.0),
    )
    shallow = bars(
        (110.0, 111.0, 99.0, 100.0),
        (99.5, 100.5, 98.5, 99.6),
        (100.0, 102.0, 99.5, 101.0),
    )
    assert bool(compute("cs_morning_star", deep).iloc[-1])
    assert not bool(compute("cs_morning_star", shallow).iloc[-1])


def test_cs_evening_star_needs_the_third_bar_to_penetrate() -> None:
    frame = bars(
        (100.0, 111.0, 99.0, 110.0),
        (110.5, 111.5, 109.5, 110.4),
        (110.0, 110.5, 103.0, 104.0),
    )
    assert bool(compute("cs_evening_star", frame).iloc[-1])


def test_cs_three_white_soldiers_rejects_three_gaps_up() -> None:
    """Each bar must open inside the previous body, not above it."""
    proper = bars(
        *flat_run(21, level=90.0, body=2.0),
        (100.0, 105.2, 99.8, 105.0),
        (103.0, 110.2, 102.8, 110.0),
        (108.0, 115.2, 107.8, 115.0),
    )
    gapped = bars(
        *flat_run(21, level=90.0, body=2.0),
        (100.0, 105.2, 99.8, 105.0),
        (106.0, 110.2, 105.8, 110.0),
        (111.0, 115.2, 110.8, 115.0),
    )
    assert bool(compute("cs_three_white_soldiers", proper).iloc[-1])
    assert not bool(compute("cs_three_white_soldiers", gapped).iloc[-1])


def test_cs_three_black_crows_rejects_three_gaps_down() -> None:
    proper = bars(
        *flat_run(21, level=120.0, body=2.0),
        (115.0, 115.2, 109.8, 110.0),
        (112.0, 112.2, 104.8, 105.0),
        (107.0, 107.2, 99.8, 100.0),
    )
    assert bool(compute("cs_three_black_crows", proper).iloc[-1])


def test_cs_bullish_popgun_uses_ranges_not_bodies() -> None:
    frame = bars(
        (100.0, 110.0, 90.0, 105.0),
        (103.0, 106.0, 101.0, 104.0),
        (102.0, 108.0, 100.0, 107.0),
    )
    assert bool(compute("cs_bullish_popgun", frame).iloc[-1])


def test_cs_bearish_popgun_uses_ranges_not_bodies() -> None:
    frame = bars(
        (100.0, 110.0, 90.0, 105.0),
        (103.0, 106.0, 101.0, 104.0),
        (107.0, 108.0, 100.0, 101.0),
    )
    assert bool(compute("cs_bearish_popgun", frame).iloc[-1])


def test_every_candlestick_entry_returns_booleans(wobble: pd.DataFrame) -> None:
    """One sweep over the family, so a new entry cannot ship returning floats."""
    from factorbase import default_catalog

    candles = [f for f in default_catalog() if f.family == "candlestick"]
    assert len(candles) == 24
    for factor in candles:
        result = compute(factor.id, wobble)
        assert result.dtype == bool, factor.id
        assert len(result) == len(wobble), factor.id


# ── Against the definitions, re-derived from raw OHLC ────────────────────────
#
# The tests above hand each pattern a bar built to satisfy its rule, which
# proves the rule fires and not that the rule is the published one. What
# follows re-states each definition from the raw columns, without calling
# `anatomy` or any other helper the implementations use, and asserts that the
# package agrees across a whole series rather than on one bar.


def raw(frame: pd.DataFrame) -> dict[str, list[float]]:
    return {name: frame[name].tolist() for name in ("open", "high", "low", "close")}


def test_engulfing_agrees_with_the_definition_over_a_whole_series(
    wobble: pd.DataFrame,
) -> None:
    """Nison: the second body covers the first, and the shadows play no part."""
    o, h, low, c = raw(wobble).values()
    expected = [False]
    for i in range(1, len(c)):
        previous_bearish = c[i - 1] < o[i - 1]
        top, bottom = max(o[i], c[i]), min(o[i], c[i])
        previous_top, previous_bottom = max(o[i - 1], c[i - 1]), min(o[i - 1], c[i - 1])
        expected.append(
            c[i] > o[i]
            and previous_bearish
            and bottom <= previous_bottom
            and top >= previous_top
            and abs(c[i] - o[i]) > abs(c[i - 1] - o[i - 1])
        )
    result = compute("cs_bullish_engulfing", wobble).tolist()
    assert sum(expected) > 10
    assert result == expected


def test_harami_is_the_containment_the_other_way_round(wobble: pd.DataFrame) -> None:
    o, h, low, c = raw(wobble).values()
    expected = [False]
    for i in range(1, len(c)):
        top, bottom = max(o[i], c[i]), min(o[i], c[i])
        previous_top, previous_bottom = max(o[i - 1], c[i - 1]), min(o[i - 1], c[i - 1])
        expected.append(
            c[i] > o[i]
            and c[i - 1] < o[i - 1]
            and top <= previous_top
            and bottom >= previous_bottom
            and abs(c[i] - o[i]) < abs(c[i - 1] - o[i - 1])
        )
    assert sum(expected) > 5
    assert compute("cs_bullish_harami", wobble).tolist() == expected


def test_no_bar_is_both_an_engulfing_and_a_harami(wobble: pd.DataFrame) -> None:
    """One contains the other; they cannot hold at once, in either polarity."""
    for engulfing, harami in (
        ("cs_bullish_engulfing", "cs_bullish_harami"),
        ("cs_bearish_engulfing", "cs_bearish_harami"),
    ):
        both = compute(engulfing, wobble) & compute(harami, wobble)
        assert not both.any(), f"{engulfing} and {harami} fired on the same bar"


def test_doji_variants_are_doji(wobble: pd.DataFrame) -> None:
    """Dragonfly and gravestone add a shadow condition to the doji rule, so
    every bar they fire on must also be a doji under the same threshold."""
    plain = compute("cs_doji", wobble)
    for narrow in ("cs_dragonfly_doji", "cs_gravestone_doji"):
        assert (compute(narrow, wobble) <= plain).all()


def test_a_marubozu_is_a_belt_hold_but_not_the_reverse(wobble: pd.DataFrame) -> None:
    """A marubozu has no shadow at either end; a belt hold tolerates one at the
    far end. The stricter pattern is a subset of the looser one."""
    marubozu = compute("cs_white_marubozu", wobble)
    belt = compute("cs_bullish_belt_hold", wobble)
    assert (marubozu <= belt).all()


def test_every_candlestick_agrees_with_its_own_polarity(wobble: pd.DataFrame) -> None:
    """A pattern named bullish must fire only on an up bar, and one named
    bearish only on a down bar. Checked against the raw columns."""
    up = wobble["close"] > wobble["open"]
    down = wobble["close"] < wobble["open"]
    bullish = [
        "cs_bullish_engulfing",
        "cs_bullish_harami",
        "cs_bullish_belt_hold",
        "cs_bullish_popgun",
        "cs_big_white_candle",
        "cs_white_marubozu",
        "cs_above_the_stomach",
        "cs_morning_star",
    ]
    bearish = [
        "cs_bearish_engulfing",
        "cs_bearish_harami",
        "cs_bearish_belt_hold",
        "cs_bearish_popgun",
        "cs_big_black_candle",
        "cs_black_marubozu",
        "cs_below_the_stomach",
        "cs_evening_star",
    ]
    for name in bullish:
        assert (compute(name, wobble) <= up).all(), name
    for name in bearish:
        assert (compute(name, wobble) <= down).all(), name
