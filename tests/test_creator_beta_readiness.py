from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from chip_labs.creator_beta_readiness import build_creator_system_beta_check
from chip_labs.creator_generator import run_multi_seed_generator_validation
from chip_labs.creator_release_evidence import build_creator_system_release_evidence


SCHEMA = Path("docs/creator_system/schemas/creator-system-beta-check.schema.json")
RELEASE_EVIDENCE_SCHEMA = Path(
    "docs/creator_system/schemas/creator-system-release-evidence.schema.json"
)
PRODUCT_READ_ONLY_REVIEW = Path(
    "docs/creator_system/examples/product-runtime-review/review-complete-read-only.json"
)


def _validate_schema(payload: dict[str, object]) -> None:
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(payload)


def _validate_release_evidence_schema(payload: dict[str, object]) -> None:
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(RELEASE_EVIDENCE_SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(payload)


def _brief() -> dict[str, object]:
    return {
        "domain_id": "beta-readiness-demo",
        "domain_name": "Beta Readiness Demo",
        "goal": "Prove beta readiness can use generated evidence without publication.",
        "known_limits": ["Generated evidence is local candidate review only."],
        "unsafe_claims": ["Treat beta readiness as network absorption."],
    }


def _git_info(*, clean: bool) -> dict[str, object]:
    dirty_files = [] if clean else ["M docs/creator_system/task.md"]
    return {
        "path": str(Path.cwd()),
        "branch": "main",
        "commit": "a" * 40,
        "remote_url": "https://github.com/vibeforge1111/spark-domain-chip-labs.git",
        "worktree_clean": clean,
        "dirty_file_count": len(dirty_files),
        "dirty_files_sample": dirty_files,
    }


def test_creator_system_beta_check_passes_local_beta_boundary() -> None:
    result = build_creator_system_beta_check()

    _validate_schema(result)
    assert result["schema_version"] == "adaptive_creator_loop.creator_system_beta_check.v1"
    assert result["verdict"] == "pass"
    assert result["network_absorbable"] is False
    assert not result["blocking_checks"]
    checks = {check["name"]: check for check in result["checks"]}
    assert checks["creator_run_templates"]["status"] == "pass"
    assert checks["startup_yc_strict_smoke"]["detail"]["evidence_tier"] == "transfer_supported"
    assert checks["startup_yc_network_absorption_boundary"]["detail"]["verdict"] == "blocked"
    assert checks["startup_yc_production_gate_workbench"]["status"] == "pass"
    assert checks["startup_yc_production_gate_workbench"]["detail"]["verdict"] == "blocked"
    assert checks["startup_yc_production_gate_workbench"]["detail"]["workspace_was_clean"] is True
    assert checks["startup_yc_production_gate_workbench"]["detail"]["gate_verdicts"][
        "held_out_founder_advice_pass"
    ] == "passed"
    assert checks["startup_yc_production_gate_workbench"]["detail"]["gate_verdicts"][
        "multi_seed_validation"
    ] == "blocked"
    assert checks["stronger_release_gate_boundary"]["detail"]["generated_phase_passed"] is False
    assert checks["stronger_release_gate_boundary"]["detail"]["product_phase_passed"] is False


def test_creator_system_beta_check_accepts_generated_summary_without_absorption(
    tmp_path: Path,
) -> None:
    run_multi_seed_generator_validation(
        tmp_path / "generated",
        [_brief()],
        seeds=(1,),
        variants_per_domain=1,
    )
    summary_path = tmp_path / "generated" / "multi_seed_validation_summary.json"

    result = build_creator_system_beta_check(generated_summary_path=summary_path)

    _validate_schema(result)
    assert result["verdict"] == "pass"
    assert result["network_absorbable"] is False
    checks = {check["name"]: check for check in result["checks"]}
    assert checks["stronger_release_gate_boundary"]["detail"]["generated_phase_passed"] is True
    assert checks["stronger_release_gate_boundary"]["detail"]["startup_phase_passed"] is False
    assert checks["stronger_release_gate_boundary"]["detail"]["product_phase_passed"] is False


def test_creator_system_beta_check_accepts_product_review_without_absorption() -> None:
    result = build_creator_system_beta_check(
        product_runtime_review_path=PRODUCT_READ_ONLY_REVIEW,
    )

    _validate_schema(result)
    assert result["verdict"] == "pass"
    assert result["network_absorbable"] is False
    checks = {check["name"]: check for check in result["checks"]}
    assert checks["stronger_release_gate_boundary"]["detail"]["generated_phase_passed"] is False
    assert checks["stronger_release_gate_boundary"]["detail"]["startup_phase_passed"] is False
    assert checks["stronger_release_gate_boundary"]["detail"]["product_phase_passed"] is True


def test_creator_system_beta_check_blocks_broken_startup_fixture(tmp_path: Path) -> None:
    result = build_creator_system_beta_check(startup_run_dir=tmp_path / "missing-run")

    _validate_schema(result)
    assert result["verdict"] == "blocked"
    assert result["network_absorbable"] is False
    assert any(
        blocker.startswith("startup_yc_strict_smoke:")
        for blocker in result["blocking_checks"]
    )


def test_creator_system_beta_check_schema_rejects_absorbable_claim() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    result = build_creator_system_beta_check()
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

    _validate_schema(result)
    unsafe = json.loads(json.dumps(result))
    unsafe["network_absorbable"] = True
    assert list(jsonschema.Draft202012Validator(schema).iter_errors(unsafe))


def test_cli_creator_system_beta_check_fails_on_blocked(tmp_path: Path) -> None:
    output_path = tmp_path / "beta-check.json"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "chip_labs.cli",
            "creator-system-beta-check",
            "--startup-run-dir",
            str(tmp_path / "missing-run"),
            "--output",
            str(output_path),
            "--fail-on-blocked",
        ],
        cwd=Path.cwd(),
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    _validate_schema(payload)
    assert payload["verdict"] == "blocked"
    assert payload["network_absorbable"] is False


def test_creator_system_release_evidence_passes_for_clean_beta_packet() -> None:
    beta = build_creator_system_beta_check()
    result = build_creator_system_release_evidence(
        git_info=_git_info(clean=True),
        beta_check=beta,
    )

    _validate_release_evidence_schema(result)
    assert result["verdict"] == "pass"
    assert result["release_ready"] is True
    assert result["network_absorbable"] is False
    assert result["beta_check_summary"]["verdict"] == "pass"
    assert result["repo"]["worktree_clean"] is True
    assert result["promotion_boundary"]["blocked_claim"] == "network_absorbable"
    assert "publication_approval" in result["promotion_boundary"]["required_before_upgrade"]


def test_creator_system_release_evidence_blocks_dirty_worktree() -> None:
    beta = build_creator_system_beta_check()
    result = build_creator_system_release_evidence(
        git_info=_git_info(clean=False),
        beta_check=beta,
    )

    _validate_release_evidence_schema(result)
    assert result["verdict"] == "blocked"
    assert result["release_ready"] is False
    assert result["network_absorbable"] is False
    assert "repo:worktree_dirty" in result["blocking_checks"]


def test_creator_system_release_evidence_schema_rejects_absorbable_claim() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    result = build_creator_system_release_evidence(
        git_info=_git_info(clean=True),
        beta_check=build_creator_system_beta_check(),
    )
    schema = json.loads(RELEASE_EVIDENCE_SCHEMA.read_text(encoding="utf-8"))

    _validate_release_evidence_schema(result)
    unsafe = json.loads(json.dumps(result))
    unsafe["network_absorbable"] = True
    assert list(jsonschema.Draft202012Validator(schema).iter_errors(unsafe))


def test_cli_creator_system_release_evidence_writes_packet(tmp_path: Path) -> None:
    output_path = tmp_path / "release-evidence.json"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "chip_labs.cli",
            "creator-system-release-evidence",
            "--output",
            str(output_path),
        ],
        cwd=Path.cwd(),
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    _validate_release_evidence_schema(payload)
    assert payload["network_absorbable"] is False
    assert payload["beta_check_summary"]["verdict"] == "pass"
