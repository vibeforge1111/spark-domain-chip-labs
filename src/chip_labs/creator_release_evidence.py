"""Release evidence packet for the creator-system technical beta."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from .creator_beta_readiness import build_creator_system_beta_check
from .creator_production_readiness import build_creator_system_production_readiness
from .creator_run import repo_root


SCHEMA_VERSION = "adaptive_creator_loop.creator_system_release_evidence.v1"
DEFAULT_RELEASE_ID = "creator-system-beta-2026-05-04"
REQUIRED_BEFORE_NETWORK_ABSORPTION = [
    "multi_seed_validation",
    "human_operator_calibration",
    "privacy_review",
    "rollback_review",
    "publication_approval",
    "product_runtime_review",
]
RELEASE_COMMANDS = [
    "python -m ruff check src/chip_labs tests",
    "python -m pytest tests/test_creator_beta_readiness.py tests/test_creator_release_gate.py tests/test_creator_system_docs.py tests/test_startup_yc_operator_validation.py -q",
    "chip-labs creator-system-beta-check --fail-on-blocked",
    "chip-labs creator-system-production-readiness --fail-on-blocked",
    "chip-labs creator-run-smoke docs/creator_system/examples/startup-yc-creator-run --fail-on-blocked --fail-on-warn",
]


def build_creator_system_release_evidence(
    *,
    release_id: str = DEFAULT_RELEASE_ID,
    repo_path: str | Path | None = None,
    startup_run_dir: str | Path | None = None,
    validation_plan_path: str | Path | None = None,
    generated_summary_path: str | Path | None = None,
    product_runtime_review_path: str | Path | None = None,
    production_readiness_path: str | Path | None = None,
    git_info: dict[str, Any] | None = None,
    beta_check: dict[str, Any] | None = None,
    production_readiness: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a machine-readable release evidence packet without approving publication."""

    root = Path(repo_path) if repo_path else repo_root()
    repo = git_info or collect_git_info(root)
    beta = beta_check or build_creator_system_beta_check(
        startup_run_dir=startup_run_dir,
        validation_plan_path=validation_plan_path,
        generated_summary_path=generated_summary_path,
        product_runtime_review_path=product_runtime_review_path,
    )
    production = production_readiness or _load_production_readiness(
        production_readiness_path
    )
    if production is None:
        production = build_creator_system_production_readiness(
            startup_run_dir=startup_run_dir,
            validation_plan_path=validation_plan_path,
            generated_summary_path=generated_summary_path,
            product_runtime_review_path=product_runtime_review_path,
        )

    blocking_checks = _release_blockers(repo, beta, production)
    return {
        "schema_version": SCHEMA_VERSION,
        "release_id": release_id,
        "release_type": "technical_beta",
        "verdict": "blocked" if blocking_checks else "pass",
        "release_ready": not blocking_checks,
        "network_absorbable": False,
        "claim_boundary": (
            "This packet proves local technical beta release evidence only; "
            "it does not approve network absorption, product runtime controls, "
            "or Swarm publication."
        ),
        "repo": repo,
        "beta_check_summary": _summarize_beta_check(beta),
        "production_readiness_summary": _summarize_production_readiness(production),
        "required_commands": RELEASE_COMMANDS,
        "evidence_refs": _evidence_refs(),
        "promotion_boundary": {
            "blocked_claim": "network_absorbable",
            "required_before_upgrade": REQUIRED_BEFORE_NETWORK_ABSORPTION,
        },
        "blocking_checks": blocking_checks,
        "next_actions": _next_actions(blocking_checks),
    }


def collect_git_info(repo_path: str | Path) -> dict[str, Any]:
    """Collect repo identity without mutating the checkout."""

    root = Path(repo_path)
    status_lines = _git_lines(root, "status", "--short")
    dirty_files = [line.strip() for line in status_lines if line.strip()]
    return {
        "path": str(root),
        "branch": _git_text(root, "branch", "--show-current") or None,
        "commit": _git_text(root, "rev-parse", "HEAD") or None,
        "remote_url": _git_text(root, "config", "--get", "remote.origin.url") or None,
        "worktree_clean": not dirty_files,
        "dirty_file_count": len(dirty_files),
        "dirty_files_sample": dirty_files[:25],
    }


def _summarize_beta_check(beta_check: dict[str, Any]) -> dict[str, Any]:
    checks = list(beta_check.get("checks") or [])
    passing = [
        check
        for check in checks
        if isinstance(check, dict) and check.get("status") == "pass"
    ]
    return {
        "schema_version": beta_check.get("schema_version"),
        "verdict": beta_check.get("verdict"),
        "network_absorbable": beta_check.get("network_absorbable"),
        "check_count": len(checks),
        "passing_check_count": len(passing),
        "check_names": [
            str(check.get("name"))
            for check in checks
            if isinstance(check, dict) and check.get("name")
        ],
        "blocking_checks": list(beta_check.get("blocking_checks") or []),
    }


def _summarize_production_readiness(readiness: dict[str, Any]) -> dict[str, Any]:
    tracks = {
        str(track.get("name")): track
        for track in readiness.get("readiness_tracks", [])
        if isinstance(track, dict) and track.get("name")
    }
    return {
        "schema_version": readiness.get("schema_version"),
        "verdict": readiness.get("verdict"),
        "network_absorbable": readiness.get("network_absorbable"),
        "track_scores": {
            name: track.get("score")
            for name, track in tracks.items()
        },
        "track_verdicts": {
            name: track.get("verdict")
            for name, track in tracks.items()
        },
        "release_gate_verdict": (
            readiness.get("release_gate_summary", {}).get("verdict")
            if isinstance(readiness.get("release_gate_summary"), dict)
            else None
        ),
        "blocking_checks": list(readiness.get("blocking_checks") or []),
    }


def _release_blockers(
    repo: dict[str, Any],
    beta_check: dict[str, Any],
    production_readiness: dict[str, Any],
) -> list[str]:
    blockers: list[str] = []
    if beta_check.get("verdict") != "pass":
        blockers.append(f"beta_check:{beta_check.get('verdict')}")
    if beta_check.get("network_absorbable") is not False:
        blockers.append("beta_check:claimed_network_absorbable")
    if production_readiness.get("verdict") != "pass":
        blockers.append(f"production_readiness:{production_readiness.get('verdict')}")
    if production_readiness.get("network_absorbable") is not False:
        blockers.append("production_readiness:claimed_network_absorbable")
    tracks = {
        str(track.get("name")): track
        for track in production_readiness.get("readiness_tracks", [])
        if isinstance(track, dict) and track.get("name")
    }
    expected_pass_tracks = (
        "repo_user_beta_readiness",
        "production_grade_creator_system_standard",
    )
    for track_name in expected_pass_tracks:
        track = tracks.get(track_name)
        if not track:
            blockers.append(f"production_readiness:missing_track:{track_name}")
            continue
        if track.get("verdict") != "pass":
            blockers.append(
                f"production_readiness:{track_name}:{track.get('verdict')}"
            )
        if track.get("score") != 100:
            blockers.append(
                f"production_readiness:{track_name}:score:{track.get('score')}"
            )
    network_track = tracks.get("network_absorption_publication")
    if not network_track:
        blockers.append("production_readiness:missing_track:network_absorption_publication")
    elif network_track.get("verdict") != "blocked":
        blockers.append(
            "production_readiness:network_absorption_publication_not_blocked"
        )
    if repo.get("worktree_clean") is not True:
        blockers.append("repo:worktree_dirty")
    if not repo.get("commit"):
        blockers.append("repo:missing_commit")
    return blockers


def _evidence_refs() -> list[dict[str, str]]:
    return [
        {
            "label": "beta_quickstart",
            "path": "docs/creator_system/USER_QUICKSTART_BETA.md",
        },
        {
            "label": "release_checklist",
            "path": "docs/creator_system/RELEASE_READINESS_CHECKLIST_BETA.md",
        },
        {
            "label": "beta_readiness_schema",
            "path": "docs/creator_system/schemas/creator-system-beta-check.schema.json",
        },
        {
            "label": "release_evidence_schema",
            "path": "docs/creator_system/schemas/creator-system-release-evidence.schema.json",
        },
        {
            "label": "production_readiness_schema",
            "path": "docs/creator_system/schemas/creator-system-production-readiness.schema.json",
        },
    ]


def _load_production_readiness(path_value: str | Path | None) -> dict[str, Any] | None:
    if path_value is None:
        return None
    path = Path(path_value)
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def _next_actions(blocking_checks: list[str]) -> list[str]:
    if not blocking_checks:
        return [
            "Use this packet as local technical beta release evidence.",
            "Keep network absorption blocked until the full promotion boundary passes.",
        ]
    return [
        "Repair blocked release-evidence checks before tagging or announcing a new beta.",
        "Use a clean checkout for release evidence if repo:worktree_dirty is present.",
        "Do not infer network absorption or product runtime approval from this packet.",
    ]


def _git_text(repo_path: Path, *args: str) -> str:
    lines = _git_lines(repo_path, *args)
    return lines[0].strip() if lines else ""


def _git_lines(repo_path: Path, *args: str) -> list[str]:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return []
    if result.returncode != 0:
        return []
    return result.stdout.splitlines()
