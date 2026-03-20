"""Integration tests: V3 deep evaluation across real domain chip portfolio.

Runs against all discovered chips on Desktop.  Tests verify scoring
contract, dimension integrity, portfolio health, and proper separation
between genuine and scaffolded intelligence.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from chip_labs.deep_eval import (
    DeepEvalResult,
    score_chip_v3,
    score_portfolio_v3,
)


# ---------------------------------------------------------------------------
# Chip discovery
# ---------------------------------------------------------------------------

def _discover_chips() -> list[Path]:
    desktop = Path(os.path.expanduser("~")) / "Desktop"
    if not desktop.exists():
        return []
    return sorted(
        p for p in desktop.iterdir()
        if p.is_dir() and p.name.startswith("domain-chip-") and (p / "spark-chip.json").exists()
    )


_DESKTOP_CHIPS = _discover_chips()

# Skip entire module when no real chips exist
pytestmark = pytest.mark.real_chips
if not _DESKTOP_CHIPS:
    pytestmark = pytest.mark.skip("No real domain chips on Desktop")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(params=_DESKTOP_CHIPS, ids=lambda p: p.name)
def chip_path(request: pytest.FixtureRequest) -> Path:
    return request.param


@pytest.fixture
def desktop_chips() -> list[Path]:
    return _DESKTOP_CHIPS


def _all_v3_results() -> dict[str, DeepEvalResult]:
    """Score all chips and cache within test session."""
    if not hasattr(_all_v3_results, "_cache"):
        _all_v3_results._cache = {}
        for chip in _DESKTOP_CHIPS:
            _all_v3_results._cache[chip.name] = score_chip_v3(chip)
    return _all_v3_results._cache


# ---------------------------------------------------------------------------
# TestV3ScoringContract
# ---------------------------------------------------------------------------


class TestV3ScoringContract:
    """Every chip produces a valid V3 result."""

    def test_returns_deep_eval_result(self, chip_path: Path) -> None:
        result = score_chip_v3(chip_path)
        assert isinstance(result, DeepEvalResult)

    def test_has_8_dimensions(self, chip_path: Path) -> None:
        result = score_chip_v3(chip_path)
        assert len(result.dimensions) == 8

    def test_score_within_range(self, chip_path: Path) -> None:
        result = score_chip_v3(chip_path)
        assert 0 <= result.total_score <= 100

    def test_verdict_is_valid(self, chip_path: Path) -> None:
        result = score_chip_v3(chip_path)
        assert result.verdict in ("production_ready", "beta", "alpha", "scaffold")

    def test_rubric_version(self, chip_path: Path) -> None:
        result = score_chip_v3(chip_path)
        assert result.rubric_version == "3.0"

    def test_has_depth_profile(self, chip_path: Path) -> None:
        result = score_chip_v3(chip_path)
        assert len(result.depth_profile) == 8
        for level in result.depth_profile.values():
            assert level in ("absent", "surface", "moderate", "deep", "expert")


# ---------------------------------------------------------------------------
# TestDimensionIntegrity
# ---------------------------------------------------------------------------


class TestDimensionIntegrity:
    """Each dimension scores within its valid range."""

    def test_no_dimension_negative(self, chip_path: Path) -> None:
        result = score_chip_v3(chip_path)
        for dim in result.dimensions:
            assert dim.score >= 0, f"{dim.name} is negative: {dim.score}"

    def test_no_dimension_exceeds_max(self, chip_path: Path) -> None:
        result = score_chip_v3(chip_path)
        for dim in result.dimensions:
            assert dim.score <= dim.max_points + 0.1, (
                f"{dim.name}: {dim.score} > {dim.max_points}"
            )

    def test_dimension_sum_equals_total(self, chip_path: Path) -> None:
        result = score_chip_v3(chip_path)
        dim_sum = sum(d.score for d in result.dimensions)
        assert abs(dim_sum - result.total_score) < 0.5

    def test_max_points_sum_to_100(self, chip_path: Path) -> None:
        result = score_chip_v3(chip_path)
        max_sum = sum(d.max_points for d in result.dimensions)
        assert max_sum == 100.0

    def test_expected_dimension_names(self, chip_path: Path) -> None:
        result = score_chip_v3(chip_path)
        names = {d.name for d in result.dimensions}
        expected = {
            "manifest_structure",
            "empirical_velocity",
            "doctrine_quality",
            "evidence_integrity",
            "contradiction_rigor",
            "flywheel_health",
            "watchtower_depth",
            "integration_maturity",
        }
        assert names == expected


# ---------------------------------------------------------------------------
# TestPortfolioV3Health
# ---------------------------------------------------------------------------


class TestPortfolioV3Health:
    """Portfolio-level assertions across all discovered chips."""

    def test_portfolio_has_at_least_10_chips(self, desktop_chips: list[Path]) -> None:
        assert len(desktop_chips) >= 10

    def test_portfolio_average_above_30(self, desktop_chips: list[Path]) -> None:
        results = _all_v3_results()
        avg = sum(r.total_score for r in results.values()) / len(results)
        assert avg > 30, f"Portfolio average {avg:.1f} is below 30"

    def test_startup_yc_leads(self, desktop_chips: list[Path]) -> None:
        """startup-yc should be the top scorer (genuine intelligence)."""
        results = _all_v3_results()
        if "domain-chip-startup-yc" not in results:
            pytest.skip("startup-yc not found")
        yc_score = results["domain-chip-startup-yc"].total_score
        for name, r in results.items():
            if name != "domain-chip-startup-yc":
                assert yc_score >= r.total_score, (
                    f"startup-yc ({yc_score}) should lead: {name} scored {r.total_score}"
                )

    def test_no_chip_above_85(self, desktop_chips: list[Path]) -> None:
        """No chip should score 85+ on V3 without genuine deep intelligence."""
        results = _all_v3_results()
        for name, r in results.items():
            assert r.total_score <= 85, (
                f"{name} scored {r.total_score} -- suspiciously high for V3"
            )

    def test_predictive_worlds_lab_is_lowest(self, desktop_chips: list[Path]) -> None:
        """predictive-worlds-lab should be near the bottom."""
        results = _all_v3_results()
        if "domain-chip-predictive-worlds-lab" not in results:
            pytest.skip("predictive-worlds-lab not found")
        pwl_score = results["domain-chip-predictive-worlds-lab"].total_score
        above_pwl = sum(1 for r in results.values() if r.total_score > pwl_score)
        # At least 8 chips should score higher
        assert above_pwl >= 8, (
            f"predictive-worlds-lab ({pwl_score}) should be near bottom, "
            f"but only {above_pwl} chips scored higher"
        )


# ---------------------------------------------------------------------------
# TestGenuineVsScaffolded
# ---------------------------------------------------------------------------


class TestGenuineVsScaffolded:
    """Verify that chips with genuine intelligence score higher
    than chips with primarily scaffolded artifacts."""

    def test_startup_yc_velocity_is_expert(self, desktop_chips: list[Path]) -> None:
        """startup-yc has 785 real runs -- should be expert-level velocity."""
        results = _all_v3_results()
        if "domain-chip-startup-yc" not in results:
            pytest.skip("startup-yc not found")
        yc = results["domain-chip-startup-yc"]
        velocity = next(d for d in yc.dimensions if d.name == "empirical_velocity")
        assert velocity.depth_level in ("deep", "expert"), (
            f"startup-yc velocity should be deep/expert, got {velocity.depth_level}"
        )
        assert velocity.details.get("run_count", 0) >= 500

    def test_startup_yc_watchtower_is_expert(self, desktop_chips: list[Path]) -> None:
        """startup-yc has 276 Obsidian pages -- should be expert-level watchtower."""
        results = _all_v3_results()
        if "domain-chip-startup-yc" not in results:
            pytest.skip("startup-yc not found")
        yc = results["domain-chip-startup-yc"]
        watchtower = next(d for d in yc.dimensions if d.name == "watchtower_depth")
        assert watchtower.depth_level == "expert"

    def test_pokemon_red_has_high_velocity(self, desktop_chips: list[Path]) -> None:
        """pokemon-red has 776 real runs -- should have high velocity."""
        results = _all_v3_results()
        if "domain-chip-pokemon-red" not in results:
            pytest.skip("pokemon-red not found")
        pr = results["domain-chip-pokemon-red"]
        velocity = next(d for d in pr.dimensions if d.name == "empirical_velocity")
        assert velocity.details.get("run_count", 0) >= 500

    def test_scaffolded_chips_have_lower_velocity(self, desktop_chips: list[Path]) -> None:
        """Chips without genuine run data should score lower on velocity."""
        results = _all_v3_results()
        # Chips known to have scaffolded run data (few real runs)
        scaffolded_names = [
            "domain-chip-web-designer",
            "domain-chip-roblox-development",
            "domain-chip-spark-private-main",
        ]
        genuine_names = [
            "domain-chip-startup-yc",
            "domain-chip-pokemon-red",
        ]
        for scaffolded_name in scaffolded_names:
            if scaffolded_name not in results:
                continue
            s_velocity = next(
                d for d in results[scaffolded_name].dimensions
                if d.name == "empirical_velocity"
            )
            for genuine_name in genuine_names:
                if genuine_name not in results:
                    continue
                g_velocity = next(
                    d for d in results[genuine_name].dimensions
                    if d.name == "empirical_velocity"
                )
                assert g_velocity.score > s_velocity.score, (
                    f"{genuine_name} velocity ({g_velocity.score}) should exceed "
                    f"{scaffolded_name} ({s_velocity.score})"
                )


# ---------------------------------------------------------------------------
# TestAntiGamingFlags
# ---------------------------------------------------------------------------


class TestAntiGamingFlags:
    """Verify anti-gaming detection catches known patterns."""

    def test_every_chip_has_valid_flags(self, chip_path: Path) -> None:
        result = score_chip_v3(chip_path)
        assert isinstance(result.anti_gaming_flags, list)

    def test_diagnostics_present(self, chip_path: Path) -> None:
        result = score_chip_v3(chip_path)
        assert isinstance(result.gaps, list)
        assert isinstance(result.strengths, list)
        assert isinstance(result.recommendations, list)


# ---------------------------------------------------------------------------
# TestPortfolioV3Report
# ---------------------------------------------------------------------------


class TestPortfolioV3Report:
    """Test the portfolio-level report function."""

    def test_portfolio_report_structure(self) -> None:
        report = score_portfolio_v3()
        assert "chips" in report
        assert "summary" in report
        summary = report["summary"]
        assert "chip_count" in summary
        assert "average_score" in summary
        assert "verdicts" in summary
        assert "ranking" in summary

    def test_portfolio_ranking_is_sorted(self) -> None:
        report = score_portfolio_v3()
        ranking = report["summary"]["ranking"]
        scores = [s for _, s in ranking]
        assert scores == sorted(scores, reverse=True)

    def test_portfolio_chip_count_matches(self) -> None:
        report = score_portfolio_v3()
        assert report["summary"]["chip_count"] == len(report["chips"])
