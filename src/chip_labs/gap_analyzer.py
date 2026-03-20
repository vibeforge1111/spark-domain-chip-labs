"""Gap analyzer -- converts rubric failures into prioritized, actionable fixes.

Takes the output of score_chip() and produces a prioritized list of GapFix
objects, each describing what failed, how many points it is worth, and an
auto-fix function that can repair the gap in place.

The improve_chip() orchestrator drives the score -> fix -> rescore cycle
until a target score is reached or max iterations are exhausted.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from .quality_rubric import score_chip, RUBRIC_DIMENSIONS


# ---------------------------------------------------------------------------
# GapFix dataclass
# ---------------------------------------------------------------------------

@dataclass
class GapFix:
    """A single actionable fix for a failed rubric check."""

    check_id: str
    dimension: str
    description: str
    points_recoverable: int
    auto_fixable: bool
    fix_fn: Callable[[Path], bool] | None = None
    fix_description: str = ""
    applied: bool = False
    succeeded: bool = False


# ---------------------------------------------------------------------------
# Lookup tables
# ---------------------------------------------------------------------------

def _build_check_to_dimension() -> dict[str, str]:
    """Map each check_id to its parent dimension name."""
    mapping: dict[str, str] = {}
    for dim in RUBRIC_DIMENSIONS:
        for check in dim["checks"]:
            mapping[check["id"]] = dim["name"]
    return mapping


def _build_check_to_points() -> dict[str, int]:
    """Map each check_id to its point value."""
    mapping: dict[str, int] = {}
    for dim in RUBRIC_DIMENSIONS:
        for check in dim["checks"]:
            mapping[check["id"]] = check["points"]
    return mapping


def _build_check_to_description() -> dict[str, str]:
    """Map each check_id to its human-readable description."""
    mapping: dict[str, str] = {}
    for dim in RUBRIC_DIMENSIONS:
        for check in dim["checks"]:
            mapping[check["id"]] = check["description"]
    return mapping


_CHECK_TO_DIM = _build_check_to_dimension()
_CHECK_TO_PTS = _build_check_to_points()
_CHECK_TO_DESC = _build_check_to_description()


# ---------------------------------------------------------------------------
# Safe file helpers (never delete existing content)
# ---------------------------------------------------------------------------

def _read_json(path: Path) -> dict[str, Any] | None:
    """Read a JSON file, returning None on any error."""
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _write_json(path: Path, data: dict[str, Any]) -> None:
    """Write a JSON file with consistent formatting."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _ensure_file(path: Path, content: str) -> None:
    """Create a file only if it does not already exist."""
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _ensure_key(data: dict, key: str, default: Any) -> bool:
    """Set a key in a dict only if it is missing. Returns True if changed."""
    if key not in data:
        data[key] = default
        return True
    return False


# ---------------------------------------------------------------------------
# Manifest fixes (schema_version, io_protocol, all_four_hooks,
#                  frontier_enabled, required_fields_set, field_patterns_set)
# ---------------------------------------------------------------------------

def _fix_schema_version(chip_path: Path) -> bool:
    """Ensure spark-chip.json has schema_version = spark-chip.v1."""
    manifest_path = chip_path / "spark-chip.json"
    manifest = _read_json(manifest_path)
    if manifest is None:
        manifest = {}
    if manifest.get("schema_version") == "spark-chip.v1":
        return True
    manifest["schema_version"] = "spark-chip.v1"
    _write_json(manifest_path, manifest)
    return True


def _fix_io_protocol(chip_path: Path) -> bool:
    """Ensure spark-chip.json has io_protocol = spark-hook-io.v1."""
    manifest_path = chip_path / "spark-chip.json"
    manifest = _read_json(manifest_path)
    if manifest is None:
        manifest = {}
    if manifest.get("io_protocol") == "spark-hook-io.v1":
        return True
    manifest["io_protocol"] = "spark-hook-io.v1"
    _write_json(manifest_path, manifest)
    return True


def _fix_all_four_hooks(chip_path: Path) -> bool:
    """Ensure capabilities includes all four hooks."""
    manifest_path = chip_path / "spark-chip.json"
    manifest = _read_json(manifest_path)
    if manifest is None:
        manifest = {}
    required_hooks = ["evaluate", "suggest", "packets", "watchtower"]
    existing = set(manifest.get("capabilities", []))
    missing = [h for h in required_hooks if h not in existing]
    if not missing:
        return True
    manifest["capabilities"] = list(existing | set(required_hooks))
    _write_json(manifest_path, manifest)
    return True


def _fix_frontier_enabled(chip_path: Path) -> bool:
    """Ensure frontier section with enabled=true and allowed_mutations."""
    manifest_path = chip_path / "spark-chip.json"
    manifest = _read_json(manifest_path)
    if manifest is None:
        manifest = {}
    frontier = manifest.get("frontier", {})
    changed = False
    if not frontier.get("enabled"):
        frontier["enabled"] = True
        changed = True
    if not frontier.get("allowed_mutations"):
        frontier["allowed_mutations"] = ["research_focus"]
        changed = True
    if changed:
        manifest["frontier"] = frontier
        _write_json(manifest_path, manifest)
    return True


def _fix_required_fields_set(chip_path: Path) -> bool:
    """Ensure frontier has required_fields (even if empty list)."""
    manifest_path = chip_path / "spark-chip.json"
    manifest = _read_json(manifest_path)
    if manifest is None:
        manifest = {}
    frontier = manifest.get("frontier", {})
    if "required_fields" in frontier:
        return True
    frontier["required_fields"] = []
    manifest["frontier"] = frontier
    _write_json(manifest_path, manifest)
    return True


def _fix_field_patterns_set(chip_path: Path) -> bool:
    """Ensure frontier has field_patterns defined."""
    manifest_path = chip_path / "spark-chip.json"
    manifest = _read_json(manifest_path)
    if manifest is None:
        manifest = {}
    frontier = manifest.get("frontier", {})
    if frontier.get("field_patterns"):
        return True
    # Provide a sensible default pattern for the most common mutation field
    mutations = frontier.get("allowed_mutations", ["research_focus"])
    patterns = {}
    for mut in mutations:
        patterns[mut] = "^[a-z_]+$"
    frontier["field_patterns"] = patterns
    manifest["frontier"] = frontier
    _write_json(manifest_path, manifest)
    return True


# ---------------------------------------------------------------------------
# Integration fixes (project_json_valid, chip_path_set, commands_defined,
#                     guardrails_set, self_edit_config)
# ---------------------------------------------------------------------------

def _fix_project_json_valid(chip_path: Path) -> bool:
    """Ensure spark-researcher.project.json exists with project_name."""
    project_path = chip_path / "spark-researcher.project.json"
    project = _read_json(project_path)
    if project is None:
        project = {}
    if project.get("project_name"):
        _write_json(project_path, project)
        return True
    project["project_name"] = chip_path.name
    _write_json(project_path, project)
    return True


def _fix_chip_path_set(chip_path: Path) -> bool:
    """Ensure chip section has path and manifest set."""
    project_path = chip_path / "spark-researcher.project.json"
    project = _read_json(project_path)
    if project is None:
        project = {}
    chip_cfg = project.get("chip", {})
    changed = False
    if not chip_cfg.get("path"):
        chip_cfg["path"] = "."
        changed = True
    if not chip_cfg.get("manifest"):
        chip_cfg["manifest"] = "spark-chip.json"
        changed = True
    if changed:
        project["chip"] = chip_cfg
        _write_json(project_path, project)
    return True


def _fix_commands_defined(chip_path: Path) -> bool:
    """Ensure commands section includes a chip-evaluate kind command."""
    project_path = chip_path / "spark-researcher.project.json"
    project = _read_json(project_path)
    if project is None:
        project = {}
    commands = project.get("commands", {})
    has_eval = any(c.get("kind") == "chip-evaluate" for c in commands.values())
    if has_eval:
        return True
    commands["evaluate"] = {"kind": "chip-evaluate"}
    project["commands"] = commands
    _write_json(project_path, project)
    return True


def _fix_guardrails_set(chip_path: Path) -> bool:
    """Ensure guardrails with max_loop_iterations and blocked_command_fragments."""
    project_path = chip_path / "spark-researcher.project.json"
    project = _read_json(project_path)
    if project is None:
        project = {}
    guardrails = project.get("guardrails", {})
    changed = False
    if not guardrails.get("max_loop_iterations"):
        guardrails["max_loop_iterations"] = 10
        changed = True
    if not guardrails.get("blocked_command_fragments"):
        guardrails["blocked_command_fragments"] = ["rm -rf", "format c:"]
        changed = True
    if changed:
        project["guardrails"] = guardrails
        _write_json(project_path, project)
    return True


def _fix_self_edit_config(chip_path: Path) -> bool:
    """Ensure self_edit section with mutable_targets."""
    project_path = chip_path / "spark-researcher.project.json"
    project = _read_json(project_path)
    if project is None:
        project = {}
    self_edit = project.get("self_edit", {})
    if self_edit.get("mutable_targets"):
        return True
    self_edit["mutable_targets"] = ["src/"]
    project["self_edit"] = self_edit
    _write_json(project_path, project)
    return True


# ---------------------------------------------------------------------------
# Documentation fixes (readme_exists, mission_docs, architecture_docs,
#                       docs_directory, pyproject_valid)
# ---------------------------------------------------------------------------

def _fix_readme_exists(chip_path: Path) -> bool:
    """Create README.md with mission stub if missing."""
    readme_path = chip_path / "README.md"
    chip_name = chip_path.name
    _ensure_file(
        readme_path,
        f"# {chip_name}\n\n"
        f"## Mission\n\n"
        f"Domain chip for {chip_name.replace('domain-chip-', '')} research.\n\n"
        f"## Quick Start\n\n"
        f"```bash\n"
        f"# Run evaluation\n"
        f"spark-researcher evaluate\n"
        f"```\n",
    )
    return True


def _fix_mission_docs(chip_path: Path) -> bool:
    """Ensure mission/intent documentation exists."""
    docs_dir = chip_path / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)

    # Check if any existing doc already covers mission
    for md in docs_dir.rglob("*.md"):
        try:
            content = md.read_text(encoding="utf-8", errors="ignore").lower()
            if "mission" in content or "intent" in content:
                return True
        except OSError:
            pass

    # Also check README
    readme = chip_path / "README.md"
    if readme.exists():
        try:
            text = readme.read_text(encoding="utf-8", errors="ignore").lower()
            if "mission" in text:
                return True
        except OSError:
            pass

    chip_name = chip_path.name
    domain = chip_name.replace("domain-chip-", "")
    _ensure_file(
        docs_dir / "mission.md",
        f"# Mission\n\n"
        f"This chip explores the **{domain}** domain, providing structured\n"
        f"evaluation, knowledge packets, and research suggestions.\n\n"
        f"## Intent\n\n"
        f"- Evaluate domain-specific artifacts against quality criteria\n"
        f"- Generate actionable research suggestions\n"
        f"- Produce knowledge packets for downstream consumers\n"
        f"- Maintain an Obsidian vault of domain intelligence\n",
    )
    return True


def _fix_architecture_docs(chip_path: Path) -> bool:
    """Ensure architecture or one-loop documentation exists."""
    docs_dir = chip_path / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)

    # Check if any existing doc covers architecture
    for md in docs_dir.rglob("*.md"):
        try:
            name_lower = md.name.lower()
            if "architecture" in name_lower or "one_loop" in name_lower or "flywheel" in name_lower:
                return True
        except OSError:
            pass

    chip_name = chip_path.name
    domain = chip_name.replace("domain-chip-", "")
    _ensure_file(
        docs_dir / "architecture.md",
        f"# Architecture\n\n"
        f"## One-Loop Spec\n\n"
        f"The {domain} chip follows the standard spark-chip.v1 four-hook loop:\n\n"
        f"1. **evaluate** -- Score domain artifacts against metrics\n"
        f"2. **suggest** -- Propose next research mutations\n"
        f"3. **packets** -- Emit knowledge packets for consumers\n"
        f"4. **watchtower** -- Generate Obsidian vault pages\n\n"
        f"## Evidence Lanes\n\n"
        f"- research_grounded: Literature and source-backed findings\n"
        f"- benchmark_grounded: Quantitative evaluation results\n"
        f"- exploratory_frontier: Speculative hypotheses under test\n"
        f"- realworld_validated: Field-tested and confirmed patterns\n",
    )
    return True


def _fix_docs_directory(chip_path: Path) -> bool:
    """Ensure docs/ directory exists with at least one .md file."""
    docs_dir = chip_path / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    if any(docs_dir.rglob("*.md")):
        return True
    # Create a minimal index
    _ensure_file(
        docs_dir / "index.md",
        "# Documentation\n\n"
        "This directory contains structured documentation for the chip.\n",
    )
    return True


def _fix_pyproject_valid(chip_path: Path) -> bool:
    """Create pyproject.toml if missing."""
    pyproject_path = chip_path / "pyproject.toml"
    chip_name = chip_path.name
    _ensure_file(
        pyproject_path,
        f'[project]\nname = "{chip_name}"\nversion = "0.1.0"\n'
        f'description = "Domain chip for {chip_name.replace("domain-chip-", "")}"\n'
        f"requires-python = \">=3.10\"\n",
    )
    return True


# ---------------------------------------------------------------------------
# Memory / Knowledge fixes (source_registry, obsidian_vault, memory_backend)
# ---------------------------------------------------------------------------

def _fix_source_registry(chip_path: Path) -> bool:
    """Ensure a source registry document exists in docs/."""
    docs_dir = chip_path / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)

    # Check if any existing doc qualifies
    for md in docs_dir.rglob("*.md"):
        try:
            content = md.read_text(encoding="utf-8", errors="ignore").lower()
            if "source" in content and ("registry" in content or "map" in content or "list" in content):
                return True
        except OSError:
            pass

    domain = chip_path.name.replace("domain-chip-", "")
    _ensure_file(
        docs_dir / "source_registry.md",
        f"# Source Registry\n\n"
        f"Primary source map for the **{domain}** domain.\n\n"
        f"## Source List\n\n"
        f"| Source | Type | URL | Notes |\n"
        f"|--------|------|-----|-------|\n"
        f"| (add sources here) | research | - | - |\n",
    )
    return True


def _fix_obsidian_vault(chip_path: Path) -> bool:
    """Ensure obsidian-vault/ exists with at least one .md file."""
    vault_dir = chip_path / "obsidian-vault"
    vault_dir.mkdir(parents=True, exist_ok=True)
    if any(vault_dir.rglob("*.md")):
        return True
    domain = chip_path.name.replace("domain-chip-", "")
    _ensure_file(
        vault_dir / "index.md",
        f"# {domain} Knowledge Vault\n\n"
        f"Watchtower-generated pages for the {domain} domain.\n\n"
        f"## Pages\n\n"
        f"- [[index]] -- This page\n",
    )
    return True


def _fix_memory_backend(chip_path: Path) -> bool:
    """Ensure memory.backend is set in spark-researcher.project.json."""
    project_path = chip_path / "spark-researcher.project.json"
    project = _read_json(project_path)
    if project is None:
        project = {}
    memory = project.get("memory", {})
    if memory.get("backend"):
        return True
    memory["backend"] = "local"
    project["memory"] = memory
    _write_json(project_path, project)
    return True


# ---------------------------------------------------------------------------
# Evaluation depth fixes (primary_metric, baseline_trial, scoring_logic)
# ---------------------------------------------------------------------------

def _fix_primary_metric(chip_path: Path) -> bool:
    """Ensure eval_metric is set in spark-researcher.project.json."""
    project_path = chip_path / "spark-researcher.project.json"
    project = _read_json(project_path)
    if project is None:
        project = {}
    if project.get("eval_metric"):
        return True
    project["eval_metric"] = "quality_score"
    _write_json(project_path, project)
    return True


def _fix_baseline_trial(chip_path: Path) -> bool:
    """Ensure candidate_trials includes a baseline with empty mutations."""
    project_path = chip_path / "spark-researcher.project.json"
    project = _read_json(project_path)
    if project is None:
        project = {}
    trials = project.get("candidate_trials", [])
    has_baseline = any(
        t.get("mutations", None) == {} or t.get("mutations") is None
        for t in trials
    )
    if has_baseline:
        return True
    trials.insert(0, {"name": "baseline", "mutations": {}})
    project["candidate_trials"] = trials
    _write_json(project_path, project)
    return True


def _fix_scoring_logic(chip_path: Path) -> bool:
    """Ensure src/ contains a Python file with scoring logic."""
    src_dir = chip_path / "src"
    src_dir.mkdir(parents=True, exist_ok=True)

    # Check if scoring logic already exists
    for py in src_dir.rglob("*.py"):
        try:
            content = py.read_text(encoding="utf-8", errors="ignore")
            if "score" in content.lower() and ("def " in content or "class " in content):
                return True
        except OSError:
            pass

    # Create a minimal evaluate.py with a score function
    _ensure_file(
        src_dir / "evaluate.py",
        '"""Evaluation scoring logic for the chip."""\n\n\n'
        "def score(mutations: dict) -> float:\n"
        '    """Score a trial based on provided mutations.\n\n'
        "    Returns a float between 0.0 and 1.0.\n"
        '    """\n'
        "    # TODO: implement domain-specific scoring\n"
        "    return 0.5\n",
    )
    return True


# ---------------------------------------------------------------------------
# Fix registry -- maps check_id to (fix_fn, fix_description)
# ---------------------------------------------------------------------------

_FIX_REGISTRY: dict[str, tuple[Callable[[Path], bool], str]] = {
    # Manifest
    "schema_version": (
        _fix_schema_version,
        "Set schema_version to spark-chip.v1 in spark-chip.json",
    ),
    "io_protocol": (
        _fix_io_protocol,
        "Set io_protocol to spark-hook-io.v1 in spark-chip.json",
    ),
    "all_four_hooks": (
        _fix_all_four_hooks,
        "Add missing hooks to capabilities in spark-chip.json",
    ),
    "frontier_enabled": (
        _fix_frontier_enabled,
        "Enable frontier with allowed_mutations in spark-chip.json",
    ),
    "required_fields_set": (
        _fix_required_fields_set,
        "Add required_fields to frontier section in spark-chip.json",
    ),
    "field_patterns_set": (
        _fix_field_patterns_set,
        "Add field_patterns to frontier section in spark-chip.json",
    ),
    # Integration
    "project_json_valid": (
        _fix_project_json_valid,
        "Create/fix spark-researcher.project.json with project_name",
    ),
    "chip_path_set": (
        _fix_chip_path_set,
        "Set chip.path and chip.manifest in project config",
    ),
    "commands_defined": (
        _fix_commands_defined,
        "Add chip-evaluate command to project config",
    ),
    "guardrails_set": (
        _fix_guardrails_set,
        "Add guardrails with loop limits and blocked fragments",
    ),
    "self_edit_config": (
        _fix_self_edit_config,
        "Add self_edit section with mutable_targets to project config",
    ),
    # Documentation
    "readme_exists": (
        _fix_readme_exists,
        "Create README.md with mission and quick start",
    ),
    "mission_docs": (
        _fix_mission_docs,
        "Create docs/mission.md with intent documentation",
    ),
    "architecture_docs": (
        _fix_architecture_docs,
        "Create docs/architecture.md with one-loop spec",
    ),
    "docs_directory": (
        _fix_docs_directory,
        "Create docs/ directory with initial content",
    ),
    "pyproject_valid": (
        _fix_pyproject_valid,
        "Create pyproject.toml with valid package config",
    ),
    # Memory / Knowledge
    "source_registry": (
        _fix_source_registry,
        "Create docs/source_registry.md with source map template",
    ),
    "obsidian_vault": (
        _fix_obsidian_vault,
        "Create obsidian-vault/ with initial index page",
    ),
    "memory_backend": (
        _fix_memory_backend,
        "Set memory.backend to local in project config",
    ),
    # Evaluation depth
    "primary_metric": (
        _fix_primary_metric,
        "Set eval_metric in spark-researcher.project.json",
    ),
    "baseline_trial": (
        _fix_baseline_trial,
        "Add baseline trial with empty mutations to candidate_trials",
    ),
    "scoring_logic": (
        _fix_scoring_logic,
        "Create src/evaluate.py with a score function",
    ),
}


# ---------------------------------------------------------------------------
# Gap analysis
# ---------------------------------------------------------------------------

def analyze_gaps(score_result: dict[str, Any]) -> list[GapFix]:
    """Convert score_chip() output into a prioritized list of GapFix objects.

    Returns a list sorted by points_recoverable descending (highest-value
    fixes first).
    """
    gaps: list[GapFix] = []

    for check_id in score_result.get("failed_checks", []):
        dimension = _CHECK_TO_DIM.get(check_id, "unknown")
        description = _CHECK_TO_DESC.get(check_id, check_id)
        points = _CHECK_TO_PTS.get(check_id, 0)

        fix_entry = _FIX_REGISTRY.get(check_id)
        auto_fixable = fix_entry is not None
        fix_fn = fix_entry[0] if fix_entry else None
        fix_desc = fix_entry[1] if fix_entry else "Manual fix required"

        gaps.append(GapFix(
            check_id=check_id,
            dimension=dimension,
            description=description,
            points_recoverable=points,
            auto_fixable=auto_fixable,
            fix_fn=fix_fn,
            fix_description=fix_desc,
        ))

    # Sort by points_recoverable descending, then by check_id for stability
    gaps.sort(key=lambda g: (-g.points_recoverable, g.check_id))
    return gaps


# ---------------------------------------------------------------------------
# Score persistence
# ---------------------------------------------------------------------------

def _persist_score(chip_path: Path, score_result: dict[str, Any]) -> None:
    """Append a score result to the chip's JSONL ledger file.

    Writes to {chip_path}/score_history.jsonl, one JSON object per line.
    Each entry includes a timestamp for tracking progression.
    """
    ledger_path = chip_path / "score_history.jsonl"
    entry = {
        "timestamp": time.time(),
        "total_score": score_result.get("total_score", 0),
        "verdict": score_result.get("verdict", "unknown"),
        "passed_count": len(score_result.get("passed_checks", [])),
        "failed_count": len(score_result.get("failed_checks", [])),
        "passed_checks": score_result.get("passed_checks", []),
        "failed_checks": score_result.get("failed_checks", []),
        "dimensions": [
            {
                "name": d["name"],
                "score": d["score"],
                "max_points": d["max_points"],
            }
            for d in score_result.get("dimensions", [])
        ],
    }
    with open(ledger_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------------------
# Improvement orchestrator
# ---------------------------------------------------------------------------

def improve_chip(
    chip_path: str | Path,
    target_score: int = 60,
    max_iterations: int = 20,
) -> dict[str, Any]:
    """Run the autonomous score -> fix -> rescore improvement cycle.

    Scores the chip, applies auto-fixes for the highest-value gaps, rescores,
    and repeats until the target score is reached or max_iterations are
    exhausted.

    Returns a summary dict with:
      - initial_score: int
      - final_score: int
      - target_score: int
      - iterations: int
      - fixes_applied: list of {check_id, points_recoverable, succeeded}
      - final_result: full score_chip() output
      - reached_target: bool
    """
    chip_path = Path(chip_path)
    fixes_applied: list[dict[str, Any]] = []

    # Initial score
    result = score_chip(chip_path)
    initial_score = result["total_score"]
    _persist_score(chip_path, result)

    if initial_score >= target_score:
        return {
            "initial_score": initial_score,
            "final_score": initial_score,
            "target_score": target_score,
            "iterations": 0,
            "fixes_applied": [],
            "final_result": result,
            "reached_target": True,
        }

    for iteration in range(1, max_iterations + 1):
        gaps = analyze_gaps(result)

        # Filter to auto-fixable gaps only
        fixable = [g for g in gaps if g.auto_fixable and g.fix_fn is not None]
        if not fixable:
            # No more auto-fixable gaps remain
            break

        # Apply the highest-value fixable gap this iteration
        gap = fixable[0]
        try:
            succeeded = gap.fix_fn(chip_path)
        except Exception:
            succeeded = False

        gap.applied = True
        gap.succeeded = succeeded

        fixes_applied.append({
            "check_id": gap.check_id,
            "dimension": gap.dimension,
            "points_recoverable": gap.points_recoverable,
            "fix_description": gap.fix_description,
            "succeeded": succeeded,
            "iteration": iteration,
        })

        # Rescore after applying the fix
        result = score_chip(chip_path)
        _persist_score(chip_path, result)

        if result["total_score"] >= target_score:
            break

    final_score = result["total_score"]

    return {
        "initial_score": initial_score,
        "final_score": final_score,
        "target_score": target_score,
        "iterations": len(fixes_applied),
        "fixes_applied": fixes_applied,
        "final_result": result,
        "reached_target": final_score >= target_score,
    }
