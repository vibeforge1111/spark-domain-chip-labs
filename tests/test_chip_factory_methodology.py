"""Tests for chip_labs.chip_factory.methodology helpers."""

from __future__ import annotations

import pytest

from chip_labs.chip_factory.methodology import (
    CREATION_CHECKLIST,
    PROVEN_PATTERNS,
    get_creation_checklist,
    get_patterns_for_area,
    get_proven_patterns,
)


def test_get_proven_patterns_returns_documented_set() -> None:
    patterns = get_proven_patterns()
    assert patterns is PROVEN_PATTERNS  # helper returns the canonical list, not a copy
    assert len(patterns) >= 1
    # Every pattern must expose the contract the chip factory + watchtower depend on.
    for p in patterns:
        assert {"id", "label", "description", "evidence_chips", "evidence_lane", "transferable"} <= set(p.keys())


def test_pattern_ids_are_unique() -> None:
    ids = [p["id"] for p in PROVEN_PATTERNS]
    assert len(ids) == len(set(ids)), "duplicate pattern ids would silently collide downstream"


def test_pattern_evidence_lanes_are_in_known_set() -> None:
    # The evidence-lane separation pattern itself names the canonical four lanes;
    # every pattern must declare one of them so promotion gates don't crash.
    known_lanes = {
        "research_grounded",
        "benchmark_grounded",
        "realworld_validated",
        "exploratory_frontier",
    }
    for p in PROVEN_PATTERNS:
        assert p["evidence_lane"] in known_lanes, f"unknown evidence_lane on {p['id']}"


def test_get_creation_checklist_steps_are_sequential() -> None:
    checklist = get_creation_checklist()
    assert checklist is CREATION_CHECKLIST
    assert len(checklist) >= 1
    # Each item must expose step/label/description and the steps must be 1..N.
    for item in checklist:
        assert set(item.keys()) == {"step", "label", "description"}
    steps = [item["step"] for item in checklist]
    assert steps == list(range(1, len(steps) + 1))


def test_get_patterns_for_area_returns_only_matches_for_known_area() -> None:
    matches = get_patterns_for_area("scoring_systems")
    assert len(matches) >= 1
    assert all(p in PROVEN_PATTERNS for p in matches)
    keywords = {"score", "scoring", "rubric", "deterministic"}
    for p in matches:
        # At least one keyword must appear (case-insensitive) in the description.
        assert any(k in p["description"].lower() for k in keywords)


def test_get_patterns_for_area_filters_evidence_lane_terms() -> None:
    matches = get_patterns_for_area("evidence_lanes")
    assert any("evidence" in p["description"].lower() for p in matches)


def test_get_patterns_for_area_returns_full_list_for_unknown_area() -> None:
    # Per the implementation: when no keywords match the area, return the whole catalogue.
    fallback = get_patterns_for_area("totally-unknown-area")
    assert fallback == PROVEN_PATTERNS


def test_get_patterns_for_area_returns_full_list_for_empty_string() -> None:
    fallback = get_patterns_for_area("")
    assert fallback == PROVEN_PATTERNS


@pytest.mark.parametrize(
    "area,required_keyword",
    [
        ("evaluation_frameworks", "evaluator"),
        ("frontier_design", "frontier"),
        ("source_registry", "source"),
        ("packet_quality", "packet"),
        ("graduation_criteria", "graduation"),
    ],
)
def test_get_patterns_for_area_covers_every_documented_area_alias(area: str, required_keyword: str) -> None:
    # Each documented area maps to at least one keyword; for every area, the lookup must
    # at least be addressable (lookup succeeds; may return empty if no pattern matches today,
    # which is fine -- the point is the area->keyword table is honoured).
    matches = get_patterns_for_area(area)
    # If any pattern's description mentions the required keyword, it must surface in matches.
    expected_hits = [p for p in PROVEN_PATTERNS if required_keyword in p["description"].lower()]
    for hit in expected_hits:
        assert hit in matches
