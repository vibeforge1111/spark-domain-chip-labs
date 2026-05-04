"""Chip quality rubric v2 -- hardened 7-dimension evaluator.

Scores domain chips on a 100-point scale across seven dimensions (37 checks).
Backward compatible with v1 via ``score_chip(path, version="v2")``.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from chip_labs.quality_rubric import score_chip as _score_chip_v1

# ---------------------------------------------------------------------------
# Rubric dimensions and weights (total = 100, 37 checks)
# ---------------------------------------------------------------------------

RUBRIC_DIMENSIONS_V2: list[dict[str, Any]] = [
    # 1. Manifest Validity -- same as v1 (15 pts, 6 checks)
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
    # 2. Evidence Separation -- hardened (15 pts, 4 checks)
    {
        "name": "evidence_separation",
        "label": "Evidence Separation",
        "max_points": 15,
        "checks": [
            {"id": "has_research_grounded", "points": 4, "description": "research/research_grounded/ has file >50 bytes"},
            {"id": "has_benchmark_grounded", "points": 4, "description": "research/benchmark_grounded/ has file >50 bytes"},
            {"id": "has_exploratory_frontier", "points": 4, "description": "research/exploratory_frontier/ has file >50 bytes"},
            {"id": "has_realworld_validated", "points": 3, "description": "research/realworld_validated/ has file >50 bytes or docs fallback"},
        ],
    },
    # 3. Evaluation Depth -- hardened (15 pts, 5 checks)
    {
        "name": "evaluation_depth",
        "label": "Evaluation Depth",
        "max_points": 15,
        "checks": [
            {"id": "primary_metric", "points": 3, "description": "Primary eval metric defined in project.json"},
            {"id": "multiple_metrics", "points": 3, "description": "At least 3 metrics defined"},
            {"id": "scoring_function", "points": 3, "description": "Real scoring function (def + return numeric)"},
            {"id": "candidate_trials", "points": 3, "description": "At least 3 candidate trials defined"},
            {"id": "baseline_trial", "points": 3, "description": "Global baseline trial with empty mutations"},
        ],
    },
    # 4. Memory & Knowledge -- hardened (10 pts, 4 checks)
    {
        "name": "memory_knowledge",
        "label": "Memory & Knowledge",
        "max_points": 10,
        "checks": [
            {"id": "source_registry_urls", "points": 3, "description": "Docs contain real URLs (https, doi, arxiv, isbn)"},
            {"id": "packet_structured", "points": 3, "description": "Packet output has structured fields (claim/mechanism/boundary)"},
            {"id": "watchtower_pages", "points": 2, "description": "Watchtower generates Obsidian pages"},
            {"id": "obsidian_vault", "points": 2, "description": "Obsidian vault exists with content"},
        ],
    },
    # 5. Integration Health -- same logic, reduced points (10 pts, 5 checks)
    {
        "name": "integration_health",
        "label": "Integration Health",
        "max_points": 10,
        "checks": [
            {"id": "project_json_valid", "points": 2, "description": "spark-researcher.project.json exists and is valid"},
            {"id": "chip_path_set", "points": 2, "description": "Chip path correctly points to manifest"},
            {"id": "commands_defined", "points": 2, "description": "Commands section with chip-evaluate kind"},
            {"id": "guardrails_set", "points": 2, "description": "Guardrails with loop limits and safety"},
            {"id": "self_edit_config", "points": 2, "description": "Self-edit section with mutable_targets"},
        ],
    },
    # 6. Documentation -- hardened (10 pts, 5 checks)
    {
        "name": "documentation",
        "label": "Documentation",
        "max_points": 10,
        "checks": [
            {"id": "readme_exists", "points": 2, "description": "README.md with 200+ chars of content"},
            {"id": "mission_docs", "points": 2, "description": "Mission/intent doc with 150+ chars"},
            {"id": "architecture_docs", "points": 2, "description": "Architecture doc with 150+ chars"},
            {"id": "docs_directory", "points": 2, "description": "docs/ directory with 2+ files"},
            {"id": "pyproject_valid", "points": 2, "description": "pyproject.toml with valid package config"},
        ],
    },
    # 7. Flywheel Intelligence -- NEW (25 pts, 7 checks)
    {
        "name": "flywheel_intelligence",
        "label": "Flywheel Intelligence",
        "max_points": 25,
        "checks": [
            {"id": "has_run_history", "points": 4, "description": "Non-empty run history (JSONL/JSON/runs/ or research/meta/)"},
            {"id": "belief_promotion", "points": 5, "description": "Score trajectory improving or beliefs promoted"},
            {"id": "metric_trajectory", "points": 4, "description": "3+ entries with 2+ ascending transitions"},
            {"id": "contradiction_handling", "points": 4, "description": "CONTRADICTIONS.md or docs/beliefs/CONTRADICTIONS.md with >50 chars real content"},
            {"id": "packet_quality_real", "points": 3, "description": "research/packets/ has structured JSON packets"},
            {"id": "has_dspy_integration", "points": 3, "description": "DSPy scripts/config detected"},
            {"id": "has_skill_file", "points": 2, "description": "chip_skill.md or doctrine corpus exists with >200 chars"},
        ],
    },
]


# ---------------------------------------------------------------------------
# Dimension checkers
# ---------------------------------------------------------------------------

def _check_evidence_separation_v2(chip_path: Path) -> dict[str, bool]:
    """Hardened evidence check -- requires actual files in research/ sub-dirs."""
    results: dict[str, bool] = {}

    lane_dirs = {
        "has_research_grounded": "research/research_grounded",
        "has_benchmark_grounded": "research/benchmark_grounded",
        "has_exploratory_frontier": "research/exploratory_frontier",
        "has_realworld_validated": "research/realworld_validated",
    }

    for check_id, rel_dir in lane_dirs.items():
        lane_path = chip_path / rel_dir
        found = False
        if lane_path.is_dir():
            for fp in lane_path.iterdir():
                if fp.is_file() and fp.stat().st_size > 50:
                    found = True
                    break
        # Fallback for realworld_validated: docs file mentioning
        # "realworld" + ("plan" or "validation")
        if not found and check_id == "has_realworld_validated":
            docs_dir = chip_path / "docs"
            if docs_dir.is_dir():
                for md in docs_dir.rglob("*.md"):
                    try:
                        text = md.read_text(encoding="utf-8", errors="ignore").lower()
                        if "realworld" in text and ("plan" in text or "validation" in text):
                            found = True
                            break
                    except OSError:
                        pass
        results[check_id] = found

    return results


def _has_closed_mutation_space(allowed_mutations: Any) -> bool:
    """Return True when the mutation space is explicitly enumerated.

    Closed enum-style mutation spaces provide structural validation even when
    a chip omits regex field_patterns. This keeps v2 strict for open-ended
    frontiers while not penalizing chips that already constrain mutations to
    explicit value lists.
    """
    if isinstance(allowed_mutations, list):
        return bool(allowed_mutations)
    if isinstance(allowed_mutations, dict):
        return bool(allowed_mutations) and all(
            isinstance(values, list) and bool(values)
            for values in allowed_mutations.values()
        )
    return False


def _check_manifest_v2(chip_path: Path) -> dict[str, bool]:
    """Manifest validity with support for closed enum mutation spaces."""
    manifest_path = chip_path / "spark-chip.json"
    if not manifest_path.exists():
        return {
            c["id"]: False
            for dim in RUBRIC_DIMENSIONS_V2
            if dim["name"] == "manifest_validity"
            for c in dim["checks"]
        }

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {
            c["id"]: False
            for dim in RUBRIC_DIMENSIONS_V2
            if dim["name"] == "manifest_validity"
            for c in dim["checks"]
        }

    results: dict[str, bool] = {}
    results["schema_version"] = manifest.get("schema_version") == "spark-chip.v1"
    results["io_protocol"] = manifest.get("io_protocol") == "spark-hook-io.v1"

    caps = set(manifest.get("capabilities", []))
    results["all_four_hooks"] = {
        "evaluate", "suggest", "packets", "watchtower"
    }.issubset(caps)

    frontier = manifest.get("frontier", {})
    allowed_mutations = frontier.get("allowed_mutations")
    closed_mutation_space = _has_closed_mutation_space(allowed_mutations)

    results["frontier_enabled"] = bool(frontier.get("enabled")) and bool(allowed_mutations)
    results["required_fields_set"] = "required_fields" in frontier or closed_mutation_space
    results["field_patterns_set"] = bool(frontier.get("field_patterns")) or closed_mutation_space
    return results


def _check_evaluation_depth_v2(chip_path: Path) -> dict[str, bool]:
    """Hardened evaluation check -- regex-based scoring function detection."""
    results: dict[str, bool] = {}
    project_path = chip_path / "spark-researcher.project.json"

    if not project_path.exists():
        return {c["id"]: False for dim in RUBRIC_DIMENSIONS_V2
                if dim["name"] == "evaluation_depth" for c in dim["checks"]}

    try:
        project = json.loads(project_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {c["id"]: False for dim in RUBRIC_DIMENSIONS_V2
                if dim["name"] == "evaluation_depth" for c in dim["checks"]}

    results["primary_metric"] = bool(project.get("eval_metric"))
    metrics = project.get("metrics", {})
    results["multiple_metrics"] = len(metrics) >= 3
    trials = project.get("candidate_trials", [])
    results["candidate_trials"] = len(trials) >= 3
    results["baseline_trial"] = any(
        t.get("mutations", None) == {} or t.get("mutations") is None
        for t in trials
    )

    # Hardened: regex for real scoring function
    scoring_re = re.compile(
        r"def\s+(score|evaluate)\s*\(.*?\)\s*.*?:"
        r"[\s\S]*?"
        r"return\s+",
        re.MULTILINE,
    )
    src_dir = chip_path / "src"
    has_scoring = False
    if src_dir.exists():
        for py in src_dir.rglob("*.py"):
            try:
                content = py.read_text(encoding="utf-8", errors="ignore")
                if scoring_re.search(content):
                    has_scoring = True
                    break
            except OSError:
                pass
    results["scoring_function"] = has_scoring

    return results


def _check_memory_knowledge_v2(chip_path: Path) -> dict[str, bool]:
    """Hardened memory check -- real URLs and structured packets."""
    results: dict[str, bool] = {}

    # source_registry_urls -- require actual URL patterns in docs/
    url_re = re.compile(r"https?://\S+|doi:\S+|arxiv:\S+|isbn:\S+", re.IGNORECASE)
    docs_dir = chip_path / "docs"
    has_urls = False
    if docs_dir.is_dir():
        for md in docs_dir.rglob("*"):
            if not md.is_file():
                continue
            try:
                text = md.read_text(encoding="utf-8", errors="ignore")
                if url_re.search(text):
                    has_urls = True
                    break
            except OSError:
                pass
    results["source_registry_urls"] = has_urls

    # packet_structured -- check src/ for structured packet fields
    src_dir = chip_path / "src"
    has_packet = False
    required_fields_a = {"claim", "mechanism", "boundary"}
    required_fields_b = {"type", "evidence_lane", "content"}
    if src_dir.exists():
        for py in src_dir.rglob("*.py"):
            try:
                text = py.read_text(encoding="utf-8", errors="ignore").lower()
                if all(f in text for f in required_fields_a) or all(f in text for f in required_fields_b):
                    has_packet = True
                    break
            except OSError:
                pass
    results["packet_structured"] = has_packet

    # watchtower_pages
    all_py = ""
    if src_dir.exists():
        for py in src_dir.rglob("*.py"):
            try:
                all_py += py.read_text(encoding="utf-8", errors="ignore").lower()
            except OSError:
                pass
    results["watchtower_pages"] = "watchtower" in all_py or "obsidian" in all_py

    # obsidian_vault
    vault = chip_path / "obsidian-vault"
    results["obsidian_vault"] = vault.exists() and any(vault.rglob("*.md"))

    return results


def _check_integration_health_v2(chip_path: Path) -> dict[str, bool]:
    """Integration health -- same logic as v1."""
    results: dict[str, bool] = {}
    project_path = chip_path / "spark-researcher.project.json"

    if not project_path.exists():
        return {c["id"]: False for dim in RUBRIC_DIMENSIONS_V2
                if dim["name"] == "integration_health" for c in dim["checks"]}

    try:
        project = json.loads(project_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {c["id"]: False for dim in RUBRIC_DIMENSIONS_V2
                if dim["name"] == "integration_health" for c in dim["checks"]}

    results["project_json_valid"] = bool(project.get("project_name"))
    chip_cfg = project.get("chip", {})
    results["chip_path_set"] = bool(chip_cfg.get("path")) and bool(chip_cfg.get("manifest"))
    commands = project.get("commands", {})
    results["commands_defined"] = any(
        c.get("kind") == "chip-evaluate" for c in commands.values()
    )
    guardrails = project.get("guardrails", {})
    results["guardrails_set"] = bool(guardrails.get("max_loop_iterations")) and any(
        [
            bool(guardrails.get("blocked_command_fragments")),
            bool(guardrails.get("consecutive_discard_limit")),
            bool(guardrails.get("require_human_approval_for_self_edit")),
        ]
    )
    results["self_edit_config"] = bool(
        project.get("self_edit", {}).get("mutable_targets")
    )

    return results


def _check_documentation_v2(chip_path: Path) -> dict[str, bool]:
    """Hardened documentation check -- minimum content lengths."""
    results: dict[str, bool] = {}

    # readme_exists -- 200+ chars
    readme = chip_path / "README.md"
    if readme.exists():
        try:
            text = readme.read_text(encoding="utf-8", errors="ignore")
            results["readme_exists"] = len(text) >= 200
        except OSError:
            results["readme_exists"] = False
    else:
        results["readme_exists"] = False

    # pyproject_valid
    results["pyproject_valid"] = (chip_path / "pyproject.toml").exists()

    # docs_directory -- needs 2+ files
    docs_dir = chip_path / "docs"
    if docs_dir.is_dir():
        file_count = sum(1 for _ in docs_dir.rglob("*") if _.is_file())
        results["docs_directory"] = file_count >= 2
    else:
        results["docs_directory"] = False

    # mission_docs -- 150+ chars in a mission/intent doc
    has_mission = False
    if docs_dir.is_dir():
        for md in docs_dir.rglob("*.md"):
            name_lower = md.name.lower()
            if "mission" in name_lower or "intent" in name_lower:
                try:
                    text = md.read_text(encoding="utf-8", errors="ignore")
                    if len(text) >= 150:
                        has_mission = True
                        break
                except OSError:
                    pass
    # Fallback: README.md with mission content >= 150 chars referencing "mission"
    if not has_mission and readme.exists():
        try:
            text = readme.read_text(encoding="utf-8", errors="ignore")
            if len(text) >= 150 and "mission" in text.lower():
                has_mission = True
        except OSError:
            pass
    results["mission_docs"] = has_mission

    # architecture_docs -- 150+ chars
    has_arch = False
    if docs_dir.is_dir():
        for md in docs_dir.rglob("*.md"):
            name_lower = md.name.lower()
            if "architecture" in name_lower or "one_loop" in name_lower or "flywheel" in name_lower:
                try:
                    text = md.read_text(encoding="utf-8", errors="ignore")
                    if len(text) >= 150:
                        has_arch = True
                        break
                except OSError:
                    pass
    results["architecture_docs"] = has_arch

    return results


def _check_flywheel_intelligence(chip_path: Path) -> dict[str, bool]:
    """NEW dimension -- flywheel intelligence checks."""
    results: dict[str, bool] = {}

    # --- has_run_history (4 pts) ---
    has_history = False
    for candidate in [
        chip_path / "score_history.jsonl",
        chip_path / "loop_telemetry.json",
        chip_path / "research" / "meta" / "runs.jsonl",
        chip_path / "research" / "meta" / "loop_telemetry.json",
    ]:
        if candidate.is_file() and candidate.stat().st_size > 0:
            has_history = True
            break
    if not has_history:
        runs_dir = chip_path / "runs"
        if runs_dir.is_dir() and any(runs_dir.iterdir()):
            has_history = True
    results["has_run_history"] = has_history

    # --- belief_promotion (5 pts) ---
    # Score trajectory shows improvement OR belief files contain "promoted"/"durable"
    promoted = False
    # Check JSONL run histories for improvement
    scores: list[float] = []
    for history_path in [
        chip_path / "score_history.jsonl",
        chip_path / "research" / "meta" / "runs.jsonl",
    ]:
        if not history_path.is_file():
            continue
        try:
            for line in history_path.read_text(encoding="utf-8", errors="ignore").splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    if "score" in entry:
                        scores.append(float(entry["score"]))
                except (json.JSONDecodeError, ValueError, TypeError):
                    pass
        except OSError:
            pass
        if scores:
            break

    # Also try loop telemetry arrays
    if not scores:
        for telemetry_path in [
            chip_path / "loop_telemetry.json",
            chip_path / "research" / "meta" / "loop_telemetry.json",
        ]:
            if not telemetry_path.is_file():
                continue
            try:
                data = json.loads(telemetry_path.read_text(encoding="utf-8"))
                if isinstance(data, list):
                    for entry in data:
                        if isinstance(entry, dict) and "score" in entry:
                            scores.append(float(entry["score"]))
            except (json.JSONDecodeError, OSError, ValueError, TypeError):
                pass
            if scores:
                break

    if len(scores) >= 2 and scores[-1] > scores[0]:
        promoted = True

    # Check belief files for "promoted" or "durable"
    if not promoted:
        belief_candidates: list[Path] = []

        for pattern in [
            "belief*.md",
            "belief*.json",
            "**/belief*.md",
            "**/belief*.json",
            "beliefs/**/*.md",
            "beliefs/**/*.json",
            "docs/beliefs/**/*.md",
            "docs/beliefs/**/*.json",
            "artifacts/memory/**/*.md",
            "artifacts/memory/**/*.json",
        ]:
            for fp in chip_path.glob(pattern):
                if fp.is_file():
                    belief_candidates.append(fp)

        seen_candidates: set[Path] = set()
        for fp in belief_candidates:
            if fp in seen_candidates:
                continue
            seen_candidates.add(fp)
            try:
                text = fp.read_text(encoding="utf-8", errors="ignore").lower()
                if "promoted" in text or "durable" in text:
                    promoted = True
                    break
            except OSError:
                pass
    results["belief_promotion"] = promoted

    # --- metric_trajectory (4 pts) ---
    # 3+ entries with 2+ ascending transitions
    ascending_count = 0
    for i in range(1, len(scores)):
        if scores[i] > scores[i - 1]:
            ascending_count += 1
    results["metric_trajectory"] = len(scores) >= 3 and ascending_count >= 2

    # --- contradiction_handling (4 pts) ---
    has_contradictions = False
    for contradictions_path in [
        chip_path / "CONTRADICTIONS.md",
        chip_path / "docs" / "beliefs" / "CONTRADICTIONS.md",
    ]:
        if not contradictions_path.is_file():
            continue
        try:
            text = contradictions_path.read_text(encoding="utf-8", errors="ignore")
            # Strip headers (lines starting with #) and whitespace
            content_lines = [
                line for line in text.splitlines()
                if line.strip() and not line.strip().startswith("#")
            ]
            real_content = "\n".join(content_lines).strip()
            has_contradictions = len(real_content) > 50
            if has_contradictions:
                break
        except OSError:
            pass
    results["contradiction_handling"] = has_contradictions

    # --- packet_quality_real (3 pts) ---
    packets_dir = chip_path / "research" / "packets"
    has_real_packets = False
    if packets_dir.is_dir():
        required_a = {"claim", "mechanism", "boundary"}
        required_b = {"type", "evidence_lane", "content"}
        for fp in packets_dir.iterdir():
            if not fp.is_file() or fp.suffix.lower() != ".json":
                continue
            try:
                data = json.loads(fp.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    keys = set(data.keys())
                    if required_a.issubset(keys) or required_b.issubset(keys):
                        has_real_packets = True
                        break
            except (json.JSONDecodeError, OSError):
                pass
    results["packet_quality_real"] = has_real_packets

    # --- has_dspy_integration (3 pts) ---
    has_dspy = False
    # Check for dspy_config.json
    if (chip_path / "dspy_config.json").is_file():
        has_dspy = True
    # Check for DSPy scripts or imports in src/
    if not has_dspy:
        src_dir = chip_path / "src"
        if src_dir.is_dir():
            for py in src_dir.rglob("*.py"):
                try:
                    text = py.read_text(encoding="utf-8", errors="ignore")
                    if "import dspy" in text or "DSpySlot" in text:
                        has_dspy = True
                        break
                except OSError:
                    pass
    # Check for dspy scripts at top level
    if not has_dspy:
        for py in chip_path.glob("*dspy*"):
            if py.is_file():
                has_dspy = True
                break
    results["has_dspy_integration"] = has_dspy

    # --- has_skill_file (2 pts) ---
    has_skill = False
    for skill_file in [
        chip_path / "chip_skill.md",
        chip_path / "docs" / "doctrines" / "loop_governance.md",
        chip_path / "docs" / "doctrines" / "transfer_promotion.md",
        chip_path / "docs" / "beliefs" / "evidence_lanes.md",
    ]:
        if not skill_file.is_file():
            continue
        try:
            text = skill_file.read_text(encoding="utf-8", errors="ignore")
            if len(text) > 200:
                has_skill = True
                break
        except OSError:
            pass
    results["has_skill_file"] = has_skill

    return results


# ---------------------------------------------------------------------------
# Checker dispatch
# ---------------------------------------------------------------------------

_CHECKERS_V2 = {
    "manifest_validity": _check_manifest_v2,
    "evidence_separation": _check_evidence_separation_v2,
    "evaluation_depth": _check_evaluation_depth_v2,
    "memory_knowledge": _check_memory_knowledge_v2,
    "integration_health": _check_integration_health_v2,
    "documentation": _check_documentation_v2,
    "flywheel_intelligence": _check_flywheel_intelligence,
}


# ---------------------------------------------------------------------------
# Main scoring function
# ---------------------------------------------------------------------------

def score_chip_v2(chip_path: str | Path) -> dict[str, Any]:
    """Score a domain chip against the hardened v2 quality rubric.

    Returns a dict with:
      - total_score: int (0-100)
      - dimensions: list of dimension results (7 dimensions)
      - passed_checks: list of check ids that passed
      - failed_checks: list of check ids that failed
      - verdict: str ("production_ready" | "beta" | "alpha" | "scaffold")
      - rubric_version: "2.0"
    """
    chip_path = Path(chip_path)
    if not chip_path.exists():
        return {
            "total_score": 0,
            "dimensions": [],
            "passed_checks": [],
            "failed_checks": [],
            "verdict": "not_found",
            "rubric_version": "2.0",
            "error": f"Chip path does not exist: {chip_path}",
        }

    all_passed: list[str] = []
    all_failed: list[str] = []
    dimension_results: list[dict[str, Any]] = []
    total = 0

    for dim in RUBRIC_DIMENSIONS_V2:
        checker = _CHECKERS_V2.get(dim["name"])
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
        "rubric_version": "2.0",
    }


# ---------------------------------------------------------------------------
# Backward-compatible dispatcher
# ---------------------------------------------------------------------------

def score_chip(chip_path: str | Path, version: str = "v2") -> dict[str, Any]:
    """Score a chip using the specified rubric version.

    Parameters
    ----------
    chip_path : str | Path
        Root directory of the domain chip.
    version : str
        ``"v1"`` for the original rubric, ``"v2"`` (default) for the
        hardened 7-dimension rubric.
    """
    if version == "v1":
        return _score_chip_v1(chip_path)
    return score_chip_v2(chip_path)
