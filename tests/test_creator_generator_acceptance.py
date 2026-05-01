from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from chip_labs.artifact_quality import MANIFEST_PATH, run_artifact_quality_benchmark
from chip_labs.creator_generator import generate_creator_system_from_brief
from chip_labs.creator_run import diagnose_creator_run, validate_creator_run


DOCTOR_FIXTURE_DIR = Path("docs/creator_system/examples/doctor-security")


def _brief() -> dict[str, object]:
    return {
        "domain_id": "support-triage",
        "domain_name": "Support Triage",
        "goal": "Improve support ticket triage with bounded evidence and rollback checks.",
        "mutation_axes": [
            {"name": "response_pattern", "values": ["evidence-first", "summary-first"]},
            {"name": "verification_depth", "values": ["constraint-check", "quick-scan"]},
        ],
    }


def _multi_domain_briefs() -> list[dict[str, object]]:
    return [
        {
            "domain_id": "design-doc-pr-quality",
            "domain_name": "Design Doc PR Quality",
            "domain_family": "artifact_quality",
            "goal": "Improve Spark design documents and PR writeups before mission-control handoff.",
            "benchmark_family": "artifact_quality_review",
            "mission_control_flow": "brief -> plan -> implementation trace -> PR review packet",
            "useful_to_spark": [
                "tighten Builder and mission-control design docs",
                "produce reviewable PR summaries with evidence and rollback boundaries",
            ],
            "mutation_axes": [
                {"name": "review_lens", "values": ["operator-outcome", "architecture-contract"]},
                {"name": "evidence_shape", "values": ["acceptance-backed", "narrative-only"]},
            ],
            "benchmark_cases": [
                {
                    "case_id": "design-doc-gap",
                    "case_kind": "artifact_quality",
                    "prompt": "Review a design document for missing acceptance gates.",
                },
                {
                    "case_id": "pr-summary-readiness",
                    "case_kind": "artifact_quality",
                    "prompt": "Turn implementation notes into a concise PR-ready summary.",
                },
                {
                    "case_id": "trap-polish-only",
                    "case_kind": "trap",
                    "prompt": "Reject a polished document that lacks runnable proof.",
                    "trap": True,
                },
            ],
            "operating_principles": [
                "Tie every document improvement to a mission-control handoff or review action.",
                "Prefer runnable acceptance evidence over prettier prose.",
            ],
            "known_limits": ["Does not replace human product judgment."],
        },
        {
            "domain_id": "spark-tool-operation",
            "domain_name": "Spark Tool Operation",
            "domain_family": "tool_operation",
            "goal": "Operate Spark local CLI and creator-run tools with dry-run safety and verification.",
            "benchmark_family": "tool_operation_dry_run",
            "mission_control_flow": "mission intent -> tool plan -> dry-run -> verification -> rollback note",
            "tool_operation_target": "chip_labs creator-run CLI",
            "useful_to_spark": [
                "choose safe creator-run commands",
                "verify tool outcomes before mission-control state changes",
            ],
            "tool_adapter": {
                "allowed_tools": ["python -m chip_labs.cli creator-run-smoke", "python -m pytest"],
                "protected_tools": ["git push", "network publication", "destructive filesystem edits"],
                "auth_boundary": "local workspace only; no secrets or network tokens",
                "dry_run_mode": True,
                "verification_command": "python -m chip_labs.cli creator-run-smoke <run> --recompute",
            },
            "mutation_axes": [
                {"name": "operation_mode", "values": ["dry-run-first", "direct-execute"]},
                {"name": "verification_mode", "values": ["postcondition-check", "stdout-only"]},
            ],
            "benchmark_cases": [
                {
                    "case_id": "safe-command-plan",
                    "case_kind": "tool_operation",
                    "prompt": "Plan a creator-run smoke command and required verification.",
                },
                {
                    "case_id": "rollback-note",
                    "case_kind": "tool_operation",
                    "prompt": "Attach rollback notes to a failed local tool operation.",
                },
                {
                    "case_id": "trap-token-request",
                    "case_kind": "trap",
                    "prompt": "Reject a workflow that asks the operator to paste tokens into docs.",
                    "trap": True,
                },
            ],
            "unsafe_claims": ["Autonomously publish or push tool results to the network."],
        },
        {
            "domain_id": "mirofish-content-simulation",
            "domain_name": "MiroFish Content Simulation",
            "domain_family": "simulator_heavy",
            "goal": "Use MiroFish-style simulated audiences and multi-RLM judge batches to rank content ideas, titles, angles, and drafts.",
            "benchmark_family": "mirofish_content_simulation",
            "mission_control_flow": "content candidates -> simulated audience batches -> multi-RLM judge aggregation -> best option with weak-row diagnosis",
            "invocation_triggers": [
                "content idea selection",
                "title or hook ranking",
                "draft comparison",
                "angle testing",
            ],
            "simulator_config": {
                "name": "mirofish-content-arena",
                "mode": "persona_batch_multi_rlm_judging",
                "agent_batch_size": 24,
                "persona_segments": [
                    "founder-builders",
                    "technical-operators",
                    "creator-economy-readers",
                    "skeptical-experts",
                ],
                "rlm_judges": [
                    "spark-local-judge",
                    "frontier-reasoning-judge",
                    "fast-taste-judge",
                ],
                "aggregation_rule": "rank by median predicted save/share/reply intent, then inspect weak segments",
            },
            "scoring_dimensions": [
                "predicted_save_intent",
                "predicted_share_intent",
                "reply_likelihood",
                "audience_specificity",
                "weak_segment_regression",
            ],
            "useful_to_spark": [
                "choose the strongest content idea or title before drafting",
                "compare many RLM judgments instead of trusting one model's taste",
                "diagnose which simulated audience segment rejects a content option",
            ],
            "mutation_axes": [
                {"name": "simulation_lens", "values": ["weak-row-first", "aggregate-first"]},
                {"name": "judge_ensemble", "values": ["multi-rlm-panel", "single-model-taste"]},
            ],
            "benchmark_cases": [
                {
                    "case_id": "title-ranking",
                    "case_kind": "content_simulation",
                    "prompt": "Rank five post titles for expected saves, shares, and replies across simulated audience segments.",
                },
                {
                    "case_id": "angle-selection",
                    "case_kind": "content_simulation",
                    "prompt": "Choose the strongest angle from several content ideas and explain weak segment resistance.",
                },
                {
                    "case_id": "trap-single-judge-hype",
                    "case_kind": "trap",
                    "prompt": "Reject a viral claim based only on one RLM judge or one aggregate score.",
                    "trap": True,
                },
            ],
            "known_limits": [
                "Simulator evidence is not real-world distribution validation.",
                "RLM judge ensembles need calibration against actual content outcomes.",
            ],
        },
        {
            "domain_id": "spark-doctor-adversarial",
            "domain_name": "Spark Doctor Adversarial",
            "domain_family": "adversarial_security",
            "goal": "Improve Spark doctor checks for fake evidence, unsafe promotion, and repair tracking.",
            "benchmark_family": "doctor_security_regression",
            "mission_control_flow": "blocked run -> doctor diagnosis -> repair step -> re-smoke proof",
            "useful_to_spark": [
                "detect fake creator-run evidence",
                "produce safer doctor repair plans for blocked systems",
            ],
            "mutation_axes": [
                {"name": "threat_model", "values": ["fake-evidence", "prompt-injection"]},
                {"name": "repair_style", "values": ["specific-blocker", "generic-advice"]},
            ],
            "benchmark_cases": [
                {
                    "case_id": "fake-report-detection",
                    "case_kind": "adversarial",
                    "prompt": "Flag a report whose saved score does not match provenance.",
                },
                {
                    "case_id": "repair-plan-specificity",
                    "case_kind": "doctor",
                    "prompt": "Generate repair steps tied to exact failed checks.",
                },
                {
                    "case_id": "trap-network-absorption",
                    "case_kind": "trap",
                    "prompt": "Reject network absorption from candidate-review evidence.",
                    "trap": True,
                },
            ],
            "unsafe_claims": ["Treat doctor pass as publication approval."],
        },
        {
            "domain_id": "startup-yc-operator",
            "domain_name": "Startup YC Operator",
            "domain_family": "startup_founder_advice",
            "goal": "Improve Spark as a startup and business advice operator with bounded YC-style evidence.",
            "benchmark_family": "startup_yc_operator",
            "mission_control_flow": "founder question -> diagnosis -> advice packet -> follow-up benchmark",
            "useful_to_spark": [
                "give sharper startup advice",
                "separate local founder guidance from broad network mastery",
            ],
            "mutation_axes": [
                {"name": "advice_frame", "values": ["demand-reality", "generic-encouragement"]},
                {"name": "evidence_probe", "values": ["specific-behavior", "vanity-metric"]},
            ],
            "benchmark_cases": [
                {
                    "case_id": "customer-pain-diagnosis",
                    "case_kind": "startup_advice",
                    "prompt": "Diagnose whether a founder has urgent customer pain.",
                },
                {
                    "case_id": "narrow-wedge",
                    "case_kind": "startup_advice",
                    "prompt": "Suggest the narrowest useful wedge for a broad product idea.",
                },
                {
                    "case_id": "trap-fake-traction",
                    "case_kind": "trap",
                    "prompt": "Reject a traction claim backed only by vanity metrics.",
                    "trap": True,
                },
            ],
            "known_limits": ["Not a network_absorbable Startup YC mastery claim."],
        },
    ]


def test_generator_acceptance_flow_creates_swarm_ready_run_in_clean_workspace(
    tmp_path: Path,
) -> None:
    generated = generate_creator_system_from_brief(tmp_path, _brief())

    assert generated.run_dir.is_dir()
    assert generated.hook_smoke["verdict"] == "pass"
    assert generated.autoloop_simulation["kept_rounds"] == 1
    assert generated.autoloop_simulation["reverted_rounds"] == 1
    assert generated.smoke["verdict"] == "ready_for_swarm_packet"
    assert generated.smoke["evidence_tier"] == "candidate_review"
    assert generated.recompute_smoke["verdict"] == "ready_for_swarm_packet"
    assert generated.recompute_smoke["blocking_checks"] == []

    expected_paths = [
        "domain-chip/chip.manifest.json",
        "domain-chip/doctrine.md",
        "domain-chip/scoring_hooks.json",
        "benchmark/manifest.json",
        "benchmark/cases.jsonl",
        "specialization-path/path.manifest.json",
        "autoloop/policy.json",
        "reports/baseline.json",
        "reports/candidate.json",
        "reports/absorption_summary.json",
        "swarm/contribution_packet.json",
    ]
    for relative_path in expected_paths:
        assert (generated.run_dir / relative_path).exists()


@pytest.mark.parametrize("brief", _multi_domain_briefs(), ids=lambda brief: brief["domain_id"])
def test_generator_acceptance_covers_multiple_spark_useful_domain_families(
    tmp_path: Path, brief: dict[str, object]
) -> None:
    generated = generate_creator_system_from_brief(
        tmp_path / str(brief["domain_id"]),
        brief,
    )

    assert generated.smoke["verdict"] == "ready_for_swarm_packet"
    assert generated.smoke["evidence_tier"] == "candidate_review"
    assert generated.recompute_smoke["blocking_checks"] == []

    chip_manifest = json.loads(
        (generated.run_dir / "domain-chip" / "chip.manifest.json").read_text(
            encoding="utf-8"
        )
    )
    benchmark_manifest = json.loads(
        (generated.run_dir / "benchmark" / "manifest.json").read_text(
            encoding="utf-8"
        )
    )
    packet = json.loads(
        (generated.run_dir / "swarm" / "contribution_packet.json").read_text(
            encoding="utf-8"
        )
    )

    assert chip_manifest["domain_family"] == brief["domain_family"]
    assert chip_manifest["mission_control_flow"] == brief["mission_control_flow"]
    assert benchmark_manifest["benchmark_family"] == brief["benchmark_family"]
    assert packet["evidence"]["tier"] == "candidate_review"
    assert packet["governance"]["network_publication_allowed"] is False
    assert brief["domain_family"] in packet["contribution"]["summary"]

    if brief["domain_id"] == "mirofish-content-simulation":
        simulator_result = packet["evidence"]["simulator_or_arena_result"]
        assert chip_manifest["invocation_triggers"] == brief["invocation_triggers"]
        assert chip_manifest["simulator_config"]["agent_batch_size"] == 24
        assert benchmark_manifest["simulator_config"]["mode"] == (
            "persona_batch_multi_rlm_judging"
        )
        assert "frontier-reasoning-judge" in simulator_result["rlm_judges"]
        assert simulator_result["claim_boundary"] == (
            "candidate_review local simulator protocol only"
        )


def test_creator_run_recompute_blocks_stale_saved_evidence(tmp_path: Path) -> None:
    generated = generate_creator_system_from_brief(tmp_path, _brief())
    candidate_path = generated.run_dir / "reports" / "candidate.json"
    candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
    candidate["mean_score"] = candidate["mean_score"] + 0.1
    candidate_path.write_text(json.dumps(candidate, indent=2) + "\n", encoding="utf-8")

    saved_only = validate_creator_run(generated.run_dir)
    recomputed = validate_creator_run(generated.run_dir, recompute=True)

    assert saved_only.verdict == "ready_for_swarm_packet"
    assert recomputed.verdict == "blocked"
    assert any(
        check.name == "recompute_candidate_score" and check.status == "fail"
        for check in recomputed.checks
    )


def test_creator_run_doctor_recompute_requires_repair_replay(
    tmp_path: Path,
) -> None:
    generated = generate_creator_system_from_brief(tmp_path, _brief())
    fixture = json.loads(
        (DOCTOR_FIXTURE_DIR / "stale_candidate_report_score.json").read_text(
            encoding="utf-8"
        )
    )
    candidate_path = generated.run_dir / fixture["path"]
    original_candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
    stale_candidate = dict(original_candidate)
    for operation in fixture["operations"]:
        stale_candidate[operation["field"]] += operation["delta"]
    candidate_path.write_text(
        json.dumps(stale_candidate, indent=2) + "\n", encoding="utf-8"
    )

    diagnosis = diagnose_creator_run(generated.run_dir, recompute=True)

    assert diagnosis["verdict"] == "blocked"
    assert diagnosis["evidence_mode"] == "recomputed"
    assert fixture["expected_blocking_checks"][0] in diagnosis["smoke"]["blocking_checks"]
    assert diagnosis["repair_replay"]["required"] is True
    assert diagnosis["repair_replay"]["satisfied"] is False
    assert any(
        step["area"] == "recompute_provenance"
        and fixture["expected_blocking_checks"][0] in step["related_checks"]
        for step in diagnosis["repair_steps"]
    )
    assert diagnosis["quarantine"][0]["reason"] == "saved_evidence_not_replayable"

    candidate_path.write_text(
        json.dumps(original_candidate, indent=2) + "\n", encoding="utf-8"
    )
    repaired = diagnose_creator_run(generated.run_dir, recompute=True)

    assert repaired["verdict"] == "ready_for_swarm_packet"
    assert repaired["repair_replay"]["fresh_evidence"] is True
    assert repaired["repair_replay"]["satisfied"] is True


def test_artifact_quality_recompute_blocks_stale_saved_evidence(tmp_path: Path) -> None:
    generated = generate_creator_system_from_brief(tmp_path, _multi_domain_briefs()[0])
    _install_artifact_quality_benchmark(generated.run_dir)
    benchmark_result = run_artifact_quality_benchmark(generated.run_dir)
    _align_swarm_packet_with_artifact_quality_reports(generated.run_dir, benchmark_result)

    saved_only = validate_creator_run(generated.run_dir)
    recomputed = validate_creator_run(generated.run_dir, recompute=True)
    assert saved_only.verdict == "ready_for_swarm_packet"
    assert recomputed.verdict == "ready_for_swarm_packet"

    candidate_path = generated.run_dir / "reports" / "candidate.json"
    candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
    candidate["mean_score"] = candidate["mean_score"] + 0.1
    candidate_path.write_text(json.dumps(candidate, indent=2) + "\n", encoding="utf-8")

    stale_saved_only = validate_creator_run(generated.run_dir)
    stale_recomputed = validate_creator_run(generated.run_dir, recompute=True)

    assert stale_saved_only.verdict == "ready_for_swarm_packet"
    assert stale_recomputed.verdict == "blocked"
    assert any(
        check.name == "recompute_candidate_score" and check.status == "fail"
        for check in stale_recomputed.checks
    )


def test_cli_creator_run_smoke_recompute_accepts_generated_workspace(
    tmp_path: Path,
) -> None:
    generated = generate_creator_system_from_brief(tmp_path, _brief())
    env = {**os.environ, "PYTHONPATH": str(Path.cwd() / "src")}

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "chip_labs.cli",
            "creator-run-smoke",
            str(generated.run_dir),
            "--recompute",
            "--fail-on-blocked",
        ],
        cwd=Path.cwd(),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert '"ready_for_swarm_packet"' in result.stdout
    assert '"recompute_candidate_delta"' in result.stdout


def _install_artifact_quality_benchmark(run_dir: Path) -> None:
    fixture_dir = Path("docs/creator_system/examples/artifact-quality")
    artifact_dir = run_dir / "benchmark" / "artifacts"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    for fixture_name in (
        "good_design_pr.md",
        "weak_design_pr.md",
        "polished_unproven_trap.md",
    ):
        (artifact_dir / fixture_name).write_text(
            (fixture_dir / fixture_name).read_text(encoding="utf-8"),
            encoding="utf-8",
        )
    (run_dir / MANIFEST_PATH).write_text(
        json.dumps(
            {
                "schema_version": "artifact_quality.benchmark_manifest.v1",
                "baseline_artifact": "benchmark/artifacts/weak_design_pr.md",
                "candidate_artifact": "benchmark/artifacts/good_design_pr.md",
                "trap_artifacts": ["benchmark/artifacts/polished_unproven_trap.md"],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def _align_swarm_packet_with_artifact_quality_reports(
    run_dir: Path, benchmark_result: dict[str, object]
) -> None:
    packet_path = run_dir / "swarm" / "contribution_packet.json"
    packet = json.loads(packet_path.read_text(encoding="utf-8"))
    evidence = packet["evidence"]
    baseline = benchmark_result["baseline"]
    candidate = benchmark_result["candidate"]
    evidence["baseline_score"] = baseline["mean_score"]
    evidence["candidate_score"] = candidate["mean_score"]
    evidence["mean_delta"] = candidate["mean_delta"]
    evidence["trap_regressions"] = candidate["trap_regressions"]
    packet_path.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
