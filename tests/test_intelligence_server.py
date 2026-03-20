"""Tests for the intelligence delivery system."""

import json
from pathlib import Path

import pytest

from chip_labs.intelligence_server import (
    ChipIntelligence,
    _score_relevance,
    build_context,
    build_doctrine_digest,
    build_skill,
    extract_intelligence,
    refresh_skill,
    serve_context,
)


# ---------------------------------------------------------------------------
# Test helper: build a chip with rich intelligence
# ---------------------------------------------------------------------------

def _build_chip_with_intelligence(tmp_path: Path) -> Path:
    """Create a chip directory populated with doctrines, packets, and scores."""
    chip_dir = tmp_path / "domain-chip-test-intel"
    chip_dir.mkdir()

    # spark-chip.json
    manifest = {
        "schema_version": "spark-chip.v1",
        "io_protocol": "spark-hook-io.v1",
        "chip_name": "test-intel-chip",
        "domain": "test-domain",
        "version": "0.2.0",
        "capabilities": ["evaluate", "suggest", "packets", "watchtower"],
        "frontier": {
            "enabled": True,
            "allowed_mutations": {
                "research_focus": ["methodology", "quality_audit"],
                "target": ["alpha", "beta"],
            },
            "required_fields": ["research_focus"],
            "field_patterns": {"research_focus": "^[a-z_]+$"},
        },
    }
    (chip_dir / "spark-chip.json").write_text(
        json.dumps(manifest), encoding="utf-8"
    )

    # spark-researcher.project.json
    project = {
        "project_name": "domain-chip-test-intel",
        "project_root": ".",
        "chip": {"path": ".", "manifest": "spark-chip.json"},
        "eval_metric": "quality_score",
        "metrics": {"quality_score": {}, "coverage": {}, "depth": {}},
        "candidate_trials": [
            {"id": "baseline", "mutations": {}},
            {"id": "v1", "mutations": {"research_focus": "methodology"}},
            {"id": "v2", "mutations": {"research_focus": "quality_audit", "target": "alpha"}},
        ],
        "commands": {"evaluate": {"kind": "chip-evaluate"}},
        "guardrails": {
            "max_loop_iterations": 8,
            "blocked_command_fragments": ["rm -rf"],
        },
        "self_edit": {"mutable_targets": ["src/"]},
        "memory": {"backend": "local"},
    }
    (chip_dir / "spark-researcher.project.json").write_text(
        json.dumps(project), encoding="utf-8"
    )

    # docs/MISSION.md
    docs_dir = chip_dir / "docs"
    docs_dir.mkdir()
    (docs_dir / "MISSION.md").write_text(
        "# Mission: Test Intelligence Chip\n\n"
        "Build domain intelligence for testing through recursive evaluation.\n"
        "This chip explores mutation-based scoring to validate intelligence extraction.\n",
        encoding="utf-8",
    )

    # docs/doctrines.md (markdown-based doctrines)
    (docs_dir / "doctrines.md").write_text(
        "# Doctrines\n\n"
        "## Doctrine: Additive scoring outperforms multiplicative\n"
        "- claim: Additive scoring produces more stable results than multiplicative\n"
        "- mechanism: Linear combination avoids catastrophic zero-out\n"
        "- boundary: Only valid for independent mutation axes\n\n"
        "## Doctrine: Evidence lanes improve trust\n"
        "- claim: Separating evidence by lane improves result trustworthiness\n"
        "- mechanism: Lane tagging enables provenance tracking\n"
        "- boundary: Requires at least 3 distinct lanes\n",
        encoding="utf-8",
    )

    # research/packets/ with JSON packet
    packets_dir = chip_dir / "research" / "packets"
    packets_dir.mkdir(parents=True)
    (packets_dir / "finding_001.json").write_text(
        json.dumps({
            "claim": "Mutation-based exploration converges faster than random search",
            "mechanism": "Guided mutations use prior scores to narrow search space",
            "boundary": "Assumes smooth scoring landscape",
            "evidence_lane": "benchmark_grounded",
            "confidence": "high",
            "packet_kind": "finding",
        }),
        encoding="utf-8",
    )
    (packets_dir / "finding_002.json").write_text(
        json.dumps({
            "claim": "Portfolio diversity correlates with resilience",
            "mechanism": "Diverse domains reduce single-point-of-failure risk",
            "boundary": "Minimum 5 chips needed for meaningful diversity",
            "evidence_lane": "research_grounded",
            "confidence": "medium",
        }),
        encoding="utf-8",
    )

    # research/research_grounded/ with a note
    rg_dir = chip_dir / "research" / "research_grounded"
    rg_dir.mkdir(parents=True)
    (rg_dir / "note.md").write_text(
        "# Research Note\n\nPrimary source analysis of chip evaluation patterns.\n",
        encoding="utf-8",
    )
    (rg_dir / "study.md").write_text(
        "# Study\n\nComparative study of mutation strategies.\n",
        encoding="utf-8",
    )

    # research/benchmark_grounded/ with a benchmark
    bg_dir = chip_dir / "research" / "benchmark_grounded"
    bg_dir.mkdir(parents=True)
    (bg_dir / "bench_001.json").write_text(
        json.dumps({
            "name": "Baseline benchmark",
            "score": 72,
            "date": "2026-01-15",
        }),
        encoding="utf-8",
    )

    # score_history.jsonl
    (chip_dir / "score_history.jsonl").write_text(
        '{"total_score": 40, "iteration": 1}\n'
        '{"total_score": 55, "iteration": 2}\n'
        '{"total_score": 72, "iteration": 3}\n',
        encoding="utf-8",
    )

    # CONTRADICTIONS.md
    (chip_dir / "CONTRADICTIONS.md").write_text(
        "# Contradictions\n\n"
        "## Contradiction: Scoring stability vs sensitivity\n"
        "- belief_a: Additive scoring is more stable\n"
        "- belief_b: Multiplicative scoring captures interactions better\n"
        "- resolution: Use additive as default with optional interaction terms\n"
        "- status: resolved\n",
        encoding="utf-8",
    )

    # README.md
    (chip_dir / "README.md").write_text(
        "# domain-chip-test-intel\n\n> Test chip for intelligence extraction.\n\n"
        "## Mission\n\nWhat this is: a test chip.\n",
        encoding="utf-8",
    )

    # pyproject.toml
    (chip_dir / "pyproject.toml").write_text(
        '[project]\nname = "domain-chip-test-intel"\nversion = "0.2.0"\n',
        encoding="utf-8",
    )

    # src/ directory with scoring logic
    src_dir = chip_dir / "src" / "test_intel"
    src_dir.mkdir(parents=True)
    (src_dir / "__init__.py").write_text("", encoding="utf-8")
    (src_dir / "evaluate.py").write_text(
        "def score(mutations):\n    return 0.5\n",
        encoding="utf-8",
    )

    # obsidian-vault
    vault_dir = chip_dir / "obsidian-vault"
    vault_dir.mkdir()
    (vault_dir / "Home.md").write_text(
        "# Observatory\n\nDomain intelligence observatory.\n",
        encoding="utf-8",
    )

    # source registry doc
    (docs_dir / "source_registry.md").write_text(
        "# Source Registry\n\nSource map and list of primary sources.\n",
        encoding="utf-8",
    )
    (docs_dir / "architecture.md").write_text(
        "# Architecture\n\nOne-loop architecture spec.\n",
        encoding="utf-8",
    )

    return chip_dir


def _build_minimal_chip(tmp_path: Path) -> Path:
    """Create a minimal chip with just spark-chip.json."""
    chip_dir = tmp_path / "domain-chip-minimal"
    chip_dir.mkdir()

    manifest = {
        "schema_version": "spark-chip.v1",
        "io_protocol": "spark-hook-io.v1",
        "chip_name": "minimal-chip",
        "domain": "minimal",
        "version": "0.0.1",
        "capabilities": ["evaluate"],
    }
    (chip_dir / "spark-chip.json").write_text(
        json.dumps(manifest), encoding="utf-8"
    )

    return chip_dir


# ---------------------------------------------------------------------------
# TestExtractIntelligence
# ---------------------------------------------------------------------------

class TestExtractIntelligence:
    """Test intelligence extraction from chip directories."""

    def test_extracts_from_scaffolded_chip(self, tmp_path: Path) -> None:
        chip_dir = _build_chip_with_intelligence(tmp_path)
        intel = extract_intelligence(chip_dir)
        assert isinstance(intel, ChipIntelligence)
        assert intel.chip_name == "test-intel-chip"

    def test_extracts_domain(self, tmp_path: Path) -> None:
        chip_dir = _build_chip_with_intelligence(tmp_path)
        intel = extract_intelligence(chip_dir)
        assert intel.domain == "test-domain"

    def test_extracts_version(self, tmp_path: Path) -> None:
        chip_dir = _build_chip_with_intelligence(tmp_path)
        intel = extract_intelligence(chip_dir)
        assert intel.version == "0.2.0"

    def test_extracts_from_minimal_chip(self, tmp_path: Path) -> None:
        chip_dir = _build_minimal_chip(tmp_path)
        intel = extract_intelligence(chip_dir)
        assert isinstance(intel, ChipIntelligence)
        assert intel.chip_name == "minimal-chip"
        assert intel.domain == "minimal"

    def test_minimal_chip_has_empty_doctrines(self, tmp_path: Path) -> None:
        chip_dir = _build_minimal_chip(tmp_path)
        intel = extract_intelligence(chip_dir)
        assert intel.doctrines == []

    def test_finds_doctrines_in_json_packets(self, tmp_path: Path) -> None:
        chip_dir = _build_chip_with_intelligence(tmp_path)
        intel = extract_intelligence(chip_dir)
        json_doctrines = [d for d in intel.doctrines if d.get("source", "").endswith(".json")]
        assert len(json_doctrines) >= 1

    def test_json_doctrine_has_claim(self, tmp_path: Path) -> None:
        chip_dir = _build_chip_with_intelligence(tmp_path)
        intel = extract_intelligence(chip_dir)
        json_doctrines = [d for d in intel.doctrines if d.get("source", "").endswith(".json")]
        assert any(d.get("claim") for d in json_doctrines)

    def test_finds_doctrines_in_markdown(self, tmp_path: Path) -> None:
        chip_dir = _build_chip_with_intelligence(tmp_path)
        intel = extract_intelligence(chip_dir)
        md_doctrines = [d for d in intel.doctrines if d.get("source", "").endswith(".md")]
        assert len(md_doctrines) >= 1

    def test_markdown_doctrine_has_mechanism(self, tmp_path: Path) -> None:
        chip_dir = _build_chip_with_intelligence(tmp_path)
        intel = extract_intelligence(chip_dir)
        md_doctrines = [d for d in intel.doctrines if d.get("source", "").endswith(".md")]
        assert any(d.get("mechanism") for d in md_doctrines)

    def test_reads_score_trajectory_from_jsonl(self, tmp_path: Path) -> None:
        chip_dir = _build_chip_with_intelligence(tmp_path)
        intel = extract_intelligence(chip_dir)
        assert intel.score_trajectory == [40, 55, 72]

    def test_score_trajectory_empty_for_minimal(self, tmp_path: Path) -> None:
        chip_dir = _build_minimal_chip(tmp_path)
        intel = extract_intelligence(chip_dir)
        assert intel.score_trajectory == []

    def test_detects_contradictions(self, tmp_path: Path) -> None:
        chip_dir = _build_chip_with_intelligence(tmp_path)
        intel = extract_intelligence(chip_dir)
        assert len(intel.contradictions) >= 1

    def test_contradiction_has_belief_a(self, tmp_path: Path) -> None:
        chip_dir = _build_chip_with_intelligence(tmp_path)
        intel = extract_intelligence(chip_dir)
        assert intel.contradictions[0].get("belief_a")

    def test_contradiction_has_status(self, tmp_path: Path) -> None:
        chip_dir = _build_chip_with_intelligence(tmp_path)
        intel = extract_intelligence(chip_dir)
        assert intel.contradictions[0].get("status") == "resolved"

    def test_counts_evidence_files_correctly(self, tmp_path: Path) -> None:
        chip_dir = _build_chip_with_intelligence(tmp_path)
        intel = extract_intelligence(chip_dir)
        assert intel.evidence_summary["research_grounded"] == 2
        assert intel.evidence_summary["benchmark_grounded"] == 1

    def test_evidence_lanes_all_present(self, tmp_path: Path) -> None:
        chip_dir = _build_chip_with_intelligence(tmp_path)
        intel = extract_intelligence(chip_dir)
        for lane in ["research_grounded", "benchmark_grounded", "exploratory_frontier", "realworld_validated"]:
            assert lane in intel.evidence_summary

    def test_extracts_mutation_axes(self, tmp_path: Path) -> None:
        chip_dir = _build_chip_with_intelligence(tmp_path)
        intel = extract_intelligence(chip_dir)
        assert len(intel.mutation_axes) >= 1
        names = [a["name"] for a in intel.mutation_axes]
        assert "research_focus" in names

    def test_extracts_mission(self, tmp_path: Path) -> None:
        chip_dir = _build_chip_with_intelligence(tmp_path)
        intel = extract_intelligence(chip_dir)
        assert "intelligence" in intel.mission.lower() or "test" in intel.mission.lower()

    def test_extracts_key_benchmarks(self, tmp_path: Path) -> None:
        chip_dir = _build_chip_with_intelligence(tmp_path)
        intel = extract_intelligence(chip_dir)
        assert len(intel.key_benchmarks) >= 1
        assert intel.key_benchmarks[0]["score"] == 72

    def test_counts_packets(self, tmp_path: Path) -> None:
        chip_dir = _build_chip_with_intelligence(tmp_path)
        intel = extract_intelligence(chip_dir)
        assert intel.packet_count == 2

    def test_has_last_updated(self, tmp_path: Path) -> None:
        chip_dir = _build_chip_with_intelligence(tmp_path)
        intel = extract_intelligence(chip_dir)
        assert intel.last_updated
        assert "T" in intel.last_updated

    def test_doctrines_sorted_by_confidence(self, tmp_path: Path) -> None:
        chip_dir = _build_chip_with_intelligence(tmp_path)
        intel = extract_intelligence(chip_dir)
        if len(intel.doctrines) >= 2:
            confidence_order = {"very high": 0, "high": 1, "medium": 2, "low": 3}
            for i in range(len(intel.doctrines) - 1):
                c1 = confidence_order.get(str(intel.doctrines[i].get("confidence", "low")).lower(), 3)
                c2 = confidence_order.get(str(intel.doctrines[i + 1].get("confidence", "low")).lower(), 3)
                assert c1 <= c2

    def test_dspy_not_detected_when_absent(self, tmp_path: Path) -> None:
        chip_dir = _build_chip_with_intelligence(tmp_path)
        intel = extract_intelligence(chip_dir)
        assert intel.has_dspy is False

    def test_dspy_detected_when_config_exists(self, tmp_path: Path) -> None:
        chip_dir = _build_minimal_chip(tmp_path)
        (chip_dir / "dspy_config.json").write_text("{}", encoding="utf-8")
        intel = extract_intelligence(chip_dir)
        assert intel.has_dspy is True

    def test_dspy_detected_when_import_in_src(self, tmp_path: Path) -> None:
        chip_dir = _build_minimal_chip(tmp_path)
        src_dir = chip_dir / "src"
        src_dir.mkdir()
        (src_dir / "pipeline.py").write_text("import dspy\n", encoding="utf-8")
        intel = extract_intelligence(chip_dir)
        assert intel.has_dspy is True


# ---------------------------------------------------------------------------
# TestBuildSkill
# ---------------------------------------------------------------------------

class TestBuildSkill:
    """Test chip_skill.md generation."""

    def test_creates_skill_file(self, tmp_path: Path) -> None:
        chip_dir = _build_chip_with_intelligence(tmp_path)
        result = build_skill(chip_dir)
        assert result.exists()
        assert result.name == "chip_skill.md"

    def test_skill_in_chip_directory(self, tmp_path: Path) -> None:
        chip_dir = _build_chip_with_intelligence(tmp_path)
        result = build_skill(chip_dir)
        assert result.parent == chip_dir

    def test_contains_domain_identity_section(self, tmp_path: Path) -> None:
        chip_dir = _build_chip_with_intelligence(tmp_path)
        build_skill(chip_dir)
        content = (chip_dir / "chip_skill.md").read_text(encoding="utf-8")
        assert "## Domain Identity" in content

    def test_contains_domain_name(self, tmp_path: Path) -> None:
        chip_dir = _build_chip_with_intelligence(tmp_path)
        build_skill(chip_dir)
        content = (chip_dir / "chip_skill.md").read_text(encoding="utf-8")
        assert "test-domain" in content

    def test_contains_doctrines_section(self, tmp_path: Path) -> None:
        chip_dir = _build_chip_with_intelligence(tmp_path)
        build_skill(chip_dir)
        content = (chip_dir / "chip_skill.md").read_text(encoding="utf-8")
        assert "## Core Doctrines" in content

    def test_contains_evidence_summary_table(self, tmp_path: Path) -> None:
        chip_dir = _build_chip_with_intelligence(tmp_path)
        build_skill(chip_dir)
        content = (chip_dir / "chip_skill.md").read_text(encoding="utf-8")
        assert "## Evidence Summary" in content
        assert "research_grounded" in content

    def test_contains_mutation_axes_section(self, tmp_path: Path) -> None:
        chip_dir = _build_chip_with_intelligence(tmp_path)
        build_skill(chip_dir)
        content = (chip_dir / "chip_skill.md").read_text(encoding="utf-8")
        assert "## Mutation Axes" in content

    def test_file_is_longer_than_200_chars(self, tmp_path: Path) -> None:
        chip_dir = _build_chip_with_intelligence(tmp_path)
        build_skill(chip_dir)
        content = (chip_dir / "chip_skill.md").read_text(encoding="utf-8")
        assert len(content) > 200

    def test_is_valid_plain_markdown(self, tmp_path: Path) -> None:
        chip_dir = _build_chip_with_intelligence(tmp_path)
        build_skill(chip_dir)
        content = (chip_dir / "chip_skill.md").read_text(encoding="utf-8")
        # Basic markdown validity: has headings and no stray braces
        assert content.startswith("#")
        assert "{{" not in content
        assert "}}" not in content

    def test_regeneration_is_idempotent(self, tmp_path: Path) -> None:
        chip_dir = _build_chip_with_intelligence(tmp_path)
        build_skill(chip_dir)
        content_1 = (chip_dir / "chip_skill.md").read_text(encoding="utf-8")
        build_skill(chip_dir)
        content_2 = (chip_dir / "chip_skill.md").read_text(encoding="utf-8")
        # Both should have the same structural content (timestamps may differ)
        assert "## Domain Identity" in content_1
        assert "## Domain Identity" in content_2
        # Same number of sections
        assert content_1.count("##") == content_2.count("##")

    def test_minimal_chip_skill_has_placeholder(self, tmp_path: Path) -> None:
        chip_dir = _build_minimal_chip(tmp_path)
        build_skill(chip_dir)
        content = (chip_dir / "chip_skill.md").read_text(encoding="utf-8")
        assert "No doctrines extracted yet" in content


# ---------------------------------------------------------------------------
# TestBuildContext
# ---------------------------------------------------------------------------

class TestBuildContext:
    """Test chip_context.json generation."""

    def test_creates_valid_json_file(self, tmp_path: Path) -> None:
        chip_dir = _build_chip_with_intelligence(tmp_path)
        result = build_context(chip_dir)
        assert result.exists()
        data = json.loads(result.read_text(encoding="utf-8"))
        assert isinstance(data, dict)

    def test_has_chip_name_key(self, tmp_path: Path) -> None:
        chip_dir = _build_chip_with_intelligence(tmp_path)
        build_context(chip_dir)
        data = json.loads((chip_dir / "chip_context.json").read_text(encoding="utf-8"))
        assert "chip_name" in data
        assert data["chip_name"] == "test-intel-chip"

    def test_has_domain_key(self, tmp_path: Path) -> None:
        chip_dir = _build_chip_with_intelligence(tmp_path)
        build_context(chip_dir)
        data = json.loads((chip_dir / "chip_context.json").read_text(encoding="utf-8"))
        assert "domain" in data

    def test_has_doctrines_key(self, tmp_path: Path) -> None:
        chip_dir = _build_chip_with_intelligence(tmp_path)
        build_context(chip_dir)
        data = json.loads((chip_dir / "chip_context.json").read_text(encoding="utf-8"))
        assert "doctrines" in data
        assert isinstance(data["doctrines"], list)

    def test_has_evidence_summary_key(self, tmp_path: Path) -> None:
        chip_dir = _build_chip_with_intelligence(tmp_path)
        build_context(chip_dir)
        data = json.loads((chip_dir / "chip_context.json").read_text(encoding="utf-8"))
        assert "evidence_summary" in data
        assert isinstance(data["evidence_summary"], dict)

    def test_roundtrips_through_json(self, tmp_path: Path) -> None:
        chip_dir = _build_chip_with_intelligence(tmp_path)
        build_context(chip_dir)
        text = (chip_dir / "chip_context.json").read_text(encoding="utf-8")
        data = json.loads(text)
        roundtrip = json.dumps(data, indent=2)
        data2 = json.loads(roundtrip)
        assert data == data2

    def test_context_has_score_trajectory(self, tmp_path: Path) -> None:
        chip_dir = _build_chip_with_intelligence(tmp_path)
        build_context(chip_dir)
        data = json.loads((chip_dir / "chip_context.json").read_text(encoding="utf-8"))
        assert "score_trajectory" in data
        assert data["score_trajectory"] == [40, 55, 72]


# ---------------------------------------------------------------------------
# TestBuildDoctrineDigest
# ---------------------------------------------------------------------------

class TestBuildDoctrineDigest:
    """Test chip_doctrine_digest.md generation."""

    def test_creates_markdown_file(self, tmp_path: Path) -> None:
        chip_dir = _build_chip_with_intelligence(tmp_path)
        result = build_doctrine_digest(chip_dir)
        assert result.exists()
        assert result.name == "chip_doctrine_digest.md"

    def test_contains_doctrine_entries(self, tmp_path: Path) -> None:
        chip_dir = _build_chip_with_intelligence(tmp_path)
        build_doctrine_digest(chip_dir)
        content = (chip_dir / "chip_doctrine_digest.md").read_text(encoding="utf-8")
        assert "###" in content
        # Should contain at least one doctrine-like entry
        assert "confidence" in content.lower() or "mechanism" in content.lower()

    def test_is_shorter_than_full_skill(self, tmp_path: Path) -> None:
        chip_dir = _build_chip_with_intelligence(tmp_path)
        build_skill(chip_dir)
        build_doctrine_digest(chip_dir)
        skill_content = (chip_dir / "chip_skill.md").read_text(encoding="utf-8")
        digest_content = (chip_dir / "chip_doctrine_digest.md").read_text(encoding="utf-8")
        assert len(digest_content) < len(skill_content)

    def test_minimal_chip_digest_has_placeholder(self, tmp_path: Path) -> None:
        chip_dir = _build_minimal_chip(tmp_path)
        build_doctrine_digest(chip_dir)
        content = (chip_dir / "chip_doctrine_digest.md").read_text(encoding="utf-8")
        assert "No doctrines extracted yet" in content

    def test_digest_starts_with_heading(self, tmp_path: Path) -> None:
        chip_dir = _build_chip_with_intelligence(tmp_path)
        build_doctrine_digest(chip_dir)
        content = (chip_dir / "chip_doctrine_digest.md").read_text(encoding="utf-8")
        assert content.startswith("#")


# ---------------------------------------------------------------------------
# TestServeContext
# ---------------------------------------------------------------------------

class TestServeContext:
    """Test query-based context serving."""

    def test_returns_relevant_doctrines_for_matching_query(self, tmp_path: Path) -> None:
        chip_dir = _build_chip_with_intelligence(tmp_path)
        result = serve_context(chip_dir, "mutation scoring")
        assert "relevant_doctrines" in result
        assert len(result["relevant_doctrines"]) >= 1

    def test_returns_chip_summary_always(self, tmp_path: Path) -> None:
        chip_dir = _build_chip_with_intelligence(tmp_path)
        result = serve_context(chip_dir, "anything")
        assert "chip_name" in result
        assert result["chip_name"] == "test-intel-chip"
        assert "evidence_summary" in result
        assert "score" in result

    def test_empty_query_returns_all_doctrines(self, tmp_path: Path) -> None:
        chip_dir = _build_chip_with_intelligence(tmp_path)
        intel = extract_intelligence(chip_dir)
        result = serve_context(chip_dir, "")
        assert len(result["relevant_doctrines"]) == len(intel.doctrines)

    def test_non_matching_query_returns_fewer_results(self, tmp_path: Path) -> None:
        chip_dir = _build_chip_with_intelligence(tmp_path)
        result_all = serve_context(chip_dir, "")
        result_specific = serve_context(chip_dir, "xyznonexistent")
        # Top-5 limit means specific may have equal or fewer
        assert len(result_specific["relevant_doctrines"]) <= max(5, len(result_all["relevant_doctrines"]))

    def test_result_has_query_field(self, tmp_path: Path) -> None:
        chip_dir = _build_chip_with_intelligence(tmp_path)
        result = serve_context(chip_dir, "test query")
        assert result["query"] == "test query"

    def test_result_has_score_field(self, tmp_path: Path) -> None:
        chip_dir = _build_chip_with_intelligence(tmp_path)
        result = serve_context(chip_dir, "test")
        assert "score" in result
        assert isinstance(result["score"], int)

    def test_result_has_evidence_summary(self, tmp_path: Path) -> None:
        chip_dir = _build_chip_with_intelligence(tmp_path)
        result = serve_context(chip_dir, "scoring")
        assert "evidence_summary" in result
        assert isinstance(result["evidence_summary"], dict)


# ---------------------------------------------------------------------------
# TestRefreshSkill
# ---------------------------------------------------------------------------

class TestRefreshSkill:
    """Test refresh_skill regenerates all deliverables."""

    def test_creates_all_three_files(self, tmp_path: Path) -> None:
        chip_dir = _build_chip_with_intelligence(tmp_path)
        refresh_skill(chip_dir)
        assert (chip_dir / "chip_skill.md").exists()
        assert (chip_dir / "chip_context.json").exists()
        assert (chip_dir / "chip_doctrine_digest.md").exists()

    def test_returns_metadata_dict(self, tmp_path: Path) -> None:
        chip_dir = _build_chip_with_intelligence(tmp_path)
        result = refresh_skill(chip_dir)
        assert isinstance(result, dict)
        assert "skill_path" in result
        assert "context_path" in result
        assert "digest_path" in result

    def test_returns_chip_name(self, tmp_path: Path) -> None:
        chip_dir = _build_chip_with_intelligence(tmp_path)
        result = refresh_skill(chip_dir)
        assert result["chip_name"] == "test-intel-chip"

    def test_returns_doctrine_count(self, tmp_path: Path) -> None:
        chip_dir = _build_chip_with_intelligence(tmp_path)
        result = refresh_skill(chip_dir)
        assert result["doctrine_count"] >= 1

    def test_returns_evidence_files_count(self, tmp_path: Path) -> None:
        chip_dir = _build_chip_with_intelligence(tmp_path)
        result = refresh_skill(chip_dir)
        assert result["evidence_files"] >= 1

    def test_returns_verdict(self, tmp_path: Path) -> None:
        chip_dir = _build_chip_with_intelligence(tmp_path)
        result = refresh_skill(chip_dir)
        assert result["verdict"] in ("production_ready", "beta", "alpha", "scaffold")

    def test_is_idempotent(self, tmp_path: Path) -> None:
        chip_dir = _build_chip_with_intelligence(tmp_path)
        result_1 = refresh_skill(chip_dir)
        result_2 = refresh_skill(chip_dir)
        assert result_1["doctrine_count"] == result_2["doctrine_count"]
        assert result_1["evidence_files"] == result_2["evidence_files"]
        assert result_1["chip_name"] == result_2["chip_name"]

    def test_returns_packet_count(self, tmp_path: Path) -> None:
        chip_dir = _build_chip_with_intelligence(tmp_path)
        result = refresh_skill(chip_dir)
        assert result["packet_count"] == 2


# ---------------------------------------------------------------------------
# TestScoreRelevance
# ---------------------------------------------------------------------------

class TestScoreRelevance:
    """Test Jaccard similarity scoring."""

    def test_identical_strings_return_one(self) -> None:
        assert _score_relevance("hello world", "hello world") == 1.0

    def test_no_overlap_returns_zero(self) -> None:
        assert _score_relevance("apple banana", "cherry durian") == 0.0

    def test_partial_overlap_between_zero_and_one(self) -> None:
        score = _score_relevance("hello world foo", "hello bar baz")
        assert 0.0 < score < 1.0

    def test_empty_query_returns_zero(self) -> None:
        assert _score_relevance("", "some text") == 0.0

    def test_empty_text_returns_zero(self) -> None:
        assert _score_relevance("query", "") == 0.0

    def test_both_empty_returns_zero(self) -> None:
        assert _score_relevance("", "") == 0.0

    def test_case_insensitive(self) -> None:
        assert _score_relevance("Hello World", "hello world") == 1.0

    def test_punctuation_split(self) -> None:
        score = _score_relevance("hello-world", "hello world")
        assert score == 1.0

    def test_superset_less_than_one(self) -> None:
        score = _score_relevance("hello", "hello world extra words here")
        assert 0.0 < score < 1.0
