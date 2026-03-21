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
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from chip_labs.deep_eval import score_chip_v3
from .intelligence_server import (
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
        chip_name=manifest.get("chip_name") or manifest.get("name", chip_path.name),
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
    if search_dir is None:
        descriptors = _include_current_workspace_chip(descriptors)
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


def _include_current_workspace_chip(
    descriptors: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Add the current chip workspace when running inside a chip repo.

    The portfolio registry primarily discovers Desktop chips by directory
    prefix. This repo does not follow that prefix, so serving/advisory flows
    launched from inside the current workspace would otherwise exclude the
    active chip entirely.
    """
    current_chip = _find_current_workspace_chip()
    if current_chip is None:
        return descriptors

    existing_paths = {
        str(Path(desc.get("path", "")).resolve())
        for desc in descriptors
        if desc.get("path")
    }
    current_path = str(current_chip.resolve())
    if current_path in existing_paths:
        return descriptors

    return [
        *descriptors,
        {
            "name": current_chip.name,
            "path": current_path,
        },
    ]


def _find_current_workspace_chip(start: Path | None = None) -> Path | None:
    """Walk upward from *start* (or CWD) until a chip manifest is found."""
    current = (start or Path.cwd()).resolve()
    for candidate in [current, *current.parents]:
        if (candidate / "spark-chip.json").exists():
            return candidate
    return None


def _execute_subprocess(
    chip: ChipHandle,
    hook_name: str,
    mutations: dict[str, Any] | None,
) -> HookResult:
    """Run the hook as a subprocess and capture JSON output."""
    cmd = chip.commands[hook_name]

    try:
        with tempfile.TemporaryDirectory(prefix="chip-hook-") as tmpdir:
            tmp_path = Path(tmpdir)
            input_path = tmp_path / f"{hook_name}_input.json"
            output_path = tmp_path / f"{hook_name}_output.json"
            input_path.write_text(
                json.dumps(mutations or {}, indent=2),
                encoding="utf-8",
            )

            resolved_cmd, use_stdin = _prepare_hook_command(
                cmd,
                hook_name,
                input_path,
                output_path,
            )

            proc = subprocess.run(
                resolved_cmd,
                input=json.dumps(mutations or {}) if use_stdin else None,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(chip.chip_path),
            )

        if proc.returncode == 0:
            output = _parse_hook_output(output_path, proc.stdout)
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


def _prepare_hook_command(
    cmd: list[str] | str,
    hook_name: str,
    input_path: Path,
    output_path: Path,
) -> tuple[list[str], bool]:
    """Prepare a hook command for execution.

    Preferred path is file-based I/O using ``--input`` / ``--output`` because
    the lab CLI and scaffolded chips are built around that contract. Commands
    that do not appear to support file I/O fall back to the previous stdin
    behavior.
    """
    if isinstance(cmd, str):
        normalized = [cmd]
    else:
        normalized = [str(part) for part in cmd]

    has_input_flag = any(part == "--input" or "{input}" in part for part in normalized)
    has_output_flag = any(part == "--output" or "{output}" in part for part in normalized)
    uses_placeholders = any(
        "{input}" in part or "{output}" in part
        for part in normalized
    )
    looks_like_cli_hook = (
        any(".cli" in part for part in normalized)
        or (normalized and normalized[-1] == hook_name)
    )

    resolved = [
        part.replace("{input}", str(input_path)).replace("{output}", str(output_path))
        for part in normalized
    ]

    if uses_placeholders or looks_like_cli_hook:
        if not has_input_flag:
            resolved.extend(["--input", str(input_path)])
        if not has_output_flag:
            resolved.extend(["--output", str(output_path)])
        return resolved, False

    return resolved, True


def _parse_hook_output(output_path: Path, stdout: str) -> dict[str, Any]:
    """Read hook output from file first, then fall back to stdout parsing."""
    if output_path.exists():
        try:
            return json.loads(output_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass

    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        return {"raw_stdout": stdout}


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
