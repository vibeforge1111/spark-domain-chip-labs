from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from chip_labs.artifact_quality import (
    CLAIM_BOUNDARY,
    MANIFEST_PATH,
    format_artifact_quality_markdown,
    run_artifact_quality_benchmark,
    score_artifact_quality_file,
)


FIXTURE_DIR = Path("docs/creator_system/examples/artifact-quality")
REPORT_SCHEMA = Path("docs/creator_system/schemas/artifact-quality-report.schema.json")
MANIFEST_SCHEMA = Path(
    "docs/creator_system/schemas/artifact-quality-benchmark-manifest.schema.json"
)
BENCHMARK_RESULT_SCHEMA = Path(
    "docs/creator_system/schemas/artifact-quality-benchmark-result.schema.json"
)


def _benchmark_manifest() -> dict[str, object]:
    return {
        "schema_version": "artifact_quality.benchmark_manifest.v1",
        "baseline_artifact": "benchmark/artifacts/weak_design_pr.md",
        "candidate_artifact": "benchmark/artifacts/good_design_pr.md",
        "trap_artifacts": ["benchmark/artifacts/polished_unproven_trap.md"],
        "case_expectations": {
            "baseline": {"max_score": 0.85},
            "candidate": {"verdict": "review_ready", "min_score": 0.85},
            "traps": {
                "verdict": "blocked",
                "required_trap_flags": ["polished_but_unproven"],
            },
        },
        "reviewer_calibration_cases": [
            {
                "case_id": "pr-writeup-ready",
                "artifact_path": "benchmark/artifacts/good_design_pr.md",
                "artifact_kind": "pr_writeup",
                "reviewer_verdict": "review_ready",
                "min_score": 0.85,
            },
            {
                "case_id": "polished-trap",
                "artifact_path": "benchmark/artifacts/polished_unproven_trap.md",
                "artifact_kind": "design_doc",
                "reviewer_verdict": "blocked",
                "required_trap_flags": ["polished_but_unproven"],
                "required_missing_checks": ["runnable_evidence", "rollback_plan"],
            },
        ],
    }


def _artifact_run(tmp_path: Path, manifest: dict[str, object] | None = None) -> Path:
    run_dir = tmp_path / "artifact-run"
    artifact_dir = run_dir / "benchmark" / "artifacts"
    artifact_dir.mkdir(parents=True)
    (run_dir / "reports").mkdir()
    for fixture_name in (
        "good_design_pr.md",
        "weak_design_pr.md",
        "polished_unproven_trap.md",
        "design_decision_record_ready.md",
        "mission_handoff_ready.md",
    ):
        (artifact_dir / fixture_name).write_text(
            (FIXTURE_DIR / fixture_name).read_text(encoding="utf-8"),
            encoding="utf-8",
        )
    manifest_path = run_dir / MANIFEST_PATH
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(manifest or _benchmark_manifest(), indent=2) + "\n",
        encoding="utf-8",
    )
    return run_dir


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


def test_saved_good_artifact_quality_report_matches_current_scorer() -> None:
    saved = json.loads(
        (FIXTURE_DIR / "good_design_pr.report.json").read_text(encoding="utf-8")
    )
    regenerated = score_artifact_quality_file(
        FIXTURE_DIR / "good_design_pr.md",
        artifact_kind="pr_writeup",
    )
    saved_markdown = (FIXTURE_DIR / "good_design_pr.report.md").read_text(
        encoding="utf-8"
    )

    assert regenerated == saved
    assert saved["verdict"] == "review_ready"
    assert saved["claim_boundary"] == CLAIM_BOUNDARY
    assert saved_markdown == format_artifact_quality_markdown(saved)


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
        "design_decision_record_ready.md",
        "mission_handoff_ready.md",
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
            "case_expectations": {
                "baseline": {"max_score": 0.85},
                "candidate": {"verdict": "review_ready", "min_score": 0.85},
                "traps": {
                    "verdict": "blocked",
                    "required_trap_flags": ["polished_but_unproven"],
                },
            },
            "reviewer_calibration_cases": [
                {
                    "case_id": "pr-writeup-ready",
                    "artifact_path": "benchmark/artifacts/good_design_pr.md",
                    "artifact_kind": "pr_writeup",
                    "reviewer_verdict": "review_ready",
                    "min_score": 0.85,
                },
                {
                    "case_id": "design-decision-ready",
                    "artifact_path": "benchmark/artifacts/design_decision_record_ready.md",
                    "artifact_kind": "design_doc",
                    "reviewer_verdict": "review_ready",
                    "min_score": 0.85,
                },
                {
                    "case_id": "handoff-ready",
                    "artifact_path": "benchmark/artifacts/mission_handoff_ready.md",
                    "artifact_kind": "mission_handoff",
                    "reviewer_verdict": "review_ready",
                    "min_score": 0.85,
                },
                {
                    "case_id": "polished-trap",
                    "artifact_path": "benchmark/artifacts/polished_unproven_trap.md",
                    "artifact_kind": "design_doc",
                    "reviewer_verdict": "blocked",
                    "required_trap_flags": ["polished_but_unproven"],
                    "required_missing_checks": ["runnable_evidence", "rollback_plan"],
                },
            ],
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
    assert result["candidate"]["calibration_verdict"] == "pass"
    assert result["candidate"]["reviewer_calibration_case_count"] == 4
    assert {
        row["artifact_kind"] for row in result["candidate"]["reviewer_calibration_rows"]
    } == {"pr_writeup", "design_doc", "mission_handoff"}
    assert all(
        row["status"] == "pass"
        for row in result["candidate"]["reviewer_calibration_rows"]
    )
    assert all(
        check["status"] == "pass"
        for check in result["candidate"]["expectation_checks"]
    )
    assert result["candidate"]["provenance"]["source"] == "artifact_quality_v1"
    assert (
        "benchmark/artifacts/design_decision_record_ready.md"
        in result["candidate"]["provenance"]["input_hashes"]
    )


def test_artifact_quality_benchmark_blocks_failed_case_expectations(
    tmp_path: Path,
) -> None:
    run_dir = tmp_path / "artifact-run"
    artifact_dir = run_dir / "benchmark" / "artifacts"
    artifact_dir.mkdir(parents=True)
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
            "case_expectations": {
                "candidate": {"verdict": "blocked"},
            },
        }, indent=2)
        + "\n",
        encoding="utf-8",
    )

    result = run_artifact_quality_benchmark(run_dir)

    assert result["verdict"] == "blocked"
    assert result["candidate"]["decision"] == "revert"
    assert result["candidate"]["calibration_verdict"] == "blocked"
    assert any(
        check["case_role"] == "candidate"
        and check["check_id"] == "verdict"
        and check["status"] == "fail"
        for check in result["candidate"]["expectation_checks"]
    )


def test_artifact_quality_benchmark_rejects_unknown_case_expectation_role(
    tmp_path: Path,
) -> None:
    manifest = _benchmark_manifest()
    assert isinstance(manifest["case_expectations"], dict)
    manifest["case_expectations"]["canddiate"] = {
        "verdict": "review_ready",
        "min_score": 0.95,
    }
    run_dir = _artifact_run(tmp_path, manifest)

    with pytest.raises(ValueError, match="unknown role"):
        run_artifact_quality_benchmark(run_dir)


def test_artifact_quality_benchmark_rejects_unknown_case_expectation_field(
    tmp_path: Path,
) -> None:
    manifest = _benchmark_manifest()
    assert isinstance(manifest["case_expectations"], dict)
    assert isinstance(manifest["case_expectations"]["candidate"], dict)
    manifest["case_expectations"]["candidate"]["minimum_score"] = 0.95
    run_dir = _artifact_run(tmp_path, manifest)

    with pytest.raises(ValueError, match="unknown field"):
        run_artifact_quality_benchmark(run_dir)


def test_artifact_quality_benchmark_rejects_unknown_reviewer_calibration_field(
    tmp_path: Path,
) -> None:
    manifest = _benchmark_manifest()
    assert isinstance(manifest["reviewer_calibration_cases"], list)
    manifest["reviewer_calibration_cases"][0]["minimum_score"] = 0.95
    run_dir = _artifact_run(tmp_path, manifest)

    with pytest.raises(ValueError, match="unknown field"):
        run_artifact_quality_benchmark(run_dir)


def test_artifact_quality_benchmark_blocks_failed_reviewer_calibration(
    tmp_path: Path,
) -> None:
    run_dir = tmp_path / "artifact-run"
    artifact_dir = run_dir / "benchmark" / "artifacts"
    artifact_dir.mkdir(parents=True)
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
            "reviewer_calibration_cases": [
                {
                    "case_id": "miscalibrated-good-pr",
                    "artifact_path": "benchmark/artifacts/good_design_pr.md",
                    "artifact_kind": "pr_writeup",
                    "reviewer_verdict": "blocked",
                },
            ],
        }, indent=2)
        + "\n",
        encoding="utf-8",
    )

    result = run_artifact_quality_benchmark(run_dir)

    assert result["verdict"] == "blocked"
    assert result["candidate"]["decision"] == "revert"
    assert result["candidate"]["calibration_verdict"] == "blocked"
    assert result["candidate"]["reviewer_calibration_rows"][0]["status"] == "fail"
    assert any(
        check["check_id"] == "verdict" and check["status"] == "fail"
        for check in result["candidate"]["reviewer_calibration_rows"][0]["checks"]
    )


def test_artifact_quality_schemas_validate_reports_and_benchmark(
    tmp_path: Path,
) -> None:
    jsonschema = pytest.importorskip("jsonschema")
    referencing = pytest.importorskip("referencing")
    report_schema = json.loads(REPORT_SCHEMA.read_text(encoding="utf-8"))
    manifest_schema = json.loads(MANIFEST_SCHEMA.read_text(encoding="utf-8"))
    benchmark_schema = json.loads(BENCHMARK_RESULT_SCHEMA.read_text(encoding="utf-8"))
    registry = referencing.Registry().with_resources([
        (
            report_schema["$id"],
            referencing.Resource.from_contents(report_schema),
        ),
        (
            "https://sparkswarm.ai/schemas/adaptive_creator_loop/artifact-quality-report.schema.json",
            referencing.Resource.from_contents(report_schema),
        ),
    ])

    saved_report = json.loads(
        (FIXTURE_DIR / "good_design_pr.report.json").read_text(encoding="utf-8")
    )
    manifest = _benchmark_manifest()
    run_dir = _artifact_run(tmp_path, manifest)
    result = run_artifact_quality_benchmark(run_dir)

    jsonschema.Draft202012Validator(report_schema).validate(saved_report)
    jsonschema.Draft202012Validator(manifest_schema).validate(manifest)
    jsonschema.Draft202012Validator(benchmark_schema, registry=registry).validate(result)


def test_artifact_quality_schemas_reject_unsafe_shapes(tmp_path: Path) -> None:
    jsonschema = pytest.importorskip("jsonschema")
    referencing = pytest.importorskip("referencing")
    report_schema = json.loads(REPORT_SCHEMA.read_text(encoding="utf-8"))
    benchmark_schema = json.loads(BENCHMARK_RESULT_SCHEMA.read_text(encoding="utf-8"))
    registry = referencing.Registry().with_resources([
        (
            report_schema["$id"],
            referencing.Resource.from_contents(report_schema),
        ),
        (
            "https://sparkswarm.ai/schemas/adaptive_creator_loop/artifact-quality-report.schema.json",
            referencing.Resource.from_contents(report_schema),
        ),
    ])
    report = score_artifact_quality_file(FIXTURE_DIR / "good_design_pr.md")
    run_dir = _artifact_run(tmp_path)
    result = run_artifact_quality_benchmark(run_dir)

    report["unsafe_claim"] = "This proves everything."
    result["candidate"]["calibration_verdict"] = "blocked"

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(report_schema).validate(report)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(benchmark_schema, registry=registry).validate(result)
