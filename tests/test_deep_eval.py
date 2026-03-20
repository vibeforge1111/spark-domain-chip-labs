"""Unit tests for the V3 deep evaluation engine.

Tests utility functions, individual dimension checkers, the orchestrator,
and anti-gaming detection.  Uses temporary chip directories -- no real
Desktop chips required.
"""

from __future__ import annotations

import json
import os
import textwrap
from pathlib import Path
from typing import Any

import pytest

from chip_labs.deep_eval import (
    DeepEvalResult,
    DimensionResult,
    _boundary_specificity,
    _causal_density,
    _content_density_words,
    _extract_doctrines,
    _extract_scores_from_runs,
    _extract_timestamps,
    _gini_coefficient,
    _jaccard_distance,
    _load_all_runs,
    _parse_contradictions,
    _spearman_rank_correlation,
    check_contradiction_rigor,
    check_doctrine_quality,
    check_empirical_velocity,
    check_evidence_integrity,
    check_flywheel_health,
    check_integration_maturity,
    check_manifest_structure,
    check_watchtower_depth,
    score_chip_v3,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def empty_chip(tmp_path: Path) -> Path:
    """Minimal empty chip directory with just a manifest."""
    chip = tmp_path / "domain-chip-test"
    chip.mkdir()
    (chip / "spark-chip.json").write_text(
        json.dumps({
            "schema": "spark-chip.v1",
            "io_protocol": "spark-hook-io.v1",
            "hooks": {
                "evaluate": {"command": "echo"},
                "suggest": {"command": "echo"},
                "packets": {"command": "echo"},
                "watchtower": {"command": "echo"},
            },
            "frontier": {"allowed_mutations": ["test"]},
        }),
        encoding="utf-8",
    )
    return chip


@pytest.fixture
def rich_chip(tmp_path: Path) -> Path:
    """Chip with substantial artifacts simulating genuine intelligence."""
    chip = tmp_path / "domain-chip-rich"
    chip.mkdir()

    # Manifest
    (chip / "spark-chip.json").write_text(
        json.dumps({
            "schema": "spark-chip.v1",
            "io_protocol": "spark-hook-io.v1",
            "hooks": {
                "evaluate": {"command": "python -m rich.evaluate"},
                "suggest": {"command": "python -m rich.suggest"},
                "packets": {"command": "python -m rich.packets"},
                "watchtower": {"command": "python -m rich.watchtower"},
            },
            "frontier": {"allowed_mutations": ["factor_weights", "scoring_model"]},
        }),
        encoding="utf-8",
    )

    # Project.json
    (chip / "spark-researcher.project.json").write_text(
        json.dumps({
            "project_name": "rich-test",
            "eval_metric": "quality_score",
            "metrics": {"quality_score": {}, "coverage": {}, "accuracy": {}},
            "candidate_trials": [
                {"name": "baseline", "mutations": {}},
                {"name": "v1", "mutations": {"weight": 0.5}},
                {"name": "v2", "mutations": {"weight": 0.8}},
            ],
        }),
        encoding="utf-8",
    )

    # Score history with 100 runs, ascending trajectory
    history = chip / "score_history.jsonl"
    lines = []
    import random
    rng = random.Random(42)
    for i in range(100):
        score = 0.3 + (i / 100.0) * 0.5 + rng.uniform(-0.02, 0.02)
        verdict = rng.choice(["improved", "baseline", "regressed", "deferred"])
        lines.append(json.dumps({
            "run_id": f"run_{i:04d}",
            "score": round(score, 4),
            "metric_value": round(score, 4),
            "verdict": verdict,
            "created_at": f"2026-03-{(i % 28) + 1:02d}T12:00:00Z",
        }))
    history.write_text("\n".join(lines), encoding="utf-8")

    # Doctrines with causal language
    (chip / "chip_skill.md").write_text(textwrap.dedent("""\
        # Domain Identity
        Rich domain chip for testing deep evaluation.

        ## Core Doctrines

        ### Doctrine 1: Quality over Quantity
        Because high-quality evaluations lead to better outcomes, therefore
        we prioritize depth of analysis over breadth. This results in more
        accurate scoring models that enable better decision-making. However,
        this only applies when we have at least 50 data points, as fewer
        samples lead to unreliable conclusions limited to 0.3 confidence.

        ### Doctrine 2: Iterative Improvement
        Due to the nature of machine learning, each iteration causes the
        model to learn new patterns. This enables progressive refinement
        that prevents stagnation. The boundary constraint is that we must
        not exceed 1000 iterations, as diminishing returns set in at 95%.

        ### Doctrine 3: Evidence-Based Decisions
        When empirical data contradicts our assumptions, then we update our
        beliefs accordingly. This leads to more robust conclusions because
        we avoid confirmation bias. The caveat is that this only works when
        our measurement instruments have at least 0.8 reliability, except
        in exploratory contexts where 0.5 suffices.

        ### Doctrine 4: Contradiction as Signal
        Regressions are not failures but learning opportunities. Because
        each regression reveals a boundary condition, therefore we document
        all contradictions with specific metrics and resolution paths.

        ## Future Work
        Not yet covered: real-time evaluation, multi-agent coordination.
    """), encoding="utf-8")

    # Research lanes
    for lane in ["research_grounded", "benchmark_grounded", "exploratory_frontier"]:
        lane_dir = chip / "research" / lane
        lane_dir.mkdir(parents=True)
        for j in range(5):
            (lane_dir / f"evidence_{j}.md").write_text(
                f"# Evidence {j}\n\n" + "Substantial research content with real findings. " * 40,
                encoding="utf-8",
            )

    # Packets
    packets_dir = chip / "research" / "packets"
    packets_dir.mkdir(parents=True)
    for j in range(15):
        (packets_dir / f"packet_{j}.json").write_text(
            json.dumps({
                "claim": f"Factor {j} improves outcomes",
                "mechanism": "Evaluated via chip:evaluate with quality_score=0.85. " +
                             "The mechanism works by adjusting weight parameters " +
                             "that influence the scoring function through gradient descent.",
                "boundary": f"Evidence count: {j * 10}. Verdict: improved. Baseline: 0.3",
            }),
            encoding="utf-8",
        )

    # Contradictions
    (chip / "CONTRADICTIONS.md").write_text(textwrap.dedent("""\
        # Belief Contradictions

        ## Regressed Factors (15 total)

        - **weight_0.9**: scored 0.45 vs baseline 0.52 (delta: -0.07)
        - **factor_decay**: scored 0.38 vs baseline 0.50 (delta: -0.12)
        - **learning_rate_high**: scored 0.29 vs baseline 0.48 (delta: -0.19)

        ## Resolution Policy

        1. Factors that regress are tagged `defer` rather than rejected outright
        2. Root cause analysis: weight_0.9 was resolved by reducing to 0.75
        3. factor_decay was addressed via exponential schedule in run_0042
        4. learning_rate_high was mitigated by adding warmup in 2026-03-15
    """), encoding="utf-8")

    # Obsidian vault
    vault = chip / "obsidian-vault"
    vault.mkdir()
    for page_name in ["Overview", "Architecture", "Research Log", "Decision Log"]:
        (vault / f"{page_name}.md").write_text(
            f"# {page_name}\n\n"
            + f"Strategic analysis of the {page_name.lower()} dimension. " * 50
            + "\n\n## Related\n\n"
            + "See [[Architecture]] and [[Research Log]] for details.\n",
            encoding="utf-8",
        )

    # src/ with scoring function
    src_dir = chip / "src" / "rich"
    src_dir.mkdir(parents=True)
    (src_dir / "__init__.py").write_text("", encoding="utf-8")
    (src_dir / "evaluate.py").write_text(textwrap.dedent("""\
        import dspy
        from dspy import Module

        def score(candidate, baseline, metrics):
            quality_score = metrics.get("quality_score", 0)
            coverage = metrics.get("coverage", 0)
            weight = 0.7 * quality_score + 0.3 * coverage
            if quality_score > 0.8:
                weight *= 1.1
            if coverage < 0.3:
                weight *= 0.5
            return weight
    """), encoding="utf-8")

    # DSPy config
    (chip / "dspy_config.json").write_text(
        json.dumps({"modules": {"evaluator": "src.rich.evaluate"}}),
        encoding="utf-8",
    )

    return chip


@pytest.fixture
def scaffolded_chip(tmp_path: Path) -> Path:
    """Chip with minimal scaffolded artifacts -- should score LOW."""
    chip = tmp_path / "domain-chip-scaffolded"
    chip.mkdir()

    (chip / "spark-chip.json").write_text(
        json.dumps({
            "schema": "spark-chip.v1",
            "io_protocol": "spark-hook-io.v1",
            "hooks": {"evaluate": {"command": "echo"}},
        }),
        encoding="utf-8",
    )

    # Minimal score history (3 identical scores, same day)
    history = chip / "score_history.jsonl"
    lines = []
    for i in range(3):
        lines.append(json.dumps({
            "run_id": f"run_{i}",
            "score": 0.5,
            "verdict": "baseline",
            "created_at": "2026-03-01T12:00:00Z",
        }))
    history.write_text("\n".join(lines), encoding="utf-8")

    # Generic chip_skill.md with no causal language
    (chip / "chip_skill.md").write_text(textwrap.dedent("""\
        # Domain Identity
        This is a domain chip for testing.

        ## Core Doctrines
        The chip provides evaluation capabilities.
        It supports multiple metrics and scoring.
        The system handles various input formats.
    """), encoding="utf-8")

    # One file per lane (minimal)
    for lane in ["research_grounded"]:
        lane_dir = chip / "research" / lane
        lane_dir.mkdir(parents=True)
        (lane_dir / "stub.md").write_text("# Stub\n\nMinimal content here.", encoding="utf-8")

    # Generic contradictions
    (chip / "CONTRADICTIONS.md").write_text(textwrap.dedent("""\
        # Belief Contradictions

        ## Status
        No active contradictions detected in the evaluation history.
    """), encoding="utf-8")

    return chip


# ---------------------------------------------------------------------------
# TestSpearman
# ---------------------------------------------------------------------------


class TestSpearman:
    """Spearman rank correlation utility."""

    def test_perfect_positive(self) -> None:
        assert _spearman_rank_correlation([1, 2, 3, 4, 5], [1, 2, 3, 4, 5]) == pytest.approx(1.0)

    def test_perfect_negative(self) -> None:
        assert _spearman_rank_correlation([1, 2, 3, 4, 5], [5, 4, 3, 2, 1]) == pytest.approx(-1.0)

    def test_no_correlation(self) -> None:
        rho = _spearman_rank_correlation([1, 2, 3, 4, 5], [3, 1, 5, 2, 4])
        assert -0.5 < rho < 0.5

    def test_too_few_points(self) -> None:
        assert _spearman_rank_correlation([1, 2], [2, 1]) == 0.0

    def test_empty(self) -> None:
        assert _spearman_rank_correlation([], []) == 0.0

    def test_ties(self) -> None:
        """Handles tied values."""
        rho = _spearman_rank_correlation([1, 1, 2, 3, 4], [1, 2, 3, 4, 5])
        assert isinstance(rho, float)


# ---------------------------------------------------------------------------
# TestGini
# ---------------------------------------------------------------------------


class TestGini:
    """Gini coefficient utility."""

    def test_perfect_equality(self) -> None:
        assert _gini_coefficient([10, 10, 10, 10]) == pytest.approx(0.0, abs=0.01)

    def test_inequality(self) -> None:
        gini = _gini_coefficient([0, 0, 0, 100])
        assert gini > 0.5

    def test_single_value(self) -> None:
        assert _gini_coefficient([42]) == 0.0

    def test_empty(self) -> None:
        assert _gini_coefficient([]) == 0.0

    def test_two_values(self) -> None:
        gini = _gini_coefficient([10, 10])
        assert gini == pytest.approx(0.0, abs=0.01)


# ---------------------------------------------------------------------------
# TestJaccard
# ---------------------------------------------------------------------------


class TestJaccard:
    """Jaccard distance utility."""

    def test_identical_sets(self) -> None:
        assert _jaccard_distance({"a", "b", "c"}, {"a", "b", "c"}) == pytest.approx(0.0)

    def test_disjoint_sets(self) -> None:
        assert _jaccard_distance({"a", "b"}, {"c", "d"}) == pytest.approx(1.0)

    def test_partial_overlap(self) -> None:
        d = _jaccard_distance({"a", "b", "c"}, {"b", "c", "d"})
        assert 0.0 < d < 1.0

    def test_both_empty(self) -> None:
        assert _jaccard_distance(set(), set()) == 1.0


# ---------------------------------------------------------------------------
# TestCausalDensity
# ---------------------------------------------------------------------------


class TestCausalDensity:
    """Causal density metric."""

    def test_no_causal_markers(self) -> None:
        assert _causal_density("This is a simple text without markers.") == pytest.approx(0.0)

    def test_has_causal_markers(self) -> None:
        text = "Because this leads to improvement, therefore we enable it."
        cd = _causal_density(text)
        assert cd > 0

    def test_empty_text(self) -> None:
        assert _causal_density("") == 0.0

    def test_high_density(self) -> None:
        text = "Because A leads to B, therefore C. Due to D, this results in E. Hence F enables G."
        cd = _causal_density(text)
        assert cd > 3.0


# ---------------------------------------------------------------------------
# TestBoundarySpecificity
# ---------------------------------------------------------------------------


class TestBoundarySpecificity:
    """Boundary specificity metric."""

    def test_no_boundaries(self) -> None:
        assert _boundary_specificity("Simple text here.\nAnother line.") == pytest.approx(0.0)

    def test_has_boundaries(self) -> None:
        text = "Only when X applies.\nLimited to 50%.\nExcept in edge cases."
        bs = _boundary_specificity(text)
        assert bs > 0.5

    def test_empty(self) -> None:
        assert _boundary_specificity("") == 0.0


# ---------------------------------------------------------------------------
# TestContentDensity
# ---------------------------------------------------------------------------


class TestContentDensity:
    """Content density word count."""

    def test_normal_file(self, tmp_path: Path) -> None:
        f = tmp_path / "test.md"
        f.write_text("# Header\n\nThis is some content with words.\n\nMore content here.")
        assert _content_density_words(f) > 0

    def test_only_headers(self, tmp_path: Path) -> None:
        f = tmp_path / "test.md"
        f.write_text("# Header\n## Subheader\n### Another")
        assert _content_density_words(f) == 0

    def test_missing_file(self, tmp_path: Path) -> None:
        assert _content_density_words(tmp_path / "nonexistent.md") == 0


# ---------------------------------------------------------------------------
# TestLoadRuns
# ---------------------------------------------------------------------------


class TestLoadRuns:
    """Run loading from multiple sources."""

    def test_loads_from_score_history(self, tmp_path: Path) -> None:
        chip = tmp_path / "chip"
        chip.mkdir()
        history = chip / "score_history.jsonl"
        history.write_text(
            json.dumps({"run_id": "r1", "score": 0.5}) + "\n"
            + json.dumps({"run_id": "r2", "score": 0.7}) + "\n"
        )
        runs = _load_all_runs(chip)
        assert len(runs) == 2

    def test_deduplicates(self, tmp_path: Path) -> None:
        chip = tmp_path / "chip"
        chip.mkdir()
        # Same run_id in two files
        (chip / "score_history.jsonl").write_text(
            json.dumps({"run_id": "r1", "score": 0.5}) + "\n"
        )
        ledger_dir = chip / "artifacts" / "ledger"
        ledger_dir.mkdir(parents=True)
        (ledger_dir / "runs.jsonl").write_text(
            json.dumps({"run_id": "r1", "score": 0.6}) + "\n"
        )
        runs = _load_all_runs(chip)
        assert len(runs) == 1

    def test_empty_chip(self, tmp_path: Path) -> None:
        chip = tmp_path / "chip"
        chip.mkdir()
        assert _load_all_runs(chip) == []


# ---------------------------------------------------------------------------
# TestExtractDoctrines
# ---------------------------------------------------------------------------


class TestExtractDoctrines:
    def test_extracts_from_skill_file(self, tmp_path: Path) -> None:
        chip = tmp_path / "chip"
        chip.mkdir()
        (chip / "chip_skill.md").write_text(
            "# Identity\nSome intro text that is long enough to count as a section.\n\n"
            "## Doctrine 1\nBecause X leads to Y, we do Z. This is a substantial section.\n"
        )
        doctrines = _extract_doctrines(chip)
        assert len(doctrines) >= 1

    def test_empty_chip(self, tmp_path: Path) -> None:
        chip = tmp_path / "chip"
        chip.mkdir()
        assert _extract_doctrines(chip) == []


# ---------------------------------------------------------------------------
# TestParseContradictions
# ---------------------------------------------------------------------------


class TestParseContradictions:
    def test_parses_entries(self, tmp_path: Path) -> None:
        chip = tmp_path / "chip"
        chip.mkdir()
        (chip / "CONTRADICTIONS.md").write_text(
            "# Contradictions\n\n"
            "- **factor_a**: scored 0.3 vs baseline 0.5\n"
            "- **factor_b**: scored 0.2 vs baseline 0.4\n"
        )
        entries, full_text = _parse_contradictions(chip)
        assert len(entries) == 2
        assert "factor_a" in full_text

    def test_empty_chip(self, tmp_path: Path) -> None:
        chip = tmp_path / "chip"
        chip.mkdir()
        entries, full_text = _parse_contradictions(chip)
        assert entries == []
        assert full_text == ""


# ---------------------------------------------------------------------------
# TestCheckManifestStructure
# ---------------------------------------------------------------------------


class TestCheckManifestStructure:
    def test_full_manifest(self, empty_chip: Path) -> None:
        result = check_manifest_structure(empty_chip)
        assert result.score >= 4.0  # Valid manifest with 4 hooks
        assert result.max_points == 10.0

    def test_no_manifest(self, tmp_path: Path) -> None:
        chip = tmp_path / "chip"
        chip.mkdir()
        result = check_manifest_structure(chip)
        assert result.score == 0.0

    def test_with_project_json(self, rich_chip: Path) -> None:
        result = check_manifest_structure(rich_chip)
        assert result.score >= 8.0  # Full manifest + project + scoring function


# ---------------------------------------------------------------------------
# TestCheckEmpiricalVelocity
# ---------------------------------------------------------------------------


class TestCheckEmpiricalVelocity:
    def test_rich_chip_high_velocity(self, rich_chip: Path) -> None:
        result = check_empirical_velocity(rich_chip)
        assert result.score >= 10.0  # 100 runs, ascending, diverse verdicts
        assert result.details["run_count"] == 100

    def test_empty_chip_zero_velocity(self, empty_chip: Path) -> None:
        result = check_empirical_velocity(empty_chip)
        assert result.score == 0.0

    def test_scaffolded_low_velocity(self, scaffolded_chip: Path) -> None:
        result = check_empirical_velocity(scaffolded_chip)
        assert result.score < 8.0  # Only 3 runs, 1 verdict -- may get recency points

    def test_max_points(self, rich_chip: Path) -> None:
        result = check_empirical_velocity(rich_chip)
        assert result.max_points == 18.0


# ---------------------------------------------------------------------------
# TestCheckDoctrineQuality
# ---------------------------------------------------------------------------


class TestCheckDoctrineQuality:
    def test_rich_doctrines(self, rich_chip: Path) -> None:
        result = check_doctrine_quality(rich_chip)
        assert result.score >= 8.0  # Rich causal language + boundaries + uniqueness

    def test_scaffolded_low_quality(self, scaffolded_chip: Path) -> None:
        result = check_doctrine_quality(scaffolded_chip)
        assert result.score < 5.0

    def test_empty_chip(self, empty_chip: Path) -> None:
        result = check_doctrine_quality(empty_chip)
        assert result.score == 0.0


# ---------------------------------------------------------------------------
# TestCheckEvidenceIntegrity
# ---------------------------------------------------------------------------


class TestCheckEvidenceIntegrity:
    def test_rich_evidence(self, rich_chip: Path) -> None:
        result = check_evidence_integrity(rich_chip)
        assert result.score >= 8.0  # 3 lanes, dense content, structured packets

    def test_scaffolded_low_evidence(self, scaffolded_chip: Path) -> None:
        result = check_evidence_integrity(scaffolded_chip)
        assert result.score < 3.0

    def test_empty_chip(self, empty_chip: Path) -> None:
        result = check_evidence_integrity(empty_chip)
        assert result.score == 0.0


# ---------------------------------------------------------------------------
# TestCheckContradictionRigor
# ---------------------------------------------------------------------------


class TestCheckContradictionRigor:
    def test_rich_contradictions(self, rich_chip: Path) -> None:
        result = check_contradiction_rigor(rich_chip)
        assert result.score >= 6.0  # Specific contradictions + resolutions

    def test_empty_chip(self, empty_chip: Path) -> None:
        result = check_contradiction_rigor(empty_chip)
        assert result.score <= 2.0

    def test_scaffolded_generic(self, scaffolded_chip: Path) -> None:
        result = check_contradiction_rigor(scaffolded_chip)
        assert result.score < 4.0


# ---------------------------------------------------------------------------
# TestCheckFlywheelHealth
# ---------------------------------------------------------------------------


class TestCheckFlywheelHealth:
    def test_rich_flywheel(self, rich_chip: Path) -> None:
        result = check_flywheel_health(rich_chip)
        assert result.score >= 5.0

    def test_empty_chip(self, empty_chip: Path) -> None:
        result = check_flywheel_health(empty_chip)
        assert result.score == 0.0

    def test_scaffolded_low(self, scaffolded_chip: Path) -> None:
        result = check_flywheel_health(scaffolded_chip)
        assert result.score < 5.0


# ---------------------------------------------------------------------------
# TestCheckWatchtowerDepth
# ---------------------------------------------------------------------------


class TestCheckWatchtowerDepth:
    def test_rich_vault(self, rich_chip: Path) -> None:
        result = check_watchtower_depth(rich_chip)
        assert result.score >= 5.0  # 4 pages, good content, cross-refs

    def test_no_vault(self, empty_chip: Path) -> None:
        result = check_watchtower_depth(empty_chip)
        assert result.score == 0.0


# ---------------------------------------------------------------------------
# TestCheckIntegrationMaturity
# ---------------------------------------------------------------------------


class TestCheckIntegrationMaturity:
    def test_rich_integration(self, rich_chip: Path) -> None:
        result = check_integration_maturity(rich_chip)
        assert result.score >= 6.0  # DSPy + scoring + hooks

    def test_empty_chip(self, empty_chip: Path) -> None:
        result = check_integration_maturity(empty_chip)
        # Has 4 hooks but nothing else
        assert result.score >= 2.0


# ---------------------------------------------------------------------------
# TestScoreChipV3 (Orchestrator)
# ---------------------------------------------------------------------------


class TestScoreChipV3:
    def test_returns_deep_eval_result(self, rich_chip: Path) -> None:
        result = score_chip_v3(rich_chip)
        assert isinstance(result, DeepEvalResult)

    def test_has_8_dimensions(self, rich_chip: Path) -> None:
        result = score_chip_v3(rich_chip)
        assert len(result.dimensions) == 8

    def test_rich_chip_high_score(self, rich_chip: Path) -> None:
        result = score_chip_v3(rich_chip)
        assert result.total_score >= 50.0

    def test_empty_chip_low_score(self, empty_chip: Path) -> None:
        result = score_chip_v3(empty_chip)
        assert result.total_score < 20.0

    def test_verdict_is_valid(self, rich_chip: Path) -> None:
        result = score_chip_v3(rich_chip)
        assert result.verdict in ("production_ready", "beta", "alpha", "scaffold")

    def test_rubric_version(self, rich_chip: Path) -> None:
        result = score_chip_v3(rich_chip)
        assert result.rubric_version == "3.0"

    def test_has_gaps_and_strengths(self, rich_chip: Path) -> None:
        result = score_chip_v3(rich_chip)
        assert isinstance(result.gaps, list)
        assert isinstance(result.strengths, list)

    def test_has_depth_profile(self, rich_chip: Path) -> None:
        result = score_chip_v3(rich_chip)
        assert len(result.depth_profile) == 8

    def test_nonexistent_chip(self, tmp_path: Path) -> None:
        result = score_chip_v3(tmp_path / "nonexistent")
        assert result.total_score == 0.0
        assert result.verdict == "not_found"

    def test_as_dict(self, rich_chip: Path) -> None:
        result = score_chip_v3(rich_chip)
        d = result.as_dict()
        assert "total_score" in d
        assert "dimensions" in d
        assert "gaps" in d
        assert "anti_gaming_flags" in d

    def test_dimension_sum_equals_total(self, rich_chip: Path) -> None:
        result = score_chip_v3(rich_chip)
        dim_sum = sum(d.score for d in result.dimensions)
        assert abs(dim_sum - result.total_score) < 0.2  # rounding tolerance

    def test_max_possible_is_100(self, rich_chip: Path) -> None:
        result = score_chip_v3(rich_chip)
        max_sum = sum(d.max_points for d in result.dimensions)
        assert max_sum == 100.0


# ---------------------------------------------------------------------------
# TestAntiGaming
# ---------------------------------------------------------------------------


class TestAntiGaming:
    """Verify anti-gaming detection catches suspicious patterns."""

    def test_scaffolded_scores_much_lower(self, rich_chip: Path, scaffolded_chip: Path) -> None:
        """Core anti-gaming test: rich chip >> scaffolded chip."""
        rich_result = score_chip_v3(rich_chip)
        scaffolded_result = score_chip_v3(scaffolded_chip)
        assert rich_result.total_score > scaffolded_result.total_score + 25, (
            f"Rich ({rich_result.total_score}) should be 25+ points above "
            f"scaffolded ({scaffolded_result.total_score})"
        )

    def test_identical_scores_flagged(self, tmp_path: Path) -> None:
        """Chip with identical run scores should be flagged."""
        chip = tmp_path / "domain-chip-gaming"
        chip.mkdir()
        (chip / "spark-chip.json").write_text(
            json.dumps({"schema": "spark-chip.v1", "io_protocol": "spark-hook-io.v1", "hooks": {}}),
            encoding="utf-8",
        )
        history = chip / "score_history.jsonl"
        lines = [
            json.dumps({"run_id": f"r{i}", "score": 0.5, "created_at": "2026-03-01T12:00:00Z"})
            for i in range(10)
        ]
        history.write_text("\n".join(lines), encoding="utf-8")
        result = score_chip_v3(chip)
        assert "identical_scores" in result.anti_gaming_flags

    def test_batch_generation_flagged(self, tmp_path: Path) -> None:
        """Runs all on same day should be flagged."""
        chip = tmp_path / "domain-chip-batch"
        chip.mkdir()
        (chip / "spark-chip.json").write_text(
            json.dumps({"schema": "spark-chip.v1", "io_protocol": "spark-hook-io.v1", "hooks": {}}),
            encoding="utf-8",
        )
        history = chip / "score_history.jsonl"
        lines = [
            json.dumps({
                "run_id": f"r{i}",
                "score": 0.5 + i * 0.01,
                "created_at": "2026-03-15T12:00:00Z",
            })
            for i in range(15)
        ]
        history.write_text("\n".join(lines), encoding="utf-8")
        result = score_chip_v3(chip)
        assert "single_day_batch" in result.anti_gaming_flags

    def test_high_structure_low_velocity_flagged(self, empty_chip: Path) -> None:
        """Full manifest but no runs should be flagged."""
        result = score_chip_v3(empty_chip)
        assert "high_structure_low_velocity" in result.anti_gaming_flags
