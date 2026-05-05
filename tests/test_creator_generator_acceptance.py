from __future__ import annotations

import json
import os
import hashlib
import subprocess
import sys
from pathlib import Path

import pytest

from chip_labs.artifact_quality import MANIFEST_PATH, run_artifact_quality_benchmark
from chip_labs.creator_generator import (
    generate_creator_system_from_brief,
    run_multi_seed_generator_validation,
    validate_multi_seed_generator_summary,
)
from chip_labs.creator_mission_adapter import build_creator_mission_status
from chip_labs.creator_run import diagnose_creator_run, validate_creator_run


DOCTOR_FIXTURE_DIR = Path("docs/creator_system/examples/doctor-security")
CREATOR_MISSION_SCHEMA = Path(
    "docs/creator_system/schemas/creator-mission-status.schema.json"
)
GENERATED_MULTI_SEED_SUMMARY_SCHEMA = Path(
    "docs/creator_system/schemas/generated-multi-seed-summary.schema.json"
)
GENERATED_MULTI_SEED_SUMMARY_CHECK_SCHEMA = Path(
    "docs/creator_system/schemas/generated-multi-seed-summary-check.schema.json"
)
GENERATED_MULTI_DOMAIN_BRIEFS = Path(
    "docs/creator_system/examples/generated-multi-domain-briefs.json"
)
DOMAIN_CHIP_MANIFEST_SCHEMA = Path(
    "docs/creator_system/schemas/domain-chip-manifest.schema.json"
)
HOOK_SMOKE_SCHEMA = Path("docs/creator_system/schemas/hook-smoke-result.schema.json")
SPECIALIZATION_PATH_SCHEMA = Path(
    "docs/creator_system/schemas/specialization-path-manifest.schema.json"
)
AUTOLOOP_SIMULATION_SCHEMA = Path(
    "docs/creator_system/schemas/autoloop-simulation-result.schema.json"
)
BENCHMARK_REPORT_SCHEMA = Path(
    "docs/creator_system/schemas/benchmark-report.schema.json"
)
ABSORPTION_SUMMARY_SCHEMA = Path(
    "docs/creator_system/schemas/absorption-summary.schema.json"
)
SCORING_HOOKS_SCHEMA = Path("docs/creator_system/schemas/scoring-hooks.schema.json")
BENCHMARK_CASE_SCHEMA = Path("docs/creator_system/schemas/benchmark-case.schema.json")
BENCHMARK_PACK_SCHEMA = Path(
    "docs/creator_system/schemas/benchmark-pack-manifest.schema.json"
)
SWARM_PACKET_SCHEMA = Path(
    "docs/creator_system/schemas/swarm-contribution-packet.schema.json"
)
LOOP_POLICY_SCHEMA = Path("docs/creator_system/schemas/loop-policy-manifest.schema.json")
CREATOR_INTENT_SCHEMA = Path("docs/creator_system/schemas/creator-intent.schema.json")
CREATED_ARTIFACT_MANIFEST_SCHEMA = Path(
    "docs/creator_system/schemas/created-artifact-manifest.schema.json"
)


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
        {
            "domain_id": "retrieval-memory-boundary",
            "domain_name": "Retrieval Memory Boundary",
            "domain_family": "retrieval_memory",
            "goal": "Keep Spark memory recall source-aware, privacy-bounded, and resistant to stale or contradicted context.",
            "benchmark_family": "retrieval_memory_contract",
            "mission_control_flow": "prior context -> source check -> freshness check -> promotion boundary",
            "useful_to_spark": [
                "separate correct prior decisions from stale or contradicted memory",
                "block conversational residue before it becomes promoted evidence",
            ],
            "mutation_axes": [
                {"name": "recall_policy", "values": ["source-aware", "residue-trusting"]},
                {"name": "privacy_lane", "values": ["explicit-boundary", "implicit-share"]},
            ],
            "benchmark_cases": [
                {
                    "case_id": "correct-prior-decision",
                    "case_kind": "retrieval_memory",
                    "prompt": "Accept a prior decision only when source, freshness, and scope are explicit.",
                },
                {
                    "case_id": "stale-memory-block",
                    "case_kind": "retrieval_memory",
                    "prompt": "Block stale context whose newer source contradicts the old memory.",
                },
                {
                    "case_id": "trap-conversation-residue",
                    "case_kind": "trap",
                    "prompt": "Reject chat residue as evidence unless it has a reviewed source lane.",
                    "trap": True,
                },
            ],
            "known_limits": [
                "Local retrieval-memory contract only; no production memory runtime wiring.",
            ],
            "unsafe_claims": [
                "Treat private or conversational residue as network-shareable memory.",
            ],
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
    assert generated.smoke["evidence_mode"] == "saved"
    assert generated.recompute_smoke["evidence_mode"] == "recomputed"
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
        "reports/operator_review_packet.json",
        "swarm/contribution_packet.json",
    ]
    for relative_path in expected_paths:
        assert (generated.run_dir / relative_path).exists()

    for report_path in (
        "reports/baseline.json",
        "reports/candidate.json",
        "reports/absorption_summary.json",
    ):
        report = json.loads((generated.run_dir / report_path).read_text(encoding="utf-8"))
        provenance = report["provenance"]
        assert provenance["source"] == "creator_generator_v1"
        assert provenance["input_hashes"] == {
            "benchmark/manifest.json": _sha256(
                generated.run_dir / "benchmark" / "manifest.json"
            ),
            "benchmark/cases.jsonl": _sha256(
                generated.run_dir / "benchmark" / "cases.jsonl"
            ),
            "domain-chip/scoring_hooks.json": _sha256(
                generated.run_dir / "domain-chip" / "scoring_hooks.json"
            ),
        }
        assert _smoke_check_status(
            generated.recompute_smoke,
            f"report_provenance:{report_path}:input_hashes",
        ) == "pass"


def test_generated_domain_chip_contract_schemas_validate(tmp_path: Path) -> None:
    jsonschema = pytest.importorskip("jsonschema")
    generated = generate_creator_system_from_brief(tmp_path, _brief())
    chip_manifest = json.loads(
        (generated.run_dir / "domain-chip" / "chip.manifest.json").read_text(
            encoding="utf-8"
        )
    )
    startup_yc_manifest = json.loads(
        Path(
            "docs/creator_system/examples/startup-yc-creator-run/domain-chip/chip.manifest.json"
        ).read_text(encoding="utf-8")
    )
    domain_schema = json.loads(DOMAIN_CHIP_MANIFEST_SCHEMA.read_text(encoding="utf-8"))
    hook_schema = json.loads(HOOK_SMOKE_SCHEMA.read_text(encoding="utf-8"))

    jsonschema.Draft202012Validator(domain_schema).validate(chip_manifest)
    jsonschema.Draft202012Validator(domain_schema).validate(startup_yc_manifest)
    jsonschema.Draft202012Validator(hook_schema).validate(generated.hook_smoke)


def test_generated_domain_chip_contract_schemas_reject_unsafe_shapes(
    tmp_path: Path,
) -> None:
    jsonschema = pytest.importorskip("jsonschema")
    generated = generate_creator_system_from_brief(tmp_path, _brief())
    chip_manifest = json.loads(
        (generated.run_dir / "domain-chip" / "chip.manifest.json").read_text(
            encoding="utf-8"
        )
    )
    hook_smoke = dict(generated.hook_smoke)
    domain_schema = json.loads(DOMAIN_CHIP_MANIFEST_SCHEMA.read_text(encoding="utf-8"))
    hook_schema = json.loads(HOOK_SMOKE_SCHEMA.read_text(encoding="utf-8"))

    chip_manifest["publication_boundary"] = "network_absorbable"
    hook_smoke["checks"][0]["status"] = "fail"

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(domain_schema).validate(chip_manifest)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(hook_schema).validate(hook_smoke)


def test_generated_path_and_autoloop_contract_schemas_validate(
    tmp_path: Path,
) -> None:
    jsonschema = pytest.importorskip("jsonschema")
    generated = generate_creator_system_from_brief(tmp_path, _brief())
    path_manifest = json.loads(
        (generated.run_dir / "specialization-path" / "path.manifest.json").read_text(
            encoding="utf-8"
        )
    )
    startup_yc_path = json.loads(
        Path(
            "docs/creator_system/examples/startup-yc-creator-run/specialization-path/path.manifest.json"
        ).read_text(encoding="utf-8")
    )
    path_schema = json.loads(SPECIALIZATION_PATH_SCHEMA.read_text(encoding="utf-8"))
    autoloop_schema = json.loads(
        AUTOLOOP_SIMULATION_SCHEMA.read_text(encoding="utf-8")
    )

    jsonschema.Draft202012Validator(path_schema).validate(path_manifest)
    jsonschema.Draft202012Validator(path_schema).validate(startup_yc_path)
    compatibility = path_manifest["spark_swarm_compatibility"]
    assert compatibility["runtime_core"] == "spark-researcher"
    assert compatibility["collective_payload"] == (
        "SparkResearcherCollectiveSyncPayload"
    )
    assert compatibility["path_specific_logic_owner"] == "specialization-path-*"
    assert set(compatibility["forbidden_ownership"]) == {
        "identity",
        "channel_auth",
        "provider_secrets",
        "global_tool_authority",
    }
    jsonschema.Draft202012Validator(autoloop_schema).validate(
        generated.autoloop_simulation
    )


def test_generated_path_and_autoloop_contract_schemas_reject_unsafe_shapes(
    tmp_path: Path,
) -> None:
    jsonschema = pytest.importorskip("jsonschema")
    generated = generate_creator_system_from_brief(tmp_path, _brief())
    path_manifest = json.loads(
        (generated.run_dir / "specialization-path" / "path.manifest.json").read_text(
            encoding="utf-8"
        )
    )
    autoloop_simulation = dict(generated.autoloop_simulation)
    path_schema = json.loads(SPECIALIZATION_PATH_SCHEMA.read_text(encoding="utf-8"))
    autoloop_schema = json.loads(
        AUTOLOOP_SIMULATION_SCHEMA.read_text(encoding="utf-8")
    )

    path_manifest["benchmark_gate"] = "network_absorption"
    autoloop_simulation["rounds"] = [
        {**round_, "decision": "keep", "mean_delta": 0.01, "trap_regressions": 0}
        for round_ in autoloop_simulation["rounds"]
    ]
    autoloop_simulation["reverted_rounds"] = 0

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(path_schema).validate(path_manifest)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(autoloop_schema).validate(
            autoloop_simulation
        )


def test_specialization_path_schema_rejects_runtime_authority_drift(
    tmp_path: Path,
) -> None:
    jsonschema = pytest.importorskip("jsonschema")
    generated = generate_creator_system_from_brief(tmp_path, _brief())
    path_manifest = json.loads(
        (generated.run_dir / "specialization-path" / "path.manifest.json").read_text(
            encoding="utf-8"
        )
    )
    path_schema = json.loads(SPECIALIZATION_PATH_SCHEMA.read_text(encoding="utf-8"))

    path_manifest["spark_swarm_compatibility"]["runtime_core"] = "custom-runtime"

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(path_schema).validate(path_manifest)


def test_specialization_path_schema_rejects_missing_forbidden_ownership(
    tmp_path: Path,
) -> None:
    jsonschema = pytest.importorskip("jsonschema")
    generated = generate_creator_system_from_brief(tmp_path, _brief())
    path_manifest = json.loads(
        (generated.run_dir / "specialization-path" / "path.manifest.json").read_text(
            encoding="utf-8"
        )
    )
    path_schema = json.loads(SPECIALIZATION_PATH_SCHEMA.read_text(encoding="utf-8"))

    path_manifest["spark_swarm_compatibility"]["forbidden_ownership"].remove(
        "provider_secrets"
    )

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(path_schema).validate(path_manifest)


def test_generated_report_contract_schemas_validate_saved_evidence(
    tmp_path: Path,
) -> None:
    jsonschema = pytest.importorskip("jsonschema")
    generated = generate_creator_system_from_brief(tmp_path, _brief())
    report_schema = json.loads(BENCHMARK_REPORT_SCHEMA.read_text(encoding="utf-8"))
    absorption_schema = json.loads(
        ABSORPTION_SUMMARY_SCHEMA.read_text(encoding="utf-8")
    )

    for report_name in ("baseline.json", "candidate.json"):
        report = json.loads(
            (generated.run_dir / "reports" / report_name).read_text(encoding="utf-8")
        )
        jsonschema.Draft202012Validator(report_schema).validate(report)

    absorption = json.loads(
        (generated.run_dir / "reports" / "absorption_summary.json").read_text(
            encoding="utf-8"
        )
    )
    jsonschema.Draft202012Validator(absorption_schema).validate(absorption)


def test_report_contract_schemas_validate_startup_yc_source_linked_evidence() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    run_dir = Path("docs/creator_system/examples/startup-yc-creator-run")
    report_schema = json.loads(BENCHMARK_REPORT_SCHEMA.read_text(encoding="utf-8"))
    absorption_schema = json.loads(
        ABSORPTION_SUMMARY_SCHEMA.read_text(encoding="utf-8")
    )

    for report_name in ("baseline.json", "candidate.json"):
        report = json.loads((run_dir / "reports" / report_name).read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator(report_schema).validate(report)

    absorption = json.loads(
        (run_dir / "reports" / "absorption_summary.json").read_text(encoding="utf-8")
    )
    jsonschema.Draft202012Validator(absorption_schema).validate(absorption)


def test_generated_report_contract_schemas_reject_stale_or_unbounded_evidence(
    tmp_path: Path,
) -> None:
    jsonschema = pytest.importorskip("jsonschema")
    generated = generate_creator_system_from_brief(tmp_path, _brief())
    candidate = json.loads(
        (generated.run_dir / "reports" / "candidate.json").read_text(encoding="utf-8")
    )
    absorption = json.loads(
        (generated.run_dir / "reports" / "absorption_summary.json").read_text(
            encoding="utf-8"
        )
    )
    report_schema = json.loads(BENCHMARK_REPORT_SCHEMA.read_text(encoding="utf-8"))
    absorption_schema = json.loads(
        ABSORPTION_SUMMARY_SCHEMA.read_text(encoding="utf-8")
    )

    candidate["provenance"]["source"] = "unknown"
    absorption["all_modes_scored"] = False

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(report_schema).validate(candidate)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(absorption_schema).validate(absorption)


def test_generated_scoring_hooks_and_case_contract_schemas_validate(
    tmp_path: Path,
) -> None:
    jsonschema = pytest.importorskip("jsonschema")
    generated = generate_creator_system_from_brief(tmp_path, _brief())
    scoring_hooks = json.loads(
        (generated.run_dir / "domain-chip" / "scoring_hooks.json").read_text(
            encoding="utf-8"
        )
    )
    startup_yc_hooks = json.loads(
        Path(
            "docs/creator_system/examples/startup-yc-creator-run/domain-chip/scoring_hooks.json"
        ).read_text(encoding="utf-8")
    )
    hooks_schema = json.loads(SCORING_HOOKS_SCHEMA.read_text(encoding="utf-8"))
    case_schema = json.loads(BENCHMARK_CASE_SCHEMA.read_text(encoding="utf-8"))

    jsonschema.Draft202012Validator(hooks_schema).validate(scoring_hooks)
    jsonschema.Draft202012Validator(hooks_schema).validate(startup_yc_hooks)
    for line in (generated.run_dir / "benchmark" / "cases.jsonl").read_text(
        encoding="utf-8"
    ).splitlines():
        jsonschema.Draft202012Validator(case_schema).validate(json.loads(line))


def test_generated_scoring_hooks_and_case_contract_schemas_reject_unsafe_shapes(
    tmp_path: Path,
) -> None:
    jsonschema = pytest.importorskip("jsonschema")
    generated = generate_creator_system_from_brief(tmp_path, _brief())
    scoring_hooks = json.loads(
        (generated.run_dir / "domain-chip" / "scoring_hooks.json").read_text(
            encoding="utf-8"
        )
    )
    case = json.loads(
        (generated.run_dir / "benchmark" / "cases.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()[-1]
    )
    hooks_schema = json.loads(SCORING_HOOKS_SCHEMA.read_text(encoding="utf-8"))
    case_schema = json.loads(BENCHMARK_CASE_SCHEMA.read_text(encoding="utf-8"))

    scoring_hooks["trap_regression_policy"] = "allow_promotion"
    case["trap"] = True
    case["case_lane"] = "development"

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(hooks_schema).validate(scoring_hooks)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(case_schema).validate(case)


def test_benchmark_pack_contract_schema_validates_generated_and_source_manifests(
    tmp_path: Path,
) -> None:
    jsonschema = pytest.importorskip("jsonschema")
    generated = generate_creator_system_from_brief(tmp_path, _brief())
    generated_manifest = json.loads(
        (generated.run_dir / "benchmark" / "manifest.json").read_text(
            encoding="utf-8"
        )
    )
    startup_yc_manifest = json.loads(
        Path(
            "docs/creator_system/examples/startup-yc-creator-run/benchmark/manifest.json"
        ).read_text(encoding="utf-8")
    )
    schema = json.loads(BENCHMARK_PACK_SCHEMA.read_text(encoding="utf-8"))

    jsonschema.Draft202012Validator(schema).validate(generated_manifest)
    jsonschema.Draft202012Validator(schema).validate(startup_yc_manifest)


def test_benchmark_pack_contract_schema_rejects_hidden_lane_failures(
    tmp_path: Path,
) -> None:
    jsonschema = pytest.importorskip("jsonschema")
    generated = generate_creator_system_from_brief(tmp_path, _brief())
    manifest = json.loads(
        (generated.run_dir / "benchmark" / "manifest.json").read_text(
            encoding="utf-8"
        )
    )
    schema = json.loads(BENCHMARK_PACK_SCHEMA.read_text(encoding="utf-8"))

    manifest["aggregation_policy"]["failed_lane_blocks_stronger_claim"] = False

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate(manifest)


def test_swarm_packet_contract_schema_blocks_network_publication_claim(
    tmp_path: Path,
) -> None:
    jsonschema = pytest.importorskip("jsonschema")
    generated = generate_creator_system_from_brief(tmp_path, _brief())
    generated_packet = json.loads(
        (generated.run_dir / "swarm" / "contribution_packet.json").read_text(
            encoding="utf-8"
        )
    )
    startup_yc_packet = json.loads(
        Path(
            "docs/creator_system/examples/startup-yc-creator-run/swarm/contribution_packet.json"
        ).read_text(encoding="utf-8")
    )
    schema = json.loads(SWARM_PACKET_SCHEMA.read_text(encoding="utf-8"))

    jsonschema.Draft202012Validator(schema).validate(generated_packet)
    jsonschema.Draft202012Validator(schema).validate(startup_yc_packet)

    generated_packet["governance"]["network_publication_allowed"] = True

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate(generated_packet)


def test_loop_policy_contract_schema_blocks_network_publication_claim(
    tmp_path: Path,
) -> None:
    jsonschema = pytest.importorskip("jsonschema")
    generated = generate_creator_system_from_brief(tmp_path, _brief())
    generated_policy = json.loads(
        (generated.run_dir / "autoloop" / "policy.json").read_text(encoding="utf-8")
    )
    startup_yc_policy = json.loads(
        Path(
            "docs/creator_system/examples/startup-yc-creator-run/autoloop/policy.json"
        ).read_text(encoding="utf-8")
    )
    schema = json.loads(LOOP_POLICY_SCHEMA.read_text(encoding="utf-8"))

    jsonschema.Draft202012Validator(schema).validate(generated_policy)
    jsonschema.Draft202012Validator(schema).validate(startup_yc_policy)

    generated_policy["network_publication_allowed"] = True

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate(generated_policy)

    generated_policy["network_publication_allowed"] = False
    generated_policy["evidence_tier_goal"] = "magic_mastery"

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate(generated_policy)

    generated_policy["evidence_tier_goal"] = "network_absorbable"

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate(generated_policy)


def test_creator_intent_contract_schema_blocks_network_publication_claim(
    tmp_path: Path,
) -> None:
    jsonschema = pytest.importorskip("jsonschema")
    generated = generate_creator_system_from_brief(tmp_path, _brief())
    generated_intent = json.loads(
        (generated.run_dir / "creator-intent.json").read_text(encoding="utf-8")
    )
    startup_yc_intent = json.loads(
        Path(
            "docs/creator_system/examples/startup-yc-creator-run/creator-intent.json"
        ).read_text(encoding="utf-8")
    )
    schema = json.loads(CREATOR_INTENT_SCHEMA.read_text(encoding="utf-8"))

    jsonschema.Draft202012Validator(schema).validate(generated_intent)
    jsonschema.Draft202012Validator(schema).validate(startup_yc_intent)

    generated_intent["constraints"]["network_publication_allowed"] = True

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate(generated_intent)

    generated_intent["constraints"]["network_publication_allowed"] = False
    generated_intent["success_criteria"]["minimum_evidence_tier"] = "magic_mastery"

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate(generated_intent)

    generated_intent["success_criteria"]["minimum_evidence_tier"] = (
        "network_absorbable"
    )

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate(generated_intent)


def test_created_artifact_manifest_schema_blocks_publication_boundary_drift(
    tmp_path: Path,
) -> None:
    jsonschema = pytest.importorskip("jsonschema")
    generated = generate_creator_system_from_brief(tmp_path, _brief())
    generated_manifest = json.loads(
        (generated.run_dir / "created-artifact-manifest.json").read_text(
            encoding="utf-8"
        )
    )
    startup_yc_manifest = json.loads(
        Path(
            "docs/creator_system/examples/startup-yc-creator-run/created-artifact-manifest.json"
        ).read_text(encoding="utf-8")
    )
    schema = json.loads(
        CREATED_ARTIFACT_MANIFEST_SCHEMA.read_text(encoding="utf-8")
    )

    jsonschema.Draft202012Validator(schema).validate(generated_manifest)
    jsonschema.Draft202012Validator(schema).validate(startup_yc_manifest)

    generated_manifest["publication_boundary"] = "swarm_shared"
    generated_manifest["artifacts"][0]["status"] = "published"

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate(generated_manifest)

    generated_manifest["publication_boundary"] = "local_only"
    generated_manifest["artifacts"][0]["status"] = "validated"
    generated_manifest["artifacts"][0]["evidence_tier"] = "magic_mastery"

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate(generated_manifest)

    generated_manifest["artifacts"][0]["evidence_tier"] = "network_absorbable"

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate(generated_manifest)


@pytest.mark.parametrize("brief", _multi_domain_briefs(), ids=lambda brief: brief["domain_id"])
def test_generator_acceptance_covers_multiple_spark_useful_domain_families(
    tmp_path: Path, brief: dict[str, object]
) -> None:
    jsonschema = pytest.importorskip("jsonschema")
    generated = generate_creator_system_from_brief(
        tmp_path / str(brief["domain_id"]),
        brief,
    )

    assert generated.smoke["verdict"] == "ready_for_swarm_packet"
    assert generated.smoke["evidence_tier"] == "candidate_review"
    assert generated.smoke["evidence_mode"] == "saved"
    assert generated.recompute_smoke["evidence_mode"] == "recomputed"
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
    assert benchmark_manifest["target_capability"] == brief["goal"]
    assert benchmark_manifest["case_lanes"]["adversarial"] >= 1
    assert benchmark_manifest["aggregation_policy"] == {
        "aggregate_mean_allowed": True,
        "lane_breakdown_required": True,
        "failed_lane_blocks_stronger_claim": True,
        "failed_seed_blocks_aggregate": True,
    }
    assert "Every case carries an oracle expectation and failure mode." in (
        benchmark_manifest["anti_gaming_checks"]
    )
    assert packet["evidence"]["tier"] == "candidate_review"
    assert packet["governance"]["network_publication_allowed"] is False
    assert brief["domain_family"] in packet["contribution"]["summary"]
    operator_review = json.loads(
        (generated.run_dir / "reports" / "operator_review_packet.json").read_text(
            encoding="utf-8"
        )
    )
    assert operator_review["network_absorbable"] is False
    assert operator_review["gate_status"]["publication_approval"] is False
    assert "network_absorbable" in operator_review["forbidden_claims"]

    cases = [
        json.loads(line)
        for line in (generated.run_dir / "benchmark" / "cases.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
        if line.strip()
    ]
    assert all(case["case_lane"] for case in cases)
    assert all(case["oracle"]["expected_behavior"] for case in cases)
    assert all(case["oracle"]["failure_mode"] for case in cases)
    assert all(case["calibration_status"] == "generated_uncalibrated" for case in cases)
    assert any(case["trap"] is True and case["hallucination_risk"] == "high" for case in cases)

    candidate_report = json.loads(
        (generated.run_dir / "reports" / "candidate.json").read_text(encoding="utf-8")
    )
    absorption_report = json.loads(
        (generated.run_dir / "reports" / "absorption_summary.json").read_text(
            encoding="utf-8"
        )
    )
    assert "adversarial" in candidate_report["lane_results"]
    assert candidate_report["lane_results"] == absorption_report["lane_results"]
    assert _smoke_check_status(
        generated.recompute_smoke,
        "recompute_candidate_lane_results",
    ) == "pass"

    mission_status = build_creator_mission_status(
        mission_id=f"{brief['domain_id']}-generated",
        smoke=generated.recompute_smoke,
    )
    schema = json.loads(CREATOR_MISSION_SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(mission_status)
    assert mission_status["canonical"]["evidence_mode"] == "recomputed"
    assert mission_status["publication"]["network_absorbable"] is False
    assert mission_status["surface_adapters"]["builder"]["evidence_mode"] == (
        "recomputed"
    )
    assert "Evidence mode: `recomputed`." in mission_status["surface_adapters"][
        "telegram"
    ]["text"]
    assert any(
        node.get("id") == "creator_mission"
        and node.get("evidence_mode") == "recomputed"
        for node in mission_status["surface_adapters"]["canvas"]["nodes"]
    )
    kanban_cards = [
        card
        for cards in mission_status["surface_adapters"]["kanban"]["columns"].values()
        for card in cards
    ]
    assert kanban_cards[0]["evidence_mode"] == "recomputed"

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

    assert saved_only.verdict == "blocked"
    assert recomputed.verdict == "blocked"
    assert any(
        check.name == "swarm_packet_candidate_score_matches_report"
        and check.status == "fail"
        for check in saved_only.checks
    )
    assert any(
        check.name == "recompute_candidate_score" and check.status == "fail"
        for check in recomputed.checks
    )


def test_creator_run_recompute_blocks_tampered_benchmark_manifest(
    tmp_path: Path,
) -> None:
    generated = generate_creator_system_from_brief(tmp_path, _brief())
    manifest_path = generated.run_dir / "benchmark" / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["promotion_rules"]["minimum_delta"] = -1
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    recomputed = validate_creator_run(generated.run_dir, recompute=True)

    assert recomputed.verdict == "blocked"
    assert any(
        check.name.startswith("report_provenance:")
        and check.name.endswith(":input_hashes")
        and check.status == "fail"
        and "benchmark/manifest.json hash mismatch" in check.message
        for check in recomputed.checks
    )


def test_creator_run_recompute_blocks_tampered_lane_results(tmp_path: Path) -> None:
    generated = generate_creator_system_from_brief(tmp_path, _brief())
    candidate_path = generated.run_dir / "reports" / "candidate.json"
    candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
    candidate["lane_results"]["adversarial"]["trap_regressions"] = 1
    candidate_path.write_text(json.dumps(candidate, indent=2) + "\n", encoding="utf-8")

    recomputed = validate_creator_run(generated.run_dir, recompute=True)

    assert recomputed.verdict == "blocked"
    assert any(
        check.name == "recompute_candidate_lane_results" and check.status == "fail"
        for check in recomputed.checks
    )


def test_generator_multi_seed_validation_runs_full_domain_matrix(
    tmp_path: Path,
) -> None:
    jsonschema = pytest.importorskip("jsonschema")
    summary = run_multi_seed_generator_validation(
        tmp_path,
        _multi_domain_briefs(),
        seeds=(1, 2),
        variants_per_domain=3,
    )

    assert summary["schema_version"] == (
        "adaptive_creator_loop.generated_multi_seed_validation.v1"
    )
    assert summary["matrix"] == {
        "domain_count": 6,
        "variants_per_domain": 3,
        "seeds": [1, 2],
        "target_run_count": 36,
        "completed_run_count": 36,
    }
    assert summary["verdict"] == "candidate_review"
    assert summary["evidence_tier"] == "candidate_review"
    assert summary["evidence_mode"] == "recomputed"
    assert summary["network_absorbable"] is False
    assert summary["aggregate_hidden_failures"] is False
    assert summary["passed_run_count"] == 36
    assert summary["blocked_run_count"] == 0
    assert summary["failed_seed_ids"] == []
    assert len(summary["rows"]) == 36
    assert all(row["evidence_mode"] == "recomputed" for row in summary["rows"])
    assert all(row["evidence_tier"] == "candidate_review" for row in summary["rows"])
    assert all(row["network_absorbable"] is False for row in summary["rows"])
    assert {
        row["base_domain_id"] for row in summary["rows"]
    } == {
        "design-doc-pr-quality",
        "spark-tool-operation",
        "mirofish-content-simulation",
        "spark-doctor-adversarial",
        "startup-yc-operator",
        "retrieval-memory-boundary",
    }
    assert (tmp_path / "multi_seed_validation_summary.json").exists()
    summary_schema = json.loads(
        GENERATED_MULTI_SEED_SUMMARY_SCHEMA.read_text(encoding="utf-8")
    )
    jsonschema.Draft202012Validator(summary_schema).validate(summary)
    checked = validate_multi_seed_generator_summary(
        tmp_path / "multi_seed_validation_summary.json"
    )
    check_schema = json.loads(
        GENERATED_MULTI_SEED_SUMMARY_CHECK_SCHEMA.read_text(encoding="utf-8")
    )
    jsonschema.Draft202012Validator(check_schema).validate(checked)
    assert checked["verdict"] == "pass"
    assert checked["blocking_checks"] == []
    assert checked["row_count"] == 36


def test_generated_multi_domain_briefs_file_is_operator_matrix_input() -> None:
    payload = json.loads(GENERATED_MULTI_DOMAIN_BRIEFS.read_text(encoding="utf-8"))
    briefs = payload["briefs"]

    assert len(briefs) == 6
    assert {brief["domain_family"] for brief in briefs} == {
        "artifact_quality",
        "tool_operation",
        "simulator_heavy",
        "adversarial_security",
        "startup_founder_advice",
        "retrieval_memory",
    }
    assert all("network_absorbable" not in brief.get("goal", "") for brief in briefs)
    assert all(brief["mutation_axes"] for brief in briefs)
    assert all(
        any(case.get("trap") is True for case in brief["benchmark_cases"])
        for brief in briefs
    )


def test_generator_multi_seed_validation_exposes_failed_seed_rows(
    tmp_path: Path,
) -> None:
    jsonschema = pytest.importorskip("jsonschema")
    summary = run_multi_seed_generator_validation(
        tmp_path,
        [_multi_domain_briefs()[0]],
        seeds=(1, 2),
        variants_per_domain=1,
        weak_seed_ids={"design-doc-pr-quality:v1:seed2"},
    )

    assert summary["verdict"] == "blocked"
    assert summary["evidence_tier"] == "blocked"
    assert summary["aggregate_hidden_failures"] is False
    assert summary["passed_run_count"] == 1
    assert summary["blocked_run_count"] == 1
    assert summary["failed_seed_ids"] == ["design-doc-pr-quality:v1:seed2"]
    failed_row = [
        row
        for row in summary["rows"]
        if row["seed_id"] == "design-doc-pr-quality:v1:seed2"
    ][0]
    assert failed_row["verdict"] == "blocked"
    assert "recompute_candidate_lane_results" in failed_row["blocking_checks"]
    assert "Do not promote a packet when any seed row is blocked." in (
        summary["next_actions"]
    )
    summary_schema = json.loads(
        GENERATED_MULTI_SEED_SUMMARY_SCHEMA.read_text(encoding="utf-8")
    )
    jsonschema.Draft202012Validator(summary_schema).validate(summary)


def test_multi_seed_summary_validation_blocks_tampered_saved_rows(
    tmp_path: Path,
) -> None:
    run_multi_seed_generator_validation(
        tmp_path,
        [_multi_domain_briefs()[0]],
        seeds=(1, 2),
        variants_per_domain=1,
    )
    summary_path = tmp_path / "multi_seed_validation_summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    summary["rows"][0]["verdict"] = "ready_for_swarm_packet_but_fake"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    checked = validate_multi_seed_generator_summary(summary_path)
    jsonschema = pytest.importorskip("jsonschema")
    check_schema = json.loads(
        GENERATED_MULTI_SEED_SUMMARY_CHECK_SCHEMA.read_text(encoding="utf-8")
    )
    jsonschema.Draft202012Validator(check_schema).validate(checked)

    assert checked["verdict"] == "blocked"
    assert "row:design-doc-pr-quality:v1:seed1:verdict_mismatch" in (
        checked["blocking_checks"]
    )


def test_multi_seed_summary_validation_blocks_stale_underlying_run(
    tmp_path: Path,
) -> None:
    run_multi_seed_generator_validation(
        tmp_path,
        [_multi_domain_briefs()[0]],
        seeds=(1, 2),
        variants_per_domain=1,
    )
    summary_path = tmp_path / "multi_seed_validation_summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    first_run_dir = Path(summary["rows"][0]["run_dir"])
    candidate_path = first_run_dir / "reports" / "candidate.json"
    candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
    candidate["lane_results"]["adversarial"]["trap_regressions"] = 1
    candidate_path.write_text(json.dumps(candidate, indent=2) + "\n", encoding="utf-8")

    checked = validate_multi_seed_generator_summary(summary_path)
    jsonschema = pytest.importorskip("jsonschema")
    check_schema = json.loads(
        GENERATED_MULTI_SEED_SUMMARY_CHECK_SCHEMA.read_text(encoding="utf-8")
    )
    jsonschema.Draft202012Validator(check_schema).validate(checked)

    assert checked["verdict"] == "blocked"
    assert summary["rows"][0]["seed_id"] in checked["failed_seed_ids"]
    assert "row:design-doc-pr-quality:v1:seed1:verdict_mismatch" in (
        checked["blocking_checks"]
    )
    assert "summary:verdict_mismatch" in checked["blocking_checks"]


def test_cli_generated_multi_seed_summary_check_recomputes_saved_summary(
    tmp_path: Path,
) -> None:
    jsonschema = pytest.importorskip("jsonschema")
    run_multi_seed_generator_validation(
        tmp_path,
        [_multi_domain_briefs()[0]],
        seeds=(1, 2),
        variants_per_domain=1,
    )
    summary_path = tmp_path / "multi_seed_validation_summary.json"
    output_path = tmp_path / "multi_seed_validation_summary.check.json"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "chip_labs.cli",
            "generated-multi-seed-summary-check",
            "--summary",
            str(summary_path),
            "--output",
            str(output_path),
            "--fail-on-blocked",
        ],
        cwd=Path.cwd(),
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    check_schema = json.loads(
        GENERATED_MULTI_SEED_SUMMARY_CHECK_SCHEMA.read_text(encoding="utf-8")
    )
    jsonschema.Draft202012Validator(check_schema).validate(payload)
    assert payload["verdict"] == "pass"
    assert payload["row_count"] == 2
    assert payload["network_absorbable"] is False

    tampered = json.loads(summary_path.read_text(encoding="utf-8"))
    tampered["rows"][0]["network_absorbable"] = True
    summary_path.write_text(json.dumps(tampered, indent=2) + "\n", encoding="utf-8")
    blocked = subprocess.run(
        [
            sys.executable,
            "-m",
            "chip_labs.cli",
            "generated-multi-seed-summary-check",
            "--summary",
            str(summary_path),
            "--fail-on-blocked",
        ],
        cwd=Path.cwd(),
        capture_output=True,
        text=True,
        check=False,
    )

    assert blocked.returncode == 1
    assert "network_absorbable_mismatch" in blocked.stdout


def test_cli_generated_multi_seed_run_writes_summary_and_workspace(
    tmp_path: Path,
) -> None:
    jsonschema = pytest.importorskip("jsonschema")
    briefs_path = tmp_path / "briefs.json"
    workspace_dir = tmp_path / "generated-matrix"
    output_path = tmp_path / "generated-summary.json"
    briefs_path.write_text(
        json.dumps({"briefs": [_multi_domain_briefs()[0]]}, indent=2) + "\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "chip_labs.cli",
            "generated-multi-seed-run",
            "--briefs",
            str(briefs_path),
            "--workspace-dir",
            str(workspace_dir),
            "--variants-per-domain",
            "1",
            "--seeds",
            "1,2",
            "--output",
            str(output_path),
            "--fail-on-blocked",
        ],
        cwd=Path.cwd(),
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    summary = json.loads(output_path.read_text(encoding="utf-8"))
    summary_schema = json.loads(
        GENERATED_MULTI_SEED_SUMMARY_SCHEMA.read_text(encoding="utf-8")
    )
    jsonschema.Draft202012Validator(summary_schema).validate(summary)
    assert summary["verdict"] == "candidate_review"
    assert summary["matrix"]["completed_run_count"] == 2
    assert summary["network_absorbable"] is False
    assert (workspace_dir / "multi_seed_validation_summary.json").exists()

    check_result = subprocess.run(
        [
            sys.executable,
            "-m",
            "chip_labs.cli",
            "generated-multi-seed-summary-check",
            "--summary",
            str(workspace_dir / "multi_seed_validation_summary.json"),
            "--fail-on-blocked",
        ],
        cwd=Path.cwd(),
        capture_output=True,
        text=True,
        check=False,
    )
    assert check_result.returncode == 0
    assert '"verdict": "pass"' in check_result.stdout


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
    assert diagnosis["repair_calibration"]["verdict"] == "pass"
    assert diagnosis["repair_calibration"]["uncovered_smoke_checks"] == []
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

    assert stale_saved_only.verdict == "blocked"
    assert stale_recomputed.verdict == "blocked"
    assert any(
        check.name == "swarm_packet_candidate_score_matches_report"
        and check.status == "fail"
        for check in stale_saved_only.checks
    )
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
        "design_decision_record_ready.md",
        "mission_handoff_ready.md",
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
    absorption = benchmark_result["absorption"]
    evidence["baseline_score"] = baseline["mean_score"]
    evidence["candidate_score"] = candidate["mean_score"]
    evidence["mean_delta"] = candidate["mean_delta"]
    evidence["trap_regressions"] = candidate["trap_regressions"]
    evidence["fresh_agent_absorption_delta"] = absorption[
        "mean_validated_pack_delta"
    ]
    packet_path.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _smoke_check_status(smoke: dict[str, object], name: str) -> str | None:
    checks = smoke.get("checks", [])
    if not isinstance(checks, list):
        return None
    for check in checks:
        if isinstance(check, dict) and check.get("name") == name:
            return str(check.get("status"))
    return None
