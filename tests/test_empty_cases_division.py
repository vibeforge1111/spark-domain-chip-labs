"""Test that empty benchmark cases do not cause ZeroDivisionError."""

import json
import tempfile
from pathlib import Path

from chip_labs.creator_generator import _compute_reports, _lane_results
from chip_labs.creator_run import _generated_lane_results


def _write_empty_benchmark(run_path: Path) -> None:
    (run_path / "benchmark").mkdir(parents=True)
    (run_path / "benchmark" / "cases.jsonl").write_text("")
    (run_path / "domain-chip").mkdir(parents=True)
    (run_path / "domain-chip" / "scoring_hooks.json").write_text(
        json.dumps({"hooks": [], "candidate_mutations": {}})
    )


def test_compute_reports_empty_cases():
    with tempfile.TemporaryDirectory() as tmp:
        run_path = Path(tmp)
        _write_empty_benchmark(run_path)
        result = _compute_reports(run_path)
        assert result["case_count"] == 0
        assert result["baseline"]["mean_score"] == 0.0
        assert result["candidate"]["mean_score"] == 0.0


def test_lane_results_empty_scores():
    lane_scores = {
        "development": {
            "case_count": 0,
            "baseline_scores": [],
            "candidate_scores": [],
            "trap_regressions": 0,
        }
    }
    result = _lane_results(lane_scores)
    assert result["development"]["baseline_mean"] == 0.0
    assert result["development"]["candidate_mean"] == 0.0


def test_generated_lane_results_empty_scores():
    lane_scores = {
        "development": {
            "case_count": 0,
            "baseline_scores": [],
            "candidate_scores": [],
            "trap_regressions": 0,
        }
    }
    result = _generated_lane_results(lane_scores)
    assert result["development"]["baseline_mean"] == 0.0
    assert result["development"]["candidate_mean"] == 0.0
