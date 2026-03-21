"""V3 deep evaluation -- genuine intelligence measurement.

Scores domain chips on a 100-point scale across 8 dimensions using content
analysis, statistical metrics, and anti-gaming heuristics.  Every checker
returns a continuous score based on *depth*, not file existence.

Zero external dependencies.  All statistical utilities are implemented inline.
"""

from __future__ import annotations

import json
import math
import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class DimensionResult:
    """Result of evaluating a single dimension."""

    name: str
    label: str
    score: float
    max_points: float
    details: dict[str, Any] = field(default_factory=dict)
    depth_level: str = "absent"  # absent | surface | moderate | deep | expert

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "label": self.label,
            "score": self.score,
            "max_points": self.max_points,
            "depth_level": self.depth_level,
            "details": self.details,
        }


@dataclass
class DeepEvalResult:
    """Complete V3 deep evaluation result."""

    total_score: float
    dimensions: list[DimensionResult]
    verdict: str
    rubric_version: str = "3.0"
    gaps: list[str] = field(default_factory=list)
    strengths: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    anti_gaming_flags: list[str] = field(default_factory=list)
    depth_profile: dict[str, str] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "total_score": round(self.total_score, 1),
            "verdict": self.verdict,
            "rubric_version": self.rubric_version,
            "dimensions": [d.as_dict() for d in self.dimensions],
            "gaps": self.gaps,
            "strengths": self.strengths,
            "recommendations": self.recommendations,
            "anti_gaming_flags": self.anti_gaming_flags,
            "depth_profile": self.depth_profile,
        }


# ---------------------------------------------------------------------------
# Utility functions (zero external dependencies)
# ---------------------------------------------------------------------------

def _spearman_rank_correlation(x: list[float], y: list[float]) -> float:
    """Spearman rank correlation without scipy.

    Returns rho in [-1, 1].  Returns 0.0 if fewer than 3 data points.
    """
    n = min(len(x), len(y))
    if n < 3:
        return 0.0

    def _rank(values: list[float]) -> list[float]:
        indexed = sorted(enumerate(values[:n]), key=lambda t: t[1])
        ranks = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j < n - 1 and indexed[j + 1][1] == indexed[j][1]:
                j += 1
            avg_rank = (i + j) / 2.0 + 1.0
            for k in range(i, j + 1):
                ranks[indexed[k][0]] = avg_rank
            i = j + 1
        return ranks

    rx = _rank(x[:n])
    ry = _rank(y[:n])

    d_sq = sum((rx[i] - ry[i]) ** 2 for i in range(n))
    denom = n * (n * n - 1)
    if denom == 0:
        return 0.0
    return 1.0 - (6.0 * d_sq / denom)


def _gini_coefficient(values: list[float]) -> float:
    """Gini coefficient.  0 = perfect equality, 1 = total inequality.

    Returns 0.0 for empty or single-element lists.
    """
    if len(values) <= 1:
        return 0.0
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    total = sum(sorted_vals)
    if total == 0:
        return 0.0
    cumulative = 0.0
    gini_sum = 0.0
    for v in sorted_vals:
        cumulative += v
        gini_sum += cumulative
    return 1.0 - (2.0 * gini_sum) / (n * total) + 1.0 / n


def _jaccard_distance(set_a: set[str], set_b: set[str]) -> float:
    """Jaccard distance: 1 - |intersection| / |union|.

    Higher = more different.  Returns 1.0 if both sets are empty.
    """
    if not set_a and not set_b:
        return 1.0
    union = set_a | set_b
    if not union:
        return 1.0
    return 1.0 - len(set_a & set_b) / len(union)


_CAUSAL_MARKERS = re.compile(
    r"\b(?:because|therefore|leads?\s+to|causes?|results?\s+in|due\s+to|"
    r"enables?|prevents?|when\b.*?\bthen|consequently|hence|thus|"
    r"in\s+order\s+to|so\s+that|as\s+a\s+result|"
    # Domain-specific knowledge indicators
    r"prioritize|optimize|tradeoff|trade-off|"
    r"ensure|require|validate|verify|"
    r"signal|indicator|factor|metric|heuristic|"
    r"improve|degrade|regress|promote|"
    r"iterate|refine|evolve|adapt)\b",
    re.IGNORECASE,
)

_BOUNDARY_MARKERS = re.compile(
    r"\b(?:only\s+when|does\s+not\s+apply|limited\s+to|except|"
    r"boundary|constraint|caveat|however|unless|"
    r"not\s+applicable|should\s+not|must\s+not|"
    r"at\s+most|at\s+least|no\s+more\s+than)\b"
    r"|\d+%|\d+\.\d+",
    re.IGNORECASE,
)

_SPECIFICITY_MARKERS = re.compile(
    r"\d+\.\d+|\d+%|v\d+\.\d+|"
    r"\b(?:run_\w+|candidate_\w+|baseline_\w+)\b|"
    r"\b\d{4}-\d{2}-\d{2}\b",
    re.IGNORECASE,
)

_RESOLUTION_MARKERS = re.compile(
    r"\b(?:resolved?\s+(?:by|via|in|through)|fixed\s+(?:by|in)|"
    r"addressed\s+(?:via|by|in)|root\s+cause|workaround|mitigated|"
    r"corrected|patched|updated\s+to|replaced\s+with)\b",
    re.IGNORECASE,
)

_EXPECTED_HOOK_NAMES = {"evaluate", "suggest", "packets", "watchtower"}


def _causal_density(text: str) -> float:
    """Causal markers per 100 words."""
    words = text.split()
    if not words:
        return 0.0
    matches = _CAUSAL_MARKERS.findall(text)
    return (len(matches) / len(words)) * 100.0


def _boundary_specificity(text: str) -> float:
    """Fraction of non-empty lines containing boundary markers."""
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if not lines:
        return 0.0
    count = sum(1 for l in lines if _BOUNDARY_MARKERS.search(l))
    return count / len(lines)


def _content_density_words(file_path: Path) -> int:
    """Word count ignoring markdown headers and blank lines."""
    try:
        text = file_path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return 0
    words = 0
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        words += len(stripped.split())
    return words


def _manifest_schema_version(manifest: dict[str, Any]) -> str:
    """Return the declared schema version across old and current manifest keys."""
    schema = manifest.get("schema") or manifest.get("schema_version")
    return schema if isinstance(schema, str) else ""


def _manifest_hook_names(manifest: dict[str, Any]) -> set[str]:
    """Extract hook names across legacy and current manifest conventions."""
    present: set[str] = set()

    hooks = manifest.get("hooks", {})
    if isinstance(hooks, dict):
        present.update(name for name in hooks if isinstance(name, str))
    elif isinstance(hooks, list):
        for hook in hooks:
            if isinstance(hook, str):
                present.add(hook)
            elif isinstance(hook, dict):
                name = hook.get("name")
                if isinstance(name, str):
                    present.add(name)

    capabilities = manifest.get("capabilities", [])
    if isinstance(capabilities, list):
        present.update(name for name in capabilities if isinstance(name, str))

    commands = manifest.get("commands", {})
    if isinstance(commands, dict):
        present.update(name for name in commands if isinstance(name, str))

    return present & _EXPECTED_HOOK_NAMES


def _load_all_runs(chip_path: Path) -> list[dict[str, Any]]:
    """Load runs from all known locations, deduplicated by run_id."""
    runs: dict[str, dict[str, Any]] = {}

    # score_history.jsonl
    for candidate in [
        chip_path / "score_history.jsonl",
        chip_path / "artifacts" / "ledger" / "runs.jsonl",
        chip_path / "research" / "meta" / "runs.jsonl",
    ]:
        if not candidate.is_file():
            continue
        try:
            for line in candidate.read_text(encoding="utf-8", errors="ignore").splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    rid = entry.get("run_id", "")
                    if rid and rid not in runs:
                        runs[rid] = entry
                    elif not rid:
                        runs[f"_anon_{len(runs)}"] = entry
                except json.JSONDecodeError:
                    pass
        except OSError:
            pass

    # loop_telemetry.json (array)
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
                    if isinstance(entry, dict):
                        rid = entry.get("run_id", f"_telem_{len(runs)}")
                        if rid not in runs:
                            runs[rid] = entry
        except (json.JSONDecodeError, OSError):
            pass

    return list(runs.values())


def _extract_scores_from_runs(runs: list[dict[str, Any]]) -> list[float]:
    """Extract numeric scores from run entries."""
    scores: list[float] = []
    for run in runs:
        score = run.get("score") or run.get("metric_value") or run.get("total_score")
        if score is not None:
            try:
                scores.append(float(score))
            except (ValueError, TypeError):
                pass
    return scores


def _extract_timestamps(runs: list[dict[str, Any]]) -> list[datetime]:
    """Extract timestamps from runs, sorted chronologically."""
    timestamps: list[datetime] = []
    for run in runs:
        ts = run.get("created_at") or run.get("timestamp")
        if not ts:
            continue
        try:
            if isinstance(ts, str):
                # Try ISO format
                ts = ts.replace("Z", "+00:00")
                dt = datetime.fromisoformat(ts)
                timestamps.append(dt)
        except (ValueError, TypeError):
            pass
    return sorted(timestamps)


def _extract_doctrines(chip_path: Path) -> list[str]:
    """Extract individual doctrine texts from chip_skill.md, beliefs/, doctrines/."""
    doctrines: list[str] = []

    # chip_skill.md -- extract sections between headers
    skill_file = chip_path / "chip_skill.md"
    if skill_file.is_file():
        try:
            text = skill_file.read_text(encoding="utf-8", errors="ignore")
            # Split by headers and take substantial sections
            sections = re.split(r"\n##?\s+", text)
            for section in sections:
                section = section.strip()
                if len(section) > 50:
                    doctrines.append(section)
        except OSError:
            pass

    # docs/beliefs/*.md and docs/doctrines/*.md
    for subdir in ["docs/beliefs", "docs/doctrines", "beliefs", "doctrines"]:
        beliefs_dir = chip_path / subdir
        if not beliefs_dir.is_dir():
            continue
        for md in beliefs_dir.glob("*.md"):
            if md.name.startswith("INDEX") or md.name.startswith("README"):
                continue
            try:
                text = md.read_text(encoding="utf-8", errors="ignore").strip()
                if len(text) > 50:
                    doctrines.append(text)
            except OSError:
                pass

    return doctrines


def _parse_contradictions(chip_path: Path) -> tuple[list[str], str]:
    """Parse contradictions from CONTRADICTIONS.md.

    Returns (list of individual contradiction entries, full text).
    """
    entries: list[str] = []
    full_text = ""

    for candidate in [
        chip_path / "CONTRADICTIONS.md",
        chip_path / "docs" / "beliefs" / "CONTRADICTIONS.md",
    ]:
        if not candidate.is_file():
            continue
        try:
            full_text = candidate.read_text(encoding="utf-8", errors="ignore")
            # Extract bullet-pointed entries
            for line in full_text.splitlines():
                stripped = line.strip()
                if stripped.startswith("- **") or stripped.startswith("- "):
                    entries.append(stripped)
            break
        except OSError:
            pass

    return entries, full_text


def _depth_level(score: float, max_points: float) -> str:
    """Map a score to a depth level string."""
    if max_points == 0:
        return "absent"
    ratio = score / max_points
    if ratio <= 0.0:
        return "absent"
    if ratio < 0.25:
        return "surface"
    if ratio < 0.50:
        return "moderate"
    if ratio < 0.75:
        return "deep"
    return "expert"


# ---------------------------------------------------------------------------
# Dimension 1: Manifest & Structure (10 pts)
# ---------------------------------------------------------------------------

def check_manifest_structure(chip_path: Path) -> DimensionResult:
    """Manifest validity + project.json completeness."""
    score = 0.0
    details: dict[str, Any] = {}

    # 5 pts: manifest valid
    manifest_path = chip_path / "spark-chip.json"
    manifest_score = 0.0
    if manifest_path.is_file():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            # Schema check -- accept spark-chip.v1 or presence of io_protocol as v1 signal
            schema = _manifest_schema_version(manifest)
            if schema == "spark-chip.v1" or (
                not schema and manifest.get("io_protocol")
            ):
                manifest_score += 1.0
            if manifest.get("io_protocol") == "spark-hook-io.v1":
                manifest_score += 1.0
            present = _manifest_hook_names(manifest)
            manifest_score += len(present)
            manifest_score = min(manifest_score, 5.0)
            # Frontier with allowed_mutations is a strong signal
            frontier = manifest.get("frontier", {})
            if frontier.get("allowed_mutations") and manifest_score < 5.0:
                manifest_score = min(manifest_score + 1.0, 5.0)
        except (json.JSONDecodeError, OSError):
            pass
    details["manifest_score"] = manifest_score
    score += min(manifest_score, 5.0)

    # 3 pts: project.json completeness
    project_path = chip_path / "spark-researcher.project.json"
    project_score = 0.0
    if project_path.is_file():
        try:
            project = json.loads(project_path.read_text(encoding="utf-8"))
            if project.get("eval_metric"):
                project_score += 1.0
            if len(project.get("metrics", {})) >= 3:
                project_score += 1.0
            if len(project.get("candidate_trials", [])) >= 3:
                project_score += 1.0
        except (json.JSONDecodeError, OSError):
            pass
    details["project_score"] = project_score
    score += min(project_score, 3.0)

    # 2 pts: scoring function in src/
    scoring_re = re.compile(
        r"def\s+(score|evaluate)\s*\(.*?\)\s*.*?:" r"[\s\S]*?" r"return\s+",
        re.MULTILINE,
    )
    src_dir = chip_path / "src"
    has_scoring = False
    if src_dir.is_dir():
        for py in src_dir.rglob("*.py"):
            try:
                content = py.read_text(encoding="utf-8", errors="ignore")
                if scoring_re.search(content):
                    has_scoring = True
                    break
            except OSError:
                pass
    if has_scoring:
        score += 2.0
    details["has_scoring_function"] = has_scoring

    return DimensionResult(
        name="manifest_structure",
        label="Manifest & Structure",
        score=round(score, 1),
        max_points=10.0,
        details=details,
        depth_level=_depth_level(score, 10.0),
    )


# ---------------------------------------------------------------------------
# Dimension 2: Empirical Velocity (18 pts)
# ---------------------------------------------------------------------------

def check_empirical_velocity(chip_path: Path) -> DimensionResult:
    """Run count, trajectory quality, verdict diversity, recency."""
    runs = _load_all_runs(chip_path)
    scores_list = _extract_scores_from_runs(runs)
    timestamps = _extract_timestamps(runs)
    details: dict[str, Any] = {"run_count": len(runs)}

    total = 0.0

    # 5 pts: Run volume (logarithmic tiers)
    n = len(runs)
    if n == 0:
        vol_score = 0.0
    elif n < 10:
        vol_score = 1.0
    elif n < 50:
        vol_score = 2.0
    elif n < 200:
        vol_score = 3.0
    elif n < 500:
        vol_score = 4.0
    else:
        vol_score = 5.0
    total += vol_score
    details["volume_score"] = vol_score

    # 5 pts: Trajectory quality (Spearman rank correlation)
    if len(scores_list) >= 5:
        indices = list(range(len(scores_list)))
        rho = _spearman_rank_correlation(indices, scores_list)
        if rho < 0:
            traj_score = 0.0
        elif rho < 0.3:
            traj_score = 1.0
        elif rho < 0.5:
            traj_score = 2.0
        elif rho < 0.7:
            traj_score = 3.0
        elif rho < 0.85:
            traj_score = 4.0
        else:
            traj_score = 5.0
        details["spearman_rho"] = round(rho, 3)
    elif len(scores_list) >= 2:
        # Not enough for meaningful Spearman; give partial credit if improving
        if scores_list[-1] > scores_list[0]:
            traj_score = 2.0
        else:
            traj_score = 1.0
        details["spearman_rho"] = None
    else:
        traj_score = 0.0
        details["spearman_rho"] = None
    total += traj_score
    details["trajectory_score"] = traj_score

    # 4 pts: Verdict diversity
    verdicts = set()
    for run in runs:
        v = run.get("verdict")
        if v:
            verdicts.add(v)
    verdict_count = len(verdicts)
    verdict_score = min(verdict_count, 4)
    total += float(verdict_score)
    details["unique_verdicts"] = sorted(verdicts)
    details["verdict_score"] = verdict_score

    # 4 pts: Recency
    if timestamps:
        last_run = timestamps[-1]
        if last_run.tzinfo is None:
            last_run = last_run.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        days_ago = (now - last_run).days
        if days_ago > 90:
            recency_score = 0.0
        elif days_ago > 60:
            recency_score = 1.0
        elif days_ago > 30:
            recency_score = 2.0
        elif days_ago > 7:
            recency_score = 3.0
        else:
            recency_score = 4.0
        details["days_since_last_run"] = days_ago
    else:
        recency_score = 0.0
        details["days_since_last_run"] = None
    total += recency_score
    details["recency_score"] = recency_score

    return DimensionResult(
        name="empirical_velocity",
        label="Empirical Velocity",
        score=round(total, 1),
        max_points=18.0,
        details=details,
        depth_level=_depth_level(total, 18.0),
    )


# ---------------------------------------------------------------------------
# Dimension 3: Doctrine Quality (15 pts)
# ---------------------------------------------------------------------------

def check_doctrine_quality(chip_path: Path) -> DimensionResult:
    """Causal density, boundary specificity, uniqueness."""
    doctrines = _extract_doctrines(chip_path)
    details: dict[str, Any] = {"doctrine_count": len(doctrines)}
    total = 0.0

    # Concatenate all doctrines for aggregate analysis
    all_text = "\n\n".join(doctrines)

    # 5 pts: Causal density
    cd = _causal_density(all_text) if all_text else 0.0
    if cd <= 0:
        causal_score = 0.0
    elif cd < 1.0:
        causal_score = 1.0
    elif cd < 2.0:
        causal_score = 2.0
    elif cd < 3.0:
        causal_score = 3.0
    elif cd < 5.0:
        causal_score = 4.0
    else:
        causal_score = 5.0
    total += causal_score
    details["causal_density"] = round(cd, 2)
    details["causal_score"] = causal_score

    # 5 pts: Boundary specificity
    bs = _boundary_specificity(all_text) if all_text else 0.0
    if bs <= 0:
        boundary_score = 0.0
    elif bs < 0.05:
        boundary_score = 1.0
    elif bs < 0.10:
        boundary_score = 2.0
    elif bs < 0.20:
        boundary_score = 3.0
    elif bs < 0.30:
        boundary_score = 4.0
    else:
        boundary_score = 5.0
    total += boundary_score
    details["boundary_specificity"] = round(bs, 3)
    details["boundary_score"] = boundary_score

    # 5 pts: Uniqueness (average Jaccard distance between doctrine pairs)
    if len(doctrines) >= 3:
        # Build word sets (lowercased, no stopwords)
        stopwords = {
            "the", "a", "an", "is", "are", "was", "were", "be", "been",
            "being", "have", "has", "had", "do", "does", "did", "will",
            "would", "could", "should", "may", "might", "shall", "can",
            "of", "in", "to", "for", "with", "on", "at", "from", "by",
            "and", "or", "but", "not", "no", "if", "then", "else",
            "this", "that", "it", "its", "as", "so", "up",
        }
        word_sets = []
        for d in doctrines:
            words = set(w.lower() for w in re.findall(r"\b\w{3,}\b", d)) - stopwords
            if words:
                word_sets.append(words)

        if len(word_sets) >= 3:
            distances: list[float] = []
            for i in range(len(word_sets)):
                for j in range(i + 1, len(word_sets)):
                    distances.append(_jaccard_distance(word_sets[i], word_sets[j]))
            avg_distance = sum(distances) / len(distances) if distances else 0.0

            if avg_distance < 0.3:
                uniqueness_score = 0.0  # too similar
            elif avg_distance < 0.5:
                uniqueness_score = 2.0
            elif avg_distance < 0.7:
                uniqueness_score = 3.0
            else:
                uniqueness_score = 5.0
            details["avg_jaccard_distance"] = round(avg_distance, 3)
        else:
            uniqueness_score = 1.0
            details["avg_jaccard_distance"] = None
    elif len(doctrines) >= 1:
        uniqueness_score = 1.0  # have doctrines, too few to compare
        details["avg_jaccard_distance"] = None
    else:
        uniqueness_score = 0.0
        details["avg_jaccard_distance"] = None
    total += uniqueness_score
    details["uniqueness_score"] = uniqueness_score

    return DimensionResult(
        name="doctrine_quality",
        label="Doctrine Quality",
        score=round(total, 1),
        max_points=15.0,
        details=details,
        depth_level=_depth_level(total, 15.0),
    )


# ---------------------------------------------------------------------------
# Dimension 4: Evidence Integrity (12 pts)
# ---------------------------------------------------------------------------

def check_evidence_integrity(chip_path: Path) -> DimensionResult:
    """Lane balance, content density, structured packets."""
    details: dict[str, Any] = {}
    total = 0.0

    lanes = {
        "research_grounded": chip_path / "research" / "research_grounded",
        "benchmark_grounded": chip_path / "research" / "benchmark_grounded",
        "exploratory_frontier": chip_path / "research" / "exploratory_frontier",
        "realworld_validated": chip_path / "research" / "realworld_validated",
    }

    # Count files and words per lane
    lane_file_counts: list[float] = []
    all_word_counts: list[int] = []
    populated_lanes = 0

    for lane_name, lane_path in lanes.items():
        if not lane_path.is_dir():
            lane_file_counts.append(0)
            continue
        files = [f for f in lane_path.iterdir() if f.is_file() and f.stat().st_size > 50]
        lane_file_counts.append(float(len(files)))
        if files:
            populated_lanes += 1
        for f in files:
            all_word_counts.append(_content_density_words(f))

    details["populated_lanes"] = populated_lanes
    details["lane_file_counts"] = {
        name: int(count) for name, count in zip(lanes.keys(), lane_file_counts)
    }

    # 4 pts: Lane balance (Gini coefficient)
    populated_counts = [c for c in lane_file_counts if c > 0]
    if len(populated_counts) <= 1:
        balance_score = 0.0 if populated_lanes <= 1 else 1.0
    else:
        gini = _gini_coefficient(populated_counts)
        if gini < 0.3:
            balance_score = 4.0
        elif gini < 0.5:
            balance_score = 3.0
        elif gini < 0.7:
            balance_score = 2.0
        else:
            balance_score = 1.0
        details["gini_coefficient"] = round(gini, 3)
    total += balance_score
    details["balance_score"] = balance_score

    # 4 pts: Content density (average words per file)
    if all_word_counts:
        avg_words = sum(all_word_counts) / len(all_word_counts)
    else:
        avg_words = 0
    if avg_words < 50:
        density_score = 0.0
    elif avg_words < 100:
        density_score = 1.0
    elif avg_words < 200:
        density_score = 2.0
    elif avg_words < 500:
        density_score = 3.0
    else:
        density_score = 4.0
    total += density_score
    details["avg_words_per_file"] = round(avg_words, 1)
    details["density_score"] = density_score

    # 4 pts: Structured packets quality
    packets_dir = chip_path / "research" / "packets"
    structured_count = 0
    substantive_count = 0
    required_fields = {"claim", "mechanism", "boundary"}
    if packets_dir.is_dir():
        for fp in packets_dir.iterdir():
            if not fp.is_file() or fp.suffix.lower() != ".json":
                continue
            try:
                data = json.loads(fp.read_text(encoding="utf-8"))
                if isinstance(data, dict) and required_fields.issubset(data.keys()):
                    structured_count += 1
                    # Check if mechanism has real content (>20 words)
                    mech = data.get("mechanism", "")
                    if isinstance(mech, str) and len(mech.split()) > 20:
                        substantive_count += 1
            except (json.JSONDecodeError, OSError):
                pass

    if structured_count == 0:
        packet_score = 0.0
    elif structured_count <= 2:
        packet_score = 1.0
    elif structured_count <= 9:
        packet_score = 2.0
    elif structured_count <= 29:
        packet_score = 3.0
    else:
        packet_score = 4.0
    total += packet_score
    details["structured_packets"] = structured_count
    details["substantive_packets"] = substantive_count
    details["packet_score"] = packet_score

    return DimensionResult(
        name="evidence_integrity",
        label="Evidence Integrity",
        score=round(total, 1),
        max_points=12.0,
        details=details,
        depth_level=_depth_level(total, 12.0),
    )


# ---------------------------------------------------------------------------
# Dimension 5: Contradiction Rigor (12 pts)
# ---------------------------------------------------------------------------

def check_contradiction_rigor(chip_path: Path) -> DimensionResult:
    """Contradiction-to-run ratio, specificity, resolution quality."""
    entries, full_text = _parse_contradictions(chip_path)
    runs = _load_all_runs(chip_path)
    run_count = len(runs)
    details: dict[str, Any] = {
        "contradiction_entries": len(entries),
        "run_count": run_count,
    }
    total = 0.0

    # 4 pts: Contradiction-to-run ratio
    # A healthy loop generates some contradictions. Zero with many runs is suspicious.
    # The key insight: both the absolute count AND the ratio matter.
    if run_count < 10:
        # Not enough data to judge meaningfully
        if entries:
            ratio_score = 2.0
        else:
            ratio_score = 1.0
    elif len(entries) == 0 and run_count >= 50:
        # SUSPICIOUS: real loops always have regressions
        ratio_score = 0.0
        details["ratio_flag"] = "suspicious_zero_contradictions"
    else:
        ratio = len(entries) / max(run_count, 1)
        # Score based on absolute contradiction count (evidence of analysis depth)
        # AND having a reasonable ratio (not suspiciously high or low)
        abs_score = min(len(entries) / 5.0, 1.0)  # 5+ contradictions = full credit
        # Reasonable ratio: 0.005-0.3 is healthy
        if ratio < 0.005:
            ratio_factor = 0.5  # suspiciously few
        elif ratio > 0.5:
            ratio_factor = 0.7  # suspiciously many
        else:
            ratio_factor = 1.0  # healthy range
        ratio_score = round(abs_score * ratio_factor * 4.0, 1)
        ratio_score = min(ratio_score, 4.0)
        details["contradiction_ratio"] = round(ratio, 4)
    total += ratio_score
    details["ratio_score"] = ratio_score

    # 4 pts: Specificity (named entity density)
    if full_text:
        specificity_matches = _SPECIFICITY_MARKERS.findall(full_text)
        spec_per_100w = (len(specificity_matches) / max(len(full_text.split()), 1)) * 100
        if spec_per_100w <= 0:
            spec_score = 0.0
        elif spec_per_100w < 1.0:
            spec_score = 1.0
        elif spec_per_100w < 3.0:
            spec_score = 2.0
        elif spec_per_100w < 5.0:
            spec_score = 3.0
        else:
            spec_score = 4.0
        details["specificity_per_100w"] = round(spec_per_100w, 2)
    else:
        spec_score = 0.0
        details["specificity_per_100w"] = 0
    total += spec_score
    details["specificity_score"] = spec_score

    # 4 pts: Resolution quality
    if full_text:
        resolution_matches = _RESOLUTION_MARKERS.findall(full_text)
        if len(resolution_matches) == 0:
            res_score = 0.0
        elif len(resolution_matches) <= 2:
            res_score = 1.0
        elif len(resolution_matches) <= 5:
            res_score = 2.0
        else:
            # Check if resolutions reference specific runs/data
            has_specific_refs = any(
                _SPECIFICITY_MARKERS.search(full_text[max(0, m.start() - 100):m.end() + 100])
                for m in _RESOLUTION_MARKERS.finditer(full_text)
            )
            res_score = 4.0 if has_specific_refs else 3.0
        details["resolution_matches"] = len(resolution_matches)
    else:
        res_score = 0.0
        details["resolution_matches"] = 0
    total += res_score
    details["resolution_score"] = res_score

    return DimensionResult(
        name="contradiction_rigor",
        label="Contradiction Rigor",
        score=round(total, 1),
        max_points=12.0,
        details=details,
        depth_level=_depth_level(total, 12.0),
    )


# ---------------------------------------------------------------------------
# Dimension 6: Flywheel Health (15 pts)
# ---------------------------------------------------------------------------

def check_flywheel_health(chip_path: Path) -> DimensionResult:
    """Loop activity frequency, delta per iteration, coverage awareness."""
    runs = _load_all_runs(chip_path)
    scores_list = _extract_scores_from_runs(runs)
    timestamps = _extract_timestamps(runs)
    details: dict[str, Any] = {"run_count": len(runs)}
    total = 0.0

    # 5 pts: Loop activity frequency
    if len(timestamps) >= 2:
        intervals: list[float] = []
        for i in range(1, len(timestamps)):
            delta = (timestamps[i] - timestamps[i - 1]).total_seconds() / 86400.0
            intervals.append(delta)
        avg_interval = sum(intervals) / len(intervals) if intervals else 999
        details["avg_interval_days"] = round(avg_interval, 2)

        if avg_interval > 30:
            freq_score = 1.0
        elif avg_interval > 7:
            freq_score = 2.0
        elif avg_interval > 1:
            freq_score = 3.0
        elif avg_interval > 0.1:
            freq_score = 4.0
        else:
            # Sustained? Check if there are 7+ days of activity
            unique_days = set()
            for ts in timestamps:
                unique_days.add(ts.date())
            freq_score = 5.0 if len(unique_days) >= 7 else 4.0
    else:
        freq_score = 0.0
        details["avg_interval_days"] = None
    total += freq_score
    details["frequency_score"] = freq_score

    # 5 pts: Delta per iteration
    if len(scores_list) >= 3:
        # Rolling window deltas
        window = min(10, len(scores_list))
        deltas: list[float] = []
        for i in range(1, len(scores_list)):
            deltas.append(scores_list[i] - scores_list[i - 1])

        avg_delta = sum(deltas) / len(deltas) if deltas else 0

        # Check for all-identical scores (gaming signal)
        all_same = len(set(round(s, 6) for s in scores_list)) == 1
        if all_same:
            delta_score = 0.0
            details["gaming_signal"] = "all_scores_identical"
        elif avg_delta < 0:
            delta_score = 0.0
        elif avg_delta == 0:
            delta_score = 1.0
        elif avg_delta < 0.01:
            delta_score = 2.0
        elif avg_delta < 0.05:
            delta_score = 3.0
        else:
            # Check for acceleration
            first_half = deltas[: len(deltas) // 2]
            second_half = deltas[len(deltas) // 2 :]
            avg_first = sum(first_half) / len(first_half) if first_half else 0
            avg_second = sum(second_half) / len(second_half) if second_half else 0
            delta_score = 5.0 if avg_second > avg_first else 4.0
        details["avg_delta"] = round(avg_delta, 4)
    else:
        delta_score = 0.0
        details["avg_delta"] = None
    total += delta_score
    details["delta_score"] = delta_score

    # 5 pts: Coverage awareness
    coverage_score = 0.0

    # 2 pts: GAPS.md or gaps section
    gaps_path = chip_path / "GAPS.md"
    has_gaps_file = gaps_path.is_file() and gaps_path.stat().st_size > 50
    if not has_gaps_file:
        # Check README for gaps/limitations section
        readme = chip_path / "README.md"
        if readme.is_file():
            try:
                text = readme.read_text(encoding="utf-8", errors="ignore").lower()
                if "gaps" in text or "limitations" in text or "known issues" in text:
                    has_gaps_file = True
            except OSError:
                pass
    if has_gaps_file:
        coverage_score += 2.0

    # 1 pt: Explicit "not yet covered" / "future work"
    has_future = False
    for candidate in [chip_path / "README.md", chip_path / "chip_skill.md", chip_path / "GAPS.md"]:
        if not candidate.is_file():
            continue
        try:
            text = candidate.read_text(encoding="utf-8", errors="ignore").lower()
            if any(phrase in text for phrase in [
                "not yet covered", "future work", "not yet implemented",
                "planned", "roadmap", "todo", "upcoming",
            ]):
                has_future = True
                break
        except OSError:
            pass
    if has_future:
        coverage_score += 1.0

    # 2 pts: suggest hook output or docs/suggestions/ references gaps
    suggestions_dir = chip_path / "docs" / "suggestions"
    has_suggest = False
    if suggestions_dir.is_dir() and any(suggestions_dir.iterdir()):
        has_suggest = True
    if not has_suggest:
        # Check for suggest output referencing gaps in any doc
        for md in (chip_path / "docs").rglob("*.md") if (chip_path / "docs").is_dir() else []:
            try:
                text = md.read_text(encoding="utf-8", errors="ignore").lower()
                if "suggest" in text and ("gap" in text or "improve" in text or "next" in text):
                    has_suggest = True
                    break
            except OSError:
                pass
    if has_suggest:
        coverage_score += 2.0

    total += coverage_score
    details["coverage_score"] = coverage_score
    details["has_gaps_file"] = has_gaps_file
    details["has_future_work"] = has_future
    details["has_suggest_output"] = has_suggest

    return DimensionResult(
        name="flywheel_health",
        label="Flywheel Health",
        score=round(total, 1),
        max_points=15.0,
        details=details,
        depth_level=_depth_level(total, 15.0),
    )


# ---------------------------------------------------------------------------
# Dimension 7: Watchtower Depth (8 pts)
# ---------------------------------------------------------------------------

def check_watchtower_depth(chip_path: Path) -> DimensionResult:
    """Page count, substance, cross-references in obsidian vault."""
    details: dict[str, Any] = {}
    total = 0.0

    vault_path = chip_path / "obsidian-vault"
    if not vault_path.is_dir():
        return DimensionResult(
            name="watchtower_depth",
            label="Watchtower Depth",
            score=0.0,
            max_points=8.0,
            details={"page_count": 0},
            depth_level="absent",
        )

    md_files = list(vault_path.rglob("*.md"))
    page_count = len(md_files)
    details["page_count"] = page_count

    # 3 pts: Page count (logarithmic)
    if page_count == 0:
        page_score = 0.0
    elif page_count <= 2:
        page_score = 1.0
    elif page_count <= 9:
        page_score = 2.0
    else:
        page_score = 3.0
    total += page_score
    details["page_score"] = page_score

    # 3 pts: Substance per page (average words)
    word_counts = []
    for md in md_files:
        word_counts.append(_content_density_words(md))
    avg_words = sum(word_counts) / len(word_counts) if word_counts else 0
    details["avg_words_per_page"] = round(avg_words, 1)

    if avg_words < 50:
        substance_score = 0.0
    elif avg_words < 150:
        substance_score = 1.0
    elif avg_words < 400:
        substance_score = 2.0
    else:
        substance_score = 3.0
    total += substance_score
    details["substance_score"] = substance_score

    # 2 pts: Cross-references (wikilinks [[...]])
    wikilink_re = re.compile(r"\[\[([^\]]+)\]\]")
    total_links = 0
    pages_with_links = 0
    for md in md_files:
        try:
            text = md.read_text(encoding="utf-8", errors="ignore")
            links = wikilink_re.findall(text)
            if links:
                total_links += len(links)
                pages_with_links += 1
        except OSError:
            pass
    details["total_wikilinks"] = total_links
    details["pages_with_links"] = pages_with_links

    if total_links == 0:
        xref_score = 0.0
    elif pages_with_links <= 2:
        xref_score = 1.0
    else:
        xref_score = 2.0
    total += xref_score
    details["xref_score"] = xref_score

    return DimensionResult(
        name="watchtower_depth",
        label="Watchtower Depth",
        score=round(total, 1),
        max_points=8.0,
        details=details,
        depth_level=_depth_level(total, 8.0),
    )


# ---------------------------------------------------------------------------
# Dimension 8: Integration Maturity (10 pts)
# ---------------------------------------------------------------------------

def check_integration_maturity(chip_path: Path) -> DimensionResult:
    """DSPy purposefulness, scoring model complexity, hook wiring."""
    details: dict[str, Any] = {}
    total = 0.0

    # 4 pts: DSPy purposefulness
    dspy_score = 0.0
    dspy_config = chip_path / "dspy_config.json"
    if dspy_config.is_file():
        dspy_score = 1.0
        try:
            config = json.loads(dspy_config.read_text(encoding="utf-8"))
            # Check for real module paths (not placeholder)
            modules = config.get("modules", {})
            if modules and not all(
                v in ("placeholder", "", None) for v in modules.values()
            ):
                dspy_score = 2.0
        except (json.JSONDecodeError, OSError):
            pass

    # Check src/ for DSPy imports with actual usage
    src_dir = chip_path / "src"
    if src_dir.is_dir():
        for py in src_dir.rglob("*.py"):
            try:
                text = py.read_text(encoding="utf-8", errors="ignore")
                if "import dspy" in text or "from dspy" in text:
                    dspy_score = max(dspy_score, 3.0)
                    # Check if it references chip-specific metrics
                    chip_name = chip_path.name.replace("domain-chip-", "")
                    if chip_name in text.lower() or any(
                        kw in text.lower()
                        for kw in ["eval_metric", "startup_score", "metric_value"]
                    ):
                        dspy_score = 4.0
                    break
            except OSError:
                pass

    # Also check top-level DSPy scripts
    if dspy_score < 3.0:
        for py in chip_path.glob("*dspy*.py"):
            try:
                text = py.read_text(encoding="utf-8", errors="ignore")
                if "import dspy" in text or "dspy" in text.lower():
                    dspy_score = max(dspy_score, 3.0)
                    break
            except OSError:
                pass

    total += dspy_score
    details["dspy_score"] = dspy_score

    # 3 pts: Scoring model complexity
    scoring_score = 0.0
    if src_dir.is_dir():
        for py in src_dir.rglob("*.py"):
            try:
                text = py.read_text(encoding="utf-8", errors="ignore")
                # Simple threshold
                if re.search(r"def\s+(score|evaluate)\s*\(", text):
                    scoring_score = max(scoring_score, 1.0)
                    # Multi-metric weighted
                    if "weight" in text.lower() and re.search(r"\*\s*\d", text):
                        scoring_score = max(scoring_score, 2.0)
                    # Conditional/domain-specific
                    if_count = len(re.findall(r"\bif\b", text))
                    if if_count >= 5 and scoring_score >= 1.0:
                        scoring_score = 3.0
            except OSError:
                pass
    total += scoring_score
    details["scoring_model_score"] = scoring_score

    # 3 pts: Hook wiring completeness
    manifest_path = chip_path / "spark-chip.json"
    hook_count = 0
    if manifest_path.is_file():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            hook_count = len(_manifest_hook_names(manifest))
        except (json.JSONDecodeError, OSError):
            pass

    if hook_count <= 1:
        hook_score = 0.0
    elif hook_count == 2:
        hook_score = 1.0
    elif hook_count == 3:
        hook_score = 2.0
    else:
        hook_score = 3.0
    total += hook_score
    details["hook_count"] = hook_count
    details["hook_score"] = hook_score

    return DimensionResult(
        name="integration_maturity",
        label="Integration Maturity",
        score=round(total, 1),
        max_points=10.0,
        details=details,
        depth_level=_depth_level(total, 10.0),
    )


# ---------------------------------------------------------------------------
# Diagnostic report generator
# ---------------------------------------------------------------------------

def _generate_diagnostics(
    dimensions: list[DimensionResult],
    anti_gaming_flags: list[str],
) -> tuple[list[str], list[str], list[str]]:
    """Generate gaps, strengths, and recommendations from dimension results."""
    gaps: list[str] = []
    strengths: list[str] = []
    recommendations: list[str] = []

    for dim in dimensions:
        ratio = dim.score / dim.max_points if dim.max_points > 0 else 0

        if ratio >= 0.75:
            strengths.append(f"{dim.label}: {dim.depth_level} ({dim.score}/{dim.max_points})")
        elif ratio < 0.25:
            gaps.append(f"{dim.label}: {dim.depth_level} ({dim.score}/{dim.max_points})")

        # Dimension-specific recommendations
        if dim.name == "empirical_velocity" and dim.details.get("run_count", 0) < 50:
            recommendations.append(
                f"Run more evaluation loops (currently {dim.details.get('run_count', 0)} runs, need 50+ for meaningful trajectory)"
            )
        if dim.name == "doctrine_quality" and dim.details.get("causal_density", 0) < 2.0:
            recommendations.append(
                "Enrich doctrines with causal reasoning (because/therefore/leads to)"
            )
        if dim.name == "evidence_integrity" and dim.details.get("populated_lanes", 0) < 3:
            recommendations.append(
                f"Populate more evidence lanes (currently {dim.details.get('populated_lanes', 0)}/4)"
            )
        if dim.name == "contradiction_rigor" and dim.details.get("ratio_flag"):
            recommendations.append(
                "Zero contradictions with many runs is suspicious -- review if loop is genuinely testing hypotheses"
            )
        if dim.name == "flywheel_health" and dim.details.get("gaming_signal"):
            recommendations.append(
                "All scores identical -- the flywheel may not be genuinely iterating"
            )
        if dim.name == "watchtower_depth" and dim.details.get("page_count", 0) == 0:
            recommendations.append(
                "Create Obsidian vault pages to document strategic knowledge"
            )

    if anti_gaming_flags:
        gaps.append(f"Anti-gaming flags: {', '.join(anti_gaming_flags)}")

    return gaps, strengths, recommendations


def _detect_anti_gaming_flags(
    dimensions: list[DimensionResult],
    runs: list[dict[str, Any]],
) -> list[str]:
    """Detect suspicious patterns that suggest gaming rather than genuine intelligence."""
    flags: list[str] = []

    # Flag: high manifest score but low empirical velocity
    manifest_dim = next((d for d in dimensions if d.name == "manifest_structure"), None)
    velocity_dim = next((d for d in dimensions if d.name == "empirical_velocity"), None)
    if manifest_dim and velocity_dim:
        if manifest_dim.score / manifest_dim.max_points >= 0.5 and velocity_dim.score / velocity_dim.max_points < 0.1:
            flags.append("high_structure_low_velocity")

    # Flag: all scores identical in run history
    scores = _extract_scores_from_runs(runs)
    if len(scores) >= 5 and len(set(round(s, 6) for s in scores)) == 1:
        flags.append("identical_scores")

    # Flag: all runs created at same timestamp (batch generation)
    timestamps = _extract_timestamps(runs)
    if len(timestamps) >= 10:
        unique_dates = set(ts.date() for ts in timestamps)
        if len(unique_dates) == 1:
            flags.append("single_day_batch")

    # Flag: very high doctrine count but low causal density
    doctrine_dim = next((d for d in dimensions if d.name == "doctrine_quality"), None)
    if doctrine_dim:
        if doctrine_dim.details.get("doctrine_count", 0) > 10 and doctrine_dim.details.get("causal_density", 0) < 0.5:
            flags.append("high_doctrine_count_low_substance")

    return flags


# ---------------------------------------------------------------------------
# Main scoring function
# ---------------------------------------------------------------------------

def score_chip_v3(chip_path: str | Path) -> DeepEvalResult:
    """Score a domain chip with the v3 deep evaluation rubric.

    Returns a DeepEvalResult with total_score (0-100), 8 dimension results,
    diagnostic gaps/strengths/recommendations, and anti-gaming flags.
    """
    chip_path = Path(chip_path)
    if not chip_path.exists():
        return DeepEvalResult(
            total_score=0.0,
            dimensions=[],
            verdict="not_found",
            gaps=[f"Chip path does not exist: {chip_path}"],
        )

    # Run all 8 dimension checkers
    dimensions = [
        check_manifest_structure(chip_path),
        check_empirical_velocity(chip_path),
        check_doctrine_quality(chip_path),
        check_evidence_integrity(chip_path),
        check_contradiction_rigor(chip_path),
        check_flywheel_health(chip_path),
        check_watchtower_depth(chip_path),
        check_integration_maturity(chip_path),
    ]

    total = sum(d.score for d in dimensions)

    # Detect anti-gaming flags
    runs = _load_all_runs(chip_path)
    anti_gaming_flags = _detect_anti_gaming_flags(dimensions, runs)

    # Generate diagnostics
    gaps, strengths, recommendations = _generate_diagnostics(dimensions, anti_gaming_flags)

    # Determine verdict
    if total >= 75:
        verdict = "production_ready"
    elif total >= 50:
        verdict = "beta"
    elif total >= 25:
        verdict = "alpha"
    else:
        verdict = "scaffold"

    # Build depth profile
    depth_profile = {d.name: d.depth_level for d in dimensions}

    return DeepEvalResult(
        total_score=round(total, 1),
        dimensions=dimensions,
        verdict=verdict,
        gaps=gaps,
        strengths=strengths,
        recommendations=recommendations,
        anti_gaming_flags=anti_gaming_flags,
        depth_profile=depth_profile,
    )


# ---------------------------------------------------------------------------
# Portfolio scoring
# ---------------------------------------------------------------------------

def score_portfolio_v3(
    search_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Score all discovered chips and produce a portfolio report."""
    if search_dir is None:
        search_dir = Path(os.path.expanduser("~")) / "Desktop"
    else:
        search_dir = Path(search_dir)

    if not search_dir.exists():
        return {"error": f"Search directory does not exist: {search_dir}", "chips": {}}

    chips = sorted(
        p
        for p in search_dir.iterdir()
        if p.is_dir()
        and p.name.startswith("domain-chip-")
        and (p / "spark-chip.json").exists()
    )

    results: dict[str, dict[str, Any]] = {}
    for chip in chips:
        result = score_chip_v3(chip)
        results[chip.name] = result.as_dict()

    # Portfolio summary
    scores = [r["total_score"] for r in results.values()]
    avg = sum(scores) / len(scores) if scores else 0
    verdicts = {}
    for r in results.values():
        v = r["verdict"]
        verdicts[v] = verdicts.get(v, 0) + 1

    return {
        "chips": results,
        "summary": {
            "chip_count": len(chips),
            "average_score": round(avg, 1),
            "verdicts": verdicts,
            "ranking": sorted(
                [(name, r["total_score"]) for name, r in results.items()],
                key=lambda t: t[1],
                reverse=True,
            ),
        },
    }
