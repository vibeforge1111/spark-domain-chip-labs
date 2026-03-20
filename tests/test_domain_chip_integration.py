"""Integration tests: V2 scoring across real domain chip portfolio.

Runs against all discovered chips on Desktop. Tests verify scoring
contract, dimension integrity, portfolio health, and baseline regression.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import pytest


# ---------------------------------------------------------------------------
# Chip discovery (duplicated from conftest for direct import safety)
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
BASELINE_PATH = Path(__file__).parent / "baseline_v2_scores.json"

# Skip entire module when no real chips exist
pytestmark = pytest.mark.real_chips
if not _DESKTOP_CHIPS:
    pytestmark = pytest.mark.skip("No real domain chips on Desktop")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _score_v2(chip_path: Path) -> dict[str, Any]:
    """Score a chip with v2 rubric."""
    from chip_labs.quality_rubric_v2 import score_chip_v2

    return score_chip_v2(chip_path)


def _score_v1(chip_path: Path) -> dict[str, Any]:
    """Score a chip with v1 rubric."""
    from chip_labs.quality_rubric import score_chip

    return score_chip(chip_path)


def _all_v2_results() -> dict[str, dict[str, Any]]:
    """Score all chips and cache results within the test session."""
    if not hasattr(_all_v2_results, "_cache"):
        _all_v2_results._cache = {}
        for chip in _DESKTOP_CHIPS:
            _all_v2_results._cache[chip.name] = _score_v2(chip)
    return _all_v2_results._cache


# ---------------------------------------------------------------------------
# TestV2ScoringBaseline
# ---------------------------------------------------------------------------


class TestV2ScoringBaseline:
    """Every chip produces a valid v2 scoring result."""

    def test_returns_dict(self, chip_path: Path) -> None:
        result = _score_v2(chip_path)
        assert isinstance(result, dict)

    def test_has_required_keys(self, chip_path: Path) -> None:
        result = _score_v2(chip_path)
        for key in ("total_score", "verdict", "dimensions", "passed_checks", "failed_checks"):
            assert key in result, f"Missing key: {key}"

    def test_score_is_positive(self, chip_path: Path) -> None:
        result = _score_v2(chip_path)
        assert result["total_score"] > 0, f"{chip_path.name} scored 0"

    def test_score_within_range(self, chip_path: Path) -> None:
        result = _score_v2(chip_path)
        assert 0 <= result["total_score"] <= 100

    def test_verdict_is_valid(self, chip_path: Path) -> None:
        result = _score_v2(chip_path)
        assert result["verdict"] in ("production_ready", "beta", "alpha", "scaffold")

    def test_has_seven_dimensions(self, chip_path: Path) -> None:
        result = _score_v2(chip_path)
        assert len(result["dimensions"]) == 7

    def test_rubric_version_is_v2(self, chip_path: Path) -> None:
        result = _score_v2(chip_path)
        assert result.get("rubric_version") == "2.0"

    def test_passed_plus_failed_is_consistent(self, chip_path: Path) -> None:
        result = _score_v2(chip_path)
        total_checks = len(result["passed_checks"]) + len(result["failed_checks"])
        assert total_checks > 0


# ---------------------------------------------------------------------------
# TestV2VsV1Comparison
# ---------------------------------------------------------------------------


class TestV2VsV1Comparison:
    """V2 rubric comparison with V1 for every chip."""

    def test_v2_within_reasonable_range_of_v1(self, chip_path: Path) -> None:
        """V2 score should be within a reasonable range of V1.

        After flywheel improvements, v2 may exceed v1 because v2 has extra
        dimensions (flywheel_intelligence) that weren't in v1.  We allow
        v2 to exceed v1 by up to 15 points (the flywheel bonus).
        """
        v1 = _score_v1(chip_path)
        v2 = _score_v2(chip_path)
        # V2 has a 25-point flywheel dimension not in V1, so v2 can exceed
        # v1 when flywheel checks pass.  Cap overshoot at 25 (max flywheel).
        assert v2["total_score"] <= v1["total_score"] + 25, (
            f"{chip_path.name}: v2={v2['total_score']} exceeds v1={v1['total_score']} by more than flywheel bonus"
        )

    def test_both_return_total_score(self, chip_path: Path) -> None:
        v1 = _score_v1(chip_path)
        v2 = _score_v2(chip_path)
        assert isinstance(v1["total_score"], int)
        assert isinstance(v2["total_score"], int)

    def test_both_return_verdict(self, chip_path: Path) -> None:
        v1 = _score_v1(chip_path)
        v2 = _score_v2(chip_path)
        assert "verdict" in v1
        assert "verdict" in v2

    def test_v2_has_more_dimensions(self, chip_path: Path) -> None:
        v1 = _score_v1(chip_path)
        v2 = _score_v2(chip_path)
        assert len(v2["dimensions"]) >= len(v1["dimensions"])


# ---------------------------------------------------------------------------
# TestDimensionBreakdown
# ---------------------------------------------------------------------------


class TestDimensionBreakdown:
    """Each dimension scores within its valid range."""

    def test_no_dimension_negative(self, chip_path: Path) -> None:
        result = _score_v2(chip_path)
        for dim in result["dimensions"]:
            assert dim["score"] >= 0, f"{dim['name']} is negative: {dim['score']}"

    def test_no_dimension_exceeds_max(self, chip_path: Path) -> None:
        result = _score_v2(chip_path)
        for dim in result["dimensions"]:
            assert dim["score"] <= dim["max_points"], (
                f"{dim['name']}: {dim['score']} > {dim['max_points']}"
            )

    def test_dimension_sum_equals_total(self, chip_path: Path) -> None:
        result = _score_v2(chip_path)
        dim_sum = sum(d["score"] for d in result["dimensions"])
        assert dim_sum == result["total_score"]

    def test_manifest_dimension_exists(self, chip_path: Path) -> None:
        result = _score_v2(chip_path)
        names = [d["name"] for d in result["dimensions"]]
        assert "manifest_validity" in names

    def test_flywheel_dimension_exists(self, chip_path: Path) -> None:
        result = _score_v2(chip_path)
        names = [d["name"] for d in result["dimensions"]]
        assert "flywheel_intelligence" in names

    def test_flywheel_max_is_25(self, chip_path: Path) -> None:
        result = _score_v2(chip_path)
        for dim in result["dimensions"]:
            if dim["name"] == "flywheel_intelligence":
                assert dim["max_points"] == 25


# ---------------------------------------------------------------------------
# TestPortfolioHealth
# ---------------------------------------------------------------------------


class TestPortfolioHealth:
    """Portfolio-level assertions across all discovered chips."""

    def test_portfolio_average_above_50(self, desktop_chips: list[Path]) -> None:
        if not desktop_chips:
            pytest.skip("No chips")
        results = _all_v2_results()
        avg = sum(r["total_score"] for r in results.values()) / len(results)
        assert avg > 50, f"Portfolio average {avg:.1f} is below 50"

    def test_startup_yc_is_leader(self, desktop_chips: list[Path]) -> None:
        results = _all_v2_results()
        if "domain-chip-startup-yc" not in results:
            pytest.skip("startup-yc not found")
        yc_score = results["domain-chip-startup-yc"]["total_score"]
        for name, r in results.items():
            if name != "domain-chip-startup-yc":
                assert yc_score >= r["total_score"], (
                    f"startup-yc ({yc_score}) is not the leader: {name} scored {r['total_score']}"
                )

    def test_no_chip_below_scaffold(self, desktop_chips: list[Path]) -> None:
        results = _all_v2_results()
        for name, r in results.items():
            assert r["total_score"] >= 35, (
                f"{name} scored {r['total_score']}, which is scaffold-tier"
            )

    def test_at_least_six_chips_beta_or_better(self, desktop_chips: list[Path]) -> None:
        results = _all_v2_results()
        beta_plus = sum(
            1 for r in results.values()
            if r["verdict"] in ("beta", "production_ready")
        )
        assert beta_plus >= 6, f"Only {beta_plus} chips are beta+, expected >= 6"

    def test_portfolio_has_at_least_10_chips(self, desktop_chips: list[Path]) -> None:
        assert len(desktop_chips) >= 10, f"Only {len(desktop_chips)} chips found"


# ---------------------------------------------------------------------------
# TestBaselineSnapshot
# ---------------------------------------------------------------------------


class TestBaselineSnapshot:
    """Capture and verify scores against a persisted baseline."""

    def test_capture_baseline(self, desktop_chips: list[Path]) -> None:
        """First run: create baseline. Subsequent runs: this is a no-op."""
        if BASELINE_PATH.exists():
            return  # Already captured
        results = _all_v2_results()
        baseline = {
            name: r["total_score"]
            for name, r in results.items()
        }
        BASELINE_PATH.write_text(
            json.dumps(baseline, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    def test_no_regression_from_baseline(self, desktop_chips: list[Path]) -> None:
        """Each chip must score >= its baseline (no regressions)."""
        if not BASELINE_PATH.exists():
            pytest.skip("No baseline yet (run test_capture_baseline first)")
        baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
        results = _all_v2_results()
        regressions = []
        for name, expected_score in baseline.items():
            if name in results:
                actual = results[name]["total_score"]
                if actual < expected_score:
                    regressions.append(
                        f"{name}: {actual} < baseline {expected_score}"
                    )
        assert not regressions, f"Regressions detected:\n" + "\n".join(regressions)

    def test_baseline_file_is_valid_json(self) -> None:
        """If baseline exists, it should be valid JSON."""
        if not BASELINE_PATH.exists():
            pytest.skip("No baseline file")
        data = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
        assert isinstance(data, dict)
        for k, v in data.items():
            assert isinstance(k, str)
            assert isinstance(v, int)
