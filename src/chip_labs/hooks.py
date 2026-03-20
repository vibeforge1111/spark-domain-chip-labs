"""Claude Code hook handlers for domain chip intelligence delivery.

Implements hook handlers for SessionStart, PreToolUse, and PostToolUse
that inject domain chip intelligence into Claude Code agent workflows.

Usage:
    python -m chip_labs.hooks session_start   # inject doctrines at session start
    python -m chip_labs.hooks pre_tool_use    # check action against doctrines
    python -m chip_labs.hooks post_tool_use   # capture feedback from tool results

Each handler reads JSON from stdin (Claude Code hook protocol) and writes
JSON to stdout with hookSpecificOutput for context injection.

Zero external dependencies (stdlib + chip_labs siblings only).
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Minimum V3 quality score for a chip to be served
MIN_QUALITY_SCORE = 35

# Maximum chips to include in context injection
MAX_CHIPS_SESSION = 3
MAX_CHIPS_PRETOOL = 2

# Maximum doctrines to inject per chip
MAX_DOCTRINES_PER_CHIP = 5

# Environment variable to set domain hint
DOMAIN_HINT_ENV = "CHIP_DOMAIN_HINT"

# Environment variable to disable hooks
DISABLE_ENV = "CHIP_HOOKS_DISABLED"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _read_stdin() -> dict[str, Any]:
    """Read JSON from stdin (Claude Code hook protocol)."""
    try:
        raw = sys.stdin.read()
        if raw.strip():
            return json.loads(raw)
    except (json.JSONDecodeError, OSError):
        pass
    return {}


def _write_stdout(data: dict[str, Any]) -> None:
    """Write JSON to stdout."""
    sys.stdout.write(json.dumps(data))
    sys.stdout.flush()


def _load_portfolio_safe() -> list[Any]:
    """Load chip portfolio with graceful fallback."""
    try:
        from .chip_runtime import load_portfolio
        return load_portfolio(min_score=MIN_QUALITY_SCORE)
    except (ImportError, Exception):
        return []


def _build_context_text(portfolio: list[Any], query: str = "", max_chips: int = 2) -> str:
    """Build context text from portfolio for injection."""
    try:
        from .chip_context_injector import inject_context_for_task
        return inject_context_for_task(
            query,
            portfolio=portfolio,
            max_chips=max_chips,
            style="concise",
        )
    except (ImportError, Exception):
        return ""


def _build_guardrails(portfolio: list[Any]) -> str:
    """Build guardrails block from portfolio."""
    try:
        from .chip_context_injector import build_guardrails_block
        return build_guardrails_block(portfolio)
    except (ImportError, Exception):
        return ""


def _write_feedback_packet(
    chip_path: Path,
    action: str,
    tool_name: str,
    result_summary: str,
) -> Path | None:
    """Write a feedback packet to chip's realworld_validated directory."""
    rw_dir = chip_path / "research" / "realworld_validated"
    try:
        rw_dir.mkdir(parents=True, exist_ok=True)
    except OSError:
        return None

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    packet = {
        "packet_kind": "realworld_feedback",
        "evidence_lane": "realworld_validated",
        "action": action,
        "tool_name": tool_name,
        "result_summary": result_summary[:500],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "claude_code_hook",
    }

    filename = f"feedback_{timestamp}_{tool_name}.json"
    filepath = rw_dir / filename
    try:
        filepath.write_text(json.dumps(packet, indent=2), encoding="utf-8")
        return filepath
    except OSError:
        return None


# ---------------------------------------------------------------------------
# Hook handlers
# ---------------------------------------------------------------------------

def handle_session_start(input_data: dict[str, Any]) -> dict[str, Any]:
    """SessionStart hook: inject chip doctrines as additionalContext.

    Loads the chip portfolio, selects relevant chips based on CWD or
    domain hint, and injects concise doctrine context.
    """
    if os.environ.get(DISABLE_ENV, "").lower() in ("1", "true", "yes"):
        return {}

    portfolio = _load_portfolio_safe()
    if not portfolio:
        return {}

    # Use CWD or domain hint for chip selection
    cwd = input_data.get("cwd", "")
    domain_hint = os.environ.get(DOMAIN_HINT_ENV, "")
    query = domain_hint or Path(cwd).name if cwd else ""

    context = _build_context_text(portfolio, query, max_chips=MAX_CHIPS_SESSION)
    if not context or context.startswith("<!--"):
        return {}

    guardrails = _build_guardrails(portfolio)

    full_context = context
    if guardrails and "No high-confidence" not in guardrails:
        full_context += "\n\n" + guardrails

    return {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": full_context,
        }
    }


def handle_pre_tool_use(input_data: dict[str, Any]) -> dict[str, Any]:
    """PreToolUse hook: check planned action against chip doctrines.

    Provides advisory context without blocking. Uses additionalContext
    to give Claude awareness of relevant doctrines before tool execution.
    """
    if os.environ.get(DISABLE_ENV, "").lower() in ("1", "true", "yes"):
        return {}

    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})

    # Build action description from tool input
    if tool_name == "Bash":
        action = f"Running command: {tool_input.get('command', '')[:200]}"
    elif tool_name in ("Edit", "Write"):
        action = f"Modifying file: {tool_input.get('file_path', '')}"
    else:
        action = f"Using tool: {tool_name}"

    portfolio = _load_portfolio_safe()
    if not portfolio:
        return {}

    context = _build_context_text(portfolio, action, max_chips=MAX_CHIPS_PRETOOL)
    if not context or context.startswith("<!--"):
        return {}

    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": f"[Domain chip advisory for {tool_name}]\n{context}",
        }
    }


def handle_post_tool_use(input_data: dict[str, Any]) -> dict[str, Any]:
    """PostToolUse hook: capture tool outcomes as feedback for chip flywheel.

    Writes a feedback packet to the most relevant chip's
    research/realworld_validated/ directory.
    """
    if os.environ.get(DISABLE_ENV, "").lower() in ("1", "true", "yes"):
        return {}

    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})
    tool_output = input_data.get("tool_output", "")

    # Only capture significant tool outcomes
    if tool_name not in ("Bash", "Edit", "Write"):
        return {}

    # Build action description
    if tool_name == "Bash":
        action = tool_input.get("command", "")[:300]
    elif tool_name in ("Edit", "Write"):
        action = f"Modified {tool_input.get('file_path', '')}"
    else:
        action = tool_name

    # Summarize result
    if isinstance(tool_output, str):
        result_summary = tool_output[:500]
    elif isinstance(tool_output, dict):
        result_summary = json.dumps(tool_output)[:500]
    else:
        result_summary = str(tool_output)[:500]

    # Write feedback to most relevant chip
    portfolio = _load_portfolio_safe()
    if not portfolio:
        return {}

    try:
        from .chip_context_injector import select_chips_for_task
        selected = select_chips_for_task(action, portfolio, max_chips=1)
    except (ImportError, Exception):
        selected = portfolio[:1]

    feedback_paths: list[str] = []
    for chip in selected:
        path = _write_feedback_packet(chip.chip_path, action, tool_name, result_summary)
        if path:
            feedback_paths.append(str(path))

    if feedback_paths:
        return {
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": f"[Feedback captured for chip intelligence: {len(feedback_paths)} packet(s)]",
            }
        }

    return {}


# ---------------------------------------------------------------------------
# CLI dispatcher
# ---------------------------------------------------------------------------

HANDLERS = {
    "session_start": handle_session_start,
    "pre_tool_use": handle_pre_tool_use,
    "post_tool_use": handle_post_tool_use,
}


def main() -> None:
    """CLI entry point: dispatch to the appropriate hook handler."""
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: python -m chip_labs.hooks <hook_name>"}), file=sys.stderr)
        sys.exit(1)

    hook_name = sys.argv[1]
    handler = HANDLERS.get(hook_name)

    if handler is None:
        print(json.dumps({"error": f"Unknown hook: {hook_name}. Available: {list(HANDLERS.keys())}"}), file=sys.stderr)
        sys.exit(1)

    input_data = _read_stdin()
    result = handler(input_data)

    if result:
        _write_stdout(result)


if __name__ == "__main__":
    main()
