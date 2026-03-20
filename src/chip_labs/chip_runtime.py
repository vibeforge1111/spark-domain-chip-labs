"""Chip runtime -- load, execute hooks, and gate domain chips.

Provides a high-level runtime layer over the chip registry, deep evaluation,
and intelligence server.  A ChipHandle bundles manifest data with quality
scores and lazy-loaded intelligence; execute_hook() runs hook commands or
falls back to intelligence-server context serving.

Zero external dependencies (stdlib + chip_labs siblings only).
"""

from __future__ import annotations

import json
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from chip_labs.deep_eval import score_chip_v3
from chip_labs.intelligence_server import (
    ChipIntelligence,
    extract_intelligence,
    serve_context,
)
from chip_labs.registry import discover_chips


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class ChipHandle:
    """Runtime handle wrapping a domain chip with its evaluation state."""

    chip_path: Path
    chip_name: str
    domain: str
    version: str
    capabilities: list[str] = field(default_factory=list)
    commands: dict[str, list[str]] = field(default_factory=dict)
    frontier: dict[str, Any] = field(default_factory=dict)
    quality_score: float = 0.0
    quality_verdict: str = "scaffold"
    _intelligence: ChipIntelligence | None = field(
        default=None, repr=False, compare=False
    )

    # -- lazy intelligence property ----------------------------------------

    @property
    def intelligence(self) -> ChipIntelligence | None:
        """Return cached intelligence, loading lazily on first access."""
        if self._intelligence is None:
            self._intelligence = _ensure_intelligence(self)
        return self._intelligence


@dataclass
class HookResult:
    """Outcome of executing a single hook against a chip."""

    hook_name: str
    chip_name: str
    success: bool
    result: dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    execution_mode: str = "unknown"
    duration_ms: int = 0


# ---------------------------------------------------------------------------
# Chip loading
# ---------------------------------------------------------------------------


def load_chip(chip_path: Path) -> ChipHandle:
    """Load a single chip from *chip_path*, score it, and return a handle.

    Reads spark-chip.json for manifest fields and runs the v3 deep-eval
    scorer to populate quality metrics.

    Raises FileNotFoundError if the manifest is missing.
    """
    chip_path = Path(chip_path)
    manifest_path = chip_path / "spark-chip.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"No spark-chip.json in {chip_path}")

    manifest: dict[str, Any] = json.loads(
        manifest_path.read_text(encoding="utf-8")
    )

    # Deep-eval scoring
    eval_result = score_chip_v3(chip_path)

    return ChipHandle(
        chip_path=chip_path,
        chip_name=manifest.get("name", chip_path.name),
        domain=manifest.get("domain", "unknown"),
        version=manifest.get("version", "0.0.0"),
        capabilities=manifest.get("capabilities", []),
        commands=manifest.get("commands", {}),
        frontier=manifest.get("frontier", {}),
        quality_score=eval_result.total_score,
        quality_verdict=eval_result.verdict,
    )


def load_portfolio(
    search_dir: Path | None = None,
    min_score: float = 0,
) -> list[ChipHandle]:
    """Discover all chips under *search_dir* and return scored handles.

    Chips whose quality score falls below *min_score* are excluded.
    """
    descriptors = discover_chips(search_dir)
    handles: list[ChipHandle] = []
    for desc in descriptors:
        chip_dir = Path(desc["path"])
        try:
            handle = load_chip(chip_dir)
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            continue
        if handle.quality_score >= min_score:
            handles.append(handle)
    return handles


# ---------------------------------------------------------------------------
# Hook execution
# ---------------------------------------------------------------------------


def execute_hook(
    chip: ChipHandle,
    hook_name: str,
    mutations: dict[str, Any] | None = None,
) -> HookResult:
    """Execute *hook_name* on *chip*.

    **Mode 1 -- subprocess**: If chip.commands contains *hook_name*, the
    command is run as a subprocess with optional *mutations* piped as JSON on
    stdin.  stdout is parsed as JSON for the result dict.

    **Mode 2 -- intelligence fallback**: When no explicit command exists, the
    intelligence server serve_context is called instead, using
    *hook_name* as the query string.

    Returns a HookResult with timing and confidence metadata.
    """
    start_ns = time.perf_counter_ns()

    if hook_name in chip.commands:
        result = _execute_subprocess(chip, hook_name, mutations)
    else:
        result = _execute_intelligence_fallback(chip, hook_name, mutations)

    elapsed_ms = (time.perf_counter_ns() - start_ns) // 1_000_000
    result.duration_ms = elapsed_ms
    return result


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _execute_subprocess(
    chip: ChipHandle,
    hook_name: str,
    mutations: dict[str, Any] | None,
) -> HookResult:
    """Run the hook as a subprocess and capture JSON output."""
    cmd = chip.commands[hook_name]
    stdin_payload = json.dumps(mutations or {})

    try:
        proc = subprocess.run(
            cmd,
            input=stdin_payload,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(chip.chip_path),
        )
        if proc.returncode == 0:
            try:
                output = json.loads(proc.stdout)
            except json.JSONDecodeError:
                output = {"raw_stdout": proc.stdout}
            return HookResult(
                hook_name=hook_name,
                chip_name=chip.chip_name,
                success=True,
                result=output,
                confidence=chip.quality_score / 100.0,
                execution_mode="subprocess",
            )
        else:
            return HookResult(
                hook_name=hook_name,
                chip_name=chip.chip_name,
                success=False,
                result={"stderr": proc.stderr, "returncode": proc.returncode},
                confidence=0.0,
                execution_mode="subprocess",
            )
    except (subprocess.TimeoutExpired, OSError) as exc:
        return HookResult(
            hook_name=hook_name,
            chip_name=chip.chip_name,
            success=False,
            result={"error": str(exc)},
            confidence=0.0,
            execution_mode="subprocess",
        )


def _execute_intelligence_fallback(
    chip: ChipHandle,
    hook_name: str,
    mutations: dict[str, Any] | None,
) -> HookResult:
    """Fall back to intelligence_server.serve_context for the hook."""
    try:
        ctx = serve_context(chip.chip_path, hook_name)
        return HookResult(
            hook_name=hook_name,
            chip_name=chip.chip_name,
            success=True,
            result=ctx,
            confidence=chip.quality_score / 100.0,
            execution_mode="intelligence_fallback",
        )
    except Exception as exc:  # noqa: BLE001
        return HookResult(
            hook_name=hook_name,
            chip_name=chip.chip_name,
            success=False,
            result={"error": str(exc)},
            confidence=0.0,
            execution_mode="intelligence_fallback",
        )


def score_gate(chip: ChipHandle, min_score: float = 35) -> bool:
    """Return True if the chip quality score meets *min_score*."""
    return chip.quality_score >= min_score


def _ensure_intelligence(chip: ChipHandle) -> ChipIntelligence:
    """Lazily load and cache intelligence for *chip*."""
    return extract_intelligence(chip.chip_path)
