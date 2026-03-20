"""Tests for chip_advisor -- pre/post-action advisory middleware."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

from chip_labs.chip_advisor import (
    AdvisoryRequest,
    AdvisoryResponse,
    DoctrineGuidance,
    _classify_guidance,
    _compute_effective_confidence,
    advise_post_action,
    advise_pre_action,
    doctrine_check,
)
from chip_labs.intelligence_server import ChipIntelligence


# ---------------------------------------------------------------------------
# Mock ChipHandle
# ---------------------------------------------------------------------------

@dataclass
class MockChipHandle:
    chip_path: Path = Path("/mock")
    chip_name: str = "test-chip"
    domain: str = "testing"
    version: str = "0.1.0"
    capabilities: list[str] = field(default_factory=lambda: ["evaluate"])
    commands: dict[str, list[str]] = field(default_factory=dict)
    frontier: dict[str, Any] = field(default_factory=dict)
    quality_score: float = 65.0
    quality_verdict: str = "beta"
    intelligence: ChipIntelligence | None = None


def _make_intel(
    chip_name: str = "test-chip",
    domain: str = "testing",
    doctrines: list[dict[str, Any]] | None = None,
    contradictions: list[dict[str, Any]] | None = None,
    score_trajectory: list[int] | None = None,
    evidence_summary: dict[str, int] | None = None,
) -> ChipIntelligence:
    return ChipIntelligence(
        chip_name=chip_name,
        domain=domain,
        version="0.1.0",
        mission="Test mission.",
        doctrines=doctrines or [
            {"claim": "Test claim", "confidence": "high", "evidence_lane": "research_grounded"},
        ],
        contradictions=contradictions or [],
        evidence_summary=evidence_summary or {
            "research_grounded": 5, "benchmark_grounded": 0,
            "exploratory_frontier": 1, "realworld_validated": 0,
        },
        score_trajectory=score_trajectory or [40, 50, 60],
    )


def _make_portfolio(tmp_path: Path | None = None) -> list[MockChipHandle]:
    base = tmp_path or Path("/mock")
    return [
        MockChipHandle(
            chip_path=base / "domain-chip-test",
            chip_name="test-chip",
            domain="testing",
            intelligence=_make_intel(doctrines=[
                {"claim": "Always test before deploy", "confidence": "very high", "evidence_lane": "realworld_validated"},
                {"claim": "Avoid premature optimization", "confidence": "high", "evidence_lane": "research_grounded"},
            ]),
        ),
        MockChipHandle(
            chip_path=base / "domain-chip-startup",
            chip_name="startup-yc",
            domain="startup",
            quality_score=70.0,
            intelligence=_make_intel("startup-yc", "startup", doctrines=[
                {"claim": "Founder velocity matters most", "confidence": "very high"},
                {"claim": "Market size drives exits", "confidence": "high"},
            ], contradictions=[
                {"belief_a": "Move fast", "belief_b": "Move carefully", "status": "open"},
            ], score_trajectory=[30, 45, 60, 64]),
        ),
    ]


# ---------------------------------------------------------------------------
# TestClassifyGuidance
# ---------------------------------------------------------------------------

class TestClassifyGuidance:
    def test_warns_on_warning_keywords(self) -> None:
        result = _classify_guidance("deploy to production", "Never deploy without tests")
        assert result == "warns"

    def test_supports_on_keyword_overlap(self) -> None:
        result = _classify_guidance("test the deploy pipeline", "Always test before deploy")
        assert result == "supports"

    def test_informs_on_low_overlap(self) -> None:
        result = _classify_guidance("update docs", "Market analysis is key")
        assert result == "informs"


# ---------------------------------------------------------------------------
# TestComputeEffectiveConfidence
# ---------------------------------------------------------------------------

class TestComputeEffectiveConfidence:
    def test_very_high_realworld(self) -> None:
        doc = {"confidence": "very high", "evidence_lane": "realworld_validated"}
        score = _compute_effective_confidence(doc)
        assert score == 1.0  # 1.0 base * 1.0 lane weight

    def test_low_exploratory(self) -> None:
        doc = {"confidence": "low", "evidence_lane": "exploratory_frontier"}
        score = _compute_effective_confidence(doc)
        assert score == pytest.approx(0.25 * 0.3)

    def test_missing_lane(self) -> None:
        doc = {"confidence": "high"}
        score = _compute_effective_confidence(doc)
        assert score == pytest.approx(0.75 * 0.5)


# ---------------------------------------------------------------------------
# TestAdvisePreAction
# ---------------------------------------------------------------------------

class TestAdvisePreAction:
    def test_returns_response_with_portfolio(self) -> None:
        portfolio = _make_portfolio()
        request = AdvisoryRequest(action_description="test the deployment")
        response = advise_pre_action(request, portfolio=portfolio)

        assert isinstance(response, AdvisoryResponse)
        assert len(response.chips_consulted) > 0
        assert len(response.guidance) > 0

    def test_empty_portfolio_returns_proceed(self) -> None:
        request = AdvisoryRequest(action_description="anything")
        response = advise_pre_action(request, portfolio=[])
        assert response.verdict == "proceed"
        assert len(response.guidance) == 0

    def test_verdict_caution_with_contradictions(self) -> None:
        portfolio = [MockChipHandle(
            chip_name="conflicted",
            domain="testing",
            intelligence=_make_intel(contradictions=[
                {"belief_a": "A is true", "belief_b": "A is false", "status": "open"},
            ]),
        )]
        request = AdvisoryRequest(action_description="test conflicted domain")
        response = advise_pre_action(request, portfolio=portfolio)
        assert response.verdict in ("caution", "reconsider")

    def test_domain_hint_influences_selection(self) -> None:
        portfolio = _make_portfolio()
        request = AdvisoryRequest(
            action_description="evaluate opportunity",
            domain_hint="startup",
        )
        response = advise_pre_action(request, portfolio=portfolio)
        assert "startup-yc" in response.chips_consulted

    def test_trajectory_context_present(self) -> None:
        portfolio = _make_portfolio()
        request = AdvisoryRequest(action_description="analyze startup")
        response = advise_pre_action(request, portfolio=portfolio)
        assert len(response.trajectory_context) > 0

    def test_uncertainty_areas_detected(self) -> None:
        portfolio = [MockChipHandle(
            chip_name="gaps",
            domain="testing",
            intelligence=_make_intel(evidence_summary={
                "research_grounded": 5, "benchmark_grounded": 0,
                "exploratory_frontier": 1, "realworld_validated": 0,
            }),
        )]
        request = AdvisoryRequest(action_description="test gaps")
        response = advise_pre_action(request, portfolio=portfolio)
        assert len(response.uncertainty_areas) > 0
        assert any("realworld_validated" in u for u in response.uncertainty_areas)

    def test_guidance_sorted_by_relevance(self) -> None:
        portfolio = _make_portfolio()
        request = AdvisoryRequest(action_description="test deployment pipeline")
        response = advise_pre_action(request, portfolio=portfolio)
        if len(response.guidance) >= 2:
            assert response.guidance[0].relevance >= response.guidance[-1].relevance


# ---------------------------------------------------------------------------
# TestAdvisePostAction
# ---------------------------------------------------------------------------

class TestAdvisePostAction:
    def test_writes_feedback(self, tmp_path: Path) -> None:
        chip_dir = tmp_path / "domain-chip-test"
        chip_dir.mkdir()
        portfolio = [MockChipHandle(
            chip_path=chip_dir,
            chip_name="test-chip",
            intelligence=_make_intel(),
        )]

        request = AdvisoryRequest(action_description="ran npm test")
        outcome = {"success": True, "tests_passed": 50}
        result = advise_post_action(request, outcome, portfolio=portfolio)

        assert result["feedback_written"] is True
        assert result["chip_name"] == "test-chip"

        rw_dir = chip_dir / "research" / "realworld_validated"
        files = list(rw_dir.glob("feedback_*.json"))
        assert len(files) == 1

        data = json.loads(files[0].read_text())
        assert data["packet_kind"] == "realworld_feedback"
        assert data["outcome"]["tests_passed"] == 50

    def test_empty_portfolio_returns_false(self) -> None:
        request = AdvisoryRequest(action_description="test")
        result = advise_post_action(request, {}, portfolio=[])
        assert result["feedback_written"] is False


# ---------------------------------------------------------------------------
# TestDoctrineCheck
# ---------------------------------------------------------------------------

class TestDoctrineCheck:
    def test_finds_matching_doctrines(self) -> None:
        portfolio = _make_portfolio()
        results = doctrine_check("test deploy velocity market", portfolio=portfolio)
        assert len(results) > 0
        assert all(isinstance(g, DoctrineGuidance) for g in results)

    def test_empty_portfolio(self) -> None:
        results = doctrine_check("anything", portfolio=[])
        assert results == []

    def test_domain_filter(self) -> None:
        portfolio = _make_portfolio()
        results = doctrine_check("something about startups", portfolio=portfolio, domain="startup")
        for g in results:
            assert g.source_chip == "startup-yc"

    def test_sorted_by_relevance(self) -> None:
        portfolio = _make_portfolio()
        results = doctrine_check("test deploy", portfolio=portfolio)
        if len(results) >= 2:
            assert results[0].relevance >= results[-1].relevance
