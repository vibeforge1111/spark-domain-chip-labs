"""Tests for the quality rubric scoring module."""

import json
from pathlib import Path


from chip_labs.quality_rubric import score_chip, RUBRIC_DIMENSIONS


def _create_mock_chip(tmp_path: Path) -> Path:
    """Create a mock chip directory with standard files for testing."""
    chip_dir = tmp_path / "domain-chip-mock"
    chip_dir.mkdir()

    # spark-chip.json
    manifest = {
        "schema_version": "spark-chip.v1",
        "io_protocol": "spark-hook-io.v1",
        "domain": "mock",
        "version": "0.1.0",
        "capabilities": ["evaluate", "suggest", "packets", "watchtower"],
        "frontier": {
            "enabled": True,
            "allowed_mutations": ["research_focus"],
            "required_fields": ["research_focus"],
            "field_patterns": {"research_focus": "^[a-z_]+$"},
        },
    }
    (chip_dir / "spark-chip.json").write_text(json.dumps(manifest), encoding="utf-8")

    # spark-researcher.project.json
    project = {
        "project_name": "mock-chip",
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
            "max_loop_iterations": 10,
            "blocked_command_fragments": ["rm -rf"],
        },
        "self_edit": {"mutable_targets": ["src/"]},
        "memory": {"backend": "local"},
    }
    (chip_dir / "spark-researcher.project.json").write_text(
        json.dumps(project), encoding="utf-8"
    )

    # pyproject.toml
    (chip_dir / "pyproject.toml").write_text(
        '[project]\nname = "domain-chip-mock"\nversion = "0.1.0"\n',
        encoding="utf-8",
    )

    # README.md
    (chip_dir / "README.md").write_text(
        "# Mock Chip\n\n## Mission\n\nThis is a mock chip for testing.\n",
        encoding="utf-8",
    )

    # src/ with a .py file containing scoring logic
    src_dir = chip_dir / "src"
    src_dir.mkdir()
    (src_dir / "evaluate.py").write_text(
        "def score(mutations):\n    return 0.5\n",
        encoding="utf-8",
    )

    # docs/ with a .md file referencing sources and architecture
    docs_dir = chip_dir / "docs"
    docs_dir.mkdir()
    (docs_dir / "source_registry.md").write_text(
        "# Source Registry\n\nSource map and list of primary sources.\n",
        encoding="utf-8",
    )
    (docs_dir / "architecture.md").write_text(
        "# Architecture\n\nOne-loop architecture for the mock chip.\n",
        encoding="utf-8",
    )
    (docs_dir / "mission.md").write_text(
        "# Mission\n\nThe intent of the mock chip.\n",
        encoding="utf-8",
    )

    return chip_dir


class TestScoreValidChip:
    """Test scoring a valid mock chip directory."""

    def test_returns_dict_with_required_keys(self, tmp_path: Path) -> None:
        chip_dir = _create_mock_chip(tmp_path)
        result = score_chip(chip_dir)
        assert isinstance(result, dict)
        assert "total_score" in result
        assert "dimensions" in result
        assert "passed_checks" in result
        assert "failed_checks" in result
        assert "verdict" in result

    def test_total_score_is_positive(self, tmp_path: Path) -> None:
        chip_dir = _create_mock_chip(tmp_path)
        result = score_chip(chip_dir)
        assert result["total_score"] > 0

    def test_dimensions_match_rubric(self, tmp_path: Path) -> None:
        chip_dir = _create_mock_chip(tmp_path)
        result = score_chip(chip_dir)
        dimension_names = {d["name"] for d in result["dimensions"]}
        expected_names = {d["name"] for d in RUBRIC_DIMENSIONS}
        assert dimension_names == expected_names

    def test_passed_and_failed_are_disjoint(self, tmp_path: Path) -> None:
        chip_dir = _create_mock_chip(tmp_path)
        result = score_chip(chip_dir)
        passed = set(result["passed_checks"])
        failed = set(result["failed_checks"])
        assert passed.isdisjoint(failed)


class TestScoreMissingPath:
    """Test scoring a path that does not exist."""

    def test_missing_path_returns_score_zero(self, tmp_path: Path) -> None:
        result = score_chip(tmp_path / "nonexistent-chip")
        assert result["total_score"] == 0

    def test_missing_path_verdict_is_not_found(self, tmp_path: Path) -> None:
        result = score_chip(tmp_path / "nonexistent-chip")
        assert result["verdict"] == "not_found"

    def test_missing_path_has_error_key(self, tmp_path: Path) -> None:
        result = score_chip(tmp_path / "nonexistent-chip")
        assert "error" in result


class TestScoreEmptyDirectory:
    """Test scoring an empty directory returns a low score."""

    def test_empty_dir_low_score(self, tmp_path: Path) -> None:
        empty_chip = tmp_path / "domain-chip-empty"
        empty_chip.mkdir()
        result = score_chip(empty_chip)
        assert result["total_score"] < 35

    def test_empty_dir_scaffold_verdict(self, tmp_path: Path) -> None:
        empty_chip = tmp_path / "domain-chip-empty"
        empty_chip.mkdir()
        result = score_chip(empty_chip)
        assert result["verdict"] == "scaffold"


class TestVerdictThresholds:
    """Test verdict assignment thresholds."""

    def test_production_ready_requires_80_or_more(self, tmp_path: Path) -> None:
        """Verify the production_ready threshold is >= 80."""
        # We cannot easily force an exact score, but we verify the logic:
        # If total_score >= 80 then verdict == "production_ready"
        chip_dir = _create_mock_chip(tmp_path)
        result = score_chip(chip_dir)
        if result["total_score"] >= 80:
            assert result["verdict"] == "production_ready"
        else:
            assert result["verdict"] != "production_ready"

    def test_scaffold_verdict_for_low_score(self, tmp_path: Path) -> None:
        """Verify that score < 35 yields scaffold verdict."""
        empty_chip = tmp_path / "domain-chip-bare"
        empty_chip.mkdir()
        result = score_chip(empty_chip)
        assert result["total_score"] < 35
        assert result["verdict"] == "scaffold"
