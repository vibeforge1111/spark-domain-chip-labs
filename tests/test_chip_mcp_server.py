"""Tests for chip_mcp_server -- MCP protocol + tool handlers."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from unittest.mock import patch


from chip_labs.chip_mcp_server import (
    PROTOCOL_VERSION,
    SERVER_NAME,
    TOOLS,
    ChipMCPServer,
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
) -> ChipIntelligence:
    return ChipIntelligence(
        chip_name=chip_name,
        domain=domain,
        version="0.1.0",
        mission="Test mission for unit tests.",
        doctrines=doctrines or [
            {"claim": "Test claim", "confidence": "high", "evidence_lane": "research_grounded"},
        ],
        contradictions=contradictions or [],
        evidence_summary={"research_grounded": 5, "benchmark_grounded": 0, "exploratory_frontier": 1, "realworld_validated": 0},
    )


def _make_portfolio(tmp_path: Path | None = None) -> list[MockChipHandle]:
    path = tmp_path / "domain-chip-test" if tmp_path else Path("/mock/domain-chip-test")
    return [
        MockChipHandle(
            chip_path=path,
            chip_name="test-chip",
            domain="testing",
            intelligence=_make_intel(),
        ),
        MockChipHandle(
            chip_path=path.parent / "domain-chip-startup",
            chip_name="startup-yc",
            domain="startup",
            quality_score=70.0,
            intelligence=_make_intel("startup-yc", "startup", doctrines=[
                {"claim": "Founder velocity matters", "confidence": "very high"},
                {"claim": "Market size drives exits", "confidence": "high"},
            ]),
        ),
    ]


# ---------------------------------------------------------------------------
# TestToolDefinitions
# ---------------------------------------------------------------------------

class TestToolDefinitions:
    def test_seven_tools_defined(self) -> None:
        assert len(TOOLS) == 7

    def test_all_tools_have_required_fields(self) -> None:
        for tool in TOOLS:
            assert "name" in tool
            assert "description" in tool
            assert "inputSchema" in tool

    def test_tool_names(self) -> None:
        names = {t["name"] for t in TOOLS}
        expected = {"chip_query", "chip_advise", "chip_evaluate", "chip_doctrines",
                    "chip_portfolio", "chip_feedback", "chip_suggest"}
        assert names == expected


# ---------------------------------------------------------------------------
# TestMCPProtocol
# ---------------------------------------------------------------------------

class TestMCPProtocol:
    def test_initialize(self) -> None:
        server = ChipMCPServer()
        resp = server._handle_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {},
        })
        assert resp["id"] == 1
        assert resp["result"]["protocolVersion"] == PROTOCOL_VERSION
        assert resp["result"]["serverInfo"]["name"] == SERVER_NAME
        assert server._initialized is True

    def test_tools_list(self) -> None:
        server = ChipMCPServer()
        resp = server._handle_request({
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {},
        })
        assert len(resp["result"]["tools"]) == 7

    def test_unknown_method_with_id(self) -> None:
        server = ChipMCPServer()
        resp = server._handle_request({
            "jsonrpc": "2.0",
            "id": 3,
            "method": "unknown/method",
        })
        assert "error" in resp
        assert resp["error"]["code"] == -32601

    def test_notification_returns_empty(self) -> None:
        server = ChipMCPServer()
        resp = server._handle_request({
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
        })
        assert resp == {}


# ---------------------------------------------------------------------------
# TestToolDispatch
# ---------------------------------------------------------------------------

class TestToolDispatch:
    def test_unknown_tool(self) -> None:
        server = ChipMCPServer()
        result = server._dispatch_tool("nonexistent_tool", {})
        assert "error" in result

    def test_tools_call_wraps_result(self) -> None:
        server = ChipMCPServer()
        server._portfolio = _make_portfolio()
        server._last_load = 9999999999  # prevent reload
        resp = server._handle_request({
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {"name": "chip_portfolio", "arguments": {}},
        })
        assert resp["id"] == 4
        content = resp["result"]["content"]
        assert len(content) == 1
        assert content[0]["type"] == "text"
        data = json.loads(content[0]["text"])
        assert data["chip_count"] == 2


# ---------------------------------------------------------------------------
# TestChipPortfolio
# ---------------------------------------------------------------------------

class TestChipPortfolio:
    def test_returns_chip_info(self) -> None:
        server = ChipMCPServer()
        server._portfolio = _make_portfolio()
        server._last_load = 9999999999
        result = server._handle_chip_portfolio({})
        assert result["chip_count"] == 2
        assert result["average_score"] > 0
        assert "verdicts" in result
        assert len(result["chips"]) == 2

    def test_empty_portfolio(self) -> None:
        server = ChipMCPServer()
        server._portfolio = []
        # Prevent _ensure_portfolio from reloading real chips
        with patch.object(server, "_ensure_portfolio"):
            result = server._handle_chip_portfolio({})
        assert result["chip_count"] == 0
        assert result["average_score"] == 0

    def test_sorted_by_quality(self) -> None:
        server = ChipMCPServer()
        server._portfolio = _make_portfolio()
        server._last_load = 9999999999
        result = server._handle_chip_portfolio({})
        scores = [c["quality_score"] for c in result["chips"]]
        assert scores == sorted(scores, reverse=True)


# ---------------------------------------------------------------------------
# TestFindChip
# ---------------------------------------------------------------------------

class TestFindChip:
    def test_exact_match(self) -> None:
        server = ChipMCPServer()
        server._portfolio = _make_portfolio()
        server._last_load = 9999999999
        chip = server._find_chip("test-chip")
        assert chip is not None
        assert chip.chip_name == "test-chip"

    def test_not_found(self) -> None:
        server = ChipMCPServer()
        server._portfolio = _make_portfolio()
        server._last_load = 9999999999
        chip = server._find_chip("nonexistent-chip")
        assert chip is None


# ---------------------------------------------------------------------------
# TestChipDoctrines
# ---------------------------------------------------------------------------

class TestChipDoctrines:
    def test_returns_doctrines(self) -> None:
        server = ChipMCPServer()
        server._portfolio = _make_portfolio()
        server._last_load = 9999999999

        with patch("chip_labs.intelligence_server.extract_intelligence") as mock_extract:
            mock_extract.return_value = _make_intel(doctrines=[
                {"claim": "Doctrine A", "confidence": "high"},
                {"claim": "Doctrine B", "confidence": "medium"},
            ])
            result = server._handle_chip_doctrines({"chip_name": "test-chip"})
            assert result["chip_name"] == "test-chip"
            assert result["doctrine_count"] == 2
            assert len(result["doctrines"]) == 2

    def test_chip_not_found(self) -> None:
        server = ChipMCPServer()
        server._portfolio = _make_portfolio()
        server._last_load = 9999999999
        result = server._handle_chip_doctrines({"chip_name": "ghost-chip"})
        assert "error" in result

    def test_max_count_limits(self) -> None:
        server = ChipMCPServer()
        server._portfolio = _make_portfolio()
        server._last_load = 9999999999

        docs = [{"claim": f"D{i}", "confidence": "medium"} for i in range(20)]
        with patch("chip_labs.intelligence_server.extract_intelligence") as mock_extract:
            mock_extract.return_value = _make_intel(doctrines=docs)
            result = server._handle_chip_doctrines({"chip_name": "test-chip", "max_count": 5})
            assert len(result["doctrines"]) == 5


# ---------------------------------------------------------------------------
# TestChipFeedback
# ---------------------------------------------------------------------------

class TestChipFeedback:
    def test_writes_feedback_packet(self, tmp_path: Path) -> None:
        portfolio = [MockChipHandle(
            chip_path=tmp_path / "domain-chip-test",
            chip_name="test-chip",
            intelligence=_make_intel(),
        )]
        (tmp_path / "domain-chip-test").mkdir()

        server = ChipMCPServer()
        server._portfolio = portfolio
        server._last_load = 9999999999

        result = server._handle_chip_feedback({
            "chip_name": "test-chip",
            "action_description": "Ran npm test",
            "outcome": "All tests passed",
            "doctrine_confirmed": ["Test claim"],
            "doctrine_contradicted": [],
        })
        assert result["success"] is True
        assert result["doctrine_confirmed_count"] == 1

        rw_dir = tmp_path / "domain-chip-test" / "research" / "realworld_validated"
        assert rw_dir.exists()
        files = list(rw_dir.glob("feedback_*.json"))
        assert len(files) == 1

        data = json.loads(files[0].read_text())
        assert data["packet_kind"] == "realworld_feedback"
        assert data["outcome"] == "All tests passed"
        assert data["doctrine_confirmed"] == ["Test claim"]

    def test_chip_not_found(self) -> None:
        server = ChipMCPServer()
        server._portfolio = _make_portfolio()
        server._last_load = 9999999999
        result = server._handle_chip_feedback({
            "chip_name": "ghost-chip",
            "action_description": "test",
            "outcome": "test",
        })
        assert "error" in result


# ---------------------------------------------------------------------------
# TestChipSuggest
# ---------------------------------------------------------------------------

class TestChipSuggest:
    def test_suggests_for_gaps(self) -> None:
        server = ChipMCPServer()
        server._portfolio = _make_portfolio()
        server._last_load = 9999999999

        with patch("chip_labs.intelligence_server.extract_intelligence") as mock_extract:
            mock_extract.return_value = _make_intel()
            result = server._handle_chip_suggest({"chip_name": "test-chip"})
            assert "suggestions" in result
            assert len(result["suggestions"]) == 1
            sug = result["suggestions"][0]["suggestions"]
            assert any("real-world" in s.lower() or "Collect" in s for s in sug)

    def test_all_chips_without_name(self) -> None:
        server = ChipMCPServer()
        server._portfolio = _make_portfolio()
        server._last_load = 9999999999

        with patch("chip_labs.intelligence_server.extract_intelligence") as mock_extract:
            mock_extract.return_value = _make_intel()
            result = server._handle_chip_suggest({})
            assert len(result["suggestions"]) == 2


# ---------------------------------------------------------------------------
# TestChipQuery
# ---------------------------------------------------------------------------

class TestChipQuery:
    def test_queries_portfolio(self) -> None:
        server = ChipMCPServer()
        server._portfolio = _make_portfolio()
        server._last_load = 9999999999

        with patch("chip_labs.intelligence_server.extract_intelligence") as mock_extract:
            mock_extract.return_value = _make_intel()
            result = server._handle_chip_query({"query": "test something"})
            assert "results" in result
            assert result["chips_consulted"] > 0

    def test_filters_by_confidence(self) -> None:
        server = ChipMCPServer()
        server._portfolio = _make_portfolio()
        server._last_load = 9999999999

        with patch("chip_labs.intelligence_server.extract_intelligence") as mock_extract:
            mock_extract.return_value = _make_intel(doctrines=[
                {"claim": "High claim", "confidence": "high"},
                {"claim": "Low claim", "confidence": "low"},
            ])
            result = server._handle_chip_query({"query": "test", "min_confidence": "high"})
            for r in result["results"]:
                for d in r["doctrines"]:
                    assert d["confidence"] in ("high", "very high")
