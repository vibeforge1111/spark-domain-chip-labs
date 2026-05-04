"""Real outcome calibration checks for MiroFish content simulation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


EVIDENCE_SCHEMA_VERSION = "mirofish_content.outcome_calibration_evidence.v1"
CHECK_SCHEMA_VERSION = "mirofish_content.outcome_calibration_check.v1"
CLAIM_BOUNDARY = (
    "real content outcome calibration evidence; does not prove network absorption"
)
REQUIRED_QUALITATIVE_FIELDS = (
    "audience_fit",
    "reply_quality",
    "proof_quality",
    "novelty_quality",
)
REQUIRED_FORBIDDEN_CLAIMS = (
    "real_virality_proven",
    "calibrated_provider_reliability",
    "network_absorbable",
)


def check_content_outcome_calibration(evidence: dict[str, Any]) -> dict[str, Any]:
    """Check real content outcomes without accepting vanity-only evidence."""

    rows = evidence.get("rows")
    row_list = rows if isinstance(rows, list) else []
    minimum_rows = _int_value(evidence.get("minimum_rows_required"), default=20)
    checks: list[dict[str, str]] = []

    _append_check(
        checks,
        "schema_version",
        evidence.get("schema_version") == EVIDENCE_SCHEMA_VERSION,
        "Evidence schema version matches.",
        f"Evidence schema_version must be {EVIDENCE_SCHEMA_VERSION}.",
    )
    _append_check(
        checks,
        "domain",
        evidence.get("domain") == "MiroFish Content Simulation",
        "Evidence domain is MiroFish Content Simulation.",
        "Evidence domain must be MiroFish Content Simulation.",
    )
    _append_check(
        checks,
        "claim_boundary",
        evidence.get("claim_boundary") == CLAIM_BOUNDARY,
        "Claim boundary preserves calibration limits.",
        "Evidence must state that calibration does not prove network absorption.",
    )
    _append_check(
        checks,
        "network_absorbable",
        evidence.get("network_absorbable") is False,
        "Evidence keeps network_absorbable=false.",
        "Outcome calibration evidence must keep network_absorbable=false.",
    )
    _append_check(
        checks,
        "forbidden_claims",
        _has_all(evidence.get("forbidden_claims"), REQUIRED_FORBIDDEN_CLAIMS),
        "Forbidden claims are explicit.",
        "Evidence must forbid real virality, calibrated reliability, and network_absorbable claims.",
    )
    _append_check(
        checks,
        "row_count",
        len(row_list) >= minimum_rows,
        f"Evidence has at least {minimum_rows} rows.",
        f"Evidence needs at least {minimum_rows} real outcome rows.",
    )
    _append_check(
        checks,
        "candidate_coverage",
        len(_distinct(row_list, "candidate_id")) >= 2,
        "Evidence covers at least two candidates.",
        "Evidence needs at least two distinct content candidates.",
    )
    _append_check(
        checks,
        "platform_coverage",
        len(_distinct(row_list, "platform")) >= 1,
        "Evidence names at least one platform.",
        "Every outcome row must name a platform.",
    )
    checks.extend(_row_checks(row_list))
    _append_check(
        checks,
        "not_vanity_only",
        _has_downstream_signal(row_list),
        "Evidence includes downstream-aware signals.",
        "Likes or impressions alone are vanity evidence; include replies, bookmarks, clicks, follower delta, or downstream_signal.",
    )
    _append_check(
        checks,
        "qualitative_review",
        _has_qualitative_review(row_list),
        "Rows include qualitative review fields.",
        "Every row needs audience fit, reply quality, proof quality, and novelty quality review.",
    )

    blocking_checks = [
        check["check_id"] for check in checks if check["status"] == "fail"
    ]
    verdict = "supports_calibration" if not blocking_checks else "inconclusive"
    return {
        "schema_version": CHECK_SCHEMA_VERSION,
        "verdict": verdict,
        "calibration_supported": verdict == "supports_calibration",
        "network_absorbable": False,
        "claim_boundary": CLAIM_BOUNDARY,
        "row_count": len(row_list),
        "minimum_rows_required": minimum_rows,
        "distinct_candidate_count": len(_distinct(row_list, "candidate_id")),
        "checks": checks,
        "blocking_checks": blocking_checks,
        "next_actions": _next_actions(verdict),
    }


def load_content_outcome_calibration(path: str | Path) -> dict[str, Any]:
    """Load content outcome calibration evidence from JSON."""

    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def _row_checks(rows: list[Any]) -> list[dict[str, str]]:
    checks: list[dict[str, str]] = []
    for index, row in enumerate(rows, start=1):
        prefix = f"row_{index}"
        if not isinstance(row, dict):
            checks.append(
                _check(
                    f"{prefix}_shape",
                    False,
                    "Row is shaped.",
                    "Every outcome row must be a JSON object.",
                )
            )
            continue
        checks.append(
            _check(
                f"{prefix}_identity",
                bool(str(row.get("candidate_id") or "").strip())
                and bool(str(row.get("content_id") or "").strip())
                and bool(str(row.get("platform") or "").strip()),
                "Row names candidate, content item, and platform.",
                "Every row needs candidate_id, content_id, and platform.",
            )
        )
        checks.append(
            _check(
                f"{prefix}_denominator",
                _int_value(row.get("impression_count"), default=-1) > 0,
                "Row includes impression denominator.",
                "Every row needs impression_count > 0 for normalization.",
            )
        )
    return checks


def _has_downstream_signal(rows: list[Any]) -> bool:
    for row in rows:
        if not isinstance(row, dict):
            continue
        if _int_value(row.get("reply_count"), default=0) > 0:
            return True
        if _int_value(row.get("bookmark_count"), default=0) > 0:
            return True
        if _int_value(row.get("click_count"), default=0) > 0:
            return True
        if _int_value(row.get("follower_delta"), default=0) > 0:
            return True
        if row.get("downstream_signal") in {"weak", "strong"}:
            return True
    return False


def _has_qualitative_review(rows: list[Any]) -> bool:
    if not rows:
        return False
    for row in rows:
        if not isinstance(row, dict):
            return False
        review = row.get("qualitative_review")
        if not isinstance(review, dict):
            return False
        for field in REQUIRED_QUALITATIVE_FIELDS:
            if review.get(field) not in {"pass", "mixed", "fail"}:
                return False
    return True


def _append_check(
    checks: list[dict[str, str]],
    check_id: str,
    passed: bool,
    pass_message: str,
    fail_message: str,
) -> None:
    checks.append(_check(check_id, passed, pass_message, fail_message))


def _check(
    check_id: str,
    passed: bool,
    pass_message: str,
    fail_message: str,
) -> dict[str, str]:
    return {
        "check_id": check_id,
        "status": "pass" if passed else "fail",
        "message": pass_message if passed else fail_message,
    }


def _distinct(rows: list[Any], field: str) -> set[str]:
    return {
        str(row.get(field))
        for row in rows
        if isinstance(row, dict) and str(row.get(field) or "").strip()
    }


def _has_all(value: Any, required: tuple[str, ...]) -> bool:
    if not isinstance(value, list):
        return False
    return set(required).issubset({str(item) for item in value})


def _int_value(value: Any, *, default: int) -> int:
    if isinstance(value, bool):
        return default
    return value if isinstance(value, int) else default


def _next_actions(verdict: str) -> list[str]:
    if verdict == "supports_calibration":
        return [
            "Use this as calibration support only, not real virality proof.",
            "Keep network absorption blocked until review, privacy, rollback, and publication gates pass.",
        ]
    return [
        "Collect more real content outcome rows with denominator and downstream signals.",
        "Add qualitative review before trusting simulator or provider-judge reliability.",
        "Mark the calibration claim inconclusive while blockers remain.",
    ]
