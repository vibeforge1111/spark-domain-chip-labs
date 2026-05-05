from __future__ import annotations

import json
import re
from pathlib import Path

import jsonschema


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
SCHEMA_README = Path("docs/creator_system/schemas/README.md")
ROOT_README = Path("README.md")
AGENTS = Path("AGENTS.md")
PYPROJECT = Path("pyproject.toml")
WORKFLOWS_DIR = Path(".github/workflows")
CODEOWNERS = Path(".github/CODEOWNERS")
SCORECARD_WORKFLOW = Path(".github/workflows/scorecard.yml")
USER_QUICKSTART = Path("docs/creator_system/USER_QUICKSTART_BETA.md")
AGENT_CREATOR_PLAYBOOK = Path("docs/creator_system/AGENT_CREATOR_PLAYBOOK.md")
USER_AND_AGENT_ONBOARDING = Path(
    "docs/creator_system/CREATOR_SYSTEM_USER_AND_AGENT_ONBOARDING.md"
)
RELEASE_CHECKLIST = Path("docs/creator_system/RELEASE_READINESS_CHECKLIST_BETA.md")
BETA_RELEASE = Path("docs/creator_system/CREATOR_SYSTEM_BETA_RELEASE_2026-05-04.md")
PUBLIC_BETA_HANDOFF = Path(
    "docs/creator_system/PUBLIC_BETA_RELEASE_HANDOFF_2026-05-04.md"
)
SWARM_REUSABILITY_TASKS = Path(
    "docs/creator_system/CREATOR_SYSTEM_SWARM_REUSABILITY_TASKS.md"
)
SWARM_REUSE_E2E_PLAN = Path(
    "docs/creator_system/CREATOR_SYSTEM_SWARM_REUSE_END_TO_END_PLAN.md"
)
SWARM_REUSE_EXECUTION_EVIDENCE = Path(
    "docs/creator_system/CREATOR_SYSTEM_SWARM_REUSE_EXECUTION_EVIDENCE_2026-05-05.md"
)
SPARK_SWARM_ALIGNMENT_TASKS = Path(
    "docs/creator_system/CREATOR_SYSTEM_SPARK_SWARM_ALIGNMENT_AND_LAUNCH_TASKS.md"
)
SPARK_SWARM_PHASED_BUILD_PLAN = Path(
    "docs/creator_system/CREATOR_SYSTEM_SPARK_SWARM_PHASED_BUILD_PLAN.md"
)
SPARK_SWARM_LAUNCH_REHEARSAL = Path(
    "docs/creator_system/CREATOR_SYSTEM_SPARK_SWARM_LAUNCH_REHEARSAL_2026-05-05.md"
)
SPARK_SWARM_POST_P8_CLEAN_CLONE_REHEARSAL = Path(
    "docs/creator_system/CREATOR_SYSTEM_SPARK_SWARM_POST_P8_CLEAN_CLONE_REHEARSAL_2026-05-05.md"
)
SPARK_SWARM_LAUNCH_HARDENING = Path(
    "docs/creator_system/SPARK_SWARM_LAUNCH_HARDENING_CHECKLIST.md"
)
SPARK_SWARM_PROPOSAL_STATUS_UX_HANDOFF = Path(
    "docs/creator_system/SPARK_SWARM_PROPOSAL_STATUS_UX_HANDOFF.md"
)
SWARM_REUSABLE_PATH = Path("docs/creator_system/SWARM_REUSABLE_CREATOR_PATH.md")
CONTRIBUTING_CREATOR_DOMAINS = Path(
    "docs/creator_system/CONTRIBUTING_CREATOR_DOMAINS.md"
)
SWARM_REVIEW_BUNDLE_SCHEMA = Path(
    "docs/creator_system/schemas/swarm-review-bundle.schema.json"
)
SWARM_CONTRIBUTION_SCHEMA = Path(
    "docs/creator_system/schemas/swarm-contribution-packet.schema.json"
)
STARTUP_YC_SWARM_REVIEW_BUNDLE = Path(
    "docs/creator_system/examples/swarm-review-bundles/startup-yc-transfer-supported/review_bundle.json"
)


def test_creator_system_readme_keeps_claim_boundaries_visible() -> None:
    text = README.read_text(encoding="utf-8")

    assert "## Current Claim Levels" in text
    assert "CREATOR_SYSTEM_RELEASE_NOTES_2026-05-01.md" in text
    assert "CREATOR_SYSTEM_BETA_RELEASE_2026-05-04.md" in text
    assert "PUBLIC_BETA_RELEASE_HANDOFF_2026-05-04.md" in text
    assert "CREATOR_SYSTEM_USER_AND_AGENT_ONBOARDING.md" in text
    assert "CONTRIBUTING_CREATOR_DOMAINS.md" in text
    assert "CREATOR_SYSTEM_SWARM_REUSE_END_TO_END_PLAN.md" in text
    assert "CREATOR_SYSTEM_SWARM_REUSE_EXECUTION_EVIDENCE_2026-05-05.md" in text
    assert "CREATOR_SYSTEM_SPARK_SWARM_ALIGNMENT_AND_LAUNCH_TASKS.md" in text
    assert "CREATOR_SYSTEM_SPARK_SWARM_PHASED_BUILD_PLAN.md" in text
    assert "CREATOR_SYSTEM_SPARK_SWARM_LAUNCH_REHEARSAL_2026-05-05.md" in text
    assert (
        "CREATOR_SYSTEM_SPARK_SWARM_POST_P8_CLEAN_CLONE_REHEARSAL_2026-05-05.md"
        in text
    )
    assert "SPARK_SWARM_LAUNCH_HARDENING_CHECKLIST.md" in text
    assert "SPARK_SWARM_PROPOSAL_STATUS_UX_HANDOFF.md" in text
    assert "CREATOR_SYSTEM_SWARM_REUSABILITY_TASKS.md" in text
    assert "SWARM_REUSABLE_CREATOR_PATH.md" in text
    assert "PRODUCT_SURFACE_READ_ONLY_ADAPTERS.md" in text
    assert "examples/product-runtime-review/" in text
    assert "examples/swarm-review-bundles/" in text
    assert "CREATOR_SYSTEM_MULTI_DOMAIN_VALIDATION_PLAN.md" in text
    assert "BENCHMARK_GENERATION_HONESTY_STANDARD.md" in text
    assert "| Startup YC reference fixture | `transfer_supported` |" in text
    assert "| Multi-domain generated matrix | `candidate_review` |" in text
    assert "validated 36-row generated multi-seed summary" in text
    assert (
        "--generated-multi-seed /tmp/generated-creator-matrix/multi_seed_validation_summary.json"
        in text
    )
    assert "`network_absorbable` is blocked" in text
    assert "| Product surfaces | Read-only consumer branches |" in text
    assert "| Network absorption | Future gated claim |" in text
    assert "| Retrieval memory domain | Local memory-lane contract |" in text
    assert "does not prove real virality" in text
    assert "does not prove product correctness" in text
    assert "STARTUP_YC_EXTERNAL_RECOMPUTE_ADAPTERS.md" in text
    assert (
        "generated multi-seed summaries, and Startup YC validation plan, evidence, shape-check, gate-check, and suite outputs"
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
        "startup-yc-external-provenance-packet",
        "artifact-quality-score",
        "artifact-quality-benchmark",
        "tool-operation-check",
        "retrieval-memory-check",
        "operator-review-check",
        "product-runtime-review-template",
        "product-runtime-review-check",
        "generated-multi-seed-run",
        "generated-multi-seed-summary-check",
        "creator-mission-status",
        "creator-swarm-collective-dry-run",
        "creator-release-gate",
        "creator-system-beta-check",
        "creator-system-release-evidence",
        "startup-yc-promotion-gate-check",
        "startup-yc-validation-evidence-check",
        "startup-yc-multi-seed-check",
        "startup-yc-heldout-check",
        "startup-yc-review-gates-check",
        "startup-yc-promotion-evidence-check",
        "startup-yc-validation-suite",
        "mirofish-content-simulate",
        "mirofish-content-multi-seed",
        "mirofish-content-route",
        "mirofish-provider-adapter-check",
        "mirofish-outcome-calibration-check",
    ):
        assert command in text


def test_agent_creator_playbook_keeps_fresh_agent_boot_path_safe() -> None:
    text = AGENT_CREATOR_PLAYBOOK.read_text(encoding="utf-8")

    for phrase in (
        "## Fresh Agent Boot Sequence",
        "CREATOR_SYSTEM_USER_AND_AGENT_ONBOARDING.md",
        "git status --short",
        "creator-run-template-check --fail-on-blocked",
        "creator-system-beta-check --fail-on-blocked",
        "creator-system-production-readiness --fail-on-blocked",
        "adaptive_creator_loop.creator_intent.v1",
        "CREATOR_SYSTEM_SWARM_REUSABILITY_TASKS.md",
        "SWARM_REUSABLE_CREATOR_PATH.md",
        "local review bundle",
        "CONTRIBUTING_CREATOR_DOMAINS.md",
        "network_publication_allowed\": false",
        "read-only mission-status packet",
        "product wiring stays deferred",
        "creator-run-smoke runs/<run-name> --fail-on-blocked --fail-on-warn",
        "\"network_absorbable\": false",
        "trust the CLI result",
    ):
        assert phrase in text


def test_user_and_agent_onboarding_covers_complete_creator_value_path() -> None:
    text = USER_AND_AGENT_ONBOARDING.read_text(encoding="utf-8")

    for phrase in (
        "# Creator System User And Agent Onboarding",
        "## User Value By System Part",
        "## Step-By-Step User Flow",
        "## Spark Agent Operating Contract",
        "## Proof-Domain Examples",
        "## Documentation Map",
        "Creator intent",
        "Adapter map",
        "Domain chip",
        "Benchmark pack",
        "Specialization path",
        "Autoloop policy",
        "Evidence ladder",
        "Swarm packet",
        "Mission status",
        "Release evidence",
        "python -m chip_labs.cli creator-run-init",
        "python -m chip_labs.cli creator-run-smoke runs/<run-name> --recompute --fail-on-blocked",
        "creator-mission-status",
        "`publication.network_absorbable=false`",
        "network_absorbable` stays `false`",
        "CREATOR_SYSTEM_SWARM_REUSE_END_TO_END_PLAN.md",
        "CREATOR_SYSTEM_SWARM_REUSE_EXECUTION_EVIDENCE_2026-05-05.md",
        "CREATOR_SYSTEM_SPARK_SWARM_ALIGNMENT_AND_LAUNCH_TASKS.md",
        "CREATOR_SYSTEM_SPARK_SWARM_PHASED_BUILD_PLAN.md",
        "CREATOR_SYSTEM_SWARM_REUSABILITY_TASKS.md",
        "SWARM_REUSABLE_CREATOR_PATH.md",
        "CONTRIBUTING_CREATOR_DOMAINS.md",
        "Artifact quality",
        "Tool operation",
        "MiroFish content simulation",
        "Doctor security",
        "Startup YC founder advice",
        "Retrieval memory",
        "what artifacts were created or updated",
        "the weakest evidence tier",
    ):
        assert phrase in text


def test_onboarding_is_linked_from_first_read_docs() -> None:
    docs = {
        README: "CREATOR_SYSTEM_USER_AND_AGENT_ONBOARDING.md",
        USER_QUICKSTART: "CREATOR_SYSTEM_USER_AND_AGENT_ONBOARDING.md",
        AGENT_CREATOR_PLAYBOOK: "CREATOR_SYSTEM_USER_AND_AGENT_ONBOARDING.md",
        Path("docs/creator_system/CREATOR_RUN_GOLDEN_PATH_V1.md"): (
            "CREATOR_SYSTEM_USER_AND_AGENT_ONBOARDING.md"
        ),
        Path("docs/creator_system/templates/creator-run/README.md"): (
            "../../CREATOR_SYSTEM_USER_AND_AGENT_ONBOARDING.md"
        ),
    }

    for path, phrase in docs.items():
        assert phrase in path.read_text(encoding="utf-8")


def test_root_readme_points_to_creator_system_beta_quickstart() -> None:
    text = ROOT_README.read_text(encoding="utf-8")

    assert "## Creator-System Beta Quickstart" in text
    assert "python -m venv .venv" in text
    assert "source .venv/bin/activate  # Windows: .venv\\Scripts\\activate" in text
    assert "chip-labs creator-run-template-check --fail-on-blocked" in text
    assert "chip-labs creator-system-beta-check --fail-on-blocked" in text
    assert "docs/creator_system/CREATOR_SYSTEM_USER_AND_AGENT_ONBOARDING.md" in text
    assert "docs/creator_system/USER_QUICKSTART_BETA.md" in text
    assert "docs/creator_system/CONTRIBUTING_CREATOR_DOMAINS.md" in text
    assert "docs/creator_system/CREATOR_SYSTEM_SWARM_REUSE_END_TO_END_PLAN.md" in text
    assert "docs/creator_system/CREATOR_SYSTEM_SPARK_SWARM_ALIGNMENT_AND_LAUNCH_TASKS.md" in text
    assert "docs/creator_system/CREATOR_SYSTEM_SPARK_SWARM_PHASED_BUILD_PLAN.md" in text
    assert "docs/creator_system/CREATOR_SYSTEM_SWARM_REUSABILITY_TASKS.md" in text
    assert "docs/creator_system/SWARM_REUSABLE_CREATOR_PATH.md" in text
    assert "docs/creator_system/RELEASE_READINESS_CHECKLIST_BETA.md" in text
    assert "docs/creator_system/PUBLIC_BETA_RELEASE_HANDOFF_2026-05-04.md" in text
    assert "docs/creator_system/CREATOR_RUN_GOLDEN_PATH_V1.md" in text
    assert "does not approve `network_absorbable`" in text


def test_repo_agents_file_points_fresh_agents_to_creator_system_contract() -> None:
    text = AGENTS.read_text(encoding="utf-8")

    for phrase in (
        "## Creator-System Fresh Agent Path",
        "docs/creator_system/CREATOR_SYSTEM_USER_AND_AGENT_ONBOARDING.md",
        "docs/creator_system/AGENT_CREATOR_PLAYBOOK.md",
        "docs/creator_system/USER_QUICKSTART_BETA.md",
        "git status --short",
        "creator-run-template-check --fail-on-blocked",
        "creator-system-beta-check --fail-on-blocked",
        "creator-system-production-readiness --fail-on-blocked",
        "ready_for_swarm_packet",
        "Do not claim `network_absorbable`",
        "runtime creator controls",
    ):
        assert phrase in text


def test_pyproject_exposes_chip_labs_console_entrypoint() -> None:
    text = PYPROJECT.read_text(encoding="utf-8")

    assert "[project.scripts]" in text
    assert 'chip-labs = "chip_labs.cli:main"' in text


def test_creator_system_beta_quickstart_is_user_runnable() -> None:
    text = USER_QUICKSTART.read_text(encoding="utf-8")

    for phrase in (
        "python -m pip install -e .",
        "chip-labs creator-run-template-check --fail-on-blocked",
        "chip-labs creator-system-beta-check --fail-on-blocked",
        "chip-labs creator-system-release-evidence",
        "chip-labs creator-system-production-readiness --fail-on-blocked",
        "production_grade_creator_system_standard.score",
        "network_absorption_publication",
        "chip-labs creator-run-init",
        "chip-labs creator-run-smoke",
        "chip-labs creator-run-doctor",
        "generated-multi-seed-run",
        "generated-creator-matrix-evidence",
        "CREATOR_SYSTEM_SWARM_REUSABILITY_TASKS.md",
        "SWARM_REUSABLE_CREATOR_PATH.md",
        "CONTRIBUTING_CREATOR_DOMAINS.md",
        "Startup YC",
        "`network_absorbable`",
        "Startup YC production-gate workbench subcheck",
        "expected blocked rehearsal state",
        "does not publish to Spark Swarm automatically",
    ):
        assert phrase in text


def test_release_readiness_checklist_preserves_beta_boundary() -> None:
    text = RELEASE_CHECKLIST.read_text(encoding="utf-8")

    for phrase in (
        "technical beta, not network publication",
        "`network_absorbable` remains blocked",
        "Fresh clone succeeds",
        "python -m pip install -e .",
        "chip-labs --help",
        "Strict Startup YC saved-evidence smoke passes",
        "Release tag selected: `creator-system-beta-2026-05-04`",
        "chip-labs creator-system-beta-check --fail-on-blocked",
        "creator-system-release-evidence --fail-on-blocked",
        "production-readiness summary",
        "creator-system-production-readiness --fail-on-blocked",
        "creator-system-release-evidence` as a workflow",
        "creator-system-production-readiness` as a workflow",
        "spark-domain-chip-labs-beta-check-20260504190038",
        "spark-domain-chip-labs-beta-fresh-20260504223056",
        "spark-domain-chip-labs-hardening3-fresh-20260505012347",
        "spark-domain-chip-labs-hardening3-fresh-outputs-20260505012347",
        "repo.worktree_clean=true",
        "Hardening 4 public prerelease verification passed on 2026-05-05",
        "creator-system-beta-2026-05-05-hardening-4",
        "sha256:452eee808cca7fbaa4d74599d5b13dc68c6876169190a1f98afd1392b1c27ba1",
        "Hardening 5 public prerelease verification passed on 2026-05-05",
        "creator-system-beta-2026-05-05-hardening-5",
        "0fc3087e36b275d8ca94d2b78ce79e3723d1a992",
        "25346693023",
        "25346723797",
        "sha256:f212b4055d64d43f04fca273c693b3f107e51b29c3a2fc8589a6cba4f7207faa",
        "CREATOR_SYSTEM_USER_AND_AGENT_ONBOARDING.md",
        "Startup YC production-gate workbench beta subcheck",
        "saved blocked fixture",
        "recomputes it before any stronger release claim",
        "Manual generated multi-seed matrix workflow dispatch passed",
        "`36/36`",
        "Extended local generated matrix passed on 2026-05-04",
        "`54/54`",
        "generated-creator-matrix-evidence",
        "summary-check",
        "dirty local",
        "unstaged",
        "MiroFish outcome calibration blocks insufficient or vanity-only",
        "Do not upgrade claims to `network_absorbable`",
    ):
        assert phrase in text


def test_creator_system_beta_release_artifact_preserves_production_boundary() -> None:
    text = BETA_RELEASE.read_text(encoding="utf-8")

    for phrase in (
        "creator-system-beta-2026-05-04",
        "Latest verified hardening baseline: `0fc3087`",
        "creator-system-beta-2026-05-05-hardening-5",
        "https://github.com/vibeforge1111/spark-domain-chip-labs/releases/tag/creator-system-beta-2026-05-05-hardening-5",
        "CREATOR_SYSTEM_USER_AND_AGENT_ONBOARDING.md",
        "technical beta for local and repo-based creator-run workflows",
        "not a Spark Swarm network-publication approval",
        "Fresh clone install: passed on 2026-05-04",
        "Fresh clone plus isolated venv beta check: passed on 2026-05-04",
        "spark-domain-chip-labs-beta-check-20260504190038",
        "Template check: `57 pass / 0 warn / 0 fail`",
        "Local beta readiness check: `pass`",
        "Strict Startup YC smoke",
        "`transfer_supported`",
        "network_absorption_review_blocked.json",
        "`external_provenance:missing`",
        "Broader local creator-system suite before release: `262 passed`",
        "Post-Tag Hardening Evidence",
        "run_generated_multi_seed=true",
        "25336050060",
        "spark-domain-chip-labs-beta-fresh-20260504223056",
        "fresh Startup YC production-gate workbench",
        "`workspace_was_clean=true`",
        "25337256803",
        "creator-system-release-evidence",
        "6ead089b7b3d31a8f9b4304f59e63d156c40ae63",
        "Spark Creator System Beta Hardening 2",
        "creator-system-release-evidence.json",
        "sha256:b7fb79142196c70b06b21689ae5ffffd7dca9d1a317b3581428d2341baac210c",
        "25343419805",
        "9f5d9618b3e29f45f1c904bd8e69373dd0fde2d2",
        "`production_readiness_summary.verdict=pass`",
        "`repo_user_beta_readiness=100`",
        "`production_grade_creator_system_standard=100`",
        "`network_absorption_publication=blocked`",
        "25343638510",
        "34411b0c08e2d9d1cec9fe053f96ccc9f4c8d608",
        "Spark Creator System Beta Hardening 3",
        "creator-system-production-readiness.json",
        "sha256:0f5ed09420e08e253f26cc1f12690d9b187b53422e53aeff1f1bc820c872c409",
        "sha256:abc01895015136c1cc34143d5892b6c7a62e9aa812d9b08e0bd2b5db696745ea",
        "Downloaded the Hardening 3 release assets from GitHub Releases",
        "rechecked both SHA-256 digests",
        "Fresh clone verification for Hardening 3 passed on 2026-05-05",
        "spark-domain-chip-labs-hardening3-fresh-20260505012347",
        "spark-domain-chip-labs-hardening3-fresh-outputs-20260505012347",
        "e5d9cf747f8058eb22465fce71a24351efe19e7f",
        "25344407537",
        "a2420c4291700301524d3540ea2dce81a0503889",
        "Spark Creator System Beta Hardening 4",
        "sha256:452eee808cca7fbaa4d74599d5b13dc68c6876169190a1f98afd1392b1c27ba1",
        "Downloaded the Hardening 4 release assets from GitHub Releases",
        "0fc3087e36b275d8ca94d2b78ce79e3723d1a992",
        "Spark Creator System Beta Hardening 5",
        "sha256:f212b4055d64d43f04fca273c693b3f107e51b29c3a2fc8589a6cba4f7207faa",
        "`verdict=candidate_review`",
        "`mission_run_count=36`",
        "`verdict=pass`",
        "`repo.worktree_clean=true`",
        "`passed=36/36`",
        "Extended local generated matrix passed on 2026-05-04",
        "`passed=54/54`",
        "`row_count=54`",
        "generated-creator-matrix-evidence",
        "summary-check",
        "left untouched and unstaged",
        "does not approve `network_absorbable`",
        "does not wire live Builder, Telegram, Spawner, Canvas, or Kanban",
        "Multi-seed validation",
        "Human/operator calibration",
        "Privacy review",
        "Rollback review",
        "Publication approval",
    ):
        assert phrase in text


def test_public_beta_handoff_preserves_release_shape_and_boundaries() -> None:
    text = PUBLIC_BETA_HANDOFF.read_text(encoding="utf-8")

    for phrase in (
        "Spark Creator System Public Beta Handoff",
        "creator-system-beta-2026-05-04",
        "0fc3087",
        "creator-system-beta-2026-05-05-hardening-5",
        "https://github.com/vibeforge1111/spark-domain-chip-labs/releases/tag/creator-system-beta-2026-05-05-hardening-5",
        "CREATOR_SYSTEM_USER_AND_AGENT_ONBOARDING.md",
        "chip-labs creator-system-beta-check --fail-on-blocked",
        "`network_absorbable`: `false`",
        "Startup YC evidence tier: `transfer_supported`",
        "stronger-release gate: still blocked",
        "passed=36/36",
        "release_gate=blocked",
        "passed=54/54",
        "row_count=54",
        "generated-creator-matrix-54-0c2bd9886a154f27977a6108fa71ccc9",
        "25336050060",
        "spark-domain-chip-labs-beta-fresh-20260504223056",
        "Startup YC production-gate workbench",
        "25337256803",
        "creator-system-release-evidence",
        "6ead089b7b3d31a8f9b4304f59e63d156c40ae63",
        "Spark Creator System Beta Hardening 2",
        "creator-system-release-evidence.json",
        "sha256:b7fb79142196c70b06b21689ae5ffffd7dca9d1a317b3581428d2341baac210c",
        "25343419805",
        "production_readiness_summary.verdict=pass",
        "repo_user_beta_readiness=100",
        "production_grade_creator_system_standard=100",
        "network_absorption_publication=blocked",
        "25343638510",
        "34411b0c08e2d9d1cec9fe053f96ccc9f4c8d608",
        "Spark Creator System Beta Hardening 3",
        "creator-system-production-readiness.json",
        "sha256:0f5ed09420e08e253f26cc1f12690d9b187b53422e53aeff1f1bc820c872c409",
        "sha256:abc01895015136c1cc34143d5892b6c7a62e9aa812d9b08e0bd2b5db696745ea",
        "Downloaded the Hardening 3 release assets from GitHub Releases",
        "rechecked both SHA-256 digests",
        "Fresh clone verification for Hardening 3 passed on 2026-05-05",
        "spark-domain-chip-labs-hardening3-fresh-20260505012347",
        "spark-domain-chip-labs-hardening3-fresh-outputs-20260505012347",
        "e5d9cf747f8058eb22465fce71a24351efe19e7f",
        "25344407537",
        "a2420c4291700301524d3540ea2dce81a0503889",
        "Spark Creator System Beta Hardening 4",
        "sha256:452eee808cca7fbaa4d74599d5b13dc68c6876169190a1f98afd1392b1c27ba1",
        "Downloaded the Hardening 4 release assets from GitHub Releases",
        "0fc3087e36b275d8ca94d2b78ce79e3723d1a992",
        "Spark Creator System Beta Hardening 5",
        "sha256:f212b4055d64d43f04fca273c693b3f107e51b29c3a2fc8589a6cba4f7207faa",
        "`verdict=candidate_review`",
        "`mission_run_count=36`",
        "`verdict=pass`",
        "`repo.worktree_clean=true`",
        "generated-creator-matrix-evidence",
        "summary-check",
        "Keep this beta inside `spark-domain-chip-labs` for now",
        "Do not extract a separate `spark-creator` repo",
        "Product runtime review evidence",
        "publication authority explicitly approves that claim",
    ):
        assert phrase in text


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
    assert "generated-multi-seed-run" in text
    assert "36-row" in text
    assert "failed seed rows block the aggregate" in text
    assert "validate_multi_seed_generator_summary" in text
    assert "tampered summary rows" in text
    assert "generated-multi-seed-summary.schema.json" in text
    assert "generated-multi-seed-summary-check.schema.json" in text
    assert "generated-multi-seed-summary-check" in text
    assert "creator-mission-status --generated-multi-seed" in text
    assert "hidden-failure status" in text
    assert "operator-review-check" in text
    assert "operator-review-packet.schema.json" in text
    assert "operator-review-check.schema.json" in text
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
    assert "startup-yc-external-provenance-packet" in text
    assert "external source hashes" in text
    assert "Startup YC transfer summary now pins hashes" in text
    assert "rejects forged `passed` packets" in text
    assert "startup-yc-network-absorption-review" in text
    assert "startup-yc-network-absorption-review.schema.json" in text
    assert "network_absorption_review_blocked.json" in text
    assert "raw-evidence input hashes" in text
    assert "run_generated_multi_seed=true" in text
    assert "`passed=36/36`" in text
    assert "`mission_run_count=36`" in text
    assert "generated-creator-matrix-evidence" in text
    assert "generated summary" in text
    assert "summary-check" in text
    assert "CLI coverage now generates gate outputs" in text
    assert "validates each saved subcheck" in text
    assert "Full `src/chip_labs` and `tests` ruff cleanup is now committed" in text
    assert "python -m ruff check src/chip_labs tests" in text
    assert "workflow_dispatch" in text
    assert "run_generated_multi_seed" in text
    assert "Creator System CI now runs `creator-release-gate`" in text
    assert "creator-release-gate.schema.json" in text
    assert "/tmp/generated-release-gate.json" in text
    assert "creator-system-beta-check" in text
    assert "creator-system-beta-check.schema.json" in text
    assert "fresh Startup YC production-gate" in text
    assert "expected blocked" in text
    assert "rehearsal state before returning `pass`" in text
    assert "creator-system-release-evidence" in text
    assert "machine-readable technical beta" in text
    assert "clean-worktree status" in text
    assert "Dirty checkouts block release" in text
    assert "uploads the clean-checkout" in text
    assert "workflow artifact" in text
    assert "generated-multi-domain-briefs.json" in text
    assert "tests/test_creator_mission_adapter.py" in text
    assert "tests/test_operator_review.py" in text
    assert "src/chip_labs/operator_review.py" in text
    assert "mirofish-provider-adapter-check" in text
    assert "mirofish-provider-adapter-manifest.schema.json" in text
    assert "mirofish-provider-adapter-check.schema.json" in text
    assert "mirofish-outcome-calibration-check" in text
    assert "mirofish-outcome-calibration-evidence.schema.json" in text
    assert "mirofish-outcome-calibration-check.schema.json" in text
    assert "SPARK_CREATOR_PUBLIC_REPO_DECISION.md" in text
    assert "USER_QUICKSTART_BETA.md" in text
    assert "RELEASE_READINESS_CHECKLIST_BETA.md" in text
    assert "`chip-labs` console entrypoint" in text
    assert "Latest focused creator-system suite result before CI push: `262 passed`." in text
    assert "case_expectations" in text
    assert "calibration_verdict" in text
    assert "failed expectations force `revert`" in text
    assert "multi-RLM judge coverage" in text
    assert "expected-winner oracles" in text
    assert "mirofish-content-multi-seed" in text
    assert "top-candidate stability" in text
    assert "multi-seed-result.json" in text
    assert "expected_postconditions" in text
    assert "plausible success packets" in text
    assert "stable top-candidate evidence" in text
    assert "minimum seed count" in text
    assert "repair_calibration" in text
    assert "recompute replay" in text
    assert "provenance.source_path" in text
    assert "exact `source_refs`" in text
    assert "covered operator moves" in text
    assert "advice artifact reference" in text
    assert "Boolean pass flags alone" in text
    assert "held_out_founder_advice_evidence.json" in text
    assert "held-out gate can pass locally" in text
    assert "weekly scheduled generated-matrix run" in text
    assert "Saved product runtime review fixtures" in text
    assert "read-only review-complete packet" in text
    assert "product runtime phase of `creator-release-gate`" in text
    assert "Extended generated-domain validation now has a recorded 54-row local run" in text


def test_swarm_reusable_creator_path_keeps_review_bundle_local() -> None:
    tasks = SWARM_REUSABILITY_TASKS.read_text(encoding="utf-8")
    path = SWARM_REUSABLE_PATH.read_text(encoding="utf-8")

    for phrase in (
        "Swarm-reusable means",
        "generated-creator-matrix-evidence",
        "SWARM_REUSABLE_CREATOR_PATH.md",
        "CONTRIBUTING_CREATOR_DOMAINS.md",
        "swarm-review-bundle.schema.json",
        "examples/swarm-review-bundles/startup-yc-transfer-supported/",
        "SR-07",
        "Done in `97397ea` via the post-P8 clean-clone rehearsal.",
        "SR-08",
        "CI artifacts remain default",
        "release assets require a future hardening tag with fresh evidence",
        "Remaining Launch Bridge",
        "Spark Swarm commit `c225fcf`",
        "Spark Swarm commit `2185f3f`",
        "Spark Swarm commit `d487e18`",
        "Spark Swarm commit `cd68cf7`",
        "Spark Swarm commit `0783c7d`",
        "Spark Swarm commit `6a61b9e`",
        "Spark Swarm commit `83cb10f`",
        "Spark Swarm commit `4b160d8`",
        "Spark Swarm commit `8a8efe7`",
        "Spark Swarm commit `4951c64`",
        "Spark Swarm commit `5e90b4e`",
        "Spark Swarm commit `00fa489`",
        "--creator-proposal-bundle",
        "bundle policy hardening",
        "creator-network-proposal-bundle.template.json",
        "verified-repo-pr-proof.placeholder.json",
        "publication-approval.placeholder.json",
        "signed-publication-manifest-authority.placeholder.json",
        "creator-system-proposal-status.ui-fixture.json",
        "creator-system-launch-readiness.template.json",
        "scoped-absorption-policy.placeholder.json",
        "hosted-runtime-ui-proof.template.json",
        "hosted-runtime-ui-assertion-matrix.template.json",
        "sharing-preference.template.json",
        "creatorVerifiedRepoPrProof",
        "creatorPublicationApproval",
        "verified-repo PR proof placeholder",
        "standalone blocked authority",
        "not_approved",
        "generated matrix JSON",
        "runtime creator controls as approval inputs",
        "hosted Spark Swarm UI consumption",
        "hosted runtime UI proof still pending",
        "signed publication manifest authority",
        "machine-readable launch readiness template",
        "overall_stage=workspace_and_proposal_contract_ready",
        "network_launch_stage=blocked_by_design",
        "network-memory movement",
        "placeholder_blocked",
        "revocation coverage",
        "template_only",
        "desktop/mobile screenshots",
        "interaction assertions",
        "forbidden public-approval copy",
        "publish/promote/absorb controls",
        "disabled future network-absorbable state",
        "trusted_auto_propose",
        "public_by_policy",
        "share_everything",
        "publication approval",
        "revocation",
        "No task in this ledger may change `network_absorbable` to `true`.",
        "multi-seed validation",
        "product runtime review",
        "publication authority",
    ):
        assert phrase in tasks

    for phrase in (
        "# Swarm Reusable Creator Path",
        "local review bundle",
        "governance.network_publication_allowed=false",
        "publication.network_absorbable=false",
        "swarm/contribution_packet.json",
        "creator-run-smoke <run-dir> --recompute --fail-on-blocked",
        "generated-creator-matrix-evidence",
        "docs/creator_system/schemas/swarm-contribution-packet.schema.json",
        "anti_drift.known_limits",
        "It is not network absorption.",
        "product runtime review",
        "publication authority",
    ):
        assert phrase in path


def test_creator_domain_contributor_guide_preserves_review_boundaries() -> None:
    text = CONTRIBUTING_CREATOR_DOMAINS.read_text(encoding="utf-8")

    for phrase in (
        "# Contributing Creator-System Domains",
        "outside users and fresh Spark agents",
        "`candidate_review`",
        "`transfer_supported`",
        "`network_absorbable=true`",
        "SWARM_REUSABLE_CREATOR_PATH.md",
        "creator-run-smoke <run-dir> --fail-on-blocked --fail-on-warn",
        "creator-run-smoke <run-dir> --recompute --fail-on-blocked",
        "local Swarm packet path",
        "network_absorbable=false",
        "network_publication_allowed=true",
        "ready_for_swarm_packet",
        "full promotion bundle passes",
    ):
        assert phrase in text


def test_swarm_reuse_end_to_end_plan_preserves_blocked_boundaries() -> None:
    text = SWARM_REUSE_E2E_PLAN.read_text(encoding="utf-8")

    for phrase in (
        "# Creator System Swarm Reuse End-To-End Plan",
        "`network_absorbable=false`",
        "`network_publication_allowed=false`",
        "fresh-clone verification",
        "Generated matrix JSON",
        "Inventory report",
        "future promotion bundle plan",
        "Repo/user beta readiness remains at `100`",
        "Creator-system standard readiness remains at `100`",
        "## Blocked By Design",
        "## Completion Log",
        "E2E-07",
        "Final local gates passed on 2026-05-05",
        "product runtime creator controls",
        "publication authority",
    ):
        assert phrase in text


def test_swarm_reuse_execution_evidence_records_artifacts_and_blockers() -> None:
    text = SWARM_REUSE_EXECUTION_EVIDENCE.read_text(encoding="utf-8")

    for phrase in (
        "# Creator System Swarm Reuse Execution Evidence 2026-05-05",
        "`network_absorbable=false`",
        "`network_publication_allowed=false`",
        "Fresh-Clone Verification",
        "c22d6f19ad519c5120b4c6b5883b7db7e78bbbff",
        "Generated Matrix JSON Release-Asset Policy",
        "generated-creator-matrix-evidence",
        "Do not retroactively mutate the Hardening 5 prerelease assets",
        "Inventory Report",
        "`PROJECT.md`; `src/chip_labs/mirofish/personas.py`",
        "`nul`",
        "Future Promotion Bundle Plan",
        "Human/operator calibration",
        "Publication approval",
        "No automatic Spark Swarm publish path from this repo.",
        "Until that promotion bundle exists and passes, the correct state is blocked.",
        "Final Local Gates",
        "25 passed",
        "creator-system-production-readiness --fail-on-blocked",
        "network absorption publication blocked",
    ):
        assert phrase in text


def test_spark_swarm_alignment_tasks_connect_private_and_public_lanes() -> None:
    text = SPARK_SWARM_ALIGNMENT_TASKS.read_text(encoding="utf-8")

    for phrase in (
        "# Creator System Spark Swarm Alignment And Launch Tasks",
        "SPARK_SWARM_WORKSPACE_VS_NETWORK_CONTRIBUTION.md",
        "SPARK_SWARM_INSIGHT_PUBLICATION_SECURITY_OVERVIEW.md",
        "OWASP Top 10 for LLM Applications",
        "NIST AI Risk Management Framework",
        "GitHub App installation-token scoping",
        "private workspace lane",
        "network proposal bundle",
        "verified-repo GitHub PR proof",
        "private_draft",
        "workspace_validated",
        "reviewed_candidate",
        "`network_absorbable=false`",
        "SparkResearcherCollectiveSyncPayload",
        "share_class",
        "CSS-01",
        "CSS-12",
        "Stop-Ship Gates",
        "Launch Readiness Definition",
        "no automatic publish",
    ):
        assert phrase in text


def test_spark_swarm_phased_build_plan_is_executable_and_blocked() -> None:
    text = SPARK_SWARM_PHASED_BUILD_PLAN.read_text(encoding="utf-8")
    alignment = SPARK_SWARM_ALIGNMENT_TASKS.read_text(encoding="utf-8")

    for phrase in (
        "# Creator System Spark Swarm Phased Build Plan",
        "Commit coherent slices often.",
        "P0",
        "P1",
        "P2",
        "P3",
        "P4",
        "P5",
        "P6",
        "P7",
        "P8",
        "creator-swarm-lane-taxonomy.schema.json",
        "creator-network-proposal-bundle.schema.json",
        "SparkResearcherCollectiveSyncPayload",
        "share_class",
        "private_draft",
        "workspace_validated",
        "pr_submitted",
        "reviewed_candidate",
        "blocked_network_absorption",
        "`network_absorbable=false`",
        "`ready_for_swarm_packet` as artifact readiness only",
        "no automatic publish",
        "Cross-Phase Done Definition",
        "Current Next Build Slice",
        "P1 through P8 are complete from this repo's side",
        "Spark Swarm launch bridge",
        "Spark Swarm commit `c225fcf`",
        "Spark Swarm commit `2185f3f`",
        "Spark Swarm commit `d487e18`",
        "Spark Swarm commit `cd68cf7`",
        "Spark Swarm commit `0783c7d`",
        "Spark Swarm commit `6a61b9e`",
        "Spark Swarm commit `83cb10f`",
        "Spark Swarm commit `4b160d8`",
        "Spark Swarm commit `8a8efe7`",
        "Spark Swarm commit `4951c64`",
        "Spark Swarm commit `5e90b4e`",
        "Spark Swarm commit `00fa489`",
        "--creator-proposal-bundle",
        "creator-network-proposal-bundle.template.json",
        "verified-repo-pr-proof.placeholder.json",
        "publication-approval.placeholder.json",
        "signed-publication-manifest-authority.placeholder.json",
        "creator-system-proposal-status.ui-fixture.json",
        "creator-system-launch-readiness.template.json",
        "scoped-absorption-policy.placeholder.json",
        "hosted-runtime-ui-proof.template.json",
        "hosted-runtime-ui-assertion-matrix.template.json",
        "sharing-preference.template.json",
        "not_configured",
        "signing key id",
        "incomplete approved proofs",
        "replay commands",
        "raw Windows paths",
        "unexpected public absorption",
        "creatorVerifiedRepoPrProof",
        "creatorPublicationApproval",
        "verified-repo PR proof placeholder",
        "standalone blocked authority",
        "`not_approved`",
        "generated matrix JSON",
        "runtime creator controls as approval inputs",
        "hosted Spark Swarm UI consumption",
        "display-only contract",
        "`automatic_publish=false`",
        "Hosted runtime UI",
        "signed publication manifest authority",
        "machine-readable launch readiness report",
        "`overall_stage=workspace_and_proposal_contract_ready`",
        "`network_launch_stage=blocked_by_design`",
        "scoped absorption policy",
        "network-memory movement",
        "private/workspace artifacts",
        "runtime creator controls",
        "raw private paths",
        "full creator-run trees",
        "revocation coverage",
        "dirty web runtime files",
        "`template_only`",
        "desktop/mobile screenshots",
        "publish controls",
        "forbidden public-approval copy",
        "publish/promote/absorb controls",
        "disabled future",
        "trusted_auto_propose",
        "public_by_policy",
        "proposal candidates only",
        "cannot bypass redaction",
    ):
        assert phrase in text

    assert "Start with P1" not in text
    assert "CREATOR_SYSTEM_SPARK_SWARM_PHASED_BUILD_PLAN.md" in alignment


def test_spark_swarm_proposal_status_ux_handoff_preserves_claim_boundaries() -> None:
    text = SPARK_SWARM_PROPOSAL_STATUS_UX_HANDOFF.read_text(encoding="utf-8")

    for phrase in (
        "# Spark Swarm Proposal Status UX Handoff",
        "`private`",
        "`workspace_validated`",
        "`proposal_blocked`",
        "`proposal_submitted`",
        "`reviewed_candidate`",
        "`network_absorbable`",
        "ready for review without being ready for network absorption",
        "share_class",
        "redaction_status",
        "allowed_lane",
        "verified_repo_pr_proof.status",
        "publication_approval.status",
        "network absorption is not approved",
        "Stop-Ship Copy Checks",
        "Do not reach this state from this repo today.",
        "future approved publication manifest",
    ):
        assert phrase in text


def test_spark_swarm_launch_rehearsal_records_blocked_private_path() -> None:
    text = SPARK_SWARM_LAUNCH_REHEARSAL.read_text(encoding="utf-8")

    for phrase in (
        "# Creator System Spark Swarm Launch Rehearsal 2026-05-05",
        "Rehearsal status: `pass`",
        "Creator artifact verdict: `ready_for_swarm_packet`",
        "Evidence tier: `transfer_supported`",
        "Mastery share scope: `private`",
        "Review decision: `defer`",
        "Network absorption: `network_absorbable=false`",
        "no automatic publish",
        "creator-swarm-collective-dry-run",
        "SparkResearcherCollectiveSyncPayload-shaped dry-run payload",
        "blocked network proposal bundle contract",
        "19 passed",
        "It does not publish to Spark Swarm.",
        "It does not approve network absorption.",
        "It does not change `network_absorbable=false`.",
        "verified-repo PR proof placeholder",
    ):
        assert phrase in text


def test_spark_swarm_post_p8_clean_clone_rehearsal_records_portable_path() -> None:
    text = SPARK_SWARM_POST_P8_CLEAN_CLONE_REHEARSAL.read_text(encoding="utf-8")

    for phrase in (
        "# Creator System Spark Swarm Post-P8 Clean-Clone Rehearsal 2026-05-05",
        "Rehearsal status: `pass`",
        "Verified commit: `ece3c55`",
        "Clean before: yes",
        "Clean after: yes",
        "Network absorption: `network_absorbable=false`",
        "no automatic publish",
        "49 passed",
        "ready_for_swarm_packet",
        "transfer_supported",
        "workspace-private-clean-clone",
        "shareScope",
        "private",
        "reviewDecision",
        "defer",
        "canonical text hashing",
        "reproducible across normal text checkouts",
        "no hosted Spark Swarm UI consumption proof yet",
        "no signed publication manifest authority",
    ):
        assert phrase in text


def test_spark_swarm_launch_hardening_checklist_covers_security_and_scale() -> None:
    text = SPARK_SWARM_LAUNCH_HARDENING.read_text(encoding="utf-8")

    for phrase in (
        "# Spark Swarm Launch Hardening Checklist",
        "`network_absorbable=false`",
        "`network_publication_allowed=false`",
        "no automatic publish",
        "Least-privilege GitHub tokens",
        "GitHub App installation tokens",
        "Actions hardening",
        "explicit read-only default `GITHUB_TOKEN` permissions",
        "full-length commit SHAs",
        "Workflow change governance",
        "Changes to `.github/workflows/**`",
        "CODEOWNERS or GitHub rulesets",
        "Secret scanning",
        "OpenSSF Scorecard",
        "pinned read-only OpenSSF Scorecard workflow",
        "uploads a JSON review artifact",
        "Verified-repo PR proof",
        "Signed publication manifest",
        "share_class",
        "redaction_status",
        "allowed_lane",
        "full creator-run trees",
        "raw benchmark case corpora",
        "Collective dry-run payload",
        "<= 128 KB target",
        "Proposal bundle",
        "<= 256 KB target",
        "clean clone",
        "not network absorbable",
    ):
        assert phrase in text


def test_swarm_review_bundle_example_is_schema_valid_and_local_only() -> None:
    schema = json.loads(SWARM_REVIEW_BUNDLE_SCHEMA.read_text(encoding="utf-8"))
    bundle = json.loads(STARTUP_YC_SWARM_REVIEW_BUNDLE.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(bundle)

    assert bundle["evidence_tier"] == "transfer_supported"
    assert bundle["network_absorbable"] is False
    assert bundle["network_publication_allowed"] is False
    assert bundle["promotion_boundary"]["product_runtime_controls"] == "read_only"
    assert "network_absorbable" in bundle["promotion_boundary"]["forbidden_claims"]
    assert bundle["bundle_paths"]["creator_intent"]["share_class"] == "private"
    assert bundle["bundle_paths"]["swarm_packet"]["share_class"] == "proposal_redacted"
    assert bundle["bundle_paths"]["swarm_packet"]["allowed_lane"] == (
        "blocked_network_absorption"
    )

    run_dir = Path(bundle["creator_run_dir"])
    assert run_dir.is_dir()
    for record in bundle["bundle_paths"].values():
        assert "share_class" in record
        assert "redaction_status" in record
        assert "allowed_lane" in record
        path = record["path"]
        if path is None:
            assert "absent_reason" in record
            continue
        assert (run_dir / path).exists()

    contribution_schema = json.loads(SWARM_CONTRIBUTION_SCHEMA.read_text(encoding="utf-8"))
    swarm_path = run_dir / bundle["bundle_paths"]["swarm_packet"]["path"]
    swarm_packet = json.loads(swarm_path.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(contribution_schema).validate(swarm_packet)
    assert swarm_packet["evidence"]["tier"] == bundle["evidence_tier"]
    assert swarm_packet["governance"]["network_publication_allowed"] is False


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
    assert "--output /tmp/startup-yc-network-absorption-review.json" in text
    assert "startup-yc-network-absorption-review.schema.json" in text
    assert "network_absorption_review_blocked.json" in text
    assert "startup-yc-production-gate-workbench" in text
    assert "--workspace-dir /tmp/startup-yc-production-gate-workbench" in text
    assert "--output /tmp/startup-yc-production-gate-workbench.json" in text
    assert "startup-yc-production-gate-workbench.schema.json" in text
    assert 'assert workbench_payload["workspace_was_clean"] is True' in text
    assert 'assert workbench_payload["gate_verdicts"]["held_out_founder_advice_pass"] == "passed"' in text
    assert 'assert payload["network_absorbable"] is False' in text
    assert "--output /tmp/creator-release-gate.json" in text
    assert "creator-release-gate.schema.json" in text
    assert "creator-system-release-evidence --production-readiness /tmp/creator-system-production-readiness.json --output /tmp/creator-system-release-evidence.json --fail-on-blocked" in text
    assert "creator-system-release-evidence.schema.json" in text
    assert 'payload["production_readiness_summary"]["verdict"] == "pass"' in text
    assert "creator-system-production-readiness --workspace-dir /tmp/creator-system-production-readiness --output /tmp/creator-system-production-readiness.json --fail-on-blocked" in text
    assert "creator-system-production-readiness.schema.json" in text
    assert "creator-system-production-readiness-artifact" in text
    assert "creator-system-production-readiness.json" in text
    assert (
        "actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a # v7"
        in text
    )
    assert "creator-system-release-evidence-artifact" in text
    assert "creator-system-release-evidence.json" in text
    assert "if-no-files-found: error" in text
    assert "retention-days: 30" in text
    assert 'assert payload["release_ready"] is True' in text
    assert 'assert payload["repo"]["worktree_clean"] is True' in text
    assert "tests/test_creator_beta_readiness.py" in text
    assert "creator-system-beta-check --output /tmp/creator-system-beta-check.json --fail-on-blocked" in text
    assert "creator-system-beta-check.schema.json" in text
    assert 'assert payload["verdict"] == "pass"' in text
    assert 'assert release_payload["verdict"] == "blocked"' in text
    assert 'assert release_payload["network_absorbable"] is False' in text
    assert "generated_multi_seed_validation:missing_generated_multi_seed_summary" in text
    assert "product_runtime_integration_review:missing_product_runtime_review" in text
    assert "validator.validate(payload)" in text
    assert "schedule:" in text
    assert "17 3 * * 1" in text
    assert "github.event_name == 'schedule'" in text
    assert "workflow_dispatch" in text
    assert "run_generated_multi_seed" in text
    assert "generated-multi-seed-run" in text
    assert "generated-multi-domain-briefs.json" in text
    assert "generated-multi-seed-summary-check" in text
    assert "generated-multi-seed-summary.schema.json" in text
    assert "generated-multi-seed-summary-check.schema.json" in text
    assert "creator-mission-status" in text
    assert "generated-mission-status.json" in text
    assert "creator-mission-status.schema.json" in text
    assert "--output /tmp/generated-release-gate.json" in text
    assert 'assert generated_phase["passed"] is True' in text
    assert 'assert product_phase["passed"] is False' in text
    assert "missing_product_runtime_review" in text
    assert "Generated matrix:" in text
    assert "release_gate" in text
    assert "mission_run_count" in text
    assert "generated-creator-matrix-artifact" in text
    assert "generated-creator-matrix-evidence" in text
    assert "generated-multi-seed-summary.json" in text
    assert "generated-multi-seed-summary-check.json" in text
    assert "generated-mission-status.json" in text
    assert "generated-release-gate.json" in text
    assert "permissions:" in text
    assert "contents: read" in text
    assert "tests/test_startup_yc_operator_validation.py" in text
    assert "tests/test_operator_review.py" in text
    assert "python -m ruff check src/chip_labs tests" in text


def test_creator_system_workflow_pins_third_party_actions_to_commit_shas() -> None:
    text = CREATOR_SYSTEM_WORKFLOW.read_text(encoding="utf-8")
    action_refs = re.findall(r"uses:\s+([^@\s]+)@([0-9a-f]{40})(?:\s+#\s+\S+)?", text)
    uses_lines = [line.strip() for line in text.splitlines() if line.strip().startswith("uses:")]

    assert len(action_refs) == len(uses_lines)
    assert ("actions/checkout", "de0fac2e4500dabe0009e67214ff5f5447ce83dd") in action_refs
    assert (
        "actions/setup-python",
        "a309ff8b426b58ec0e2a45f0f869d46889d02405",
    ) in action_refs
    assert (
        "actions/upload-artifact",
        "043fb46d1a93c77aae656e7c1c64a875d1fc6a0a",
    ) in action_refs
    assert "actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd # v6" in text
    assert (
        "actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405 # v6"
        in text
    )
    assert "FORCE_JAVASCRIPT_ACTIONS_TO_NODE24" not in text


def test_creator_system_workflows_avoid_privileged_untrusted_pr_patterns() -> None:
    workflow_paths = sorted(WORKFLOWS_DIR.glob("*.yml")) + sorted(WORKFLOWS_DIR.glob("*.yaml"))

    assert workflow_paths
    for workflow_path in workflow_paths:
        text = workflow_path.read_text(encoding="utf-8")
        assert "pull_request_target:" not in text, workflow_path
        assert "contents: write" not in text, workflow_path
        assert "id-token: write" not in text, workflow_path


def test_creator_system_scorecard_workflow_records_supply_chain_review() -> None:
    text = SCORECARD_WORKFLOW.read_text(encoding="utf-8")
    action_refs = re.findall(r"uses:\s+([^@\s]+)@([0-9a-f]{40})(?:\s+#\s+\S+)?", text)
    uses_lines = [line.strip() for line in text.splitlines() if line.strip().startswith("uses:")]

    assert "permissions:" in text
    assert "contents: read" in text
    assert "security-events: write" not in text
    assert "id-token: write" not in text
    assert "publish_results: false" in text
    assert "results_file: /tmp/scorecard-results.json" in text
    assert "results_format: json" in text
    assert "openssf-scorecard-results" in text
    assert len(action_refs) == len(uses_lines)
    assert ("actions/checkout", "34e114876b0b11c390a56381ad16ebd13914f8d5") in action_refs
    assert (
        "ossf/scorecard-action",
        "4eaacf0543bb3f2c246792bd56e8cdeffafb205a",
    ) in action_refs
    assert (
        "actions/upload-artifact",
        "ea165f8d65b6e75b540449e92b4886f43607fa02",
    ) in action_refs


def test_creator_system_codeowners_covers_workflow_and_launch_gate_changes() -> None:
    text = CODEOWNERS.read_text(encoding="utf-8")

    for phrase in (
        ".github/workflows/** @vibeforge1111",
        "docs/creator_system/SPARK_SWARM_LAUNCH_HARDENING_CHECKLIST.md @vibeforge1111",
    ):
        assert phrase in text


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
        "startup-yc-external-provenance-packet",
        "startup-yc-external-rerun-provenance.schema.json",
        "per-adapter rerun packets",
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
        "case_expectations",
        "`calibration_verdict`",
        "failed expectations force a revert",
        "multi-RLM judge coverage",
        "expected-winner oracle",
        "expected postconditions",
        "control is allowed to trust",
        "`repair_calibration`",
        "quarantine findings",
        "failure modes",
        "lane-level report results",
        "Changed benchmark manifests block recompute",
        "Changed saved lane results block recompute",
        "run_multi_seed_generator_validation",
        "generated-multi-seed-run --briefs <briefs.json> --workspace-dir <dir>",
        "workflow_dispatch",
        "run_generated_multi_seed",
        "generated-multi-domain-briefs.json",
        "validate_multi_seed_generator_summary",
        "generated-multi-seed-summary.schema.json",
        "generated-multi-seed-summary-check.schema.json",
        "generated-multi-seed-summary-check --fail-on-blocked",
        "creator-mission-status --generated-multi-seed",
        "generated matrix mission-status packet",
        "generated-creator-matrix-evidence",
        "failed seed IDs",
        "operator-review-check",
        "operator-review-packet.schema.json",
        "operator-review-check.schema.json",
        "tests/test_operator_review.py",
        "src/chip_labs/operator_review.py",
        "multi_seed_validation_summary.json",
        "`aggregate_hidden_failures` to false",
        "forced weak-seed regression",
        "Changed generated multi-seed summary rows block summary validation",
        "Changed underlying run reports block generated multi-seed summary validation",
        "36 generated runs total",
        "does not approve `network_absorbable`",
    ):
        assert phrase in text


def test_schema_readme_lists_generated_multi_seed_schema_anchors() -> None:
    text = SCHEMA_README.read_text(encoding="utf-8")

    for phrase in (
        "generated-multi-seed-summary.schema.json",
        "generated-multi-seed-summary-check.schema.json",
        "Generated multi-domain multi-seed summary output",
        "Recomputed generated multi-seed summary check output",
        "domain-chip-manifest.schema.json",
        "scoring-hooks.schema.json",
        "hook-smoke-result.schema.json",
        "Generated domain-chip hook smoke output",
        "benchmark-report.schema.json",
        "absorption-summary.schema.json",
        "benchmark-case.schema.json",
        "specialization-path-manifest.schema.json",
        "autoloop-simulation-result.schema.json",
        "Generated keep/revert autoloop simulation output",
        "`network_absorbable=false`",
        "no hidden aggregate failures",
        "tampered summary rows",
        "stale underlying run reports",
        "operator-review-packet.schema.json",
        "operator-review-check.schema.json",
        "swarm-review-bundle.schema.json",
        "Local Spark Swarm review bundle manifest",
        "creator-release-gate.schema.json",
        "creator-system-beta-check.schema.json",
        "creator-system-release-evidence.schema.json",
        "creator-system-production-readiness.schema.json",
        "Machine-readable technical beta release evidence packet",
        "Local creator-system beta readiness aggregate",
        "Honest repo/user beta and creator-system standard readiness tracks",
        "production-readiness summary",
        "product-runtime-review-packet.schema.json",
        "product-runtime-review-check.schema.json",
        "doctor-adversarial-sweep-manifest.schema.json",
        "doctor-adversarial-sweep-result.schema.json",
        "retrieval-memory-packet.schema.json",
        "retrieval-memory-check.schema.json",
        "artifact-quality-report.schema.json",
        "artifact-quality-benchmark-manifest.schema.json",
        "artifact-quality-benchmark-result.schema.json",
        "mirofish-content-route.schema.json",
        "mirofish-content-simulation-result.schema.json",
        "mirofish-content-multi-seed-result.schema.json",
        "mirofish-provider-adapter-manifest.schema.json",
        "mirofish-provider-adapter-check.schema.json",
        "mirofish-outcome-calibration-evidence.schema.json",
        "mirofish-outcome-calibration-check.schema.json",
        "startup-yc-external-rerun-provenance.schema.json",
        "Startup YC external recompute provenance packet",
        "present without a hash",
        "tool-operation-manifest.schema.json",
        "tool-operation-packet.schema.json",
        "tool-operation-check.schema.json",
        "schema-family mutation",
        "production memory runtime remains deferred",
        "local design-doc and PR evidence reviewer",
        "local content-routing and simulator",
        "mission-control safety boundary",
        "local review packages",
        "human/operator calibration",
        "review evidence only",
        "stronger-release evidence",
        "technical beta",
        "dirty release evidence blocks",
        "production-grade creator-system standard",
        "disabled creator controls",
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
