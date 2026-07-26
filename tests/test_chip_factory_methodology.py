"""Contract tests for the canonical chip-factory methodology catalogue."""

from chip_labs.chip_factory.methodology import (
    CREATION_CHECKLIST,
    PROVEN_PATTERNS,
    get_creation_checklist,
    get_patterns_for_area,
    get_proven_patterns,
)


def test_methodology_helpers_return_canonical_collections() -> None:
    assert get_proven_patterns() is PROVEN_PATTERNS
    assert get_creation_checklist() is CREATION_CHECKLIST


def test_methodology_pattern_ids_and_lanes_are_valid() -> None:
    ids = [pattern["id"] for pattern in PROVEN_PATTERNS]
    assert len(ids) == len(set(ids))
    known_lanes = {
        "research_grounded",
        "benchmark_grounded",
        "realworld_validated",
        "exploratory_frontier",
    }
    assert all(pattern["evidence_lane"] in known_lanes for pattern in PROVEN_PATTERNS)


def test_methodology_checklist_is_sequential() -> None:
    assert [item["step"] for item in CREATION_CHECKLIST] == list(
        range(1, len(CREATION_CHECKLIST) + 1)
    )


def test_unknown_methodology_area_returns_full_catalogue() -> None:
    assert get_patterns_for_area("totally-unknown-area") == PROVEN_PATTERNS
