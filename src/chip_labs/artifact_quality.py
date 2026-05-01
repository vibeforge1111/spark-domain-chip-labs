"""Local artifact-quality scoring for Spark design docs and PR writeups."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any


CLAIM_BOUNDARY = "artifact_quality local review only"

CHECKS = (
    {
        "id": "acceptance_gates",
        "label": "Acceptance gates",
        "keywords": ("acceptance", "gate", "success criteria", "done when"),
        "repair": "Add explicit acceptance gates or success criteria.",
    },
    {
        "id": "runnable_evidence",
        "label": "Runnable evidence",
        "keywords": ("pytest", "creator-run-smoke", "ruff", "command", "recompute"),
        "repair": "Name the exact verification command or recompute path.",
    },
    {
        "id": "test_evidence",
        "label": "Test evidence",
        "keywords": ("test", "tests", "passed", "failed", "coverage"),
        "repair": "Add test evidence and current pass/fail state.",
    },
    {
        "id": "risk_boundary",
        "label": "Risk boundary",
        "keywords": ("risk", "failure mode", "blocker", "unsafe", "known limit"),
        "repair": "Name the main risks, known limits, or blockers.",
    },
    {
        "id": "rollback_plan",
        "label": "Rollback plan",
        "keywords": ("rollback", "revert", "deprecation", "back out"),
        "repair": "Add rollback or deprecation steps.",
    },
    {
        "id": "claim_boundary",
        "label": "Claim boundary",
        "keywords": ("claim boundary", "do not claim", "local only", "not network_absorbable"),
        "repair": "State what the artifact proves and what it does not prove.",
    },
    {
        "id": "mission_handoff",
        "label": "Mission handoff",
        "keywords": ("mission", "handoff", "owner", "next action", "operator"),
        "repair": "Add owner, next action, or mission-control handoff details.",
    },
)

POLISH_WORDS = (
    "beautiful",
    "delightful",
    "elegant",
    "frictionless",
    "game-changing",
    "intuitive",
    "magical",
    "seamless",
    "world-class",
)

PROOF_CHECKS = {"acceptance_gates", "runnable_evidence", "test_evidence", "rollback_plan"}


def score_artifact_quality(
    text: str,
    *,
    artifact_id: str = "",
    artifact_kind: str = "design_doc",
    source_path: str = "",
) -> dict[str, Any]:
    """Score a design/PR artifact for review-readiness evidence."""

    normalized = _normalize(text)
    checks = [_score_check(normalized, check) for check in CHECKS]
    passed = [check for check in checks if check["status"] == "pass"]
    failed = [check for check in checks if check["status"] == "fail"]
    score = round(len(passed) / len(checks), 4)
    failed_ids = {check["id"] for check in failed}
    polish_hits = _keyword_hits(normalized, POLISH_WORDS)
    trap_flags = []
    if polish_hits and failed_ids & PROOF_CHECKS:
        trap_flags.append("polished_but_unproven")
    verdict = _verdict(score, trap_flags, failed_ids)
    return {
        "packet_kind": "artifact_quality_report",
        "artifact_id": artifact_id,
        "artifact_kind": artifact_kind,
        "source_path": source_path,
        "verdict": verdict,
        "score": score,
        "status_counts": {
            "pass": len(passed),
            "fail": len(failed),
        },
        "checks": checks,
        "trap_flags": trap_flags,
        "polish_hits": polish_hits,
        "missing_checks": [check["id"] for check in failed],
        "repair_actions": [check["repair"] for check in failed],
        "claim_boundary": CLAIM_BOUNDARY,
        "safe_claim": "This artifact is locally reviewable for evidence completeness.",
        "unsafe_claim": "This artifact quality score does not prove product correctness or replace human review.",
    }


def score_artifact_quality_file(path: str | Path, *, artifact_kind: str = "design_doc") -> dict[str, Any]:
    """Read and score an artifact-quality input file."""

    source = Path(path)
    return score_artifact_quality(
        source.read_text(encoding="utf-8"),
        artifact_id=source.stem,
        artifact_kind=artifact_kind,
        source_path=str(source),
    )


def format_artifact_quality_markdown(report: dict[str, Any]) -> str:
    """Render an operator-facing artifact-quality report."""

    lines = [
        "# Artifact Quality Report",
        "",
        f"- Verdict: `{report.get('verdict', 'unknown')}`",
        f"- Score: `{report.get('score', 0):.2f}`",
        f"- Claim boundary: `{report.get('claim_boundary', CLAIM_BOUNDARY)}`",
        f"- Trap flags: `{', '.join(report.get('trap_flags', [])) or 'none'}`",
        "",
        "## Checks",
        "",
    ]
    for check in report.get("checks", []):
        lines.append(f"- `{check['status']}` {check['label']}: {check['message']}")
    if report.get("repair_actions"):
        lines.extend(["", "## Repair Actions", ""])
        for action in report["repair_actions"]:
            lines.append(f"- {action}")
    lines.extend([
        "",
        "## Claim Boundary",
        "",
        f"Safe: {report.get('safe_claim', '')}",
        "",
        f"Unsafe: {report.get('unsafe_claim', '')}",
    ])
    return "\n".join(lines).rstrip() + "\n"


def _score_check(normalized: str, check: dict[str, Any]) -> dict[str, str]:
    hits = _keyword_hits(normalized, check["keywords"])
    status = "pass" if hits else "fail"
    message = f"Found: {', '.join(hits)}." if hits else check["repair"]
    return {
        "id": check["id"],
        "label": check["label"],
        "status": status,
        "message": message,
        "repair": check["repair"],
    }


def _verdict(score: float, trap_flags: list[str], failed_ids: set[str]) -> str:
    if trap_flags or len(failed_ids & PROOF_CHECKS) >= 2:
        return "blocked"
    if score < 0.85:
        return "needs_revision"
    return "review_ready"


def _keyword_hits(normalized: str, keywords: tuple[str, ...]) -> list[str]:
    hits = []
    for keyword in keywords:
        pattern = r"\b" + re.escape(keyword.lower()).replace(r"\ ", r"\s+") + r"\b"
        if re.search(pattern, normalized):
            hits.append(keyword)
    return hits


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()
