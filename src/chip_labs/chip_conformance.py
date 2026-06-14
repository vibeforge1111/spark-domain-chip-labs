"""Read-only Spark chip conformance checks."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


REQUIRED_MANIFEST_KEYS = (
    "manifest_version",
    "schema_version",
    "io_protocol",
    "chip_name",
    "version",
    "domain",
    "description",
    "requires_runtime",
    "capabilities",
    "commands",
    "task_topics",
    "task_keywords",
)
REQUIRED_HOOKS = ("evaluate", "suggest", "packets", "watchtower")
ALLOWED_RUNTIMES = {"spark-intelligence-builder", "spark-harness-core", "spark-cli"}
CHIP_NAME_RE = re.compile(r"^[a-z][a-z0-9-]{1,63}$")
SEMVER_RE = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(-[0-9A-Za-z.-]+)?$")
TASK_TOPIC_RE = re.compile(r"^[a-z0-9][a-z0-9_]*$")
EVIDENCE_PACKET_ID_RE = re.compile(r"^[a-z][a-z0-9_.:-]{2,127}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def validate_chip_conformance(chip_path: str | Path) -> dict[str, Any]:
    """Validate a chip directory without modifying it."""
    root = Path(chip_path)
    checks: list[dict[str, str]] = []

    _add_check(checks, "path.exists", root.exists(), "chip path exists")
    _add_check(checks, "path.directory", root.is_dir(), "chip path is a directory")
    if not root.exists() or not root.is_dir():
        return _report(root, checks)

    manifest = _load_manifest(root, checks)
    if isinstance(manifest, dict):
        _check_manifest_contract(manifest, checks)
    _check_scaffold_shape(root, checks)

    return _report(root, checks)


def _load_manifest(root: Path, checks: list[dict[str, str]]) -> dict[str, Any] | None:
    manifest_path = root / "spark-chip.json"
    _add_check(checks, "manifest.exists", manifest_path.is_file(), "spark-chip.json exists")
    if not manifest_path.is_file():
        return None

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        _add_check(checks, "manifest.valid_json", False, "spark-chip.json is valid JSON")
        return None

    _add_check(checks, "manifest.valid_json", isinstance(manifest, dict), "spark-chip.json is a JSON object")
    return manifest if isinstance(manifest, dict) else None


def _check_manifest_contract(manifest: dict[str, Any], checks: list[dict[str, str]]) -> None:
    missing = [key for key in REQUIRED_MANIFEST_KEYS if key not in manifest]
    _add_check(
        checks,
        "manifest.required_keys",
        not missing,
        "required spark-chip.v2 keys are present",
    )
    _add_check(checks, "manifest.version_const", manifest.get("manifest_version") == 2, "manifest_version is 2")
    _add_check(checks, "manifest.schema_const", manifest.get("schema_version") == "spark-chip.v2", "schema_version is spark-chip.v2")
    _add_check(checks, "manifest.protocol_const", manifest.get("io_protocol") == "spark-hook-io.v1", "io_protocol is spark-hook-io.v1")
    _add_check(checks, "manifest.chip_name", _matches(manifest.get("chip_name"), CHIP_NAME_RE), "chip_name is router-safe")
    _add_check(checks, "manifest.version_semver", _matches(manifest.get("version"), SEMVER_RE), "version is semver-compatible")
    _add_check(checks, "manifest.domain", _non_empty_string(manifest.get("domain")), "domain is non-empty")
    _add_check(checks, "manifest.description", _non_empty_string(manifest.get("description")), "description is non-empty")
    _check_requires_runtime(manifest.get("requires_runtime"), checks)
    _check_capabilities_and_commands(
        manifest.get("capabilities"),
        manifest.get("commands"),
        checks,
    )
    _check_router_metadata("task_topics", manifest.get("task_topics"), checks)
    _check_router_metadata("task_keywords", manifest.get("task_keywords"), checks)
    _check_executed_evidence(manifest.get("executed_evidence"), checks)


def _check_requires_runtime(value: Any, checks: list[dict[str, str]]) -> None:
    is_runtime_map = isinstance(value, dict) and bool(value)
    _add_check(checks, "manifest.requires_runtime.map", is_runtime_map, "requires_runtime is a non-empty object")
    if not isinstance(value, dict):
        return
    unknown = [key for key in value if key not in ALLOWED_RUNTIMES]
    bad_ranges = [key for key, item in value.items() if not _non_empty_string(item)]
    _add_check(checks, "manifest.requires_runtime.names", not unknown, "runtime names are known")
    _add_check(checks, "manifest.requires_runtime.ranges", not bad_ranges, "runtime ranges are non-empty strings")


def _check_capabilities_and_commands(capabilities: Any, commands: Any, checks: list[dict[str, str]]) -> None:
    capability_list = capabilities if isinstance(capabilities, list) else []
    _add_check(
        checks,
        "manifest.capabilities.array",
        isinstance(capabilities, list) and bool(capabilities) and _all_non_empty_strings(capabilities),
        "capabilities is a non-empty string array",
    )
    _add_check(
        checks,
        "manifest.capabilities.unique",
        isinstance(capabilities, list) and len(set(capabilities)) == len(capabilities),
        "capabilities are unique",
    )
    _add_check(
        checks,
        "manifest.capabilities.required_hooks",
        all(hook in capability_list for hook in REQUIRED_HOOKS),
        "canonical hooks are listed as capabilities",
    )
    _add_check(checks, "manifest.commands.map", isinstance(commands, dict) and bool(commands), "commands is a non-empty object")
    if not isinstance(commands, dict):
        return

    for hook in REQUIRED_HOOKS:
        command = commands.get(hook)
        _add_check(
            checks,
            f"manifest.commands.{hook}",
            _argv_command(command),
            f"{hook} command is argv-array form",
        )


def _check_router_metadata(name: str, value: Any, checks: list[dict[str, str]]) -> None:
    is_array = isinstance(value, list) and bool(value) and _all_non_empty_strings(value)
    _add_check(checks, f"manifest.{name}.array", is_array, f"{name} is a non-empty string array")
    if not isinstance(value, list):
        return

    _add_check(checks, f"manifest.{name}.unique", len(set(value)) == len(value), f"{name} entries are unique")
    if name == "task_topics":
        _add_check(
            checks,
            "manifest.task_topics.shape",
            all(isinstance(item, str) and TASK_TOPIC_RE.fullmatch(item) for item in value),
            "task_topics are router tokens",
        )
    else:
        _add_check(
            checks,
            "manifest.task_keywords.length",
            all(isinstance(item, str) and len(item) >= 2 for item in value),
            "task_keywords are at least two characters",
        )


def _check_executed_evidence(value: Any, checks: list[dict[str, str]]) -> None:
    if value is None:
        _add_check(checks, "manifest.executed_evidence.optional", True, "executed_evidence is optional")
        return
    if not isinstance(value, dict):
        _add_check(checks, "manifest.executed_evidence.object", False, "executed_evidence is an object when present")
        return

    allowed = {"packet_id", "packet_schema_version", "path_or_uri", "sha256", "tier_claim", "generated_at"}
    required = {"packet_id", "packet_schema_version", "path_or_uri", "sha256"}
    _add_check(checks, "manifest.executed_evidence.required", required.issubset(value), "executed_evidence required keys are present")
    _add_check(checks, "manifest.executed_evidence.closed", set(value).issubset(allowed), "executed_evidence has only known keys")
    _add_check(checks, "manifest.executed_evidence.packet_id", _matches(value.get("packet_id"), EVIDENCE_PACKET_ID_RE), "executed_evidence packet_id is valid")
    _add_check(
        checks,
        "manifest.executed_evidence.schema",
        value.get("packet_schema_version") == "spark.evidence_scorecard_packet.v1",
        "executed_evidence packet schema is valid",
    )
    _add_check(checks, "manifest.executed_evidence.path", _non_empty_string(value.get("path_or_uri")), "executed_evidence path_or_uri is non-empty")
    _add_check(checks, "manifest.executed_evidence.sha256", _matches(value.get("sha256"), SHA256_RE), "executed_evidence sha256 is valid")


def _check_scaffold_shape(root: Path, checks: list[dict[str, str]]) -> None:
    required_files = (
        "README.md",
        "pyproject.toml",
        "spark-researcher.project.json",
        "docs/ARCHITECTURE.md",
        "docs/SOURCE_REGISTRY.md",
        "docs/MISSION.md",
    )
    missing_files = [item for item in required_files if not (root / item).is_file()]
    _add_check(checks, "scaffold.required_files", not missing_files, "scaffold core files are present")
    _add_check(checks, "scaffold.src", (root / "src").is_dir(), "src directory is present")
    _add_check(checks, "scaffold.tests", (root / "tests").is_dir(), "tests directory is present")


def _report(root: Path, checks: list[dict[str, str]]) -> dict[str, Any]:
    blocking_checks = [check["name"] for check in checks if check["status"] == "fail"]
    return {
        "schema_version": "spark_chip.conformance.v1",
        "chip_path": str(root),
        "read_only": True,
        "verdict": "blocked" if blocking_checks else "pass",
        "blocking_checks": blocking_checks,
        "checks": checks,
    }


def _add_check(checks: list[dict[str, str]], name: str, passed: bool, message: str) -> None:
    checks.append(
        {
            "name": name,
            "status": "pass" if passed else "fail",
            "message": message,
        }
    )


def _argv_command(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and _all_non_empty_strings(value)


def _all_non_empty_strings(value: list[Any]) -> bool:
    return all(_non_empty_string(item) for item in value)


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value)


def _matches(value: Any, pattern: re.Pattern[str]) -> bool:
    return isinstance(value, str) and bool(pattern.fullmatch(value))
