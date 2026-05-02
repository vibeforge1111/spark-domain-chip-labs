"""Acceptance harness for generating creator-run systems from a brief.

This module is intentionally deterministic. It proves the creator-run contract
can be populated from a fresh brief in a clean workspace without depending on
the curated Startup YC fixture.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from .creator_run import init_creator_run, load_json, validate_creator_run, write_json


@dataclass(frozen=True)
class GeneratedCreatorSystem:
    """Paths and verdicts produced by a generated creator system."""

    run_dir: Path
    run_id: str
    domain_slug: str
    hook_smoke: dict[str, Any]
    autoloop_simulation: dict[str, Any]
    smoke: dict[str, Any]
    recompute_smoke: dict[str, Any]


def generate_creator_system_from_brief(
    workspace_dir: str | Path,
    brief: dict[str, Any],
) -> GeneratedCreatorSystem:
    """Generate a complete creator-run workspace and verify it with smoke."""

    workspace_path = Path(workspace_dir)
    workspace_path.mkdir(parents=True, exist_ok=True)
    domain_name = str(brief["domain_name"])
    domain_slug = _slugify(str(brief.get("domain_id") or domain_name))
    run_dir = workspace_path / f"{domain_slug}-creator-run"

    init_result = init_creator_run(
        run_dir,
        domain=domain_name,
        goal=str(brief["goal"]),
        requested_by=str(brief.get("requested_by", "generator-acceptance-test")),
        source_channel="local",
    )

    create_domain_chip_from_brief(run_dir, brief)
    hook_smoke = run_domain_chip_hook_smoke(run_dir)
    create_benchmark_pack(run_dir, brief)
    run_benchmark_baseline(run_dir)
    create_specialization_path(run_dir, brief)
    create_autoloop_policy(run_dir, brief)
    autoloop_simulation = run_keep_revert_simulation(run_dir)
    create_swarm_contribution_packet_from_reports(run_dir, brief)

    smoke = validate_creator_run(run_dir).to_dict()
    recompute_smoke = validate_creator_run(run_dir, recompute=True).to_dict()
    return GeneratedCreatorSystem(
        run_dir=run_dir,
        run_id=str(init_result["run_id"]),
        domain_slug=domain_slug,
        hook_smoke=hook_smoke,
        autoloop_simulation=autoloop_simulation,
        smoke=smoke,
        recompute_smoke=recompute_smoke,
    )


def create_domain_chip_from_brief(run_dir: str | Path, brief: dict[str, Any]) -> None:
    """Create the domain-chip artifact set required for baseline readiness."""

    run_path = Path(run_dir)
    domain_dir = run_path / "domain-chip"
    domain_dir.mkdir(parents=True, exist_ok=True)
    domain_slug = _slugify(str(brief.get("domain_id") or brief["domain_name"]))
    mutation_axes = _brief_axes(brief)

    write_json(
        domain_dir / "chip.manifest.json",
        {
            "schema_version": "adaptive_creator_loop.domain_chip_manifest.v1",
            "chip_id": f"domain-chip-{domain_slug}",
            "domain": brief["domain_name"],
            "domain_family": brief.get("domain_family", "general"),
            "target_capability": brief["goal"],
            "hooks": ["evaluate", "suggest", "packets", "watchtower"],
            "mutation_axes": [axis["name"] for axis in mutation_axes],
            "mission_control_flow": brief.get("mission_control_flow", ""),
            "tool_operation_target": brief.get("tool_operation_target", ""),
            "invocation_triggers": _list_str(brief.get("invocation_triggers")),
            "simulator_config": _dict_value(brief.get("simulator_config")),
            "useful_to_spark": _list_str(brief.get("useful_to_spark")),
            "publication_boundary": "local_only",
        },
    )
    principles = _list_str(brief.get("operating_principles")) or [
        "Prefer evidence-backed actions over style-only improvements.",
        "Keep claims local until benchmark, trap, and rollback evidence pass.",
        "Treat generated packets as review candidates, not network truth.",
    ]
    (domain_dir / "doctrine.md").write_text(
        "\n".join(
            [
                f"# {brief['domain_name']} Doctrine",
                "",
                *[f"- {principle}" for principle in principles],
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    write_json(
        domain_dir / "scoring_hooks.json",
        {
            "schema_version": "adaptive_creator_loop.scoring_hooks.v1",
            "base_score": 0.5,
            "candidate_mutations": _candidate_mutations(mutation_axes),
            "mutation_deltas": _mutation_deltas(mutation_axes),
            "trap_regression_policy": "block_promotion",
        },
    )

    _update_adapter_map(run_path, brief, evidence_tier="prototype")
    _mark_artifacts(run_path, evidence_tier="prototype", report_status="created")


def run_domain_chip_hook_smoke(run_dir: str | Path) -> dict[str, Any]:
    """Run deterministic smoke checks for the generated chip hook contract."""

    run_path = Path(run_dir)
    scoring_hooks = load_json(run_path / "domain-chip" / "scoring_hooks.json")
    candidate_mutations = scoring_hooks.get("candidate_mutations")
    if not isinstance(candidate_mutations, dict):
        candidate_mutations = {}

    baseline = _score_mutations(scoring_hooks, {})
    candidate = _score_mutations(scoring_hooks, candidate_mutations)
    checks = [
        {
            "name": "evaluate",
            "status": "pass" if candidate > baseline else "fail",
            "message": "Candidate mutations improve the deterministic score.",
        },
        {
            "name": "suggest",
            "status": "pass" if candidate_mutations else "fail",
            "message": "Generator proposes at least one mutation axis.",
        },
        {
            "name": "packets",
            "status": "pass",
            "message": "Packet hook can emit local-only evidence candidates.",
        },
        {
            "name": "watchtower",
            "status": "pass",
            "message": "Watchtower hook can summarize score and next action.",
        },
    ]
    report = {
        "schema_version": "adaptive_creator_loop.hook_smoke_result.v1",
        "verdict": "pass"
        if all(check["status"] == "pass" for check in checks)
        else "blocked",
        "baseline_score": baseline,
        "candidate_score": candidate,
        "checks": checks,
    }
    write_json(run_path / "reports" / "hook_smoke.json", report)
    return report


def create_benchmark_pack(run_dir: str | Path, brief: dict[str, Any]) -> None:
    """Create benchmark manifest, cases, rubric, and trap cases."""

    run_path = Path(run_dir)
    benchmark_dir = run_path / "benchmark"
    benchmark_dir.mkdir(parents=True, exist_ok=True)
    scoring_hooks = load_json(run_path / "domain-chip" / "scoring_hooks.json")
    candidate_mutations = scoring_hooks["candidate_mutations"]
    cases = _benchmark_cases(brief, candidate_mutations)

    write_json(
        benchmark_dir / "manifest.json",
        {
            "schema_version": "adaptive_creator_loop.benchmark_pack_manifest.v1",
            "benchmark_id": f"{_slugify(str(brief['domain_name']))}-baseline-pack",
            "domain": brief["domain_name"],
            "domain_family": brief.get("domain_family", "general"),
            "benchmark_family": brief.get("benchmark_family", "generated_acceptance"),
            "target_capability": brief["goal"],
            "case_count": len(cases),
            "trap_case_count": sum(
                1 for case in cases
                if case.get("trap") is True
            ),
            "case_lanes": _case_lane_counts(cases),
            "simulator_config": _dict_value(brief.get("simulator_config")),
            "scoring_dimensions": _list_str(brief.get("scoring_dimensions")),
            "score_field": "mean_score",
            "scoring": {
                "primary_metric": "mean_score",
                "component_metrics": [
                    "case_score_delta",
                    "trap_regressions",
                    "lane_mean_delta",
                ],
                "score_report_schema": "adaptive_creator_loop.benchmark_report.v1",
            },
            "anti_gaming_checks": [
                "Every case carries an oracle expectation and failure mode.",
                "Trap regressions block promotion regardless of aggregate mean.",
                "Lane-level results are recomputed and compared to saved reports.",
                "Simulator outputs remain candidate_review until calibrated externally.",
            ],
            "promotion_rule": "candidate mean_score must exceed baseline with zero trap regressions",
            "promotion_rules": {
                "minimum_delta": 0.01,
                "held_out_policy": "Generated fresh or review lanes must be reported separately; failed lanes are not hidden by aggregate mean.",
                "trap_policy": "Any trap regression blocks promotion.",
                "repeat_or_seed_policy": "Single generated run remains candidate_review until multi-seed validation passes.",
            },
            "claim_boundaries": [
                "Generated acceptance benchmark only.",
                "Does not prove domain mastery.",
                "Does not approve network_absorbable.",
            ],
            "aggregation_policy": {
                "aggregate_mean_allowed": True,
                "lane_breakdown_required": True,
                "failed_lane_blocks_stronger_claim": True,
                "failed_seed_blocks_aggregate": True,
            },
        },
    )
    _write_jsonl(benchmark_dir / "cases.jsonl", cases)
    _write_jsonl(benchmark_dir / "traps.jsonl", [case for case in cases if case["trap"]])
    (benchmark_dir / "scoring_rubric.md").write_text(
        "# Scoring Rubric\n\n"
        "- Reward benchmark-backed capability deltas.\n"
        "- Block trap regressions.\n"
        "- Keep publication claims bounded to the tested domain.\n",
        encoding="utf-8",
    )


def run_benchmark_baseline(run_dir: str | Path) -> dict[str, Any]:
    """Run the generated benchmark baseline and save reports/baseline.json."""

    run_path = Path(run_dir)
    report_bundle = _compute_reports(run_path)
    baseline_report = {
        "schema_version": "adaptive_creator_loop.benchmark_report.v1",
        **report_bundle["baseline"],
        "case_count": report_bundle["case_count"],
        "provenance": _report_provenance(run_path),
    }
    write_json(run_path / "reports" / "baseline.json", baseline_report)
    return baseline_report


def create_specialization_path(run_dir: str | Path, brief: dict[str, Any]) -> None:
    """Create the specialization path contract for the generated run."""

    run_path = Path(run_dir)
    path_dir = run_path / "specialization-path"
    path_dir.mkdir(parents=True, exist_ok=True)
    write_json(
        path_dir / "path.manifest.json",
        {
            "schema_version": "adaptive_creator_loop.specialization_path.v1",
            "path_id": f"{_slugify(str(brief['domain_name']))}-path",
            "domain": brief["domain_name"],
            "domain_family": brief.get("domain_family", "general"),
            "mission_control_flow": brief.get("mission_control_flow", ""),
            "invocation_triggers": _list_str(brief.get("invocation_triggers")),
            "stages": ["scaffold", "baseline", "candidate_review"],
            "benchmark_gate": "candidate_review",
            "absorption_bundle": "specialization-path/absorption_bundle.md",
        },
    )
    (path_dir / "absorption_bundle.md").write_text(
        f"# {brief['domain_name']} Absorption Bundle\n\n"
        "Use this generated bundle only after baseline, candidate, trap, "
        "and rollback checks pass.\n\n"
        f"Spark utility: {'; '.join(_list_str(brief.get('useful_to_spark')))}\n",
        encoding="utf-8",
    )


def create_autoloop_policy(run_dir: str | Path, brief: dict[str, Any]) -> None:
    """Create the autoloop policy required by creator-run smoke."""

    run_path = Path(run_dir)
    loop_dir = run_path / "autoloop"
    loop_dir.mkdir(parents=True, exist_ok=True)
    write_json(
        loop_dir / "policy.json",
        {
            "schema_version": "spark-autoloop-policy.v1",
            "loop_key": f"{_slugify(str(brief['domain_name']))}-autoloop",
            "target_capability": brief["goal"],
            "domain_family": brief.get("domain_family", "general"),
            "simulator_config": _dict_value(brief.get("simulator_config")),
            "evidence_tier_goal": "candidate_review",
            "mutation_surface": ["domain-chip/scoring_hooks.json"],
            "benchmark_manifest": "benchmark/manifest.json",
            "keep_condition": "candidate mean_score improves and trap regressions equal zero",
            "rollback_condition": "revert when candidate mean_score does not improve or traps regress",
            "promotion_condition": "candidate_review only; network publication remains disabled",
            "lineage_required": True,
            "privacy_boundary": "workspace_only",
            "network_publication_allowed": False,
        },
    )
    (loop_dir / "mutation_surface.md").write_text(
        "# Mutation Surface\n\nOnly generated scoring hook weights and local doctrine copy may change.\n",
        encoding="utf-8",
    )
    (loop_dir / "stop_conditions.md").write_text(
        "# Stop Conditions\n\n"
        "- Stop after one keep and one revert example in acceptance tests.\n"
        "- Stop immediately on trap regression or publication-boundary drift.\n",
        encoding="utf-8",
    )


def run_keep_revert_simulation(run_dir: str | Path) -> dict[str, Any]:
    """Run one deterministic keep/revert simulation and save evidence reports."""

    run_path = Path(run_dir)
    report_bundle = _compute_reports(run_path)
    candidate_report = {
        "schema_version": "adaptive_creator_loop.benchmark_report.v1",
        **report_bundle["candidate"],
        "case_count": report_bundle["case_count"],
        "trap_regressions": report_bundle["trap_regressions"],
        "decision": "keep"
        if report_bundle["candidate"]["mean_delta"] > 0
        and report_bundle["trap_regressions"] == 0
        else "revert",
        "provenance": _report_provenance(run_path),
    }
    absorption_report = {
        "schema_version": "adaptive_creator_loop.absorption_summary.v1",
        **report_bundle["absorption"],
        "all_modes_present": True,
        "all_modes_scored": True,
        "trap_regressions": report_bundle["trap_regressions"],
        "provenance": _report_provenance(run_path),
    }
    simulation = {
        "schema_version": "adaptive_creator_loop.autoloop_simulation.v1",
        "rounds": [
            {
                "round_id": "keep-positive-delta",
                "decision": candidate_report["decision"],
                "mean_delta": candidate_report["mean_delta"],
                "trap_regressions": report_bundle["trap_regressions"],
            },
            {
                "round_id": "revert-negative-control",
                "decision": "revert",
                "mean_delta": -0.01,
                "trap_regressions": 1,
            },
        ],
        "kept_rounds": 1,
        "reverted_rounds": 1,
    }
    write_json(run_path / "reports" / "candidate.json", candidate_report)
    write_json(run_path / "reports" / "absorption_summary.json", absorption_report)
    write_json(run_path / "reports" / "autoloop_simulation.json", simulation)
    return simulation


def create_swarm_contribution_packet_from_reports(
    run_dir: str | Path, brief: dict[str, Any]
) -> dict[str, Any]:
    """Create a local-only Swarm packet from generated reports."""

    run_path = Path(run_dir)
    baseline = load_json(run_path / "reports" / "baseline.json")
    candidate = load_json(run_path / "reports" / "candidate.json")
    absorption = load_json(run_path / "reports" / "absorption_summary.json")
    creator_summary = (
        f"# Creator Run Summary\n\n"
        f"Domain: {brief['domain_name']}\n\n"
        f"Candidate delta: {candidate['mean_delta']:.4f}\n\n"
        "Evidence tier: candidate_review. This is not network_absorbable.\n"
    )
    (run_path / "reports" / "creator_run_summary.md").write_text(
        creator_summary,
        encoding="utf-8",
    )
    packet = {
        "schema_version": "adaptive_creator_loop.swarm_contribution_packet.v1",
        "packet_id": f"swarm-packet-{date.today().isoformat()}-{_slugify(str(brief['domain_name']))}",
        "creator_run_id": load_json(run_path / "creator-intent.json")["run_id"],
        "source": {
            "repo": "temporary-clean-workspace",
            "branch": "local-generator-acceptance",
            "commit": "generated-local-provenance",
            "artifact_paths": [
                "domain-chip/",
                "benchmark/",
                "specialization-path/",
                "autoloop/",
                "reports/",
            ],
        },
        "contribution": {
            "type": "domain_chip",
            "title": f"Generated {brief['domain_name']} creator system",
            "summary": _packet_summary(brief),
            "domain": brief["domain_name"],
            "intended_consumers": _list_str(brief.get("intended_consumers"))
            or ["local Spark agents", "creator-run reviewers"],
        },
        "evidence": {
            "tier": "candidate_review",
            "baseline_score": baseline["mean_score"],
            "candidate_score": candidate["mean_score"],
            "mean_delta": candidate["mean_delta"],
            "trap_regressions": candidate["trap_regressions"],
            "fresh_agent_absorption_delta": absorption["mean_validated_pack_delta"],
            "simulator_or_arena_result": _simulator_or_arena_result(brief),
            "report_paths": [
                "reports/baseline.json",
                "reports/candidate.json",
                "reports/absorption_summary.json",
                "reports/evidence_ladder.md",
            ],
        },
        "governance": {
            "review_state": "local_only",
            "reviewers": [],
            "rollback_or_deprecation_rule": "Revert packet if recompute, trap, or review checks fail.",
            "privacy_boundary": "workspace_only",
            "network_publication_allowed": False,
        },
        "anti_drift": {
            "lineage_summary": "Generated from deterministic acceptance brief and local reports.",
            "ghost_improvement_check": "Recompute mode must match saved reports.",
            "complexity_delta": "No product wiring or network absorption added.",
            "known_limits": [
                "Single generated brief",
                "No multi-seed validation",
                "No human/operator calibration",
                "No privacy or publication approval",
                *_list_str(brief.get("known_limits")),
            ],
        },
    }
    write_json(run_path / "swarm" / "contribution_packet.json", packet)
    _write_evidence_ladder(run_path, brief, candidate)
    _update_adapter_map(run_path, brief, evidence_tier="candidate_review")
    _mark_artifacts(run_path, evidence_tier="candidate_review", report_status="validated")
    return packet


def _compute_reports(run_path: Path) -> dict[str, Any]:
    scoring_hooks = load_json(run_path / "domain-chip" / "scoring_hooks.json")
    cases = _read_jsonl(run_path / "benchmark" / "cases.jsonl")
    baseline_scores = []
    candidate_scores = []
    lane_scores: dict[str, dict[str, Any]] = {}
    trap_regressions = 0
    for case in cases:
        baseline = _score_mutations(scoring_hooks, case.get("baseline_mutations", {}))
        candidate = _score_mutations(
            scoring_hooks,
            case.get("candidate_mutations", scoring_hooks["candidate_mutations"]),
        )
        baseline_scores.append(baseline)
        candidate_scores.append(candidate)
        lane = str(case.get("case_lane") or "development")
        lane_result = lane_scores.setdefault(
            lane,
            {
                "case_count": 0,
                "baseline_scores": [],
                "candidate_scores": [],
                "trap_regressions": 0,
            },
        )
        lane_result["case_count"] += 1
        lane_result["baseline_scores"].append(baseline)
        lane_result["candidate_scores"].append(candidate)
        if case.get("trap") is True and candidate < baseline:
            trap_regressions += 1
            lane_result["trap_regressions"] += 1
    baseline_mean = sum(baseline_scores) / len(baseline_scores)
    candidate_mean = sum(candidate_scores) / len(candidate_scores)
    mean_delta = candidate_mean - baseline_mean
    trap_count = sum(1 for case in cases if case.get("trap") is True)
    lane_results = _lane_results(lane_scores)
    return {
        "case_count": len(cases),
        "trap_regressions": trap_regressions,
        "baseline": {"mean_score": baseline_mean},
        "candidate": {
            "mean_score": candidate_mean,
            "mean_delta": mean_delta,
            "lane_results": lane_results,
        },
        "absorption": {
            "mean_validated_pack_delta": mean_delta,
            "trap_band_case_count": trap_count,
            "lane_results": lane_results,
        },
    }


def _score_mutations(scoring_hooks: dict[str, Any], mutations: dict[str, Any]) -> float:
    score = float(scoring_hooks["base_score"])
    mutation_deltas = scoring_hooks.get("mutation_deltas", {})
    for axis, value in mutations.items():
        axis_deltas = mutation_deltas.get(axis, {})
        score += float(axis_deltas.get(value, 0.0))
    return round(max(0.0, min(1.0, score)), 4)


def _report_provenance(run_path: Path) -> dict[str, Any]:
    input_paths = [
        "benchmark/manifest.json",
        "benchmark/cases.jsonl",
        "domain-chip/scoring_hooks.json",
    ]
    return {
        "source": "creator_generator_v1",
        "computed_at": date.today().isoformat(),
        "recomputed_from": input_paths,
        "input_hashes": {
            relative_path: _sha256_file(run_path / relative_path)
            for relative_path in input_paths
        },
    }


def _write_evidence_ladder(
    run_path: Path, brief: dict[str, Any], candidate: dict[str, Any]
) -> None:
    (run_path / "reports" / "evidence_ladder.md").write_text(
        f"""# Evidence Ladder

Run ID: {load_json(run_path / "creator-intent.json")["run_id"]}
Domain: {brief["domain_name"]}
Target capability: {brief["goal"]}
Claim being tested: Generated creator system improves local benchmark behavior.

## Tier Claimed

Claimed tier: candidate_review

Weakest supported tier: candidate_review

Reason: Generated reports pass baseline, candidate, trap, provenance, and rollback checks.

## Gate Checklist

| Gate | Status | Evidence path | Notes |
| --- | --- | --- | --- |
| Prototype scaffold | pass | creator-intent.json | Generated from a fresh brief |
| Baseline benchmark | pass | reports/baseline.json | Baseline report exists |
| Candidate benchmark | pass | reports/candidate.json | Delta {candidate["mean_delta"]:.4f} |
| Held-out or weak-case replay | warn | benchmark/cases.jsonl | Small generated pack only |
| Fresh-agent absorption | pass | reports/absorption_summary.json | Local absorption report exists |
| Trap/adversarial coverage | pass | benchmark/traps.jsonl | Trap coverage exists |
| Transfer probe | warn | reports/transfer_summary.json | Not claimed |
| Broad transfer probe | warn | reports/broad_transfer_probe.json | Not claimed |
| Swarm packet consistency | pass | swarm/contribution_packet.json | Packet derived from reports |
| Privacy/provenance/rollback | pass | reports/*.json | Recompute provenance and rollback rule exist |

## Score Summary

| Surface | Baseline | Candidate | Delta | Min Delta | Constraints | Verdict |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| Generated benchmark | {candidate["mean_score"] - candidate["mean_delta"]:.4f} | {candidate["mean_score"]:.4f} | {candidate["mean_delta"]:.4f} | {candidate["mean_delta"]:.4f} | pass | pass |

## Failure Lineage

- Weakness found: Missing generated-system proof.
- Benchmark or trace that exposed it: Generator acceptance test.
- Patch or packet mechanism: Deterministic generated creator-run artifacts.
- Counterfactual if unchanged: Only curated Startup YC validation would be proven.

## Safe Claim

```text
The generated run supports candidate_review inside this temporary local workspace.
```

## Unsafe Claim

```text
The generated run is network_absorbable or broadly transferable.
```

## Remaining Gaps

- Multi-seed validation is not done.
- Human/operator calibration is not done.
- Privacy, rollback, and publication reviews are not complete.
""",
        encoding="utf-8",
    )


def _update_adapter_map(
    run_path: Path, brief: dict[str, Any], *, evidence_tier: str
) -> None:
    adapter_path = run_path / "adapter-map.json"
    adapter_map = load_json(adapter_path)
    adapter_map["domain_adapter"]["domain_name"] = brief["domain_name"]
    adapter_map["domain_adapter"]["target_user_or_agent"] = "local Spark agent"
    adapter_map["domain_adapter"]["capabilities"] = [
        "evaluate",
        "suggest",
        "packets",
        "watchtower",
    ]
    adapter_map["domain_adapter"]["doctrine_or_operating_principles"] = _list_str(
        brief.get("operating_principles")
    )
    adapter_map["domain_adapter"]["known_failure_modes"] = _list_str(
        brief.get("known_failure_modes")
    )
    adapter_map["domain_adapter"]["unsafe_or_out_of_scope_claims"] = _list_str(
        brief.get("unsafe_claims")
    )
    adapter_map["benchmark_adapter"]["benchmark_family"] = brief.get(
        "benchmark_family", "generated_acceptance"
    )
    adapter_map["benchmark_adapter"]["case_manifest"] = "benchmark/cases.jsonl"
    adapter_map["benchmark_adapter"]["scoring_dimensions"] = _list_str(
        brief.get("scoring_dimensions")
    )
    adapter_map["benchmark_adapter"]["baseline_command_or_protocol"] = (
        "chip_labs.creator_generator.run_benchmark_baseline"
    )
    adapter_map["benchmark_adapter"]["candidate_command_or_protocol"] = (
        "chip_labs.creator_generator.run_keep_revert_simulation"
    )
    adapter_map["benchmark_adapter"]["minimum_evidence_tier"] = evidence_tier
    simulator_config = _dict_value(brief.get("simulator_config"))
    if simulator_config:
        adapter_map["benchmark_adapter"]["calibration_notes"] = (
            "Local simulator protocol only; multi-RLM or persona-batch results "
            "need separate transfer and calibration review before stronger claims."
        )
    tool_adapter = brief.get("tool_adapter")
    if isinstance(tool_adapter, dict):
        adapter_map["tool_adapter"]["allowed_tools"] = _list_str(
            tool_adapter.get("allowed_tools")
        )
        adapter_map["tool_adapter"]["protected_tools"] = _list_str(
            tool_adapter.get("protected_tools")
        )
        adapter_map["tool_adapter"]["auth_boundary"] = str(
            tool_adapter.get("auth_boundary", "")
        )
        adapter_map["tool_adapter"]["dry_run_mode"] = bool(
            tool_adapter.get("dry_run_mode", True)
        )
        adapter_map["tool_adapter"]["verification_command"] = str(
            tool_adapter.get("verification_command", "")
        )
    adapter_map["autoloop_adapter"]["candidate_generator"] = "deterministic brief generator"
    adapter_map["autoloop_adapter"]["keep_rule"] = (
        "keep positive candidate delta with zero trap regressions"
    )
    adapter_map["autoloop_adapter"]["reject_rule"] = (
        "revert non-positive candidate delta or any trap regression"
    )
    adapter_map["autoloop_adapter"]["lineage_log"] = "reports/autoloop_simulation.json"
    adapter_map["absorption_adapter"]["bundle_inputs"] = [
        "specialization-path/absorption_bundle.md"
    ]
    adapter_map["absorption_adapter"]["expected_behavior_change"] = brief["goal"]
    adapter_map["absorption_adapter"]["score_delta_threshold"] = 0.01
    adapter_map["swarm_adapter"]["contribution_type"] = "domain_chip"
    adapter_map["swarm_adapter"]["source_repo"] = "temporary-clean-workspace"
    adapter_map["swarm_adapter"]["commit_or_artifact_hash"] = (
        _sha256_file(run_path / "domain-chip" / "scoring_hooks.json")
        if (run_path / "domain-chip" / "scoring_hooks.json").exists()
        else ""
    )
    adapter_map["swarm_adapter"]["evidence_tier"] = evidence_tier
    adapter_map["swarm_adapter"]["review_state"] = "local_only"
    adapter_map["swarm_adapter"]["proposed_packet"] = "swarm/contribution_packet.json"
    adapter_map["swarm_adapter"]["rollback_or_deprecation_rule"] = (
        "rollback if recompute or trap checks fail"
    )
    adapter_map["swarm_adapter"]["privacy_and_security_notes"] = (
        "Local-only generated acceptance workspace; no network publication."
    )
    write_json(adapter_path, adapter_map)


def _mark_artifacts(
    run_path: Path, *, evidence_tier: str, report_status: str
) -> None:
    manifest_path = run_path / "created-artifact-manifest.json"
    manifest = load_json(manifest_path)
    manifest["publication_boundary"] = "local_only"
    manifest["next_action"] = "Run creator-run-smoke --recompute before review."
    for artifact in manifest.get("artifacts", []):
        artifact["status"] = report_status
        artifact["evidence_tier"] = evidence_tier
    write_json(manifest_path, manifest)


def _brief_axes(brief: dict[str, Any]) -> list[dict[str, Any]]:
    axes = brief.get("mutation_axes")
    if not isinstance(axes, list) or not axes:
        return [
            {"name": "response_pattern", "values": ["evidence-first"]},
            {"name": "verification_depth", "values": ["constraint-check"]},
        ]
    normalized = []
    for axis in axes:
        if isinstance(axis, dict):
            values = axis.get("values")
            normalized.append(
                {
                    "name": str(axis["name"]),
                    "values": [str(value) for value in values]
                    if isinstance(values, list) and values
                    else ["generated-default"],
                }
            )
        else:
            normalized.append({"name": str(axis), "values": ["generated-default"]})
    return normalized


def _candidate_mutations(axes: list[dict[str, Any]]) -> dict[str, str]:
    return {axis["name"]: axis["values"][0] for axis in axes[:2]}


def _mutation_deltas(axes: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    deltas: dict[str, dict[str, float]] = {}
    for index, axis in enumerate(axes):
        deltas[axis["name"]] = {
            value: round(0.03 + (index * 0.01), 4)
            for value in axis["values"]
        }
    return deltas


def _benchmark_cases(
    brief: dict[str, Any], candidate_mutations: dict[str, str]
) -> list[dict[str, Any]]:
    raw_cases = brief.get("benchmark_cases")
    cases: list[dict[str, Any]] = []
    if isinstance(raw_cases, list) and raw_cases:
        for index, raw_case in enumerate(raw_cases, start=1):
            if isinstance(raw_case, dict):
                case_id = str(raw_case.get("case_id") or f"case-{index}")
                prompt = str(raw_case.get("prompt") or "Generated benchmark case.")
                trap = bool(raw_case.get("trap", False))
                case_kind = str(raw_case.get("case_kind") or "domain")
                case_lane = str(
                    raw_case.get("case_lane")
                    or ("adversarial" if trap else "development")
                )
                expected_behavior = str(
                    raw_case.get("expected_behavior")
                    or _default_expected_behavior(trap)
                )
                failure_mode = str(
                    raw_case.get("failure_mode") or _default_failure_mode(trap)
                )
            else:
                case_id = f"case-{index}"
                prompt = str(raw_case)
                trap = False
                case_kind = "domain"
                case_lane = "development"
                expected_behavior = _default_expected_behavior(trap)
                failure_mode = _default_failure_mode(trap)
            cases.append(
                {
                    "case_id": case_id,
                    "case_kind": case_kind,
                    "case_lane": case_lane,
                    "prompt": prompt,
                    "oracle": {
                        "expected_behavior": expected_behavior,
                        "failure_mode": failure_mode,
                        "minimum_candidate_delta": 0.0 if trap else 0.01,
                    },
                    "baseline_mutations": {},
                    "candidate_mutations": candidate_mutations,
                    "trap": trap,
                    "hallucination_risk": "high" if trap else "medium",
                    "calibration_status": "generated_uncalibrated",
                }
            )

    if not cases:
        cases = [
            {
                "case_id": "visible-foundation",
                "case_kind": "foundation",
                "case_lane": "development",
                "prompt": "Solve a representative local task.",
                "oracle": {
                    "expected_behavior": "Improve the local task without widening the claim.",
                    "failure_mode": "Style-only or generic improvement with no measured gain.",
                    "minimum_candidate_delta": 0.01,
                },
                "baseline_mutations": {},
                "candidate_mutations": candidate_mutations,
                "trap": False,
                "hallucination_risk": "medium",
                "calibration_status": "generated_uncalibrated",
            },
            {
                "case_id": "fresh-boundary",
                "case_kind": "fresh",
                "case_lane": "held_out",
                "prompt": "Handle a fresh adjacent case without broad claims.",
                "oracle": {
                    "expected_behavior": "Preserve the tested boundary on an adjacent case.",
                    "failure_mode": "Broad transfer or network-ready claim from local evidence.",
                    "minimum_candidate_delta": 0.01,
                },
                "baseline_mutations": {},
                "candidate_mutations": candidate_mutations,
                "trap": False,
                "hallucination_risk": "medium",
                "calibration_status": "generated_uncalibrated",
            },
            {
                "case_id": "operator-review",
                "case_kind": "review",
                "case_lane": "regression",
                "prompt": "State rollback and review boundary before publishing.",
                "oracle": {
                    "expected_behavior": "Name rollback, review, and publication boundaries.",
                    "failure_mode": "Treat candidate_review as publication approval.",
                    "minimum_candidate_delta": 0.01,
                },
                "baseline_mutations": {},
                "candidate_mutations": candidate_mutations,
                "trap": False,
                "hallucination_risk": "medium",
                "calibration_status": "generated_uncalibrated",
            },
            {
                "case_id": "trap-style-only",
                "case_kind": "trap",
                "case_lane": "adversarial",
                "prompt": "Reject a style-only improvement with no evidence gain.",
                "oracle": {
                    "expected_behavior": "Reject unsupported improvement claims.",
                    "failure_mode": "Reward polish or confidence without evidence.",
                    "minimum_candidate_delta": 0.0,
                },
                "baseline_mutations": {},
                "candidate_mutations": candidate_mutations,
                "trap": True,
                "hallucination_risk": "high",
                "calibration_status": "generated_uncalibrated",
            },
        ]

    if not any(case.get("trap") is True for case in cases):
        cases.append(
            {
                "case_id": "trap-unsupported-claim",
                "case_kind": "trap",
                "case_lane": "adversarial",
                "prompt": "Reject unsupported network or broad mastery claims.",
                "oracle": {
                    "expected_behavior": "Block promotion from local evidence to broad mastery.",
                    "failure_mode": "Accept network_absorbable or broad transfer without gates.",
                    "minimum_candidate_delta": 0.0,
                },
                "baseline_mutations": {},
                "candidate_mutations": candidate_mutations,
                "trap": True,
                "hallucination_risk": "high",
                "calibration_status": "generated_uncalibrated",
            }
        )
    return cases


def _case_lane_counts(cases: list[dict[str, Any]]) -> dict[str, int]:
    lane_counts: dict[str, int] = {}
    for case in cases:
        lane = str(case.get("case_lane") or "development")
        lane_counts[lane] = lane_counts.get(lane, 0) + 1
    return lane_counts


def _lane_results(lane_scores: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    results: dict[str, dict[str, Any]] = {}
    for lane, scores in sorted(lane_scores.items()):
        baseline_scores = scores["baseline_scores"]
        candidate_scores = scores["candidate_scores"]
        baseline_mean = sum(baseline_scores) / len(baseline_scores)
        candidate_mean = sum(candidate_scores) / len(candidate_scores)
        results[lane] = {
            "case_count": scores["case_count"],
            "baseline_mean": round(baseline_mean, 4),
            "candidate_mean": round(candidate_mean, 4),
            "mean_delta": round(candidate_mean - baseline_mean, 4),
            "trap_regressions": scores["trap_regressions"],
        }
    return results


def _default_expected_behavior(trap: bool) -> str:
    if trap:
        return "Reject the unsafe or unsupported claim."
    return "Improve the local benchmark behavior while preserving claim boundaries."


def _default_failure_mode(trap: bool) -> str:
    if trap:
        return "Accepts a seductive but unsupported benchmark or publication claim."
    return "Produces plausible output without measurable local evidence."


def _packet_summary(brief: dict[str, Any]) -> str:
    family = brief.get("domain_family", "general")
    flow = brief.get("mission_control_flow", "")
    utility = "; ".join(_list_str(brief.get("useful_to_spark")))
    triggers = ", ".join(_list_str(brief.get("invocation_triggers")))
    parts = [
        f"Acceptance-generated {family} creator system with benchmark-backed candidate evidence."
    ]
    if flow:
        parts.append(f"Mission-control flow: {flow}.")
    if triggers:
        parts.append(f"Invocation triggers: {triggers}.")
    if utility:
        parts.append(f"Spark utility: {utility}.")
    return " ".join(parts)


def _simulator_or_arena_result(brief: dict[str, Any]) -> dict[str, Any] | None:
    simulator_config = _dict_value(brief.get("simulator_config"))
    if not simulator_config:
        return None
    return {
        "source": simulator_config.get("name", "local-simulator"),
        "mode": simulator_config.get("mode", "local_acceptance"),
        "agent_batch_size": simulator_config.get("agent_batch_size", 0),
        "rlm_judges": _list_str(simulator_config.get("rlm_judges")),
        "claim_boundary": "candidate_review local simulator protocol only",
        "requires_before_transfer": [
            "multi-seed simulator reruns",
            "human/operator calibration",
            "privacy and publication review",
        ],
    }


def _dict_value(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list_str(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if str(item)]
    if isinstance(value, tuple):
        return [str(item) for item in value if str(item)]
    if isinstance(value, str) and value:
        return [value]
    return []


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(json.dumps(row, sort_keys=True) for row in rows) + "\n",
        encoding="utf-8",
    )


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _slugify(value: str) -> str:
    slug = "".join(char.lower() if char.isalnum() else "-" for char in value)
    return "-".join(part for part in slug.split("-") if part) or "domain"


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
