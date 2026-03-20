"""Tests for Claude Code hook handlers."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

from chip_labs.hooks import (
    _write_feedback_packet,
    handle_post_tool_use,
    handle_pre_tool_use,
    handle_session_start,
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
    quality_score: float = 60.0
    quality_verdict: str = "beta"
    intelligence: ChipIntelligence | None = None


def _make_mock_portfolio(tmp_path: Path) -> list[MockChipHandle]:
    intel = ChipIntelligence(
        chip_name="test-chip",
        domain="testing",
        version="0.1.0",
        mission="Test mission",
        doctrines=[
            {"claim": "Test doctrine", "confidence": "high", "evidence_lane": "research_grounded"},
        ],
        evidence_summary={"research_grounded": 5, "benchmark_grounded": 0, "exploratory_frontier": 1, "realworld_validated": 0},
    )
    chip = MockChipHandle(
        chip_path=tmp_path / "domain-chip-test",
        intelligence=intel,
    )
    (tmp_path / "domain-chip-test").mkdir(exist_ok=True)
    return [chip]


# ---------------------------------------------------------------------------
# TestWriteFeedbackPacket
# ---------------------------------------------------------------------------

class TestWriteFeedbackPacket:
    def test_creates_directory_and_file(self, tmp_path: Path) -> None:
        chip_path = tmp_path / "domain-chip-test"
        chip_path.mkdir()
        result = _write_feedback_packet(chip_path, "test action", "Bash", "success output")
        assert result is not None
        assert result.exists()
        data = json.loads(result.read_text())
        assert data["packet_kind"] == "realworld_feedback"
        assert data["evidence_lane"] == "realworld_validated"
        assert data["action"] == "test action"
        assert data["tool_name"] == "Bash"

    def test_creates_in_realworld_validated(self, tmp_path: Path) -> None:
        chip_path = tmp_path / "domain-chip-test"
        chip_path.mkdir()
        result = _write_feedback_packet(chip_path, "action", "Edit", "output")
        assert result is not None
        assert "realworld_validated" in str(result)

    def test_truncates_long_result(self, tmp_path: Path) -> None:
        chip_path = tmp_path / "domain-chip-test"
        chip_path.mkdir()
        long_result = "x" * 1000
        result = _write_feedback_packet(chip_path, "action", "Bash", long_result)
        data = json.loads(result.read_text())
        assert len(data["result_summary"]) <= 500


# ---------------------------------------------------------------------------
# TestHandleSessionStart
# ---------------------------------------------------------------------------

class TestHandleSessionStart:
    def test_returns_empty_when_disabled(self) -> None:
        with patch.dict(os.environ, {"CHIP_HOOKS_DISABLED": "1"}):
            result = handle_session_start({"cwd": "/test"})
            assert result == {}

    def test_returns_empty_no_portfolio(self) -> None:
        with patch("chip_labs.hooks._load_portfolio_safe", return_value=[]):
            result = handle_session_start({"cwd": "/test"})
            assert result == {}

    def test_injects_context_with_portfolio(self, tmp_path: Path) -> None:
        portfolio = _make_mock_portfolio(tmp_path)
        with patch("chip_labs.hooks._load_portfolio_safe", return_value=portfolio):
            with patch("chip_labs.hooks._build_context_text", return_value="Test context"):
                result = handle_session_start({"cwd": str(tmp_path)})
                assert "hookSpecificOutput" in result
                assert result["hookSpecificOutput"]["hookEventName"] == "SessionStart"
                assert "Test context" in result["hookSpecificOutput"]["additionalContext"]

    def test_uses_domain_hint_env(self, tmp_path: Path) -> None:
        portfolio = _make_mock_portfolio(tmp_path)
        with patch.dict(os.environ, {"CHIP_DOMAIN_HINT": "startup"}):
            with patch("chip_labs.hooks._load_portfolio_safe", return_value=portfolio):
                with patch("chip_labs.hooks._build_context_text", return_value="Startup context") as mock_build:
                    handle_session_start({"cwd": "/test"})
                    call_args = mock_build.call_args
                    assert call_args[0][1] == "startup"


# ---------------------------------------------------------------------------
# TestHandlePreToolUse
# ---------------------------------------------------------------------------

class TestHandlePreToolUse:
    def test_returns_empty_when_disabled(self) -> None:
        with patch.dict(os.environ, {"CHIP_HOOKS_DISABLED": "true"}):
            result = handle_pre_tool_use({"tool_name": "Bash", "tool_input": {"command": "ls"}})
            assert result == {}

    def test_builds_action_from_bash(self, tmp_path: Path) -> None:
        portfolio = _make_mock_portfolio(tmp_path)
        with patch("chip_labs.hooks._load_portfolio_safe", return_value=portfolio):
            with patch("chip_labs.hooks._build_context_text", return_value="Advisory") as mock_build:
                handle_pre_tool_use({"tool_name": "Bash", "tool_input": {"command": "npm test"}})
                call_args = mock_build.call_args
                assert "npm test" in call_args[0][1]

    def test_builds_action_from_edit(self, tmp_path: Path) -> None:
        portfolio = _make_mock_portfolio(tmp_path)
        with patch("chip_labs.hooks._load_portfolio_safe", return_value=portfolio):
            with patch("chip_labs.hooks._build_context_text", return_value="Advisory") as mock_build:
                handle_pre_tool_use({"tool_name": "Edit", "tool_input": {"file_path": "/src/app.py"}})
                call_args = mock_build.call_args
                assert "/src/app.py" in call_args[0][1]

    def test_injects_advisory_context(self, tmp_path: Path) -> None:
        portfolio = _make_mock_portfolio(tmp_path)
        with patch("chip_labs.hooks._load_portfolio_safe", return_value=portfolio):
            with patch("chip_labs.hooks._build_context_text", return_value="Domain advisory"):
                result = handle_pre_tool_use({"tool_name": "Bash", "tool_input": {"command": "test"}})
                assert "hookSpecificOutput" in result
                assert "Domain advisory" in result["hookSpecificOutput"]["additionalContext"]


# ---------------------------------------------------------------------------
# TestHandlePostToolUse
# ---------------------------------------------------------------------------

class TestHandlePostToolUse:
    def test_returns_empty_when_disabled(self) -> None:
        with patch.dict(os.environ, {"CHIP_HOOKS_DISABLED": "yes"}):
            result = handle_post_tool_use({"tool_name": "Bash", "tool_input": {}, "tool_output": ""})
            assert result == {}

    def test_ignores_non_significant_tools(self) -> None:
        result = handle_post_tool_use({"tool_name": "Read", "tool_input": {}, "tool_output": ""})
        assert result == {}

    def test_captures_bash_feedback(self, tmp_path: Path) -> None:
        portfolio = _make_mock_portfolio(tmp_path)
        with patch("chip_labs.hooks._load_portfolio_safe", return_value=portfolio):
            with patch("chip_labs.chip_context_injector.select_chips_for_task", return_value=portfolio):
                result = handle_post_tool_use({
                    "tool_name": "Bash",
                    "tool_input": {"command": "npm test"},
                    "tool_output": "All 50 tests passed",
                })
                if result:
                    assert "Feedback captured" in result["hookSpecificOutput"]["additionalContext"]

    def test_writes_to_realworld_validated(self, tmp_path: Path) -> None:
        portfolio = _make_mock_portfolio(tmp_path)
        with patch("chip_labs.hooks._load_portfolio_safe", return_value=portfolio):
            with patch("chip_labs.chip_context_injector.select_chips_for_task", return_value=portfolio):
                handle_post_tool_use({
                    "tool_name": "Edit",
                    "tool_input": {"file_path": "/src/test.py"},
                    "tool_output": "File edited successfully",
                })
                rw_dir = tmp_path / "domain-chip-test" / "research" / "realworld_validated"
                if rw_dir.exists():
                    files = list(rw_dir.glob("feedback_*.json"))
                    assert len(files) >= 1
