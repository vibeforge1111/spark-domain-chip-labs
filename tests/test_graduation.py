"""Tests for the graduation assessment module."""

from pathlib import Path

import pytest

from chip_labs.graduation import assess_graduation, GRADUATION_CRITERIA


class TestAssessMissingPath:
    """Test graduation assessment on a path that does not exist."""

    def test_missing_path_returns_not_ready(self, tmp_path: Path) -> None:
        result = assess_graduation(tmp_path / "nonexistent-chip")
        assert result["verdict"] == "not_ready"

    def test_missing_path_zero_readiness(self, tmp_path: Path) -> None:
        result = assess_graduation(tmp_path / "nonexistent-chip")
        assert result["readiness_score"] < 0.5

    def test_missing_path_no_required_passed(self, tmp_path: Path) -> None:
        result = assess_graduation(tmp_path / "nonexistent-chip")
        assert result["all_required_passed"] is False


class TestHumanApproval:
    """Test that human_approval is always False for automated assessment."""

    def test_human_approval_false_on_missing_path(self, tmp_path: Path) -> None:
        result = assess_graduation(tmp_path / "nonexistent-chip")
        human_criterion = next(
            c for c in result["criteria"] if c["id"] == "human_approval"
        )
        assert human_criterion["passed"] is False

    def test_human_approval_false_on_empty_chip(self, tmp_path: Path) -> None:
        chip_dir = tmp_path / "domain-chip-empty"
        chip_dir.mkdir()
        result = assess_graduation(chip_dir)
        human_criterion = next(
            c for c in result["criteria"] if c["id"] == "human_approval"
        )
        assert human_criterion["passed"] is False


class TestGraduationCriteria:
    """Test the graduation criteria list structure."""

    def test_criteria_list_has_seven_items(self) -> None:
        assert len(GRADUATION_CRITERIA) == 7

    def test_criteria_have_required_fields(self) -> None:
        for criterion in GRADUATION_CRITERIA:
            assert "id" in criterion
            assert "label" in criterion
            assert "description" in criterion
            assert "weight" in criterion
            assert "required" in criterion

    def test_criteria_weights_sum_to_one(self) -> None:
        total_weight = sum(c["weight"] for c in GRADUATION_CRITERIA)
        assert abs(total_weight - 1.0) < 0.01

    def test_criteria_ids_are_unique(self) -> None:
        ids = [c["id"] for c in GRADUATION_CRITERIA]
        assert len(ids) == len(set(ids))

    def test_human_approval_is_required(self) -> None:
        human = next(c for c in GRADUATION_CRITERIA if c["id"] == "human_approval")
        assert human["required"] is True
