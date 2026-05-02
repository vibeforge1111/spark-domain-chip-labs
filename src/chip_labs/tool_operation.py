"""Safe local tool-operation checks for creator-system workflows."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


CLAIM_BOUNDARY = "tool_operation local postcondition check only"

SUPPORTED_OPERATIONS = {
    "creator-run-smoke": {
        "fragments": ("creator-run-smoke",),
        "packet_kind": "adaptive_creator_loop.smoke_result.v1",
        "required_fields": ("verdict", "evidence_mode", "automation", "status_counts"),
        "success_field": "verdict",
        "success_values": ("prototype", "ready_for_baseline", "ready_for_swarm_packet"),
    },
    "creator-run-doctor": {
        "fragments": ("creator-run-doctor",),
        "packet_kind": "adaptive_creator_loop.doctor_result.v1",
        "required_fields": ("smoke", "repair_plan"),
        "success_field": None,
        "success_values": (),
    },
    "creator-run-template-check": {
        "fragments": ("creator-run-template-check",),
        "packet_kind": "adaptive_creator_loop.template_check_result.v1",
        "required_fields": ("verdict", "checks", "status_counts"),
        "success_field": "verdict",
        "success_values": ("pass",),
    },
    "artifact-quality-benchmark": {
        "fragments": ("artifact-quality-benchmark",),
        "packet_kind": "artifact_quality.benchmark_result.v1",
        "required_fields": ("verdict", "baseline", "candidate", "absorption"),
        "success_field": "verdict",
        "success_values": ("pass",),
    },
    "artifact-quality-score": {
        "fragments": ("artifact-quality-score",),
        "packet_kind": "artifact_quality_report",
        "required_fields": ("verdict", "score", "checks"),
        "success_field": "verdict",
        "success_values": ("review_ready", "needs_revision"),
    },
}

PROTECTED_COMMAND_MARKERS = (
    "git push",
    "git reset --hard",
    "rm -rf",
    "remove-item -recurse",
    "publish",
    "network_absorbable",
)

SECRET_MARKERS = (
    "api_key",
    "api key",
    "bearer ",
    "password",
    "paste token",
    "secret",
    "session token",
    ".env",
)


def check_tool_operation(packet: dict[str, Any]) -> dict[str, Any]:
    """Check a local tool operation packet against safe postconditions."""

    command = str(packet.get("command", "")).strip()
    result = packet.get("result")
    exit_code = _coerce_int(packet.get("exit_code"))
    rollback_note = str(packet.get("rollback_note", "")).strip()
    expected_postconditions = packet.get("expected_postconditions")
    operation_key = identify_operation(command)
    operation = SUPPORTED_OPERATIONS.get(operation_key or "")
    checks: list[dict[str, str]] = []

    _append_check(
        checks,
        "command_present",
        bool(command),
        "Command is present.",
        "Operation packet must include command.",
    )
    protected_reason = _protected_reason(command)
    _append_check(
        checks,
        "protected_command",
        protected_reason is None,
        "Command is allowed by the local manifest.",
        protected_reason or "Command is not protected.",
    )
    secret_reason = _secret_reason(packet)
    _append_check(
        checks,
        "secret_boundary",
        secret_reason is None,
        "No secret/token handling request detected.",
        secret_reason or "No secret boundary issue detected.",
    )
    _append_check(
        checks,
        "operation_supported",
        operation is not None,
        f"Operation `{operation_key}` is supported.",
        "Command is not in the local creator-run operation manifest.",
    )
    _append_check(
        checks,
        "parsed_result",
        isinstance(result, dict),
        "Parsed JSON result is present.",
        "Stdout alone is insufficient; provide the parsed JSON result.",
    )

    failed_operation = exit_code not in (None, 0)
    if isinstance(result, dict):
        verdict = str(result.get("verdict", "")).lower()
        failed_operation = failed_operation or verdict in {"blocked", "fail", "failed"}

    if operation and isinstance(result, dict):
        _check_result_shape(operation_key or "", operation, command, result, checks)
    if isinstance(result, dict) and isinstance(expected_postconditions, dict):
        _check_expected_postconditions(expected_postconditions, result, checks)

    rollback_required = failed_operation or any(
        check["status"] == "fail" for check in checks
    )
    _append_check(
        checks,
        "rollback_note",
        (not rollback_required) or bool(rollback_note),
        "Rollback note is present when required.",
        "Failed or blocked operations must include a rollback note.",
    )

    verdict = "pass" if all(check["status"] == "pass" for check in checks) else "blocked"
    blocking_checks = [
        check["name"] for check in checks
        if check["status"] == "fail"
    ]
    return {
        "schema_version": "tool_operation.check_result.v1",
        "operation_key": operation_key,
        "verdict": verdict,
        "allowed": verdict == "pass",
        "claim_boundary": CLAIM_BOUNDARY,
        "checks": checks,
        "blocking_checks": blocking_checks,
        "rollback_note": rollback_note,
        "rollback_report": _rollback_report(
            verdict=verdict,
            rollback_note=rollback_note,
            blocking_checks=blocking_checks,
            operation_key=operation_key,
            result=result if isinstance(result, dict) else None,
        ),
        "next_actions": _next_actions(verdict, operation_key),
    }


def load_tool_operation_packet(path: str | Path) -> dict[str, Any]:
    """Load a tool-operation packet from JSON."""

    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def identify_operation(command: str) -> str | None:
    """Return the supported operation key for a command string."""

    normalized = command.lower()
    for key, operation in SUPPORTED_OPERATIONS.items():
        if all(fragment in normalized for fragment in operation["fragments"]):
            return key
    return None


def default_tool_operation_manifest() -> dict[str, Any]:
    """Return the local safe command manifest."""

    return {
        "schema_version": "tool_operation.manifest.v1",
        "claim_boundary": CLAIM_BOUNDARY,
        "supported_operations": {
            key: {
                "required_fragments": list(operation["fragments"]),
                "packet_kind": operation["packet_kind"],
                "required_fields": list(operation["required_fields"]),
                "success_field": operation["success_field"],
                "success_values": list(operation["success_values"]),
            }
            for key, operation in SUPPORTED_OPERATIONS.items()
        },
        "protected_command_markers": list(PROTECTED_COMMAND_MARKERS),
        "secret_markers": list(SECRET_MARKERS),
    }


def _check_result_shape(
    operation_key: str,
    operation: dict[str, Any],
    command: str,
    result: dict[str, Any],
    checks: list[dict[str, str]],
) -> None:
    expected_packet_kind = str(operation["packet_kind"])
    actual_packet_kind = str(
        result.get("schema_version") or result.get("packet_kind") or ""
    )
    _append_check(
        checks,
        "packet_kind",
        actual_packet_kind == expected_packet_kind,
        f"{operation_key} result has expected packet kind.",
        f"Expected {expected_packet_kind}; got {actual_packet_kind or 'missing'}.",
    )
    missing_fields = [
        field for field in operation["required_fields"]
        if field not in result
    ]
    _append_check(
        checks,
        "required_fields",
        not missing_fields,
        "Required result fields are present.",
        "Missing required result fields: " + ", ".join(missing_fields),
    )
    success_field = operation.get("success_field")
    success_values = set(operation.get("success_values") or ())
    if success_field:
        actual_value = str(result.get(str(success_field), ""))
        _append_check(
            checks,
            "success_value",
            actual_value in success_values,
            f"{success_field} is an allowed success value.",
            f"{success_field} must be one of {sorted(success_values)}; "
            f"got {actual_value or 'missing'}.",
        )
    if operation_key == "creator-run-smoke":
        expected_mode = "recomputed" if "--recompute" in command.lower() else "saved"
        actual_mode = result.get("evidence_mode")
        _append_check(
            checks,
            "evidence_mode",
            actual_mode == expected_mode,
            f"Smoke result evidence_mode matches command mode `{expected_mode}`.",
            f"Expected evidence_mode `{expected_mode}` for this command; "
            f"got `{actual_mode or 'missing'}`.",
        )


def _check_expected_postconditions(
    expected: dict[str, Any],
    result: dict[str, Any],
    checks: list[dict[str, str]],
) -> None:
    expected_verdict = expected.get("verdict")
    if expected_verdict is not None:
        actual_verdict = result.get("verdict")
        _append_check(
            checks,
            "expected_verdict",
            actual_verdict == expected_verdict,
            f"Result verdict matches expected `{expected_verdict}`.",
            f"Expected verdict `{expected_verdict}`; got `{actual_verdict or 'missing'}`.",
        )
    if expected.get("blocking_checks_empty") is True:
        blocking_checks = result.get("blocking_checks")
        _append_check(
            checks,
            "expected_no_blocking_checks",
            blocking_checks == [] or blocking_checks is None,
            "Result has no blocking checks.",
            "Result still has blocking checks: " + ", ".join(blocking_checks or []),
        )
    if expected.get("missing_paths_empty") is True:
        missing_paths = result.get("missing_paths")
        _append_check(
            checks,
            "expected_no_missing_paths",
            missing_paths == [] or missing_paths is None,
            "Result has no missing paths.",
            "Result still has missing paths: " + ", ".join(missing_paths or []),
        )
    if "automation_blocked" in expected:
        actual = _nested(result, "automation", "blocked")
        _append_check(
            checks,
            "expected_automation_blocked",
            actual is expected["automation_blocked"],
            f"automation.blocked matches expected `{expected['automation_blocked']}`.",
            f"Expected automation.blocked `{expected['automation_blocked']}`; got `{actual}`.",
        )


def _protected_reason(command: str) -> str | None:
    normalized = command.lower()
    for marker in PROTECTED_COMMAND_MARKERS:
        if marker in normalized:
            return f"Protected command marker detected: {marker}."
    return None


def _secret_reason(packet: dict[str, Any]) -> str | None:
    inspected = {
        "command": packet.get("command", ""),
        "operator_request": packet.get("operator_request", ""),
        "notes": packet.get("notes", ""),
        "stdout": packet.get("stdout", ""),
        "stderr": packet.get("stderr", ""),
    }
    haystack = json.dumps(inspected, default=str).lower()
    for marker in SECRET_MARKERS:
        if marker in haystack:
            return f"Secret/token marker detected: {marker}."
    return None


def _append_check(
    checks: list[dict[str, str]],
    name: str,
    passed: bool,
    pass_message: str,
    fail_message: str,
) -> None:
    checks.append(
        {
            "name": name,
            "status": "pass" if passed else "fail",
            "message": pass_message if passed else fail_message,
        }
    )


def _next_actions(verdict: str, operation_key: str | None) -> list[str]:
    if verdict == "pass":
        return ["Record the parsed result and postcondition check with the mission trace."]
    actions = [
        "Do not update mission-control state from this operation.",
        "Repair failed checks and rerun the tool-operation check.",
    ]
    if operation_key is None:
        actions.append("Choose a command from the local safe operation manifest.")
    return actions


def _rollback_report(
    *,
    verdict: str,
    rollback_note: str,
    blocking_checks: list[str],
    operation_key: str | None,
    result: dict[str, Any] | None,
) -> dict[str, Any]:
    required = verdict == "blocked"
    return {
        "required": required,
        "provided": bool(rollback_note),
        "note": rollback_note,
        "operation_key": operation_key,
        "blocked_state_update": required,
        "blocking_checks": blocking_checks,
        "result_verdict": result.get("verdict") if result else None,
        "recommendation": (
            "Do not update mission-control state; repair failed checks and rerun."
            if required
            else "Mission trace may record this operation result."
        ),
    }


def _nested(data: dict[str, Any], *keys: str) -> Any:
    current: Any = data
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _coerce_int(value: Any) -> int | None:
    try:
        if value is None:
            return None
        return int(value)
    except (TypeError, ValueError):
        return None
