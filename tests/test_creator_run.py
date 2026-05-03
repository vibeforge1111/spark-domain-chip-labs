from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from chip_labs.creator_run import (
    diagnose_creator_run,
    init_creator_run,
    run_doctor_adversarial_sweep,
    validate_creator_run,
    validate_creator_templates,
)


DOCTOR_FIXTURE_DIR = Path("docs/creator_system/examples/doctor-security")
ADAPTER_MAP_SCHEMA = Path("docs/creator_system/schemas/adapter-map.schema.json")
SMOKE_RESULT_SCHEMA = Path("docs/creator_system/schemas/smoke-result.schema.json")
DOCTOR_RESULT_SCHEMA = Path("docs/creator_system/schemas/doctor-result.schema.json")
DOCTOR_SWEEP_MANIFEST_SCHEMA = Path(
    "docs/creator_system/schemas/doctor-adversarial-sweep-manifest.schema.json"
)
DOCTOR_SWEEP_RESULT_SCHEMA = Path(
    "docs/creator_system/schemas/doctor-adversarial-sweep-result.schema.json"
)


def test_init_creator_run_creates_valid_prototype(tmp_path: Path) -> None:
    run_dir = tmp_path / "startup-yc-run"

    result = init_creator_run(
        run_dir,
        domain="Startup YC",
        goal="Create a benchmarked Startup YC specialization path.",
        requested_by="test",
    )
    smoke = validate_creator_run(run_dir)

    assert result["run_id"].startswith("creator-run-")
    assert (run_dir / "creator-intent.json").exists()
    assert (run_dir / "adapter-map.json").exists()
    assert (run_dir / "created-artifact-manifest.json").exists()
    artifact_manifest = json.loads(
        (run_dir / "created-artifact-manifest.json").read_text(encoding="utf-8")
    )
    assert artifact_manifest["creator_run_id"] == result["run_id"]
    assert artifact_manifest["publication_boundary"] == "local_only"
    assert smoke.verdict == "prototype"
    assert any(
        check.name == "created_artifact_manifest_required_kinds"
        and check.status == "pass"
        for check in smoke.checks
    )
    assert "benchmark/manifest.json" in smoke.missing_paths


def test_smoke_result_exposes_machine_routing_fields(tmp_path: Path) -> None:
    jsonschema = pytest.importorskip("jsonschema")
    run_dir = tmp_path / "startup-yc-run"
    init_creator_run(run_dir, domain="Startup YC", goal="Route this run.")

    payload = validate_creator_run(run_dir).to_dict()
    schema = json.loads(SMOKE_RESULT_SCHEMA.read_text(encoding="utf-8"))

    jsonschema.Draft202012Validator(schema).validate(payload)
    assert payload["schema_version"] == "adaptive_creator_loop.smoke_result.v1"
    assert payload["evidence_mode"] == "saved"
    assert payload["status_counts"]["pass"] > 0
    assert payload["status_counts"]["fail"] == 0
    assert payload["blocking_checks"] == []
    assert payload["warning_checks"] == []
    assert payload["automation"]["blocked"] is False
    assert payload["automation"]["ci_exit_code"] == 0
    assert payload["automation"]["recommended_next_command"]

    recomputed_payload = validate_creator_run(run_dir, recompute=True).to_dict()
    jsonschema.Draft202012Validator(schema).validate(recomputed_payload)
    assert recomputed_payload["evidence_mode"] == "recomputed"


def test_core_schemas_reject_unknown_evidence_tier(tmp_path: Path) -> None:
    jsonschema = pytest.importorskip("jsonschema")
    run_dir = tmp_path / "startup-yc-run"
    init_creator_run(run_dir, domain="Startup YC", goal="Reject fake tiers.")

    adapter_map = json.loads((run_dir / "adapter-map.json").read_text(encoding="utf-8"))
    smoke = validate_creator_run(run_dir).to_dict()
    doctor = diagnose_creator_run(run_dir)

    schema_payloads = [
        (ADAPTER_MAP_SCHEMA, adapter_map, ("swarm_adapter", "evidence_tier")),
        (SMOKE_RESULT_SCHEMA, smoke, ("evidence_tier",)),
        (DOCTOR_RESULT_SCHEMA, doctor, ("evidence_tier",)),
    ]
    for schema_path, payload, field_path in schema_payloads:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        validator = jsonschema.Draft202012Validator(schema)
        validator.validate(payload)

        unsafe = json.loads(json.dumps(payload))
        target = unsafe
        for field in field_path[:-1]:
            target = target[field]
        target[field_path[-1]] = "magic_mastery"
        assert list(validator.iter_errors(unsafe))


def test_cli_fail_on_blocked_exits_nonzero(tmp_path: Path) -> None:
    run_dir = tmp_path / "creator-run"
    init_creator_run(run_dir, domain="Startup YC", goal="Test blocked CI exit.")
    (run_dir / "creator-intent.json").unlink()

    env = {**os.environ, "PYTHONPATH": str(Path.cwd() / "src")}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "chip_labs.cli",
            "creator-run-smoke",
            str(run_dir),
            "--fail-on-blocked",
        ],
        cwd=Path.cwd(),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    assert "adaptive_creator_loop.smoke_result.v1" in result.stdout
    assert '"blocked": true' in result.stdout


def test_cli_fail_on_warn_exits_nonzero_for_warning_fixture(tmp_path: Path) -> None:
    fixture_dir = _write_candidate_review_run(
        tmp_path, evidence_tier="transfer_supported"
    )
    _write_transfer_report(fixture_dir)
    _write_broad_transfer_probe(fixture_dir, delta=-0.01)
    env = {**os.environ, "PYTHONPATH": str(Path.cwd() / "src")}

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "chip_labs.cli",
            "creator-run-smoke",
            str(fixture_dir),
            "--fail-on-warn",
        ],
        cwd=Path.cwd(),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    assert '"warning_checks": [' in result.stdout
    assert '"broad_transfer_delta"' in result.stdout


def test_creator_run_doctor_returns_repair_steps(tmp_path: Path) -> None:
    run_dir = tmp_path / "creator-run"
    init_creator_run(run_dir, domain="Startup YC", goal="Diagnose this run.")

    result = diagnose_creator_run(run_dir)

    assert result["schema_version"] == "adaptive_creator_loop.doctor_result.v1"
    assert result["verdict"] == "prototype"
    assert result["workspace_ready"] is True
    assert result["publication_ready"] is False
    assert result["repair_calibration"]["verdict"] == "pass"
    assert result["repair_calibration"]["uncovered_smoke_checks"] == []
    assert any(step["area"] == "artifact_scaffold" for step in result["repair_steps"])


def test_creator_run_doctor_quarantines_malicious_packet_fixture(
    tmp_path: Path,
) -> None:
    run_dir = _write_candidate_review_run(tmp_path)
    fixture = json.loads(
        (DOCTOR_FIXTURE_DIR / "malicious_network_absorption_packet.json").read_text(
            encoding="utf-8"
        )
    )
    packet_path = run_dir / fixture["path"]
    packet = json.loads(packet_path.read_text(encoding="utf-8"))
    for operation in fixture["operations"]:
        _apply_fixture_operation(packet, operation)
    packet_path.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")

    result = diagnose_creator_run(run_dir)

    assert result["verdict"] == "blocked"
    assert fixture["expected_blocking_checks"][0] in result["smoke"]["blocking_checks"]
    assert any(
        step["area"] == "swarm_packet"
        and fixture["expected_blocking_checks"][0] in step["related_checks"]
        for step in result["repair_steps"]
    )
    assert result["quarantine"][0]["reason"] == fixture["quarantine_reason"]
    assert result["repair_calibration"]["verdict"] == "pass"
    assert result["repair_calibration"]["uncovered_smoke_checks"] == []


def test_creator_run_doctor_adversarial_sweep_covers_schema_families(
    tmp_path: Path,
) -> None:
    run_dir = _write_candidate_review_run(tmp_path)

    result = run_doctor_adversarial_sweep(
        run_dir,
        manifest_path=DOCTOR_FIXTURE_DIR / "adversarial_schema_sweep.json",
    )

    assert result["schema_version"] == "adaptive_creator_loop.doctor_adversarial_sweep.v1"
    assert result["verdict"] == "pass"
    assert result["case_count"] == 5
    assert result["passed_case_count"] == 5
    assert result["network_absorbable"] is False
    assert set(result["schema_families"]) == {
        "adapter_map",
        "absorption_summary",
        "candidate_report",
        "evidence_ladder",
        "swarm_packet",
    }
    assert all(row["doctor_verdict"] == "blocked" for row in result["rows"])
    assert all(row["repair_calibration_verdict"] == "pass" for row in result["rows"])
    assert any(
        row["case_id"] == "swarm-packet-tier-escalation"
        and row["observed_quarantine_reasons"] == ["unsafe_swarm_packet_claim"]
        for row in result["rows"]
    )


def test_creator_run_doctor_adversarial_sweep_schemas_validate_fixture_and_result(
    tmp_path: Path,
) -> None:
    jsonschema = pytest.importorskip("jsonschema")
    run_dir = _write_candidate_review_run(tmp_path)
    manifest = json.loads(
        (DOCTOR_FIXTURE_DIR / "adversarial_schema_sweep.json").read_text(
            encoding="utf-8"
        )
    )
    result = run_doctor_adversarial_sweep(
        run_dir,
        manifest_path=DOCTOR_FIXTURE_DIR / "adversarial_schema_sweep.json",
    )
    manifest_schema = json.loads(
        DOCTOR_SWEEP_MANIFEST_SCHEMA.read_text(encoding="utf-8")
    )
    result_schema = json.loads(DOCTOR_SWEEP_RESULT_SCHEMA.read_text(encoding="utf-8"))

    jsonschema.Draft202012Validator(manifest_schema).validate(manifest)
    jsonschema.Draft202012Validator(result_schema).validate(result)


def test_creator_run_doctor_adversarial_sweep_schemas_reject_unsafe_shapes(
    tmp_path: Path,
) -> None:
    jsonschema = pytest.importorskip("jsonschema")
    run_dir = _write_candidate_review_run(tmp_path)
    manifest = json.loads(
        (DOCTOR_FIXTURE_DIR / "adversarial_schema_sweep.json").read_text(
            encoding="utf-8"
        )
    )
    result = run_doctor_adversarial_sweep(
        run_dir,
        manifest_path=DOCTOR_FIXTURE_DIR / "adversarial_schema_sweep.json",
    )
    manifest_schema = json.loads(
        DOCTOR_SWEEP_MANIFEST_SCHEMA.read_text(encoding="utf-8")
    )
    result_schema = json.loads(DOCTOR_SWEEP_RESULT_SCHEMA.read_text(encoding="utf-8"))

    manifest["cases"][0]["expected_blocking_checks"] = []
    result["network_absorbable"] = True

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(manifest_schema).validate(manifest)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(result_schema).validate(result)


def test_cli_creator_run_doctor_adversarial_sweep_outputs_pass(
    tmp_path: Path,
) -> None:
    run_dir = _write_candidate_review_run(tmp_path)
    output_path = tmp_path / "doctor-sweep.json"
    env = {**os.environ, "PYTHONPATH": str(Path.cwd() / "src")}

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "chip_labs.cli",
            "creator-run-doctor-adversarial-sweep",
            str(run_dir),
            "--manifest",
            str(DOCTOR_FIXTURE_DIR / "adversarial_schema_sweep.json"),
            "--output",
            str(output_path),
            "--fail-on-blocked",
        ],
        cwd=Path.cwd(),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["verdict"] == "pass"
    assert payload["failed_case_ids"] == []


def test_template_check_passes_default_templates() -> None:
    result = validate_creator_templates()

    assert result["schema_version"] == "adaptive_creator_loop.template_check_result.v1"
    assert result["verdict"] == "pass"
    assert result["blocking_checks"] == []


def test_template_check_blocks_missing_required_creator_template(
    tmp_path: Path,
) -> None:
    template_dir = tmp_path / "creator-run"
    shutil.copytree(
        Path.cwd() / "docs" / "creator_system" / "templates" / "creator-run",
        template_dir,
    )
    (template_dir / "benchmark-pack.template.md").unlink()

    result = validate_creator_templates(template_dir)

    assert result["verdict"] == "blocked"
    assert "template_exists:benchmark-pack.template.md" in result["blocking_checks"]


def test_creator_system_schema_files_are_valid_json() -> None:
    schema_dir = Path.cwd() / "docs" / "creator_system" / "schemas"
    schema_files = sorted(schema_dir.glob("*.schema.json"))

    assert schema_files
    for schema_file in schema_files:
        payload = json.loads(schema_file.read_text(encoding="utf-8"))
        assert payload["$schema"].startswith("https://json-schema.org/")
        assert payload["title"]
        assert payload["type"] == "object"


def test_cli_creator_run_doctor_outputs_repair_plan(tmp_path: Path) -> None:
    run_dir = tmp_path / "creator-run"
    init_creator_run(run_dir, domain="Startup YC", goal="Doctor this run.")
    env = {**os.environ, "PYTHONPATH": str(Path.cwd() / "src")}

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "chip_labs.cli",
            "creator-run-doctor",
            str(run_dir),
        ],
        cwd=Path.cwd(),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "adaptive_creator_loop.doctor_result.v1" in result.stdout
    assert "artifact_scaffold" in result.stdout


def test_cli_creator_run_template_check_passes() -> None:
    env = {**os.environ, "PYTHONPATH": str(Path.cwd() / "src")}

    result = subprocess.run(
        [sys.executable, "-m", "chip_labs.cli", "creator-run-template-check"],
        cwd=Path.cwd(),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "adaptive_creator_loop.template_check_result.v1" in result.stdout
    assert '"verdict": "pass"' in result.stdout


def test_creator_run_ready_for_baseline_when_core_artifacts_exist(
    tmp_path: Path,
) -> None:
    run_dir = tmp_path / "creator-run"
    init_creator_run(run_dir, domain="Startup YC", goal="Test readiness.")

    for relative_path in (
        "domain-chip/chip.manifest.json",
        "domain-chip/doctrine.md",
        "domain-chip/scoring_hooks.json",
        "specialization-path/path.manifest.json",
        "specialization-path/absorption_bundle.md",
        "benchmark/manifest.json",
        "benchmark/cases.jsonl",
        "benchmark/scoring_rubric.md",
        "benchmark/traps.jsonl",
        "autoloop/policy.json",
        "autoloop/mutation_surface.md",
        "autoloop/stop_conditions.md",
    ):
        path = run_dir / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "{}\n" if path.suffix == ".json" else "draft\n", encoding="utf-8"
        )

    smoke = validate_creator_run(run_dir)

    assert smoke.verdict == "ready_for_baseline"
    assert "reports/baseline.json" in smoke.missing_paths


def test_creator_run_ready_for_swarm_packet_when_reports_exist(tmp_path: Path) -> None:
    run_dir = tmp_path / "creator-run"
    init_creator_run(run_dir, domain="Startup YC", goal="Test swarm readiness.")

    for relative_path in (
        "domain-chip/chip.manifest.json",
        "domain-chip/doctrine.md",
        "domain-chip/scoring_hooks.json",
        "specialization-path/path.manifest.json",
        "specialization-path/absorption_bundle.md",
        "benchmark/manifest.json",
        "benchmark/cases.jsonl",
        "benchmark/scoring_rubric.md",
        "benchmark/traps.jsonl",
        "autoloop/policy.json",
        "autoloop/mutation_surface.md",
        "autoloop/stop_conditions.md",
        "reports/baseline.json",
        "reports/candidate.json",
        "reports/absorption_summary.json",
        "reports/creator_run_summary.md",
        "swarm/contribution_packet.json",
    ):
        path = run_dir / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "{}\n" if path.suffix == ".json" else "draft\n", encoding="utf-8"
        )

    smoke = validate_creator_run(run_dir)

    assert smoke.verdict == "ready_for_swarm_packet"
    assert smoke.missing_paths == ()


def test_creator_run_blocks_unknown_evidence_tier(tmp_path: Path) -> None:
    run_dir = tmp_path / "creator-run"
    init_creator_run(run_dir, domain="Startup YC", goal="Test evidence tier.")
    adapter_path = run_dir / "adapter-map.json"
    adapter_map = json.loads(adapter_path.read_text(encoding="utf-8"))
    adapter_map["swarm_adapter"]["evidence_tier"] = "magic_mastery"
    adapter_path.write_text(json.dumps(adapter_map), encoding="utf-8")

    smoke = validate_creator_run(run_dir)

    assert smoke.verdict == "blocked"
    assert any(
        check.name == "evidence_tier" and check.status == "fail"
        for check in smoke.checks
    )


def test_creator_run_blocks_missing_intent(tmp_path: Path) -> None:
    run_dir = tmp_path / "creator-run"
    init_creator_run(run_dir, domain="Startup YC", goal="Test missing intent.")
    (run_dir / "creator-intent.json").unlink()

    smoke = validate_creator_run(run_dir)

    assert smoke.verdict == "blocked"
    assert any(
        check.name == "creator_intent" and check.status == "fail"
        for check in smoke.checks
    )


def test_creator_run_blocks_missing_artifact_manifest(tmp_path: Path) -> None:
    run_dir = tmp_path / "creator-run"
    init_creator_run(run_dir, domain="Startup YC", goal="Test missing manifest.")
    (run_dir / "created-artifact-manifest.json").unlink()

    smoke = validate_creator_run(run_dir)

    assert smoke.verdict == "blocked"
    assert any(
        check.name == "created_artifact_manifest" and check.status == "fail"
        for check in smoke.checks
    )


def test_creator_run_blocks_artifact_manifest_run_id_mismatch(
    tmp_path: Path,
) -> None:
    run_dir = tmp_path / "creator-run"
    init_creator_run(run_dir, domain="Startup YC", goal="Test manifest mismatch.")
    manifest_path = run_dir / "created-artifact-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["creator_run_id"] = "creator-run-other"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    smoke = validate_creator_run(run_dir)

    assert smoke.verdict == "blocked"
    assert any(
        check.name == "created_artifact_manifest_run_id"
        and check.status == "fail"
        for check in smoke.checks
    )


def test_candidate_review_blocks_negative_delta(tmp_path: Path) -> None:
    run_dir = _write_candidate_review_run(tmp_path)
    candidate_path = run_dir / "reports" / "candidate.json"
    candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
    candidate["mean_score"] = 0.49
    candidate["mean_delta"] = -0.01
    candidate_path.write_text(json.dumps(candidate), encoding="utf-8")

    smoke = validate_creator_run(run_dir)

    assert smoke.verdict == "blocked"
    assert any(
        check.name == "candidate_delta" and check.status == "fail"
        for check in smoke.checks
    )
    assert any(
        check.name == "candidate_beats_baseline" and check.status == "fail"
        for check in smoke.checks
    )


def test_candidate_review_blocks_missing_evidence_ladder(tmp_path: Path) -> None:
    run_dir = _write_candidate_review_run(tmp_path)
    (run_dir / "reports" / "evidence_ladder.md").unlink()

    smoke = validate_creator_run(run_dir)

    assert smoke.verdict == "blocked"
    assert any(
        check.name == "evidence_ladder" and check.status == "fail"
        for check in smoke.checks
    )


def test_candidate_review_blocks_unsupported_evidence_ladder_tier(
    tmp_path: Path,
) -> None:
    run_dir = _write_candidate_review_run(tmp_path, evidence_tier="transfer_supported")
    ladder_path = run_dir / "reports" / "evidence_ladder.md"
    text = ladder_path.read_text(encoding="utf-8")
    ladder_path.write_text(
        text.replace("Weakest supported tier: transfer_supported", "Weakest supported tier: candidate_review"),
        encoding="utf-8",
    )
    _write_transfer_report(run_dir)

    smoke = validate_creator_run(run_dir)

    assert smoke.verdict == "blocked"
    assert any(
        check.name == "evidence_ladder_weakest_tier" and check.status == "fail"
        for check in smoke.checks
    )


def test_candidate_review_blocks_swarm_packet_mismatch(tmp_path: Path) -> None:
    run_dir = _write_candidate_review_run(tmp_path)
    packet_path = run_dir / "swarm" / "contribution_packet.json"
    packet = json.loads(packet_path.read_text(encoding="utf-8"))
    packet["evidence"]["tier"] = "prototype"
    packet["evidence"]["mean_delta"] = 0.99
    packet_path.write_text(json.dumps(packet), encoding="utf-8")

    smoke = validate_creator_run(run_dir)

    assert smoke.verdict == "blocked"
    assert any(
        check.name == "swarm_packet_tier" and check.status == "fail"
        for check in smoke.checks
    )
    assert any(
        check.name == "swarm_packet_delta" and check.status == "fail"
        for check in smoke.checks
    )


def test_candidate_review_blocks_missing_trap_coverage(tmp_path: Path) -> None:
    run_dir = _write_candidate_review_run(tmp_path)
    absorption_path = run_dir / "reports" / "absorption_summary.json"
    absorption = json.loads(absorption_path.read_text(encoding="utf-8"))
    absorption["trap_band_case_count"] = 0
    absorption_path.write_text(json.dumps(absorption), encoding="utf-8")

    smoke = validate_creator_run(run_dir)

    assert smoke.verdict == "blocked"
    assert any(
        check.name == "trap_coverage" and check.status == "fail"
        for check in smoke.checks
    )


def test_transfer_supported_requires_transfer_report(tmp_path: Path) -> None:
    run_dir = _write_candidate_review_run(tmp_path, evidence_tier="transfer_supported")

    smoke = validate_creator_run(run_dir)

    assert smoke.verdict == "blocked"
    assert any(
        check.name == "transfer_report" and check.status == "fail"
        for check in smoke.checks
    )


def test_transfer_supported_blocks_negative_transfer_delta(tmp_path: Path) -> None:
    run_dir = _write_candidate_review_run(tmp_path, evidence_tier="transfer_supported")
    _write_transfer_report(run_dir, delta=-0.01)

    smoke = validate_creator_run(run_dir)

    assert smoke.verdict == "blocked"
    assert any(
        check.name == "transfer_delta" and check.status == "fail"
        for check in smoke.checks
    )


def test_transfer_supported_accepts_positive_transfer_report(tmp_path: Path) -> None:
    run_dir = _write_candidate_review_run(tmp_path, evidence_tier="transfer_supported")
    _write_transfer_report(run_dir)

    smoke = validate_creator_run(run_dir)

    assert smoke.verdict == "ready_for_swarm_packet"
    assert any(
        check.name == "transfer_delta" and check.status == "pass"
        for check in smoke.checks
    )


def test_transfer_supported_warns_on_negative_broad_probe(tmp_path: Path) -> None:
    run_dir = _write_candidate_review_run(tmp_path, evidence_tier="transfer_supported")
    _write_transfer_report(run_dir)
    _write_broad_transfer_probe(run_dir, delta=-0.01)

    smoke = validate_creator_run(run_dir)

    assert smoke.verdict == "ready_for_swarm_packet"
    assert any(
        check.name == "broad_transfer_delta" and check.status == "warn"
        for check in smoke.checks
    )


def test_transfer_supported_warns_on_mixed_positive_broad_probe(
    tmp_path: Path,
) -> None:
    run_dir = _write_candidate_review_run(tmp_path, evidence_tier="transfer_supported")
    _write_transfer_report(run_dir)
    _write_broad_transfer_probe(
        run_dir, delta=0.03, min_delta=-0.01, negative_scenarios=1
    )

    smoke = validate_creator_run(run_dir)

    assert smoke.verdict == "ready_for_swarm_packet"
    assert any(
        check.name == "broad_transfer_no_negative_rows" and check.status == "warn"
        for check in smoke.checks
    )


def test_recompute_checks_external_startup_yc_transfer_source(
    tmp_path: Path,
) -> None:
    run_dir = _write_candidate_review_run(tmp_path, evidence_tier="transfer_supported")
    source_report = tmp_path / "adapter_selector_report.json"
    _write_external_selector_report(source_report, delta=0.02)
    _write_transfer_report(run_dir, delta=0.02, selector_report=source_report)

    smoke = validate_creator_run(run_dir, recompute=True)

    assert any(
        check.name == "external_recompute_transfer_delta"
        and check.status == "pass"
        for check in smoke.checks
    )
    assert any(
        check.name == "recompute_provenance_source" and check.status == "fail"
        for check in smoke.checks
    )


def test_recompute_blocks_stale_external_startup_yc_transfer_source(
    tmp_path: Path,
) -> None:
    run_dir = _write_candidate_review_run(tmp_path, evidence_tier="transfer_supported")
    source_report = tmp_path / "adapter_selector_report.json"
    _write_external_selector_report(source_report, delta=0.02)
    _write_transfer_report(run_dir, delta=0.03, selector_report=source_report)

    smoke = validate_creator_run(run_dir, recompute=True)

    assert smoke.verdict == "blocked"
    assert any(
        check.name == "external_recompute_transfer_delta"
        and check.status == "fail"
        for check in smoke.checks
    )


def test_recompute_checks_external_startup_yc_absorption_source(
    tmp_path: Path,
) -> None:
    run_dir = _write_candidate_review_run(tmp_path, evidence_tier="transfer_supported")
    source_report = tmp_path / "proof_report.json"
    _write_external_absorption_report(source_report, candidate_score=0.53)
    _attach_absorption_source_report(run_dir, source_report)
    _write_transfer_report(run_dir)

    smoke = validate_creator_run(run_dir, recompute=True)

    assert any(
        check.name == "external_recompute_absorption_candidate_score"
        and check.status == "pass"
        for check in smoke.checks
    )
    assert any(
        check.name == "recompute_provenance_source" and check.status == "fail"
        for check in smoke.checks
    )


def test_recompute_accepts_startup_yc_external_provenance(
    tmp_path: Path,
) -> None:
    run_dir = _write_candidate_review_run(tmp_path, evidence_tier="transfer_supported")
    source_report = tmp_path / "proof_report.json"
    _write_external_absorption_report(source_report, candidate_score=0.53)
    _attach_absorption_source_report(run_dir, source_report)
    _attach_startup_yc_external_provenance(run_dir, source_report)
    _write_transfer_report(run_dir)
    _write_complete_swarm_packet_evidence(run_dir)

    smoke = validate_creator_run(run_dir, recompute=True)

    assert smoke.verdict == "ready_for_swarm_packet"
    assert any(
        check.name == "recompute_inputs" and check.status == "pass"
        for check in smoke.checks
    )


def test_recompute_blocks_stale_startup_yc_external_provenance_hash(
    tmp_path: Path,
) -> None:
    run_dir = _write_candidate_review_run(tmp_path, evidence_tier="transfer_supported")
    source_report = tmp_path / "proof_report.json"
    _write_external_absorption_report(source_report, candidate_score=0.53)
    _attach_absorption_source_report(run_dir, source_report)
    _attach_startup_yc_external_provenance(run_dir, source_report, digest="stale")
    _write_transfer_report(run_dir)
    _write_complete_swarm_packet_evidence(run_dir)

    smoke = validate_creator_run(run_dir, recompute=True)

    assert smoke.verdict == "blocked"
    assert any(
        check.name == "report_provenance:reports/baseline.json:input_hashes"
        and check.status == "fail"
        for check in smoke.checks
    )


def test_creator_run_doctor_quarantines_stale_external_startup_yc_fixture(
    tmp_path: Path,
) -> None:
    fixture = json.loads(
        (
            DOCTOR_FIXTURE_DIR / "stale_external_startup_yc_candidate_score.json"
        ).read_text(encoding="utf-8")
    )
    run_dir = _write_candidate_review_run(tmp_path, evidence_tier="transfer_supported")
    source_report = tmp_path / "proof_report.json"
    _write_external_absorption_report(source_report, candidate_score=0.53)
    _attach_absorption_source_report(run_dir, source_report)
    _attach_startup_yc_external_provenance(run_dir, source_report)
    _write_transfer_report(run_dir)
    _write_complete_swarm_packet_evidence(run_dir)

    report_path = run_dir / fixture["path"]
    report = json.loads(report_path.read_text(encoding="utf-8"))
    for operation in fixture["operations"]:
        report[operation["field"]] += operation["delta"]
    report_path.write_text(json.dumps(report), encoding="utf-8")

    diagnosis = diagnose_creator_run(run_dir, recompute=True)

    expected_check = fixture["expected_blocking_checks"][0]
    assert diagnosis["verdict"] == "blocked"
    assert expected_check in diagnosis["smoke"]["blocking_checks"]
    assert diagnosis["quarantine"][0]["reason"] == "saved_evidence_not_replayable"
    assert expected_check in diagnosis["quarantine"][0]["related_checks"]
    assert any(
        step["area"] == "recompute_provenance"
        and expected_check in step["related_checks"]
        for step in diagnosis["repair_steps"]
    )
    assert diagnosis["repair_calibration"]["verdict"] == "pass"
    assert diagnosis["repair_calibration"]["uncovered_smoke_checks"] == []


def test_recompute_blocks_stale_external_startup_yc_absorption_source(
    tmp_path: Path,
) -> None:
    run_dir = _write_candidate_review_run(tmp_path, evidence_tier="transfer_supported")
    source_report = tmp_path / "proof_report.json"
    _write_external_absorption_report(source_report, candidate_score=0.52)
    _attach_absorption_source_report(run_dir, source_report)
    _write_transfer_report(run_dir)

    smoke = validate_creator_run(run_dir, recompute=True)

    assert smoke.verdict == "blocked"
    assert any(
        check.name == "external_recompute_absorption_candidate_score"
        and check.status == "fail"
        for check in smoke.checks
    )


def test_recompute_checks_external_startup_yc_broad_transfer_source(
    tmp_path: Path,
) -> None:
    run_dir = _write_candidate_review_run(tmp_path, evidence_tier="transfer_supported")
    source_report = tmp_path / "adapter_selector_report.json"
    _write_external_selector_report(source_report, delta=0.02, scenario_id="case_0")
    _write_transfer_report(run_dir, selector_report=source_report)
    _write_broad_transfer_probe(run_dir, delta=0.02, scenario_count=1)

    smoke = validate_creator_run(run_dir, recompute=True)

    assert any(
        check.name == "external_recompute_broad_transfer_rows"
        and check.status == "pass"
        for check in smoke.checks
    )
    assert any(
        check.name == "recompute_provenance_source" and check.status == "fail"
        for check in smoke.checks
    )


def test_recompute_blocks_stale_external_startup_yc_broad_transfer_source(
    tmp_path: Path,
) -> None:
    run_dir = _write_candidate_review_run(tmp_path, evidence_tier="transfer_supported")
    source_report = tmp_path / "adapter_selector_report.json"
    _write_external_selector_report(source_report, delta=0.02, scenario_id="case_0")
    _write_transfer_report(run_dir, selector_report=source_report)
    _write_broad_transfer_probe(run_dir, delta=0.03, scenario_count=1)

    smoke = validate_creator_run(run_dir, recompute=True)

    assert smoke.verdict == "blocked"
    assert any(
        check.name == "external_recompute_broad_transfer_delta"
        and check.status == "fail"
        for check in smoke.checks
    )


def test_recompute_checks_external_startup_yc_swarm_packet(
    tmp_path: Path,
) -> None:
    run_dir = _write_candidate_review_run(tmp_path, evidence_tier="transfer_supported")
    _write_transfer_report(run_dir)
    _write_broad_transfer_probe(run_dir)
    _write_complete_swarm_packet_evidence(run_dir)

    smoke = validate_creator_run(run_dir, recompute=True)

    assert any(
        check.name == "external_recompute_swarm_mean_delta"
        and check.status == "pass"
        for check in smoke.checks
    )
    assert any(
        check.name == "external_recompute_swarm_publication_boundary"
        and check.status == "pass"
        for check in smoke.checks
    )


def test_recompute_blocks_stale_external_startup_yc_swarm_packet(
    tmp_path: Path,
) -> None:
    run_dir = _write_candidate_review_run(tmp_path, evidence_tier="transfer_supported")
    _write_transfer_report(run_dir)
    _write_broad_transfer_probe(run_dir)
    _write_complete_swarm_packet_evidence(run_dir)
    packet_path = run_dir / "swarm" / "contribution_packet.json"
    packet = json.loads(packet_path.read_text(encoding="utf-8"))
    packet["evidence"]["candidate_score"] = 0.99
    packet_path.write_text(json.dumps(packet), encoding="utf-8")

    smoke = validate_creator_run(run_dir, recompute=True)

    assert smoke.verdict == "blocked"
    assert any(
        check.name == "external_recompute_swarm_candidate_score"
        and check.status == "fail"
        for check in smoke.checks
    )


def test_network_absorbable_blocks_negative_broad_probe(tmp_path: Path) -> None:
    run_dir = _write_candidate_review_run(tmp_path, evidence_tier="network_absorbable")
    _write_transfer_report(run_dir)
    _write_broad_transfer_probe(run_dir, delta=-0.01)

    smoke = validate_creator_run(run_dir)

    assert smoke.verdict == "blocked"
    assert any(
        check.name == "broad_transfer_delta" and check.status == "fail"
        for check in smoke.checks
    )


def test_network_absorbable_blocks_mixed_positive_broad_probe(
    tmp_path: Path,
) -> None:
    run_dir = _write_candidate_review_run(tmp_path, evidence_tier="network_absorbable")
    _write_transfer_report(run_dir)
    _write_broad_transfer_probe(
        run_dir, delta=0.03, min_delta=-0.01, negative_scenarios=1
    )

    smoke = validate_creator_run(run_dir)

    assert smoke.verdict == "blocked"
    assert any(
        check.name == "broad_transfer_no_negative_rows" and check.status == "fail"
        for check in smoke.checks
    )


def _write_candidate_review_run(
    tmp_path: Path, evidence_tier: str = "candidate_review"
) -> Path:
    run_dir = tmp_path / "candidate-review-run"
    init_creator_run(
        run_dir, domain="Startup YC", goal="Test candidate review evidence."
    )

    adapter_path = run_dir / "adapter-map.json"
    adapter_map = json.loads(adapter_path.read_text(encoding="utf-8"))
    adapter_map["swarm_adapter"]["evidence_tier"] = evidence_tier
    adapter_path.write_text(json.dumps(adapter_map), encoding="utf-8")

    for relative_path in (
        "domain-chip/chip.manifest.json",
        "domain-chip/doctrine.md",
        "domain-chip/scoring_hooks.json",
        "specialization-path/path.manifest.json",
        "specialization-path/absorption_bundle.md",
        "benchmark/manifest.json",
        "benchmark/cases.jsonl",
        "benchmark/scoring_rubric.md",
        "benchmark/traps.jsonl",
        "autoloop/policy.json",
        "autoloop/mutation_surface.md",
        "autoloop/stop_conditions.md",
    ):
        path = run_dir / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "{}\n" if path.suffix == ".json" else "draft\n", encoding="utf-8"
        )

    (run_dir / "reports" / "baseline.json").write_text(
        json.dumps({"mean_score": 0.5}),
        encoding="utf-8",
    )
    (run_dir / "reports" / "candidate.json").write_text(
        json.dumps({"mean_score": 0.53, "mean_delta": 0.03}),
        encoding="utf-8",
    )
    (run_dir / "reports" / "absorption_summary.json").write_text(
        json.dumps(
            {
                "all_modes_present": True,
                "all_modes_scored": True,
                "mean_validated_pack_delta": 0.03,
                "trap_band_case_count": 2,
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "reports" / "creator_run_summary.md").write_text(
        "summary\n", encoding="utf-8"
    )
    (run_dir / "swarm" / "contribution_packet.json").write_text(
        json.dumps(
            {
                "source": {"commit": "abc123"},
                "evidence": {
                    "tier": evidence_tier,
                    "mean_delta": 0.03,
                    "trap_regressions": 0,
                },
                "governance": {
                    "rollback_or_deprecation_rule": "rollback if repeat fails",
                },
            }
        ),
        encoding="utf-8",
    )
    _write_evidence_ladder(run_dir, evidence_tier)
    return run_dir


def _write_transfer_report(
    run_dir: Path, delta: float = 0.02, selector_report: Path | None = None
) -> None:
    transfer_score = 0.62 + delta
    transfer = {
        "source": "startup-bench",
        "scenario_count": 1,
        "baseline_score": 0.62,
        "transfer_score": transfer_score,
        "delta": delta,
        "min_delta": delta,
        "max_delta": delta,
        "constraints_passed": True,
    }
    if selector_report is not None:
        transfer["source_artifacts"] = {"selector_report": str(selector_report)}
    (run_dir / "reports" / "transfer_summary.json").write_text(
        json.dumps(transfer),
        encoding="utf-8",
    )
    packet_path = run_dir / "swarm" / "contribution_packet.json"
    packet = json.loads(packet_path.read_text(encoding="utf-8"))
    packet["evidence"]["simulator_or_arena_result"] = {
        "source": "startup-bench",
        "scenario_count": 1,
        "delta": delta,
    }
    packet_path.write_text(json.dumps(packet), encoding="utf-8")


def _write_complete_swarm_packet_evidence(run_dir: Path) -> None:
    baseline = json.loads(
        (run_dir / "reports" / "baseline.json").read_text(encoding="utf-8")
    )
    candidate = json.loads(
        (run_dir / "reports" / "candidate.json").read_text(encoding="utf-8")
    )
    absorption = json.loads(
        (run_dir / "reports" / "absorption_summary.json").read_text(encoding="utf-8")
    )
    transfer = json.loads(
        (run_dir / "reports" / "transfer_summary.json").read_text(encoding="utf-8")
    )
    packet_path = run_dir / "swarm" / "contribution_packet.json"
    packet = json.loads(packet_path.read_text(encoding="utf-8"))
    packet["evidence"].update(
        {
            "baseline_score": baseline["mean_score"],
            "candidate_score": candidate["mean_score"],
            "mean_delta": candidate["mean_delta"],
            "fresh_agent_absorption_delta": absorption[
                "mean_validated_pack_delta"
            ],
            "simulator_or_arena_result": {
                "scenario_count": transfer["scenario_count"],
                "baseline_score": transfer["baseline_score"],
                "transfer_score": transfer["transfer_score"],
                "delta": transfer["delta"],
                "min_delta": transfer["min_delta"],
                "max_delta": transfer["max_delta"],
                "constraints_passed": transfer["constraints_passed"],
            },
            "report_paths": [
                "reports/baseline.json",
                "reports/candidate.json",
                "reports/absorption_summary.json",
                "reports/evidence_ladder.md",
                "reports/transfer_summary.json",
                "reports/broad_transfer_probe.json",
            ],
        }
    )
    packet["governance"]["network_publication_allowed"] = False
    packet_path.write_text(json.dumps(packet), encoding="utf-8")


def _write_external_selector_report(
    path: Path, delta: float, scenario_id: str = "external_case"
) -> None:
    path.write_text(
        json.dumps(
            {
                "schema_version": "startup_yc.adapter_selector_report.v1",
                "summary": {
                    "scenario_count": 1,
                    "win_count": 1 if delta > 0 else 0,
                    "skipped_count": 0,
                    "mean_delta": delta,
                    "min_delta": delta,
                    "max_delta": delta,
                },
                "results": [
                    {
                        "status": "ok",
                        "selection": {
                            "scenario": {
                                "scenario_id": scenario_id,
                                "track": "gtm",
                            }
                        },
                        "runs": {
                            "candidate": {
                                "score": {
                                    "scenario_score": 0.62 + delta,
                                    "pass": True,
                                }
                            },
                            "baseline": {
                                "score": {
                                    "scenario_score": 0.62,
                                    "pass": True,
                                }
                            },
                        },
                        "delta": {"scenario_score": delta},
                        "verdict": "win" if delta > 0 else "loss",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )


def _attach_absorption_source_report(run_dir: Path, source_report: Path) -> None:
    for relative_path in (
        "reports/baseline.json",
        "reports/candidate.json",
        "reports/absorption_summary.json",
    ):
        path = run_dir / relative_path
        report = json.loads(path.read_text(encoding="utf-8"))
        report["source_report"] = str(source_report)
        if relative_path.endswith("baseline.json"):
            report["pass_rate"] = 0.95
            report["case_count"] = 20
        if relative_path.endswith("candidate.json"):
            report["pass_rate"] = 0.95
            report["case_count"] = 20
            report["positive_cases"] = 15
            report["negative_cases"] = 4
            report["flat_cases"] = 1
        path.write_text(json.dumps(report), encoding="utf-8")


def _attach_startup_yc_external_provenance(
    run_dir: Path, source_report: Path, digest: str | None = None
) -> None:
    resolved_digest = digest or hashlib.sha256(source_report.read_bytes()).hexdigest()
    for relative_path in (
        "reports/baseline.json",
        "reports/candidate.json",
        "reports/absorption_summary.json",
    ):
        path = run_dir / relative_path
        report = json.loads(path.read_text(encoding="utf-8"))
        report["provenance"] = {
            "source": "startup_yc_external_v1",
            "input_hashes": {str(source_report): resolved_digest},
        }
        path.write_text(json.dumps(report), encoding="utf-8")


def _write_external_absorption_report(path: Path, candidate_score: float) -> None:
    candidate_delta = candidate_score - 0.5
    path.write_text(
        json.dumps(
            {
                "summary": {
                    "case_count": 20,
                    "integrity": {
                        "all_modes_present": True,
                        "all_modes_scored": True,
                    },
                    "score_summary": {
                        "mean_no_pack_score": 0.5,
                        "mean_validated_pack_score": candidate_score,
                        "mean_validated_pack_delta": candidate_delta,
                        "pass_rates": {
                            "no_pack": 0.95,
                            "validated_pack": 0.95,
                        },
                        "validated_delta_buckets": {
                            "positive": 15,
                            "negative": 4,
                            "flat": 1,
                        },
                    },
                    "trap_integrity": {
                        "trap_case_count": 2,
                    },
                },
            }
        ),
        encoding="utf-8",
    )


def _write_broad_transfer_probe(
    run_dir: Path,
    delta: float = 0.03,
    min_delta: float | None = None,
    negative_scenarios: int | None = None,
    scenario_count: int = 10,
) -> None:
    baseline_score = 0.62
    transfer_score = baseline_score + delta
    resolved_min_delta = delta if min_delta is None else min_delta
    resolved_negative_scenarios = (
        0 if negative_scenarios is None and resolved_min_delta > 0 else negative_scenarios
    )
    if resolved_negative_scenarios is None:
        resolved_negative_scenarios = 1
    (run_dir / "reports" / "broad_transfer_probe.json").write_text(
        json.dumps(
            {
                "source": "startup-bench",
                "scenario_count": scenario_count,
                "baseline_score": baseline_score,
                "transfer_score": transfer_score,
                "delta": delta,
                "min_delta": resolved_min_delta,
                "negative_scenarios": resolved_negative_scenarios,
                "constraints_passed": True,
                "verdict": (
                    "broad_transfer_supported" if delta > 0 else "defer_broad_transfer"
                ),
                "scenario_results": [
                    {
                        "scenario_id": f"case_{index}",
                        "track": "gtm",
                        "startup_yc_score": baseline_score + resolved_min_delta,
                        "baseline_score": baseline_score,
                        "delta": resolved_min_delta,
                        "startup_yc_pass_rate": 1,
                        "baseline_pass_rate": 1,
                    }
                    for index in range(scenario_count)
                ],
            }
        ),
        encoding="utf-8",
    )


def _apply_fixture_operation(packet: dict[str, object], operation: dict[str, object]) -> None:
    if operation["op"] != "set_nested":
        raise AssertionError(f"Unsupported fixture operation: {operation['op']}")
    current = packet
    field_path = operation["field_path"]
    if not isinstance(field_path, list):
        raise AssertionError("Fixture field_path must be a list")
    for key in field_path[:-1]:
        if not isinstance(key, str):
            raise AssertionError("Fixture field_path entries must be strings")
        next_value = current[key]
        if not isinstance(next_value, dict):
            raise AssertionError(f"Fixture path {key} does not point to an object")
        current = next_value
    final_key = field_path[-1]
    if not isinstance(final_key, str):
        raise AssertionError("Fixture final field_path entry must be a string")
    current[final_key] = operation["value"]


def _write_evidence_ladder(run_dir: Path, evidence_tier: str) -> None:
    transfer_status = "pass" if evidence_tier in {
        "transfer_supported",
        "network_absorbable",
        "standard_update",
    } else "warn"
    broad_status = "pass" if evidence_tier in {
        "network_absorbable",
        "standard_update",
    } else "warn"
    (run_dir / "reports" / "evidence_ladder.md").write_text(
        f"""# Evidence Ladder

Run ID: candidate-review-run
Domain: Startup YC
Target capability: Test evidence validation
Claim being tested: Candidate packet improves Startup YC behavior.

## Tier Claimed

Claimed tier: {evidence_tier}

Weakest supported tier: {evidence_tier}

Reason: Test fixture supports the claimed tier.

## Gate Checklist

| Gate | Status | Evidence path | Notes |
| --- | --- | --- | --- |
| Prototype scaffold | pass | creator-intent.json | ok |
| Baseline benchmark | pass | reports/baseline.json | ok |
| Candidate benchmark | pass | reports/candidate.json | ok |
| Held-out or weak-case replay | warn | reports/candidate.json | not required for this fixture |
| Fresh-agent absorption | pass | reports/absorption_summary.json | ok |
| Trap/adversarial coverage | pass | reports/absorption_summary.json | ok |
| Transfer probe | {transfer_status} | reports/transfer_summary.json | tier dependent |
| Broad transfer probe | {broad_status} | reports/broad_transfer_probe.json | tier dependent |
| Swarm packet consistency | pass | swarm/contribution_packet.json | ok |
| Privacy/provenance/rollback | pass | swarm/contribution_packet.json | ok |

## Score Summary

| Surface | Baseline | Candidate | Delta | Min Delta | Constraints | Verdict |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| Main benchmark | 0.50 | 0.53 | +0.03 | +0.03 | pass | pass |

## Failure Lineage

- Weakness found: Fixture weakness.
- Benchmark or trace that exposed it: Test report.
- Patch or packet mechanism: Test mechanism.
- Counterfactual if unchanged: No improvement.

## Safe Claim

```text
The fixture supports {evidence_tier} inside this test boundary.
```

## Unsafe Claim

```text
The fixture proves broad mastery.
```

## Remaining Gaps

- Test-only fixture.
""",
        encoding="utf-8",
    )
