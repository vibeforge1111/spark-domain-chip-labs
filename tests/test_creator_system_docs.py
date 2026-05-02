from __future__ import annotations

from pathlib import Path


README = Path("docs/creator_system/README.md")
RELEASE_NOTES = Path("docs/creator_system/CREATOR_SYSTEM_RELEASE_NOTES_2026-05-01.md")
PHASE_2_BACKLOG = Path("docs/creator_system/PHASE_2_PRODUCT_FLOW_BACKLOG.md")
PRODUCT_FLOW = Path("docs/creator_system/TELEGRAM_BUILDER_SPAWNER_CREATOR_FLOW.md")
PRODUCT_CONSUMER_BRANCHES = Path("docs/creator_system/PRODUCT_SURFACE_CONSUMER_BRANCHES_2026-05-01.md")
CREATOR_SYSTEM_WORKFLOW = Path(".github/workflows/creator-system.yml")
MULTI_DOMAIN_VALIDATION = Path(
    "docs/creator_system/CREATOR_SYSTEM_MULTI_DOMAIN_VALIDATION_PLAN.md"
)
BENCHMARK_HONESTY_STANDARD = Path(
    "docs/creator_system/BENCHMARK_GENERATION_HONESTY_STANDARD.md"
)
STARTUP_YC_EXTERNAL_RECOMPUTE = Path(
    "docs/creator_system/STARTUP_YC_EXTERNAL_RECOMPUTE_ADAPTERS.md"
)


def test_creator_system_readme_keeps_claim_boundaries_visible() -> None:
    text = README.read_text(encoding="utf-8")

    assert "## Current Claim Levels" in text
    assert "CREATOR_SYSTEM_RELEASE_NOTES_2026-05-01.md" in text
    assert "PRODUCT_SURFACE_READ_ONLY_ADAPTERS.md" in text
    assert "CREATOR_SYSTEM_MULTI_DOMAIN_VALIDATION_PLAN.md" in text
    assert "BENCHMARK_GENERATION_HONESTY_STANDARD.md" in text
    assert "| Startup YC reference fixture | `transfer_supported` |" in text
    assert "| Multi-domain generated matrix | `candidate_review` |" in text
    assert "36-row generated multi-seed summary" in text
    assert "`network_absorbable` is blocked" in text
    assert "| Product surfaces | Read-only consumer branches |" in text
    assert "| Network absorption | Future gated claim |" in text
    assert "| Retrieval memory domain | Local memory-lane contract |" in text
    assert "does not prove real virality" in text
    assert "does not prove product correctness" in text
    assert "STARTUP_YC_EXTERNAL_RECOMPUTE_ADAPTERS.md" in text
    assert (
        "Startup YC validation plan, evidence, shape-check, gate-check, and suite outputs"
        in text
    )
    assert "shape-only raw evidence CI fixture" in text
    assert (
        "`evidence_mode`: `saved` for normal smoke, `recomputed` for `--recompute`"
        in text
    )


def test_creator_system_readme_keeps_command_index_visible() -> None:
    text = README.read_text(encoding="utf-8")

    assert "## Executable Command Index" in text
    for command in (
        "creator-run-init",
        "creator-run-smoke",
        "creator-run-doctor",
        "creator-run-template-check",
        "artifact-quality-score",
        "artifact-quality-benchmark",
        "tool-operation-check",
        "retrieval-memory-check",
        "creator-mission-status",
        "startup-yc-promotion-gate-check",
        "startup-yc-validation-evidence-check",
        "startup-yc-multi-seed-check",
        "startup-yc-heldout-check",
        "startup-yc-review-gates-check",
        "startup-yc-promotion-evidence-check",
        "startup-yc-validation-suite",
        "mirofish-content-simulate",
        "mirofish-content-route",
    ):
        assert command in text


def test_creator_system_release_notes_keep_network_boundary_visible() -> None:
    text = RELEASE_NOTES.read_text(encoding="utf-8")

    assert "Startup YC remains `transfer_supported`, not `network_absorbable`." in text
    assert "Product runtime wiring remains deferred" in text
    assert "creator-mission-status" in text
    assert "startup-yc-promotion-gate-check" in text
    assert "startup-yc-multi-seed-check" in text
    assert "startup-yc-heldout-check" in text
    assert "startup-yc-review-gates-check" in text
    assert "startup-yc-promotion-evidence-check" in text
    assert "startup-yc-validation-suite" in text
    assert "validation_suite_blocked.json" in text
    assert "startup-yc-validation-evidence.schema.json" in text
    assert "startup-yc-validation-evidence-check-result.schema.json" in text
    assert "startup-yc-validation-evidence-check" in text
    assert "shape_only_multi_seed_evidence.json" in text
    assert "does not count as Startup YC multi-seed validation" in text
    assert "Raw validation-evidence shape-check outputs now include source input hashes" in text
    assert "Generator acceptance tests now assert generated report input hashes" in text
    assert "`creator-run-smoke` output now includes `evidence_mode`" in text
    assert "`creator-mission-status` now carries smoke `evidence_mode`" in text
    assert "Builder" in text
    assert "Telegram read-only views" in text
    assert "Spawner, Canvas, and Kanban mission-status projections" in text
    assert "recomputed-mode regression" in text
    assert "Product-flow docs now require downstream surfaces to preserve" in text
    assert "`creator-mission-status.schema.json` now rejects Canvas and Kanban" in text
    assert "CREATOR_SYSTEM_MULTI_DOMAIN_VALIDATION_PLAN.md" in text
    assert "BENCHMARK_GENERATION_HONESTY_STANDARD.md" in text
    assert "case oracles" in text
    assert "lane results" in text
    assert "tampered benchmark manifests" in text
    assert "run_multi_seed_generator_validation" in text
    assert "36-row" in text
    assert "failed seed rows block the aggregate" in text
    assert "Generator acceptance now includes a retrieval/memory boundary domain" in text
    assert "evidence shape-check outputs and rejects accidental" in text
    assert "validate saved `startup-yc-validation-evidence-check`" in text
    assert "input hashes from absent evidence with explicit missing-input records" in text
    assert "rejects impossible raw-evidence verdicts" in text
    assert "validates it against the check-result schema" in text
    assert "startup-yc-validation-plan.schema.json" in text
    assert "validates the saved Startup YC `validation_plan.json`" in text
    assert "source-report recompute checks" in text
    assert "startup-yc-gate-check-result.schema.json" in text
    assert "startup-yc-validation-suite.schema.json" in text
    assert "raw-evidence input hashes" in text
    assert "CLI coverage now generates gate outputs" in text
    assert "validates each saved subcheck" in text
    assert "Creator-system CI now runs focused lint" in text
    assert "tests/test_creator_mission_adapter.py" in text
    assert "Latest focused creator-system suite result before CI push: `145 passed`." in text


def test_creator_system_workflow_validates_raw_evidence_check_result_schema() -> None:
    text = CREATOR_SYSTEM_WORKFLOW.read_text(encoding="utf-8")

    assert "startup-yc-validation-evidence-check" in text
    assert "--output /tmp/startup-yc-smoke.json" in text
    assert "smoke-result.schema.json" in text
    assert 'assert smoke_payload["evidence_mode"] == "saved"' in text
    assert "--output /tmp/startup-yc-validation-evidence-check.json" in text
    assert "startup-yc-validation-evidence.schema.json" in text
    assert "shape_only_multi_seed_evidence.json" in text
    assert "startup-yc-validation-evidence-check-result.schema.json" in text
    assert "startup-yc-validation-plan.schema.json" in text
    assert "Draft202012Validator(plan_schema).validate(plan_payload)" in text
    assert "Draft202012Validator(raw_schema).validate(raw_payload)" in text
    assert "Draft202012Validator(schema).validate(payload)" in text
    assert "--output /tmp/startup-yc-validation-suite.json" in text
    assert "startup-yc-validation-suite.schema.json" in text
    assert "startup-yc-gate-check-result.schema.json" in text
    assert "validation_suite_blocked.json" in text
    assert "validator.validate(payload)" in text
    assert "tests/test_startup_yc_operator_validation.py" in text
    assert "actions/checkout@v6" in text
    assert "actions/setup-python@v6" in text
    assert "FORCE_JAVASCRIPT_ACTIONS_TO_NODE24" not in text


def test_product_flow_docs_use_creator_mission_status_as_read_only_bridge() -> None:
    phase_2 = PHASE_2_BACKLOG.read_text(encoding="utf-8")
    product_flow = PRODUCT_FLOW.read_text(encoding="utf-8")

    for text in (phase_2, product_flow):
        assert "creator-mission-status" in text
        assert "read-only" in text
        assert "evidence_mode" in text
        assert "network_absorbable" in text

    assert "Product tests prove read-only adapters preserve claim boundaries" in phase_2
    assert "adaptive_creator_loop.creator_mission_status.v1" in product_flow


def test_product_consumer_branch_ledger_preserves_deferred_runtime_boundary() -> None:
    text = PRODUCT_CONSUMER_BRANCHES.read_text(encoding="utf-8")

    for repo in (
        "spark-intelligence-builder",
        "spawner-ui",
        "spark-canvas",
        "spark-telegram-bot",
    ):
        assert repo in text
    assert "adaptive_creator_loop.creator_mission_status.v1" in text
    assert "`ready_for_swarm_packet` remains a review state, not `network_absorbable`." in text
    assert "Product PRs are open but not merged here." in text
    assert "https://github.com/vibeforge1111/spark-intelligence-builder/pull/26" in text
    assert "https://github.com/vibeforge1111/vibeship-spawner-ui/pull/1" in text
    assert "https://github.com/vibeforge1111/spark-canvas/pull/1" in text
    assert "https://github.com/vibeforge1111/spark-telegram-bot/pull/1" in text


def test_startup_yc_external_recompute_adapter_contract_blocks_stronger_claims() -> None:
    text = STARTUP_YC_EXTERNAL_RECOMPUTE.read_text(encoding="utf-8")

    for phrase in (
        "Startup Bench transfer adapter",
        "Specialization-path absorption adapter",
        "Broad transfer adapter",
        "Swarm packet regeneration adapter",
        "Report provenance adapter",
        "stale_external_startup_yc_candidate_score.json",
        "adaptive_creator_loop.external_recompute.v1",
        "creator-run-smoke --recompute --fail-on-blocked",
        "creator-run-doctor --recompute",
        "implemented for baseline mean",
        "implemented for aggregate scores",
        "implemented for packet evidence",
        "absent or stale source reports",
        "standalone external rerun provenance packets",
        "startup_yc_external_v1",
        "not `network_absorbable`",
        "multi-seed validation",
        "publication approval",
    ):
        assert phrase in text


def test_multi_domain_validation_plan_tracks_benchmark_maturity() -> None:
    text = MULTI_DOMAIN_VALIDATION.read_text(encoding="utf-8")

    for phrase in (
        "Domain Matrix",
        "Benchmark Maturity",
        "Generated acceptance benchmark packs",
        "Domain-specific benchmark systems",
        "Artifact quality",
        "Tool operation",
        "Content simulation",
        "Doctor/security",
        "Startup operator",
        "Retrieval/memory",
        "schema-valid `creator-mission-status` packet",
        "BENCHMARK_GENERATION_HONESTY_STANDARD.md",
        "case oracles",
        "failure modes",
        "lane-level report results",
        "Changed benchmark manifests block recompute",
        "Changed saved lane results block recompute",
        "run_multi_seed_generator_validation",
        "multi_seed_validation_summary.json",
        "`aggregate_hidden_failures` to false",
        "forced weak-seed regression",
        "36 generated runs total",
        "does not approve `network_absorbable`",
    ):
        assert phrase in text


def test_benchmark_generation_honesty_standard_keeps_swarm_boundary_visible() -> None:
    text = BENCHMARK_HONESTY_STANDARD.read_text(encoding="utf-8")

    for phrase in (
        "Required Case Contract",
        "oracle.expected_behavior",
        "oracle.failure_mode",
        "hallucination_risk",
        "calibration_status",
        "Required Manifest Contract",
        "anti-gaming checks",
        "failed seeds cannot be hidden",
        "Required Report Contract",
        "lane_results",
        "benchmark/manifest.json",
        "benchmark/cases.jsonl",
        "domain-chip/scoring_hooks.json",
        "`network_absorbable`",
        "multi-seed validation",
        "publication approval",
    ):
        assert phrase in text
