"""Tests for the recursive loop controller module."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from chip_labs.loop_controller import (
    EVIDENCE_LANES,
    IterationRecord,
    LoopConfig,
    LoopResult,
    LoopTelemetry,
    RecursiveLoopController,
    _create_initial_packets,
    _seed_benchmark_baseline,
    _seed_evidence_stubs,
    _seed_research_sources,
)
from chip_labs.quality_rubric import score_chip
from chip_labs.scaffold import scaffold_chip


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_brief(**overrides: Any) -> dict[str, Any]:
    """Create a minimal valid domain brief for testing."""
    brief: dict[str, Any] = {
        "domain_id": "test-loop",
        "domain_name": "Test Loop Domain",
        "category": "technology",
        "description": "A domain chip for testing the loop controller.",
        "primary_metric": "quality_score",
        "mutation_axes": [
            {"name": "approach", "values": ["baseline", "optimized", "experimental"]},
            {"name": "scale", "values": ["small", "medium", "large"]},
        ],
    }
    brief.update(overrides)
    return brief


def _scaffold_chip(tmp_path: Path) -> Path:
    """Scaffold a chip in tmp_path and return the chip directory path."""
    brief = _make_brief()
    return scaffold_chip(brief, output_dir=tmp_path)


def _create_mock_chip(tmp_path: Path) -> Path:
    """Create a manually-constructed mock chip for fine-grained testing."""
    chip_dir = tmp_path / "domain-chip-manual"
    chip_dir.mkdir(parents=True, exist_ok=True)

    # spark-chip.json
    manifest = {
        "schema_version": "spark-chip.v1",
        "io_protocol": "spark-hook-io.v1",
        "name": "manual-chip",
        "capabilities": ["evaluate", "suggest", "packets", "watchtower"],
        "frontier": {
            "enabled": True,
            "allowed_mutations": {"approach": ["a", "b"]},
            "required_fields": ["approach"],
            "field_patterns": {"approach": "^[a-z]+$"},
        },
    }
    (chip_dir / "spark-chip.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )

    # spark-researcher.project.json
    project = {
        "project_name": "manual-chip",
        "eval_metric": "quality_score",
        "metrics": {"quality_score": {}, "coverage": {}, "depth": {}},
        "candidate_trials": [
            {"name": "baseline", "mutations": {}},
            {"name": "v1", "mutations": {"approach": "a"}},
            {"name": "v2", "mutations": {"approach": "b"}},
        ],
        "chip": {"path": ".", "manifest": "spark-chip.json"},
        "commands": {"evaluate": {"kind": "chip-evaluate"}},
        "guardrails": {
            "max_loop_iterations": 10,
            "blocked_command_fragments": ["rm -rf"],
        },
        "self_edit": {"mutable_targets": ["src/"]},
        "memory": {"backend": "local"},
    }
    (chip_dir / "spark-researcher.project.json").write_text(
        json.dumps(project, indent=2), encoding="utf-8"
    )

    # pyproject.toml
    (chip_dir / "pyproject.toml").write_text(
        '[project]\nname = "domain-chip-manual"\nversion = "0.1.0"\n',
        encoding="utf-8",
    )

    # README.md
    (chip_dir / "README.md").write_text(
        "# Manual Chip\n\n## Mission\n\nManual test chip.\n",
        encoding="utf-8",
    )

    # src/ with scoring logic
    src_dir = chip_dir / "src"
    src_dir.mkdir(parents=True, exist_ok=True)
    (src_dir / "evaluate.py").write_text(
        "def score(mutations):\n    return 0.5\n",
        encoding="utf-8",
    )

    # docs/
    docs_dir = chip_dir / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    (docs_dir / "source_registry.md").write_text(
        "# Source Registry\n\nSource map and list for this domain.\n",
        encoding="utf-8",
    )
    (docs_dir / "architecture.md").write_text(
        "# Architecture\n\nOne-loop spec.\n",
        encoding="utf-8",
    )
    (docs_dir / "mission.md").write_text(
        "# Mission\n\nThe intent of this chip.\n",
        encoding="utf-8",
    )

    # obsidian-vault
    vault_dir = chip_dir / "obsidian-vault"
    vault_dir.mkdir(parents=True, exist_ok=True)
    (vault_dir / "index.md").write_text(
        "# Knowledge Vault\n\nPages go here.\n",
        encoding="utf-8",
    )

    return chip_dir


# ===========================================================================
# Test LoopConfig
# ===========================================================================


class TestLoopConfig:
    """Test LoopConfig defaults and validation."""

    def test_defaults(self) -> None:
        cfg = LoopConfig()
        assert cfg.target_score == 80
        assert cfg.max_iterations == 50
        assert cfg.max_stall_iterations == 5
        assert cfg.autonomy_level == "full_auto"
        assert cfg.research_enabled is True
        assert cfg.structural_fix_enabled is True
        assert cfg.evidence_gathering_enabled is True
        assert cfg.telemetry_enabled is True

    def test_custom_values(self) -> None:
        cfg = LoopConfig(
            target_score=60,
            max_iterations=10,
            max_stall_iterations=3,
            autonomy_level="semi_auto",
            research_enabled=False,
        )
        assert cfg.target_score == 60
        assert cfg.max_iterations == 10
        assert cfg.max_stall_iterations == 3
        assert cfg.autonomy_level == "semi_auto"
        assert cfg.research_enabled is False

    def test_invalid_autonomy_level_raises(self) -> None:
        with pytest.raises(ValueError, match="Invalid autonomy_level"):
            LoopConfig(autonomy_level="yolo")

    def test_invalid_target_score_raises(self) -> None:
        with pytest.raises(ValueError, match="target_score must be 0-100"):
            LoopConfig(target_score=150)

    def test_invalid_max_iterations_raises(self) -> None:
        with pytest.raises(ValueError, match="max_iterations must be >= 1"):
            LoopConfig(max_iterations=0)

    def test_invalid_max_stall_iterations_raises(self) -> None:
        with pytest.raises(ValueError, match="max_stall_iterations must be >= 1"):
            LoopConfig(max_stall_iterations=0)


# ===========================================================================
# Test LoopTelemetry
# ===========================================================================


class TestLoopTelemetry:
    """Test LoopTelemetry initialization and serialization."""

    def test_default_values(self) -> None:
        t = LoopTelemetry()
        assert t.start_time == ""
        assert t.end_time is None
        assert t.iterations == []
        assert t.score_trajectory == []
        assert t.stall_count == 0
        assert t.fixes_applied == 0
        assert t.research_actions == 0
        assert t.evidence_gathered == 0
        assert t.status == "running"

    def test_to_dict_roundtrips_through_json(self) -> None:
        t = LoopTelemetry(
            start_time="2026-01-01T00:00:00+00:00",
            status="completed",
            score_trajectory=[40, 55, 70, 80],
            fixes_applied=3,
        )
        d = t.to_dict()
        # Must be JSON-serializable
        serialized = json.dumps(d)
        parsed = json.loads(serialized)
        assert parsed["status"] == "completed"
        assert parsed["score_trajectory"] == [40, 55, 70, 80]
        assert parsed["fixes_applied"] == 3

    def test_to_dict_includes_iteration_records(self) -> None:
        record = IterationRecord(
            iteration=1,
            action_type="structural_fix",
            action_detail="fixed schema_version",
            score_before=40,
            score_after=43,
            delta=3,
            duration_ms=12,
        )
        t = LoopTelemetry(iterations=[record])
        d = t.to_dict()
        assert len(d["iterations"]) == 1
        assert d["iterations"][0]["action_type"] == "structural_fix"
        assert d["iterations"][0]["delta"] == 3


# ===========================================================================
# Test IterationRecord
# ===========================================================================


class TestIterationRecord:
    """Test IterationRecord dataclass."""

    def test_fields(self) -> None:
        r = IterationRecord(
            iteration=5,
            action_type="gap_analysis",
            action_detail="Analyzed 3 gaps",
            score_before=50,
            score_after=55,
            delta=5,
            duration_ms=100,
        )
        assert r.iteration == 5
        assert r.action_type == "gap_analysis"
        assert r.delta == 5


# ===========================================================================
# Test LoopResult
# ===========================================================================


class TestLoopResult:
    """Test LoopResult dataclass."""

    def test_fields(self, tmp_path: Path) -> None:
        chip_dir = tmp_path / "chip"
        chip_dir.mkdir()
        lr = LoopResult(
            chip_path=chip_dir,
            initial_score=40,
            final_score=82,
            verdict="production_ready",
            iterations=7,
            telemetry=LoopTelemetry(),
            improvements=["Fix A", "Fix B"],
            remaining_gaps=["gap C"],
        )
        assert lr.initial_score == 40
        assert lr.final_score == 82
        assert lr.verdict == "production_ready"
        assert len(lr.improvements) == 2
        assert len(lr.remaining_gaps) == 1


# ===========================================================================
# Test research seeder functions
# ===========================================================================


class TestSeedEvidenceStubs:
    """Test _seed_evidence_stubs creates evidence lane directories."""

    def test_creates_all_lanes(self, tmp_path: Path) -> None:
        chip_dir = tmp_path / "chip"
        chip_dir.mkdir()
        count = _seed_evidence_stubs(chip_dir)
        assert count == len(EVIDENCE_LANES)
        for lane in EVIDENCE_LANES:
            readme = chip_dir / "research" / lane / "README.md"
            assert readme.exists()
            content = readme.read_text(encoding="utf-8")
            assert lane.replace("_", " ").title() in content

    def test_idempotent(self, tmp_path: Path) -> None:
        chip_dir = tmp_path / "chip"
        chip_dir.mkdir()
        first = _seed_evidence_stubs(chip_dir)
        second = _seed_evidence_stubs(chip_dir)
        assert first == len(EVIDENCE_LANES)
        assert second == 0  # Already exist

    def test_does_not_overwrite_existing(self, tmp_path: Path) -> None:
        chip_dir = tmp_path / "chip"
        lane_dir = chip_dir / "research" / "research_grounded"
        lane_dir.mkdir(parents=True)
        custom_content = "# My custom research"
        (lane_dir / "README.md").write_text(custom_content, encoding="utf-8")

        _seed_evidence_stubs(chip_dir)
        assert (lane_dir / "README.md").read_text(encoding="utf-8") == custom_content


class TestSeedResearchSources:
    """Test _seed_research_sources populates source registry."""

    def test_creates_source_registry(self, tmp_path: Path) -> None:
        chip_dir = tmp_path / "chip"
        chip_dir.mkdir()
        brief = _make_brief()
        count = _seed_research_sources(chip_dir, brief)
        assert count > 0
        registry = chip_dir / "docs" / "SOURCE_REGISTRY.md"
        assert registry.exists()
        content = registry.read_text(encoding="utf-8")
        assert "Source Type" in content

    def test_uses_template_source_types(self, tmp_path: Path) -> None:
        chip_dir = tmp_path / "chip"
        chip_dir.mkdir()
        brief = _make_brief()
        brief["_research_source_types"] = ["papers", "datasets"]
        _seed_research_sources(chip_dir, brief)
        content = (chip_dir / "docs" / "SOURCE_REGISTRY.md").read_text(encoding="utf-8")
        assert "papers" in content
        assert "datasets" in content


class TestSeedBenchmarkBaseline:
    """Test _seed_benchmark_baseline creates baseline benchmark."""

    def test_creates_baseline(self, tmp_path: Path) -> None:
        chip_dir = tmp_path / "chip"
        chip_dir.mkdir()
        created = _seed_benchmark_baseline(chip_dir)
        assert created is True
        baseline_path = chip_dir / "research" / "benchmark_grounded" / "baseline_benchmark.json"
        assert baseline_path.exists()
        data = json.loads(baseline_path.read_text(encoding="utf-8"))
        assert data["benchmark_id"] == "baseline-v1"
        assert data["result"]["score"] == 50

    def test_idempotent(self, tmp_path: Path) -> None:
        chip_dir = tmp_path / "chip"
        chip_dir.mkdir()
        first = _seed_benchmark_baseline(chip_dir)
        second = _seed_benchmark_baseline(chip_dir)
        assert first is True
        assert second is False


class TestCreateInitialPackets:
    """Test _create_initial_packets writes packet files."""

    def test_creates_packets(self, tmp_path: Path) -> None:
        chip_dir = tmp_path / "chip"
        chip_dir.mkdir()
        count = _create_initial_packets(chip_dir)
        assert count == 2
        packets_dir = chip_dir / "research" / "packets"
        files = list(packets_dir.glob("*.json"))
        assert len(files) == 2

    def test_idempotent(self, tmp_path: Path) -> None:
        chip_dir = tmp_path / "chip"
        chip_dir.mkdir()
        first = _create_initial_packets(chip_dir)
        second = _create_initial_packets(chip_dir)
        assert first == 2
        assert second == 0

    def test_packet_content_valid_json(self, tmp_path: Path) -> None:
        chip_dir = tmp_path / "chip"
        chip_dir.mkdir()
        _create_initial_packets(chip_dir)
        packets_dir = chip_dir / "research" / "packets"
        for f in packets_dir.glob("*.json"):
            data = json.loads(f.read_text(encoding="utf-8"))
            assert "packet_kind" in data
            assert "evidence_lane" in data
            assert "created_at" in data


# ===========================================================================
# Test RecursiveLoopController -- structural phase
# ===========================================================================


class TestStructuralPhase:
    """Test that the structural phase runs gap_analyzer fixes."""

    def test_structural_phase_improves_score(self, tmp_path: Path) -> None:
        """Scaffold a chip and verify the structural phase can boost its score."""
        chip_dir = _scaffold_chip(tmp_path)
        initial = score_chip(chip_dir)["total_score"]

        config = LoopConfig(
            target_score=100,  # unreachable, just test phase runs
            max_iterations=1,
            structural_fix_enabled=True,
            research_enabled=False,
            evidence_gathering_enabled=False,
        )
        ctrl = RecursiveLoopController(config)

        # Directly test the structural phase
        ctrl._telemetry = LoopTelemetry(
            start_time="test",
            status="running",
        )
        ctrl._current_score = initial
        ctrl._iteration = 0

        improvements = ctrl._structural_phase(chip_dir)
        # The structural phase should produce at least some improvements
        # (scaffolded chips start with most things passing, so this may be empty
        # or have a few fixes)
        assert isinstance(improvements, list)
        assert ctrl._current_score >= initial


# ===========================================================================
# Test RecursiveLoopController -- stall detection
# ===========================================================================


class TestStallDetection:
    """Test stall detection logic."""

    def test_no_stall_with_short_trajectory(self) -> None:
        ctrl = RecursiveLoopController(LoopConfig(max_stall_iterations=3))
        ctrl._telemetry.score_trajectory = [40, 45]
        assert ctrl._detect_stall() is False

    def test_stall_detected_when_scores_flat(self) -> None:
        ctrl = RecursiveLoopController(LoopConfig(max_stall_iterations=3))
        ctrl._telemetry.score_trajectory = [40, 50, 55, 55, 55, 55]
        assert ctrl._detect_stall() is True
        assert ctrl._telemetry.stall_count == 1

    def test_stall_detected_when_no_improvement(self) -> None:
        ctrl = RecursiveLoopController(LoopConfig(max_stall_iterations=3))
        ctrl._telemetry.score_trajectory = [40, 50, 55, 55, 53, 54]
        assert ctrl._detect_stall() is True

    def test_no_stall_when_improving(self) -> None:
        ctrl = RecursiveLoopController(LoopConfig(max_stall_iterations=3))
        ctrl._telemetry.score_trajectory = [40, 50, 55, 56, 58, 60]
        assert ctrl._detect_stall() is False

    def test_stall_count_increments(self) -> None:
        ctrl = RecursiveLoopController(LoopConfig(max_stall_iterations=3))
        ctrl._telemetry.score_trajectory = [40, 50, 55, 55, 55, 55]
        ctrl._detect_stall()
        ctrl._detect_stall()
        assert ctrl._telemetry.stall_count == 2


# ===========================================================================
# Test RecursiveLoopController -- telemetry recording
# ===========================================================================


class TestTelemetryRecording:
    """Test that the controller properly records telemetry."""

    def test_run_on_chip_records_telemetry(self, tmp_path: Path) -> None:
        chip_dir = _create_mock_chip(tmp_path)
        config = LoopConfig(
            target_score=100,  # unreachable
            max_iterations=2,
            max_stall_iterations=3,
            telemetry_enabled=True,
        )
        ctrl = RecursiveLoopController(config)
        ctrl.run_on_chip(chip_dir)

        telemetry = ctrl.get_telemetry()
        assert telemetry.start_time != ""
        assert telemetry.end_time is not None
        assert len(telemetry.score_trajectory) >= 1
        assert len(telemetry.iterations) >= 1
        assert telemetry.status in (
            "running", "completed", "stalled", "target_reached", "max_iterations"
        )

    def test_telemetry_persisted_to_disk(self, tmp_path: Path) -> None:
        chip_dir = _create_mock_chip(tmp_path)
        config = LoopConfig(
            target_score=100,
            max_iterations=1,
            telemetry_enabled=True,
        )
        ctrl = RecursiveLoopController(config)
        ctrl.run_on_chip(chip_dir)

        telemetry_path = chip_dir / "loop_telemetry.json"
        assert telemetry_path.exists()
        data = json.loads(telemetry_path.read_text(encoding="utf-8"))
        assert "start_time" in data
        assert "score_trajectory" in data
        assert "iterations" in data

    def test_telemetry_disabled_no_file(self, tmp_path: Path) -> None:
        chip_dir = _create_mock_chip(tmp_path)
        config = LoopConfig(
            target_score=100,
            max_iterations=1,
            telemetry_enabled=False,
        )
        ctrl = RecursiveLoopController(config)
        ctrl.run_on_chip(chip_dir)

        telemetry_path = chip_dir / "loop_telemetry.json"
        assert not telemetry_path.exists()

    def test_score_trajectory_has_initial_score(self, tmp_path: Path) -> None:
        chip_dir = _create_mock_chip(tmp_path)
        config = LoopConfig(
            target_score=100,
            max_iterations=1,
        )
        ctrl = RecursiveLoopController(config)
        result = ctrl.run_on_chip(chip_dir)

        trajectory = ctrl.get_telemetry().score_trajectory
        assert len(trajectory) >= 1
        assert trajectory[0] == result.initial_score


# ===========================================================================
# Test RecursiveLoopController -- run_from_brief
# ===========================================================================


class TestRunFromBrief:
    """Test run_from_brief scaffolds a chip and runs the loop."""

    def test_creates_chip_directory(self, tmp_path: Path) -> None:
        brief = _make_brief()
        config = LoopConfig(
            target_score=100,
            max_iterations=2,
            max_stall_iterations=3,
        )
        ctrl = RecursiveLoopController(config)
        result = ctrl.run_from_brief(brief, tmp_path)

        assert result.chip_path.exists()
        assert (result.chip_path / "spark-chip.json").exists()
        assert (result.chip_path / "spark-researcher.project.json").exists()

    def test_returns_loop_result(self, tmp_path: Path) -> None:
        brief = _make_brief()
        config = LoopConfig(
            target_score=100,
            max_iterations=2,
            max_stall_iterations=3,
        )
        ctrl = RecursiveLoopController(config)
        result = ctrl.run_from_brief(brief, tmp_path)

        assert isinstance(result, LoopResult)
        assert result.initial_score >= 0
        assert result.final_score >= result.initial_score
        assert result.iterations >= 0
        assert isinstance(result.improvements, list)
        assert isinstance(result.remaining_gaps, list)

    def test_loop_improves_score(self, tmp_path: Path) -> None:
        brief = _make_brief()
        config = LoopConfig(
            target_score=95,
            max_iterations=5,
            max_stall_iterations=4,
        )
        ctrl = RecursiveLoopController(config)
        result = ctrl.run_from_brief(brief, tmp_path)

        assert result.final_score >= result.initial_score

    def test_invalid_brief_raises(self, tmp_path: Path) -> None:
        bad_brief = {"domain_id": ""}  # Missing required fields
        config = LoopConfig()
        ctrl = RecursiveLoopController(config)
        with pytest.raises(ValueError, match="Invalid brief"):
            ctrl.run_from_brief(bad_brief, tmp_path)

    def test_applies_category_template(self, tmp_path: Path) -> None:
        brief = {
            "domain_id": "test-finance",
            "domain_name": "Test Finance",
            "category": "finance",
            "primary_metric": "risk_adjusted_return",
            "mutation_axes": [
                {"name": "risk_model", "values": ["var_95", "cvar"]},
            ],
        }
        config = LoopConfig(
            target_score=100,
            max_iterations=1,
            max_stall_iterations=3,
        )
        ctrl = RecursiveLoopController(config)
        result = ctrl.run_from_brief(brief, tmp_path)
        assert result.chip_path.exists()


# ===========================================================================
# Test RecursiveLoopController -- run_on_chip
# ===========================================================================


class TestRunOnChip:
    """Test run_on_chip on existing chip directories."""

    def test_runs_on_existing_chip(self, tmp_path: Path) -> None:
        chip_dir = _create_mock_chip(tmp_path)
        config = LoopConfig(
            target_score=100,
            max_iterations=2,
            max_stall_iterations=3,
        )
        ctrl = RecursiveLoopController(config)
        result = ctrl.run_on_chip(chip_dir)

        assert isinstance(result, LoopResult)
        assert result.chip_path == chip_dir
        assert result.final_score >= result.initial_score

    def test_missing_chip_raises(self, tmp_path: Path) -> None:
        config = LoopConfig()
        ctrl = RecursiveLoopController(config)
        with pytest.raises(FileNotFoundError):
            ctrl.run_on_chip(tmp_path / "nonexistent-chip")

    def test_target_already_reached(self, tmp_path: Path) -> None:
        chip_dir = _create_mock_chip(tmp_path)
        # Set a very low target that should already be met
        config = LoopConfig(
            target_score=1,
            max_iterations=10,
        )
        ctrl = RecursiveLoopController(config)
        result = ctrl.run_on_chip(chip_dir)

        assert result.iterations == 0
        assert result.final_score >= 1
        assert ctrl.get_telemetry().status == "target_reached"

    def test_max_iterations_respected(self, tmp_path: Path) -> None:
        chip_dir = _create_mock_chip(tmp_path)
        config = LoopConfig(
            target_score=100,  # unreachable
            max_iterations=2,
            max_stall_iterations=5,  # high to avoid stall exit
        )
        ctrl = RecursiveLoopController(config)
        result = ctrl.run_on_chip(chip_dir)

        assert result.iterations <= 2


# ===========================================================================
# Test research seeding integration
# ===========================================================================


class TestResearchSeedingIntegration:
    """Test that research seeding creates proper evidence structures.

    Uses _create_mock_chip which scores below 100, so the loop enters
    the improvement phases (structural, research, evaluation, etc.)
    rather than short-circuiting at target_reached.
    """

    def test_evidence_stubs_in_chip(self, tmp_path: Path) -> None:
        chip_dir = _create_mock_chip(tmp_path)
        config = LoopConfig(
            target_score=100,
            max_iterations=1,
            research_enabled=True,
            max_stall_iterations=3,
        )
        ctrl = RecursiveLoopController(config)
        result = ctrl.run_on_chip(chip_dir)

        # All evidence lanes should have directories
        for lane in EVIDENCE_LANES:
            lane_dir = result.chip_path / "research" / lane
            assert lane_dir.exists(), f"Missing evidence lane: {lane}"

    def test_baseline_benchmark_created(self, tmp_path: Path) -> None:
        chip_dir = _create_mock_chip(tmp_path)
        config = LoopConfig(
            target_score=100,
            max_iterations=1,
            research_enabled=True,
            max_stall_iterations=3,
        )
        ctrl = RecursiveLoopController(config)
        result = ctrl.run_on_chip(chip_dir)

        baseline = result.chip_path / "research" / "benchmark_grounded" / "baseline_benchmark.json"
        assert baseline.exists()

    def test_initial_packets_created(self, tmp_path: Path) -> None:
        chip_dir = _create_mock_chip(tmp_path)
        config = LoopConfig(
            target_score=100,
            max_iterations=1,
            research_enabled=True,
            max_stall_iterations=3,
        )
        ctrl = RecursiveLoopController(config)
        result = ctrl.run_on_chip(chip_dir)

        packets_dir = result.chip_path / "research" / "packets"
        assert packets_dir.exists()
        packet_files = list(packets_dir.glob("*.json"))
        assert len(packet_files) >= 2

    def test_research_disabled_skips_seeding(self, tmp_path: Path) -> None:
        chip_dir = _create_mock_chip(tmp_path)
        config = LoopConfig(
            target_score=100,
            max_iterations=1,
            research_enabled=False,
            max_stall_iterations=3,
        )
        ctrl = RecursiveLoopController(config)
        ctrl.run_on_chip(chip_dir)

        # Should not create evidence lane directories under research/
        # (unless they already existed from mock creation)
        benchmark_dir = chip_dir / "research" / "benchmark_grounded"
        baseline = benchmark_dir / "baseline_benchmark.json"
        assert not baseline.exists()


# ===========================================================================
# Test end-to-end loop behavior
# ===========================================================================


class TestEndToEndLoop:
    """Integration tests for the full loop cycle.

    Note: scaffold_chip with a complete brief produces a chip that scores
    100/100, so it immediately hits target_reached. These tests use
    _create_mock_chip (which scores below 100) to exercise the loop body.
    """

    def test_full_loop_on_mock_chip(self, tmp_path: Path) -> None:
        """End-to-end: existing chip -> loop -> result."""
        chip_dir = _create_mock_chip(tmp_path)
        config = LoopConfig(
            target_score=100,
            max_iterations=3,
            max_stall_iterations=5,
        )
        ctrl = RecursiveLoopController(config)
        result = ctrl.run_on_chip(chip_dir)

        # Basic sanity
        assert result.chip_path.exists()
        assert result.final_score >= result.initial_score
        assert isinstance(result.verdict, str)
        assert result.verdict in (
            "production_ready", "beta", "alpha", "scaffold", "not_found"
        )

        # Telemetry was recorded
        telemetry = ctrl.get_telemetry()
        assert telemetry.start_time != ""
        assert telemetry.end_time is not None
        assert len(telemetry.score_trajectory) >= 2  # at least initial + one phase

    def test_full_loop_from_brief_high_score(self, tmp_path: Path) -> None:
        """Scaffolded chip with complete brief reaches target immediately."""
        brief = _make_brief()
        config = LoopConfig(
            target_score=80,
            max_iterations=10,
            max_stall_iterations=5,
        )
        ctrl = RecursiveLoopController(config)
        result = ctrl.run_from_brief(brief, tmp_path)

        # Scaffolded chip should reach target immediately
        assert result.chip_path.exists()
        assert result.final_score >= 80
        assert result.verdict == "production_ready"
        assert ctrl.get_telemetry().status == "target_reached"

    def test_improvements_list_populated(self, tmp_path: Path) -> None:
        """Use mock chip so the loop actually runs phases and produces improvements."""
        chip_dir = _create_mock_chip(tmp_path)
        config = LoopConfig(
            target_score=100,
            max_iterations=3,
            max_stall_iterations=5,
        )
        ctrl = RecursiveLoopController(config)
        result = ctrl.run_on_chip(chip_dir)

        # The loop should have made at least some improvements
        assert isinstance(result.improvements, list)
        # With all phases enabled, at least research seeding should produce entries
        assert len(result.improvements) >= 1

    def test_remaining_gaps_list(self, tmp_path: Path) -> None:
        brief = _make_brief()
        config = LoopConfig(
            target_score=100,
            max_iterations=2,
            max_stall_iterations=3,
        )
        ctrl = RecursiveLoopController(config)
        result = ctrl.run_from_brief(brief, tmp_path)

        # remaining_gaps is always a list, but may be empty if chip scores 100
        assert isinstance(result.remaining_gaps, list)
