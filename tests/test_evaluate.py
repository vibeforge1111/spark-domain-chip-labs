"""Tests for the meta-evaluator module."""

import pytest

from chip_labs.evaluate import evaluate


class TestMethodologyFocus:
    """Test evaluate with research_focus='methodology'."""

    def test_methodology_returns_positive_coverage(self) -> None:
        result = evaluate({"research_focus": "methodology"})
        assert result["methodology_coverage"] > 0

    def test_methodology_has_comparison_class(self) -> None:
        result = evaluate({"research_focus": "methodology"})
        assert result["comparison_class"] == "exploratory_frontier"

    def test_methodology_has_area_field(self) -> None:
        result = evaluate({"research_focus": "methodology"})
        assert "methodology_area" in result

    def test_methodology_custom_area(self) -> None:
        result = evaluate({
            "research_focus": "methodology",
            "methodology_area": "scoring_systems",
        })
        assert result["methodology_area"] == "scoring_systems"
        assert result["methodology_coverage"] > 0


class TestAgiTheoryFocus:
    """Test evaluate with research_focus='agi_theory'."""

    def test_agi_theory_returns_exploratory_frontier(self) -> None:
        result = evaluate({"research_focus": "agi_theory"})
        assert result["comparison_class"] == "exploratory_frontier"

    def test_agi_theory_has_note(self) -> None:
        result = evaluate({"research_focus": "agi_theory"})
        assert "note" in result

    def test_agi_theory_low_initial_score(self) -> None:
        result = evaluate({"research_focus": "agi_theory"})
        assert result["lab_research_quality_score"] < 0.5


class TestUnknownFocus:
    """Test evaluate with an unknown research_focus."""

    def test_unknown_focus_returns_error(self) -> None:
        result = evaluate({"research_focus": "totally_invalid_focus"})
        assert "error" in result

    def test_unknown_focus_zero_score(self) -> None:
        result = evaluate({"research_focus": "totally_invalid_focus"})
        assert result["lab_research_quality_score"] == 0.0

    def test_unknown_focus_has_comparison_class(self) -> None:
        result = evaluate({"research_focus": "totally_invalid_focus"})
        assert "comparison_class" in result
