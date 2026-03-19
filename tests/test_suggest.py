"""Tests for the suggestion engine module."""

from pathlib import Path

import pytest

from chip_labs.suggest import suggest


class TestSuggestBasic:
    """Test basic suggestion generation."""

    def test_suggest_returns_list(self, tmp_path: Path) -> None:
        result = suggest(chip_search_dir=tmp_path)
        assert isinstance(result, list)

    def test_suggestions_are_non_empty(self, tmp_path: Path) -> None:
        """With no chips discovered, methodology and domain-discovery
        suggestions should still be generated."""
        result = suggest(chip_search_dir=tmp_path)
        assert len(result) > 0


class TestSuggestionFields:
    """Test that suggestions have the required fields."""

    def test_has_candidate_id(self, tmp_path: Path) -> None:
        result = suggest(chip_search_dir=tmp_path)
        for s in result:
            assert "candidate_id" in s, f"Missing candidate_id in suggestion: {s}"

    def test_has_mutations(self, tmp_path: Path) -> None:
        result = suggest(chip_search_dir=tmp_path)
        for s in result:
            assert "mutations" in s, f"Missing mutations in suggestion: {s}"
            assert isinstance(s["mutations"], dict)

    def test_has_hypothesis(self, tmp_path: Path) -> None:
        result = suggest(chip_search_dir=tmp_path)
        for s in result:
            assert "hypothesis" in s, f"Missing hypothesis in suggestion: {s}"
            assert len(s["hypothesis"]) > 0


class TestRecentMutationsFilter:
    """Test that recent_mutations filters out already-tried suggestions."""

    def test_recent_mutations_reduces_suggestions(self, tmp_path: Path) -> None:
        all_suggestions = suggest(chip_search_dir=tmp_path)
        if not all_suggestions:
            pytest.skip("No suggestions generated to filter")

        # Use the first suggestion's mutations as a recent mutation
        first_mutation = all_suggestions[0]["mutations"]
        filtered = suggest(
            recent_mutations=[first_mutation],
            chip_search_dir=tmp_path,
        )
        assert len(filtered) < len(all_suggestions)

    def test_filtering_all_removes_corresponding_entries(self, tmp_path: Path) -> None:
        all_suggestions = suggest(chip_search_dir=tmp_path)
        all_mutations = [s["mutations"] for s in all_suggestions]

        filtered = suggest(
            recent_mutations=all_mutations,
            chip_search_dir=tmp_path,
        )
        assert len(filtered) == 0
