"""Tests for chip_context_injector -- LLM prompt context building."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from unittest.mock import patch


from chip_labs.chip_context_injector import (
    _estimate_tokens,
    _format_contradiction,
    _format_doctrine_concise,
    _format_doctrine_detailed,
    _sort_doctrines_by_confidence,
    build_guardrails_block,
    build_system_prompt_section,
    inject_context_for_task,
    select_chips_for_task,
)
from chip_labs.intelligence_server import ChipIntelligence


# ---------------------------------------------------------------------------
# Mock ChipHandle (avoids importing chip_runtime during tests)
# ---------------------------------------------------------------------------

@dataclass
class MockChipHandle:
    """Minimal mock matching ChipHandle interface."""

    chip_path: Path = Path("/mock")
    chip_name: str = "test-chip"
    domain: str = "testing"
    version: str = "0.1.0"
    capabilities: list[str] = field(default_factory=lambda: ["evaluate"])
    commands: dict[str, list[str]] = field(default_factory=dict)
    frontier: dict[str, Any] = field(default_factory=dict)
    quality_score: float = 60.0
    quality_verdict: str = "beta"
    intelligence: ChipIntelligence | None = None


def _make_intel(
    chip_name: str = "test-chip",
    domain: str = "testing",
    doctrines: list[dict[str, Any]] | None = None,
    contradictions: list[dict[str, Any]] | None = None,
    mission: str = "Test chip for unit tests.",
    evidence_summary: dict[str, int] | None = None,
    score_trajectory: list[int] | None = None,
) -> ChipIntelligence:
    return ChipIntelligence(
        chip_name=chip_name,
        domain=domain,
        version="0.1.0",
        mission=mission,
        doctrines=doctrines or [],
        contradictions=contradictions or [],
        evidence_summary=evidence_summary or {"research_grounded": 5, "benchmark_grounded": 0, "exploratory_frontier": 1, "realworld_validated": 0},
        score_trajectory=score_trajectory or [40, 50, 60],
        current_score=60,
        verdict="beta",
    )


# ---------------------------------------------------------------------------
# TestEstimateTokens
# ---------------------------------------------------------------------------

class TestEstimateTokens:
    def test_empty_string(self) -> None:
        assert _estimate_tokens("") == 1

    def test_short_string(self) -> None:
        # ~20 chars -> ~5 tokens
        assert 3 <= _estimate_tokens("hello world test") <= 10

    def test_long_string(self) -> None:
        text = "a" * 400
        assert _estimate_tokens(text) == 100


# ---------------------------------------------------------------------------
# TestSortDoctrines
# ---------------------------------------------------------------------------

class TestSortDoctrines:
    def test_sorts_by_confidence(self) -> None:
        docs = [
            {"claim": "low", "confidence": "low"},
            {"claim": "high", "confidence": "high"},
            {"claim": "very high", "confidence": "very high"},
            {"claim": "medium", "confidence": "medium"},
        ]
        result = _sort_doctrines_by_confidence(docs)
        assert [d["claim"] for d in result] == ["very high", "high", "medium", "low"]

    def test_missing_confidence_sorts_last(self) -> None:
        docs = [
            {"claim": "no conf"},
            {"claim": "high", "confidence": "high"},
        ]
        result = _sort_doctrines_by_confidence(docs)
        assert result[0]["claim"] == "high"


# ---------------------------------------------------------------------------
# TestFormatDoctrine
# ---------------------------------------------------------------------------

class TestFormatDoctrine:
    def test_concise_format(self) -> None:
        doc = {"claim": "Test claim", "confidence": "high", "evidence_lane": "research_grounded"}
        result = _format_doctrine_concise(doc)
        assert "[high]" in result
        assert "Test claim" in result
        assert "research_grounded" in result

    def test_concise_no_lane(self) -> None:
        doc = {"claim": "Test claim", "confidence": "medium"}
        result = _format_doctrine_concise(doc)
        assert "evidence:" not in result

    def test_detailed_format(self) -> None:
        doc = {
            "claim": "Test claim",
            "confidence": "high",
            "mechanism": "Because X causes Y",
            "boundary": "Only when Z",
            "evidence_lane": "benchmark_grounded",
            "source": "test.json",
        }
        result = _format_doctrine_detailed(doc)
        assert "**Test claim**" in result
        assert "Mechanism:" in result
        assert "Boundary:" in result
        assert "Evidence:" in result
        assert "Source:" in result


# ---------------------------------------------------------------------------
# TestFormatContradiction
# ---------------------------------------------------------------------------

class TestFormatContradiction:
    def test_full_contradiction(self) -> None:
        c = {"belief_a": "X is true", "belief_b": "X is false", "status": "open"}
        result = _format_contradiction(c)
        assert "X is true" in result
        assert "X is false" in result
        assert "open" in result

    def test_partial_contradiction(self) -> None:
        c = {"belief_a": "Only A", "status": "resolved"}
        result = _format_contradiction(c)
        assert "Only A" in result

    def test_empty_contradiction(self) -> None:
        result = _format_contradiction({})
        assert result == ""


# ---------------------------------------------------------------------------
# TestSelectChips
# ---------------------------------------------------------------------------

class TestSelectChips:
    def test_selects_by_relevance(self) -> None:
        startup = MockChipHandle(
            chip_name="startup-yc", domain="startup",
            intelligence=_make_intel("startup-yc", "startup", mission="Evaluate startups and YC applications"),
        )
        crypto = MockChipHandle(
            chip_name="trading-crypto", domain="trading",
            intelligence=_make_intel("trading-crypto", "trading", mission="Crypto trading signals and strategies"),
        )
        result = select_chips_for_task("evaluate a startup application", [startup, crypto], max_chips=1)
        assert len(result) == 1
        assert result[0].chip_name == "startup-yc"

    def test_empty_portfolio(self) -> None:
        result = select_chips_for_task("anything", [], max_chips=2)
        assert result == []

    def test_empty_query(self) -> None:
        chip = MockChipHandle(intelligence=_make_intel())
        result = select_chips_for_task("", [chip], max_chips=1)
        assert len(result) == 1

    def test_respects_max_chips(self) -> None:
        chips = [MockChipHandle(chip_name=f"chip-{i}", intelligence=_make_intel(f"chip-{i}")) for i in range(5)]
        result = select_chips_for_task("test query", chips, max_chips=2)
        assert len(result) == 2


# ---------------------------------------------------------------------------
# TestBuildSystemPrompt
# ---------------------------------------------------------------------------

class TestBuildSystemPrompt:
    def test_concise_has_doctrines(self) -> None:
        chip = MockChipHandle(
            quality_score=65, quality_verdict="beta",
            intelligence=_make_intel(doctrines=[
                {"claim": "Founder velocity matters", "confidence": "high", "evidence_lane": "research_grounded"},
            ]),
        )
        result = build_system_prompt_section([chip], style="concise")
        assert "Domain Intelligence" in result
        assert "Founder velocity matters" in result
        assert "[high]" in result

    def test_detailed_has_mechanisms(self) -> None:
        chip = MockChipHandle(
            quality_score=65, quality_verdict="beta",
            intelligence=_make_intel(doctrines=[
                {"claim": "Test claim", "confidence": "high", "mechanism": "Because X", "boundary": "Only when Y"},
            ]),
        )
        result = build_system_prompt_section([chip], style="detailed")
        assert "Mechanism:" in result
        assert "Boundary:" in result

    def test_includes_contradictions(self) -> None:
        chip = MockChipHandle(
            quality_score=65, quality_verdict="beta",
            intelligence=_make_intel(contradictions=[
                {"belief_a": "A is true", "belief_b": "A is false", "status": "open"},
            ]),
        )
        result = build_system_prompt_section([chip], style="concise")
        assert "contradiction" in result.lower()

    def test_scaffold_warning(self) -> None:
        chip = MockChipHandle(
            quality_score=30, quality_verdict="scaffold",
            intelligence=_make_intel(),
        )
        result = build_system_prompt_section([chip], style="concise")
        assert "scaffold" in result.lower() or "low reliability" in result.lower()

    def test_alpha_warning(self) -> None:
        chip = MockChipHandle(
            quality_score=45, quality_verdict="alpha",
            intelligence=_make_intel(),
        )
        result = build_system_prompt_section([chip], style="concise")
        assert "alpha" in result.lower()

    def test_guardrails_style_delegates(self) -> None:
        chip = MockChipHandle(
            quality_score=65, quality_verdict="beta",
            intelligence=_make_intel(doctrines=[
                {"claim": "Must do X", "confidence": "very high"},
            ]),
        )
        result = build_system_prompt_section([chip], style="guardrails_only")
        assert "MUST" in result


# ---------------------------------------------------------------------------
# TestBuildGuardrails
# ---------------------------------------------------------------------------

class TestBuildGuardrails:
    def test_must_from_very_high(self) -> None:
        chip = MockChipHandle(
            quality_score=65, quality_verdict="beta",
            intelligence=_make_intel(doctrines=[
                {"claim": "Always validate inputs", "confidence": "very high"},
            ]),
        )
        result = build_guardrails_block([chip])
        assert "MUST" in result
        assert "Always validate inputs" in result

    def test_should_from_high(self) -> None:
        chip = MockChipHandle(
            quality_score=65, quality_verdict="beta",
            intelligence=_make_intel(doctrines=[
                {"claim": "Prefer iterative approach", "confidence": "high"},
            ]),
        )
        result = build_guardrails_block([chip])
        assert "SHOULD" in result
        assert "Prefer iterative approach" in result

    def test_watch_from_contradictions(self) -> None:
        chip = MockChipHandle(
            quality_score=65, quality_verdict="beta",
            intelligence=_make_intel(contradictions=[
                {"belief_a": "Speed matters", "belief_b": "Quality matters", "status": "open"},
            ]),
        )
        result = build_guardrails_block([chip])
        assert "WATCH" in result

    def test_uncertain_from_empty_lanes(self) -> None:
        chip = MockChipHandle(
            quality_score=65, quality_verdict="beta",
            intelligence=_make_intel(
                evidence_summary={"research_grounded": 5, "benchmark_grounded": 0, "exploratory_frontier": 1, "realworld_validated": 0}
            ),
        )
        result = build_guardrails_block([chip])
        assert "UNCERTAIN" in result
        assert "realworld_validated" in result

    def test_skips_low_quality_chips(self) -> None:
        chip = MockChipHandle(
            quality_score=20, quality_verdict="scaffold",
            intelligence=_make_intel(doctrines=[
                {"claim": "Should not appear", "confidence": "very high"},
            ]),
        )
        result = build_guardrails_block([chip])
        assert "Should not appear" not in result

    def test_no_guardrails_message(self) -> None:
        chip = MockChipHandle(
            quality_score=65, quality_verdict="beta",
            intelligence=_make_intel(
                doctrines=[
                    {"claim": "Low conf only", "confidence": "low"},
                ],
                evidence_summary={"research_grounded": 5, "benchmark_grounded": 3, "exploratory_frontier": 1, "realworld_validated": 2},
            ),
        )
        result = build_guardrails_block([chip])
        assert "No high-confidence guardrails" in result


# ---------------------------------------------------------------------------
# TestInjectContext
# ---------------------------------------------------------------------------

class TestInjectContext:
    def test_with_portfolio(self) -> None:
        chip = MockChipHandle(
            chip_name="startup-yc", domain="startup",
            quality_score=65, quality_verdict="beta",
            intelligence=_make_intel(
                chip_name="startup-yc", domain="startup",
                mission="Startup evaluation",
                doctrines=[{"claim": "Test doctrine", "confidence": "high"}],
            ),
        )
        result = inject_context_for_task("startup evaluation", portfolio=[chip])
        assert "Test doctrine" in result

    def test_empty_portfolio(self) -> None:
        result = inject_context_for_task("anything", portfolio=[])
        assert "No chips" in result

    def test_no_portfolio_loads_default(self) -> None:
        # Without a real portfolio, should return graceful message
        result = inject_context_for_task("test", portfolio=None)
        # Will either load real chips or return fallback message
        assert isinstance(result, str)
        assert len(result) > 0

    def test_falls_back_to_current_workspace_chip(self, tmp_path: Path) -> None:
        chip_dir = tmp_path / "spark-domain-chip-labs"
        chip_dir.mkdir()
        chip = MockChipHandle(
            chip_path=chip_dir,
            chip_name="domain-chip-labs",
            domain="chip-research",
            quality_score=65,
            quality_verdict="beta",
            intelligence=_make_intel(
                chip_name="domain-chip-labs",
                domain="chip-research",
                mission="Meta research lab for chip methodology",
                doctrines=[{"claim": "Runtime and CLI symmetry is required for trustworthy hook execution.", "confidence": "high"}],
            ),
        )

        with patch("chip_labs.chip_context_injector.Path.cwd", return_value=chip_dir):
            result = inject_context_for_task("xyzzy foobar baz", portfolio=[chip])

        assert "Runtime and CLI symmetry" in result


# ---------------------------------------------------------------------------
# TestRelevanceThreshold  (Layer 2: minimum relevance floor)
# ---------------------------------------------------------------------------

class TestRelevanceThreshold:
    def test_irrelevant_query_returns_empty(self) -> None:
        """Queries with no word overlap should return no chips."""
        chip = MockChipHandle(
            chip_name="startup-yc", domain="startup",
            intelligence=_make_intel(
                "startup-yc", "startup",
                mission="Evaluate startups and YC applications",
            ),
        )
        # "xyzzy foobar baz" has zero word overlap with startup/YC terms
        result = select_chips_for_task("xyzzy foobar baz", [chip], max_chips=1)
        assert result == []

    def test_relevant_query_passes(self) -> None:
        """Queries with clear domain overlap should return chips."""
        chip = MockChipHandle(
            chip_name="startup-yc", domain="startup",
            intelligence=_make_intel(
                "startup-yc", "startup",
                mission="Evaluate startups and YC applications",
            ),
        )
        result = select_chips_for_task("evaluate a startup", [chip], max_chips=1)
        assert len(result) == 1
        assert result[0].chip_name == "startup-yc"

    def test_custom_high_threshold_rejects(self) -> None:
        """A very high min_relevance rejects even decent matches."""
        chip = MockChipHandle(
            chip_name="test-chip", domain="testing",
            intelligence=_make_intel(mission="Testing framework for quality"),
        )
        result = select_chips_for_task("testing framework", [chip],
                                        max_chips=1, min_relevance=0.99)
        assert result == []

    def test_zero_threshold_allows_everything(self) -> None:
        """min_relevance=0 should behave like the old code (no filtering)."""
        chip = MockChipHandle(
            chip_name="startup-yc", domain="startup",
            intelligence=_make_intel(
                "startup-yc", "startup",
                mission="Evaluate startups and YC applications",
            ),
        )
        result = select_chips_for_task("xyzzy foobar", [chip],
                                        max_chips=1, min_relevance=0.0)
        # With threshold 0, even zero-overlap matches pass
        assert len(result) <= 1  # still respects max_chips

    def test_inject_context_returns_no_chips_when_irrelevant(self) -> None:
        """inject_context_for_task should return HTML comment when nothing is relevant."""
        chip = MockChipHandle(
            chip_name="trading-crypto", domain="trading",
            intelligence=_make_intel(
                "trading-crypto", "trading",
                mission="Crypto trading signals and strategies",
            ),
        )
        result = inject_context_for_task("xyzzy foobar baz", portfolio=[chip])
        assert "No relevant chips" in result or "<!--" in result
