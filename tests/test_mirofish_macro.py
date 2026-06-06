"""Tests for mirofish.macro global context system.

macro.py defines global conditions (economic sentiment, AI displacement
pressure, etc.) that modify ALL persona adoption thresholds across the
simulation. compute_macro_modifier subtracts a clamped amount from the
threshold; generate_macro_signals injects ambient "rising tide" signals.
The clamp + tag-matching contracts are critical — a regression to either
silently changes every simulation outcome.
"""

from __future__ import annotations

from chip_labs.mirofish.macro import (
    MARCH_2026,
    MacroContext,
    apply_macro_event,
    compute_macro_modifier,
    create_macro_event,
    generate_macro_signals,
)


# ----- MacroContext shape -----


def test_macro_context_clamps_constructor_args_to_unit_range() -> None:
    m = MacroContext(
        economic_sentiment=2.0,
        ai_displacement_pressure=-3.0,
        speculative_appetite=0.5,
    )
    assert m.economic_sentiment == 1.0
    assert m.ai_displacement_pressure == -1.0
    assert m.speculative_appetite == 0.5


def test_macro_context_copy_returns_isolated_instance() -> None:
    m = MacroContext(economic_sentiment=0.5)
    m2 = m.copy()
    m2.economic_sentiment = -0.5
    # Mutating the copy must not bleed into the original.
    assert m.economic_sentiment == 0.5
    assert m2.economic_sentiment == -0.5


def test_macro_context_to_dict_rounds_to_three_places() -> None:
    m = MacroContext(economic_sentiment=0.123456)
    assert m.to_dict()["economic_sentiment"] == 0.123


# ----- compute_macro_modifier -----


def test_compute_macro_modifier_empty_tags_returns_zero() -> None:
    m = MacroContext(ai_displacement_pressure=1.0)
    assert compute_macro_modifier(m, []) == 0.0


def test_compute_macro_modifier_clamps_to_unit_band() -> None:
    # All AI dimension tags at full pressure exceed the per-dim cap.
    m = MacroContext(ai_displacement_pressure=1.0)
    big = compute_macro_modifier(
        m, ["career", "reskill", "ai_survival", "productivity", "easy_start"]
    )
    assert -0.15 <= big <= 0.15
    # And specifically, full pressure on career-adjacent tags hits the
    # +0.15 ceiling.
    assert big == 0.15


def test_compute_macro_modifier_neutral_macro_state_returns_zero() -> None:
    m = MacroContext()  # All zeros
    assert compute_macro_modifier(m, ["career", "defi", "compliance"]) == 0.0


def test_compute_macro_modifier_unrelated_tags_return_zero() -> None:
    m = MacroContext(ai_displacement_pressure=1.0)
    assert compute_macro_modifier(m, ["totally-unrelated-tag"]) == 0.0


# ----- create_macro_event + apply_macro_event -----


def test_create_macro_event_returns_expected_shape() -> None:
    ev = create_macro_event(5, "test-event", {"economic_sentiment": 0.2})
    assert ev == {
        "inject_at_round": 5,
        "label": "test-event",
        "changes": {"economic_sentiment": 0.2},
    }


def test_apply_macro_event_mutates_in_place_and_clamps() -> None:
    m = MacroContext(economic_sentiment=0.5)
    apply_macro_event(m, create_macro_event(0, "x", {"economic_sentiment": 0.8}))
    # 0.5 + 0.8 = 1.3 -> clamped to 1.0
    assert m.economic_sentiment == 1.0


def test_apply_macro_event_ignores_unknown_dimensions() -> None:
    m = MacroContext(economic_sentiment=0.5)
    apply_macro_event(m, create_macro_event(0, "x", {"unknown_dim": 9.0}))
    # Unknown dimension is silently skipped.
    assert m.economic_sentiment == 0.5


# ----- generate_macro_signals -----


def test_generate_macro_signals_emits_for_above_threshold_dimensions_only() -> None:
    # MARCH_2026 has ai_displacement_pressure=0.8 (above 0.2 threshold)
    # but speculative_appetite=0.3 (also above) and economic_sentiment=-0.3
    # (abs above 0.2). We supply tags matching ONLY ai_displacement.
    signals = generate_macro_signals(MARCH_2026, {"d1": ["career"]}, round_num=2)
    assert any(s["signal_type"] == "macro_ai_displacement_pressure" for s in signals)
    # All signals should target d1 since it is the only domain.
    for s in signals:
        assert s["affects_domains"] == ["d1"]
        assert s["inject_at_round"] == 2


def test_generate_macro_signals_skips_below_threshold_dimensions() -> None:
    weak = MacroContext(ai_displacement_pressure=0.1)
    # 0.1 is below the abs(0.2) threshold -> no signals emitted.
    signals = generate_macro_signals(weak, {"d1": ["career"]}, round_num=0)
    assert signals == []


def test_generate_macro_signals_returns_empty_when_no_domain_tag_match() -> None:
    signals = generate_macro_signals(MARCH_2026, {"d1": ["unrelated-tag"]}, round_num=0)
    assert signals == []


def test_generate_macro_signals_marks_effect_direction_by_macro_sign() -> None:
    positive = MacroContext(ai_displacement_pressure=0.8)
    negative = MacroContext(ai_displacement_pressure=-0.8)
    pos_sigs = generate_macro_signals(positive, {"d1": ["career"]}, round_num=0)
    neg_sigs = generate_macro_signals(negative, {"d1": ["career"]}, round_num=0)
    assert pos_sigs and pos_sigs[0]["effect"] == "positive"
    assert neg_sigs and neg_sigs[0]["effect"] == "negative"
