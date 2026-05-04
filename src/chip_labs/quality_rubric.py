"""Chip quality rubric -- the lab's fixed evaluator.

Scores domain chips on a 100-point scale across six dimensions.
This is the meta-chip's primary evaluation surface.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Rubric dimensions and weights (total = 100)
# ---------------------------------------------------------------------------

RUBRIC_DIMENSIONS: list[dict[str, Any]] = [
    {
        "name": "manifest_validity",
        "label": "Manifest Validity",
        "max_points": 15,
        "checks": [
            {"id": "schema_version", "points": 3, "description": "spark-chip.v1 schema declared"},
            {"id": "io_protocol", "points": 2, "description": "spark-hook-io.v1 protocol declared"},
            {"id": "all_four_hooks", "points": 4, "description": "evaluate, suggest, packets, watchtower all present"},
            {"id": "frontier_enabled", "points": 3, "description": "Frontier section with allowed_mutations defined"},
            {"id": "required_fields_set", "points": 1, "description": "At least one required_field or explicit empty"},
            {"id": "field_patterns_set", "points": 2, "description": "Field patterns defined for validation"},
        ],
    },
    {
        "name": "evidence_separation",
        "label": "Evidence Separation",
        "max_points": 20,
        "checks": [
            {"id": "has_research_grounded", "points": 5, "description": "Research-grounded evidence lane exists"},
            {"id": "has_benchmark_grounded", "points": 5, "description": "Benchmark-grounded evidence lane exists"},
            {"id": "has_exploratory_frontier", "points": 5, "description": "Exploratory frontier lane exists"},
            {"id": "has_realworld_validated", "points": 5, "description": "Real-world validation lane exists or is planned"},
        ],
    },
    {
        "name": "evaluation_depth",
        "label": "Evaluation Depth",
        "max_points": 20,
        "checks": [
            {"id": "primary_metric", "points": 4, "description": "Primary eval metric defined in project.json"},
            {"id": "multiple_metrics", "points": 4, "description": "At least 3 metrics defined"},
            {"id": "scoring_logic", "points": 4, "description": "Scoring logic exists in evaluate hook"},
            {"id": "candidate_trials", "points": 4, "description": "At least 3 candidate trials defined"},
            {"id": "baseline_trial", "points": 4, "description": "Global baseline trial with empty mutations"},
        ],
    },
    {
        "name": "memory_knowledge",
        "label": "Memory & Knowledge",
        "max_points": 15,
        "checks": [
            {"id": "source_registry", "points": 3, "description": "Source registry or documentation of primary sources"},
            {"id": "packet_schema", "points": 3, "description": "Packet output schema defined or documented"},
            {"id": "watchtower_pages", "points": 3, "description": "Watchtower generates meaningful Obsidian pages"},
            {"id": "obsidian_vault", "points": 3, "description": "Obsidian vault exists with content"},
            {"id": "memory_backend", "points": 3, "description": "Memory backend configured (local or ruvector)"},
        ],
    },
    {
        "name": "integration_health",
        "label": "Integration Health",
        "max_points": 15,
        "checks": [
            {"id": "project_json_valid", "points": 3, "description": "spark-researcher.project.json exists and is valid"},
            {"id": "chip_path_set", "points": 3, "description": "Chip path correctly points to manifest"},
            {"id": "commands_defined", "points": 3, "description": "Commands section with chip-evaluate kind"},
            {"id": "guardrails_set", "points": 3, "description": "Guardrails with loop limits and safety"},
            {"id": "self_edit_config", "points": 3, "description": "Self-edit section with mutable_targets"},
        ],
    },
    {
        "name": "documentation",
        "label": "Documentation",
        "max_points": 15,
        "checks": [
            {"id": "readme_exists", "points": 3, "description": "README.md with mission and quick start"},
            {"id": "mission_docs", "points": 3, "description": "Mission or intent documentation"},
            {"id": "architecture_docs", "points": 3, "description": "Architecture or one-loop spec documented"},
            {"id": "docs_directory", "points": 3, "description": "docs/ directory with structured content"},
            {"id": "pyproject_valid", "points": 3, "description": "pyproject.toml with valid package config"},
        ],
    },
]


def _check_manifest(chip_path: Path) -> dict[str, bool]:
    """Run manifest validity checks against a chip's spark-chip.json."""
    manifest_path = chip_path / "spark-chip.json"
    results: dict[str, bool] = {}

    if not manifest_path.exists():
        return {c["id"]: False for dim in RUBRIC_DIMENSIONS if dim["name"] == "manifest_validity" for c in dim["checks"]}

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {c["id"]: False for dim in RUBRIC_DIMENSIONS if dim["name"] == "manifest_validity" for c in dim["checks"]}

    results["schema_version"] = manifest.get("schema_version") == "spark-chip.v1"
    results["io_protocol"] = manifest.get("io_protocol") == "spark-hook-io.v1"

    caps = set(manifest.get("capabilities", []))
    results["all_four_hooks"] = {"evaluate", "suggest", "packets", "watchtower"}.issubset(caps)

    frontier = manifest.get("frontier", {})
    results["frontier_enabled"] = bool(frontier.get("enabled")) and bool(frontier.get("allowed_mutations"))
    results["required_fields_set"] = "required_fields" in frontier
    results["field_patterns_set"] = bool(frontier.get("field_patterns"))

    return results


def _check_evidence_separation(chip_path: Path) -> dict[str, bool]:
    """Check for evidence lane separation indicators."""
    results: dict[str, bool] = {}

    # Check across docs, src, and obsidian-vault for evidence lane references
    all_text = ""
    for pattern in ["docs/**/*.md", "src/**/*.py", "obsidian-vault/**/*.md", "README.md"]:
        for fp in chip_path.glob(pattern):
            try:
                all_text += fp.read_text(encoding="utf-8", errors="ignore").lower()
            except OSError:
                pass

    results["has_research_grounded"] = "research_grounded" in all_text or "research-grounded" in all_text or "source" in all_text
    results["has_benchmark_grounded"] = "benchmark_grounded" in all_text or "benchmark-grounded" in all_text or "benchmark" in all_text
    results["has_exploratory_frontier"] = "exploratory_frontier" in all_text or "exploratory" in all_text or "frontier" in all_text
    results["has_realworld_validated"] = "realworld_validated" in all_text or "real-world" in all_text or "realworld" in all_text

    return results


def _check_evaluation_depth(chip_path: Path) -> dict[str, bool]:
    """Check evaluation surface depth."""
    results: dict[str, bool] = {}
    project_path = chip_path / "spark-researcher.project.json"

    if not project_path.exists():
        return {c["id"]: False for dim in RUBRIC_DIMENSIONS if dim["name"] == "evaluation_depth" for c in dim["checks"]}

    try:
        project = json.loads(project_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {c["id"]: False for dim in RUBRIC_DIMENSIONS if dim["name"] == "evaluation_depth" for c in dim["checks"]}

    results["primary_metric"] = bool(project.get("eval_metric"))
    metrics = project.get("metrics", {})
    results["multiple_metrics"] = len(metrics) >= 3
    trials = project.get("candidate_trials", [])
    results["candidate_trials"] = len(trials) >= 3
    results["baseline_trial"] = any(t.get("mutations", None) == {} or t.get("mutations") is None for t in trials)

    # Check for scoring logic in src
    src_dir = chip_path / "src"
    has_scoring = False
    if src_dir.exists():
        for py in src_dir.rglob("*.py"):
            try:
                content = py.read_text(encoding="utf-8", errors="ignore")
                if "score" in content.lower() and ("def " in content or "class " in content):
                    has_scoring = True
                    break
            except OSError:
                pass
    results["scoring_logic"] = has_scoring

    return results


def _check_memory_knowledge(chip_path: Path) -> dict[str, bool]:
    """Check memory and knowledge system quality."""
    results: dict[str, bool] = {}

    # Source registry
    docs_dir = chip_path / "docs"
    has_sources = False
    if docs_dir.exists():
        for md in docs_dir.rglob("*.md"):
            try:
                content = md.read_text(encoding="utf-8", errors="ignore").lower()
                if "source" in content and ("registry" in content or "map" in content or "list" in content):
                    has_sources = True
                    break
            except OSError:
                pass
    results["source_registry"] = has_sources

    # Packet schema
    all_py = ""
    src_dir = chip_path / "src"
    if src_dir.exists():
        for py in src_dir.rglob("*.py"):
            try:
                all_py += py.read_text(encoding="utf-8", errors="ignore").lower()
            except OSError:
                pass
    results["packet_schema"] = "packet" in all_py

    # Watchtower
    results["watchtower_pages"] = "watchtower" in all_py or "obsidian" in all_py

    # Obsidian vault
    vault = chip_path / "obsidian-vault"
    results["obsidian_vault"] = vault.exists() and any(vault.rglob("*.md"))

    # Memory backend
    project_path = chip_path / "spark-researcher.project.json"
    if project_path.exists():
        try:
            project = json.loads(project_path.read_text(encoding="utf-8"))
            results["memory_backend"] = bool(project.get("memory", {}).get("backend"))
        except (json.JSONDecodeError, OSError):
            results["memory_backend"] = False
    else:
        results["memory_backend"] = False

    return results


def _check_integration_health(chip_path: Path) -> dict[str, bool]:
    """Check spark-researcher integration health."""
    results: dict[str, bool] = {}
    project_path = chip_path / "spark-researcher.project.json"

    if not project_path.exists():
        return {c["id"]: False for dim in RUBRIC_DIMENSIONS if dim["name"] == "integration_health" for c in dim["checks"]}

    try:
        project = json.loads(project_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {c["id"]: False for dim in RUBRIC_DIMENSIONS if dim["name"] == "integration_health" for c in dim["checks"]}

    results["project_json_valid"] = bool(project.get("project_name"))
    chip_cfg = project.get("chip", {})
    results["chip_path_set"] = bool(chip_cfg.get("path")) and bool(chip_cfg.get("manifest"))
    commands = project.get("commands", {})
    results["commands_defined"] = any(c.get("kind") == "chip-evaluate" for c in commands.values())
    guardrails = project.get("guardrails", {})
    results["guardrails_set"] = bool(guardrails.get("max_loop_iterations")) and bool(guardrails.get("blocked_command_fragments"))
    results["self_edit_config"] = bool(project.get("self_edit", {}).get("mutable_targets"))

    return results


def _check_documentation(chip_path: Path) -> dict[str, bool]:
    """Check documentation quality."""
    results: dict[str, bool] = {}

    results["readme_exists"] = (chip_path / "README.md").exists()
    results["pyproject_valid"] = (chip_path / "pyproject.toml").exists()

    docs_dir = chip_path / "docs"
    results["docs_directory"] = docs_dir.exists() and any(docs_dir.rglob("*.md"))

    # Check for mission/intent docs
    has_mission = False
    has_architecture = False
    if docs_dir.exists():
        for md in docs_dir.rglob("*.md"):
            name_lower = md.name.lower()
            if "mission" in name_lower or "intent" in name_lower:
                has_mission = True
            if "architecture" in name_lower or "one_loop" in name_lower or "flywheel" in name_lower:
                has_architecture = True
    # Also check README for mission content
    readme = chip_path / "README.md"
    if readme.exists():
        try:
            readme_text = readme.read_text(encoding="utf-8", errors="ignore").lower()
            if "mission" in readme_text or "what this is" in readme_text:
                has_mission = True
        except OSError:
            pass

    results["mission_docs"] = has_mission
    results["architecture_docs"] = has_architecture

    return results


# ---------------------------------------------------------------------------
# Main scoring function
# ---------------------------------------------------------------------------

_CHECKERS = {
    "manifest_validity": _check_manifest,
    "evidence_separation": _check_evidence_separation,
    "evaluation_depth": _check_evaluation_depth,
    "memory_knowledge": _check_memory_knowledge,
    "integration_health": _check_integration_health,
    "documentation": _check_documentation,
}


def score_chip(chip_path: str | Path) -> dict[str, Any]:
    """Score a domain chip against the quality rubric.

    Returns a dict with:
      - total_score: int (0-100)
      - dimensions: list of dimension results
      - passed_checks: list of check ids that passed
      - failed_checks: list of check ids that failed
      - verdict: str ("production_ready" | "beta" | "alpha" | "scaffold")
    """
    chip_path = Path(chip_path)
    if not chip_path.exists():
        return {
            "total_score": 0,
            "dimensions": [],
            "passed_checks": [],
            "failed_checks": [],
            "verdict": "not_found",
            "error": f"Chip path does not exist: {chip_path}",
        }

    all_passed: list[str] = []
    all_failed: list[str] = []
    dimension_results: list[dict[str, Any]] = []
    total = 0

    for dim in RUBRIC_DIMENSIONS:
        checker = _CHECKERS.get(dim["name"])
        if not checker:
            continue

        check_results = checker(chip_path)
        dim_score = 0
        dim_checks: list[dict[str, Any]] = []

        for check in dim["checks"]:
            passed = check_results.get(check["id"], False)
            if passed:
                dim_score += check["points"]
                all_passed.append(check["id"])
            else:
                all_failed.append(check["id"])
            dim_checks.append({
                "id": check["id"],
                "description": check["description"],
                "points": check["points"],
                "passed": passed,
            })

        total += dim_score
        dimension_results.append({
            "name": dim["name"],
            "label": dim["label"],
            "max_points": dim["max_points"],
            "score": dim_score,
            "checks": dim_checks,
        })

    # Determine verdict
    if total >= 80:
        verdict = "production_ready"
    elif total >= 60:
        verdict = "beta"
    elif total >= 35:
        verdict = "alpha"
    else:
        verdict = "scaffold"

    return {
        "total_score": total,
        "dimensions": dimension_results,
        "passed_checks": all_passed,
        "failed_checks": all_failed,
        "verdict": verdict,
    }


def score_portfolio(chip_paths: list[str | Path]) -> dict[str, Any]:
    """Score an entire portfolio of chips.

    Returns aggregate stats and per-chip results.
    """
    results: list[dict[str, Any]] = []
    total_score_sum = 0

    for cp in chip_paths:
        chip_result = score_chip(cp)
        chip_result["chip_path"] = str(cp)
        chip_result["chip_name"] = Path(cp).name
        results.append(chip_result)
        total_score_sum += chip_result["total_score"]

    avg_score = total_score_sum / len(results) if results else 0.0

    verdict_counts = {}
    for r in results:
        v = r["verdict"]
        verdict_counts[v] = verdict_counts.get(v, 0) + 1

    return {
        "portfolio_size": len(results),
        "average_score": round(avg_score, 2),
        "verdict_distribution": verdict_counts,
        "chips": results,
    }
