from __future__ import annotations

from pathlib import Path


README = Path("docs/creator_system/README.md")
RELEASE_NOTES = Path("docs/creator_system/CREATOR_SYSTEM_RELEASE_NOTES_2026-05-01.md")
PHASE_2_BACKLOG = Path("docs/creator_system/PHASE_2_PRODUCT_FLOW_BACKLOG.md")
PRODUCT_FLOW = Path("docs/creator_system/TELEGRAM_BUILDER_SPAWNER_CREATOR_FLOW.md")
PRODUCT_CONSUMER_BRANCHES = Path("docs/creator_system/PRODUCT_SURFACE_CONSUMER_BRANCHES_2026-05-01.md")
STARTUP_YC_EXTERNAL_RECOMPUTE = Path(
    "docs/creator_system/STARTUP_YC_EXTERNAL_RECOMPUTE_ADAPTERS.md"
)


def test_creator_system_readme_keeps_claim_boundaries_visible() -> None:
    text = README.read_text(encoding="utf-8")

    assert "## Current Claim Levels" in text
    assert "CREATOR_SYSTEM_RELEASE_NOTES_2026-05-01.md" in text
    assert "PRODUCT_SURFACE_READ_ONLY_ADAPTERS.md" in text
    assert "| Startup YC reference fixture | `transfer_supported` |" in text
    assert "`network_absorbable` is blocked" in text
    assert "| Product surfaces | Read-only consumer branches |" in text
    assert "| Network absorption | Future gated claim |" in text
    assert "| Retrieval memory domain | Local memory-lane contract |" in text
    assert "does not prove real virality" in text
    assert "does not prove product correctness" in text
    assert "STARTUP_YC_EXTERNAL_RECOMPUTE_ADAPTERS.md" in text
    assert "Startup YC gate-check/validation-suite outputs" in text


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
    assert "startup-yc-gate-check-result.schema.json" in text
    assert "startup-yc-validation-suite.schema.json" in text
    assert "Creator-system CI now runs focused lint" in text
    assert "Latest focused creator-system suite result before CI push: `126 passed`." in text


def test_product_flow_docs_use_creator_mission_status_as_read_only_bridge() -> None:
    phase_2 = PHASE_2_BACKLOG.read_text(encoding="utf-8")
    product_flow = PRODUCT_FLOW.read_text(encoding="utf-8")

    for text in (phase_2, product_flow):
        assert "creator-mission-status" in text
        assert "read-only" in text
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
        "startup_yc_external_v1",
        "not `network_absorbable`",
        "multi-seed validation",
        "publication approval",
    ):
        assert phrase in text
