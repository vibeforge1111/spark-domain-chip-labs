"""Tests for the shared scoring engine.

Covers:
    - Basic scoring with empty mutations (base_score)
    - Scoring with dimension deltas
    - Pair bonuses
    - System bonuses
    - Clamping behaviour
    - Verdict thresholds
    - from_brief() factory
    - from_manifest() factory
    - Bulk scoring and leaderboard
    - ScoringConfigBuilder fluent API
    - Evidence lane classification
    - Edge cases (unknown dimensions, broken conditions)
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from chip_labs.scoring_engine import (
    MutationScoringEngine,
    ScoringConfig,
    ScoringConfigBuilder,
    SystemBonus,
    from_brief,
    from_manifest,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _minimal_config(**overrides: object) -> ScoringConfig:
    """Build a minimal ScoringConfig with optional overrides."""
    defaults = {
        "base_score": 50,
        "dimensions": {
            "regime": {"bull": 10, "bear": -5, "crisis": -15},
            "strategy": {"momentum": 8, "mean_reversion": 4},
        },
    }
    defaults.update(overrides)
    return ScoringConfig(**defaults)


def _engine_with_everything() -> MutationScoringEngine:
    """Build an engine that exercises all scoring components."""
    config = (
        ScoringConfigBuilder()
        .set_base_score(50)
        .add_dimension("regime", {"bull": 10, "bear": -5, "crisis": -15})
        .add_dimension("strategy", {"momentum": 8, "mean_reversion": 4})
        .add_pair_bonus("regime", "bull", "strategy", "momentum", 5)
        .add_system_bonus(
            "paper_gate", -20,
            lambda m: m.get("paper_trade") == "fail",
        )
        .add_system_bonus(
            "live_bonus", 3,
            lambda m: m.get("live_validated") is True,
        )
        .set_thresholds(approve=70, defer=40)
        .add_evidence_lane_rule("regime=crisis", "realworld_validated")
        .build()
    )
    return MutationScoringEngine(config)


# ===================================================================
# 1. Basic scoring -- empty mutations
# ===================================================================

class TestEmptyMutations:

    def test_empty_mutations_return_base_score(self) -> None:
        engine = MutationScoringEngine(_minimal_config())
        result = engine.score({})
        assert result.total == 50

    def test_empty_mutations_no_breakdown(self) -> None:
        engine = MutationScoringEngine(_minimal_config())
        result = engine.score({})
        assert result.breakdown == {}

    def test_empty_mutations_zero_pair_bonus(self) -> None:
        engine = MutationScoringEngine(_minimal_config())
        result = engine.score({})
        assert result.pair_bonus_total == 0.0

    def test_empty_mutations_zero_system_bonus(self) -> None:
        engine = MutationScoringEngine(_minimal_config())
        result = engine.score({})
        assert result.system_bonus_total == 0.0

    def test_empty_mutations_echo_back(self) -> None:
        engine = MutationScoringEngine(_minimal_config())
        result = engine.score({})
        assert result.mutations == {}

    def test_empty_mutations_verdict_is_defer(self) -> None:
        """Base 50 is above default defer (40) but below approve (70)."""
        engine = MutationScoringEngine(_minimal_config())
        result = engine.score({})
        assert result.verdict == "defer"


# ===================================================================
# 2. Dimension deltas
# ===================================================================

class TestDimensionDeltas:

    def test_single_positive_delta(self) -> None:
        engine = MutationScoringEngine(_minimal_config())
        result = engine.score({"regime": "bull"})
        assert result.total == 60  # 50 + 10

    def test_single_negative_delta(self) -> None:
        engine = MutationScoringEngine(_minimal_config())
        result = engine.score({"regime": "bear"})
        assert result.total == 45  # 50 - 5

    def test_multiple_dimension_deltas(self) -> None:
        engine = MutationScoringEngine(_minimal_config())
        result = engine.score({"regime": "bull", "strategy": "momentum"})
        assert result.total == 68  # 50 + 10 + 8

    def test_unknown_dimension_ignored(self) -> None:
        engine = MutationScoringEngine(_minimal_config())
        result = engine.score({"nonexistent": "foo"})
        assert result.total == 50

    def test_unknown_value_ignored(self) -> None:
        engine = MutationScoringEngine(_minimal_config())
        result = engine.score({"regime": "unknown_regime"})
        assert result.total == 50
        assert "regime" not in result.breakdown

    def test_breakdown_records_each_dimension(self) -> None:
        engine = MutationScoringEngine(_minimal_config())
        result = engine.score({"regime": "bull", "strategy": "mean_reversion"})
        assert result.breakdown["regime"] == {"value": "bull", "delta": 10}
        assert result.breakdown["strategy"] == {"value": "mean_reversion", "delta": 4}

    def test_large_negative_delta_does_not_crash(self) -> None:
        """Score can go below base but clamping prevents going below 0."""
        config = _minimal_config(
            dimensions={"doom": {"total": -999}},
        )
        engine = MutationScoringEngine(config)
        result = engine.score({"doom": "total"})
        assert result.total == 0  # clamped at 0


# ===================================================================
# 3. Pair bonuses
# ===================================================================

class TestPairBonuses:

    def test_pair_bonus_applied_when_both_match(self) -> None:
        engine = _engine_with_everything()
        result = engine.score({"regime": "bull", "strategy": "momentum"})
        assert result.pair_bonus_total == 5
        assert result.total == 73  # 50 + 10 + 8 + 5

    def test_pair_bonus_not_applied_when_only_one_matches(self) -> None:
        engine = _engine_with_everything()
        result = engine.score({"regime": "bull", "strategy": "mean_reversion"})
        assert result.pair_bonus_total == 0

    def test_pair_bonus_not_applied_when_neither_matches(self) -> None:
        engine = _engine_with_everything()
        result = engine.score({"regime": "bear"})
        assert result.pair_bonus_total == 0

    def test_pair_bonus_details_populated(self) -> None:
        engine = _engine_with_everything()
        result = engine.score({"regime": "bull", "strategy": "momentum"})
        assert len(result.pair_bonus_details) == 1
        detail = result.pair_bonus_details[0]
        assert detail["bonus"] == 5
        assert "regime=bull" in detail["label"]
        assert "strategy=momentum" in detail["label"]

    def test_multiple_pair_bonuses(self) -> None:
        config = (
            ScoringConfigBuilder()
            .set_base_score(50)
            .add_dimension("a", {"x": 0})
            .add_dimension("b", {"y": 0})
            .add_dimension("c", {"z": 0})
            .add_pair_bonus("a", "x", "b", "y", 3)
            .add_pair_bonus("b", "y", "c", "z", 7)
            .build()
        )
        engine = MutationScoringEngine(config)
        result = engine.score({"a": "x", "b": "y", "c": "z"})
        assert result.pair_bonus_total == 10


# ===================================================================
# 4. System bonuses
# ===================================================================

class TestSystemBonuses:

    def test_system_penalty_applied(self) -> None:
        engine = _engine_with_everything()
        result = engine.score({"paper_trade": "fail"})
        assert result.system_bonus_total == -20
        assert result.total == 30  # 50 - 20

    def test_system_bonus_applied(self) -> None:
        engine = _engine_with_everything()
        result = engine.score({"live_validated": True})
        assert result.system_bonus_total == 3

    def test_system_bonus_not_applied_when_condition_false(self) -> None:
        engine = _engine_with_everything()
        result = engine.score({"paper_trade": "pass"})
        assert result.system_bonus_total == 0

    def test_system_bonus_details_populated(self) -> None:
        engine = _engine_with_everything()
        result = engine.score({"paper_trade": "fail"})
        assert len(result.system_bonus_details) == 1
        assert result.system_bonus_details[0]["label"] == "paper_gate"
        assert result.system_bonus_details[0]["bonus"] == -20

    def test_broken_condition_does_not_crash(self) -> None:
        """A condition that raises should be silently skipped."""
        config = ScoringConfig(
            base_score=50,
            system_bonuses=[
                SystemBonus(
                    label="broken",
                    bonus=99,
                    condition=lambda m: 1 / 0,  # always raises
                ),
            ],
        )
        engine = MutationScoringEngine(config)
        result = engine.score({})
        assert result.total == 50
        assert result.system_bonus_total == 0


# ===================================================================
# 5. Clamping behaviour
# ===================================================================

class TestClamping:

    def test_clamp_to_100(self) -> None:
        config = _minimal_config(base_score=95)
        engine = MutationScoringEngine(config)
        result = engine.score({"regime": "bull"})
        # 95 + 10 = 105 -> clamped to 100
        assert result.total == 100

    def test_clamp_to_zero(self) -> None:
        config = _minimal_config(base_score=10)
        engine = MutationScoringEngine(config)
        result = engine.score({"regime": "crisis"})
        # 10 - 15 = -5 -> clamped to 0
        assert result.total == 0

    def test_custom_clamp_range(self) -> None:
        config = _minimal_config(clamp_range=(20.0, 80.0))
        engine = MutationScoringEngine(config)

        high = engine.score({"regime": "bull", "strategy": "momentum"})
        assert high.total == 68  # 50+10+8=68, within range

        low = engine.score({"regime": "crisis"})
        assert low.total == 35  # 50-15=35, within range

    def test_custom_clamp_enforces_floor(self) -> None:
        config = _minimal_config(
            base_score=10,
            clamp_range=(25.0, 80.0),
        )
        engine = MutationScoringEngine(config)
        result = engine.score({"regime": "crisis"})
        # 10 - 15 = -5 -> clamped to 25
        assert result.total == 25

    def test_custom_clamp_enforces_ceiling(self) -> None:
        config = _minimal_config(
            base_score=90,
            clamp_range=(25.0, 80.0),
        )
        engine = MutationScoringEngine(config)
        result = engine.score({"regime": "bull"})
        # 90 + 10 = 100 -> clamped to 80
        assert result.total == 80


# ===================================================================
# 6. Verdict thresholds
# ===================================================================

class TestVerdictThresholds:

    def test_approve_at_threshold(self) -> None:
        config = _minimal_config(base_score=70)
        engine = MutationScoringEngine(config)
        result = engine.score({})
        assert result.verdict == "approve"

    def test_approve_above_threshold(self) -> None:
        config = _minimal_config(base_score=85)
        engine = MutationScoringEngine(config)
        result = engine.score({})
        assert result.verdict == "approve"

    def test_defer_at_threshold(self) -> None:
        config = _minimal_config(base_score=40)
        engine = MutationScoringEngine(config)
        result = engine.score({})
        assert result.verdict == "defer"

    def test_defer_between_thresholds(self) -> None:
        config = _minimal_config(base_score=55)
        engine = MutationScoringEngine(config)
        result = engine.score({})
        assert result.verdict == "defer"

    def test_reject_below_defer(self) -> None:
        config = _minimal_config(base_score=30)
        engine = MutationScoringEngine(config)
        result = engine.score({})
        assert result.verdict == "reject"

    def test_custom_thresholds(self) -> None:
        config = _minimal_config(
            base_score=50,
            approve_threshold=80.0,
            defer_threshold=30.0,
        )
        engine = MutationScoringEngine(config)

        assert engine.score({}).verdict == "defer"  # 50 >= 30 but < 80
        assert engine.score({"regime": "bull", "strategy": "momentum"}).verdict == "defer"  # 68 < 80
        assert engine.score({"regime": "crisis"}).verdict == "defer"  # 35 >= 30


# ===================================================================
# 7. Evidence lane classification
# ===================================================================

class TestEvidenceLanes:

    def test_empty_mutations_use_default_lane(self) -> None:
        engine = _engine_with_everything()
        result = engine.score({})
        assert result.evidence_lane == "benchmark_grounded"

    def test_rule_match_overrides_default(self) -> None:
        engine = _engine_with_everything()
        result = engine.score({"regime": "crisis"})
        assert result.evidence_lane == "realworld_validated"

    def test_no_rule_match_uses_exploratory(self) -> None:
        engine = _engine_with_everything()
        result = engine.score({"regime": "bull"})
        assert result.evidence_lane == "exploratory_frontier"

    def test_custom_default_evidence_lane(self) -> None:
        config = (
            ScoringConfigBuilder()
            .set_base_score(50)
            .set_default_evidence_lane("research_grounded")
            .build()
        )
        engine = MutationScoringEngine(config)
        result = engine.score({})
        assert result.evidence_lane == "research_grounded"


# ===================================================================
# 8. from_brief() factory
# ===================================================================

class TestFromBrief:

    def test_minimal_brief(self) -> None:
        brief = {
            "domain_id": "test-chip",
            "domain_name": "Test Chip",
            "primary_metric": "test_score",
            "mutation_axes": [
                {"name": "style", "values": ["bold", "subtle", "minimal"]},
            ],
        }
        config = from_brief(brief)
        assert config.base_score == 50
        assert "style" in config.dimensions
        assert config.dimensions["style"]["bold"] == 2
        assert config.dimensions["style"]["subtle"] == 4
        assert config.dimensions["style"]["minimal"] == 6

    def test_custom_base_score(self) -> None:
        brief = {
            "domain_id": "t",
            "mutation_axes": [],
            "base_score": 42,
        }
        config = from_brief(brief)
        assert config.base_score == 42

    def test_custom_thresholds(self) -> None:
        brief = {
            "domain_id": "t",
            "mutation_axes": [],
            "approve_threshold": 80,
            "defer_threshold": 30,
        }
        config = from_brief(brief)
        assert config.approve_threshold == 80
        assert config.defer_threshold == 30

    def test_explicit_dimensions_override_axes(self) -> None:
        brief = {
            "domain_id": "t",
            "mutation_axes": [{"name": "a", "values": ["x"]}],
            "dimensions": {"custom": {"val": 99}},
        }
        config = from_brief(brief)
        assert "custom" in config.dimensions
        assert config.dimensions["custom"]["val"] == 99
        # mutation_axes should NOT be auto-generated when explicit dims given
        assert "a" not in config.dimensions

    def test_pair_bonuses_from_brief(self) -> None:
        brief = {
            "domain_id": "t",
            "mutation_axes": [],
            "pair_bonuses": [
                {"dim_a": "a", "val_a": "x", "dim_b": "b", "val_b": "y", "bonus": 7},
            ],
        }
        config = from_brief(brief)
        assert len(config.pair_bonuses) == 1
        assert config.pair_bonuses[0].bonus == 7

    def test_evidence_lane_rules_from_brief(self) -> None:
        brief = {
            "domain_id": "t",
            "mutation_axes": [],
            "evidence_lane_rules": {"regime=live": "realworld_validated"},
        }
        config = from_brief(brief)
        assert config.evidence_lane_rules["regime=live"] == "realworld_validated"

    def test_empty_brief_produces_valid_config(self) -> None:
        config = from_brief({"domain_id": "empty", "mutation_axes": []})
        engine = MutationScoringEngine(config)
        result = engine.score({})
        assert result.total == 50
        assert result.verdict == "defer"

    def test_multi_axis_brief(self) -> None:
        """Simulate a web-designer-like brief with many axes."""
        brief = {
            "domain_id": "web-designer",
            "domain_name": "Web Designer",
            "primary_metric": "design_quality_score",
            "mutation_axes": [
                {"name": "site_type", "values": ["saas_landing", "portfolio", "ecommerce"]},
                {"name": "design_direction", "values": ["minimal", "expressive", "brutalist"]},
                {"name": "narrative", "values": ["story_driven", "data_driven"]},
                {"name": "interaction", "values": ["scroll_based", "click_based"]},
                {"name": "proof", "values": ["social_proof", "case_studies"]},
                {"name": "conversion", "values": ["cta_focused", "educational"]},
                {"name": "accessibility", "values": ["wcag_aa", "wcag_aaa"]},
            ],
        }
        config = from_brief(brief)
        assert len(config.dimensions) == 7
        engine = MutationScoringEngine(config)

        # Score a full mutation set
        mutations = {
            "site_type": "saas_landing",
            "design_direction": "minimal",
            "narrative": "story_driven",
            "interaction": "scroll_based",
            "proof": "social_proof",
            "conversion": "cta_focused",
            "accessibility": "wcag_aa",
        }
        result = engine.score(mutations)
        # Each axis uses (index+1)*2, all first values -> delta 2 each
        # 50 + 7 * 2 = 64
        assert result.total == 64
        assert len(result.breakdown) == 7


# ===================================================================
# 9. from_manifest() factory
# ===================================================================

class TestFromManifest:

    def test_from_manifest_reads_allowed_mutations(self, tmp_path: Path) -> None:
        manifest = {
            "schema_version": "spark-chip.v1",
            "frontier": {
                "enabled": True,
                "allowed_mutations": {
                    "regime": ["bull", "bear", "crisis"],
                    "strategy": ["momentum", "arb"],
                },
            },
        }
        manifest_path = tmp_path / "spark-chip.json"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

        config = from_manifest(manifest_path)
        assert "regime" in config.dimensions
        assert config.dimensions["regime"]["bull"] == 2
        assert config.dimensions["regime"]["bear"] == 4
        assert config.dimensions["regime"]["crisis"] == 6
        assert "strategy" in config.dimensions

    def test_from_manifest_missing_file_raises(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            from_manifest(tmp_path / "nonexistent.json")

    def test_from_manifest_empty_frontier(self, tmp_path: Path) -> None:
        manifest = {"schema_version": "spark-chip.v1"}
        manifest_path = tmp_path / "spark-chip.json"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

        config = from_manifest(manifest_path)
        assert config.dimensions == {}
        assert config.base_score == 50

    def test_from_manifest_produces_scorable_config(self, tmp_path: Path) -> None:
        manifest = {
            "schema_version": "spark-chip.v1",
            "frontier": {
                "allowed_mutations": {
                    "quality": ["high", "medium", "low"],
                },
            },
        }
        manifest_path = tmp_path / "spark-chip.json"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

        config = from_manifest(manifest_path)
        engine = MutationScoringEngine(config)
        result = engine.score({"quality": "high"})
        assert result.total == 52  # 50 + 2 (first value delta)


# ===================================================================
# 10. Bulk scoring and leaderboard
# ===================================================================

class TestBulkAndLeaderboard:

    def test_bulk_score_preserves_order(self) -> None:
        engine = MutationScoringEngine(_minimal_config())
        mutations = [
            {"regime": "crisis"},   # 50 - 15 = 35
            {"regime": "bull"},     # 50 + 10 = 60
            {},                     # 50
        ]
        results = engine.bulk_score(mutations)
        assert len(results) == 3
        assert results[0].total == 35
        assert results[1].total == 60
        assert results[2].total == 50

    def test_bulk_score_empty_list(self) -> None:
        engine = MutationScoringEngine(_minimal_config())
        results = engine.bulk_score([])
        assert results == []

    def test_leaderboard_sorted_descending(self) -> None:
        engine = MutationScoringEngine(_minimal_config())
        mutations = [
            {"regime": "crisis"},           # 35
            {"regime": "bull"},             # 60
            {},                             # 50
            {"strategy": "momentum"},       # 58
            {"regime": "bull", "strategy": "momentum"},  # 68
        ]
        top = engine.leaderboard(mutations, top_n=3)
        assert len(top) == 3
        assert top[0].total >= top[1].total >= top[2].total
        assert top[0].total == 68
        assert top[1].total == 60
        assert top[2].total == 58

    def test_leaderboard_top_n_exceeds_list(self) -> None:
        engine = MutationScoringEngine(_minimal_config())
        mutations = [{"regime": "bull"}, {}]
        top = engine.leaderboard(mutations, top_n=100)
        assert len(top) == 2

    def test_leaderboard_default_top_n(self) -> None:
        engine = MutationScoringEngine(_minimal_config())
        mutations = [{}] * 15
        top = engine.leaderboard(mutations)
        assert len(top) == 10  # default top_n=10


# ===================================================================
# 11. ScoringConfigBuilder fluent API
# ===================================================================

class TestScoringConfigBuilder:

    def test_builder_default_config(self) -> None:
        config = ScoringConfigBuilder().build()
        assert config.base_score == 50
        assert config.dimensions == {}
        assert config.pair_bonuses == []
        assert config.system_bonuses == []
        assert config.clamp_range == (0.0, 100.0)
        assert config.approve_threshold == 70.0
        assert config.defer_threshold == 40.0

    def test_builder_chaining(self) -> None:
        """All setters should return self for chaining."""
        builder = ScoringConfigBuilder()
        result = (
            builder
            .set_base_score(60)
            .add_dimension("x", {"a": 1})
            .add_pair_bonus("x", "a", "y", "b", 2)
            .add_system_bonus("test", 1, lambda m: True)
            .set_thresholds(approve=80, defer=50)
            .set_clamp_range(10, 90)
            .add_evidence_lane_rule("x=a", "research_grounded")
            .set_default_evidence_lane("benchmark_grounded")
        )
        assert result is builder

    def test_builder_produces_valid_engine(self) -> None:
        config = (
            ScoringConfigBuilder()
            .set_base_score(45)
            .add_dimension("color", {"red": 5, "blue": -2})
            .set_thresholds(approve=60, defer=35)
            .build()
        )
        engine = MutationScoringEngine(config)

        red = engine.score({"color": "red"})
        assert red.total == 50  # 45 + 5
        assert red.verdict == "defer"  # 50 >= 35 but < 60

        blue = engine.score({"color": "blue"})
        assert blue.total == 43  # 45 - 2

    def test_builder_add_dimension_replaces(self) -> None:
        """Adding the same dimension twice should replace it."""
        config = (
            ScoringConfigBuilder()
            .add_dimension("x", {"a": 1})
            .add_dimension("x", {"a": 99})
            .build()
        )
        assert config.dimensions["x"]["a"] == 99

    def test_builder_set_clamp_range(self) -> None:
        config = (
            ScoringConfigBuilder()
            .set_clamp_range(20, 80)
            .build()
        )
        assert config.clamp_range == (20.0, 80.0)


# ===================================================================
# 12. ScoringResult dataclass
# ===================================================================

class TestScoringResult:

    def test_result_fields_present(self) -> None:
        engine = MutationScoringEngine(_minimal_config())
        result = engine.score({"regime": "bull"})

        assert isinstance(result.total, float)
        assert isinstance(result.breakdown, dict)
        assert isinstance(result.pair_bonus_total, float)
        assert isinstance(result.pair_bonus_details, list)
        assert isinstance(result.system_bonus_total, float)
        assert isinstance(result.system_bonus_details, list)
        assert isinstance(result.verdict, str)
        assert isinstance(result.evidence_lane, str)
        assert isinstance(result.mutations, dict)

    def test_result_mutations_is_copy(self) -> None:
        """Mutations dict should be a copy, not a reference."""
        engine = MutationScoringEngine(_minimal_config())
        original = {"regime": "bull"}
        result = engine.score(original)
        original["regime"] = "bear"
        assert result.mutations["regime"] == "bull"


# ===================================================================
# 13. Integration: trading-crypto-like config
# ===================================================================

class TestTradingCryptoLike:
    """Simulates the trading-crypto chip's scoring model."""

    @staticmethod
    def _build_engine() -> MutationScoringEngine:
        config = (
            ScoringConfigBuilder()
            .set_base_score(50)
            .add_dimension("doctrine", {
                "trend_following": 6,
                "mean_reversion": 4,
                "statistical_arb": 8,
            })
            .add_dimension("strategy", {
                "momentum": 5,
                "breakout": 3,
                "grid": 2,
            })
            .add_dimension("regime", {
                "trending": 4,
                "ranging": 2,
                "volatile": -3,
                "crisis": -10,
            })
            .add_dimension("timeframe", {
                "1m": -2,
                "5m": 0,
                "1h": 3,
                "4h": 5,
                "1d": 4,
            })
            .add_dimension("venue", {
                "cex_tier1": 3,
                "cex_tier2": 1,
                "dex_major": 2,
                "dex_minor": -2,
            })
            .add_pair_bonus("doctrine", "trend_following", "regime", "trending", 5)
            .add_pair_bonus("doctrine", "mean_reversion", "regime", "ranging", 4)
            .add_system_bonus(
                "paper_gate", -20,
                lambda m: m.get("paper_trade") == "fail",
            )
            .set_thresholds(approve=70, defer=40)
            .build()
        )
        return MutationScoringEngine(config)

    def test_baseline_score(self) -> None:
        engine = self._build_engine()
        result = engine.score({})
        assert result.total == 50

    def test_strong_combination(self) -> None:
        engine = self._build_engine()
        result = engine.score({
            "doctrine": "trend_following",
            "regime": "trending",
            "timeframe": "4h",
            "venue": "cex_tier1",
            "strategy": "momentum",
        })
        # 50 + 6 + 4 + 5 + 3 + 5 + 5(pair) = 78
        assert result.total == 78
        assert result.verdict == "approve"

    def test_crisis_with_paper_fail(self) -> None:
        engine = self._build_engine()
        result = engine.score({
            "regime": "crisis",
            "paper_trade": "fail",
        })
        # 50 - 10 - 20 = 20
        assert result.total == 20
        assert result.verdict == "reject"


# ===================================================================
# 14. Integration: startup-yc-like config
# ===================================================================

class TestStartupYcLike:
    """Simulates the startup-yc chip's scoring model."""

    @staticmethod
    def _build_engine() -> MutationScoringEngine:
        config = (
            ScoringConfigBuilder()
            .set_base_score(50)
            .add_dimension("business_model", {
                "saas": 5,
                "marketplace": 3,
                "hardware": -2,
                "consumer": 1,
            })
            .add_dimension("team_strength", {
                "repeat_founders": 10,
                "domain_expert": 7,
                "first_time": 2,
                "solo": -3,
            })
            .add_dimension("market_size", {
                "massive": 8,
                "large": 5,
                "niche": 1,
                "tiny": -5,
            })
            .add_dimension("traction", {
                "revenue": 10,
                "users": 6,
                "waitlist": 3,
                "idea_only": -2,
            })
            .add_pair_bonus("business_model", "saas", "traction", "revenue", 5)
            .add_system_bonus(
                "yc_batch_signal", 4,
                lambda m: m.get("yc_batch") is not None,
            )
            .add_system_bonus(
                "contradiction_penalty", -8,
                lambda m: (
                    m.get("business_model") == "marketplace"
                    and m.get("traction") == "idea_only"
                ),
            )
            .set_thresholds(approve=75, defer=45)
            .build()
        )
        return MutationScoringEngine(config)

    def test_strong_startup(self) -> None:
        engine = self._build_engine()
        result = engine.score({
            "business_model": "saas",
            "team_strength": "repeat_founders",
            "market_size": "massive",
            "traction": "revenue",
            "yc_batch": "W26",
        })
        # 50 + 5 + 10 + 8 + 10 + 5(pair) + 4(yc) = 92
        assert result.total == 92
        assert result.verdict == "approve"

    def test_contradiction_penalty(self) -> None:
        engine = self._build_engine()
        result = engine.score({
            "business_model": "marketplace",
            "traction": "idea_only",
        })
        # 50 + 3 + (-2) + (-8) = 43
        assert result.total == 43
        assert result.verdict == "reject"  # 43 < 45 defer threshold

    def test_weak_startup(self) -> None:
        engine = self._build_engine()
        result = engine.score({
            "business_model": "hardware",
            "team_strength": "solo",
            "market_size": "tiny",
            "traction": "idea_only",
        })
        # 50 + (-2) + (-3) + (-5) + (-2) = 38
        assert result.total == 38
        assert result.verdict == "reject"
