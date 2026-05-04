"""Honest production-readiness aggregate for the creator-system beta."""

from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

from .creator_beta_readiness import build_creator_system_beta_check
from .creator_generator import run_multi_seed_generator_validation
from .creator_release_gate import build_creator_release_gate
from .creator_run import repo_root


SCHEMA_VERSION = "adaptive_creator_loop.creator_system_production_readiness.v1"


def build_creator_system_production_readiness(
    *,
    workspace_dir: str | Path | None = None,
    startup_run_dir: str | Path | None = None,
    validation_plan_path: str | Path | None = None,
    generated_briefs_path: str | Path | None = None,
    generated_summary_path: str | Path | None = None,
    product_runtime_review_path: str | Path | None = None,
    seeds: tuple[int, ...] = (1,),
    variants_per_domain: int = 1,
) -> dict[str, Any]:
    """Build a user-beta and standard-readiness packet without publication claims."""

    root = repo_root()
    validation_plan = Path(validation_plan_path) if validation_plan_path else _default_validation_plan(root)
    generated_briefs = Path(generated_briefs_path) if generated_briefs_path else _default_generated_briefs(root)
    product_review = Path(product_runtime_review_path) if product_runtime_review_path else _default_product_review(root)
    startup_review = _default_startup_network_review(root)

    workspace = Path(workspace_dir) if workspace_dir else _default_workspace()
    workspace_clean_before = not workspace.exists() or not any(workspace.iterdir())
    workspace.mkdir(parents=True, exist_ok=True)

    generation_blockers: list[str] = []
    generated_summary_ref: Path | None = Path(generated_summary_path) if generated_summary_path else None
    generated_matrix: dict[str, Any] | None = None
    if generated_summary_ref is None:
        if not workspace_clean_before:
            generation_blockers.append("workspace_dir_not_clean")
        else:
            briefs = _load_briefs(generated_briefs)
            generated_matrix = run_multi_seed_generator_validation(
                workspace / "generated-multi-seed",
                briefs,
                seeds=seeds,
                variants_per_domain=variants_per_domain,
            )
            generated_summary_ref = workspace / "generated-multi-seed" / "multi_seed_validation_summary.json"

    beta = build_creator_system_beta_check(
        startup_run_dir=startup_run_dir,
        validation_plan_path=validation_plan,
        generated_summary_path=generated_summary_ref,
        product_runtime_review_path=product_review,
    )
    release_gate = build_creator_release_gate(
        validation_plan_path=validation_plan,
        generated_summary_path=generated_summary_ref,
        startup_network_review_path=startup_review,
        product_runtime_review_path=product_review,
        requested_release="production_standard_rehearsal",
    )
    tracks = _tracks(
        beta=beta,
        release_gate=release_gate,
        generated_matrix=generated_matrix,
        generation_blockers=generation_blockers,
    )
    blocking_checks = [
        f"{track['name']}:{blocker}"
        for track in tracks
        if track["verdict"] != "pass"
        and track["name"] != "network_absorption_publication"
        for blocker in track["blocking_checks"]
    ]
    return {
        "schema_version": SCHEMA_VERSION,
        "verdict": "pass" if not blocking_checks else "blocked",
        "network_absorbable": False,
        "claim_boundary": (
            "This packet can approve repo/user beta readiness and creator-system "
            "standard readiness only; it does not approve network_absorbable or "
            "product runtime publication."
        ),
        "readiness_tracks": tracks,
        "blocking_checks": blocking_checks,
        "release_gate_summary": _release_gate_summary(release_gate),
        "input_provenance": [
            _provenance("workspace_dir", workspace),
            _provenance("validation_plan", validation_plan),
            _provenance("generated_briefs", generated_briefs),
            _provenance("generated_summary", generated_summary_ref),
            _provenance("startup_network_review", startup_review),
            _provenance("product_runtime_review", product_review),
        ],
        "next_actions": _next_actions(blocking_checks),
    }


def _tracks(
    *,
    beta: dict[str, Any],
    release_gate: dict[str, Any],
    generated_matrix: dict[str, Any] | None,
    generation_blockers: list[str],
) -> list[dict[str, Any]]:
    phases = {
        str(phase.get("phase")): phase
        for phase in release_gate.get("phase_status", [])
        if isinstance(phase, dict)
    }
    generated_phase = phases.get("generated_multi_seed_validation", {})
    startup_phase = phases.get("startup_yc_network_absorption_review", {})
    product_phase = phases.get("product_runtime_integration_review", {})

    beta_blockers = list(beta.get("blocking_checks") or [])
    standard_blockers = list(generation_blockers)
    if beta.get("verdict") != "pass":
        standard_blockers.append(f"beta_verdict:{beta.get('verdict')}")
    if generated_phase.get("passed") is not True:
        standard_blockers.append("generated_multi_seed_phase_not_passing")
    if product_phase.get("passed") is not True:
        standard_blockers.append("product_runtime_phase_not_passing")
    if startup_phase.get("passed") is not False:
        standard_blockers.append("startup_network_absorption_boundary_not_blocked")
    if release_gate.get("network_absorbable") is not False:
        standard_blockers.append("release_gate_claimed_network_absorbable")

    network_blockers = [
        blocker
        for blocker in release_gate.get("blocking_checks", [])
        if str(blocker).startswith("startup_yc_network_absorption_review:")
    ]
    if not network_blockers:
        network_blockers.append("startup_network_absorption_requires_human_release_review")

    return [
        _track(
            "repo_user_beta_readiness",
            blockers=beta_blockers,
            detail={
                "score": 100 if not beta_blockers else 0,
                "beta_verdict": beta.get("verdict"),
                "check_count": len(beta.get("checks") or []),
            },
        ),
        _track(
            "production_grade_creator_system_standard",
            blockers=standard_blockers,
            detail={
                "score": 100 if not standard_blockers else 0,
                "generated_phase_passed": generated_phase.get("passed"),
                "generated_run_count": _generated_run_count(generated_matrix, generated_phase),
                "product_phase_passed": product_phase.get("passed"),
                "startup_network_absorption_blocked": startup_phase.get("passed") is False,
            },
        ),
        {
            "name": "network_absorption_publication",
            "verdict": "blocked",
            "score": 0,
            "blocking_checks": network_blockers,
            "detail": {
                "network_absorbable": False,
                "required_before_upgrade": [
                    "multi_seed_validation",
                    "human_operator_calibration",
                    "privacy_review",
                    "rollback_review",
                    "publication_approval",
                ],
            },
        },
    ]


def _track(name: str, *, blockers: list[str], detail: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": name,
        "verdict": "pass" if not blockers else "blocked",
        "score": 100 if not blockers else 0,
        "blocking_checks": _dedupe(blockers),
        "detail": detail,
    }


def _release_gate_summary(release_gate: dict[str, Any]) -> dict[str, Any]:
    phases = {
        str(phase.get("phase")): phase
        for phase in release_gate.get("phase_status", [])
        if isinstance(phase, dict)
    }
    return {
        "verdict": release_gate.get("verdict"),
        "network_absorbable": release_gate.get("network_absorbable"),
        "generated_phase_passed": phases.get("generated_multi_seed_validation", {}).get("passed"),
        "startup_phase_passed": phases.get("startup_yc_network_absorption_review", {}).get("passed"),
        "product_phase_passed": phases.get("product_runtime_integration_review", {}).get("passed"),
        "blocking_checks": release_gate.get("blocking_checks", []),
    }


def _generated_run_count(
    generated_matrix: dict[str, Any] | None,
    generated_phase: dict[str, Any],
) -> int | None:
    if generated_matrix:
        matrix = generated_matrix.get("matrix")
        if isinstance(matrix, dict):
            count = matrix.get("completed_run_count")
            return int(count) if isinstance(count, int) else None
    detail = generated_phase.get("detail")
    if isinstance(detail, dict) and isinstance(detail.get("row_count"), int):
        return int(detail["row_count"])
    return None


def _load_briefs(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    briefs = data.get("briefs") if isinstance(data, dict) else data
    if not isinstance(briefs, list) or not briefs:
        raise ValueError(f"{path} must contain a non-empty JSON list or {{'briefs': [...]}}")
    if not all(isinstance(item, dict) for item in briefs):
        raise ValueError(f"{path} briefs must be JSON objects")
    return briefs


def _next_actions(blocking_checks: list[str]) -> list[str]:
    if not blocking_checks:
        return [
            "Use this repo as a local technical beta with production-grade creator-system standard checks.",
            "Keep network absorption blocked until the Startup YC promotion bundle and human release review pass.",
        ]
    return [
        "Repair blocked readiness tracks before claiming 100% beta or standard readiness.",
        "Keep network_absorbable false while blockers remain visible.",
    ]


def _provenance(label: str, path_value: str | Path | None) -> dict[str, Any]:
    if path_value is None:
        return {"label": label, "path": None, "present": False, "sha256": None}
    path = Path(path_value)
    present = path.exists()
    return {
        "label": label,
        "path": str(path),
        "present": present,
        "sha256": _sha256(path) if present and path.is_file() else None,
    }


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dedupe(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))


def _default_workspace() -> Path:
    return Path(tempfile.mkdtemp(prefix="creator-system-production-readiness-"))


def _default_validation_plan(root: Path) -> Path:
    return root / "docs" / "creator_system" / "examples" / "startup-yc-operator-validation" / "validation_plan.json"


def _default_generated_briefs(root: Path) -> Path:
    return root / "docs" / "creator_system" / "examples" / "generated-multi-domain-briefs.json"


def _default_product_review(root: Path) -> Path:
    return root / "docs" / "creator_system" / "examples" / "product-runtime-review" / "review-complete-read-only.json"


def _default_startup_network_review(root: Path) -> Path:
    return root / "docs" / "creator_system" / "examples" / "startup-yc-operator-validation" / "network_absorption_review_blocked.json"
