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


def test_creator_run_ready_for_baseline_when_core_artifacts_exist(tmp_path: Path) -> None:
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
        path.write_text("{}\n" if path.suffix == ".json" else "draft\n", encoding="utf-8")

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
        path.write_text("{}\n" if path.suffix == ".json" else "draft\n", encoding="utf-8")

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
    assert any(check.name == "evidence_tier" and check.status == "fail" for check in smoke.checks)


def test_creator_run_blocks_missing_intent(tmp_path: Path) -> None:
    run_dir = tmp_path / "creator-run"
    init_creator_run(run_dir, domain="Startup YC", goal="Test missing intent.")
    (run_dir / "creator-intent.json").unlink()

    smoke = validate_creator_run(run_dir)

    assert smoke.verdict == "blocked"
    assert any(check.name == "creator_intent" and check.status == "fail" for check in smoke.checks)

