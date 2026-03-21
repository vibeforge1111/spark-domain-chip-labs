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
# Layer 1: Command pre-filter (sub-millisecond, no I/O)
# ---------------------------------------------------------------------------

# Commands that are never domain-relevant.  Matched against the first
# token of tool_input["command"] (case-insensitive, after path/extension stripping).
_SKIP_COMMANDS = frozenset({
    # Version control
    "git", "gh", "svn",
    # Package managers
    "npm", "npx", "yarn", "pnpm", "bun", "pip", "pip3", "pipx",
    "poetry", "uv", "cargo", "go", "gem", "composer", "nuget",
    "apt", "apt-get", "brew", "choco", "winget", "scoop",
    # Navigation / filesystem inspection
    "ls", "dir", "cd", "pwd", "tree", "find", "which", "where",
    "wc", "du", "df", "stat", "file", "type",
    # Text inspection (read-only)
    "cat", "head", "tail", "less", "more", "grep", "rg", "ag",
    "sed", "awk", "sort", "uniq", "diff", "comm",
    # Process / system
    "ps", "top", "htop", "kill", "tasklist", "taskkill",
    "echo", "printf", "env", "set", "export", "printenv",
    "whoami", "hostname", "uname", "systemctl", "journalctl",
    # Network inspection
    "curl", "wget", "ping", "ssh", "scp", "rsync",
    "netstat", "nslookup", "dig", "tracert", "traceroute",
    # Container / infra
    "docker", "docker-compose", "kubectl", "terraform", "ansible",
    # Build / lint / test runners
    "make", "cmake", "tsc", "eslint", "prettier", "black",
    "ruff", "mypy", "pytest", "jest", "vitest",
    # Shells
    "bash", "sh", "zsh", "powershell", "cmd",
})

# File extensions that are never domain-relevant when edited/written.
_SKIP_EXTENSIONS = frozenset({
    ".lock", ".sum", ".log", ".pid", ".tmp", ".bak",
    ".gitignore", ".gitattributes", ".editorconfig",
    ".prettierrc", ".eslintrc", ".stylelintrc",
})

# Well-known config/lock files by basename.
_SKIP_BASENAMES = frozenset({
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
    ".gitignore", ".dockerignore", "dockerfile",
    "makefile", "tsconfig.json", "pyproject.toml",
    "setup.py", "setup.cfg",
})


def _should_skip_action(tool_name: str, tool_input: dict[str, Any]) -> bool:
    """Fast pre-filter: return True if this action is never domain-relevant.

    Executes in <1ms.  No file I/O, no imports.  Pure string matching.
    """
    if tool_name == "Bash":
        command = tool_input.get("command", "").strip()
        if not command:
            return True
        # Extract first token (the executable)
        first_token = command.split()[0]
        # Handle path prefixes:  /usr/bin/git -> git,  C:\...\git.exe -> git
        base = first_token.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]
        # Strip .exe / .cmd / .bat / .ps1 suffixes (Windows)
        for suffix in (".exe", ".cmd", ".bat", ".ps1"):
            if base.lower().endswith(suffix):
                base = base[: -len(suffix)]
                break
        if base.lower() in _SKIP_COMMANDS:
            return True

    elif tool_name in ("Edit", "Write"):
        file_path = tool_input.get("file_path", "")
        if file_path:
            lower_path = file_path.lower()
            for ext in _SKIP_EXTENSIONS:
                if lower_path.endswith(ext):
                    return True
            basename = file_path.rsplit("/", 1)[-1].rsplit("\\", 1)[-1].lower()
            if basename in _SKIP_BASENAMES:
                return True

    return False


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


# Portfolio cache TTL in seconds (avoids re-running V3 deep eval on every hook call)
_PORTFOLIO_CACHE_TTL = 600  # 10 minutes
_PORTFOLIO_CACHE_DIR = Path.home() / ".cache" / "chip-labs"

# Layer 3: Session domain file -- written by SessionStart, read by Pre/PostToolUse
_SESSION_DOMAIN_FILE = _PORTFOLIO_CACHE_DIR / "session_domain.json"
_SESSION_DOMAIN_TTL = 3600  # 1 hour (typical session length)


def _write_session_domain(selected_chips: list[Any], query: str) -> None:
    """Persist session domain context for Pre/PostToolUse hooks."""
    try:
        _PORTFOLIO_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        data = {
            "query": query,
            "chip_names": [c.chip_name for c in selected_chips],
            "domains": list({c.domain for c in selected_chips}),
            "ts": datetime.now(timezone.utc).isoformat(),
        }
        _SESSION_DOMAIN_FILE.write_text(
            json.dumps(data, indent=2), encoding="utf-8",
        )
    except OSError:
        pass


def _read_session_domain() -> dict[str, Any] | None:
    """Read session domain context.  Returns None if stale or missing."""
    try:
        if not _SESSION_DOMAIN_FILE.exists():
            return None
        age = datetime.now(timezone.utc).timestamp() - _SESSION_DOMAIN_FILE.stat().st_mtime
        if age > _SESSION_DOMAIN_TTL:
            return None
        return json.loads(_SESSION_DOMAIN_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _load_portfolio_safe() -> list[Any]:
    """Load chip portfolio with file-based caching.

    V3 deep eval is expensive (~3s per chip).  We cache serialized portfolio
    metadata to a JSON file and reconstruct lightweight handles from it.
    The cache refreshes every ``_PORTFOLIO_CACHE_TTL`` seconds.
    """
    cache_file = _PORTFOLIO_CACHE_DIR / "portfolio_cache.json"

    # Try loading from cache first
    try:
        if cache_file.exists():
            age = datetime.now(timezone.utc).timestamp() - cache_file.stat().st_mtime
            if age < _PORTFOLIO_CACHE_TTL:
                return _load_from_cache(cache_file)
    except (OSError, Exception):
        pass

    # Full load (expensive -- runs V3 deep eval)
    try:
        from .chip_runtime import load_portfolio
        portfolio = load_portfolio(min_score=MIN_QUALITY_SCORE)
    except (ImportError, Exception):
        return []

    # Write cache for next hook call
    _write_cache(cache_file, portfolio)
    return portfolio


def _write_cache(cache_file: Path, portfolio: list[Any]) -> None:
    """Serialize portfolio handles to a JSON cache file."""
    try:
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        entries = []
        for chip in portfolio:
            intel = None
            try:
                intel_obj = chip.intelligence
                if intel_obj:
                    intel = {
                        "chip_name": intel_obj.chip_name,
                        "domain": intel_obj.domain,
                        "version": intel_obj.version,
                        "mission": intel_obj.mission,
                        "doctrines": intel_obj.doctrines,
                        "contradictions": intel_obj.contradictions,
                        "evidence_summary": intel_obj.evidence_summary,
                        "score_trajectory": intel_obj.score_trajectory,
                        "current_score": getattr(intel_obj, "current_score", 0),
                        "verdict": getattr(intel_obj, "verdict", ""),
                    }
            except Exception:
                pass
            entries.append({
                "chip_path": str(chip.chip_path),
                "chip_name": chip.chip_name,
                "domain": chip.domain,
                "version": chip.version,
                "capabilities": chip.capabilities,
                "quality_score": chip.quality_score,
                "quality_verdict": chip.quality_verdict,
                "intelligence": intel,
            })
        cache_file.write_text(
            json.dumps({"portfolio": entries, "ts": datetime.now(timezone.utc).isoformat()},
                       indent=2, default=str),
            encoding="utf-8",
        )
    except (OSError, Exception):
        pass


def _load_from_cache(cache_file: Path) -> list[Any]:
    """Reconstruct lightweight chip handles from cached JSON."""
    from dataclasses import dataclass, field

    data = json.loads(cache_file.read_text(encoding="utf-8"))

    # Import ChipIntelligence for reconstruction
    try:
        from .intelligence_server import ChipIntelligence
    except ImportError:
        return []

    @dataclass
    class CachedChipHandle:
        chip_path: Path
        chip_name: str
        domain: str
        version: str
        capabilities: list[str] = field(default_factory=list)
        commands: dict[str, list[str]] = field(default_factory=dict)
        frontier: dict[str, Any] = field(default_factory=dict)
        quality_score: float = 0.0
        quality_verdict: str = "scaffold"
        intelligence: ChipIntelligence | None = None

    handles = []
    for entry in data.get("portfolio", []):
        intel = None
        intel_data = entry.get("intelligence")
        if intel_data:
            intel = ChipIntelligence(
                chip_name=intel_data.get("chip_name", ""),
                domain=intel_data.get("domain", ""),
                version=intel_data.get("version", ""),
                mission=intel_data.get("mission", ""),
                doctrines=intel_data.get("doctrines", []),
                contradictions=intel_data.get("contradictions", []),
                evidence_summary=intel_data.get("evidence_summary", {}),
                score_trajectory=intel_data.get("score_trajectory", []),
                current_score=intel_data.get("current_score", 0),
                verdict=intel_data.get("verdict", ""),
            )
        handles.append(CachedChipHandle(
            chip_path=Path(entry["chip_path"]),
            chip_name=entry["chip_name"],
            domain=entry["domain"],
            version=entry["version"],
            capabilities=entry.get("capabilities", []),
            quality_score=entry.get("quality_score", 0),
            quality_verdict=entry.get("quality_verdict", "scaffold"),
            intelligence=intel,
        ))
    return handles


def _select_session_chips(
    query: str, portfolio: list[Any], max_chips: int = MAX_CHIPS_SESSION,
) -> list[Any]:
    """Select chips for a session using both Jaccard and substring matching.

    Short domain hints like "startup" or "trading" fail Jaccard against large
    chip texts (1 word / 70 word union = 0.014 < 0.03 threshold).  So we also
    check if the query appears as a substring in the chip's name or domain.
    This is only used by SessionStart where the query is a deliberate domain signal.
    """
    if not portfolio or not query.strip():
        return portfolio[:max_chips] if portfolio else []

    query_lower = query.strip().lower()

    # First: try Jaccard (works for multi-word queries)
    try:
        from .chip_context_injector import select_chips_for_task
        jaccard_result = select_chips_for_task(query, portfolio, max_chips=max_chips)
        if jaccard_result:
            return jaccard_result
    except (ImportError, Exception):
        pass

    # Fallback: substring match on chip_name and domain
    matches = []
    for chip in portfolio:
        name_lower = chip.chip_name.lower()
        domain_lower = chip.domain.lower()
        if query_lower in name_lower or query_lower in domain_lower:
            matches.append(chip)

    return matches[:max_chips]


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

    # For SessionStart, select chips with domain-aware matching.
    # Short domain hints (e.g. "startup") fail Jaccard against large chip texts,
    # so we also do substring matching on chip_name and domain fields.
    try:
        from .chip_context_injector import select_chips_for_task
        selected = _select_session_chips(query, portfolio)
    except (ImportError, Exception):
        selected = portfolio[:MAX_CHIPS_SESSION]

    if not selected:
        # No chips match -- try broader context build as fallback
        context = _build_context_text(portfolio, query, max_chips=MAX_CHIPS_SESSION)
        if not context or context.startswith("<!--"):
            return {}
    else:
        # Build context from selected chips directly
        try:
            from .chip_context_injector import build_system_prompt_section
            context = build_system_prompt_section(selected, style="concise")
        except (ImportError, Exception):
            context = _build_context_text(portfolio, query, max_chips=MAX_CHIPS_SESSION)
        if not context or context.startswith("<!--"):
            return {}

    # Layer 3: Persist session domain for Pre/PostToolUse hooks
    if selected:
        _write_session_domain(selected, query)

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

    Three-layer gating:
      Layer 1: Fast pre-filter (skip git/npm/ls etc. in <1ms)
      Layer 2: Relevance threshold (via select_chips_for_task min_relevance)
      Layer 3: Session domain enrichment (from SessionStart context)
    """
    if os.environ.get(DISABLE_ENV, "").lower() in ("1", "true", "yes"):
        return {}

    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})

    # Layer 1: Fast pre-filter -- skip clearly irrelevant actions
    if _should_skip_action(tool_name, tool_input):
        return {}

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

    # Layer 3: If session domain is active, restrict to session chips and
    # preserve the session's domain hint when building advisory context.
    session = _read_session_domain()
    if session:
        session_chip_names = set(session.get("chip_names", []))
        if session_chip_names:
            narrowed = [c for c in portfolio if c.chip_name in session_chip_names]
            if narrowed:
                domain_prefix = " ".join(session.get("domains", []))
                query = f"{domain_prefix} {action}".strip() if domain_prefix else action
                context = _build_context_text(
                    narrowed,
                    query,
                    max_chips=min(MAX_CHIPS_PRETOOL, len(narrowed)),
                )
                if context and not context.startswith("<!--"):
                    return {
                        "hookSpecificOutput": {
                            "hookEventName": "PreToolUse",
                            "additionalContext": f"[Domain chip advisory for {tool_name}]\n{context}",
                        }
                    }

    # No session domain -- fall back to Jaccard-based selection with threshold
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

    Three-layer gating:
      Layer 1: Fast pre-filter (skip git/npm/ls etc.)
      Layer 2: Relevance threshold (via select_chips_for_task min_relevance)
      Layer 3: Session domain restriction (only write feedback to relevant chips)
    """
    if os.environ.get(DISABLE_ENV, "").lower() in ("1", "true", "yes"):
        return {}

    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})
    tool_output = input_data.get("tool_output", "")

    # Only capture significant tool outcomes
    if tool_name not in ("Bash", "Edit", "Write"):
        return {}

    # Layer 1: Fast pre-filter -- skip clearly irrelevant actions
    if _should_skip_action(tool_name, tool_input):
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

    # Layer 3: Restrict to session-relevant chips if session domain is known.
    # When the session domain narrows the portfolio, those chips are already
    # confirmed relevant -- use them directly (skip Jaccard threshold).
    session = _read_session_domain()
    session_restricted = False
    if session:
        session_chip_names = set(session.get("chip_names", []))
        if session_chip_names:
            narrowed = [c for c in portfolio if c.chip_name in session_chip_names]
            if narrowed:
                portfolio = narrowed
                session_restricted = True
            else:
                return {}  # No session chips in portfolio

    if session_restricted:
        # Session already established relevance -- pick best match without threshold
        selected = portfolio[:1]
    else:
        # No session context -- rely on Jaccard + threshold
        try:
            from .chip_context_injector import select_chips_for_task
            selected = select_chips_for_task(action, portfolio, max_chips=1)
        except (ImportError, Exception):
            selected = portfolio[:1]

    # Layer 2: If nothing passes the relevance threshold, skip feedback
    if not selected:
        return {}

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
