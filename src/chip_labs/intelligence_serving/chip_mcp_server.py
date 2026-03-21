"""MCP server exposing domain chip intelligence as tools.

Implements a JSON-RPC 2.0 over stdio MCP server with 7 tools for querying,
advising, and feeding back intelligence to domain chips.  Replaces static
Spawner skills with dynamic, self-improving domain knowledge.

Usage:
    python -m chip_labs.chip_mcp_server

Zero external dependencies (stdlib + chip_labs siblings only).
"""

from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SERVER_NAME = "domain-chip-intelligence"
SERVER_VERSION = "1.0.0"
PROTOCOL_VERSION = "2024-11-05"

MIN_QUALITY_SCORE = 35
PORTFOLIO_TTL_SECONDS = 300  # 5 min cache


# ---------------------------------------------------------------------------
# Tool definitions
# ---------------------------------------------------------------------------

TOOLS = [
    {
        "name": "chip_query",
        "description": "Query domain chip intelligence. Returns evidence-weighted doctrines, contradictions, and trajectory context for a topic.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "What you want to know about"},
                "domain": {"type": "string", "description": "Filter to a specific domain (e.g., 'startup', 'trading')"},
                "min_confidence": {"type": "string", "enum": ["low", "medium", "high", "very high"], "description": "Minimum doctrine confidence"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "chip_advise",
        "description": "Get pre-action advisory from domain chips. Checks planned action against chip doctrines and returns guidance.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "description": "What you plan to do"},
                "domain": {"type": "string", "description": "Domain context"},
                "action_type": {"type": "string", "enum": ["tool_call", "code_generation", "decision", "general"]},
            },
            "required": ["action"],
        },
    },
    {
        "name": "chip_evaluate",
        "description": "Run evaluation against a domain chip's scoring model with given mutations.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "chip_name": {"type": "string", "description": "Which chip to evaluate against"},
                "mutations": {"type": "object", "description": "Mutation parameters for evaluation"},
            },
            "required": ["chip_name"],
        },
    },
    {
        "name": "chip_doctrines",
        "description": "List core doctrines from a domain chip, sorted by confidence.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "chip_name": {"type": "string", "description": "Which chip"},
                "max_count": {"type": "integer", "description": "Maximum doctrines to return", "default": 10},
            },
            "required": ["chip_name"],
        },
    },
    {
        "name": "chip_portfolio",
        "description": "Get portfolio overview of all available domain chips with quality scores and summaries.",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "chip_feedback",
        "description": "Feed action outcomes back into chip intelligence. Helps chips learn from real-world usage.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "chip_name": {"type": "string", "description": "Which chip received the advice"},
                "action_description": {"type": "string", "description": "What was done"},
                "outcome": {"type": "string", "description": "What happened"},
                "doctrine_confirmed": {"type": "array", "items": {"type": "string"}, "description": "Doctrines that proved correct"},
                "doctrine_contradicted": {"type": "array", "items": {"type": "string"}, "description": "Doctrines that proved wrong"},
            },
            "required": ["chip_name", "action_description", "outcome"],
        },
    },
    {
        "name": "chip_suggest",
        "description": "Get next research suggestions from a chip's frontier.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "chip_name": {"type": "string", "description": "Specific chip, or omit for all"},
                "focus": {"type": "string", "description": "Research focus area"},
            },
        },
    },
]


# ---------------------------------------------------------------------------
# Server state
# ---------------------------------------------------------------------------

class ChipMCPServer:
    """MCP server exposing domain chip intelligence as callable tools."""

    def __init__(self, search_dir: Path | None = None) -> None:
        self._search_dir = search_dir
        self._portfolio: list[Any] = []
        self._last_load: float = 0
        self._initialized = False

    # -- Portfolio management -----------------------------------------------

    def _ensure_portfolio(self) -> None:
        """Load/refresh portfolio with TTL caching."""
        now = time.time()
        if self._portfolio and (now - self._last_load) < PORTFOLIO_TTL_SECONDS:
            return

        try:
            from ..chip_runtime import load_portfolio
            kwargs: dict[str, Any] = {"min_score": MIN_QUALITY_SCORE}
            if self._search_dir:
                kwargs["search_dir"] = self._search_dir
            self._portfolio = load_portfolio(**kwargs)
        except (ImportError, Exception):
            self._portfolio = []
        self._last_load = now

    def _find_chip(self, chip_name: str) -> Any | None:
        """Find a chip by name in the portfolio."""
        self._ensure_portfolio()
        # Try exact match first
        for chip in self._portfolio:
            if chip.chip_name == chip_name:
                return chip
        # Try partial match (domain-chip- prefix stripped)
        clean = chip_name.replace("domain-chip-", "")
        for chip in self._portfolio:
            if chip.chip_name.replace("domain-chip-", "") == clean:
                return chip
        return None

    # -- Tool handlers ------------------------------------------------------

    def _handle_chip_query(self, args: dict[str, Any]) -> dict[str, Any]:
        """Query chip intelligence."""
        self._ensure_portfolio()
        query = args.get("query", "")
        domain_filter = args.get("domain")
        min_conf = args.get("min_confidence", "low")

        try:
            from .chip_context_injector import select_chips_for_task
            from .intelligence_server import extract_intelligence
        except ImportError:
            return {"error": "chip_labs modules not available"}

        portfolio = self._portfolio
        if domain_filter:
            portfolio = [c for c in portfolio if domain_filter.lower() in c.domain.lower()]

        selected = select_chips_for_task(query, portfolio, max_chips=3)
        results: list[dict[str, Any]] = []

        conf_priority = {"very high": 0, "high": 1, "medium": 2, "low": 3}
        min_level = conf_priority.get(min_conf, 3)

        for chip in selected:
            intel = extract_intelligence(chip.chip_path)
            filtered_docs = [
                d for d in intel.doctrines
                if conf_priority.get(str(d.get("confidence", "low")).lower(), 3) <= min_level
            ]
            results.append({
                "chip_name": intel.chip_name,
                "domain": intel.domain,
                "quality": f"{chip.quality_score:.0f}/100 ({chip.quality_verdict})",
                "doctrines": filtered_docs[:10],
                "contradictions": intel.contradictions[:5],
                "trajectory": intel.score_trajectory[-10:] if intel.score_trajectory else [],
            })

        return {"query": query, "results": results, "chips_consulted": len(selected)}

    def _handle_chip_advise(self, args: dict[str, Any]) -> dict[str, Any]:
        """Pre-action advisory."""
        self._ensure_portfolio()
        action = args.get("action", "")

        try:
            from .chip_advisor import AdvisoryRequest, advise_pre_action
        except ImportError:
            # Fallback to simpler query
            return self._handle_chip_query({"query": action})

        request = AdvisoryRequest(
            action_description=action,
            domain_hint=args.get("domain"),
            action_type=args.get("action_type", "general"),
        )

        response = advise_pre_action(request, portfolio=self._portfolio)
        return {
            "verdict": response.verdict,
            "guidance": [
                {
                    "claim": g.claim,
                    "confidence": g.confidence,
                    "guidance_type": g.guidance_type,
                    "relevance": round(g.relevance, 3),
                    "source_chip": g.source_chip,
                }
                for g in response.guidance[:10]
            ],
            "contradictions": response.contradictions[:5],
            "uncertainty_areas": response.uncertainty_areas,
            "trajectory_context": response.trajectory_context,
            "chips_consulted": response.chips_consulted,
        }

    def _handle_chip_evaluate(self, args: dict[str, Any]) -> dict[str, Any]:
        """Run chip evaluation hook."""
        chip_name = args.get("chip_name", "")
        mutations = args.get("mutations", {})

        chip = self._find_chip(chip_name)
        if not chip:
            return {"error": f"Chip '{chip_name}' not found in portfolio"}

        try:
            from ..chip_runtime import execute_hook
            result = execute_hook(chip, "evaluate", mutations=mutations)
            return {
                "chip_name": result.chip_name,
                "success": result.success,
                "result": result.result,
                "confidence": round(result.confidence, 3),
                "execution_mode": result.execution_mode,
                "duration_ms": result.duration_ms,
            }
        except (ImportError, Exception) as exc:
            return {"error": str(exc)}

    def _handle_chip_doctrines(self, args: dict[str, Any]) -> dict[str, Any]:
        """List chip doctrines."""
        chip_name = args.get("chip_name", "")
        max_count = args.get("max_count", 10)

        chip = self._find_chip(chip_name)
        if not chip:
            return {"error": f"Chip '{chip_name}' not found"}

        try:
            from .intelligence_server import extract_intelligence
            intel = extract_intelligence(chip.chip_path)
            return {
                "chip_name": intel.chip_name,
                "domain": intel.domain,
                "doctrine_count": len(intel.doctrines),
                "doctrines": intel.doctrines[:max_count],
            }
        except (ImportError, Exception) as exc:
            return {"error": str(exc)}

    def _handle_chip_portfolio(self, args: dict[str, Any]) -> dict[str, Any]:
        """Portfolio overview."""
        self._ensure_portfolio()
        chips_info = []
        for chip in self._portfolio:
            chips_info.append({
                "chip_name": chip.chip_name,
                "domain": chip.domain,
                "version": chip.version,
                "quality_score": round(chip.quality_score, 1),
                "quality_verdict": chip.quality_verdict,
                "capabilities": chip.capabilities,
            })

        # Sort by quality score descending
        chips_info.sort(key=lambda c: c["quality_score"], reverse=True)

        avg_score = sum(c["quality_score"] for c in chips_info) / len(chips_info) if chips_info else 0
        verdicts: dict[str, int] = {}
        for c in chips_info:
            v = c["quality_verdict"]
            verdicts[v] = verdicts.get(v, 0) + 1

        return {
            "chip_count": len(chips_info),
            "average_score": round(avg_score, 1),
            "verdicts": verdicts,
            "chips": chips_info,
        }

    def _handle_chip_feedback(self, args: dict[str, Any]) -> dict[str, Any]:
        """Feed outcomes back into chip intelligence."""
        chip_name = args.get("chip_name", "")
        action_desc = args.get("action_description", "")
        outcome = args.get("outcome", "")
        confirmed = args.get("doctrine_confirmed", [])
        contradicted = args.get("doctrine_contradicted", [])

        chip = self._find_chip(chip_name)
        if not chip:
            return {"error": f"Chip '{chip_name}' not found"}

        # Write feedback packet to realworld_validated
        rw_dir = chip.chip_path / "research" / "realworld_validated"
        try:
            rw_dir.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            return {"error": f"Cannot create directory: {exc}"}

        timestamp = datetime.now(timezone.utc)
        packet = {
            "packet_kind": "realworld_feedback",
            "evidence_lane": "realworld_validated",
            "action": action_desc,
            "outcome": outcome,
            "doctrine_confirmed": confirmed,
            "doctrine_contradicted": contradicted,
            "timestamp": timestamp.isoformat(),
            "source": "mcp_chip_feedback",
        }

        filename = f"feedback_{timestamp.strftime('%Y%m%dT%H%M%SZ')}.json"
        filepath = rw_dir / filename

        try:
            filepath.write_text(json.dumps(packet, indent=2), encoding="utf-8")
        except OSError as exc:
            return {"error": f"Cannot write feedback: {exc}"}

        return {
            "success": True,
            "chip_name": chip.chip_name,
            "feedback_path": str(filepath),
            "doctrine_confirmed_count": len(confirmed),
            "doctrine_contradicted_count": len(contradicted),
        }

    def _handle_chip_suggest(self, args: dict[str, Any]) -> dict[str, Any]:
        """Get research suggestions."""
        chip_name = args.get("chip_name")
        focus = args.get("focus", "")

        if chip_name:
            chip = self._find_chip(chip_name)
            if not chip:
                return {"error": f"Chip '{chip_name}' not found"}
            chips = [chip]
        else:
            self._ensure_portfolio()
            chips = self._portfolio

        suggestions: list[dict[str, Any]] = []
        for chip in chips[:5]:
            try:
                from .intelligence_server import extract_intelligence
                intel = extract_intelligence(chip.chip_path)
                # Build suggestions from gaps in evidence
                chip_suggestions: list[str] = []
                if intel.evidence_summary.get("realworld_validated", 0) == 0:
                    chip_suggestions.append("Collect real-world validation data")
                if intel.evidence_summary.get("benchmark_grounded", 0) <= 1:
                    chip_suggestions.append("Add benchmark comparisons")
                if not intel.contradictions:
                    chip_suggestions.append("Document contradictions from evaluation runs")
                if len(intel.doctrines) < 3:
                    chip_suggestions.append("Develop more domain doctrines with causal reasoning")

                suggestions.append({
                    "chip_name": intel.chip_name,
                    "domain": intel.domain,
                    "suggestions": chip_suggestions,
                    "focus": focus,
                })
            except Exception:
                pass

        return {"suggestions": suggestions}

    # -- MCP protocol -------------------------------------------------------

    def _dispatch_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Dispatch a tool call to the appropriate handler."""
        handlers = {
            "chip_query": self._handle_chip_query,
            "chip_advise": self._handle_chip_advise,
            "chip_evaluate": self._handle_chip_evaluate,
            "chip_doctrines": self._handle_chip_doctrines,
            "chip_portfolio": self._handle_chip_portfolio,
            "chip_feedback": self._handle_chip_feedback,
            "chip_suggest": self._handle_chip_suggest,
        }
        handler = handlers.get(name)
        if not handler:
            return {"error": f"Unknown tool: {name}"}
        return handler(arguments)

    def _handle_request(self, request: dict[str, Any]) -> dict[str, Any]:
        """Handle a single JSON-RPC request."""
        method = request.get("method", "")
        req_id = request.get("id")
        params = request.get("params", {})

        if method == "initialize":
            self._initialized = True
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": PROTOCOL_VERSION,
                    "capabilities": {"tools": {"listChanged": False}},
                    "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
                },
            }

        if method == "notifications/initialized":
            return {}  # No response needed for notifications

        if method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"tools": TOOLS},
            }

        if method == "tools/call":
            tool_name = params.get("name", "")
            tool_args = params.get("arguments", {})
            try:
                result = self._dispatch_tool(tool_name, tool_args)
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [
                            {"type": "text", "text": json.dumps(result, indent=2, default=str)},
                        ],
                        "isError": "error" in result,
                    },
                }
            except Exception as exc:
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [{"type": "text", "text": json.dumps({"error": str(exc)})}],
                        "isError": True,
                    },
                }

        # Unknown method
        if req_id is not None:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"},
            }
        return {}

    def run(self) -> None:
        """Main stdio loop implementing MCP protocol."""
        # MCP uses newline-delimited JSON over stdio
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue

            try:
                request = json.loads(line)
            except json.JSONDecodeError:
                continue

            response = self._handle_request(request)
            if response:
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Start the MCP server."""
    server = ChipMCPServer()
    server.run()


if __name__ == "__main__":
    main()
