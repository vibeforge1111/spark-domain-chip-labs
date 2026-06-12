"""Tests for mirofish.signals decay-curve helpers.

decay_signal supports four curve shapes that drive how simulation rounds
fade a signal's effect on personas: linear (default), exponential
(viral spike), s_curve (build-then-fade), and plateau (sustained then
sharp drop). Only the linear default is touched indirectly by
test_simulation.py — the three non-default curves and the rounds<=0
early return are unpinned, so a future tweak to any branch could go
unobserved.
"""

from __future__ import annotations

import math

from chip_labs.mirofish.signals import (
    build_scenario,
    create_shock,
    create_signal,
    decay_signal,
)


# ----- decay_signal: rounds <= 0 early return -----


def test_decay_signal_returns_base_strength_when_no_rounds_elapsed() -> None:
    sig = {"strength": 0.8, "decay_per_round": 0.1}
    assert decay_signal(sig, 0) == 0.8
    assert decay_signal(sig, -3) == 0.8


# ----- linear (default) -----


def test_decay_signal_linear_default_clamps_at_zero() -> None:
    sig = {"strength": 1.0, "decay_per_round": 0.1}
    # 1.0 - 0.1 * 20 = -1.0 -> clamped to 0.0
    assert decay_signal(sig, 20) == 0.0


def test_decay_signal_linear_decreases_monotonically_until_clamp() -> None:
    sig = {"strength": 1.0, "decay_per_round": 0.1}
    assert decay_signal(sig, 1) > decay_signal(sig, 3) > decay_signal(sig, 5)


# ----- exponential -----


def test_decay_signal_exponential_decays_strictly_faster_than_linear() -> None:
    base = {"strength": 1.0, "decay_per_round": 0.1}
    linear = decay_signal(base, 5)
    exp = decay_signal({**base, "decay_curve": "exponential"}, 5)
    # 3x decay multiplier inside the exp call should drive value below linear.
    assert 0.0 <= exp < linear


def test_decay_signal_exponential_matches_formula() -> None:
    sig = {"strength": 1.0, "decay_per_round": 0.1, "decay_curve": "exponential"}
    expected = round(1.0 * math.exp(-0.1 * 4 * 3), 4)
    assert decay_signal(sig, 4) == expected


# ----- s_curve -----


def test_decay_signal_s_curve_rises_then_decays_after_peak() -> None:
    sig = {"strength": 1.0, "decay_per_round": 0.1, "decay_curve": "s_curve", "peak_round": 5}
    # Below peak it rises (logistic) — pick two points strictly under peak.
    rising_low = decay_signal(sig, 1)
    rising_high = decay_signal(sig, 4)
    # After peak, decay phase starts.
    past_peak = decay_signal(sig, 8)
    assert rising_low < rising_high
    # Past-peak strictly less than the at-peak value (peak itself uses
    # logistic at boundary, so just check we keep decreasing afterwards).
    assert past_peak < decay_signal(sig, 6)


# ----- plateau -----


def test_decay_signal_plateau_holds_then_drops_sharply() -> None:
    sig = {
        "strength": 1.0, "decay_per_round": 0.1,
        "decay_curve": "plateau", "plateau_duration": 5,
    }
    # rise phase
    assert decay_signal(sig, 1) == 0.5
    assert decay_signal(sig, 2) == 1.0
    # plateau phase
    assert decay_signal(sig, 3) == 1.0
    assert decay_signal(sig, 5) == 1.0
    # past plateau the drop uses 3x decay and clamps at 0
    past = decay_signal(sig, 20)
    assert past == 0.0


# ----- create_signal / create_shock / build_scenario -----


def test_create_signal_fills_defaults_from_known_signal_type() -> None:
    sig = create_signal("s1", "viral_tweet", ["dx"])
    assert sig["signal_id"] == "s1"
    assert sig["signal_type"] == "viral_tweet"
    assert sig["affects_domains"] == ["dx"]
    # Known signal type populates label + strength + decay_per_round.
    assert sig["label"]
    assert isinstance(sig["strength"], (int, float))
    assert isinstance(sig["decay_per_round"], (int, float))


def test_create_shock_carries_curve_metadata_when_template_defines_it() -> None:
    # Pick a template — caller provides domain list + round.
    shock = create_shock("breakout_tool", ["dx"], inject_at_round=3)
    assert shock["inject_at_round"] == 3
    assert shock["affects_domains"] == ["dx"]
    # affected_persona_types and signal_type populated from template.
    assert "affected_persona_types" in shock
    assert "signal_type" in shock


def test_build_scenario_sorts_shocks_by_inject_round() -> None:
    shocks = [
        create_shock("breakout_tool", ["dx"], inject_at_round=7),
        create_shock("breakout_tool", ["dx"], inject_at_round=2),
        create_shock("breakout_tool", ["dx"], inject_at_round=5),
    ]
    scenario = build_scenario(shocks, label="ordering")
    rounds = [s["inject_at_round"] for s in scenario["shocks"]]
    assert rounds == sorted(rounds)
    assert scenario["shock_count"] == 3
    assert scenario["label"] == "ordering"
