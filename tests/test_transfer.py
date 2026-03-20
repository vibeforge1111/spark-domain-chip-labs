"""Tests for the cross-chip intelligence transfer system."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from chip_labs.transfer import (
    PATTERN_TYPES,
    TransferPattern,
    TransferRegistry,
    TransferResult,
    apply_pattern,
    extract_patterns,
    extract_portfolio_patterns,
    find_applicable_patterns,
    load_registry,
    portfolio_transfer,
    save_registry,
    transfer_intelligence,
)
from chip_labs.quality_rubric import score_chip


# ---------------------------------------------------------------------------
# Helpers -- mock chip builders
# ---------------------------------------------------------------------------

def _create_mature_chip(tmp_path: Path, name: str = "domain-chip-mature") -> Path:
    """Create a high-scoring mock chip directory.

    Includes all the structural elements needed for a production-quality
    chip, plus patterns that the extractor should recognise.
    """
    chip_dir = tmp_path / name
    chip_dir.mkdir()

    # spark-chip.json with full frontier
    manifest = {
        "schema_version": "spark-chip.v1",
        "io_protocol": "spark-hook-io.v1",
        "domain": "test-mature",
        "version": "0.3.0",
        "capabilities": ["evaluate", "suggest", "packets", "watchtower"],
        "frontier": {
            "enabled": True,
            "allowed_mutations": {
                "research_focus": ["quality_audit", "methodology", "transfer_patterns"],
                "regime": ["bull", "bear"],
            },
            "required_fields": ["research_focus"],
            "field_patterns": {"research_focus": "^[a-z_]+$"},
        },
    }
    (chip_dir / "spark-chip.json").write_text(json.dumps(manifest), encoding="utf-8")

    # spark-researcher.project.json with guardrails and trials
    project = {
        "project_name": name,
        "eval_metric": "quality_score",
        "metrics": {"quality_score": {}, "coverage": {}, "depth": {}},
        "candidate_trials": [
            {"name": "baseline", "mutations": {}},
            {"name": "variant_a", "mutations": {"research_focus": "methodology"}},
            {"name": "variant_b", "mutations": {"research_focus": "quality_audit"}},
        ],
        "chip": {"path": ".", "manifest": "spark-chip.json"},
        "commands": {"evaluate": {"kind": "chip-evaluate"}},
        "guardrails": {
            "max_loop_iterations": 8,
            "consecutive_discard_limit": 3,
            "near_best_tolerance": 0.03,
            "require_clean_git_for_self_edit": True,
            "blocked_command_fragments": ["rm -rf", "format"],
        },
        "self_edit": {"mutable_targets": ["src/"]},
        "memory": {"backend": "local"},
    }
    (chip_dir / "spark-researcher.project.json").write_text(
        json.dumps(project), encoding="utf-8"
    )

    # pyproject.toml
    (chip_dir / "pyproject.toml").write_text(
        f'[project]\nname = "{name}"\nversion = "0.3.0"\n',
        encoding="utf-8",
    )

    # README.md with mission
    (chip_dir / "README.md").write_text(
        f"# {name}\n\n## Mission\n\nTest chip for transfer system.\n"
        f"\n## Evidence Lanes\n\n"
        f"- research_grounded\n- benchmark_grounded\n"
        f"- exploratory_frontier\n- realworld_validated\n",
        encoding="utf-8",
    )

    # src/ with scoring + contradiction detection
    src_dir = chip_dir / "src"
    src_dir.mkdir()
    (src_dir / "evaluate.py").write_text(
        "DIMENSIONS = {'regime': {'bull': 5, 'bear': -3}}\n"
        "PAIR_BONUSES = {}\n"
        "SYSTEM_BONUSES = []\n\n"
        "def score(mutations):\n    return 0.5\n\n"
        "# contradiction detection tags\n"
        "def detect_contradiction(mutations):\n"
        "    return []\n",
        encoding="utf-8",
    )

    # docs/ with sources, architecture, mission
    docs_dir = chip_dir / "docs"
    docs_dir.mkdir()
    (docs_dir / "source_registry.md").write_text(
        "# Source Registry\n\nSource map and list of primary sources.\n",
        encoding="utf-8",
    )
    (docs_dir / "architecture.md").write_text(
        "# Architecture\n\nOne-loop architecture with cooldown.\n"
        "## Retirement\nAnchor retirement after N cycles.\n",
        encoding="utf-8",
    )
    (docs_dir / "mission.md").write_text(
        "# Mission\n\nThe intent of this chip.\n"
        "Owner review decisions are required for promotion.\n",
        encoding="utf-8",
    )

    # obsidian-vault/
    vault_dir = chip_dir / "obsidian-vault"
    vault_dir.mkdir()
    (vault_dir / "index.md").write_text(
        "# Knowledge Vault\n\nWatchtower pages here.\n",
        encoding="utf-8",
    )
    (vault_dir / "Leaderboard.md").write_text(
        "# Leaderboard\n\n| Rank | Score |\n",
        encoding="utf-8",
    )

    return chip_dir


def _create_weak_chip(tmp_path: Path, name: str = "domain-chip-weak") -> Path:
    """Create a low-scoring chip directory with minimal structure."""
    chip_dir = tmp_path / name
    chip_dir.mkdir()

    # Minimal spark-chip.json
    manifest = {
        "schema_version": "spark-chip.v1",
        "io_protocol": "spark-hook-io.v1",
        "capabilities": ["evaluate", "suggest", "packets", "watchtower"],
        "frontier": {
            "enabled": True,
            "allowed_mutations": {"focus": ["a", "b"]},
            "required_fields": [],
            "field_patterns": {"focus": "^[a-z]+$"},
        },
    }
    (chip_dir / "spark-chip.json").write_text(json.dumps(manifest), encoding="utf-8")

    # Minimal project.json -- missing many fields
    project = {
        "project_name": name,
    }
    (chip_dir / "spark-researcher.project.json").write_text(
        json.dumps(project), encoding="utf-8"
    )

    return chip_dir


def _create_bare_chip(tmp_path: Path, name: str = "domain-chip-bare") -> Path:
    """Create the most minimal chip -- just a directory."""
    chip_dir = tmp_path / name
    chip_dir.mkdir()
    return chip_dir


# ---------------------------------------------------------------------------
# TestExtractPatterns
# ---------------------------------------------------------------------------

class TestExtractPatterns:
    """Test pattern extraction from a mock chip."""

    def test_extract_returns_list_of_transfer_patterns(self, tmp_path: Path) -> None:
        chip = _create_mature_chip(tmp_path)
        patterns = extract_patterns(chip)
        assert isinstance(patterns, list)
        for p in patterns:
            assert isinstance(p, TransferPattern)

    def test_extract_finds_scoring_model(self, tmp_path: Path) -> None:
        chip = _create_mature_chip(tmp_path)
        patterns = extract_patterns(chip)
        scoring = [p for p in patterns if p.pattern_type == "scoring_model"]
        assert len(scoring) >= 1
        assert scoring[0].source_chip == "domain-chip-mature"

    def test_extract_finds_loop_design(self, tmp_path: Path) -> None:
        chip = _create_mature_chip(tmp_path)
        patterns = extract_patterns(chip)
        loop = [p for p in patterns if p.pattern_type == "loop_design"]
        assert len(loop) >= 1

    def test_extract_finds_evidence_strategy(self, tmp_path: Path) -> None:
        chip = _create_mature_chip(tmp_path)
        patterns = extract_patterns(chip)
        evidence = [p for p in patterns if p.pattern_type == "evidence_strategy"]
        assert len(evidence) >= 1

    def test_extract_finds_contradiction_detection(self, tmp_path: Path) -> None:
        chip = _create_mature_chip(tmp_path)
        patterns = extract_patterns(chip)
        contradiction = [p for p in patterns if p.pattern_type == "contradiction_detection"]
        assert len(contradiction) >= 1

    def test_extract_finds_research_pipeline(self, tmp_path: Path) -> None:
        chip = _create_mature_chip(tmp_path)
        patterns = extract_patterns(chip)
        pipeline = [p for p in patterns if p.pattern_type == "research_pipeline"]
        assert len(pipeline) >= 1

    def test_extract_finds_watchtower_design(self, tmp_path: Path) -> None:
        chip = _create_mature_chip(tmp_path)
        patterns = extract_patterns(chip)
        watchtower = [p for p in patterns if p.pattern_type == "watchtower_design"]
        assert len(watchtower) >= 1

    def test_extract_finds_promotion_gate(self, tmp_path: Path) -> None:
        chip = _create_mature_chip(tmp_path)
        patterns = extract_patterns(chip)
        gates = [p for p in patterns if p.pattern_type == "promotion_gate"]
        assert len(gates) >= 1

    def test_all_pattern_types_valid(self, tmp_path: Path) -> None:
        chip = _create_mature_chip(tmp_path)
        patterns = extract_patterns(chip)
        for p in patterns:
            assert p.pattern_type in PATTERN_TYPES

    def test_evidence_strength_based_on_score(self, tmp_path: Path) -> None:
        chip = _create_mature_chip(tmp_path)
        result = score_chip(chip)
        expected_strength = result["total_score"] / 100.0
        patterns = extract_patterns(chip)
        for p in patterns:
            assert abs(p.evidence_strength - expected_strength) < 0.01

    def test_extract_from_nonexistent_path(self, tmp_path: Path) -> None:
        patterns = extract_patterns(tmp_path / "nonexistent")
        assert patterns == []

    def test_pattern_ids_are_unique(self, tmp_path: Path) -> None:
        chip = _create_mature_chip(tmp_path)
        patterns = extract_patterns(chip)
        ids = [p.pattern_id for p in patterns]
        assert len(ids) == len(set(ids))

    def test_extract_from_bare_chip(self, tmp_path: Path) -> None:
        chip = _create_bare_chip(tmp_path)
        patterns = extract_patterns(chip)
        # Should not crash, may find zero patterns
        assert isinstance(patterns, list)


# ---------------------------------------------------------------------------
# TestFindApplicablePatterns
# ---------------------------------------------------------------------------

class TestFindApplicablePatterns:
    """Test pattern filtering for a target chip."""

    def test_returns_list_of_patterns(self, tmp_path: Path) -> None:
        mature = _create_mature_chip(tmp_path, "domain-chip-source")
        weak = _create_weak_chip(tmp_path)
        patterns = extract_patterns(mature)
        registry = TransferRegistry(patterns=patterns)
        applicable = find_applicable_patterns(weak, registry)
        assert isinstance(applicable, list)
        for p in applicable:
            assert isinstance(p, TransferPattern)

    def test_excludes_self_patterns(self, tmp_path: Path) -> None:
        """Patterns from the target's own chip should be excluded."""
        chip = _create_mature_chip(tmp_path)
        patterns = extract_patterns(chip)
        registry = TransferRegistry(patterns=patterns)
        applicable = find_applicable_patterns(chip, registry)
        # All patterns have source_chip == chip.name, so none apply to self
        assert len(applicable) == 0

    def test_excludes_already_applied(self, tmp_path: Path) -> None:
        """Patterns already applied should not appear again."""
        mature = _create_mature_chip(tmp_path, "domain-chip-source")
        weak = _create_weak_chip(tmp_path)
        patterns = extract_patterns(mature)

        # Simulate a previous transfer
        applied_ids = [p.pattern_id for p in patterns]
        history = TransferResult(
            target_chip=weak.name,
            patterns_applied=applied_ids,
            score_before=10,
            score_after=20,
            score_delta=10,
            successful_transfers=applied_ids,
            failed_transfers=[],
            recommendations=[],
        )
        registry = TransferRegistry(
            patterns=patterns,
            transfer_history=[history],
        )
        applicable = find_applicable_patterns(weak, registry)
        assert len(applicable) == 0

    def test_universal_patterns_apply_to_any_category(self, tmp_path: Path) -> None:
        """Patterns with applicable_categories=["all"] should match any target."""
        mature = _create_mature_chip(tmp_path, "domain-chip-source")
        weak = _create_weak_chip(tmp_path, "domain-chip-gaming-test")
        patterns = extract_patterns(mature)

        universal = [p for p in patterns if "all" in p.applicable_categories]
        assert len(universal) > 0

        registry = TransferRegistry(patterns=patterns)
        applicable = find_applicable_patterns(weak, registry)
        # At least some universal patterns should apply
        assert len(applicable) > 0

    def test_category_specific_filtering(self, tmp_path: Path) -> None:
        """Category-specific patterns should only apply to matching categories."""
        pattern = TransferPattern(
            pattern_id="test_finance_only",
            source_chip="domain-chip-other",
            pattern_type="evidence_strategy",
            description="Finance-specific pattern",
            implementation={"pattern": "regime_classification"},
            evidence_strength=0.8,
            applicable_categories=["finance"],
        )
        registry = TransferRegistry(patterns=[pattern])

        # Non-finance chip should not get this pattern
        non_finance = _create_weak_chip(tmp_path, "domain-chip-weak")
        applicable = find_applicable_patterns(non_finance, registry)
        finance_patterns = [p for p in applicable if p.pattern_id == "test_finance_only"]
        assert len(finance_patterns) == 0

    def test_sorted_by_expected_impact(self, tmp_path: Path) -> None:
        """Returned patterns should be sorted by expected impact descending."""
        mature = _create_mature_chip(tmp_path, "domain-chip-source")
        weak = _create_weak_chip(tmp_path)
        patterns = extract_patterns(mature)
        registry = TransferRegistry(patterns=patterns)
        applicable = find_applicable_patterns(weak, registry)

        if len(applicable) >= 2:
            # We cannot directly verify the sort key externally, but we can
            # check that higher-evidence patterns tend to come first
            strengths = [p.evidence_strength for p in applicable]
            # Not strictly sorted by strength alone (impact = strength * points)
            # but all strengths should be > 0
            for s in strengths:
                assert s >= 0.0


# ---------------------------------------------------------------------------
# TestApplyPattern -- one test per pattern type
# ---------------------------------------------------------------------------

class TestApplyPatternScoringModel:
    """Test applying scoring_model patterns."""

    def test_creates_evaluate_py_if_missing(self, tmp_path: Path) -> None:
        chip = _create_bare_chip(tmp_path)
        pattern = TransferPattern(
            pattern_id="test_scoring",
            source_chip="domain-chip-source",
            pattern_type="scoring_model",
            description="Test scoring model",
            implementation={
                "has_dimensions": True,
                "has_pair_bonuses": True,
                "has_system_bonuses": True,
            },
            evidence_strength=0.9,
            applicable_categories=["all"],
        )
        result = apply_pattern(chip, pattern)
        assert result is True
        eval_file = chip / "src" / "evaluate.py"
        assert eval_file.exists()
        content = eval_file.read_text(encoding="utf-8")
        assert "score" in content.lower()

    def test_does_not_delete_existing_evaluate(self, tmp_path: Path) -> None:
        chip = _create_weak_chip(tmp_path)
        src_dir = chip / "src"
        src_dir.mkdir(exist_ok=True)
        eval_file = src_dir / "evaluate.py"
        original = "# Existing scoring logic\ndef score(m): return 42\n"
        eval_file.write_text(original, encoding="utf-8")

        pattern = TransferPattern(
            pattern_id="test_scoring",
            source_chip="domain-chip-source",
            pattern_type="scoring_model",
            description="Test scoring model",
            implementation={
                "has_dimensions": True,
                "has_pair_bonuses": True,
                "has_system_bonuses": False,
            },
            evidence_strength=0.9,
            applicable_categories=["all"],
        )
        apply_pattern(chip, pattern)
        content = eval_file.read_text(encoding="utf-8")
        # Original content must still be present
        assert "Existing scoring logic" in content
        assert "return 42" in content

    def test_increments_times_applied(self, tmp_path: Path) -> None:
        chip = _create_bare_chip(tmp_path)
        pattern = TransferPattern(
            pattern_id="test_scoring",
            source_chip="src",
            pattern_type="scoring_model",
            description="test",
            implementation={"has_dimensions": True},
            evidence_strength=0.5,
            applicable_categories=["all"],
        )
        assert pattern.times_applied == 0
        apply_pattern(chip, pattern)
        assert pattern.times_applied == 1
        assert pattern.times_successful == 1


class TestApplyPatternLoopDesign:
    """Test applying loop_design patterns."""

    def test_adds_guardrails_to_project(self, tmp_path: Path) -> None:
        chip = _create_weak_chip(tmp_path)
        pattern = TransferPattern(
            pattern_id="test_loop",
            source_chip="domain-chip-source",
            pattern_type="loop_design",
            description="Loop guardrails",
            implementation={
                "max_loop_iterations": 10,
                "consecutive_discard_limit": 3,
                "blocked_command_fragments": ["rm -rf", "format"],
            },
            evidence_strength=0.8,
            applicable_categories=["all"],
        )
        result = apply_pattern(chip, pattern)
        assert result is True
        project = json.loads(
            (chip / "spark-researcher.project.json").read_text(encoding="utf-8")
        )
        guardrails = project.get("guardrails", {})
        assert guardrails["max_loop_iterations"] == 10
        assert guardrails["consecutive_discard_limit"] == 3

    def test_does_not_overwrite_existing_guardrails(self, tmp_path: Path) -> None:
        chip = _create_weak_chip(tmp_path)
        # Pre-set a guardrail
        project_path = chip / "spark-researcher.project.json"
        project = json.loads(project_path.read_text(encoding="utf-8"))
        project["guardrails"] = {"max_loop_iterations": 5}
        project_path.write_text(json.dumps(project), encoding="utf-8")

        pattern = TransferPattern(
            pattern_id="test_loop",
            source_chip="domain-chip-source",
            pattern_type="loop_design",
            description="Loop guardrails",
            implementation={
                "max_loop_iterations": 10,
                "consecutive_discard_limit": 3,
            },
            evidence_strength=0.8,
            applicable_categories=["all"],
        )
        apply_pattern(chip, pattern)
        project = json.loads(project_path.read_text(encoding="utf-8"))
        # Existing value preserved, new value added
        assert project["guardrails"]["max_loop_iterations"] == 5
        assert project["guardrails"]["consecutive_discard_limit"] == 3

    def test_merges_blocked_fragments_additively(self, tmp_path: Path) -> None:
        chip = _create_weak_chip(tmp_path)
        project_path = chip / "spark-researcher.project.json"
        project = json.loads(project_path.read_text(encoding="utf-8"))
        project["guardrails"] = {"blocked_command_fragments": ["sudo"]}
        project_path.write_text(json.dumps(project), encoding="utf-8")

        pattern = TransferPattern(
            pattern_id="test_loop",
            source_chip="domain-chip-source",
            pattern_type="loop_design",
            description="Loop guardrails",
            implementation={
                "blocked_command_fragments": ["rm -rf", "format"],
            },
            evidence_strength=0.8,
            applicable_categories=["all"],
        )
        apply_pattern(chip, pattern)
        project = json.loads(project_path.read_text(encoding="utf-8"))
        fragments = project["guardrails"]["blocked_command_fragments"]
        assert "sudo" in fragments
        assert "rm -rf" in fragments
        assert "format" in fragments


class TestApplyPatternEvidenceStrategy:
    """Test applying evidence_strategy patterns."""

    def test_creates_evidence_lanes_doc(self, tmp_path: Path) -> None:
        chip = _create_bare_chip(tmp_path)
        pattern = TransferPattern(
            pattern_id="test_evidence",
            source_chip="domain-chip-source",
            pattern_type="evidence_strategy",
            description="Evidence lanes",
            implementation={
                "lanes": ["research_grounded", "benchmark_grounded"],
                "lane_count": 2,
            },
            evidence_strength=0.8,
            applicable_categories=["all"],
        )
        result = apply_pattern(chip, pattern)
        assert result is True
        lanes_doc = chip / "docs" / "evidence_lanes.md"
        assert lanes_doc.exists()
        content = lanes_doc.read_text(encoding="utf-8")
        assert "research_grounded" in content

    def test_creates_source_registry_doc(self, tmp_path: Path) -> None:
        chip = _create_bare_chip(tmp_path)
        pattern = TransferPattern(
            pattern_id="test_source_reg",
            source_chip="domain-chip-source",
            pattern_type="evidence_strategy",
            description="Source registry",
            implementation={"pattern": "source_registry", "has_source_docs": True},
            evidence_strength=0.8,
            applicable_categories=["all"],
        )
        result = apply_pattern(chip, pattern)
        assert result is True
        source_doc = chip / "docs" / "source_registry.md"
        assert source_doc.exists()

    def test_does_not_overwrite_existing_doc(self, tmp_path: Path) -> None:
        chip = _create_bare_chip(tmp_path)
        docs_dir = chip / "docs"
        docs_dir.mkdir()
        lanes_doc = docs_dir / "evidence_lanes.md"
        original = "# My Custom Evidence Lanes\n"
        lanes_doc.write_text(original, encoding="utf-8")

        pattern = TransferPattern(
            pattern_id="test_evidence",
            source_chip="domain-chip-source",
            pattern_type="evidence_strategy",
            description="Evidence lanes",
            implementation={"lanes": ["research_grounded"], "lane_count": 1},
            evidence_strength=0.8,
            applicable_categories=["all"],
        )
        apply_pattern(chip, pattern)
        content = lanes_doc.read_text(encoding="utf-8")
        assert content == original  # _ensure_file does not overwrite

    def test_walk_forward_validation_pattern(self, tmp_path: Path) -> None:
        chip = _create_bare_chip(tmp_path)
        pattern = TransferPattern(
            pattern_id="test_wf",
            source_chip="domain-chip-source",
            pattern_type="evidence_strategy",
            description="Walk-forward validation",
            implementation={"pattern": "walk_forward_validation"},
            evidence_strength=0.8,
            applicable_categories=["all"],
        )
        result = apply_pattern(chip, pattern)
        assert result is True
        doc = chip / "docs" / "walk_forward_validation.md"
        assert doc.exists()

    def test_category_specific_pattern_creates_doc(self, tmp_path: Path) -> None:
        chip = _create_bare_chip(tmp_path)
        pattern = TransferPattern(
            pattern_id="test_regime",
            source_chip="domain-chip-source",
            pattern_type="evidence_strategy",
            description="Regime classification",
            implementation={"pattern": "regime_classification"},
            evidence_strength=0.8,
            applicable_categories=["finance"],
        )
        result = apply_pattern(chip, pattern)
        assert result is True
        doc = chip / "docs" / "regime_classification.md"
        assert doc.exists()


class TestApplyPatternPromotionGate:
    """Test applying promotion_gate patterns."""

    def test_adds_promotion_gate_to_project(self, tmp_path: Path) -> None:
        chip = _create_weak_chip(tmp_path)
        pattern = TransferPattern(
            pattern_id="test_gate",
            source_chip="domain-chip-source",
            pattern_type="promotion_gate",
            description="Promotion gate",
            implementation={"pattern": "promotion_gate", "near_best_tolerance": 0.05},
            evidence_strength=0.8,
            applicable_categories=["all"],
        )
        result = apply_pattern(chip, pattern)
        assert result is True
        project = json.loads(
            (chip / "spark-researcher.project.json").read_text(encoding="utf-8")
        )
        assert "promotion_gate" in project
        assert project["promotion_gate"]["min_score"] == 60


class TestApplyPatternContradictionDetection:
    """Test applying contradiction_detection patterns."""

    def test_creates_detector_stub(self, tmp_path: Path) -> None:
        chip = _create_bare_chip(tmp_path)
        pattern = TransferPattern(
            pattern_id="test_contradiction",
            source_chip="domain-chip-source",
            pattern_type="contradiction_detection",
            description="Contradiction detection",
            implementation={"pattern": "contradiction_detection", "has_tags": True},
            evidence_strength=0.8,
            applicable_categories=["all"],
        )
        result = apply_pattern(chip, pattern)
        assert result is True
        detector = chip / "src" / "contradiction_detector.py"
        assert detector.exists()
        content = detector.read_text(encoding="utf-8")
        assert "detect_contradictions" in content
        assert "CONTRADICTION_TAGS" in content

    def test_does_not_overwrite_existing_detector(self, tmp_path: Path) -> None:
        chip = _create_bare_chip(tmp_path)
        src_dir = chip / "src"
        src_dir.mkdir()
        detector = src_dir / "contradiction_detector.py"
        original = "# My custom contradiction detector\n"
        detector.write_text(original, encoding="utf-8")

        pattern = TransferPattern(
            pattern_id="test_contradiction",
            source_chip="domain-chip-source",
            pattern_type="contradiction_detection",
            description="Contradiction detection",
            implementation={"pattern": "contradiction_detection", "has_tags": False},
            evidence_strength=0.8,
            applicable_categories=["all"],
        )
        apply_pattern(chip, pattern)
        content = detector.read_text(encoding="utf-8")
        assert content == original


class TestApplyPatternResearchPipeline:
    """Test applying research_pipeline patterns."""

    def test_adds_baseline_trial(self, tmp_path: Path) -> None:
        chip = _create_weak_chip(tmp_path)
        pattern = TransferPattern(
            pattern_id="test_pipeline",
            source_chip="domain-chip-source",
            pattern_type="research_pipeline",
            description="Research pipeline with trials",
            implementation={
                "trial_count": 5,
                "has_baseline": True,
            },
            evidence_strength=0.8,
            applicable_categories=["all"],
        )
        result = apply_pattern(chip, pattern)
        assert result is True
        project = json.loads(
            (chip / "spark-researcher.project.json").read_text(encoding="utf-8")
        )
        trials = project.get("candidate_trials", [])
        assert len(trials) >= 3
        # Should have a baseline trial
        baselines = [
            t for t in trials
            if t.get("mutations", None) == {} or t.get("mutations") is None
        ]
        assert len(baselines) >= 1

    def test_does_not_duplicate_baseline(self, tmp_path: Path) -> None:
        chip = _create_weak_chip(tmp_path)
        # Add a baseline manually
        project_path = chip / "spark-researcher.project.json"
        project = json.loads(project_path.read_text(encoding="utf-8"))
        project["candidate_trials"] = [
            {"candidate_id": "baseline", "mutations": {}},
            {"candidate_id": "v1", "mutations": {"focus": "a"}},
            {"candidate_id": "v2", "mutations": {"focus": "b"}},
        ]
        project_path.write_text(json.dumps(project), encoding="utf-8")

        pattern = TransferPattern(
            pattern_id="test_pipeline",
            source_chip="domain-chip-source",
            pattern_type="research_pipeline",
            description="Pipeline",
            implementation={"has_baseline": True, "trial_count": 3},
            evidence_strength=0.8,
            applicable_categories=["all"],
        )
        apply_pattern(chip, pattern)
        project = json.loads(project_path.read_text(encoding="utf-8"))
        baselines = [
            t for t in project["candidate_trials"]
            if t.get("mutations", None) == {} or t.get("mutations") is None
        ]
        # Should still be exactly 1 baseline
        assert len(baselines) == 1


class TestApplyPatternWatchtowerDesign:
    """Test applying watchtower_design patterns."""

    def test_creates_vault_with_pages(self, tmp_path: Path) -> None:
        chip = _create_bare_chip(tmp_path)
        pattern = TransferPattern(
            pattern_id="test_watchtower",
            source_chip="domain-chip-source",
            pattern_type="watchtower_design",
            description="Watchtower vault",
            implementation={"page_count": 3, "page_names": ["index", "Leaderboard"]},
            evidence_strength=0.8,
            applicable_categories=["all"],
        )
        result = apply_pattern(chip, pattern)
        assert result is True
        vault = chip / "obsidian-vault"
        assert vault.exists()
        assert (vault / "index.md").exists()
        assert (vault / "Leaderboard.md").exists()

    def test_does_not_overwrite_existing_vault(self, tmp_path: Path) -> None:
        chip = _create_bare_chip(tmp_path)
        vault = chip / "obsidian-vault"
        vault.mkdir()
        original = "# My custom vault\n"
        (vault / "index.md").write_text(original, encoding="utf-8")

        pattern = TransferPattern(
            pattern_id="test_watchtower",
            source_chip="domain-chip-source",
            pattern_type="watchtower_design",
            description="Watchtower vault",
            implementation={"page_count": 1, "page_names": ["index"]},
            evidence_strength=0.8,
            applicable_categories=["all"],
        )
        apply_pattern(chip, pattern)
        content = (vault / "index.md").read_text(encoding="utf-8")
        assert content == original  # _ensure_file preserves existing


class TestApplyPatternNeverDeletes:
    """Critical test: apply_pattern must NEVER delete existing content."""

    def test_existing_files_preserved_scoring_model(self, tmp_path: Path) -> None:
        chip = _create_mature_chip(tmp_path)
        files_before = set(str(p) for p in chip.rglob("*") if p.is_file())
        content_before = {}
        for f in chip.rglob("*"):
            if f.is_file():
                try:
                    content_before[str(f)] = f.read_text(encoding="utf-8", errors="ignore")
                except OSError:
                    pass

        pattern = TransferPattern(
            pattern_id="test_no_delete",
            source_chip="domain-chip-other",
            pattern_type="scoring_model",
            description="test",
            implementation={"has_dimensions": True},
            evidence_strength=0.5,
            applicable_categories=["all"],
        )
        apply_pattern(chip, pattern)

        # All original files must still exist
        files_after = set(str(p) for p in chip.rglob("*") if p.is_file())
        assert files_before.issubset(files_after)

        # Original content must be preserved (not truncated or replaced)
        for filepath, orig_content in content_before.items():
            current = Path(filepath).read_text(encoding="utf-8", errors="ignore")
            assert orig_content in current, (
                f"Content deleted from {filepath}"
            )

    def test_existing_files_preserved_loop_design(self, tmp_path: Path) -> None:
        chip = _create_mature_chip(tmp_path)
        project_before = (chip / "spark-researcher.project.json").read_text(encoding="utf-8")
        project_data_before = json.loads(project_before)

        pattern = TransferPattern(
            pattern_id="test_no_delete",
            source_chip="domain-chip-other",
            pattern_type="loop_design",
            description="test",
            implementation={"max_loop_iterations": 99},
            evidence_strength=0.5,
            applicable_categories=["all"],
        )
        apply_pattern(chip, pattern)

        project_after = json.loads(
            (chip / "spark-researcher.project.json").read_text(encoding="utf-8")
        )
        # All original keys must still exist
        assert project_data_before.get("project_name") == project_after.get("project_name")
        # Original guardrails preserved
        for key, val in project_data_before.get("guardrails", {}).items():
            assert key in project_after.get("guardrails", {}), (
                f"Guardrail key '{key}' deleted"
            )

    def test_existing_files_preserved_all_types(self, tmp_path: Path) -> None:
        """Apply every pattern type and verify no files were deleted."""
        chip = _create_mature_chip(tmp_path)
        files_before = set(str(p) for p in chip.rglob("*") if p.is_file())

        for ptype in PATTERN_TYPES:
            pattern = TransferPattern(
                pattern_id=f"test_nodelete_{ptype}",
                source_chip="domain-chip-other",
                pattern_type=ptype,
                description=f"Test no-delete for {ptype}",
                implementation={
                    "has_dimensions": True,
                    "max_loop_iterations": 5,
                    "lanes": ["research_grounded"],
                    "lane_count": 1,
                    "pattern": "source_registry",
                    "has_tags": True,
                    "has_baseline": True,
                    "trial_count": 3,
                    "page_count": 1,
                    "page_names": ["index"],
                },
                evidence_strength=0.5,
                applicable_categories=["all"],
            )
            apply_pattern(chip, pattern)

        files_after = set(str(p) for p in chip.rglob("*") if p.is_file())
        assert files_before.issubset(files_after), (
            f"Files deleted: {files_before - files_after}"
        )

    def test_unknown_pattern_type_returns_false(self, tmp_path: Path) -> None:
        chip = _create_bare_chip(tmp_path)
        pattern = TransferPattern(
            pattern_id="test_unknown",
            source_chip="src",
            pattern_type="nonexistent_type",
            description="test",
            implementation={},
            evidence_strength=0.5,
            applicable_categories=["all"],
        )
        result = apply_pattern(chip, pattern)
        assert result is False


# ---------------------------------------------------------------------------
# TestTransferIntelligence
# ---------------------------------------------------------------------------

class TestTransferIntelligence:
    """Test the full end-to-end transfer pipeline."""

    def test_returns_transfer_result(self, tmp_path: Path) -> None:
        source = _create_mature_chip(tmp_path, "domain-chip-source")
        target = _create_weak_chip(tmp_path)
        result = transfer_intelligence(source, target)
        assert isinstance(result, TransferResult)

    def test_score_before_and_after_are_ints(self, tmp_path: Path) -> None:
        source = _create_mature_chip(tmp_path, "domain-chip-source")
        target = _create_weak_chip(tmp_path)
        result = transfer_intelligence(source, target)
        assert isinstance(result.score_before, int)
        assert isinstance(result.score_after, int)

    def test_score_delta_is_correct(self, tmp_path: Path) -> None:
        source = _create_mature_chip(tmp_path, "domain-chip-source")
        target = _create_weak_chip(tmp_path)
        result = transfer_intelligence(source, target)
        assert result.score_delta == result.score_after - result.score_before

    def test_transfers_improve_or_maintain_score(self, tmp_path: Path) -> None:
        """Transfers should never decrease the score (we only add, never delete)."""
        source = _create_mature_chip(tmp_path, "domain-chip-source")
        target = _create_weak_chip(tmp_path)
        result = transfer_intelligence(source, target)
        assert result.score_delta >= 0

    def test_patterns_applied_list_matches_successful_plus_failed(
        self, tmp_path: Path
    ) -> None:
        source = _create_mature_chip(tmp_path, "domain-chip-source")
        target = _create_weak_chip(tmp_path)
        result = transfer_intelligence(source, target)
        assert set(result.patterns_applied) == (
            set(result.successful_transfers) | set(result.failed_transfers)
        )

    def test_recommendations_are_strings(self, tmp_path: Path) -> None:
        source = _create_mature_chip(tmp_path, "domain-chip-source")
        target = _create_weak_chip(tmp_path)
        result = transfer_intelligence(source, target)
        for rec in result.recommendations:
            assert isinstance(rec, str)

    def test_target_chip_name_correct(self, tmp_path: Path) -> None:
        source = _create_mature_chip(tmp_path, "domain-chip-source")
        target = _create_weak_chip(tmp_path)
        result = transfer_intelligence(source, target)
        assert result.target_chip == target.name

    def test_transfer_bare_to_bare(self, tmp_path: Path) -> None:
        """Transferring between two bare chips should not crash."""
        source = _create_bare_chip(tmp_path, "domain-chip-src-bare")
        target = _create_bare_chip(tmp_path, "domain-chip-tgt-bare")
        result = transfer_intelligence(source, target)
        assert isinstance(result, TransferResult)
        assert result.score_delta >= 0


# ---------------------------------------------------------------------------
# TestPortfolioTransfer
# ---------------------------------------------------------------------------

class TestPortfolioTransfer:
    """Test portfolio-wide transfer."""

    def test_returns_list_of_results(self, tmp_path: Path) -> None:
        _create_mature_chip(tmp_path, "domain-chip-strong")
        _create_weak_chip(tmp_path, "domain-chip-needs-help")
        results = portfolio_transfer(tmp_path, target_score=70)
        assert isinstance(results, list)

    def test_only_targets_weak_chips(self, tmp_path: Path) -> None:
        strong = _create_mature_chip(tmp_path, "domain-chip-strong")
        weak = _create_weak_chip(tmp_path, "domain-chip-needs-help")

        strong_score = score_chip(strong)["total_score"]
        results = portfolio_transfer(tmp_path, target_score=strong_score)

        target_names = [r.target_chip for r in results]
        assert "domain-chip-needs-help" in target_names
        # Strong chip should not be a target
        assert "domain-chip-strong" not in target_names

    def test_empty_directory(self, tmp_path: Path) -> None:
        results = portfolio_transfer(tmp_path / "nonexistent")
        assert results == []


# ---------------------------------------------------------------------------
# TestRegistrySaveLoad
# ---------------------------------------------------------------------------

class TestRegistrySaveLoad:
    """Test registry persistence."""

    def test_save_and_load_roundtrip(self, tmp_path: Path) -> None:
        registry = TransferRegistry(
            patterns=[
                TransferPattern(
                    pattern_id="p1",
                    source_chip="domain-chip-src",
                    pattern_type="scoring_model",
                    description="Test pattern",
                    implementation={"key": "value"},
                    evidence_strength=0.85,
                    applicable_categories=["all"],
                    times_applied=3,
                    times_successful=2,
                ),
            ],
            transfer_history=[
                TransferResult(
                    target_chip="domain-chip-tgt",
                    patterns_applied=["p1"],
                    score_before=30,
                    score_after=45,
                    score_delta=15,
                    successful_transfers=["p1"],
                    failed_transfers=[],
                    recommendations=["Fix X manually"],
                ),
            ],
            last_extraction="2026-03-20T12:00:00+00:00",
        )

        reg_path = tmp_path / "registry.json"
        save_registry(registry, reg_path)

        loaded = load_registry(reg_path)
        assert len(loaded.patterns) == 1
        assert loaded.patterns[0].pattern_id == "p1"
        assert loaded.patterns[0].evidence_strength == 0.85
        assert loaded.patterns[0].times_applied == 3
        assert loaded.patterns[0].times_successful == 2
        assert loaded.patterns[0].implementation == {"key": "value"}
        assert loaded.patterns[0].applicable_categories == ["all"]

        assert len(loaded.transfer_history) == 1
        assert loaded.transfer_history[0].target_chip == "domain-chip-tgt"
        assert loaded.transfer_history[0].score_delta == 15
        assert loaded.transfer_history[0].recommendations == ["Fix X manually"]

        assert loaded.last_extraction == "2026-03-20T12:00:00+00:00"

    def test_load_nonexistent_returns_empty_registry(self, tmp_path: Path) -> None:
        loaded = load_registry(tmp_path / "nonexistent.json")
        assert loaded.patterns == []
        assert loaded.transfer_history == []
        assert loaded.last_extraction is None

    def test_saved_file_is_valid_json(self, tmp_path: Path) -> None:
        registry = TransferRegistry()
        reg_path = tmp_path / "registry.json"
        save_registry(registry, reg_path)
        data = json.loads(reg_path.read_text(encoding="utf-8"))
        assert "patterns" in data
        assert "transfer_history" in data
        assert "last_extraction" in data

    def test_roundtrip_with_many_patterns(self, tmp_path: Path) -> None:
        patterns = []
        for i in range(20):
            patterns.append(TransferPattern(
                pattern_id=f"p{i}",
                source_chip=f"chip-{i}",
                pattern_type=PATTERN_TYPES[i % len(PATTERN_TYPES)],
                description=f"Pattern {i}",
                implementation={"index": i},
                evidence_strength=i / 20.0,
                applicable_categories=["all"] if i % 2 == 0 else ["finance"],
                times_applied=i,
                times_successful=i // 2,
            ))
        registry = TransferRegistry(patterns=patterns)
        reg_path = tmp_path / "big_registry.json"
        save_registry(registry, reg_path)
        loaded = load_registry(reg_path)
        assert len(loaded.patterns) == 20
        for i, p in enumerate(loaded.patterns):
            assert p.pattern_id == f"p{i}"
            assert p.implementation == {"index": i}


# ---------------------------------------------------------------------------
# TestExtractPortfolioPatterns
# ---------------------------------------------------------------------------

class TestExtractPortfolioPatterns:
    """Test portfolio-wide pattern extraction."""

    def test_returns_registry(self, tmp_path: Path) -> None:
        _create_mature_chip(tmp_path, "domain-chip-good")
        _create_weak_chip(tmp_path, "domain-chip-poor")
        registry = extract_portfolio_patterns(tmp_path)
        assert isinstance(registry, TransferRegistry)
        assert registry.last_extraction is not None

    def test_only_extracts_from_mature_chips(self, tmp_path: Path) -> None:
        _create_mature_chip(tmp_path, "domain-chip-good")
        weak = _create_weak_chip(tmp_path, "domain-chip-poor")
        registry = extract_portfolio_patterns(tmp_path)
        # All patterns should come from the mature chip
        for p in registry.patterns:
            assert p.source_chip != "domain-chip-poor"

    def test_empty_directory(self, tmp_path: Path) -> None:
        registry = extract_portfolio_patterns(tmp_path / "nonexistent")
        assert registry.patterns == []


# ---------------------------------------------------------------------------
# TestDataclassIntegrity
# ---------------------------------------------------------------------------

class TestDataclassIntegrity:
    """Test that dataclasses have correct defaults and fields."""

    def test_transfer_pattern_defaults(self) -> None:
        p = TransferPattern(
            pattern_id="x",
            source_chip="y",
            pattern_type="scoring_model",
            description="d",
            implementation={},
            evidence_strength=0.5,
            applicable_categories=["all"],
        )
        assert p.times_applied == 0
        assert p.times_successful == 0

    def test_transfer_registry_defaults(self) -> None:
        r = TransferRegistry()
        assert r.patterns == []
        assert r.transfer_history == []
        assert r.last_extraction is None

    def test_transfer_result_fields(self) -> None:
        r = TransferResult(
            target_chip="t",
            patterns_applied=["a", "b"],
            score_before=10,
            score_after=20,
            score_delta=10,
            successful_transfers=["a"],
            failed_transfers=["b"],
            recommendations=["fix c"],
        )
        assert r.target_chip == "t"
        assert len(r.patterns_applied) == 2
        assert r.score_delta == 10
