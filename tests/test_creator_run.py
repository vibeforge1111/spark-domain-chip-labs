from __future__ import annotations

import json
from pathlib import Path

from chip_labs.creator_run import init_creator_run, validate_creator_run


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
    assert smoke.verdict == "prototype"
    assert "benchmark/manifest.json" in smoke.missing_paths


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
    return run_dir


def _write_transfer_report(run_dir: Path, delta: float = 0.02) -> None:
    transfer_score = 0.62 + delta
    (run_dir / "reports" / "transfer_summary.json").write_text(
        json.dumps(
            {
                "source": "startup-bench",
                "scenario_count": 1,
                "baseline_score": 0.62,
                "transfer_score": transfer_score,
                "delta": delta,
                "constraints_passed": True,
            }
        ),
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


def _write_broad_transfer_probe(run_dir: Path, delta: float = 0.03) -> None:
    baseline_score = 0.62
    transfer_score = baseline_score + delta
    (run_dir / "reports" / "broad_transfer_probe.json").write_text(
        json.dumps(
            {
                "source": "startup-bench",
                "scenario_count": 10,
                "baseline_score": baseline_score,
                "transfer_score": transfer_score,
                "delta": delta,
                "constraints_passed": True,
                "verdict": (
                    "broad_transfer_supported" if delta > 0 else "defer_broad_transfer"
                ),
            }
        ),
        encoding="utf-8",
    )
