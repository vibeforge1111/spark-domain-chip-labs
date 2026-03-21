"""Cross-chip intelligence transfer system.

Enables mature chips to teach struggling chips by extracting proven
patterns and applying them structurally.  Currently each chip is a
complete silo -- this module bridges the gap so that patterns discovered
in production chips (like startup-yc v0.3.0) propagate to newer ones.

Pipeline:
    1. Extract patterns from high-scoring chips
    2. Find applicable patterns for a target chip
    3. Apply proven patterns (additive only -- never deletes)
    4. Track transfer effectiveness with before/after scoring

Zero external dependencies.  Uses only stdlib dataclasses + json + pathlib.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..quality_rubric import score_chip


# ---------------------------------------------------------------------------
# Pattern type constants
# ---------------------------------------------------------------------------

PATTERN_TYPES = (
    "scoring_model",
    "loop_design",
    "evidence_strategy",
    "promotion_gate",
    "contradiction_detection",
    "research_pipeline",
    "watchtower_design",
)

# ---------------------------------------------------------------------------
# Category taxonomy
# ---------------------------------------------------------------------------

CATEGORY_MAP: dict[str, list[str]] = {
    "finance": [
        "trading-crypto", "fintech", "defi",
    ],
    "creative": [
        "web-designer", "content", "xcontent",
    ],
    "business": [
        "startup-yc", "agentic-marketing", "vibe-incubator",
    ],
    "gaming": [
        "pokemon-red", "roblox-development",
    ],
    "science": [
        "predictive-worlds-lab",
    ],
    "technology": [
        "domain-chip-labs",
    ],
}


def _chip_category(chip_name: str) -> str:
    """Resolve the category for a chip by name."""
    normalised = chip_name.replace("domain-chip-", "")
    for category, members in CATEGORY_MAP.items():
        if normalised in members or chip_name in members:
            return category
    return "general"


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class TransferPattern:
    """A single transferable pattern extracted from a chip."""

    pattern_id: str
    source_chip: str
    pattern_type: str  # one of PATTERN_TYPES
    description: str
    implementation: dict[str, Any]
    evidence_strength: float  # 0-1, based on source chip's rubric score
    applicable_categories: list[str]  # ["all"] for universal
    times_applied: int = 0
    times_successful: int = 0


@dataclass
class TransferResult:
    """Outcome of a transfer operation on a single target chip."""

    target_chip: str
    patterns_applied: list[str]  # pattern_ids
    score_before: int
    score_after: int
    score_delta: int
    successful_transfers: list[str]
    failed_transfers: list[str]
    recommendations: list[str]  # what still needs manual work


@dataclass
class TransferRegistry:
    """Persistent registry of known patterns and transfer history."""

    patterns: list[TransferPattern] = field(default_factory=list)
    transfer_history: list[TransferResult] = field(default_factory=list)
    last_extraction: str | None = None  # ISO timestamp


# ---------------------------------------------------------------------------
# Safe file helpers (mirror gap_analyzer conventions)
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
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _ensure_file(path: Path, content: str) -> None:
    """Create a file only if it does not already exist."""
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _ensure_key(data: dict, key: str, default: Any) -> bool:
    """Set a key in a dict only if it is missing.  Returns True if changed."""
    if key not in data:
        data[key] = default
        return True
    return False


def _pattern_id(source: str, ptype: str, discriminator: str = "") -> str:
    """Deterministic pattern id from source chip + type + discriminator."""
    raw = f"{source}:{ptype}:{discriminator}"
    short_hash = hashlib.sha256(raw.encode()).hexdigest()[:8]
    return f"{ptype}_{short_hash}"


def _collect_text(chip_path: Path, globs: list[str]) -> str:
    """Concatenate text from files matching any of the given glob patterns."""
    parts: list[str] = []
    for pattern in globs:
        for fp in chip_path.glob(pattern):
            try:
                parts.append(fp.read_text(encoding="utf-8", errors="ignore"))
            except OSError:
                pass
    return "\n".join(parts).lower()


# ---------------------------------------------------------------------------
# Pattern extraction helpers
# ---------------------------------------------------------------------------

def _extract_scoring_model_patterns(
    chip_path: Path,
    chip_name: str,
    evidence_strength: float,
) -> list[TransferPattern]:
    """Scan src/ for additive scoring model patterns."""
    patterns: list[TransferPattern] = []
    src_text = _collect_text(chip_path, ["src/**/*.py"])

    # Detect dimension dicts  -- e.g.  DIMENSIONS = { "axis": { "val": score } }
    if "dimensions" in src_text or "dim_values" in src_text or "dimension" in src_text:
        has_pair = "pair_bonus" in src_text or "pair_bonuses" in src_text
        has_system = "system_bonus" in src_text or "system_bonuses" in src_text
        impl: dict[str, Any] = {
            "has_dimensions": True,
            "has_pair_bonuses": has_pair,
            "has_system_bonuses": has_system,
            "source_files": [
                str(p.relative_to(chip_path))
                for p in chip_path.glob("src/**/*.py")
                if "score" in p.read_text(encoding="utf-8", errors="ignore").lower()
            ],
        }
        patterns.append(TransferPattern(
            pattern_id=_pattern_id(chip_name, "scoring_model", "additive"),
            source_chip=chip_name,
            pattern_type="scoring_model",
            description=(
                f"Additive mutation scoring model from {chip_name} "
                f"(dimensions{'+ pairs' if has_pair else ''}{'+ system' if has_system else ''})"
            ),
            implementation=impl,
            evidence_strength=evidence_strength,
            applicable_categories=["all"],
        ))

    return patterns


def _extract_loop_design_patterns(
    chip_path: Path,
    chip_name: str,
    evidence_strength: float,
    project: dict[str, Any] | None,
) -> list[TransferPattern]:
    """Extract loop design patterns from project.json."""
    patterns: list[TransferPattern] = []
    if project is None:
        return patterns

    guardrails = project.get("guardrails", {})
    if guardrails:
        impl: dict[str, Any] = {}
        for key in (
            "max_loop_iterations",
            "consecutive_discard_limit",
            "near_best_tolerance",
            "require_clean_git_for_self_edit",
            "require_human_approval_for_self_edit",
            "blocked_command_fragments",
        ):
            if key in guardrails:
                impl[key] = guardrails[key]

        if impl:
            patterns.append(TransferPattern(
                pattern_id=_pattern_id(chip_name, "loop_design", "guardrails"),
                source_chip=chip_name,
                pattern_type="loop_design",
                description=f"Loop guardrails from {chip_name}: {', '.join(impl.keys())}",
                implementation=impl,
                evidence_strength=evidence_strength,
                applicable_categories=["all"],
            ))

    # Agent cooldown / retirement patterns (startup-yc specific but universal)
    all_text = _collect_text(chip_path, ["src/**/*.py", "docs/**/*.md"])
    if "cooldown" in all_text or "retirement" in all_text:
        patterns.append(TransferPattern(
            pattern_id=_pattern_id(chip_name, "loop_design", "cooldown"),
            source_chip=chip_name,
            pattern_type="loop_design",
            description=f"Agent cooldown / anchor retirement pattern from {chip_name}",
            implementation={
                "has_cooldown": "cooldown" in all_text,
                "has_retirement": "retirement" in all_text,
                "pattern": "agent_lifecycle_management",
            },
            evidence_strength=evidence_strength,
            applicable_categories=["all"],
        ))

    # Tri-loop architecture (trading-crypto pattern)
    if "tri-loop" in all_text or ("learning" in all_text and "benchmark" in all_text and "validation" in all_text):
        patterns.append(TransferPattern(
            pattern_id=_pattern_id(chip_name, "loop_design", "tri_loop"),
            source_chip=chip_name,
            pattern_type="loop_design",
            description=f"Tri-loop architecture (learning -> benchmark -> validation) from {chip_name}",
            implementation={
                "loops": ["learning", "benchmark", "validation"],
                "pattern": "tri_loop_architecture",
            },
            evidence_strength=evidence_strength,
            applicable_categories=["all"],
        ))

    return patterns


def _extract_evidence_strategy_patterns(
    chip_path: Path,
    chip_name: str,
    evidence_strength: float,
) -> list[TransferPattern]:
    """Extract evidence lane configuration patterns."""
    patterns: list[TransferPattern] = []
    all_text = _collect_text(chip_path, [
        "src/**/*.py", "docs/**/*.md", "README.md", "obsidian-vault/**/*.md",
    ])

    lanes_found: list[str] = []
    for lane in ("research_grounded", "benchmark_grounded", "exploratory_frontier", "realworld_validated"):
        if lane in all_text or lane.replace("_", "-") in all_text:
            lanes_found.append(lane)

    if len(lanes_found) >= 2:
        patterns.append(TransferPattern(
            pattern_id=_pattern_id(chip_name, "evidence_strategy", "lanes"),
            source_chip=chip_name,
            pattern_type="evidence_strategy",
            description=f"Evidence lane separation with {len(lanes_found)} lanes from {chip_name}",
            implementation={
                "lanes": lanes_found,
                "lane_count": len(lanes_found),
            },
            evidence_strength=evidence_strength,
            applicable_categories=["all"],
        ))

    # Source registry pattern
    if "source" in all_text and ("registry" in all_text or "map" in all_text):
        patterns.append(TransferPattern(
            pattern_id=_pattern_id(chip_name, "evidence_strategy", "source_registry"),
            source_chip=chip_name,
            pattern_type="evidence_strategy",
            description=f"Source registry documentation pattern from {chip_name}",
            implementation={
                "pattern": "source_registry",
                "has_source_docs": True,
            },
            evidence_strength=evidence_strength,
            applicable_categories=["all"],
        ))

    # Walk-forward validation (trading-crypto specific, universal)
    if "walk-forward" in all_text or "walk_forward" in all_text:
        patterns.append(TransferPattern(
            pattern_id=_pattern_id(chip_name, "evidence_strategy", "walk_forward"),
            source_chip=chip_name,
            pattern_type="evidence_strategy",
            description=f"Walk-forward validation split from {chip_name}",
            implementation={
                "pattern": "walk_forward_validation",
                "description": "Train/test split that advances over time to prevent look-ahead bias",
            },
            evidence_strength=evidence_strength,
            applicable_categories=["all"],
        ))

    # Category-specific patterns
    category = _chip_category(chip_name)
    if category == "finance":
        if "regime" in all_text:
            patterns.append(TransferPattern(
                pattern_id=_pattern_id(chip_name, "evidence_strategy", "regime"),
                source_chip=chip_name,
                pattern_type="evidence_strategy",
                description=f"Regime classification pattern from {chip_name}",
                implementation={"pattern": "regime_classification"},
                evidence_strength=evidence_strength,
                applicable_categories=["finance"],
            ))
        if "paper" in all_text and ("trade" in all_text or "gate" in all_text):
            patterns.append(TransferPattern(
                pattern_id=_pattern_id(chip_name, "evidence_strategy", "paper_trade"),
                source_chip=chip_name,
                pattern_type="evidence_strategy",
                description=f"Paper-trade gate pattern from {chip_name}",
                implementation={"pattern": "paper_trade_gate"},
                evidence_strength=evidence_strength,
                applicable_categories=["finance"],
            ))

    if category == "creative":
        if "reference" in all_text and "vault" in all_text:
            patterns.append(TransferPattern(
                pattern_id=_pattern_id(chip_name, "evidence_strategy", "ref_vault"),
                source_chip=chip_name,
                pattern_type="evidence_strategy",
                description=f"Reference vault organization from {chip_name}",
                implementation={"pattern": "reference_vault"},
                evidence_strength=evidence_strength,
                applicable_categories=["creative"],
            ))

    if category == "business":
        if "factor" in all_text and "catalog" in all_text:
            patterns.append(TransferPattern(
                pattern_id=_pattern_id(chip_name, "evidence_strategy", "factor_catalog"),
                source_chip=chip_name,
                pattern_type="evidence_strategy",
                description=f"Factor catalog pattern from {chip_name}",
                implementation={"pattern": "factor_catalog"},
                evidence_strength=evidence_strength,
                applicable_categories=["business"],
            ))
        if "doctrine" in all_text and "review" in all_text:
            patterns.append(TransferPattern(
                pattern_id=_pattern_id(chip_name, "evidence_strategy", "doctrine_review"),
                source_chip=chip_name,
                pattern_type="evidence_strategy",
                description=f"Doctrine review cadence from {chip_name}",
                implementation={"pattern": "doctrine_review_cadence"},
                evidence_strength=evidence_strength,
                applicable_categories=["business"],
            ))

    if category == "gaming":
        if "balance" in all_text and "simulation" in all_text:
            patterns.append(TransferPattern(
                pattern_id=_pattern_id(chip_name, "evidence_strategy", "balance_sim"),
                source_chip=chip_name,
                pattern_type="evidence_strategy",
                description=f"Balance simulation pattern from {chip_name}",
                implementation={"pattern": "balance_simulation"},
                evidence_strength=evidence_strength,
                applicable_categories=["gaming"],
            ))
        if "playtest" in all_text:
            patterns.append(TransferPattern(
                pattern_id=_pattern_id(chip_name, "evidence_strategy", "playtest"),
                source_chip=chip_name,
                pattern_type="evidence_strategy",
                description=f"Playtest feedback loop from {chip_name}",
                implementation={"pattern": "playtest_feedback"},
                evidence_strength=evidence_strength,
                applicable_categories=["gaming"],
            ))

    if category == "science":
        if "brier" in all_text:
            patterns.append(TransferPattern(
                pattern_id=_pattern_id(chip_name, "evidence_strategy", "brier"),
                source_chip=chip_name,
                pattern_type="evidence_strategy",
                description=f"Brier calibration scoring from {chip_name}",
                implementation={"pattern": "brier_calibration"},
                evidence_strength=evidence_strength,
                applicable_categories=["science"],
            ))

    if category == "technology":
        if "benchmark" in all_text and ("suite" in all_text or "test" in all_text):
            patterns.append(TransferPattern(
                pattern_id=_pattern_id(chip_name, "evidence_strategy", "bench_suite"),
                source_chip=chip_name,
                pattern_type="evidence_strategy",
                description=f"Benchmark suite pattern from {chip_name}",
                implementation={"pattern": "benchmark_suite"},
                evidence_strength=evidence_strength,
                applicable_categories=["technology"],
            ))

    return patterns


def _extract_promotion_gate_patterns(
    chip_path: Path,
    chip_name: str,
    evidence_strength: float,
    project: dict[str, Any] | None,
) -> list[TransferPattern]:
    """Extract promotion threshold / gate configuration."""
    patterns: list[TransferPattern] = []
    all_text = _collect_text(chip_path, ["src/**/*.py", "docs/**/*.md"])

    # Look for promotion thresholds in code or config
    if "promot" in all_text or "graduat" in all_text or "threshold" in all_text:
        impl: dict[str, Any] = {"pattern": "promotion_gate"}

        if project:
            # Extract threshold-like config values
            guardrails = project.get("guardrails", {})
            if "near_best_tolerance" in guardrails:
                impl["near_best_tolerance"] = guardrails["near_best_tolerance"]

        patterns.append(TransferPattern(
            pattern_id=_pattern_id(chip_name, "promotion_gate", "threshold"),
            source_chip=chip_name,
            pattern_type="promotion_gate",
            description=f"Promotion gate / graduation threshold from {chip_name}",
            implementation=impl,
            evidence_strength=evidence_strength,
            applicable_categories=["all"],
        ))

    # Owner review decisions (web-designer pattern)
    if "owner" in all_text and "review" in all_text:
        patterns.append(TransferPattern(
            pattern_id=_pattern_id(chip_name, "promotion_gate", "owner_review"),
            source_chip=chip_name,
            pattern_type="promotion_gate",
            description=f"Owner review decision gate from {chip_name}",
            implementation={"pattern": "owner_review_gate"},
            evidence_strength=evidence_strength,
            applicable_categories=["all"],
        ))

    return patterns


def _extract_contradiction_detection_patterns(
    chip_path: Path,
    chip_name: str,
    evidence_strength: float,
) -> list[TransferPattern]:
    """Extract contradiction detection patterns."""
    patterns: list[TransferPattern] = []
    all_text = _collect_text(chip_path, ["src/**/*.py", "docs/**/*.md"])

    if "contradiction" in all_text:
        has_tags = "tag" in all_text and "contradiction" in all_text
        patterns.append(TransferPattern(
            pattern_id=_pattern_id(chip_name, "contradiction_detection", "base"),
            source_chip=chip_name,
            pattern_type="contradiction_detection",
            description=f"Contradiction detection {'with tagging ' if has_tags else ''}from {chip_name}",
            implementation={
                "pattern": "contradiction_detection",
                "has_tags": has_tags,
            },
            evidence_strength=evidence_strength,
            applicable_categories=["all"],
        ))

    return patterns


def _extract_research_pipeline_patterns(
    chip_path: Path,
    chip_name: str,
    evidence_strength: float,
    project: dict[str, Any] | None,
    manifest: dict[str, Any] | None,
) -> list[TransferPattern]:
    """Extract research pipeline configuration."""
    patterns: list[TransferPattern] = []

    # Research areas from manifest frontier
    if manifest:
        frontier = manifest.get("frontier", {})
        mutations = frontier.get("allowed_mutations", {})
        if mutations:
            impl: dict[str, Any] = {
                "mutation_axes": list(mutations.keys()),
                "axis_count": len(mutations),
            }
            # Extract research-focus-like axes
            for key in ("research_focus", "research_area", "focus"):
                if key in mutations:
                    impl["research_areas"] = mutations[key]
                    break

            patterns.append(TransferPattern(
                pattern_id=_pattern_id(chip_name, "research_pipeline", "mutations"),
                source_chip=chip_name,
                pattern_type="research_pipeline",
                description=f"Research pipeline with {len(mutations)} mutation axes from {chip_name}",
                implementation=impl,
                evidence_strength=evidence_strength,
                applicable_categories=["all"],
            ))

    # Candidate trials structure
    if project:
        trials = project.get("candidate_trials", [])
        if len(trials) >= 3:
            patterns.append(TransferPattern(
                pattern_id=_pattern_id(chip_name, "research_pipeline", "trials"),
                source_chip=chip_name,
                pattern_type="research_pipeline",
                description=f"Candidate trial structure with {len(trials)} trials from {chip_name}",
                implementation={
                    "trial_count": len(trials),
                    "has_baseline": any(
                        t.get("mutations", None) == {} or t.get("mutations") is None
                        for t in trials
                    ),
                },
                evidence_strength=evidence_strength,
                applicable_categories=["all"],
            ))

    return patterns


def _extract_watchtower_design_patterns(
    chip_path: Path,
    chip_name: str,
    evidence_strength: float,
) -> list[TransferPattern]:
    """Extract watchtower / Obsidian page design patterns."""
    patterns: list[TransferPattern] = []

    vault_dir = chip_path / "obsidian-vault"
    if vault_dir.exists():
        page_names = [p.stem for p in vault_dir.rglob("*.md")]
        if page_names:
            patterns.append(TransferPattern(
                pattern_id=_pattern_id(chip_name, "watchtower_design", "vault"),
                source_chip=chip_name,
                pattern_type="watchtower_design",
                description=f"Obsidian vault with {len(page_names)} pages from {chip_name}",
                implementation={
                    "page_count": len(page_names),
                    "page_names": page_names[:20],  # cap for sanity
                },
                evidence_strength=evidence_strength,
                applicable_categories=["all"],
            ))

    return patterns


# ---------------------------------------------------------------------------
# Core extraction
# ---------------------------------------------------------------------------

def extract_patterns(chip_path: Path) -> list[TransferPattern]:
    """Analyze a chip directory and extract all transferable patterns.

    Reads spark-chip.json, spark-researcher.project.json, src/, and docs/
    to identify proven patterns in scoring, loop design, evidence strategy,
    promotion gates, contradiction detection, research pipelines, and
    watchtower design.

    Each pattern's evidence_strength is based on the chip's rubric score
    (score / 100, clamped to [0, 1]).
    """
    chip_path = Path(chip_path)
    if not chip_path.exists():
        return []

    chip_name = chip_path.name

    # Score the chip for evidence strength
    score_result = score_chip(chip_path)
    total_score = score_result.get("total_score", 0)
    evidence_strength = max(0.0, min(1.0, total_score / 100.0))

    # Read config files
    manifest = _read_json(chip_path / "spark-chip.json")
    project = _read_json(chip_path / "spark-researcher.project.json")

    # Extract all pattern types
    all_patterns: list[TransferPattern] = []
    all_patterns.extend(
        _extract_scoring_model_patterns(chip_path, chip_name, evidence_strength)
    )
    all_patterns.extend(
        _extract_loop_design_patterns(chip_path, chip_name, evidence_strength, project)
    )
    all_patterns.extend(
        _extract_evidence_strategy_patterns(chip_path, chip_name, evidence_strength)
    )
    all_patterns.extend(
        _extract_promotion_gate_patterns(chip_path, chip_name, evidence_strength, project)
    )
    all_patterns.extend(
        _extract_contradiction_detection_patterns(chip_path, chip_name, evidence_strength)
    )
    all_patterns.extend(
        _extract_research_pipeline_patterns(
            chip_path, chip_name, evidence_strength, project, manifest,
        )
    )
    all_patterns.extend(
        _extract_watchtower_design_patterns(chip_path, chip_name, evidence_strength)
    )

    return all_patterns


# ---------------------------------------------------------------------------
# Portfolio extraction
# ---------------------------------------------------------------------------

def extract_portfolio_patterns(chip_search_dir: Path) -> TransferRegistry:
    """Scan all chips in a directory, extract patterns from mature ones.

    Only extracts from chips with a rubric score >= 70 to ensure quality.
    Returns a complete TransferRegistry.
    """
    chip_search_dir = Path(chip_search_dir)
    registry = TransferRegistry(
        last_extraction=datetime.now(timezone.utc).isoformat(),
    )

    if not chip_search_dir.exists():
        return registry

    for entry in sorted(chip_search_dir.iterdir()):
        if not entry.is_dir():
            continue
        if not entry.name.startswith("domain-chip-"):
            continue

        # Only extract from mature chips
        result = score_chip(entry)
        if result.get("total_score", 0) < 70:
            continue

        chip_patterns = extract_patterns(entry)
        registry.patterns.extend(chip_patterns)

    return registry


# ---------------------------------------------------------------------------
# Pattern matching
# ---------------------------------------------------------------------------

def find_applicable_patterns(
    target_chip_path: Path,
    registry: TransferRegistry,
) -> list[TransferPattern]:
    """Find patterns from the registry applicable to the target chip.

    Filters by:
    - Category match (pattern applies to target's category or is universal)
    - Not already applied (pattern_id not in target's transfer history)
    - Addresses a gap (cross-references with score_chip results)

    Returns patterns sorted by expected impact (evidence_strength * points_recoverable).
    """
    target_chip_path = Path(target_chip_path)
    target_name = target_chip_path.name
    target_category = _chip_category(target_name)

    # Score target to find gaps
    target_result = score_chip(target_chip_path)
    failed_checks = set(target_result.get("failed_checks", []))

    # Build set of already-applied pattern ids for this target
    already_applied: set[str] = set()
    for hist in registry.transfer_history:
        if hist.target_chip == target_name:
            already_applied.update(hist.patterns_applied)

    # Map pattern_type to the rubric dimensions they can help with
    type_to_dimensions: dict[str, set[str]] = {
        "scoring_model": {
            "scoring_logic", "primary_metric", "multiple_metrics",
        },
        "loop_design": {
            "guardrails_set", "self_edit_config",
        },
        "evidence_strategy": {
            "has_research_grounded", "has_benchmark_grounded",
            "has_exploratory_frontier", "has_realworld_validated",
            "source_registry",
        },
        "promotion_gate": {
            "guardrails_set",
        },
        "contradiction_detection": {
            "scoring_logic",
        },
        "research_pipeline": {
            "candidate_trials", "baseline_trial", "primary_metric",
            "commands_defined", "project_json_valid",
        },
        "watchtower_design": {
            "watchtower_pages", "obsidian_vault",
        },
    }

    # Build lookup for points per check
    from ..quality_rubric import RUBRIC_DIMENSIONS
    check_to_points: dict[str, int] = {}
    for dim in RUBRIC_DIMENSIONS:
        for check in dim["checks"]:
            check_to_points[check["id"]] = check["points"]

    applicable: list[tuple[float, TransferPattern]] = []

    for pattern in registry.patterns:
        # Skip patterns from the target itself
        if pattern.source_chip == target_name:
            continue

        # Skip already-applied patterns
        if pattern.pattern_id in already_applied:
            continue

        # Category filter
        categories = pattern.applicable_categories
        if "all" not in categories and target_category not in categories:
            continue

        # Check if this pattern addresses any gaps
        addressable_checks = type_to_dimensions.get(pattern.pattern_type, set())
        gap_overlap = addressable_checks & failed_checks
        points_recoverable = sum(check_to_points.get(c, 0) for c in gap_overlap)

        # Even if no direct gap overlap, universal patterns still get a baseline
        if not gap_overlap and "all" not in categories:
            continue

        # Expected impact = evidence_strength * recoverable points
        # Give universal patterns a minimum baseline of 1 point
        effective_points = max(points_recoverable, 1)
        expected_impact = pattern.evidence_strength * effective_points

        applicable.append((expected_impact, pattern))

    # Sort by expected impact descending
    applicable.sort(key=lambda pair: -pair[0])
    return [p for _, p in applicable]


# ---------------------------------------------------------------------------
# Pattern application
# ---------------------------------------------------------------------------

def _apply_scoring_model(target_chip_path: Path, pattern: TransferPattern) -> bool:
    """Apply a scoring model pattern: add pair bonus / system bonus templates."""
    src_dir = target_chip_path / "src"
    src_dir.mkdir(parents=True, exist_ok=True)

    # Find existing evaluate.py or create one
    eval_files = list(src_dir.rglob("evaluate.py"))
    if not eval_files:
        # Create a minimal evaluate.py with scoring model
        _ensure_file(
            src_dir / "evaluate.py",
            '"""Evaluation scoring logic."""\n\n'
            "# Scoring model transferred from: "
            f"{pattern.source_chip}\n"
            "BASE_SCORE = 50\n\n"
            "DIMENSIONS: dict[str, dict[str, int]] = {\n"
            '    # Add dimension scoring here\n'
            "}\n\n"
            "PAIR_BONUSES: dict[tuple, int] = {\n"
            "    # Add pair synergies as domain knowledge grows\n"
            "}\n\n"
            "SYSTEM_BONUSES: list = [\n"
            "    # Add system-wide bonuses/penalties\n"
            "]\n\n\n"
            "def score(mutations: dict) -> float:\n"
            '    """Score mutations using additive model."""\n'
            "    total = BASE_SCORE\n"
            "    for dim, values in DIMENSIONS.items():\n"
            "        val = mutations.get(dim)\n"
            "        if val and val in values:\n"
            "            total += values[val]\n"
            "    return max(0, min(100, total))\n",
        )
        return True

    # If evaluate.py exists, add a comment noting the transfer, but never delete
    eval_file = eval_files[0]
    try:
        existing = eval_file.read_text(encoding="utf-8")
    except OSError:
        return False

    transfer_marker = f"# Transfer: scoring_model from {pattern.source_chip}"
    if transfer_marker in existing:
        return True  # Already applied

    # Add pair bonus / system bonus templates if missing
    additions: list[str] = [f"\n{transfer_marker}\n"]

    if pattern.implementation.get("has_pair_bonuses") and "pair_bonus" not in existing.lower():
        additions.append(
            "# PAIR_BONUSES template (from transfer):\n"
            "# PAIR_BONUSES = {\n"
            '#     (("dim_a", "val_a"), ("dim_b", "val_b")): bonus_points,\n'
            "# }\n"
        )

    if pattern.implementation.get("has_system_bonuses") and "system_bonus" not in existing.lower():
        additions.append(
            "# SYSTEM_BONUSES template (from transfer):\n"
            "# SYSTEM_BONUSES = [\n"
            '#     {"label": "bonus_name", "bonus": 5, "condition": lambda m: True},\n'
            "# ]\n"
        )

    if len(additions) > 1:  # More than just the marker
        new_content = existing + "\n" + "\n".join(additions)
        eval_file.write_text(new_content, encoding="utf-8")

    return True


def _apply_loop_design(target_chip_path: Path, pattern: TransferPattern) -> bool:
    """Apply loop design pattern: update project.json with loop configuration."""
    project_path = target_chip_path / "spark-researcher.project.json"
    project = _read_json(project_path)
    if project is None:
        project = {"project_name": target_chip_path.name}

    guardrails = project.get("guardrails", {})
    changed = False

    impl = pattern.implementation

    # Add guardrail values that are missing
    for key in (
        "max_loop_iterations",
        "consecutive_discard_limit",
        "near_best_tolerance",
        "require_clean_git_for_self_edit",
        "require_human_approval_for_self_edit",
    ):
        if key in impl and key not in guardrails:
            guardrails[key] = impl[key]
            changed = True

    # Merge blocked fragments (additive only)
    if "blocked_command_fragments" in impl:
        existing_fragments = set(guardrails.get("blocked_command_fragments", []))
        new_fragments = set(impl["blocked_command_fragments"])
        merged = sorted(existing_fragments | new_fragments)
        if set(merged) != existing_fragments:
            guardrails["blocked_command_fragments"] = merged
            changed = True

    if changed:
        project["guardrails"] = guardrails
        _write_json(project_path, project)

    return True


def _apply_evidence_strategy(target_chip_path: Path, pattern: TransferPattern) -> bool:
    """Apply evidence strategy pattern: add evidence lane docs/config."""
    impl = pattern.implementation
    pat = impl.get("pattern", "")

    # Source registry pattern
    if pat == "source_registry":
        docs_dir = target_chip_path / "docs"
        docs_dir.mkdir(parents=True, exist_ok=True)
        domain = target_chip_path.name.replace("domain-chip-", "")
        _ensure_file(
            docs_dir / "source_registry.md",
            f"# Source Registry\n\n"
            f"Primary source map for the **{domain}** domain.\n"
            f"(Pattern transferred from {pattern.source_chip})\n\n"
            f"## Source List\n\n"
            f"| Source | Type | URL | Notes |\n"
            f"|--------|------|-----|-------|\n"
            f"| (add sources here) | research | - | - |\n",
        )
        return True

    # Evidence lanes pattern
    if "lanes" in impl:
        # Add evidence lane references to docs
        docs_dir = target_chip_path / "docs"
        docs_dir.mkdir(parents=True, exist_ok=True)
        lanes = impl.get("lanes", [])
        lane_text = "\n".join(f"- **{lane}**" for lane in lanes)
        _ensure_file(
            docs_dir / "evidence_lanes.md",
            f"# Evidence Lanes\n\n"
            f"(Pattern transferred from {pattern.source_chip})\n\n"
            f"## Active Lanes\n\n{lane_text}\n\n"
            f"## Lane Promotion Rules\n\n"
            f"- exploratory_frontier -> research_grounded (when source-backed)\n"
            f"- research_grounded -> benchmark_grounded (when quantitatively validated)\n"
            f"- benchmark_grounded -> realworld_validated (when field-tested)\n",
        )
        return True

    # Walk-forward validation pattern
    if pat == "walk_forward_validation":
        docs_dir = target_chip_path / "docs"
        docs_dir.mkdir(parents=True, exist_ok=True)
        _ensure_file(
            docs_dir / "walk_forward_validation.md",
            f"# Walk-Forward Validation\n\n"
            f"(Pattern transferred from {pattern.source_chip})\n\n"
            f"## Methodology\n\n"
            f"Use a sliding window approach to validate predictions:\n"
            f"1. Train on historical window\n"
            f"2. Predict next period\n"
            f"3. Slide window forward\n"
            f"4. Aggregate prediction accuracy\n\n"
            f"This prevents look-ahead bias in evaluation.\n",
        )
        return True

    # Category-specific patterns -- add as docs
    if pat in (
        "regime_classification", "paper_trade_gate", "reference_vault",
        "factor_catalog", "doctrine_review_cadence", "balance_simulation",
        "playtest_feedback", "brier_calibration", "benchmark_suite",
    ):
        docs_dir = target_chip_path / "docs"
        docs_dir.mkdir(parents=True, exist_ok=True)
        _ensure_file(
            docs_dir / f"{pat}.md",
            f"# {pat.replace('_', ' ').title()}\n\n"
            f"(Pattern transferred from {pattern.source_chip})\n\n"
            f"## Description\n\n"
            f"{pattern.description}\n\n"
            f"## Implementation Notes\n\n"
            f"TODO: Adapt this pattern for this chip's domain.\n",
        )
        return True

    return True


def _apply_promotion_gate(target_chip_path: Path, pattern: TransferPattern) -> bool:
    """Apply promotion gate pattern: add promotion threshold to project.json."""
    project_path = target_chip_path / "spark-researcher.project.json"
    project = _read_json(project_path)
    if project is None:
        project = {"project_name": target_chip_path.name}

    impl = pattern.implementation
    changed = False

    # Add near_best_tolerance if missing
    guardrails = project.get("guardrails", {})
    if "near_best_tolerance" in impl:
        if _ensure_key(guardrails, "near_best_tolerance", impl["near_best_tolerance"]):
            changed = True

    # Add promotion_gate section if missing
    if _ensure_key(project, "promotion_gate", {
        "min_score": 60,
        "require_benchmark": True,
        "require_human_review": True,
        "transferred_from": pattern.source_chip,
    }):
        changed = True

    if changed:
        project["guardrails"] = guardrails
        _write_json(project_path, project)

    return True


def _apply_contradiction_detection(target_chip_path: Path, pattern: TransferPattern) -> bool:
    """Apply contradiction detection: add stubs to src/."""
    src_dir = target_chip_path / "src"
    src_dir.mkdir(parents=True, exist_ok=True)

    _ensure_file(
        src_dir / "contradiction_detector.py",
        f'"""Contradiction detection stub.\n\n'
        f"Pattern transferred from {pattern.source_chip}.\n"
        f'"""\n\n'
        f"from __future__ import annotations\n\n"
        f"from typing import Any\n\n\n"
        f"# Contradiction tags for scoring penalties\n"
        f"CONTRADICTION_TAGS: list[dict[str, Any]] = [\n"
        f"    # Example:\n"
        f'    # {{"tag": "conflicting_strategy", "dim_a": "axis1", "val_a": "x",\n'
        f'    #  "dim_b": "axis2", "val_b": "y", "penalty": -5}},\n'
        f"]\n\n\n"
        f"def detect_contradictions(mutations: dict[str, Any]) -> list[dict[str, Any]]:\n"
        f'    """Detect contradictions in a mutation set.\n\n'
        f"    Returns list of triggered contradiction dicts.\n"
        f'    """\n'
        f"    triggered = []\n"
        f"    for tag in CONTRADICTION_TAGS:\n"
        f"        dim_a = tag.get('dim_a', '')\n"
        f"        val_a = tag.get('val_a', '')\n"
        f"        dim_b = tag.get('dim_b', '')\n"
        f"        val_b = tag.get('val_b', '')\n"
        f"        if mutations.get(dim_a) == val_a and mutations.get(dim_b) == val_b:\n"
        f"            triggered.append(tag)\n"
        f"    return triggered\n",
    )
    return True


def _apply_research_pipeline(target_chip_path: Path, pattern: TransferPattern) -> bool:
    """Apply research pipeline: add research config to project.json."""
    project_path = target_chip_path / "spark-researcher.project.json"
    project = _read_json(project_path)
    if project is None:
        project = {"project_name": target_chip_path.name}

    impl = pattern.implementation
    changed = False

    # Add research areas if present
    if "research_areas" in impl:
        if _ensure_key(project, "research_areas", impl["research_areas"]):
            changed = True

    # Add baseline trial if missing
    if impl.get("has_baseline"):
        trials = project.get("candidate_trials", [])
        has_baseline = any(
            t.get("mutations", None) == {} or t.get("mutations") is None
            for t in trials
        )
        if not has_baseline:
            trials.insert(0, {
                "candidate_id": "global-baseline",
                "candidate_summary": "Baseline (no mutations)",
                "mutations": {},
            })
            project["candidate_trials"] = trials
            changed = True

    # Ensure minimum 3 trials
    trials = project.get("candidate_trials", [])
    while len(trials) < 3:
        trials.append({
            "candidate_id": f"variant-{len(trials)}",
            "candidate_summary": f"Variant {len(trials)}",
            "mutations": {},
        })
        changed = True
    if changed:
        project["candidate_trials"] = trials

    if changed:
        _write_json(project_path, project)

    return True


def _apply_watchtower_design(target_chip_path: Path, pattern: TransferPattern) -> bool:
    """Apply watchtower design: add Obsidian vault page templates."""
    vault_dir = target_chip_path / "obsidian-vault"
    vault_dir.mkdir(parents=True, exist_ok=True)

    domain = target_chip_path.name.replace("domain-chip-", "")

    _ensure_file(
        vault_dir / "index.md",
        f"# {domain} Knowledge Vault\n\n"
        f"Watchtower-generated pages for the {domain} domain.\n"
        f"(Pattern transferred from {pattern.source_chip})\n\n"
        f"## Pages\n\n"
        f"- [[index]] -- This page\n"
        f"- [[Leaderboard]] -- Top scoring candidates\n"
        f"- [[Research Log]] -- Evidence gathering history\n",
    )

    _ensure_file(
        vault_dir / "Leaderboard.md",
        f"# Leaderboard\n\n"
        f"## Top Candidates\n\n"
        f"| Rank | Candidate | Score | Evidence Lane |\n"
        f"|------|-----------|-------|---------------|\n"
        f"| 1    | Baseline  | 50    | benchmark_grounded |\n",
    )

    return True


# Dispatch table for pattern application
_PATTERN_APPLIERS: dict[str, Any] = {
    "scoring_model": _apply_scoring_model,
    "loop_design": _apply_loop_design,
    "evidence_strategy": _apply_evidence_strategy,
    "promotion_gate": _apply_promotion_gate,
    "contradiction_detection": _apply_contradiction_detection,
    "research_pipeline": _apply_research_pipeline,
    "watchtower_design": _apply_watchtower_design,
}


def apply_pattern(target_chip_path: Path, pattern: TransferPattern) -> bool:
    """Apply a specific pattern to a target chip.

    Dispatches to the appropriate applier based on pattern_type.
    NEVER deletes existing content -- only adds or enhances.

    Returns True on success, False on failure.
    """
    target_chip_path = Path(target_chip_path)
    applier = _PATTERN_APPLIERS.get(pattern.pattern_type)
    if applier is None:
        return False

    try:
        result = applier(target_chip_path, pattern)
        pattern.times_applied += 1
        if result:
            pattern.times_successful += 1
        return result
    except Exception:
        pattern.times_applied += 1
        return False


# ---------------------------------------------------------------------------
# Full transfer pipelines
# ---------------------------------------------------------------------------

def transfer_intelligence(
    source_chip: Path,
    target_chip: Path,
) -> TransferResult:
    """Full transfer pipeline between two chips.

    1. Extract patterns from source chip
    2. Find applicable patterns for target
    3. Apply all applicable patterns
    4. Score before / after
    5. Return results

    Returns a TransferResult with full details.
    """
    source_chip = Path(source_chip)
    target_chip = Path(target_chip)
    target_name = target_chip.name

    # Score before
    before_result = score_chip(target_chip)
    score_before = before_result.get("total_score", 0)

    # Build a mini-registry from the source
    source_patterns = extract_patterns(source_chip)
    registry = TransferRegistry(patterns=source_patterns)

    # Find applicable patterns
    applicable = find_applicable_patterns(target_chip, registry)

    # Apply patterns
    applied_ids: list[str] = []
    successful: list[str] = []
    failed: list[str] = []

    for pattern in applicable:
        ok = apply_pattern(target_chip, pattern)
        applied_ids.append(pattern.pattern_id)
        if ok:
            successful.append(pattern.pattern_id)
        else:
            failed.append(pattern.pattern_id)

    # Score after
    after_result = score_chip(target_chip)
    score_after = after_result.get("total_score", 0)

    # Generate recommendations for remaining gaps
    remaining_failed = after_result.get("failed_checks", [])
    recommendations: list[str] = []
    for check_id in remaining_failed[:5]:  # Top 5 remaining gaps
        recommendations.append(f"Manual fix needed: {check_id}")

    result = TransferResult(
        target_chip=target_name,
        patterns_applied=applied_ids,
        score_before=score_before,
        score_after=score_after,
        score_delta=score_after - score_before,
        successful_transfers=successful,
        failed_transfers=failed,
        recommendations=recommendations,
    )

    return result


def portfolio_transfer(
    chip_search_dir: Path,
    target_score: int = 70,
) -> list[TransferResult]:
    """Run transfer across the entire portfolio.

    1. Extract patterns from the best chips (score >= target_score)
    2. Apply to the weakest chips (score < target_score)
    3. Report results for each target

    Returns a list of TransferResult, one per target chip.
    """
    chip_search_dir = Path(chip_search_dir)
    results: list[TransferResult] = []

    if not chip_search_dir.exists():
        return results

    # Discover all chips and score them
    chip_scores: list[tuple[Path, int]] = []
    for entry in sorted(chip_search_dir.iterdir()):
        if not entry.is_dir():
            continue
        if not entry.name.startswith("domain-chip-"):
            continue
        result = score_chip(entry)
        chip_scores.append((entry, result.get("total_score", 0)))

    # Build registry from mature chips
    registry = TransferRegistry(
        last_extraction=datetime.now(timezone.utc).isoformat(),
    )
    for chip_path, score in chip_scores:
        if score >= target_score:
            patterns = extract_patterns(chip_path)
            registry.patterns.extend(patterns)

    # Apply to weak chips
    for chip_path, score in chip_scores:
        if score < target_score:
            # Find applicable patterns
            applicable = find_applicable_patterns(chip_path, registry)

            # Score before
            score_before = score

            # Apply
            applied_ids: list[str] = []
            successful: list[str] = []
            failed: list[str] = []

            for pattern in applicable:
                ok = apply_pattern(chip_path, pattern)
                applied_ids.append(pattern.pattern_id)
                if ok:
                    successful.append(pattern.pattern_id)
                else:
                    failed.append(pattern.pattern_id)

            # Score after
            after_result = score_chip(chip_path)
            score_after = after_result.get("total_score", 0)

            remaining_failed = after_result.get("failed_checks", [])
            recommendations = [
                f"Manual fix needed: {c}" for c in remaining_failed[:5]
            ]

            result = TransferResult(
                target_chip=chip_path.name,
                patterns_applied=applied_ids,
                score_before=score_before,
                score_after=score_after,
                score_delta=score_after - score_before,
                successful_transfers=successful,
                failed_transfers=failed,
                recommendations=recommendations,
            )
            results.append(result)

            # Record in registry history
            registry.transfer_history.append(result)

    return results


# ---------------------------------------------------------------------------
# Registry persistence
# ---------------------------------------------------------------------------

def _pattern_to_dict(p: TransferPattern) -> dict[str, Any]:
    """Serialize a TransferPattern to a JSON-compatible dict."""
    return {
        "pattern_id": p.pattern_id,
        "source_chip": p.source_chip,
        "pattern_type": p.pattern_type,
        "description": p.description,
        "implementation": p.implementation,
        "evidence_strength": p.evidence_strength,
        "applicable_categories": p.applicable_categories,
        "times_applied": p.times_applied,
        "times_successful": p.times_successful,
    }


def _pattern_from_dict(d: dict[str, Any]) -> TransferPattern:
    """Deserialize a TransferPattern from a dict."""
    return TransferPattern(
        pattern_id=d["pattern_id"],
        source_chip=d["source_chip"],
        pattern_type=d["pattern_type"],
        description=d["description"],
        implementation=d.get("implementation", {}),
        evidence_strength=d.get("evidence_strength", 0.0),
        applicable_categories=d.get("applicable_categories", ["all"]),
        times_applied=d.get("times_applied", 0),
        times_successful=d.get("times_successful", 0),
    )


def _result_to_dict(r: TransferResult) -> dict[str, Any]:
    """Serialize a TransferResult to a JSON-compatible dict."""
    return {
        "target_chip": r.target_chip,
        "patterns_applied": r.patterns_applied,
        "score_before": r.score_before,
        "score_after": r.score_after,
        "score_delta": r.score_delta,
        "successful_transfers": r.successful_transfers,
        "failed_transfers": r.failed_transfers,
        "recommendations": r.recommendations,
    }


def _result_from_dict(d: dict[str, Any]) -> TransferResult:
    """Deserialize a TransferResult from a dict."""
    return TransferResult(
        target_chip=d["target_chip"],
        patterns_applied=d.get("patterns_applied", []),
        score_before=d.get("score_before", 0),
        score_after=d.get("score_after", 0),
        score_delta=d.get("score_delta", 0),
        successful_transfers=d.get("successful_transfers", []),
        failed_transfers=d.get("failed_transfers", []),
        recommendations=d.get("recommendations", []),
    )


def save_registry(registry: TransferRegistry, path: Path) -> None:
    """Persist the transfer registry as JSON."""
    path = Path(path)
    data = {
        "patterns": [_pattern_to_dict(p) for p in registry.patterns],
        "transfer_history": [_result_to_dict(r) for r in registry.transfer_history],
        "last_extraction": registry.last_extraction,
    }
    _write_json(path, data)


def load_registry(path: Path) -> TransferRegistry:
    """Load a transfer registry from JSON."""
    path = Path(path)
    data = _read_json(path)
    if data is None:
        return TransferRegistry()

    return TransferRegistry(
        patterns=[_pattern_from_dict(p) for p in data.get("patterns", [])],
        transfer_history=[_result_from_dict(r) for r in data.get("transfer_history", [])],
        last_extraction=data.get("last_extraction"),
    )
