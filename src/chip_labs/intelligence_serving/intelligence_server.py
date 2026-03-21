"""Intelligence delivery system for domain chips.

Converts a domain chip's accumulated intelligence (doctrines, evidence,
beliefs, packets) into deliverable formats that users can consume --
like Claude Code skills, Spawner skills, or structured JSON context.

Zero external dependencies (stdlib only).
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class ChipIntelligence:
    """Complete intelligence snapshot of a domain chip."""

    chip_name: str
    domain: str
    version: str
    mission: str
    doctrines: list[dict[str, Any]] = field(default_factory=list)
    contradictions: list[dict[str, Any]] = field(default_factory=list)
    mutation_axes: list[dict[str, Any]] = field(default_factory=list)
    evidence_summary: dict[str, int] = field(default_factory=dict)
    key_benchmarks: list[dict[str, Any]] = field(default_factory=list)
    score_trajectory: list[int] = field(default_factory=list)
    current_score: int = 0
    verdict: str = "scaffold"
    packet_count: int = 0
    has_dspy: bool = False
    last_updated: str = ""


# ---------------------------------------------------------------------------
# Confidence ordering
# ---------------------------------------------------------------------------

_CONFIDENCE_ORDER = {"very high": 0, "high": 1, "medium": 2, "low": 3}

_LANE_CONFIDENCE: dict[str, str] = {
    "research_grounded": "high",
    "benchmark_grounded": "high",
    "exploratory_frontier": "medium",
    "realworld_validated": "very high",
}


def _confidence_sort_key(doctrine: dict[str, Any]) -> int:
    """Return numeric sort key for a doctrine's confidence level."""
    return _CONFIDENCE_ORDER.get(
        str(doctrine.get("confidence", "low")).lower(), 3
    )


# ---------------------------------------------------------------------------
# Extraction helpers
# ---------------------------------------------------------------------------

def _read_text_safe(path: Path) -> str:
    """Read a file's text content, returning empty string on failure."""
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def _load_json_safe(path: Path) -> dict[str, Any] | list[Any] | None:
    """Load a JSON file, returning None on failure."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _extract_manifest(chip_path: Path) -> dict[str, Any]:
    """Extract chip_name, domain, version from spark-chip.json."""
    manifest_path = chip_path / "spark-chip.json"
    data = _load_json_safe(manifest_path)
    if not data or not isinstance(data, dict):
        return {"chip_name": chip_path.name, "domain": "unknown", "version": "0.0.0"}
    return {
        "chip_name": data.get("chip_name") or data.get("name") or chip_path.name,
        "domain": data.get("domain") or data.get("domain_id") or "unknown",
        "version": data.get("version") or "0.0.0",
    }


def _extract_mission(chip_path: Path) -> str:
    """Extract mission text (first 500 chars) from README or docs."""
    # Try docs/MISSION.md first
    mission_candidates = [
        chip_path / "docs" / "MISSION.md",
        chip_path / "docs" / "mission.md",
    ]
    for candidate in mission_candidates:
        if candidate.exists():
            text = _read_text_safe(candidate)
            if text.strip():
                return text.strip()[:500]

    # Fall back to README.md
    readme = chip_path / "README.md"
    if readme.exists():
        text = _read_text_safe(readme)
        if text.strip():
            return text.strip()[:500]

    return "No mission documentation found."


def _extract_doctrines_from_json(file_path: Path) -> list[dict[str, Any]]:
    """Extract doctrines from a JSON packet file."""
    data = _load_json_safe(file_path)
    if not data or not isinstance(data, dict):
        return []

    # A JSON packet is itself a doctrine if it has claim or mechanism
    doctrines: list[dict[str, Any]] = []
    if data.get("claim") or data.get("mechanism") or data.get("boundary"):
        lane = str(data.get("evidence_lane", "exploratory_frontier"))
        confidence = data.get("confidence") or _LANE_CONFIDENCE.get(lane, "medium")
        doctrines.append({
            "claim": data.get("claim", ""),
            "confidence": confidence,
            "evidence_lane": lane,
            "mechanism": data.get("mechanism", ""),
            "boundary": data.get("boundary", ""),
            "source": str(file_path.name),
        })

    # Also check for nested packets list
    packets = data.get("packets", [])
    if isinstance(packets, list):
        for pkt in packets:
            if isinstance(pkt, dict) and (pkt.get("claim") or pkt.get("mechanism")):
                lane = str(pkt.get("evidence_lane", "exploratory_frontier"))
                confidence = pkt.get("confidence") or _LANE_CONFIDENCE.get(lane, "medium")
                doctrines.append({
                    "claim": pkt.get("claim", ""),
                    "confidence": confidence,
                    "evidence_lane": lane,
                    "mechanism": pkt.get("mechanism", ""),
                    "boundary": pkt.get("boundary", ""),
                    "source": str(file_path.name),
                })

    return doctrines


def _extract_doctrines_from_markdown(file_path: Path) -> list[dict[str, Any]]:
    """Extract doctrines from a markdown file looking for doctrine/claim patterns."""
    text = _read_text_safe(file_path)
    if not text:
        return []

    doctrines: list[dict[str, Any]] = []
    lines = text.split("\n")

    # Pattern 1: Headings containing "doctrine" or "claim"
    current_claim = ""
    current_mechanism = ""
    current_boundary = ""
    in_doctrine_section = False

    for line in lines:
        stripped = line.strip()
        lower = stripped.lower()

        # Detect doctrine/claim section headers
        if stripped.startswith("#") and any(
            kw in lower for kw in ("doctrine", "belief", "claim")
        ):
            # Save previous doctrine if we had one
            if current_claim and in_doctrine_section:
                doctrines.append({
                    "claim": current_claim,
                    "confidence": "medium",
                    "evidence_lane": "research_grounded",
                    "mechanism": current_mechanism,
                    "boundary": current_boundary,
                    "source": str(file_path.name),
                })
            in_doctrine_section = True
            # Extract claim from heading
            heading_text = re.sub(r"^#+\s*", "", stripped)
            heading_text = re.sub(r"(?i)^(doctrine|belief|claim)[:\s]*", "", heading_text)
            current_claim = heading_text.strip() if heading_text.strip() else ""
            current_mechanism = ""
            current_boundary = ""
            continue

        # Pattern 2: Bullet points with claim:/mechanism:/boundary: prefixes
        claim_match = re.match(r"^[-*]\s*(?:claim|Claim)[:\s]+(.+)", stripped)
        if claim_match:
            current_claim = claim_match.group(1).strip()
            in_doctrine_section = True
            continue

        mechanism_match = re.match(r"^[-*]\s*(?:mechanism|Mechanism)[:\s]+(.+)", stripped)
        if mechanism_match:
            current_mechanism = mechanism_match.group(1).strip()
            continue

        boundary_match = re.match(r"^[-*]\s*(?:boundary|Boundary)[:\s]+(.+)", stripped)
        if boundary_match:
            current_boundary = boundary_match.group(1).strip()
            continue

        # Detect end of doctrine section (next heading)
        if stripped.startswith("#") and in_doctrine_section:
            if current_claim:
                doctrines.append({
                    "claim": current_claim,
                    "confidence": "medium",
                    "evidence_lane": "research_grounded",
                    "mechanism": current_mechanism,
                    "boundary": current_boundary,
                    "source": str(file_path.name),
                })
            in_doctrine_section = False
            current_claim = ""
            current_mechanism = ""
            current_boundary = ""

    # Flush remaining
    if current_claim and in_doctrine_section:
        doctrines.append({
            "claim": current_claim,
            "confidence": "medium",
            "evidence_lane": "research_grounded",
            "mechanism": current_mechanism,
            "boundary": current_boundary,
            "source": str(file_path.name),
        })

    return doctrines


def _extract_all_doctrines(chip_path: Path) -> list[dict[str, Any]]:
    """Extract doctrines from all sources in the chip directory."""
    doctrines: list[dict[str, Any]] = []

    # Search JSON packets in research/packets/ and docs/
    search_dirs = [
        chip_path / "research" / "packets",
        chip_path / "docs",
        chip_path / "obsidian-vault",
    ]

    for search_dir in search_dirs:
        if not search_dir.exists():
            continue
        for json_file in search_dir.rglob("*.json"):
            doctrines.extend(_extract_doctrines_from_json(json_file))

    # Search markdown files for doctrine patterns
    md_search_dirs = [
        chip_path / "docs",
        chip_path / "research",
        chip_path / "obsidian-vault",
    ]

    for search_dir in md_search_dirs:
        if not search_dir.exists():
            continue
        for md_file in search_dir.rglob("*.md"):
            text_lower = _read_text_safe(md_file).lower()
            if any(kw in text_lower for kw in ("doctrine", "belief", "claim")):
                doctrines.extend(_extract_doctrines_from_markdown(md_file))

    # De-duplicate by claim text
    seen_claims: set[str] = set()
    unique: list[dict[str, Any]] = []
    for d in doctrines:
        claim_key = d.get("claim", "").strip().lower()
        if claim_key and claim_key not in seen_claims:
            seen_claims.add(claim_key)
            unique.append(d)

    # Sort by confidence
    unique.sort(key=_confidence_sort_key)

    return unique


def _extract_contradictions(chip_path: Path) -> list[dict[str, Any]]:
    """Extract contradictions from CONTRADICTIONS.md or similar files."""
    contradictions: list[dict[str, Any]] = []

    candidates = [
        chip_path / "CONTRADICTIONS.md",
        chip_path / "docs" / "CONTRADICTIONS.md",
        chip_path / "docs" / "contradictions.md",
    ]

    for candidate in candidates:
        if not candidate.exists():
            continue
        text = _read_text_safe(candidate)
        if not text.strip():
            continue

        # Parse contradictions: look for paired beliefs and resolution
        lines = text.split("\n")
        current: dict[str, Any] = {}

        for line in lines:
            stripped = line.strip()
            lower = stripped.lower()

            # Heading-level contradiction
            if stripped.startswith("#") and any(
                kw in lower for kw in ("contradiction", "conflict", "tension")
            ):
                # Flush previous entry if it has substance
                if current.get("belief_a") and (current.get("belief_b") or current.get("resolution")):
                    contradictions.append(current)
                heading_text = re.sub(r"^#+\s*", "", stripped)
                current = {
                    "belief_a": heading_text.strip(),
                    "belief_b": "",
                    "resolution": "",
                    "status": "open",
                }
                continue

            # Bullet-style beliefs
            belief_a_match = re.match(r"^[-*]\s*(?:belief_a|Belief A)[:\s]+(.+)", stripped)
            if belief_a_match:
                current["belief_a"] = belief_a_match.group(1).strip()
                continue

            belief_b_match = re.match(r"^[-*]\s*(?:belief_b|Belief B)[:\s]+(.+)", stripped)
            if belief_b_match:
                current["belief_b"] = belief_b_match.group(1).strip()
                continue

            resolution_match = re.match(r"^[-*]\s*(?:resolution|Resolution)[:\s]+(.+)", stripped)
            if resolution_match:
                current["resolution"] = resolution_match.group(1).strip()
                continue

            status_match = re.match(r"^[-*]\s*(?:status|Status)[:\s]+(.+)", stripped)
            if status_match:
                current["status"] = status_match.group(1).strip().lower()
                continue

        # Flush remaining -- only if it has substance
        if current.get("belief_a") and (current.get("belief_b") or current.get("resolution")):
            contradictions.append(current)

    return contradictions


def _extract_mutation_axes(chip_path: Path) -> list[dict[str, Any]]:
    """Extract mutation axes from spark-researcher.project.json or manifest."""
    axes: list[dict[str, Any]] = []

    # Try project JSON first
    project_path = chip_path / "spark-researcher.project.json"
    project = _load_json_safe(project_path)
    if isinstance(project, dict):
        # Check candidate_trials for mutation keys
        trials = project.get("candidate_trials", [])
        mutation_keys: dict[str, set[str]] = {}
        for trial in trials:
            if not isinstance(trial, dict):
                continue
            mutations = trial.get("mutations", {})
            if isinstance(mutations, dict):
                for k, v in mutations.items():
                    mutation_keys.setdefault(k, set())
                    if v:
                        mutation_keys[k].add(str(v))

        for name, values in mutation_keys.items():
            axes.append({
                "name": name,
                "values": sorted(values),
                "best_value": sorted(values)[0] if values else "",
            })

    # Also check manifest frontier.allowed_mutations
    manifest_path = chip_path / "spark-chip.json"
    manifest = _load_json_safe(manifest_path)
    if isinstance(manifest, dict):
        frontier = manifest.get("frontier", {})
        allowed = frontier.get("allowed_mutations", {})
        if isinstance(allowed, dict):
            existing_names = {a["name"] for a in axes}
            for name, values in allowed.items():
                if name not in existing_names:
                    val_list = values if isinstance(values, list) else []
                    axes.append({
                        "name": name,
                        "values": val_list,
                        "best_value": val_list[0] if val_list else "",
                    })

    return axes


def _count_evidence_files(chip_path: Path) -> dict[str, int]:
    """Count files in each evidence lane under research/."""
    research_dir = chip_path / "research"
    lanes = [
        "research_grounded",
        "benchmark_grounded",
        "exploratory_frontier",
        "realworld_validated",
    ]
    summary: dict[str, int] = {}
    for lane in lanes:
        lane_dir = research_dir / lane
        if lane_dir.exists():
            count = sum(1 for _ in lane_dir.rglob("*") if _.is_file())
            summary[lane] = count
        else:
            summary[lane] = 0
    return summary


def _extract_benchmarks(chip_path: Path) -> list[dict[str, Any]]:
    """Extract key benchmarks from research/benchmark_grounded/."""
    benchmarks: list[dict[str, Any]] = []
    bench_dir = chip_path / "research" / "benchmark_grounded"
    if not bench_dir.exists():
        return benchmarks

    for fp in bench_dir.rglob("*.json"):
        data = _load_json_safe(fp)
        if isinstance(data, dict):
            benchmarks.append({
                "name": data.get("name") or data.get("title") or fp.stem,
                "score": data.get("score") or data.get("result", 0),
                "date": data.get("date") or data.get("timestamp") or "",
            })

    for fp in bench_dir.rglob("*.md"):
        text = _read_text_safe(fp)
        # Look for score patterns like "Score: 85" in markdown
        score_match = re.search(r"(?i)score[:\s]+(\d+(?:\.\d+)?)", text)
        if score_match:
            benchmarks.append({
                "name": fp.stem,
                "score": float(score_match.group(1)),
                "date": "",
            })

    return benchmarks


def _extract_score_trajectory(chip_path: Path) -> list[int]:
    """Read score history from score_history.jsonl or loop_telemetry.json."""
    trajectory: list[int] = []

    # Try score_history.jsonl
    jsonl_path = chip_path / "score_history.jsonl"
    if jsonl_path.exists():
        text = _read_text_safe(jsonl_path)
        for line in text.strip().split("\n"):
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                if isinstance(entry, dict) and "total_score" in entry:
                    trajectory.append(int(entry["total_score"]))
            except (json.JSONDecodeError, ValueError):
                pass
        if trajectory:
            return trajectory

    # Try loop_telemetry.json
    telemetry_path = chip_path / "loop_telemetry.json"
    data = _load_json_safe(telemetry_path)
    if isinstance(data, dict):
        scores = data.get("scores", [])
        if isinstance(scores, list):
            for s in scores:
                try:
                    trajectory.append(int(s))
                except (TypeError, ValueError):
                    pass
    elif isinstance(data, list):
        for entry in data:
            if isinstance(entry, dict) and "total_score" in entry:
                try:
                    trajectory.append(int(entry["total_score"]))
                except (TypeError, ValueError):
                    pass

    return trajectory


def _count_packets(chip_path: Path) -> int:
    """Count packet files in research/packets/."""
    packets_dir = chip_path / "research" / "packets"
    if not packets_dir.exists():
        return 0
    return sum(1 for f in packets_dir.rglob("*") if f.is_file())


def _detect_dspy(chip_path: Path) -> bool:
    """Detect DSPy usage in the chip."""
    # Check for dspy_config.json
    if (chip_path / "dspy_config.json").exists():
        return True

    # Check for "import dspy" in src/
    src_dir = chip_path / "src"
    if src_dir.exists():
        for py_file in src_dir.rglob("*.py"):
            text = _read_text_safe(py_file)
            if "import dspy" in text:
                return True

    return False


# ---------------------------------------------------------------------------
# Main extraction
# ---------------------------------------------------------------------------

def extract_intelligence(chip_path: Path) -> ChipIntelligence:
    """Read chip directory and extract ALL intelligence into a structured snapshot.

    Args:
        chip_path: Path to the domain chip root directory.

    Returns:
        ChipIntelligence dataclass with all extracted data.
    """
    chip_path = Path(chip_path)

    # Manifest basics
    manifest_info = _extract_manifest(chip_path)

    # Mission
    mission = _extract_mission(chip_path)

    # Doctrines
    doctrines = _extract_all_doctrines(chip_path)

    # Contradictions
    contradictions = _extract_contradictions(chip_path)

    # Mutation axes
    mutation_axes = _extract_mutation_axes(chip_path)

    # Evidence summary
    evidence_summary = _count_evidence_files(chip_path)

    # Benchmarks
    key_benchmarks = _extract_benchmarks(chip_path)

    # Score trajectory
    score_trajectory = _extract_score_trajectory(chip_path)

    # Current score (from quality rubric)
    try:
        from ..quality_rubric import score_chip
        rubric_result = score_chip(chip_path)
        current_score = rubric_result.get("total_score", 0)
        verdict = rubric_result.get("verdict", "scaffold")
    except (ImportError, Exception):
        current_score = 0
        verdict = "scaffold"

    # Packet count
    packet_count = _count_packets(chip_path)

    # DSPy detection
    has_dspy = _detect_dspy(chip_path)

    # Timestamp
    last_updated = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    return ChipIntelligence(
        chip_name=manifest_info["chip_name"],
        domain=manifest_info["domain"],
        version=manifest_info["version"],
        mission=mission,
        doctrines=doctrines,
        contradictions=contradictions,
        mutation_axes=mutation_axes,
        evidence_summary=evidence_summary,
        key_benchmarks=key_benchmarks,
        score_trajectory=score_trajectory,
        current_score=current_score,
        verdict=verdict,
        packet_count=packet_count,
        has_dspy=has_dspy,
        last_updated=last_updated,
    )


# ---------------------------------------------------------------------------
# Relevance scoring
# ---------------------------------------------------------------------------

def _score_relevance(query: str, text: str) -> float:
    """Jaccard similarity on word sets (lowercase, split on whitespace/punctuation).

    Args:
        query: The search query string.
        text: The text to compare against.

    Returns:
        Float between 0.0 and 1.0 representing Jaccard similarity.
    """
    if not query or not text:
        return 0.0

    def _tokenize(s: str) -> set[str]:
        return set(re.split(r"[\s\W]+", s.lower())) - {""}

    query_words = _tokenize(query)
    text_words = _tokenize(text)

    if not query_words or not text_words:
        return 0.0

    intersection = query_words & text_words
    union = query_words | text_words

    return len(intersection) / len(union) if union else 0.0


# ---------------------------------------------------------------------------
# Build skill (Markdown deliverable)
# ---------------------------------------------------------------------------

def build_skill(chip_path: Path) -> Path:
    """Generate chip_skill.md following the skill template.

    Args:
        chip_path: Path to the domain chip root directory.

    Returns:
        Path to the generated chip_skill.md file.
    """
    chip_path = Path(chip_path)
    intel = extract_intelligence(chip_path)

    # Build doctrines section
    doctrines_section = ""
    if intel.doctrines:
        for i, doc in enumerate(intel.doctrines, 1):
            doctrines_section += f"\n### {i}. {doc.get('claim', 'Unnamed doctrine')} (confidence: {doc.get('confidence', 'medium')})\n"
            if doc.get("evidence_lane"):
                doctrines_section += f"- **Evidence lane**: {doc['evidence_lane']}\n"
            if doc.get("mechanism"):
                doctrines_section += f"- **Mechanism**: {doc['mechanism']}\n"
            if doc.get("boundary"):
                doctrines_section += f"- **Boundary**: {doc['boundary']}\n"
            if doc.get("source"):
                doctrines_section += f"- **Source**: {doc['source']}\n"
    else:
        doctrines_section = "\nNo doctrines extracted yet. Run the researcher loop to accumulate intelligence.\n"

    # Build contradictions section
    if intel.contradictions:
        contradictions_section = ""
        for c in intel.contradictions:
            contradictions_section += f"\n- **{c.get('belief_a', '')}** vs **{c.get('belief_b', '')}**\n"
            if c.get("resolution"):
                contradictions_section += f"  - Resolution: {c['resolution']}\n"
            contradictions_section += f"  - Status: {c.get('status', 'open')}\n"
    else:
        contradictions_section = "\nNo active contradictions.\n"

    # Build mutation axes table
    if intel.mutation_axes:
        axes_rows = ""
        for axis in intel.mutation_axes:
            values_str = ", ".join(str(v) for v in axis.get("values", []))
            axes_rows += f"| {axis.get('name', '')} | {values_str} |\n"
    else:
        axes_rows = "| (none) | (none) |\n"

    # Build evidence summary table
    evidence_rows = ""
    total_evidence = 0
    for lane in ["research_grounded", "benchmark_grounded", "exploratory_frontier", "realworld_validated"]:
        count = intel.evidence_summary.get(lane, 0)
        total_evidence += count
        status = "active" if count > 0 else ""
        evidence_rows += f"| {lane} | {count} | {status} |\n"

    # Build benchmarks section
    if intel.key_benchmarks:
        benchmarks_section = "\n| Name | Score | Date |\n|------|-------|------|\n"
        for b in intel.key_benchmarks:
            benchmarks_section += f"| {b.get('name', '')} | {b.get('score', '')} | {b.get('date', '')} |\n"
    else:
        benchmarks_section = "\nNo benchmarks recorded yet.\n"

    # Build trajectory section
    if intel.score_trajectory:
        trajectory_str = " -> ".join(str(s) for s in intel.score_trajectory)
        trajectory_section = f"Score history: {trajectory_str}"
    else:
        trajectory_section = "No history yet."

    # Total evidence count for header
    total_evidence_count = sum(intel.evidence_summary.values())
    doctrine_count = len(intel.doctrines)

    skill_content = f"""# {intel.chip_name} Domain Intelligence

> Quality: {intel.current_score}/100 ({intel.verdict}) | Doctrines: {doctrine_count} | Evidence files: {total_evidence_count}
> Last updated: {intel.last_updated}

## Domain Identity

**Domain**: {intel.domain}
**Version**: {intel.version}

{intel.mission}

## Core Doctrines

These are the chip's strongest beliefs, sorted by confidence.
{doctrines_section}
## Active Contradictions
{contradictions_section}
## Mutation Axes

These are the dimensions the chip explores during research:

| Axis | Values |
|------|--------|
{axes_rows}
## Evidence Summary

| Lane | Files | Status |
|------|-------|--------|
{evidence_rows}
## Key Benchmarks
{benchmarks_section}
## Quality Trajectory

{trajectory_section}
Current: {intel.current_score}/100 ({intel.verdict})
"""

    output_path = chip_path / "chip_skill.md"
    output_path.write_text(skill_content, encoding="utf-8")
    return output_path


# ---------------------------------------------------------------------------
# Build context (JSON deliverable)
# ---------------------------------------------------------------------------

def build_context(chip_path: Path) -> Path:
    """Generate chip_context.json with the ChipIntelligence data serialized as JSON.

    Args:
        chip_path: Path to the domain chip root directory.

    Returns:
        Path to the generated chip_context.json file.
    """
    chip_path = Path(chip_path)
    intel = extract_intelligence(chip_path)
    data = asdict(intel)

    output_path = chip_path / "chip_context.json"
    output_path.write_text(
        json.dumps(data, indent=2, default=str), encoding="utf-8"
    )
    return output_path


# ---------------------------------------------------------------------------
# Build doctrine digest (concise Markdown)
# ---------------------------------------------------------------------------

def build_doctrine_digest(chip_path: Path) -> Path:
    """Generate chip_doctrine_digest.md -- concise doctrine-only summary.

    Args:
        chip_path: Path to the domain chip root directory.

    Returns:
        Path to the generated chip_doctrine_digest.md file.
    """
    chip_path = Path(chip_path)
    intel = extract_intelligence(chip_path)

    content = f"# {intel.chip_name} Doctrine Digest\n\n"
    content += f"> {len(intel.doctrines)} doctrines | Quality: {intel.current_score}/100\n\n"

    if intel.doctrines:
        for i, doc in enumerate(intel.doctrines, 1):
            content += f"### {i}. {doc.get('claim', 'Unnamed')} ({doc.get('confidence', 'medium')})\n"
            if doc.get("mechanism"):
                content += f"- Mechanism: {doc['mechanism']}\n"
            if doc.get("boundary"):
                content += f"- Boundary: {doc['boundary']}\n"
            content += "\n"
    else:
        content += "No doctrines extracted yet. Run the researcher loop to accumulate intelligence.\n"

    output_path = chip_path / "chip_doctrine_digest.md"
    output_path.write_text(content, encoding="utf-8")
    return output_path


# ---------------------------------------------------------------------------
# Serve context (query-based)
# ---------------------------------------------------------------------------

def serve_context(chip_path: Path, query: str) -> dict[str, Any]:
    """Query-based context serving.

    Extracts intelligence, scores each doctrine against query using Jaccard
    similarity, and returns top-5 most relevant doctrines plus chip summary.

    Args:
        chip_path: Path to the domain chip root directory.
        query: Search query string.

    Returns:
        Dict with chip_name, query, relevant_doctrines, evidence_summary, score.
    """
    chip_path = Path(chip_path)
    intel = extract_intelligence(chip_path)

    if not query.strip():
        # Empty query returns all doctrines
        relevant = intel.doctrines
    else:
        # Score each doctrine against query
        scored: list[tuple[float, dict[str, Any]]] = []
        for doc in intel.doctrines:
            # Combine doctrine fields into a single text for matching
            doc_text = " ".join(
                str(doc.get(k, ""))
                for k in ("claim", "mechanism", "boundary", "evidence_lane")
            )
            score = _score_relevance(query, doc_text)
            scored.append((score, doc))

        # Sort by relevance descending
        scored.sort(key=lambda x: x[0], reverse=True)

        # Return top-5
        relevant = [doc for _, doc in scored[:5]]

    return {
        "chip_name": intel.chip_name,
        "query": query,
        "relevant_doctrines": relevant,
        "evidence_summary": intel.evidence_summary,
        "score": intel.current_score,
    }


# ---------------------------------------------------------------------------
# Refresh skill (regenerate all deliverables)
# ---------------------------------------------------------------------------

def refresh_skill(chip_path: Path) -> dict[str, Any]:
    """Regenerate all deliverables: skill, context, and doctrine digest.

    Args:
        chip_path: Path to the domain chip root directory.

    Returns:
        Dict with paths and metadata.
    """
    chip_path = Path(chip_path)

    skill_path = build_skill(chip_path)
    context_path = build_context(chip_path)
    digest_path = build_doctrine_digest(chip_path)

    intel = extract_intelligence(chip_path)

    return {
        "skill_path": str(skill_path),
        "context_path": str(context_path),
        "digest_path": str(digest_path),
        "chip_name": intel.chip_name,
        "doctrine_count": len(intel.doctrines),
        "evidence_files": sum(intel.evidence_summary.values()),
        "current_score": intel.current_score,
        "verdict": intel.verdict,
        "packet_count": intel.packet_count,
        "last_updated": intel.last_updated,
    }
