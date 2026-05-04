"""Provider-adapter manifest checks for MiroFish content simulation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


MANIFEST_SCHEMA_VERSION = "mirofish_content.provider_adapter_manifest.v1"
CHECK_SCHEMA_VERSION = "mirofish_content.provider_adapter_check.v1"
CLAIM_BOUNDARY = (
    "provider adapter contract only; does not call providers or calibrate real outcomes"
)
REQUIRED_RUNTIME_GUARDS = (
    "no_secret_material",
    "no_live_calls_by_default",
    "per_judge_rows",
    "saved_prompt_hashes",
    "outcome_calibration_before_trust",
)
REQUIRED_FORBIDDEN_CLAIMS = (
    "real_virality_proven",
    "calibrated_provider_reliability",
    "network_absorbable",
)


def check_mirofish_provider_adapters(manifest: dict[str, Any]) -> dict[str, Any]:
    """Validate future RLM judge adapter slots without making provider calls."""

    checks: list[dict[str, str]] = []
    judges = manifest.get("rlm_judges")
    judge_rows = judges if isinstance(judges, list) else []
    enabled_judges = [
        judge
        for judge in judge_rows
        if isinstance(judge, dict) and judge.get("enabled") is True
    ]
    output_contract = manifest.get("output_contract")

    _append_check(
        checks,
        "schema_version",
        manifest.get("schema_version") == MANIFEST_SCHEMA_VERSION,
        "Manifest schema version matches.",
        f"Manifest schema_version must be {MANIFEST_SCHEMA_VERSION}.",
    )
    _append_check(
        checks,
        "domain",
        manifest.get("domain") == "MiroFish Content Simulation",
        "Manifest domain is MiroFish Content Simulation.",
        "Manifest domain must be MiroFish Content Simulation.",
    )
    _append_check(
        checks,
        "claim_boundary",
        manifest.get("claim_boundary") == CLAIM_BOUNDARY,
        "Claim boundary preserves provider-adapter limits.",
        "Manifest must state that adapters do not call providers or calibrate real outcomes.",
    )
    _append_check(
        checks,
        "network_calls_disabled",
        manifest.get("network_calls_allowed") is False,
        "Live network calls are disabled.",
        "Provider manifests must keep network_calls_allowed=false in this repo.",
    )
    _append_check(
        checks,
        "credentials_disabled",
        manifest.get("live_credentials_allowed") is False,
        "Live credential material is disabled.",
        "Provider manifests must keep live_credentials_allowed=false.",
    )
    _append_check(
        checks,
        "multi_judge_panel",
        len(enabled_judges) >= 2,
        "At least two enabled judge slots are present.",
        "At least two enabled RLM judge slots are required.",
    )
    _append_check(
        checks,
        "runtime_guards",
        _has_all(manifest.get("required_runtime_guards"), REQUIRED_RUNTIME_GUARDS),
        "Required runtime guards are present.",
        "Manifest must require no secrets, no live calls by default, row-level outputs, prompt hashes, and outcome calibration before trust.",
    )
    _append_check(
        checks,
        "forbidden_claims",
        _has_all(manifest.get("forbidden_claims"), REQUIRED_FORBIDDEN_CLAIMS),
        "Forbidden claims are explicit.",
        "Manifest must forbid real virality, calibrated reliability, and network_absorbable claims.",
    )
    _append_check(
        checks,
        "output_contract",
        isinstance(output_contract, dict)
        and output_contract.get("per_judge_rows") is True
        and output_contract.get("per_persona_rows") is True
        and output_contract.get("aggregate_disagreement_report") is True,
        "Output contract requires row-level judge, persona, and disagreement data.",
        "Output contract must require per-judge rows, per-persona rows, and aggregate disagreement reporting.",
    )
    checks.extend(_judge_checks(judges))

    blocking_checks = [
        check["check_id"] for check in checks if check["status"] == "fail"
    ]
    verdict = "pass" if not blocking_checks else "blocked"
    return {
        "schema_version": CHECK_SCHEMA_VERSION,
        "verdict": verdict,
        "allowed_for_local_simulation": verdict == "pass",
        "network_absorbable": False,
        "claim_boundary": CLAIM_BOUNDARY,
        "judge_count": len(judge_rows),
        "enabled_judge_count": len(enabled_judges),
        "checks": checks,
        "blocking_checks": blocking_checks,
        "next_actions": _next_actions(verdict),
    }


def load_mirofish_provider_adapter_manifest(path: str | Path) -> dict[str, Any]:
    """Load a provider-adapter manifest from JSON."""

    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def _judge_checks(judges: Any) -> list[dict[str, str]]:
    if not isinstance(judges, list):
        return [
            _check(
                "judge_rows",
                False,
                "Judge slots are shaped.",
                "rlm_judges must be a list of judge adapter slots.",
            )
        ]
    checks: list[dict[str, str]] = []
    seen_ids: set[str] = set()
    for index, judge in enumerate(judges, start=1):
        prefix = f"judge_{index}"
        if not isinstance(judge, dict):
            checks.append(
                _check(
                    f"{prefix}_shape",
                    False,
                    "Judge slot is shaped.",
                    "Every RLM judge slot must be a JSON object.",
                )
            )
            continue
        judge_id = str(judge.get("id") or "")
        checks.append(
            _check(
                f"{prefix}_identity",
                bool(judge_id.strip())
                and bool(str(judge.get("provider") or "").strip())
                and bool(str(judge.get("model_family") or "").strip()),
                "Judge identity, provider, and model family are present.",
                "Every judge needs id, provider, and model_family.",
            )
        )
        checks.append(
            _check(
                f"{prefix}_unique_id",
                not judge_id or judge_id not in seen_ids,
                "Judge id is unique.",
                "Judge ids must be unique.",
            )
        )
        seen_ids.add(judge_id)
        checks.append(
            _check(
                f"{prefix}_mode",
                judge.get("mode") in {"deterministic_shadow", "configured_provider"},
                "Judge mode is recognized.",
                "Judge mode must be deterministic_shadow or configured_provider.",
            )
        )
        checks.append(
            _check(
                f"{prefix}_calibration_status",
                judge.get("calibration_status")
                in {"uncalibrated", "shadow_calibrated", "outcome_calibrated"},
                "Judge calibration status is explicit.",
                "Judge calibration_status must be uncalibrated, shadow_calibrated, or outcome_calibrated.",
            )
        )
        if judge.get("calibration_status") == "outcome_calibrated":
            checks.append(
                _check(
                    f"{prefix}_calibration_evidence",
                    bool(str(judge.get("calibration_evidence_ref") or "").strip()),
                    "Outcome-calibrated judge names evidence.",
                    "Outcome-calibrated judge slots must name calibration_evidence_ref.",
                )
            )
    return checks


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


def _has_all(value: Any, required: tuple[str, ...]) -> bool:
    if not isinstance(value, list):
        return False
    return set(required).issubset({str(item) for item in value})


def _next_actions(verdict: str) -> list[str]:
    if verdict == "pass":
        return [
            "Use these adapter slots as local simulation metadata only.",
            "Add real outcome calibration evidence before trusting provider reliability.",
        ]
    return [
        "Repair the provider-adapter manifest before using it in content simulation.",
        "Keep live provider calls, credentials, and network absorption disabled.",
    ]
