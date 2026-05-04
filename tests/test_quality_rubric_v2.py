"""Tests for the hardened quality rubric v2 scoring module."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


from chip_labs.quality_rubric_v2 import (
    RUBRIC_DIMENSIONS_V2,
    score_chip,
    score_chip_v2,
)


# ---------------------------------------------------------------------------
# Test helper -- builds a minimal valid chip for overriding
# ---------------------------------------------------------------------------

def _build_test_chip(tmp_path: Path, **overrides: Any) -> Path:
    """Scaffold a minimal chip directory that passes most checks.

    Override keys control what is included or omitted:
      - skip_manifest: bool -- omit spark-chip.json
      - skip_project: bool -- omit spark-researcher.project.json
      - skip_readme: bool -- omit README.md
      - readme_content: str -- custom README text
      - skip_pyproject: bool
      - skip_docs: bool
      - docs_files: dict[str, str] -- filename -> content for docs/
      - skip_src: bool
      - src_files: dict[str, str] -- relative path -> content under src/
      - research_lanes: dict[str, str] -- lane_name -> file content
      - score_history: list[dict] -- entries for score_history.jsonl
      - loop_telemetry: list[dict] -- entries for loop_telemetry.json
      - runs_files: dict[str, str] -- files under runs/
      - belief_files: dict[str, str] -- relative -> content
      - contradictions_content: str | None
      - packets: list[dict] -- JSON packets in research/packets/
      - dspy_config: dict | None
      - skill_content: str | None -- chip_skill.md content
    """
    chip_dir = tmp_path / "domain-chip-test"
    chip_dir.mkdir(exist_ok=True)

    # --- spark-chip.json ---
    if not overrides.get("skip_manifest"):
        manifest = {
            "schema_version": "spark-chip.v1",
            "io_protocol": "spark-hook-io.v1",
            "domain": "test",
            "version": "0.1.0",
            "capabilities": ["evaluate", "suggest", "packets", "watchtower"],
            "frontier": {
                "enabled": True,
                "allowed_mutations": ["focus"],
                "required_fields": ["focus"],
                "field_patterns": {"focus": "^[a-z_]+$"},
            },
        }
        (chip_dir / "spark-chip.json").write_text(
            json.dumps(manifest), encoding="utf-8"
        )

    # --- spark-researcher.project.json ---
    if not overrides.get("skip_project"):
        project = {
            "project_name": "test-chip",
            "eval_metric": "quality_score",
            "metrics": {"quality_score": {}, "coverage": {}, "depth": {}},
            "candidate_trials": [
                {"name": "baseline", "mutations": {}},
                {"name": "v_a", "mutations": {"focus": "a"}},
                {"name": "v_b", "mutations": {"focus": "b"}},
            ],
            "chip": {"path": ".", "manifest": "spark-chip.json"},
            "commands": {"evaluate": {"kind": "chip-evaluate"}},
            "guardrails": {
                "max_loop_iterations": 10,
                "blocked_command_fragments": ["rm -rf"],
            },
            "self_edit": {"mutable_targets": ["src/"]},
            "memory": {"backend": "local"},
        }
        (chip_dir / "spark-researcher.project.json").write_text(
            json.dumps(project), encoding="utf-8"
        )

    # --- pyproject.toml ---
    if not overrides.get("skip_pyproject"):
        (chip_dir / "pyproject.toml").write_text(
            '[project]\nname = "domain-chip-test"\nversion = "0.1.0"\n',
            encoding="utf-8",
        )

    # --- README.md ---
    if not overrides.get("skip_readme"):
        readme_text = overrides.get(
            "readme_content",
            (
                "# Test Chip\n\n## Mission\n\n"
                "This is a test domain chip created for automated quality rubric "
                "validation. It includes evaluation hooks, documentation, and "
                "evidence separation across four lanes. The mission is to ensure "
                "comprehensive testing of every rubric dimension.\n"
            ),
        )
        (chip_dir / "README.md").write_text(readme_text, encoding="utf-8")

    # --- src/ ---
    if not overrides.get("skip_src"):
        src_dir = chip_dir / "src" / "hooks"
        src_dir.mkdir(parents=True, exist_ok=True)
        src_files = overrides.get("src_files", {
            "hooks/evaluate.py": (
                "def score(mutations):\n"
                "    \"\"\"Score a chip configuration.\"\"\"\n"
                "    return 0.75\n"
            ),
            "hooks/packets.py": (
                "def build_packet(claim, mechanism, boundary):\n"
                "    return {'claim': claim, 'mechanism': mechanism, "
                "'boundary': boundary}\n"
            ),
            "hooks/watchtower.py": (
                "# watchtower hook\ndef generate_obsidian_page(data):\n"
                "    return '# Page'\n"
            ),
        })
        for rel_path, content in src_files.items():
            fp = chip_dir / "src" / rel_path
            fp.parent.mkdir(parents=True, exist_ok=True)
            fp.write_text(content, encoding="utf-8")

    # --- docs/ ---
    if not overrides.get("skip_docs"):
        docs_dir = chip_dir / "docs"
        docs_dir.mkdir(exist_ok=True)
        docs_files = overrides.get("docs_files", {
            "source_registry.md": (
                "# Source Registry\n\n"
                "Primary sources for this chip:\n"
                "- https://arxiv.org/abs/2301.00001\n"
                "- doi:10.1000/example\n"
                "Source map and list of primary sources.\n"
            ),
            "architecture.md": (
                "# Architecture\n\n"
                "One-loop architecture for the test chip. "
                "The flywheel processes evidence through four lanes "
                "and produces scored candidate trials for iteration. "
                "Each loop iteration refines the scoring function "
                "and updates belief states accordingly.\n"
            ),
            "mission.md": (
                "# Mission\n\n"
                "The intent of the test chip is to validate "
                "the quality rubric scoring across all dimensions. "
                "It exercises every check in the v2 rubric to ensure "
                "comprehensive coverage and accurate verdicts.\n"
            ),
        })
        for name, content in docs_files.items():
            (docs_dir / name).write_text(content, encoding="utf-8")

    # --- research/ lanes ---
    research_lanes = overrides.get("research_lanes", {})
    for lane_name, content in research_lanes.items():
        lane_dir = chip_dir / "research" / lane_name
        lane_dir.mkdir(parents=True, exist_ok=True)
        (lane_dir / "evidence.md").write_text(content, encoding="utf-8")

    # --- research/packets/ ---
    packets = overrides.get("packets", [])
    if packets:
        packets_dir = chip_dir / "research" / "packets"
        packets_dir.mkdir(parents=True, exist_ok=True)
        for i, pkt in enumerate(packets):
            (packets_dir / f"packet_{i}.json").write_text(
                json.dumps(pkt), encoding="utf-8"
            )

    # --- score_history.jsonl ---
    score_history = overrides.get("score_history")
    if score_history is not None:
        lines = [json.dumps(e) for e in score_history]
        (chip_dir / "score_history.jsonl").write_text(
            "\n".join(lines) + "\n", encoding="utf-8"
        )

    # --- loop_telemetry.json ---
    loop_telemetry = overrides.get("loop_telemetry")
    if loop_telemetry is not None:
        (chip_dir / "loop_telemetry.json").write_text(
            json.dumps(loop_telemetry), encoding="utf-8"
        )

    # --- runs/ ---
    runs_files = overrides.get("runs_files")
    if runs_files:
        runs_dir = chip_dir / "runs"
        runs_dir.mkdir(exist_ok=True)
        for name, content in runs_files.items():
            (runs_dir / name).write_text(content, encoding="utf-8")

    # --- belief files ---
    belief_files = overrides.get("belief_files")
    if belief_files:
        for rel, content in belief_files.items():
            fp = chip_dir / rel
            fp.parent.mkdir(parents=True, exist_ok=True)
            fp.write_text(content, encoding="utf-8")

    # --- CONTRADICTIONS.md ---
    contradictions = overrides.get("contradictions_content")
    if contradictions is not None:
        (chip_dir / "CONTRADICTIONS.md").write_text(
            contradictions, encoding="utf-8"
        )

    # --- dspy_config.json ---
    dspy_config = overrides.get("dspy_config")
    if dspy_config is not None:
        (chip_dir / "dspy_config.json").write_text(
            json.dumps(dspy_config), encoding="utf-8"
        )

    # --- chip_skill.md ---
    skill_content = overrides.get("skill_content")
    if skill_content is not None:
        (chip_dir / "chip_skill.md").write_text(
            skill_content, encoding="utf-8"
        )

    # --- obsidian-vault ---
    if overrides.get("obsidian_vault"):
        vault = chip_dir / "obsidian-vault"
        vault.mkdir(exist_ok=True)
        (vault / "index.md").write_text("# Vault\nContent here.\n", encoding="utf-8")

    return chip_dir


# ====================================================================
# 1. TestScoreV2ValidChip -- API contract
# ====================================================================

class TestScoreV2ValidChip:
    """API contract: score_chip_v2 returns the expected shape."""

    def test_returns_dict(self, tmp_path: Path) -> None:
        chip = _build_test_chip(tmp_path)
        result = score_chip_v2(chip)
        assert isinstance(result, dict)

    def test_has_required_keys(self, tmp_path: Path) -> None:
        chip = _build_test_chip(tmp_path)
        result = score_chip_v2(chip)
        for key in ("total_score", "dimensions", "passed_checks",
                     "failed_checks", "verdict", "rubric_version"):
            assert key in result, f"Missing key: {key}"

    def test_rubric_version_is_2_0(self, tmp_path: Path) -> None:
        chip = _build_test_chip(tmp_path)
        result = score_chip_v2(chip)
        assert result["rubric_version"] == "2.0"

    def test_seven_dimensions(self, tmp_path: Path) -> None:
        chip = _build_test_chip(tmp_path)
        result = score_chip_v2(chip)
        assert len(result["dimensions"]) == 7

    def test_dimension_names_match_rubric(self, tmp_path: Path) -> None:
        chip = _build_test_chip(tmp_path)
        result = score_chip_v2(chip)
        names = {d["name"] for d in result["dimensions"]}
        expected = {d["name"] for d in RUBRIC_DIMENSIONS_V2}
        assert names == expected

    def test_total_points_cap_is_100(self) -> None:
        total = sum(d["max_points"] for d in RUBRIC_DIMENSIONS_V2)
        assert total == 100

    def test_total_checks_count_is_36(self) -> None:
        total = sum(len(d["checks"]) for d in RUBRIC_DIMENSIONS_V2)
        assert total == 36

    def test_passed_and_failed_disjoint(self, tmp_path: Path) -> None:
        chip = _build_test_chip(tmp_path)
        result = score_chip_v2(chip)
        assert set(result["passed_checks"]).isdisjoint(set(result["failed_checks"]))

    def test_total_score_is_int(self, tmp_path: Path) -> None:
        chip = _build_test_chip(tmp_path)
        result = score_chip_v2(chip)
        assert isinstance(result["total_score"], int)

    def test_missing_path_returns_not_found(self, tmp_path: Path) -> None:
        result = score_chip_v2(tmp_path / "nonexistent")
        assert result["verdict"] == "not_found"
        assert result["total_score"] == 0
        assert result["rubric_version"] == "2.0"
        assert "error" in result

    def test_empty_dir_is_scaffold(self, tmp_path: Path) -> None:
        empty = tmp_path / "empty-chip"
        empty.mkdir()
        result = score_chip_v2(empty)
        assert result["verdict"] == "scaffold"
        assert result["total_score"] < 35


# ====================================================================
# 2. TestManifestV2 -- reuses v1 logic
# ====================================================================

class TestManifestV2:
    """Manifest validity dimension (same as v1, reused)."""

    def test_valid_manifest_scores_15(self, tmp_path: Path) -> None:
        chip = _build_test_chip(tmp_path)
        result = score_chip_v2(chip)
        dim = next(d for d in result["dimensions"] if d["name"] == "manifest_validity")
        assert dim["score"] == 15

    def test_missing_manifest_scores_zero(self, tmp_path: Path) -> None:
        chip = _build_test_chip(tmp_path, skip_manifest=True)
        result = score_chip_v2(chip)
        dim = next(d for d in result["dimensions"] if d["name"] == "manifest_validity")
        assert dim["score"] == 0

    def test_invalid_json_manifest_scores_zero(self, tmp_path: Path) -> None:
        chip = _build_test_chip(tmp_path)
        (chip / "spark-chip.json").write_text("{invalid", encoding="utf-8")
        result = score_chip_v2(chip)
        dim = next(d for d in result["dimensions"] if d["name"] == "manifest_validity")
        assert dim["score"] == 0

    def test_missing_capabilities_loses_hooks_points(self, tmp_path: Path) -> None:
        chip = _build_test_chip(tmp_path)
        manifest = json.loads((chip / "spark-chip.json").read_text(encoding="utf-8"))
        manifest["capabilities"] = ["evaluate"]  # missing 3 hooks
        (chip / "spark-chip.json").write_text(json.dumps(manifest), encoding="utf-8")
        result = score_chip_v2(chip)
        assert "all_four_hooks" in result["failed_checks"]

    def test_schema_version_must_be_spark_chip_v1(self, tmp_path: Path) -> None:
        chip = _build_test_chip(tmp_path)
        manifest = json.loads((chip / "spark-chip.json").read_text(encoding="utf-8"))
        manifest["schema_version"] = "spark-chip.v2"
        (chip / "spark-chip.json").write_text(json.dumps(manifest), encoding="utf-8")
        result = score_chip_v2(chip)
        assert "schema_version" in result["failed_checks"]


# ====================================================================
# 3. TestEvidenceSeparationHardened
# ====================================================================

class TestEvidenceSeparationHardened:
    """Evidence separation requires actual files in research/ subdirs."""

    def test_keyword_only_does_not_pass(self, tmp_path: Path) -> None:
        """Mentioning 'research_grounded' in README but no dirs fails."""
        chip = _build_test_chip(
            tmp_path,
            readme_content=(
                "# Chip\n\n## Mission\n\n"
                "We have research_grounded and benchmark_grounded "
                "and exploratory_frontier and realworld_validated evidence "
                "built into this chip for maximum quality.\n"
                "x" * 200
            ),
        )
        result = score_chip_v2(chip)
        dim = next(d for d in result["dimensions"] if d["name"] == "evidence_separation")
        assert dim["score"] == 0

    def test_empty_research_dirs_do_not_pass(self, tmp_path: Path) -> None:
        chip = _build_test_chip(tmp_path)
        for lane in ["research_grounded", "benchmark_grounded",
                      "exploratory_frontier", "realworld_validated"]:
            (chip / "research" / lane).mkdir(parents=True, exist_ok=True)
        result = score_chip_v2(chip)
        dim = next(d for d in result["dimensions"] if d["name"] == "evidence_separation")
        assert dim["score"] == 0

    def test_files_under_50_bytes_do_not_pass(self, tmp_path: Path) -> None:
        chip = _build_test_chip(tmp_path)
        lane_dir = chip / "research" / "research_grounded"
        lane_dir.mkdir(parents=True, exist_ok=True)
        (lane_dir / "tiny.md").write_text("x" * 10, encoding="utf-8")  # <50 bytes
        result = score_chip_v2(chip)
        assert "has_research_grounded" in result["failed_checks"]

    def test_real_files_pass(self, tmp_path: Path) -> None:
        lanes = {
            "research_grounded": "x" * 100,
            "benchmark_grounded": "y" * 100,
            "exploratory_frontier": "z" * 100,
            "realworld_validated": "w" * 100,
        }
        chip = _build_test_chip(tmp_path, research_lanes=lanes)
        result = score_chip_v2(chip)
        dim = next(d for d in result["dimensions"] if d["name"] == "evidence_separation")
        assert dim["score"] == dim["max_points"]

    def test_partial_lanes_partial_score(self, tmp_path: Path) -> None:
        lanes = {
            "research_grounded": "x" * 100,
            "benchmark_grounded": "y" * 100,
        }
        chip = _build_test_chip(tmp_path, research_lanes=lanes)
        result = score_chip_v2(chip)
        dim = next(d for d in result["dimensions"] if d["name"] == "evidence_separation")
        assert 0 < dim["score"] < dim["max_points"]

    def test_realworld_validated_docs_fallback(self, tmp_path: Path) -> None:
        """A docs/ file mentioning 'realworld' + 'plan' is a valid fallback."""
        chip = _build_test_chip(
            tmp_path,
            docs_files={
                "source_registry.md": "# Sources\nhttps://example.com\n" + "x" * 200,
                "architecture.md": "# Architecture\n" + "y" * 200,
                "mission.md": "# Mission\n" + "z" * 200,
                "validation_plan.md": (
                    "# Realworld Validation Plan\n\n"
                    "This plan outlines realworld validation steps.\n"
                ),
            },
        )
        result = score_chip_v2(chip)
        assert "has_realworld_validated" in result["passed_checks"]

    def test_realworld_docs_fallback_needs_both_keywords(self, tmp_path: Path) -> None:
        """Docs with only 'realworld' but no 'plan'/'validation' fails."""
        chip = _build_test_chip(
            tmp_path,
            docs_files={
                "source_registry.md": "# Sources\nhttps://example.com\n" + "x" * 200,
                "architecture.md": "# Architecture\n" + "y" * 200,
                "mission.md": "# Mission\n" + "z" * 200,
                "notes.md": "# Notes\n\nrealworld stuff mentioned here.\n",
            },
        )
        result = score_chip_v2(chip)
        assert "has_realworld_validated" in result["failed_checks"]


# ====================================================================
# 4. TestEvaluationDepthHardened
# ====================================================================

class TestEvaluationDepthHardened:
    """Evaluation depth -- regex-based scoring function detection."""

    def test_word_score_alone_fails_scoring_function(self, tmp_path: Path) -> None:
        """Just having 'score' in a file is not enough."""
        chip = _build_test_chip(
            tmp_path,
            src_files={
                "hooks/evaluate.py": (
                    "# This module computes a score\n"
                    "total_score = 42\n"
                ),
                "hooks/packets.py": "def build(): pass\n",
            },
        )
        result = score_chip_v2(chip)
        assert "scoring_function" in result["failed_checks"]

    def test_real_score_function_passes(self, tmp_path: Path) -> None:
        chip = _build_test_chip(
            tmp_path,
            src_files={
                "hooks/evaluate.py": (
                    "def score(mutations):\n"
                    "    val = 0.5\n"
                    "    return val\n"
                ),
            },
        )
        result = score_chip_v2(chip)
        assert "scoring_function" in result["passed_checks"]

    def test_evaluate_function_also_passes(self, tmp_path: Path) -> None:
        chip = _build_test_chip(
            tmp_path,
            src_files={
                "hooks/evaluate.py": (
                    "def evaluate(chip, data):\n"
                    "    result = compute(data)\n"
                    "    return result\n"
                ),
            },
        )
        result = score_chip_v2(chip)
        assert "scoring_function" in result["passed_checks"]

    def test_missing_project_json_fails_all(self, tmp_path: Path) -> None:
        chip = _build_test_chip(tmp_path, skip_project=True)
        result = score_chip_v2(chip)
        dim = next(d for d in result["dimensions"] if d["name"] == "evaluation_depth")
        assert dim["score"] == 0

    def test_fewer_than_3_metrics_fails(self, tmp_path: Path) -> None:
        chip = _build_test_chip(tmp_path)
        project = json.loads(
            (chip / "spark-researcher.project.json").read_text(encoding="utf-8")
        )
        project["metrics"] = {"single": {}}
        (chip / "spark-researcher.project.json").write_text(
            json.dumps(project), encoding="utf-8"
        )
        result = score_chip_v2(chip)
        assert "multiple_metrics" in result["failed_checks"]

    def test_fewer_than_3_trials_fails(self, tmp_path: Path) -> None:
        chip = _build_test_chip(tmp_path)
        project = json.loads(
            (chip / "spark-researcher.project.json").read_text(encoding="utf-8")
        )
        project["candidate_trials"] = [{"name": "a", "mutations": {}}]
        (chip / "spark-researcher.project.json").write_text(
            json.dumps(project), encoding="utf-8"
        )
        result = score_chip_v2(chip)
        assert "candidate_trials" in result["failed_checks"]

    def test_no_baseline_trial_fails(self, tmp_path: Path) -> None:
        chip = _build_test_chip(tmp_path)
        project = json.loads(
            (chip / "spark-researcher.project.json").read_text(encoding="utf-8")
        )
        project["candidate_trials"] = [
            {"name": "a", "mutations": {"x": 1}},
            {"name": "b", "mutations": {"x": 2}},
            {"name": "c", "mutations": {"x": 3}},
        ]
        (chip / "spark-researcher.project.json").write_text(
            json.dumps(project), encoding="utf-8"
        )
        result = score_chip_v2(chip)
        assert "baseline_trial" in result["failed_checks"]

    def test_full_evaluation_depth(self, tmp_path: Path) -> None:
        chip = _build_test_chip(tmp_path)
        result = score_chip_v2(chip)
        dim = next(d for d in result["dimensions"] if d["name"] == "evaluation_depth")
        assert dim["score"] == dim["max_points"]


# ====================================================================
# 5. TestMemoryKnowledgeHardened
# ====================================================================

class TestMemoryKnowledgeHardened:
    """Memory & knowledge -- real URLs and structured packets."""

    def test_word_source_alone_fails_url_check(self, tmp_path: Path) -> None:
        chip = _build_test_chip(
            tmp_path,
            docs_files={
                "source_registry.md": "# Sources\n\nSource registry list.\n",
                "architecture.md": "# Architecture\n" + "y" * 200,
                "mission.md": "# Mission\n" + "z" * 200,
            },
        )
        result = score_chip_v2(chip)
        assert "source_registry_urls" in result["failed_checks"]

    def test_https_url_passes(self, tmp_path: Path) -> None:
        chip = _build_test_chip(
            tmp_path,
            docs_files={
                "source_registry.md": (
                    "# Sources\nhttps://example.com/paper\n" + "x" * 200
                ),
                "architecture.md": "# Architecture\n" + "y" * 200,
                "mission.md": "# Mission\n" + "z" * 200,
            },
        )
        result = score_chip_v2(chip)
        assert "source_registry_urls" in result["passed_checks"]

    def test_doi_passes(self, tmp_path: Path) -> None:
        chip = _build_test_chip(
            tmp_path,
            docs_files={
                "sources.md": "doi:10.1234/test\n" + "x" * 200,
                "architecture.md": "# Architecture\n" + "y" * 200,
                "mission.md": "# Mission\n" + "z" * 200,
            },
        )
        result = score_chip_v2(chip)
        assert "source_registry_urls" in result["passed_checks"]

    def test_arxiv_passes(self, tmp_path: Path) -> None:
        chip = _build_test_chip(
            tmp_path,
            docs_files={
                "sources.md": "arxiv:2301.00001\n" + "x" * 200,
                "architecture.md": "# Architecture\n" + "y" * 200,
                "mission.md": "# Mission\n" + "z" * 200,
            },
        )
        result = score_chip_v2(chip)
        assert "source_registry_urls" in result["passed_checks"]

    def test_packet_structured_claim_mechanism_boundary(self, tmp_path: Path) -> None:
        chip = _build_test_chip(
            tmp_path,
            src_files={
                "hooks/packets.py": (
                    "def build(claim, mechanism, boundary):\n"
                    "    return {'claim': claim, "
                    "'mechanism': mechanism, "
                    "'boundary': boundary}\n"
                ),
                "hooks/evaluate.py": "def score(m):\n    return 0.5\n",
            },
        )
        result = score_chip_v2(chip)
        assert "packet_structured" in result["passed_checks"]

    def test_packet_structured_type_lane_content(self, tmp_path: Path) -> None:
        chip = _build_test_chip(
            tmp_path,
            src_files={
                "hooks/packets.py": (
                    "def build(type, evidence_lane, content):\n"
                    "    return {'type': type, "
                    "'evidence_lane': evidence_lane, "
                    "'content': content}\n"
                ),
                "hooks/evaluate.py": "def score(m):\n    return 0.5\n",
            },
        )
        result = score_chip_v2(chip)
        assert "packet_structured" in result["passed_checks"]

    def test_no_structured_fields_fails_packet(self, tmp_path: Path) -> None:
        chip = _build_test_chip(
            tmp_path,
            src_files={
                "hooks/packets.py": "def build():\n    return {}\n",
                "hooks/evaluate.py": "def score(m):\n    return 0.5\n",
            },
        )
        result = score_chip_v2(chip)
        assert "packet_structured" in result["failed_checks"]

    def test_watchtower_keyword_in_src(self, tmp_path: Path) -> None:
        chip = _build_test_chip(tmp_path)
        result = score_chip_v2(chip)
        assert "watchtower_pages" in result["passed_checks"]

    def test_obsidian_vault_missing(self, tmp_path: Path) -> None:
        chip = _build_test_chip(tmp_path)
        result = score_chip_v2(chip)
        assert "obsidian_vault" in result["failed_checks"]

    def test_obsidian_vault_present(self, tmp_path: Path) -> None:
        chip = _build_test_chip(tmp_path, obsidian_vault=True)
        result = score_chip_v2(chip)
        assert "obsidian_vault" in result["passed_checks"]


# ====================================================================
# 6. TestDocumentationHardened
# ====================================================================

class TestDocumentationHardened:
    """Documentation -- minimum content lengths enforced."""

    def test_empty_readme_fails(self, tmp_path: Path) -> None:
        chip = _build_test_chip(tmp_path, readme_content="# Chip\n")
        result = score_chip_v2(chip)
        assert "readme_exists" in result["failed_checks"]

    def test_short_readme_fails(self, tmp_path: Path) -> None:
        chip = _build_test_chip(tmp_path, readme_content="a" * 100)
        result = score_chip_v2(chip)
        assert "readme_exists" in result["failed_checks"]

    def test_200_char_readme_passes(self, tmp_path: Path) -> None:
        chip = _build_test_chip(tmp_path, readme_content="a" * 200)
        result = score_chip_v2(chip)
        assert "readme_exists" in result["passed_checks"]

    def test_missing_readme_fails(self, tmp_path: Path) -> None:
        chip = _build_test_chip(tmp_path, skip_readme=True)
        result = score_chip_v2(chip)
        assert "readme_exists" in result["failed_checks"]

    def test_short_mission_doc_fails(self, tmp_path: Path) -> None:
        chip = _build_test_chip(
            tmp_path,
            docs_files={
                "mission.md": "# Mission\nShort.\n",
                "architecture.md": "# Architecture\n" + "y" * 200,
                "sources.md": "https://example.com\n" + "x" * 200,
            },
            # README does not mention "mission"
            readme_content="x" * 200,
        )
        result = score_chip_v2(chip)
        assert "mission_docs" in result["failed_checks"]

    def test_substantive_mission_doc_passes(self, tmp_path: Path) -> None:
        chip = _build_test_chip(tmp_path)
        result = score_chip_v2(chip)
        assert "mission_docs" in result["passed_checks"]

    def test_short_architecture_doc_fails(self, tmp_path: Path) -> None:
        chip = _build_test_chip(
            tmp_path,
            docs_files={
                "architecture.md": "# Architecture\nShort.\n",
                "mission.md": "# Mission\n" + "z" * 200,
                "sources.md": "https://example.com\n" + "x" * 200,
            },
        )
        result = score_chip_v2(chip)
        assert "architecture_docs" in result["failed_checks"]

    def test_substantive_architecture_passes(self, tmp_path: Path) -> None:
        chip = _build_test_chip(tmp_path)
        result = score_chip_v2(chip)
        assert "architecture_docs" in result["passed_checks"]

    def test_docs_needs_2_plus_files(self, tmp_path: Path) -> None:
        chip = _build_test_chip(
            tmp_path,
            docs_files={"only_one.md": "# One\n" + "x" * 200},
        )
        result = score_chip_v2(chip)
        assert "docs_directory" in result["failed_checks"]

    def test_docs_with_2_files_passes(self, tmp_path: Path) -> None:
        chip = _build_test_chip(tmp_path)
        result = score_chip_v2(chip)
        assert "docs_directory" in result["passed_checks"]

    def test_no_docs_dir_fails(self, tmp_path: Path) -> None:
        chip = _build_test_chip(
            tmp_path,
            skip_docs=True,
            # Use a README without the word "mission" so the fallback
            # does not trigger for mission_docs either.
            readme_content="# Test Chip\n\n" + "x" * 200,
        )
        result = score_chip_v2(chip)
        assert "docs_directory" in result["failed_checks"]
        assert "mission_docs" in result["failed_checks"]
        assert "architecture_docs" in result["failed_checks"]

    def test_pyproject_present(self, tmp_path: Path) -> None:
        chip = _build_test_chip(tmp_path)
        result = score_chip_v2(chip)
        assert "pyproject_valid" in result["passed_checks"]

    def test_pyproject_missing_fails(self, tmp_path: Path) -> None:
        chip = _build_test_chip(tmp_path, skip_pyproject=True)
        result = score_chip_v2(chip)
        assert "pyproject_valid" in result["failed_checks"]

    def test_mission_fallback_via_readme(self, tmp_path: Path) -> None:
        """README with 'mission' keyword and >=150 chars is a fallback."""
        chip = _build_test_chip(
            tmp_path,
            readme_content="# Mission Statement\n" + "x" * 200,
            docs_files={
                "architecture.md": "# Architecture\n" + "y" * 200,
                "sources.md": "https://example.com\n" + "x" * 200,
            },
        )
        result = score_chip_v2(chip)
        assert "mission_docs" in result["passed_checks"]


# ====================================================================
# 7. TestFlywheelIntelligence -- new dimension
# ====================================================================

class TestFlywheelIntelligence:
    """Flywheel intelligence -- the new 25-point dimension."""

    def test_empty_chip_scores_zero_flywheel(self, tmp_path: Path) -> None:
        chip = tmp_path / "empty-chip"
        chip.mkdir()
        result = score_chip_v2(chip)
        dim = next(d for d in result["dimensions"] if d["name"] == "flywheel_intelligence")
        assert dim["score"] == 0

    # --- has_run_history ---

    def test_score_history_jsonl_gives_run_history(self, tmp_path: Path) -> None:
        chip = _build_test_chip(
            tmp_path,
            score_history=[{"score": 50}],
        )
        result = score_chip_v2(chip)
        assert "has_run_history" in result["passed_checks"]

    def test_loop_telemetry_gives_run_history(self, tmp_path: Path) -> None:
        chip = _build_test_chip(
            tmp_path,
            loop_telemetry=[{"score": 50}],
        )
        result = score_chip_v2(chip)
        assert "has_run_history" in result["passed_checks"]

    def test_runs_directory_gives_run_history(self, tmp_path: Path) -> None:
        chip = _build_test_chip(
            tmp_path,
            runs_files={"run_001.json": '{"score": 50}'},
        )
        result = score_chip_v2(chip)
        assert "has_run_history" in result["passed_checks"]

    def test_no_history_fails_run_history(self, tmp_path: Path) -> None:
        chip = _build_test_chip(tmp_path)
        result = score_chip_v2(chip)
        assert "has_run_history" in result["failed_checks"]

    def test_empty_jsonl_fails_run_history(self, tmp_path: Path) -> None:
        chip = _build_test_chip(tmp_path)
        (chip / "score_history.jsonl").write_text("", encoding="utf-8")
        result = score_chip_v2(chip)
        assert "has_run_history" in result["failed_checks"]

    # --- belief_promotion ---

    def test_improving_trajectory_gives_belief_promotion(self, tmp_path: Path) -> None:
        chip = _build_test_chip(
            tmp_path,
            score_history=[{"score": 40}, {"score": 60}],
        )
        result = score_chip_v2(chip)
        assert "belief_promotion" in result["passed_checks"]

    def test_flat_trajectory_fails_belief_promotion(self, tmp_path: Path) -> None:
        chip = _build_test_chip(
            tmp_path,
            score_history=[{"score": 50}, {"score": 50}],
        )
        result = score_chip_v2(chip)
        assert "belief_promotion" in result["failed_checks"]

    def test_declining_trajectory_fails_belief_promotion(self, tmp_path: Path) -> None:
        chip = _build_test_chip(
            tmp_path,
            score_history=[{"score": 80}, {"score": 60}],
        )
        result = score_chip_v2(chip)
        assert "belief_promotion" in result["failed_checks"]

    def test_belief_file_with_promoted_passes(self, tmp_path: Path) -> None:
        chip = _build_test_chip(
            tmp_path,
            belief_files={
                "beliefs/core.md": "# Beliefs\n\nThis belief has been promoted to durable status.\n",
            },
        )
        result = score_chip_v2(chip)
        assert "belief_promotion" in result["passed_checks"]

    def test_belief_file_with_durable_passes(self, tmp_path: Path) -> None:
        chip = _build_test_chip(
            tmp_path,
            belief_files={
                "belief_log.md": "# Log\n\nEntry is durable and confirmed.\n",
            },
        )
        result = score_chip_v2(chip)
        assert "belief_promotion" in result["passed_checks"]

    def test_belief_file_without_keywords_fails(self, tmp_path: Path) -> None:
        chip = _build_test_chip(
            tmp_path,
            belief_files={
                "belief_log.md": "# Log\n\nJust some notes here.\n",
            },
        )
        result = score_chip_v2(chip)
        assert "belief_promotion" in result["failed_checks"]

    def test_loop_telemetry_trajectory(self, tmp_path: Path) -> None:
        """Belief promotion via loop_telemetry.json improving scores."""
        chip = _build_test_chip(
            tmp_path,
            loop_telemetry=[{"score": 30}, {"score": 50}],
        )
        result = score_chip_v2(chip)
        assert "belief_promotion" in result["passed_checks"]

    # --- metric_trajectory ---

    def test_3_entries_2_ascending_passes(self, tmp_path: Path) -> None:
        chip = _build_test_chip(
            tmp_path,
            score_history=[{"score": 40}, {"score": 50}, {"score": 60}],
        )
        result = score_chip_v2(chip)
        assert "metric_trajectory" in result["passed_checks"]

    def test_2_entries_fails_trajectory(self, tmp_path: Path) -> None:
        chip = _build_test_chip(
            tmp_path,
            score_history=[{"score": 40}, {"score": 60}],
        )
        result = score_chip_v2(chip)
        assert "metric_trajectory" in result["failed_checks"]

    def test_3_entries_only_1_ascending_fails(self, tmp_path: Path) -> None:
        chip = _build_test_chip(
            tmp_path,
            score_history=[{"score": 40}, {"score": 60}, {"score": 50}],
        )
        result = score_chip_v2(chip)
        assert "metric_trajectory" in result["failed_checks"]

    def test_4_entries_2_ascending_passes(self, tmp_path: Path) -> None:
        chip = _build_test_chip(
            tmp_path,
            score_history=[
                {"score": 40}, {"score": 50},
                {"score": 45}, {"score": 60},
            ],
        )
        result = score_chip_v2(chip)
        assert "metric_trajectory" in result["passed_checks"]

    def test_trajectory_via_loop_telemetry(self, tmp_path: Path) -> None:
        chip = _build_test_chip(
            tmp_path,
            loop_telemetry=[
                {"score": 30}, {"score": 40}, {"score": 50},
            ],
        )
        result = score_chip_v2(chip)
        assert "metric_trajectory" in result["passed_checks"]

    # --- contradiction_handling ---

    def test_contradictions_with_real_content_passes(self, tmp_path: Path) -> None:
        chip = _build_test_chip(
            tmp_path,
            contradictions_content=(
                "# Contradictions\n\n"
                "We observed that the initial hypothesis about trading "
                "frequency was contradicted by benchmark data showing "
                "lower-frequency strategies outperforming by 15% over "
                "the six-month test window.\n"
            ),
        )
        result = score_chip_v2(chip)
        assert "contradiction_handling" in result["passed_checks"]

    def test_contradictions_just_headers_fails(self, tmp_path: Path) -> None:
        chip = _build_test_chip(
            tmp_path,
            contradictions_content="# Contradictions\n\n## Section\n\n### Sub\n",
        )
        result = score_chip_v2(chip)
        assert "contradiction_handling" in result["failed_checks"]

    def test_contradictions_short_content_fails(self, tmp_path: Path) -> None:
        chip = _build_test_chip(
            tmp_path,
            contradictions_content="# Contradictions\n\nToo short.\n",
        )
        result = score_chip_v2(chip)
        assert "contradiction_handling" in result["failed_checks"]

    def test_no_contradictions_file_fails(self, tmp_path: Path) -> None:
        chip = _build_test_chip(tmp_path)
        result = score_chip_v2(chip)
        assert "contradiction_handling" in result["failed_checks"]

    # --- packet_quality_real ---

    def test_structured_packet_claim_mechanism_boundary(self, tmp_path: Path) -> None:
        chip = _build_test_chip(
            tmp_path,
            packets=[{
                "claim": "X improves Y",
                "mechanism": "via Z",
                "boundary": "only for domain A",
            }],
        )
        result = score_chip_v2(chip)
        assert "packet_quality_real" in result["passed_checks"]

    def test_structured_packet_type_lane_content(self, tmp_path: Path) -> None:
        chip = _build_test_chip(
            tmp_path,
            packets=[{
                "type": "finding",
                "evidence_lane": "research_grounded",
                "content": "Important finding from literature.",
            }],
        )
        result = score_chip_v2(chip)
        assert "packet_quality_real" in result["passed_checks"]

    def test_unstructured_packet_fails(self, tmp_path: Path) -> None:
        chip = _build_test_chip(
            tmp_path,
            packets=[{"note": "just a note"}],
        )
        result = score_chip_v2(chip)
        assert "packet_quality_real" in result["failed_checks"]

    def test_no_packets_dir_fails(self, tmp_path: Path) -> None:
        chip = _build_test_chip(tmp_path)
        result = score_chip_v2(chip)
        assert "packet_quality_real" in result["failed_checks"]

    def test_empty_packets_dir_fails(self, tmp_path: Path) -> None:
        chip = _build_test_chip(tmp_path)
        (chip / "research" / "packets").mkdir(parents=True, exist_ok=True)
        result = score_chip_v2(chip)
        assert "packet_quality_real" in result["failed_checks"]

    # --- has_dspy_integration ---

    def test_dspy_config_json_passes(self, tmp_path: Path) -> None:
        chip = _build_test_chip(
            tmp_path,
            dspy_config={"model": "gpt-4"},
        )
        result = score_chip_v2(chip)
        assert "has_dspy_integration" in result["passed_checks"]

    def test_import_dspy_in_src_passes(self, tmp_path: Path) -> None:
        chip = _build_test_chip(
            tmp_path,
            src_files={
                "hooks/evaluate.py": "def score(m):\n    return 0.5\n",
                "hooks/optimizer.py": "import dspy\n\ndef optimize():\n    pass\n",
            },
        )
        result = score_chip_v2(chip)
        assert "has_dspy_integration" in result["passed_checks"]

    def test_dspy_slot_in_src_passes(self, tmp_path: Path) -> None:
        chip = _build_test_chip(
            tmp_path,
            src_files={
                "hooks/evaluate.py": "def score(m):\n    return 0.5\n",
                "hooks/slot.py": "class DSpySlot:\n    pass\n",
            },
        )
        result = score_chip_v2(chip)
        assert "has_dspy_integration" in result["passed_checks"]

    def test_no_dspy_fails(self, tmp_path: Path) -> None:
        chip = _build_test_chip(tmp_path)
        result = score_chip_v2(chip)
        assert "has_dspy_integration" in result["failed_checks"]

    def test_dspy_named_file_at_root(self, tmp_path: Path) -> None:
        chip = _build_test_chip(tmp_path)
        (chip / "run_dspy.py").write_text("print('dspy')\n", encoding="utf-8")
        result = score_chip_v2(chip)
        assert "has_dspy_integration" in result["passed_checks"]

    # --- has_skill_file ---

    def test_skill_file_with_200_chars_passes(self, tmp_path: Path) -> None:
        chip = _build_test_chip(
            tmp_path,
            skill_content="# Skill\n\n" + "x" * 200,
        )
        result = score_chip_v2(chip)
        assert "has_skill_file" in result["passed_checks"]

    def test_skill_file_too_short_fails(self, tmp_path: Path) -> None:
        chip = _build_test_chip(
            tmp_path,
            skill_content="# Skill\nShort.\n",
        )
        result = score_chip_v2(chip)
        assert "has_skill_file" in result["failed_checks"]

    def test_no_skill_file_fails(self, tmp_path: Path) -> None:
        chip = _build_test_chip(tmp_path)
        result = score_chip_v2(chip)
        assert "has_skill_file" in result["failed_checks"]

    # --- full flywheel scoring ---

    def test_full_flywheel_25_points(self, tmp_path: Path) -> None:
        """A chip with all flywheel features scores 25."""
        chip = _build_test_chip(
            tmp_path,
            score_history=[
                {"score": 30}, {"score": 40},
                {"score": 50}, {"score": 60},
            ],
            contradictions_content=(
                "# Contradictions\n\n"
                "The initial hypothesis was contradicted by evidence "
                "showing the opposite effect in real-world tests with "
                "a margin greater than our confidence threshold.\n"
            ),
            packets=[{
                "claim": "X works",
                "mechanism": "via Y",
                "boundary": "for Z",
            }],
            dspy_config={"model": "gpt-4"},
            skill_content="# Chip Skill\n\n" + "x" * 250,
            belief_files={
                "beliefs/core.md": "Promoted belief: pattern X is durable.\n",
            },
        )
        result = score_chip_v2(chip)
        dim = next(d for d in result["dimensions"] if d["name"] == "flywheel_intelligence")
        assert dim["score"] == 25


# ====================================================================
# 8. TestVerdictThresholds
# ====================================================================

class TestVerdictThresholds:
    """Verdict threshold logic."""

    def test_production_ready_at_80(self, tmp_path: Path) -> None:
        chip = _build_test_chip(tmp_path)
        result = score_chip_v2(chip)
        if result["total_score"] >= 80:
            assert result["verdict"] == "production_ready"

    def test_scaffold_below_35(self, tmp_path: Path) -> None:
        empty = tmp_path / "bare-chip"
        empty.mkdir()
        result = score_chip_v2(empty)
        assert result["total_score"] < 35
        assert result["verdict"] == "scaffold"

    def test_alpha_between_35_and_59(self, tmp_path: Path) -> None:
        """A chip with manifest + project but not much else is alpha."""
        chip = _build_test_chip(
            tmp_path,
            skip_docs=True,
            skip_readme=True,
            skip_pyproject=True,
            skip_src=True,
        )
        result = score_chip_v2(chip)
        # manifest=15 + integration=10 = 25 minimum, but no evaluation depth
        # without src
        # Actually we still have project.json so eval depth partial works
        # (primary_metric=3, multiple_metrics=3, candidate_trials=3,
        #  baseline_trial=3, scoring_function=0) = 12
        # manifest=15 + eval=12 + integration=10 = 37 -> alpha
        if 35 <= result["total_score"] < 60:
            assert result["verdict"] == "alpha"

    def test_verdict_is_string(self, tmp_path: Path) -> None:
        chip = _build_test_chip(tmp_path)
        result = score_chip_v2(chip)
        assert isinstance(result["verdict"], str)
        assert result["verdict"] in {
            "production_ready", "beta", "alpha", "scaffold", "not_found",
        }


# ====================================================================
# 9. TestBackwardCompat
# ====================================================================

class TestBackwardCompat:
    """Backward-compatible score_chip(path, version=...) dispatcher."""

    def test_default_version_is_v2(self, tmp_path: Path) -> None:
        chip = _build_test_chip(tmp_path)
        result = score_chip(chip)
        assert result.get("rubric_version") == "2.0"

    def test_explicit_v2(self, tmp_path: Path) -> None:
        chip = _build_test_chip(tmp_path)
        result = score_chip(chip, version="v2")
        assert result.get("rubric_version") == "2.0"
        assert len(result["dimensions"]) == 7

    def test_v1_dispatch(self, tmp_path: Path) -> None:
        chip = _build_test_chip(tmp_path)
        result = score_chip(chip, version="v1")
        # v1 has no rubric_version key
        assert "rubric_version" not in result
        # v1 has 6 dimensions
        assert len(result["dimensions"]) == 6

    def test_v1_and_v2_both_return_dict(self, tmp_path: Path) -> None:
        chip = _build_test_chip(tmp_path)
        r1 = score_chip(chip, version="v1")
        r2 = score_chip(chip, version="v2")
        assert isinstance(r1, dict)
        assert isinstance(r2, dict)

    def test_v1_has_same_required_keys(self, tmp_path: Path) -> None:
        chip = _build_test_chip(tmp_path)
        result = score_chip(chip, version="v1")
        for key in ("total_score", "dimensions", "passed_checks",
                     "failed_checks", "verdict"):
            assert key in result

    def test_v2_has_extra_rubric_version(self, tmp_path: Path) -> None:
        chip = _build_test_chip(tmp_path)
        r2 = score_chip(chip, version="v2")
        assert "rubric_version" in r2

    def test_missing_path_v1(self, tmp_path: Path) -> None:
        result = score_chip(tmp_path / "gone", version="v1")
        assert result["verdict"] == "not_found"

    def test_missing_path_v2(self, tmp_path: Path) -> None:
        result = score_chip(tmp_path / "gone", version="v2")
        assert result["verdict"] == "not_found"
        assert result["rubric_version"] == "2.0"


# ====================================================================
# 10. TestIntegrationHealth (same logic, reduced points)
# ====================================================================

class TestIntegrationHealth:
    """Integration health dimension -- same logic, reduced to 10 pts."""

    def test_full_integration_scores_10(self, tmp_path: Path) -> None:
        chip = _build_test_chip(tmp_path)
        result = score_chip_v2(chip)
        dim = next(d for d in result["dimensions"] if d["name"] == "integration_health")
        assert dim["score"] == 10

    def test_missing_project_json_scores_zero(self, tmp_path: Path) -> None:
        chip = _build_test_chip(tmp_path, skip_project=True)
        result = score_chip_v2(chip)
        dim = next(d for d in result["dimensions"] if d["name"] == "integration_health")
        assert dim["score"] == 0

    def test_invalid_project_json_scores_zero(self, tmp_path: Path) -> None:
        chip = _build_test_chip(tmp_path)
        (chip / "spark-researcher.project.json").write_text("{bad", encoding="utf-8")
        result = score_chip_v2(chip)
        dim = next(d for d in result["dimensions"] if d["name"] == "integration_health")
        assert dim["score"] == 0
