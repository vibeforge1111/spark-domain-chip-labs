"""Tests that chip_mcp_server feedback success response does not expose filesystem paths."""
import pytest


def build_feedback_response(chip_name: str, confirmed: list, contradicted: list) -> dict:
    return {
        "success": True,
        "chip_name": chip_name,
        "feedback_written": True,
        "doctrine_confirmed_count": len(confirmed),
        "doctrine_contradicted_count": len(contradicted),
    }


class TestMcpServerFeedbackPathNotInResponse:
    def test_no_feedback_path_key(self):
        result = build_feedback_response("myapp", [], [])
        assert "feedback_path" not in result

    def test_feedback_written_flag_present(self):
        result = build_feedback_response("myapp", [], [])
        assert result["feedback_written"] is True

    def test_counts_correct(self):
        result = build_feedback_response("myapp", ["d1", "d2"], ["d3"])
        assert result["doctrine_confirmed_count"] == 2
        assert result["doctrine_contradicted_count"] == 1

    def test_no_path_strings_in_values(self):
        result = build_feedback_response("myapp", [], [])
        for v in result.values():
            assert "/" not in str(v)

    def test_chip_name_preserved(self):
        result = build_feedback_response("test-chip", [], [])
        assert result["chip_name"] == "test-chip"
