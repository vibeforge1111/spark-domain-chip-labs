"""Tests for chip_factory.methodology knowledge-base helpers.

methodology.py exposes three readers (get_proven_patterns,
get_creation_checklist, get_patterns_for_area) that other chip-factory
components consult when deciding how to design a new chip. The shape of
the returned payloads is consumed by templates and packets downstream, so
silent shape drift on these constants is the kind of regression that
shows up far from the root cause.
"""

from __future__ import annotations

from chip_labs.chip_factory import methodology


PATTERN_REQUIRED_FIELDS = {
    "id",
    "label",
    "description",
    "evidence_chips",
    "evidence_lane",
    "transferable",
}
CHECKLIST_REQUIRED_FIELDS = {"step", "label", "description"}


def test_proven_patterns_have_unique_ids_and_required_fields() -> None:
    patterns = methodology.get_proven_patterns()
    assert patterns, "PROVEN_PATTERNS should not be empty"
    ids = [p["id"] for p in patterns]
    assert len(ids) == len(set(ids)), "pattern ids must be unique"
    for p in patterns:
        missing = PATTERN_REQUIRED_FIELDS - set(p.keys())
        assert not missing, f"pattern {p.get('id')} missing fields: {missing}"
        assert isinstance(p["evidence_chips"], list) and p["evidence_chips"], (
            f"pattern {p['id']} must list evidence_chips"
        )
        assert isinstance(p["transferable"], bool)


def test_creation_checklist_is_sequential_starting_at_one() -> None:
    checklist = methodology.get_creation_checklist()
    assert checklist, "CREATION_CHECKLIST should not be empty"
    steps = [item["step"] for item in checklist]
    assert steps == list(range(1, len(steps) + 1)), (
        "checklist steps must be consecutive integers starting at 1"
    )
    for item in checklist:
        missing = CHECKLIST_REQUIRED_FIELDS - set(item.keys())
        assert not missing, f"checklist step {item.get('step')} missing fields: {missing}"
        assert isinstance(item["label"], str) and item["label"].strip()
        assert isinstance(item["description"], str) and item["description"].strip()


def test_get_patterns_for_area_unknown_area_returns_full_pattern_list() -> None:
    # Unknown areas fall back to the full proven-patterns list (defensive default).
    full = methodology.get_proven_patterns()
    assert methodology.get_patterns_for_area("not-a-real-area") == full


def test_get_patterns_for_area_filters_by_keyword() -> None:
    # 'evaluation_frameworks' keys on evaluator/scoring/metric/baseline.
    matched = methodology.get_patterns_for_area("evaluation_frameworks")
    assert matched, "should match at least one proven pattern"
    descriptions = " ".join(p["description"].lower() for p in matched)
    assert any(k in descriptions for k in ("evaluator", "scoring", "metric", "baseline"))


def test_get_patterns_for_area_empty_string_falls_back_to_full() -> None:
    full = methodology.get_proven_patterns()
    assert methodology.get_patterns_for_area("") == full


def test_compatibility_alias_module_exposes_same_helpers() -> None:
    # chip_labs.methodology is a thin compatibility alias that re-exports
    # the chip_factory.methodology module. Both surfaces must agree.
    from chip_labs import methodology as alias_module

    assert alias_module.get_proven_patterns() == methodology.get_proven_patterns()
    assert alias_module.get_creation_checklist() == methodology.get_creation_checklist()
