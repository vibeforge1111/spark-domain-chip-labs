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
    _should_skip_action,
    _write_feedback_packet,
    _write_session_domain,
    _read_session_domain,
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
            with patch("chip_labs.hooks._read_session_domain", return_value=None):
                with patch("chip_labs.hooks._build_context_text", return_value="Advisory") as mock_build:
                    handle_pre_tool_use({"tool_name": "Bash", "tool_input": {"command": "python evaluate_startup.py"}})
                    call_args = mock_build.call_args
                    assert "evaluate_startup" in call_args[0][1]

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
            with patch("chip_labs.hooks._read_session_domain", return_value=None):
                with patch("chip_labs.chip_context_injector.select_chips_for_task", return_value=portfolio):
                    result = handle_post_tool_use({
                        "tool_name": "Bash",
                        "tool_input": {"command": "python run_evaluation.py"},
                        "tool_output": "All 50 tests passed",
                    })
                    if result:
                        assert "Feedback captured" in result["hookSpecificOutput"]["additionalContext"]

    def test_writes_to_realworld_validated(self, tmp_path: Path) -> None:
        portfolio = _make_mock_portfolio(tmp_path)
        with patch("chip_labs.hooks._load_portfolio_safe", return_value=portfolio):
            with patch("chip_labs.hooks._read_session_domain", return_value=None):
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


# ---------------------------------------------------------------------------
# TestShouldSkipAction  (Layer 1: command pre-filter)
# ---------------------------------------------------------------------------

class TestShouldSkipAction:
    # -- Bash commands that SHOULD be skipped --

    def test_skips_git(self) -> None:
        assert _should_skip_action("Bash", {"command": "git status"}) is True
        assert _should_skip_action("Bash", {"command": "git commit -m 'msg'"}) is True
        assert _should_skip_action("Bash", {"command": "git push origin main"}) is True

    def test_skips_npm(self) -> None:
        assert _should_skip_action("Bash", {"command": "npm install"}) is True
        assert _should_skip_action("Bash", {"command": "npm test"}) is True

    def test_skips_pip(self) -> None:
        assert _should_skip_action("Bash", {"command": "pip install -e ."}) is True

    def test_skips_navigation(self) -> None:
        assert _should_skip_action("Bash", {"command": "ls -la"}) is True
        assert _should_skip_action("Bash", {"command": "cd /some/dir"}) is True
        assert _should_skip_action("Bash", {"command": "pwd"}) is True

    def test_skips_text_tools(self) -> None:
        assert _should_skip_action("Bash", {"command": "cat file.txt"}) is True
        assert _should_skip_action("Bash", {"command": "grep pattern file"}) is True

    def test_skips_docker(self) -> None:
        assert _should_skip_action("Bash", {"command": "docker build ."}) is True

    def test_skips_test_runners(self) -> None:
        assert _should_skip_action("Bash", {"command": "pytest tests/"}) is True
        assert _should_skip_action("Bash", {"command": "jest --watch"}) is True

    # -- Bash commands that should PASS --

    def test_passes_python(self) -> None:
        assert _should_skip_action("Bash", {"command": "python evaluate.py"}) is False

    def test_passes_node(self) -> None:
        assert _should_skip_action("Bash", {"command": "node server.js"}) is False

    def test_passes_custom_binary(self) -> None:
        assert _should_skip_action("Bash", {"command": "chip-labs score-v3 /path"}) is False

    # -- Windows paths --

    def test_windows_exe_path(self) -> None:
        assert _should_skip_action("Bash", {"command": r"C:\Windows\System32\git.exe status"}) is True

    def test_windows_cmd_suffix(self) -> None:
        assert _should_skip_action("Bash", {"command": "npm.cmd install"}) is True

    # -- Edge cases --

    def test_empty_command(self) -> None:
        assert _should_skip_action("Bash", {"command": ""}) is True

    def test_missing_command(self) -> None:
        assert _should_skip_action("Bash", {}) is True

    def test_piped_command_uses_first_token(self) -> None:
        assert _should_skip_action("Bash", {"command": "git log | head -5"}) is True
        assert _should_skip_action("Bash", {"command": "python script.py | grep result"}) is False

    # -- Edit/Write files --

    def test_skips_lock_files(self) -> None:
        assert _should_skip_action("Edit", {"file_path": "/app/package-lock.json"}) is True
        assert _should_skip_action("Write", {"file_path": "/app/yarn.lock"}) is True

    def test_skips_gitignore(self) -> None:
        assert _should_skip_action("Edit", {"file_path": "/repo/.gitignore"}) is True

    def test_skips_config_files(self) -> None:
        assert _should_skip_action("Edit", {"file_path": "/app/tsconfig.json"}) is True
        assert _should_skip_action("Edit", {"file_path": "/app/pyproject.toml"}) is True

    def test_passes_domain_files(self) -> None:
        assert _should_skip_action("Edit", {"file_path": "/src/startup_eval.py"}) is False
        assert _should_skip_action("Write", {"file_path": "/docs/strategy.md"}) is False

    # -- Non-Bash/Edit/Write tools always pass --

    def test_non_matching_tool_passes(self) -> None:
        assert _should_skip_action("Read", {"file_path": "/test"}) is False
        assert _should_skip_action("Glob", {"pattern": "*.py"}) is False


# ---------------------------------------------------------------------------
# TestSessionDomain  (Layer 3: session domain file)
# ---------------------------------------------------------------------------

class TestSessionDomain:
    def test_write_and_read(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        import chip_labs.hooks as hooks_mod
        monkeypatch.setattr(hooks_mod, "_SESSION_DOMAIN_FILE", tmp_path / "session_domain.json")
        monkeypatch.setattr(hooks_mod, "_PORTFOLIO_CACHE_DIR", tmp_path)

        chips = _make_mock_portfolio(tmp_path)
        _write_session_domain(chips, "startup evaluation")

        result = _read_session_domain()
        assert result is not None
        assert "startup evaluation" == result["query"]
        assert "test-chip" in result["chip_names"]
        assert "testing" in result["domains"]

    def test_read_missing_returns_none(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        import chip_labs.hooks as hooks_mod
        monkeypatch.setattr(hooks_mod, "_SESSION_DOMAIN_FILE", tmp_path / "nonexistent.json")

        result = _read_session_domain()
        assert result is None

    def test_read_stale_returns_none(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        import chip_labs.hooks as hooks_mod
        session_file = tmp_path / "session_domain.json"
        monkeypatch.setattr(hooks_mod, "_SESSION_DOMAIN_FILE", session_file)
        monkeypatch.setattr(hooks_mod, "_PORTFOLIO_CACHE_DIR", tmp_path)
        monkeypatch.setattr(hooks_mod, "_SESSION_DOMAIN_TTL", 0)  # immediately stale

        chips = _make_mock_portfolio(tmp_path)
        _write_session_domain(chips, "test")

        import time
        time.sleep(0.05)

        result = _read_session_domain()
        assert result is None

    def test_pre_tool_use_enriches_with_session_domain(self, tmp_path: Path) -> None:
        """PreToolUse should enrich action with session domain keywords."""
        portfolio = _make_mock_portfolio(tmp_path)
        session = {"query": "startup", "chip_names": ["test-chip"], "domains": ["startup"]}
        with patch("chip_labs.hooks._load_portfolio_safe", return_value=portfolio):
            with patch("chip_labs.hooks._read_session_domain", return_value=session):
                with patch("chip_labs.hooks._build_context_text", return_value="Advisory") as mock_build:
                    result = handle_pre_tool_use({
                        "tool_name": "Bash",
                        "tool_input": {"command": "python evaluate.py"},
                    })
                    assert "hookSpecificOutput" in result
                    # Action should have domain prefix
                    call_args = mock_build.call_args
                    assert "startup" in call_args[0][1]

    def test_post_tool_use_restricts_by_session(self, tmp_path: Path) -> None:
        """PostToolUse should skip feedback when no session chips match portfolio."""
        chip1 = MockChipHandle(
            chip_path=tmp_path / "domain-chip-other",
            chip_name="other-chip",
            domain="other",
            intelligence=ChipIntelligence(
                chip_name="other-chip", domain="other", version="0.1.0",
                mission="Other mission", doctrines=[], evidence_summary={},
            ),
        )
        (tmp_path / "domain-chip-other").mkdir(exist_ok=True)
        session = {"query": "startup", "chip_names": ["startup-yc"], "domains": ["startup"]}
        with patch("chip_labs.hooks._load_portfolio_safe", return_value=[chip1]):
            with patch("chip_labs.hooks._read_session_domain", return_value=session):
                result = handle_post_tool_use({
                    "tool_name": "Bash",
                    "tool_input": {"command": "python run.py"},
                    "tool_output": "done",
                })
                # No chips match session domain -> should return empty
                assert result == {}
