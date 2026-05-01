from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from chip_labs.artifact_quality import (
    CLAIM_BOUNDARY,
    MANIFEST_PATH,
    format_artifact_quality_markdown,
    run_artifact_quality_benchmark,
    score_artifact_quality_file,
)


FIXTURE_DIR = Path("docs/creator_system/examples/artifact-quality")


def test_artifact_quality_scores_good_fixture_review_ready() -> None:
    report = score_artifact_quality_file(FIXTURE_DIR / "good_design_pr.md")

    assert report["packet_kind"] == "artifact_quality_report"
    assert report["verdict"] == "review_ready"
    assert report["score"] >= 0.85
    assert report["claim_boundary"] == CLAIM_BOUNDARY
    assert report["trap_flags"] == []
    assert report["repair_actions"] == []


def test_artifact_quality_blocks_polished_unproven_trap() -> None:
    report = score_artifact_quality_file(FIXTURE_DIR / "polished_unproven_trap.md")

    assert report["verdict"] == "blocked"
    assert "polished_but_unproven" in report["trap_flags"]
    assert "runnable_evidence" in report["missing_checks"]
    assert "rollback_plan" in report["missing_checks"]
    assert "product correctness" in report["unsafe_claim"]


def test_artifact_quality_flags_weak_fixture_for_revision() -> None:
    report = score_artifact_quality_file(FIXTURE_DIR / "weak_design_pr.md")

    assert report["verdict"] in {"blocked", "needs_revision"}
    assert report["score"] < 0.85
    assert report["repair_actions"]


def test_format_artifact_quality_markdown_includes_repair_actions() -> None:
    report = score_artifact_quality_file(FIXTURE_DIR / "polished_unproven_trap.md")

    markdown = format_artifact_quality_markdown(report)

    assert "# Artifact Quality Report" in markdown
    assert "Repair Actions" in markdown
    assert "polished_but_unproven" in markdown


def test_cli_artifact_quality_score_outputs_json_and_markdown(tmp_path: Path) -> None:
    output_path = tmp_path / "artifact_quality.json"
    markdown_path = tmp_path / "artifact_quality.md"
    env = {**os.environ, "PYTHONPATH": str(Path.cwd() / "src")}

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "chip_labs.cli",
            "artifact-quality-score",
            "--input",
            str(FIXTURE_DIR / "good_design_pr.md"),
            "--artifact-kind",
            "pr_writeup",
            "--output",
            str(output_path),
            "--markdown-output",
            str(markdown_path),
        ],
        cwd=Path.cwd(),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["verdict"] == "review_ready"
    assert payload["artifact_kind"] == "pr_writeup"
    assert markdown_path.read_text(encoding="utf-8").startswith("# Artifact Quality Report")


def test_run_artifact_quality_benchmark_writes_recomputeable_reports(tmp_path: Path) -> None:
    run_dir = tmp_path / "artifact-run"
    artifact_dir = run_dir / "benchmark" / "artifacts"
    artifact_dir.mkdir(parents=True)
    reports_dir = run_dir / "reports"
    reports_dir.mkdir()
    for fixture_name in (
        "good_design_pr.md",
        "weak_design_pr.md",
        "polished_unproven_trap.md",
    ):
        (artifact_dir / fixture_name).write_text(
            (FIXTURE_DIR / fixture_name).read_text(encoding="utf-8"),
            encoding="utf-8",
        )
    manifest_path = run_dir / MANIFEST_PATH
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps({
            "schema_version": "artifact_quality.benchmark_manifest.v1",
            "baseline_artifact": "benchmark/artifacts/weak_design_pr.md",
            "candidate_artifact": "benchmark/artifacts/good_design_pr.md",
            "trap_artifacts": ["benchmark/artifacts/polished_unproven_trap.md"],
        }, indent=2)
        + "\n",
        encoding="utf-8",
    )

    result = run_artifact_quality_benchmark(run_dir)

    assert result["verdict"] == "pass"
    assert (reports_dir / "baseline.json").exists()
    assert (reports_dir / "candidate.json").exists()
    assert (reports_dir / "absorption_summary.json").exists()
    assert result["candidate"]["mean_delta"] > 0
    assert result["candidate"]["trap_regressions"] == 0
    assert result["candidate"]["provenance"]["source"] == "artifact_quality_v1"
