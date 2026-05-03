"""Creator-run scaffolding and validation.

This module turns the adaptive creator-loop docs into a small executable
contract. It does not run benchmarks yet; it checks whether a creator run has
enough structure and saved evidence to move to the next gate.
"""

from __future__ import annotations

import json
import re
import shutil
import hashlib
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Iterable

EVIDENCE_TIERS = (
    "prototype",
    "benchmark_signal",
    "focused_pattern",
    "candidate_review",
    "transfer_supported",
    "network_absorbable",
    "standard_update",
)

ELEVATED_EVIDENCE_TIERS = (
    "candidate_review",
    "transfer_supported",
    "network_absorbable",
    "standard_update",
)

TRANSFER_EVIDENCE_TIERS = (
    "transfer_supported",
    "network_absorbable",
    "standard_update",
)

BROAD_TRANSFER_BLOCKING_TIERS = (
    "network_absorbable",
    "standard_update",
)

EVIDENCE_TIER_RANK = {tier: index for index, tier in enumerate(EVIDENCE_TIERS)}

EVIDENCE_LADDER_PATH = "reports/evidence_ladder.md"
ARTIFACT_MANIFEST_PATH = "created-artifact-manifest.json"
ARTIFACT_MANIFEST_STATUSES = {
    "planned",
    "created",
    "validated",
    "blocked",
    "published",
}
ARTIFACT_MANIFEST_KINDS = {
    "domain_chip",
    "specialization_path",
    "benchmark_pack",
    "autoloop_policy",
    "swarm_packet",
}

TEMPLATE_FILENAMES = {
    "creator-intent.template.json": "creator-intent.json",
    "adapter-map.template.json": "adapter-map.json",
    "created-artifact-manifest.template.json": "created-artifact-manifest.json",
    "creator-run-summary.template.md": "creator-run-summary.md",
    "swarm-contribution-packet.template.json": "swarm-contribution-packet.json",
    "standard-change-proposal.template.md": "standard-change-proposal.md",
}

TEMPLATE_REQUIRED_FILES = (
    "creator-intent.template.json",
    "adapter-map.template.json",
    "autoloop-policy.template.json",
    "benchmark-pack.template.md",
    "created-artifact-manifest.template.json",
    "creator-run-summary.template.md",
    "evidence-ladder.template.md",
    "specialization-path-contract.template.md",
    "swarm-contribution-packet.template.json",
    "standard-change-proposal.template.md",
    "README.md",
)

READY_FOR_BASELINE_PATHS = (
    "domain-chip/chip.manifest.json",
    "domain-chip/doctrine.md",
    "domain-chip/scoring_hooks.json",
    "specialization-path/path.manifest.json",
    "specialization-path/absorption_bundle.md",
    "benchmark/manifest.json",
    "benchmark/cases.jsonl",
    "benchmark/scoring_rubric.md",
    "benchmark/traps.jsonl",
    "autoloop/policy.json",
    "autoloop/mutation_surface.md",
    "autoloop/stop_conditions.md",
)

READY_FOR_SWARM_PATHS = (
    "reports/baseline.json",
    "reports/candidate.json",
    "reports/absorption_summary.json",
    "reports/creator_run_summary.md",
    "swarm/contribution_packet.json",
)

TEMPLATE_REQUIRED_FIELDS = {
    "creator-intent.template.json": (
        "schema_version",
        "run_id",
        "domain.name",
        "domain.short_slug",
        "goal.plain_language_goal",
        "constraints.privacy_boundary",
        "success_criteria.minimum_evidence_tier",
    ),
    "adapter-map.template.json": (
        "schema_version",
        "run_id",
        "domain_adapter",
        "benchmark_adapter",
        "tool_adapter",
        "autoloop_adapter",
        "absorption_adapter",
        "swarm_adapter",
        "swarm_adapter.evidence_tier",
    ),
    "swarm-contribution-packet.template.json": (
        "schema_version",
        "creator_run_id",
        "source",
        "contribution",
        "evidence",
        "governance.rollback_or_deprecation_rule",
        "anti_drift.known_limits",
    ),
    "autoloop-policy.template.json": (
        "schema_version",
        "loop_key",
        "target_capability",
        "evidence_tier_goal",
        "mutation_surface",
        "benchmark_manifest",
        "keep_condition",
        "rollback_condition",
        "promotion_condition",
        "lineage_required",
        "privacy_boundary",
        "network_publication_allowed",
    ),
    "created-artifact-manifest.template.json": (
        "schema_version",
        "creator_run_id",
        "artifacts",
        "publication_boundary",
        "next_action",
    ),
}

TEMPLATE_REQUIRED_TEXT_FILES = (
    "benchmark-pack.template.md",
    "creator-run-summary.template.md",
    "evidence-ladder.template.md",
    "specialization-path-contract.template.md",
    "standard-change-proposal.template.md",
    "README.md",
)


@dataclass(frozen=True)
class SmokeCheck:
    """One smoke-check result."""

    name: str
    status: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {
            "name": self.name,
            "status": self.status,
            "message": self.message,
        }


@dataclass(frozen=True)
class SmokeResult:
    """Creator-run smoke validation result."""

    run_dir: str
    verdict: str
    evidence_tier: str
    checks: tuple[SmokeCheck, ...]
    missing_paths: tuple[str, ...]
    next_actions: tuple[str, ...]
    evidence_mode: str = "saved"

    def to_dict(self) -> dict[str, Any]:
        status_counts = _status_counts(self.checks)
        blocking_checks = _check_names_by_status(self.checks, "fail")
        warning_checks = _check_names_by_status(self.checks, "warn")
        return {
            "schema_version": "adaptive_creator_loop.smoke_result.v1",
            "run_dir": self.run_dir,
            "verdict": self.verdict,
            "evidence_tier": self.evidence_tier,
            "evidence_mode": self.evidence_mode,
            "status_counts": status_counts,
            "blocking_checks": blocking_checks,
            "warning_checks": warning_checks,
            "automation": {
                "blocked": self.verdict == "blocked",
                "ci_exit_code": 1 if self.verdict == "blocked" else 0,
                "recommended_next_command": _recommended_next_command(self),
            },
            "checks": [check.to_dict() for check in self.checks],
            "missing_paths": list(self.missing_paths),
            "next_actions": list(self.next_actions),
        }


def repo_root() -> Path:
    """Return the repo root when running from a source checkout."""

    return Path(__file__).resolve().parents[2]


def default_template_dir() -> Path:
    """Return the creator-run template directory."""

    return repo_root() / "docs" / "creator_system" / "templates" / "creator-run"


def load_json(path: Path) -> dict[str, Any]:
    """Load a JSON object from disk."""

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path} is not valid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def write_json(path: Path, data: dict[str, Any]) -> None:
    """Write formatted JSON."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def creator_run_id(domain_slug: str, today: date | None = None) -> str:
    """Build a stable creator-run id."""

    current_date = today or date.today()
    clean_slug = domain_slug.strip().lower().replace("_", "-").replace(" ", "-")
    clean_slug = "-".join(part for part in clean_slug.split("-") if part)
    if not clean_slug:
        clean_slug = "domain"
    return f"creator-run-{current_date.isoformat()}-{clean_slug}"


def init_creator_run(
    output_dir: str | Path,
    *,
    domain: str,
    goal: str,
    requested_by: str = "",
    source_channel: str = "local",
    template_dir: str | Path | None = None,
    force: bool = False,
) -> dict[str, Any]:
    """Create a creator-run folder from templates."""

    output_path = Path(output_dir)
    source_dir = Path(template_dir) if template_dir else default_template_dir()
    if not source_dir.exists():
        raise FileNotFoundError(
            f"Creator-run template directory not found: {source_dir}"
        )
    if output_path.exists() and any(output_path.iterdir()) and not force:
        raise FileExistsError(f"Output directory is not empty: {output_path}")

    output_path.mkdir(parents=True, exist_ok=True)

    written: list[str] = []
    for template_name, output_name in TEMPLATE_FILENAMES.items():
        source_file = source_dir / template_name
        target_file = output_path / output_name
        shutil.copyfile(source_file, target_file)
        written.append(str(target_file))

    for directory in (
        "domain-chip",
        "specialization-path",
        "benchmark",
        "autoloop",
        "reports",
        "swarm",
    ):
        (output_path / directory).mkdir(exist_ok=True)

    run_id = creator_run_id(domain)
    intent_path = output_path / "creator-intent.json"
    intent = load_json(intent_path)
    intent["run_id"] = run_id
    intent["created_at"] = date.today().isoformat()
    intent["requested_by"] = requested_by
    intent["source_channel"] = source_channel
    intent["domain"]["name"] = domain
    intent["domain"]["short_slug"] = (
        domain.strip().lower().replace(" ", "-").replace("_", "-")
    )
    intent["goal"]["plain_language_goal"] = goal
    write_json(intent_path, intent)

    adapter_path = output_path / "adapter-map.json"
    adapter_map = load_json(adapter_path)
    adapter_map["run_id"] = run_id
    adapter_map["domain_adapter"]["domain_name"] = domain
    write_json(adapter_path, adapter_map)

    artifact_manifest_path = output_path / "created-artifact-manifest.json"
    artifact_manifest = load_json(artifact_manifest_path)
    artifact_manifest["creator_run_id"] = run_id
    artifact_manifest["repo"]["path"] = str(output_path)
    write_json(artifact_manifest_path, artifact_manifest)

    packet_path = output_path / "swarm-contribution-packet.json"
    packet = load_json(packet_path)
    packet["creator_run_id"] = run_id
    write_json(packet_path, packet)

    return {
        "run_dir": str(output_path),
        "run_id": run_id,
        "written_files": written,
        "next_actions": [
            "Fill adapter-map.json with chosen domain, benchmark, tool, autoloop, absorption, and swarm adapters.",
            "Add the domain-chip, specialization-path, benchmark, and autoloop artifacts.",
            "Run creator-run-smoke before attempting baseline or Swarm packaging.",
        ],
    }


def diagnose_creator_run(run_dir: str | Path, *, recompute: bool = False) -> dict[str, Any]:
    """Return a concise repair plan for a creator-run directory."""

    smoke = validate_creator_run(run_dir, recompute=recompute)
    smoke_payload = smoke.to_dict()
    repair_steps = _repair_steps_for_smoke(smoke)
    quarantine = _quarantine_findings(smoke)
    repair_replay = _repair_replay(smoke, recompute=recompute)
    return {
        "schema_version": "adaptive_creator_loop.doctor_result.v1",
        "run_dir": smoke.run_dir,
        "verdict": smoke.verdict,
        "evidence_tier": smoke.evidence_tier,
        "evidence_mode": "recomputed" if recompute else "saved",
        "summary": _doctor_summary(smoke),
        "publication_ready": smoke.verdict == "ready_for_swarm_packet"
        and not smoke_payload["warning_checks"],
        "workspace_ready": smoke.verdict != "blocked",
        "repair_replay": repair_replay,
        "quarantine": quarantine,
        "repair_steps": repair_steps,
        "repair_calibration": _repair_calibration(
            smoke,
            repair_steps=repair_steps,
            quarantine=quarantine,
            repair_replay=repair_replay,
        ),
        "smoke": smoke_payload,
    }


def validate_creator_templates(
    template_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Validate creator-run templates before shipping the creator contract."""

    template_path = Path(template_dir) if template_dir else default_template_dir()
    checks: list[SmokeCheck] = []
    for template_name in TEMPLATE_REQUIRED_FILES:
        path = template_path / template_name
        if path.exists():
            checks.append(
                SmokeCheck(
                    f"template_exists:{template_name}",
                    "pass",
                    f"{template_name} exists.",
                )
            )
        else:
            checks.append(
                SmokeCheck(
                    f"template_exists:{template_name}",
                    "fail",
                    f"Missing {template_name}.",
                )
            )

    for template_name, required_fields in TEMPLATE_REQUIRED_FIELDS.items():
        data = _load_optional_template_json(
            template_path / template_name, template_name, checks
        )
        if not data:
            continue
        for field_path in required_fields:
            value = _nested_path(data, field_path)
            if _has_template_value(value):
                checks.append(
                    SmokeCheck(
                        f"template_field:{template_name}:{field_path}",
                        "pass",
                        f"{template_name} includes {field_path}.",
                    )
                )
            else:
                checks.append(
                    SmokeCheck(
                        f"template_field:{template_name}:{field_path}",
                        "fail",
                        f"{template_name} must include {field_path}.",
                    )
                )

    for template_name in TEMPLATE_REQUIRED_TEXT_FILES:
        path = template_path / template_name
        if not path.exists():
            checks.append(
                SmokeCheck(
                    f"template_text:{template_name}",
                    "fail",
                    f"Missing {template_name}.",
                )
            )
            continue
        text = path.read_text(encoding="utf-8").strip()
        if text:
            checks.append(
                SmokeCheck(
                    f"template_text:{template_name}",
                    "pass",
                    f"{template_name} has content.",
                )
            )
        else:
            checks.append(
                SmokeCheck(
                    f"template_text:{template_name}",
                    "fail",
                    f"{template_name} must not be empty.",
                )
            )

    status_counts = _status_counts(tuple(checks))
    blocking_checks = _check_names_by_status(tuple(checks), "fail")
    return {
        "schema_version": "adaptive_creator_loop.template_check_result.v1",
        "template_dir": str(template_path),
        "verdict": "blocked" if blocking_checks else "pass",
        "status_counts": status_counts,
        "blocking_checks": blocking_checks,
        "checks": [check.to_dict() for check in checks],
    }


def validate_creator_run(run_dir: str | Path, *, recompute: bool = False) -> SmokeResult:
    """Validate a creator-run directory and return a conservative readiness verdict."""

    run_path = Path(run_dir)
    checks: list[SmokeCheck] = []
    missing_paths: list[str] = []
    evidence_tier = "prototype"

    intent = _load_required_json(
        run_path / "creator-intent.json", "creator_intent", checks
    )
    adapter_map = _load_required_json(
        run_path / "adapter-map.json", "adapter_map", checks
    )
    artifact_manifest = _load_required_json(
        run_path / ARTIFACT_MANIFEST_PATH, "created_artifact_manifest", checks
    )

    if intent:
        _check_schema_prefix(
            intent,
            "adaptive_creator_loop.creator_intent.",
            "creator_intent_schema",
            checks,
        )
        _check_non_empty(
            intent.get("run_id"),
            "creator_intent_run_id",
            "creator-intent.json has a run_id.",
            checks,
        )
        _check_non_empty(
            _nested(intent, "goal", "plain_language_goal"),
            "creator_intent_goal",
            "creator-intent.json names the user goal.",
            checks,
        )

    if adapter_map:
        _check_schema_prefix(
            adapter_map,
            "adaptive_creator_loop.adapter_map.",
            "adapter_map_schema",
            checks,
        )
        evidence_tier = str(
            _nested(adapter_map, "swarm_adapter", "evidence_tier") or "prototype"
        )
        if evidence_tier not in EVIDENCE_TIERS:
            checks.append(
                SmokeCheck(
                    "evidence_tier",
                    "fail",
                    f"Unknown evidence tier '{evidence_tier}'.",
                )
            )
        else:
            checks.append(
                SmokeCheck(
                    "evidence_tier",
                    "pass",
                    f"Evidence tier is '{evidence_tier}'.",
                )
            )
        _check_adapter_sections(adapter_map, checks)

    if artifact_manifest:
        _check_artifact_manifest(artifact_manifest, intent, checks)

    for relative_path in READY_FOR_BASELINE_PATHS:
        if not (run_path / relative_path).exists():
            missing_paths.append(relative_path)

    for relative_path in READY_FOR_SWARM_PATHS:
        if not (run_path / relative_path).exists():
            missing_paths.append(relative_path)

    blocking_failures = [check for check in checks if check.status == "fail"]
    baseline_missing = [
        path for path in READY_FOR_BASELINE_PATHS if path in missing_paths
    ]
    swarm_missing = [path for path in READY_FOR_SWARM_PATHS if path in missing_paths]

    if not swarm_missing and evidence_tier in ELEVATED_EVIDENCE_TIERS:
        _check_evidence_ladder(run_path, evidence_tier, checks)
        _check_elevated_evidence(run_path, evidence_tier, checks)
        blocking_failures = [check for check in checks if check.status == "fail"]
    if not swarm_missing and evidence_tier in TRANSFER_EVIDENCE_TIERS:
        _check_transfer_evidence(run_path, evidence_tier, checks)
        blocking_failures = [check for check in checks if check.status == "fail"]
    if recompute and not swarm_missing:
        _check_recomputed_evidence(run_path, checks)
        blocking_failures = [check for check in checks if check.status == "fail"]

    if blocking_failures:
        verdict = "blocked"
        next_actions = (
            "Fix failed schema, required-field, or evidence-support checks.",
        )
    elif baseline_missing:
        verdict = "prototype"
        next_actions = (
            "Fill the missing domain-chip, specialization-path, benchmark, and autoloop artifacts.",
            "Do not run baseline or claim benchmark evidence until benchmark artifacts exist.",
        )
    elif swarm_missing:
        verdict = "ready_for_baseline"
        next_actions = (
            "Run baseline, candidate, and absorption checks.",
            "Save reports before packaging a Swarm contribution.",
        )
    else:
        verdict = "ready_for_swarm_packet"
        next_actions = (
            "Review provenance, trap status, rollback, and privacy boundary before network publication.",
        )

    return SmokeResult(
        run_dir=str(run_path),
        verdict=verdict,
        evidence_tier=evidence_tier,
        checks=tuple(checks),
        missing_paths=tuple(missing_paths),
        next_actions=next_actions,
        evidence_mode="recomputed" if recompute else "saved",
    )


def _load_required_json(
    path: Path, name: str, checks: list[SmokeCheck]
) -> dict[str, Any] | None:
    if not path.exists():
        checks.append(SmokeCheck(name, "fail", f"Missing {path.name}."))
        return None
    try:
        data = load_json(path)
    except ValueError as exc:
        checks.append(SmokeCheck(name, "fail", str(exc)))
        return None
    checks.append(SmokeCheck(name, "pass", f"Loaded {path.name}."))
    return data


def _status_counts(checks: tuple[SmokeCheck, ...]) -> dict[str, int]:
    counts = {"pass": 0, "warn": 0, "fail": 0}
    for check in checks:
        counts[check.status] = counts.get(check.status, 0) + 1
    return counts


def _check_names_by_status(checks: tuple[SmokeCheck, ...], status: str) -> list[str]:
    return [check.name for check in checks if check.status == status]


def _recommended_next_command(result: SmokeResult) -> str:
    if result.verdict == "blocked":
        return f"python -m chip_labs.cli creator-run-smoke {result.run_dir}"
    if result.verdict == "prototype":
        return "Fill missing artifact paths, then rerun creator-run-smoke."
    if result.verdict == "ready_for_baseline":
        return "Run baseline, candidate, and absorption checks, then rerun creator-run-smoke."
    if result.verdict == "ready_for_swarm_packet":
        return "Review provenance, privacy, rollback, and claim boundaries before publication."
    return f"python -m chip_labs.cli creator-run-smoke {result.run_dir}"


def _repair_steps_for_smoke(smoke: SmokeResult) -> list[dict[str, Any]]:
    checks_by_status = {
        "fail": [check for check in smoke.checks if check.status == "fail"],
        "warn": [check for check in smoke.checks if check.status == "warn"],
    }
    steps: list[dict[str, Any]] = []
    if checks_by_status["fail"]:
        steps.extend(_specific_repair_steps(checks_by_status["fail"]))
    if smoke.missing_paths:
        core_missing = [
            path for path in smoke.missing_paths if path in READY_FOR_BASELINE_PATHS
        ]
        report_missing = [
            path for path in smoke.missing_paths if path in READY_FOR_SWARM_PATHS
        ]
        if core_missing:
            steps.append(
                {
                    "priority": "next",
                    "area": "artifact_scaffold",
                    "title": "Create core creator-run artifacts",
                    "action": "Fill or link the domain chip, specialization path, benchmark, and autoloop artifacts.",
                    "related_checks": [],
                    "paths": core_missing,
                }
            )
        if report_missing:
            steps.append(
                {
                    "priority": "next",
                    "area": "evidence_reports",
                    "title": "Generate benchmark and absorption reports",
                    "action": "Run baseline, candidate, and absorption checks, then save the required report files.",
                    "related_checks": [],
                    "paths": report_missing,
                }
            )
    if checks_by_status["warn"]:
        steps.append(
            {
                "priority": "publication",
                "area": "claim_boundary",
                "title": "Resolve warnings before network publication",
                "action": "Warnings can be acceptable for workspace iteration, but strict publication should clear or explicitly accept them.",
                "related_checks": [check.name for check in checks_by_status["warn"]],
                "paths": [],
            }
        )
    if not steps:
        steps.append(
            {
                "priority": "review",
                "area": "publication",
                "title": "Review publication boundaries",
                "action": "Review provenance, privacy, rollback, trap status, and claim boundaries before publishing to Swarm.",
                "related_checks": [],
                "paths": [],
            }
        )
    return steps


def _specific_repair_steps(failed_checks: list[SmokeCheck]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for check in failed_checks:
        spec = _repair_spec_for_check(check.name)
        group = grouped.setdefault(
            spec["area"],
            {
                "priority": "blocker",
                "area": spec["area"],
                "title": spec["title"],
                "action": spec["action"],
                "related_checks": [],
                "paths": [],
            },
        )
        group["related_checks"].append(check.name)
        group["paths"].extend(spec["paths"])

    steps = list(grouped.values())
    for step in steps:
        step["related_checks"] = _dedupe_strings(step["related_checks"])
        step["paths"] = _dedupe_strings(step["paths"])
    return steps


def _repair_spec_for_check(check_name: str) -> dict[str, Any]:
    if (
        check_name.startswith("report_provenance:")
        or check_name.startswith("recompute_")
        or check_name.startswith("external_recompute_")
    ):
        return {
            "area": "recompute_provenance",
            "title": "Regenerate stale or unsupported saved evidence",
            "action": "Regenerate benchmark reports from current source artifacts, keep supported provenance input hashes, then rerun creator-run-smoke --recompute.",
            "paths": _recompute_repair_paths(check_name),
        }
    if check_name.startswith("swarm_packet_"):
        return {
            "area": "swarm_packet",
            "title": "Repair or quarantine the Swarm contribution packet",
            "action": "Align the packet evidence tier, delta, trap status, provenance, and rollback rule with validated reports before review.",
            "paths": ["swarm/contribution_packet.json"],
        }
    if check_name.startswith("evidence_ladder"):
        return {
            "area": "evidence_ladder",
            "title": "Repair the evidence ladder gates",
            "action": "Update the evidence ladder so claimed tier, weakest supported tier, gate statuses, safe claim, and unsafe claim match saved evidence.",
            "paths": [EVIDENCE_LADDER_PATH],
        }
    if check_name.startswith("broad_transfer"):
        return {
            "area": "broad_transfer",
            "title": "Repair broad-transfer evidence",
            "action": "Rerun or revise the broad-transfer probe until every scenario supports the claimed broad transfer tier.",
            "paths": ["reports/broad_transfer_probe.json"],
        }
    if check_name.startswith("transfer_"):
        return {
            "area": "transfer_evidence",
            "title": "Repair transfer evidence",
            "action": "Regenerate the transfer summary with source, scenario count, positive delta, and matching packet evidence.",
            "paths": ["reports/transfer_summary.json", "swarm/contribution_packet.json"],
        }
    if check_name.startswith("candidate_") or check_name == "baseline_score":
        return {
            "area": "benchmark_evidence",
            "title": "Repair baseline and candidate benchmark evidence",
            "action": "Rerun baseline and candidate scoring so candidate score, mean delta, and packet delta agree.",
            "paths": ["reports/baseline.json", "reports/candidate.json"],
        }
    if check_name.startswith("absorption_") or check_name == "trap_coverage":
        return {
            "area": "absorption_evidence",
            "title": "Repair absorption and trap evidence",
            "action": "Regenerate absorption evidence with all modes present, scored, positive delta, and trap coverage.",
            "paths": ["reports/absorption_summary.json"],
        }
    return {
        "area": "validation",
        "title": "Fix blocking smoke checks",
        "action": "Open the failed check names and repair the referenced schema, field, or evidence artifact before continuing.",
        "paths": [],
    }


def _recompute_repair_paths(check_name: str) -> list[str]:
    if check_name.startswith("report_provenance:"):
        parts = check_name.split(":")
        if len(parts) >= 2:
            return [parts[1]]
    if check_name.startswith("external_recompute_"):
        paths = [
            "reports/baseline.json",
            "reports/candidate.json",
            "reports/absorption_summary.json",
        ]
        if "transfer" in check_name:
            paths.extend(
                ["reports/transfer_summary.json", "swarm/contribution_packet.json"]
            )
        if "broad_transfer" in check_name:
            paths.append("reports/broad_transfer_probe.json")
        return paths
    if "candidate" in check_name:
        return [
            "reports/candidate.json",
            "benchmark/cases.jsonl",
            "domain-chip/scoring_hooks.json",
        ]
    if "baseline" in check_name:
        return [
            "reports/baseline.json",
            "benchmark/cases.jsonl",
            "domain-chip/scoring_hooks.json",
        ]
    if "absorption" in check_name or "trap" in check_name:
        return [
            "reports/absorption_summary.json",
            "benchmark/cases.jsonl",
            "domain-chip/scoring_hooks.json",
        ]
    return [
        "reports/baseline.json",
        "reports/candidate.json",
        "reports/absorption_summary.json",
        "benchmark/cases.jsonl",
        "domain-chip/scoring_hooks.json",
    ]


def _repair_replay(smoke: SmokeResult, *, recompute: bool) -> dict[str, Any]:
    rerun_command = f"python -m chip_labs.cli creator-run-smoke {smoke.run_dir} --recompute --fail-on-blocked"
    return {
        "required": smoke.verdict == "blocked",
        "satisfied": recompute and smoke.verdict != "blocked",
        "fresh_evidence": recompute,
        "command": rerun_command,
        "message": (
            "Repair is proven by a fresh recompute smoke run."
            if recompute and smoke.verdict != "blocked"
            else "Repair advice is not complete until this command passes."
        ),
    }


def _repair_calibration(
    smoke: SmokeResult,
    *,
    repair_steps: list[dict[str, Any]],
    quarantine: list[dict[str, Any]],
    repair_replay: dict[str, Any],
) -> dict[str, Any]:
    blocking_checks = [check.name for check in smoke.checks if check.status == "fail"]
    covered_checks = {
        str(check)
        for step in repair_steps
        for check in step.get("related_checks", [])
    }
    covered_checks.update(
        str(check)
        for finding in quarantine
        for check in finding.get("related_checks", [])
    )
    missing_coverage = [
        check for check in blocking_checks if check not in covered_checks
    ]
    checks = [
        {
            "name": "blocking_checks_have_repair_or_quarantine",
            "status": "pass" if not missing_coverage else "fail",
            "message": (
                "Every blocking check is tied to repair or quarantine guidance."
                if not missing_coverage
                else "Missing repair coverage for: " + ", ".join(missing_coverage)
            ),
        },
        {
            "name": "blocked_runs_require_recompute_replay",
            "status": (
                "pass"
                if (smoke.verdict != "blocked" or repair_replay.get("required") is True)
                else "fail"
            ),
            "message": (
                "Blocked runs require a recompute replay command."
                if smoke.verdict == "blocked"
                else "Run is not blocked; recompute replay is optional."
            ),
        },
    ]
    failed = [check["name"] for check in checks if check["status"] == "fail"]
    return {
        "verdict": "blocked" if failed else "pass",
        "blocking_checks": failed,
        "checks": checks,
        "uncovered_smoke_checks": missing_coverage,
    }


def _quarantine_findings(smoke: SmokeResult) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    failed_names = [check.name for check in smoke.checks if check.status == "fail"]
    stale_checks = [
        name for name in failed_names
        if name.startswith("recompute_")
        or name.startswith("report_provenance:")
        or name.startswith("external_recompute_")
    ]
    packet_checks = [name for name in failed_names if name.startswith("swarm_packet_")]
    if stale_checks:
        findings.append(
            {
                "reason": "saved_evidence_not_replayable",
                "action": "Quarantine saved reports until recompute mode passes from source artifacts.",
                "related_checks": stale_checks,
                "paths": _dedupe_strings(
                    path
                    for check_name in stale_checks
                    for path in _recompute_repair_paths(check_name)
                ),
            }
        )
    if packet_checks:
        findings.append(
            {
                "reason": "unsafe_swarm_packet_claim",
                "action": "Do not promote or publish the contribution packet until its tier and evidence match validated reports.",
                "related_checks": packet_checks,
                "paths": ["swarm/contribution_packet.json"],
            }
        )
    return findings


def _dedupe_strings(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def _doctor_summary(smoke: SmokeResult) -> str:
    if smoke.verdict == "blocked":
        return "Creator run is blocked by failed checks."
    if smoke.verdict == "prototype":
        return "Creator run has intent/adapters and needs core artifacts."
    if smoke.verdict == "ready_for_baseline":
        return "Creator run has core artifacts and needs benchmark/absorption evidence."
    if smoke.verdict == "ready_for_swarm_packet":
        warnings = len(_check_names_by_status(smoke.checks, "warn"))
        if warnings:
            return "Creator run is workspace-ready with warnings; strict publication should resolve warnings first."
        return "Creator run is ready for Swarm packet review."
    return f"Creator run verdict is {smoke.verdict}."


def _load_optional_template_json(
    path: Path, template_name: str, checks: list[SmokeCheck]
) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return load_json(path)
    except ValueError as exc:
        checks.append(SmokeCheck(f"template_json:{template_name}", "fail", str(exc)))
        return None


def _nested_path(data: dict[str, Any], path: str) -> Any:
    return _nested(data, *path.split("."))


def _has_template_value(value: Any) -> bool:
    return value is not None


def _check_schema_prefix(
    data: dict[str, Any],
    expected_prefix: str,
    name: str,
    checks: list[SmokeCheck],
) -> None:
    schema_version = str(data.get("schema_version", ""))
    if schema_version.startswith(expected_prefix):
        checks.append(SmokeCheck(name, "pass", f"Schema version is {schema_version}."))
    else:
        checks.append(
            SmokeCheck(
                name,
                "fail",
                f"Schema version must start with {expected_prefix}; got {schema_version or 'missing'}.",
            )
        )


def _check_non_empty(
    value: Any, name: str, pass_message: str, checks: list[SmokeCheck]
) -> None:
    if isinstance(value, str) and value.strip():
        checks.append(SmokeCheck(name, "pass", pass_message))
        return
    if value:
        checks.append(SmokeCheck(name, "pass", pass_message))
        return
    checks.append(SmokeCheck(name, "fail", f"{name} is required."))


def _check_adapter_sections(
    adapter_map: dict[str, Any], checks: list[SmokeCheck]
) -> None:
    required_sections = (
        "domain_adapter",
        "benchmark_adapter",
        "tool_adapter",
        "autoloop_adapter",
        "absorption_adapter",
        "swarm_adapter",
    )
    for section in required_sections:
        value = adapter_map.get(section)
        if isinstance(value, dict):
            checks.append(
                SmokeCheck(f"{section}_section", "pass", f"{section} exists.")
            )
        else:
            checks.append(
                SmokeCheck(
                    f"{section}_section", "fail", f"{section} must be an object."
                )
            )


def _check_artifact_manifest(
    artifact_manifest: dict[str, Any],
    intent: dict[str, Any] | None,
    checks: list[SmokeCheck],
) -> None:
    _check_schema_prefix(
        artifact_manifest,
        "adaptive_creator_loop.created_artifact_manifest.",
        "created_artifact_manifest_schema",
        checks,
    )

    manifest_run_id = str(artifact_manifest.get("creator_run_id") or "")
    intent_run_id = str((intent or {}).get("run_id") or "")
    if not manifest_run_id:
        checks.append(
            SmokeCheck(
                "created_artifact_manifest_run_id",
                "fail",
                "created-artifact-manifest.json must include creator_run_id.",
            )
        )
    elif intent_run_id and manifest_run_id != intent_run_id:
        checks.append(
            SmokeCheck(
                "created_artifact_manifest_run_id",
                "fail",
                f"created-artifact-manifest.json creator_run_id '{manifest_run_id}' does not match creator-intent run_id '{intent_run_id}'.",
            )
        )
    else:
        checks.append(
            SmokeCheck(
                "created_artifact_manifest_run_id",
                "pass",
                "created-artifact-manifest.json creator_run_id is present and aligned.",
            )
        )

    publication_boundary = str(artifact_manifest.get("publication_boundary") or "")
    if publication_boundary in {"local_only", "github_pr", "swarm_shared"}:
        checks.append(
            SmokeCheck(
                "created_artifact_manifest_publication_boundary",
                "pass",
                f"Artifact manifest publication boundary is {publication_boundary}.",
            )
        )
    else:
        checks.append(
            SmokeCheck(
                "created_artifact_manifest_publication_boundary",
                "fail",
                "Artifact manifest publication_boundary must be local_only, github_pr, or swarm_shared.",
            )
        )

    artifacts = artifact_manifest.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        checks.append(
            SmokeCheck(
                "created_artifact_manifest_artifacts",
                "fail",
                "Artifact manifest must include a non-empty artifacts list.",
            )
        )
        return

    checks.append(
        SmokeCheck(
            "created_artifact_manifest_artifacts",
            "pass",
            f"Artifact manifest declares {len(artifacts)} artifact(s).",
        )
    )

    seen_kinds: set[str] = set()
    invalid_entries: list[str] = []
    for index, artifact in enumerate(artifacts):
        if not isinstance(artifact, dict):
            invalid_entries.append(f"artifact[{index}] is not an object")
            continue
        kind = str(artifact.get("kind") or "")
        path = str(artifact.get("path") or "")
        status = str(artifact.get("status") or "")
        if kind:
            seen_kinds.add(kind)
        if not kind or not path or status not in ARTIFACT_MANIFEST_STATUSES:
            invalid_entries.append(
                f"artifact[{index}] must include kind, path, and valid status"
            )

    if invalid_entries:
        checks.append(
            SmokeCheck(
                "created_artifact_manifest_entries",
                "fail",
                "; ".join(invalid_entries),
            )
        )
    else:
        checks.append(
            SmokeCheck(
                "created_artifact_manifest_entries",
                "pass",
                "Artifact manifest entries include kind, path, and valid status.",
            )
        )

    missing_kinds = sorted(ARTIFACT_MANIFEST_KINDS - seen_kinds)
    if missing_kinds:
        checks.append(
            SmokeCheck(
                "created_artifact_manifest_required_kinds",
                "fail",
                "Artifact manifest is missing required kinds: "
                + ", ".join(missing_kinds),
            )
        )
    else:
        checks.append(
            SmokeCheck(
                "created_artifact_manifest_required_kinds",
                "pass",
                "Artifact manifest includes the required creator artifact kinds.",
            )
        )


def _check_elevated_evidence(
    run_path: Path, evidence_tier: str, checks: list[SmokeCheck]
) -> None:
    baseline = _load_required_json(
        run_path / "reports" / "baseline.json", "baseline_report", checks
    )
    candidate = _load_required_json(
        run_path / "reports" / "candidate.json", "candidate_report", checks
    )
    absorption = _load_required_json(
        run_path / "reports" / "absorption_summary.json", "absorption_report", checks
    )
    packet = _load_required_json(
        run_path / "swarm" / "contribution_packet.json", "swarm_packet", checks
    )

    if not all((baseline, candidate, absorption, packet)):
        return

    baseline_score = _coerce_number(baseline.get("mean_score"))
    candidate_score = _coerce_number(candidate.get("mean_score"))
    candidate_delta = _coerce_number(candidate.get("mean_delta"))
    absorption_delta = _coerce_number(absorption.get("mean_validated_pack_delta"))
    packet_delta = _coerce_number(_nested(packet, "evidence", "mean_delta"))
    packet_trap_regressions = _coerce_number(
        _nested(packet, "evidence", "trap_regressions")
    )

    if baseline_score is None:
        checks.append(
            SmokeCheck(
                "baseline_score",
                "fail",
                "reports/baseline.json must include numeric mean_score.",
            )
        )
    else:
        checks.append(
            SmokeCheck(
                "baseline_score",
                "pass",
                f"Baseline mean_score is {baseline_score:.4f}.",
            )
        )

    if candidate_score is None:
        checks.append(
            SmokeCheck(
                "candidate_score",
                "fail",
                "reports/candidate.json must include numeric mean_score.",
            )
        )
    else:
        checks.append(
            SmokeCheck(
                "candidate_score",
                "pass",
                f"Candidate mean_score is {candidate_score:.4f}.",
            )
        )

    if (
        candidate_delta is None
        and baseline_score is not None
        and candidate_score is not None
    ):
        candidate_delta = candidate_score - baseline_score
        checks.append(
            SmokeCheck(
                "candidate_delta_inferred",
                "pass",
                f"Candidate delta inferred from mean scores is {candidate_delta:.4f}.",
            )
        )

    if candidate_delta is None:
        checks.append(
            SmokeCheck(
                "candidate_delta",
                "fail",
                "reports/candidate.json must include numeric mean_delta.",
            )
        )
    elif candidate_delta > 0:
        checks.append(
            SmokeCheck(
                "candidate_delta",
                "pass",
                f"Candidate mean_delta is positive: {candidate_delta:.4f}.",
            )
        )
    else:
        checks.append(
            SmokeCheck(
                "candidate_delta",
                "fail",
                f"Candidate mean_delta must be positive; got {candidate_delta:.4f}.",
            )
        )

    if (
        baseline_score is not None
        and candidate_score is not None
        and candidate_score <= baseline_score
    ):
        checks.append(
            SmokeCheck(
                "candidate_beats_baseline",
                "fail",
                f"Candidate score must exceed baseline score for {evidence_tier}; got {candidate_score:.4f} <= {baseline_score:.4f}.",
            )
        )
    elif baseline_score is not None and candidate_score is not None:
        checks.append(
            SmokeCheck(
                "candidate_beats_baseline",
                "pass",
                f"Candidate exceeds baseline by {(candidate_score - baseline_score):.4f}.",
            )
        )

    _check_bool(
        absorption.get("all_modes_present"),
        "absorption_all_modes_present",
        "Absorption report has all modes present.",
        checks,
    )
    _check_bool(
        absorption.get("all_modes_scored"),
        "absorption_all_modes_scored",
        "Absorption report has all modes scored.",
        checks,
    )

    if absorption_delta is None:
        checks.append(
            SmokeCheck(
                "absorption_delta",
                "fail",
                "reports/absorption_summary.json must include numeric mean_validated_pack_delta.",
            )
        )
    elif absorption_delta > 0:
        checks.append(
            SmokeCheck(
                "absorption_delta",
                "pass",
                f"Absorption delta is positive: {absorption_delta:.4f}.",
            )
        )
    else:
        checks.append(
            SmokeCheck(
                "absorption_delta",
                "fail",
                f"Absorption delta must be positive; got {absorption_delta:.4f}.",
            )
        )

    trap_count = _coerce_number(absorption.get("trap_band_case_count"))
    if trap_count is None or trap_count <= 0:
        checks.append(
            SmokeCheck(
                "trap_coverage",
                "fail",
                "Absorption report must include positive trap_band_case_count.",
            )
        )
    else:
        checks.append(
            SmokeCheck(
                "trap_coverage",
                "pass",
                f"Trap coverage includes {int(trap_count)} cases.",
            )
        )

    packet_tier = str(_nested(packet, "evidence", "tier") or "")
    if packet_tier == evidence_tier:
        checks.append(
            SmokeCheck(
                "swarm_packet_tier",
                "pass",
                f"Swarm packet tier matches adapter tier: {packet_tier}.",
            )
        )
    else:
        checks.append(
            SmokeCheck(
                "swarm_packet_tier",
                "fail",
                f"Swarm packet tier must match adapter tier {evidence_tier}; got {packet_tier or 'missing'}.",
            )
        )

    if packet_delta is None:
        checks.append(
            SmokeCheck(
                "swarm_packet_delta",
                "fail",
                "Swarm packet evidence must include numeric mean_delta.",
            )
        )
    elif candidate_delta is not None and abs(packet_delta - candidate_delta) <= 0.0001:
        checks.append(
            SmokeCheck(
                "swarm_packet_delta",
                "pass",
                "Swarm packet mean_delta matches candidate report.",
            )
        )
    elif candidate_delta is not None:
        checks.append(
            SmokeCheck(
                "swarm_packet_delta",
                "fail",
                f"Swarm packet mean_delta {packet_delta:.4f} does not match candidate report {candidate_delta:.4f}.",
            )
        )

    if packet_trap_regressions is None:
        checks.append(
            SmokeCheck(
                "swarm_packet_traps",
                "fail",
                "Swarm packet must include numeric trap_regressions.",
            )
        )
    elif packet_trap_regressions <= 0:
        checks.append(
            SmokeCheck(
                "swarm_packet_traps",
                "pass",
                "Swarm packet reports no trap regressions.",
            )
        )
    else:
        checks.append(
            SmokeCheck(
                "swarm_packet_traps",
                "fail",
                f"Swarm packet reports trap regressions: {packet_trap_regressions:g}.",
            )
        )

    _check_non_empty(
        _nested(packet, "source", "commit"),
        "swarm_packet_provenance",
        "Swarm packet includes source commit provenance.",
        checks,
    )
    _check_non_empty(
        _nested(packet, "governance", "rollback_or_deprecation_rule"),
        "swarm_packet_rollback",
        "Swarm packet includes rollback/deprecation rule.",
        checks,
    )


def _check_evidence_ladder(
    run_path: Path, evidence_tier: str, checks: list[SmokeCheck]
) -> None:
    ladder_path = run_path / EVIDENCE_LADDER_PATH
    if not ladder_path.exists():
        checks.append(
            SmokeCheck(
                "evidence_ladder",
                "fail",
                f"Elevated evidence tier '{evidence_tier}' requires {EVIDENCE_LADDER_PATH}.",
            )
        )
        return

    text = ladder_path.read_text(encoding="utf-8")
    checks.append(
        SmokeCheck(
            "evidence_ladder",
            "pass",
            f"Loaded {EVIDENCE_LADDER_PATH}.",
        )
    )

    claimed_tier = _extract_ladder_field(text, "Claimed tier")
    if claimed_tier == evidence_tier:
        checks.append(
            SmokeCheck(
                "evidence_ladder_claimed_tier",
                "pass",
                f"Evidence ladder claimed tier matches adapter tier: {claimed_tier}.",
            )
        )
    else:
        checks.append(
            SmokeCheck(
                "evidence_ladder_claimed_tier",
                "fail",
                f"Evidence ladder claimed tier must match adapter tier {evidence_tier}; got {claimed_tier or 'missing'}.",
            )
        )

    weakest_tier = _extract_ladder_field(text, "Weakest supported tier")
    if weakest_tier not in EVIDENCE_TIER_RANK:
        checks.append(
            SmokeCheck(
                "evidence_ladder_weakest_tier",
                "fail",
                f"Evidence ladder weakest supported tier is invalid: {weakest_tier or 'missing'}.",
            )
        )
    elif EVIDENCE_TIER_RANK[weakest_tier] >= EVIDENCE_TIER_RANK[evidence_tier]:
        checks.append(
            SmokeCheck(
                "evidence_ladder_weakest_tier",
                "pass",
                f"Weakest supported tier '{weakest_tier}' supports claimed tier '{evidence_tier}'.",
            )
        )
    else:
        checks.append(
            SmokeCheck(
                "evidence_ladder_weakest_tier",
                "fail",
                f"Weakest supported tier '{weakest_tier}' does not support claimed tier '{evidence_tier}'.",
            )
        )

    gates = _extract_ladder_gates(text)
    if gates and all(status in {"pass", "warn", "fail"} for status in gates.values()):
        checks.append(
            SmokeCheck(
                "evidence_ladder_gate_statuses",
                "pass",
                "Evidence ladder gates are marked pass, warn, or fail.",
            )
        )
    else:
        checks.append(
            SmokeCheck(
                "evidence_ladder_gate_statuses",
                "fail",
                "Evidence ladder gates must be marked pass, warn, or fail instead of blank.",
            )
        )

    required_gates = [
        "Prototype scaffold",
        "Baseline benchmark",
        "Candidate benchmark",
        "Fresh-agent absorption",
        "Trap/adversarial coverage",
        "Swarm packet consistency",
        "Privacy/provenance/rollback",
    ]
    if evidence_tier in TRANSFER_EVIDENCE_TIERS:
        required_gates.append("Transfer probe")
    if evidence_tier in BROAD_TRANSFER_BLOCKING_TIERS:
        required_gates.append("Broad transfer probe")

    for gate_name in required_gates:
        status = gates.get(_normalize_ladder_gate(gate_name))
        if status == "pass":
            checks.append(
                SmokeCheck(
                    f"evidence_ladder_gate:{_normalize_ladder_gate(gate_name)}",
                    "pass",
                    f"Evidence ladder gate '{gate_name}' passed.",
                )
            )
        else:
            checks.append(
                SmokeCheck(
                    f"evidence_ladder_gate:{_normalize_ladder_gate(gate_name)}",
                    "fail",
                    f"Evidence ladder gate '{gate_name}' must be marked pass for {evidence_tier}; got {status or 'missing'}.",
                )
            )

    _check_ladder_claim_section(text, "Safe Claim", "evidence_ladder_safe_claim", checks)
    _check_ladder_claim_section(
        text, "Unsafe Claim", "evidence_ladder_unsafe_claim", checks
    )


def _check_transfer_evidence(
    run_path: Path, evidence_tier: str, checks: list[SmokeCheck]
) -> None:
    transfer = _load_required_json(
        run_path / "reports" / "transfer_summary.json", "transfer_report", checks
    )
    packet = _load_required_json(
        run_path / "swarm" / "contribution_packet.json", "swarm_packet_transfer", checks
    )
    if not transfer or not packet:
        return

    source = str(transfer.get("source") or "")
    if source:
        checks.append(
            SmokeCheck("transfer_source", "pass", f"Transfer source is {source}.")
        )
    else:
        checks.append(
            SmokeCheck(
                "transfer_source",
                "fail",
                "Transfer report must name a source benchmark or simulator.",
            )
        )

    scenario_count = _coerce_number(transfer.get("scenario_count"))
    if scenario_count is None or scenario_count <= 0:
        checks.append(
            SmokeCheck(
                "transfer_scenario_count",
                "fail",
                "Transfer report must include positive scenario_count.",
            )
        )
    else:
        checks.append(
            SmokeCheck(
                "transfer_scenario_count",
                "pass",
                f"Transfer report covers {int(scenario_count)} scenario(s).",
            )
        )

    transfer_score = _coerce_number(transfer.get("transfer_score"))
    baseline_score = _coerce_number(transfer.get("baseline_score"))
    transfer_delta = _coerce_number(transfer.get("delta"))
    if transfer_score is None:
        checks.append(
            SmokeCheck(
                "transfer_score",
                "fail",
                "Transfer report must include numeric transfer_score.",
            )
        )
    else:
        checks.append(
            SmokeCheck(
                "transfer_score", "pass", f"Transfer score is {transfer_score:.4f}."
            )
        )
    if baseline_score is None:
        checks.append(
            SmokeCheck(
                "transfer_baseline_score",
                "fail",
                "Transfer report must include numeric baseline_score.",
            )
        )
    else:
        checks.append(
            SmokeCheck(
                "transfer_baseline_score",
                "pass",
                f"Transfer baseline score is {baseline_score:.4f}.",
            )
        )
    if (
        transfer_delta is None
        and transfer_score is not None
        and baseline_score is not None
    ):
        transfer_delta = transfer_score - baseline_score
        checks.append(
            SmokeCheck(
                "transfer_delta_inferred",
                "pass",
                f"Transfer delta inferred as {transfer_delta:.4f}.",
            )
        )
    if transfer_delta is None:
        checks.append(
            SmokeCheck(
                "transfer_delta", "fail", "Transfer report must include numeric delta."
            )
        )
    elif transfer_delta > 0:
        checks.append(
            SmokeCheck(
                "transfer_delta",
                "pass",
                f"Transfer delta is positive: {transfer_delta:.4f}.",
            )
        )
    else:
        checks.append(
            SmokeCheck(
                "transfer_delta",
                "fail",
                f"Transfer delta must be positive; got {transfer_delta:.4f}.",
            )
        )

    _check_bool(
        transfer.get("constraints_passed"),
        "transfer_constraints_passed",
        "Transfer run passed constraints.",
        checks,
    )

    packet_transfer = _nested(packet, "evidence", "simulator_or_arena_result")
    if not isinstance(packet_transfer, dict):
        checks.append(
            SmokeCheck(
                "swarm_packet_transfer_result",
                "fail",
                "Swarm packet evidence must include simulator_or_arena_result for transfer-supported tiers.",
            )
        )
        return

    packet_transfer_delta = _coerce_number(packet_transfer.get("delta"))
    if packet_transfer_delta is None:
        checks.append(
            SmokeCheck(
                "swarm_packet_transfer_delta",
                "fail",
                "Swarm packet transfer result must include numeric delta.",
            )
        )
    elif (
        transfer_delta is not None
        and abs(packet_transfer_delta - transfer_delta) <= 0.0001
    ):
        checks.append(
            SmokeCheck(
                "swarm_packet_transfer_delta",
                "pass",
                "Swarm packet transfer delta matches transfer report.",
            )
        )
    elif transfer_delta is not None:
        checks.append(
            SmokeCheck(
                "swarm_packet_transfer_delta",
                "fail",
                f"Swarm packet transfer delta {packet_transfer_delta:.4f} does not match transfer report {transfer_delta:.4f}.",
            )
        )

    _check_broad_transfer_probe(run_path, evidence_tier, checks)


def _check_broad_transfer_probe(
    run_path: Path, evidence_tier: str, checks: list[SmokeCheck]
) -> None:
    probe_path = run_path / "reports" / "broad_transfer_probe.json"
    if not probe_path.exists():
        return

    probe = _load_required_json(probe_path, "broad_transfer_probe", checks)
    if not probe:
        return

    source = str(probe.get("source") or "")
    scenario_count = _coerce_number(probe.get("scenario_count"))
    baseline_score = _coerce_number(probe.get("baseline_score"))
    transfer_score = _coerce_number(probe.get("transfer_score"))
    delta = _coerce_number(probe.get("delta"))
    min_delta = _coerce_number(probe.get("min_delta"))
    negative_scenarios = _coerce_number(probe.get("negative_scenarios"))
    verdict = str(probe.get("verdict") or "")

    if source:
        checks.append(
            SmokeCheck(
                "broad_transfer_source", "pass", f"Broad transfer source is {source}."
            )
        )
    else:
        checks.append(
            SmokeCheck(
                "broad_transfer_source",
                "fail",
                "Broad transfer probe must name a source.",
            )
        )

    if scenario_count is None or scenario_count <= 1:
        checks.append(
            SmokeCheck(
                "broad_transfer_scenario_count",
                "fail",
                "Broad transfer probe must cover more than one scenario.",
            )
        )
    else:
        checks.append(
            SmokeCheck(
                "broad_transfer_scenario_count",
                "pass",
                f"Broad transfer probe covers {int(scenario_count)} scenarios.",
            )
        )

    if baseline_score is None:
        checks.append(
            SmokeCheck(
                "broad_transfer_baseline_score",
                "fail",
                "Broad transfer probe must include numeric baseline_score.",
            )
        )
    if transfer_score is None:
        checks.append(
            SmokeCheck(
                "broad_transfer_score",
                "fail",
                "Broad transfer probe must include numeric transfer_score.",
            )
        )
    if delta is None and baseline_score is not None and transfer_score is not None:
        delta = transfer_score - baseline_score
        checks.append(
            SmokeCheck(
                "broad_transfer_delta_inferred",
                "pass",
                f"Broad transfer delta inferred as {delta:.4f}.",
            )
        )
    if delta is None:
        checks.append(
            SmokeCheck(
                "broad_transfer_delta",
                "fail",
                "Broad transfer probe must include numeric delta.",
            )
        )
    elif delta > 0:
        checks.append(
            SmokeCheck(
                "broad_transfer_delta",
                "pass",
                f"Broad transfer probe is positive: {delta:.4f}.",
            )
        )
    elif evidence_tier in BROAD_TRANSFER_BLOCKING_TIERS:
        checks.append(
            SmokeCheck(
                "broad_transfer_delta",
                "fail",
                f"Broad transfer probe is negative ({delta:.4f}); {evidence_tier} cannot absorb or update standards on negative broad transfer.",
            )
        )
    else:
        checks.append(
            SmokeCheck(
                "broad_transfer_delta",
                "warn",
                f"Broad transfer probe is negative ({delta:.4f}); keep the claim focused and defer broad mastery.",
            )
        )

    _check_broad_transfer_row_consistency(
        probe, evidence_tier, scenario_count, min_delta, negative_scenarios, checks
    )

    _check_bool(
        probe.get("constraints_passed"),
        "broad_transfer_constraints_passed",
        "Broad transfer probe passed constraints.",
        checks,
    )

    if verdict:
        checks.append(
            SmokeCheck(
                "broad_transfer_verdict",
                "pass",
                f"Broad transfer verdict is {verdict}.",
            )
        )
    else:
        checks.append(
            SmokeCheck(
                "broad_transfer_verdict",
                "warn",
                "Broad transfer probe should include an explicit verdict.",
            )
        )


def _check_broad_transfer_row_consistency(
    probe: dict[str, Any],
    evidence_tier: str,
    scenario_count: float | None,
    min_delta: float | None,
    negative_scenarios: float | None,
    checks: list[SmokeCheck],
) -> None:
    scenario_results = probe.get("scenario_results")
    if isinstance(scenario_results, list):
        if scenario_count is not None and len(scenario_results) != int(scenario_count):
            checks.append(
                SmokeCheck(
                    "broad_transfer_scenario_results",
                    "fail",
                    f"Broad transfer scenario_results has {len(scenario_results)} rows but scenario_count is {int(scenario_count)}.",
                )
            )
        else:
            checks.append(
                SmokeCheck(
                    "broad_transfer_scenario_results",
                    "pass",
                    f"Broad transfer scenario_results covers {len(scenario_results)} row(s).",
                )
            )
    else:
        checks.append(
            SmokeCheck(
                "broad_transfer_scenario_results",
                "warn",
                "Broad transfer probe should include scenario_results rows for auditability.",
            )
        )

    row_regressions: list[str] = []
    if min_delta is not None and min_delta <= 0:
        row_regressions.append(f"min_delta {min_delta:.4f}")
    if negative_scenarios is not None and negative_scenarios > 0:
        row_regressions.append(f"{int(negative_scenarios)} negative scenario(s)")

    if not row_regressions:
        checks.append(
            SmokeCheck(
                "broad_transfer_no_negative_rows",
                "pass",
                "Broad transfer probe reports no negative scenario rows.",
            )
        )
        return

    message = (
        "Broad transfer probe has mixed rows ("
        + ", ".join(row_regressions)
        + "); keep the claim bounded until weak rows are repaired."
    )
    if evidence_tier in BROAD_TRANSFER_BLOCKING_TIERS:
        checks.append(SmokeCheck("broad_transfer_no_negative_rows", "fail", message))
    else:
        checks.append(SmokeCheck("broad_transfer_no_negative_rows", "warn", message))


def _check_bool(
    value: Any, name: str, pass_message: str, checks: list[SmokeCheck]
) -> None:
    if value is True:
        checks.append(SmokeCheck(name, "pass", pass_message))
    else:
        checks.append(SmokeCheck(name, "fail", f"{name} must be true."))


def _coerce_number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return None
    return None


def _extract_ladder_field(text: str, field_name: str) -> str:
    pattern = re.compile(rf"^{re.escape(field_name)}:\s*([A-Za-z0-9_-]+)", re.MULTILINE)
    match = pattern.search(text)
    return match.group(1).strip() if match else ""


def _extract_ladder_gates(text: str) -> dict[str, str]:
    section_match = re.search(
        r"^## Gate Checklist\s*(.*?)(?=^## |\Z)",
        text,
        flags=re.DOTALL | re.MULTILINE,
    )
    if not section_match:
        return {}
    section = section_match.group(1)
    gates: dict[str, str] = {}
    for line in section.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if len(cells) < 2:
            continue
        gate_name = cells[0]
        status = cells[1].strip("` ").lower()
        if gate_name.lower() in {"gate", "---"} or set(gate_name) <= {"-"}:
            continue
        if set(status) <= {"-"}:
            continue
        gates[_normalize_ladder_gate(gate_name)] = status
    return gates


def _normalize_ladder_gate(gate_name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", gate_name.lower()).strip("_")


def _check_ladder_claim_section(
    text: str, heading: str, check_name: str, checks: list[SmokeCheck]
) -> None:
    pattern = re.compile(rf"^## {re.escape(heading)}\s*(.*?)(?=^## |\Z)", re.DOTALL | re.MULTILINE)
    match = pattern.search(text)
    section = match.group(1) if match else ""
    cleaned = re.sub(r"```[A-Za-z0-9_-]*", "", section).replace("```", "").strip()
    if cleaned:
        checks.append(
            SmokeCheck(check_name, "pass", f"Evidence ladder includes {heading}.")
        )
    else:
        checks.append(
            SmokeCheck(check_name, "fail", f"Evidence ladder must fill {heading}.")
        )


def _nested(data: dict[str, Any], *keys: str) -> Any:
    current: Any = data
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _check_recomputed_evidence(run_path: Path, checks: list[SmokeCheck]) -> None:
    _check_external_transfer_recompute(run_path, checks)
    _check_external_broad_transfer_recompute(run_path, checks)

    report_paths = (
        "reports/baseline.json",
        "reports/candidate.json",
        "reports/absorption_summary.json",
    )
    reports: dict[str, dict[str, Any]] = {}
    for relative_path in report_paths:
        report = _load_required_json(
            run_path / relative_path,
            f"recompute_source:{relative_path}",
            checks,
        )
        if report is None:
            return
        reports[relative_path] = report
        _check_report_provenance(run_path, relative_path, report, checks)

    _check_external_absorption_recompute(run_path, reports, checks)
    _check_external_swarm_packet_recompute(run_path, reports, checks)

    provenance_sources = {
        str(_nested(report, "provenance", "source"))
        for report in reports.values()
        if _nested(report, "provenance", "source")
    }
    if provenance_sources == {"creator_generator_v1"}:
        recomputed = _recompute_creator_generator_reports(run_path, checks)
    elif provenance_sources == {"artifact_quality_v1"}:
        recomputed = _recompute_artifact_quality_reports(run_path, checks)
    elif provenance_sources == {"startup_yc_external_v1"}:
        recomputed = _recompute_startup_yc_external_reports(run_path, reports, checks)
    else:
        checks.append(
            SmokeCheck(
                "recompute_provenance_source",
                "fail",
                "Recompute reports must share one supported provenance source; got "
                + ", ".join(sorted(provenance_sources or {"missing"}))
                + ".",
            )
        )
        return
    if recomputed is None:
        return

    _check_report_number_matches(
        reports["reports/baseline.json"],
        "mean_score",
        recomputed["baseline"]["mean_score"],
        "recompute_baseline_score",
        checks,
    )
    _check_report_number_matches(
        reports["reports/candidate.json"],
        "mean_score",
        recomputed["candidate"]["mean_score"],
        "recompute_candidate_score",
        checks,
    )
    _check_report_number_matches(
        reports["reports/candidate.json"],
        "mean_delta",
        recomputed["candidate"]["mean_delta"],
        "recompute_candidate_delta",
        checks,
    )
    _check_report_number_matches(
        reports["reports/absorption_summary.json"],
        "mean_validated_pack_delta",
        recomputed["absorption"]["mean_validated_pack_delta"],
        "recompute_absorption_delta",
        checks,
    )
    _check_report_number_matches(
        reports["reports/absorption_summary.json"],
        "trap_band_case_count",
        recomputed["absorption"]["trap_band_case_count"],
        "recompute_trap_coverage",
        checks,
    )
    if provenance_sources == {"creator_generator_v1"}:
        _check_report_json_matches(
            reports["reports/candidate.json"],
            "lane_results",
            recomputed["candidate"].get("lane_results", {}),
            "recompute_candidate_lane_results",
            checks,
        )
        _check_report_json_matches(
            reports["reports/absorption_summary.json"],
            "lane_results",
            recomputed["absorption"].get("lane_results", {}),
            "recompute_absorption_lane_results",
            checks,
        )


def _check_report_provenance(
    run_path: Path,
    relative_path: str,
    report: dict[str, Any],
    checks: list[SmokeCheck],
) -> None:
    provenance = report.get("provenance")
    check_prefix = "report_provenance:" + relative_path
    if not isinstance(provenance, dict):
        checks.append(
            SmokeCheck(
                check_prefix,
                "fail",
                f"{relative_path} must include provenance for recompute mode.",
            )
        )
        return
    source = provenance.get("source")
    if source in {
        "creator_generator_v1",
        "artifact_quality_v1",
        "startup_yc_external_v1",
    }:
        checks.append(
            SmokeCheck(
                check_prefix,
                "pass",
                f"{relative_path} declares {source} provenance.",
            )
        )
    else:
        checks.append(
            SmokeCheck(
                check_prefix,
                "fail",
                f"{relative_path} provenance source must be supported for recompute mode.",
            )
        )

    input_hashes = provenance.get("input_hashes")
    if not isinstance(input_hashes, dict) or not input_hashes:
        checks.append(
            SmokeCheck(
                f"{check_prefix}:input_hashes",
                "fail",
                f"{relative_path} provenance must include input_hashes.",
            )
        )
        return

    mismatches: list[str] = []
    for input_relative_path, expected_hash in input_hashes.items():
        input_path = _resolve_external_artifact_path(
            run_path, str(input_relative_path)
        )
        if input_path is None:
            mismatches.append(f"{input_relative_path} missing")
            continue
        actual_hash = _sha256_file(input_path)
        if actual_hash != expected_hash:
            mismatches.append(f"{input_relative_path} hash mismatch")

    if mismatches:
        checks.append(
            SmokeCheck(
                f"{check_prefix}:input_hashes",
                "fail",
                "; ".join(mismatches),
            )
        )
    else:
        checks.append(
            SmokeCheck(
                f"{check_prefix}:input_hashes",
                "pass",
                f"{relative_path} provenance input hashes match current files.",
            )
        )


def _recompute_creator_generator_reports(
    run_path: Path, checks: list[SmokeCheck]
) -> dict[str, dict[str, Any]] | None:
    scoring_hooks_path = run_path / "domain-chip" / "scoring_hooks.json"
    cases_path = run_path / "benchmark" / "cases.jsonl"
    if not scoring_hooks_path.exists() or not cases_path.exists():
        checks.append(
            SmokeCheck(
                "recompute_inputs",
                "fail",
                "Recompute mode requires domain-chip/scoring_hooks.json and benchmark/cases.jsonl.",
            )
        )
        return None

    try:
        scoring_hooks = load_json(scoring_hooks_path)
        cases = _load_jsonl(cases_path)
    except ValueError as exc:
        checks.append(SmokeCheck("recompute_inputs", "fail", str(exc)))
        return None

    if not cases:
        checks.append(
            SmokeCheck(
                "recompute_cases",
                "fail",
                "benchmark/cases.jsonl must include at least one case.",
            )
        )
        return None

    baseline_scores: list[float] = []
    candidate_scores: list[float] = []
    lane_scores: dict[str, dict[str, Any]] = {}
    trap_regressions = 0
    candidate_defaults = scoring_hooks.get("candidate_mutations")
    if not isinstance(candidate_defaults, dict):
        candidate_defaults = {}

    for case in cases:
        if not isinstance(case, dict):
            checks.append(
                SmokeCheck(
                    "recompute_cases",
                    "fail",
                    "Each benchmark case must be a JSON object.",
                )
            )
            return None
        baseline_mutations = case.get("baseline_mutations")
        candidate_mutations = case.get("candidate_mutations")
        if not isinstance(baseline_mutations, dict):
            baseline_mutations = {}
        if not isinstance(candidate_mutations, dict):
            candidate_mutations = dict(candidate_defaults)
        baseline_score = _score_generated_case(scoring_hooks, baseline_mutations)
        candidate_score = _score_generated_case(scoring_hooks, candidate_mutations)
        baseline_scores.append(baseline_score)
        candidate_scores.append(candidate_score)
        lane = str(case.get("case_lane") or "development")
        lane_result = lane_scores.setdefault(
            lane,
            {
                "case_count": 0,
                "baseline_scores": [],
                "candidate_scores": [],
                "trap_regressions": 0,
            },
        )
        lane_result["case_count"] += 1
        lane_result["baseline_scores"].append(baseline_score)
        lane_result["candidate_scores"].append(candidate_score)
        if case.get("trap") is True and candidate_score < baseline_score:
            trap_regressions += 1
            lane_result["trap_regressions"] += 1

    baseline_mean = sum(baseline_scores) / len(baseline_scores)
    candidate_mean = sum(candidate_scores) / len(candidate_scores)
    candidate_delta = candidate_mean - baseline_mean
    trap_case_count = sum(1 for case in cases if case.get("trap") is True)
    lane_results = _generated_lane_results(lane_scores)
    checks.append(
        SmokeCheck(
            "recompute_inputs",
            "pass",
            f"Recomputed reports from {len(cases)} benchmark case(s).",
        )
    )
    return {
        "baseline": {"mean_score": baseline_mean},
        "candidate": {
            "mean_score": candidate_mean,
            "mean_delta": candidate_delta,
            "trap_regressions": trap_regressions,
            "lane_results": lane_results,
        },
        "absorption": {
            "mean_validated_pack_delta": candidate_delta,
            "trap_band_case_count": trap_case_count,
            "lane_results": lane_results,
        },
    }


def _recompute_artifact_quality_reports(
    run_path: Path, checks: list[SmokeCheck]
) -> dict[str, dict[str, Any]] | None:
    try:
        from .artifact_quality import compute_artifact_quality_benchmark

        result = compute_artifact_quality_benchmark(run_path)
    except (FileNotFoundError, ValueError) as exc:
        checks.append(SmokeCheck("recompute_inputs", "fail", str(exc)))
        return None

    checks.append(
        SmokeCheck(
            "recompute_inputs",
            "pass",
            "Recomputed artifact-quality reports from benchmark/artifact_quality_manifest.json.",
        )
    )
    return {
        "baseline": {"mean_score": result["baseline"]["mean_score"]},
        "candidate": {
            "mean_score": result["candidate"]["mean_score"],
            "mean_delta": result["candidate"]["mean_delta"],
            "trap_regressions": result["candidate"]["trap_regressions"],
        },
        "absorption": {
            "mean_validated_pack_delta": result["absorption"]["mean_validated_pack_delta"],
            "trap_band_case_count": result["absorption"]["trap_band_case_count"],
        },
    }


def _recompute_startup_yc_external_reports(
    run_path: Path,
    reports: dict[str, dict[str, Any]],
    checks: list[SmokeCheck],
) -> dict[str, dict[str, Any]] | None:
    baseline = reports["reports/baseline.json"]
    candidate = reports["reports/candidate.json"]
    absorption = reports["reports/absorption_summary.json"]
    source_report_ref = baseline.get("source_report")
    if not isinstance(source_report_ref, str) or not source_report_ref.strip():
        checks.append(
            SmokeCheck(
                "recompute_inputs",
                "fail",
                "Startup YC external recompute requires baseline source_report.",
            )
        )
        return None
    if candidate.get("source_report") != source_report_ref:
        checks.append(
            SmokeCheck(
                "recompute_inputs",
                "fail",
                "Startup YC candidate source_report must match baseline.",
            )
        )
        return None
    if absorption.get("source_report") != source_report_ref:
        checks.append(
            SmokeCheck(
                "recompute_inputs",
                "fail",
                "Startup YC absorption source_report must match baseline.",
            )
        )
        return None

    source_report_path = _resolve_external_artifact_path(run_path, source_report_ref)
    if source_report_path is None:
        checks.append(
            SmokeCheck(
                "recompute_inputs",
                "fail",
                f"Startup YC external source report not found: {source_report_ref}.",
            )
        )
        return None
    try:
        source_report = load_json(source_report_path)
    except ValueError as exc:
        checks.append(SmokeCheck("recompute_inputs", "fail", str(exc)))
        return None

    recomputed = _summarize_startup_yc_absorption_report(source_report)
    if recomputed is None:
        checks.append(
            SmokeCheck(
                "recompute_inputs",
                "fail",
                "Startup YC source report must include absorption summary values.",
            )
        )
        return None

    checks.append(
        SmokeCheck(
            "recompute_inputs",
            "pass",
            f"Recomputed Startup YC reports from {source_report_path}.",
        )
    )
    return {
        "baseline": {"mean_score": recomputed["baseline_score"]},
        "candidate": {
            "mean_score": recomputed["candidate_score"],
            "mean_delta": recomputed["candidate_delta"],
        },
        "absorption": {
            "mean_validated_pack_delta": recomputed["candidate_delta"],
            "trap_band_case_count": recomputed["trap_case_count"],
        },
    }


def _score_generated_case(
    scoring_hooks: dict[str, Any], mutations: dict[str, Any]
) -> float:
    base_score = _coerce_number(scoring_hooks.get("base_score"))
    score = 0.5 if base_score is None else base_score
    mutation_deltas = scoring_hooks.get("mutation_deltas")
    if not isinstance(mutation_deltas, dict):
        mutation_deltas = {}
    for axis, value in mutations.items():
        axis_deltas = mutation_deltas.get(axis)
        if not isinstance(axis_deltas, dict):
            continue
        delta = _coerce_number(axis_deltas.get(value))
        if delta is not None:
            score += delta
    return max(0.0, min(1.0, score))


def _generated_lane_results(
    lane_scores: dict[str, dict[str, Any]]
) -> dict[str, dict[str, Any]]:
    results: dict[str, dict[str, Any]] = {}
    for lane, scores in sorted(lane_scores.items()):
        baseline_scores = scores["baseline_scores"]
        candidate_scores = scores["candidate_scores"]
        baseline_mean = sum(baseline_scores) / len(baseline_scores)
        candidate_mean = sum(candidate_scores) / len(candidate_scores)
        results[lane] = {
            "case_count": scores["case_count"],
            "baseline_mean": round(baseline_mean, 4),
            "candidate_mean": round(candidate_mean, 4),
            "mean_delta": round(candidate_mean - baseline_mean, 4),
            "trap_regressions": scores["trap_regressions"],
        }
    return results


def _check_external_absorption_recompute(
    run_path: Path,
    reports: dict[str, dict[str, Any]],
    checks: list[SmokeCheck],
) -> None:
    baseline = reports["reports/baseline.json"]
    candidate = reports["reports/candidate.json"]
    absorption = reports["reports/absorption_summary.json"]
    source_report_ref = baseline.get("source_report")
    if not isinstance(source_report_ref, str) or not source_report_ref.strip():
        return
    if candidate.get("source_report") != source_report_ref:
        checks.append(
            SmokeCheck(
                "external_recompute_absorption_source",
                "fail",
                "Candidate report source_report must match baseline source_report.",
            )
        )
        return
    if absorption.get("source_report") != source_report_ref:
        checks.append(
            SmokeCheck(
                "external_recompute_absorption_source",
                "fail",
                "Absorption summary source_report must match baseline source_report.",
            )
        )
        return

    source_report_path = _resolve_external_artifact_path(run_path, source_report_ref)
    if source_report_path is None:
        checks.append(
            SmokeCheck(
                "external_recompute_absorption_source",
                "fail",
                f"External absorption source report not found: {source_report_ref}.",
            )
        )
        return

    try:
        source_report = load_json(source_report_path)
    except ValueError as exc:
        checks.append(SmokeCheck("external_recompute_absorption_source", "fail", str(exc)))
        return

    recomputed = _summarize_startup_yc_absorption_report(source_report)
    if recomputed is None:
        checks.append(
            SmokeCheck(
                "external_recompute_absorption_source",
                "fail",
                "Startup YC absorption proof report must include summary values.",
            )
        )
        return

    checks.append(
        SmokeCheck(
            "external_recompute_absorption_source",
            "pass",
            f"Loaded external absorption source report: {source_report_path}.",
        )
    )
    _check_report_number_matches(
        baseline,
        "mean_score",
        recomputed["baseline_score"],
        "external_recompute_absorption_baseline_score",
        checks,
    )
    _check_report_number_matches(
        baseline,
        "pass_rate",
        recomputed["baseline_pass_rate"],
        "external_recompute_absorption_baseline_pass_rate",
        checks,
    )
    _check_report_number_matches(
        baseline,
        "case_count",
        recomputed["case_count"],
        "external_recompute_absorption_baseline_case_count",
        checks,
    )
    _check_report_number_matches(
        candidate,
        "mean_score",
        recomputed["candidate_score"],
        "external_recompute_absorption_candidate_score",
        checks,
    )
    _check_report_number_matches(
        candidate,
        "mean_delta",
        recomputed["candidate_delta"],
        "external_recompute_absorption_candidate_delta",
        checks,
    )
    _check_report_number_matches(
        candidate,
        "pass_rate",
        recomputed["candidate_pass_rate"],
        "external_recompute_absorption_candidate_pass_rate",
        checks,
    )
    _check_report_number_matches(
        candidate,
        "positive_cases",
        recomputed["positive_cases"],
        "external_recompute_absorption_positive_cases",
        checks,
    )
    _check_report_number_matches(
        candidate,
        "negative_cases",
        recomputed["negative_cases"],
        "external_recompute_absorption_negative_cases",
        checks,
    )
    _check_report_number_matches(
        candidate,
        "flat_cases",
        recomputed["flat_cases"],
        "external_recompute_absorption_flat_cases",
        checks,
    )
    _check_report_number_matches(
        absorption,
        "mean_validated_pack_delta",
        recomputed["candidate_delta"],
        "external_recompute_absorption_delta",
        checks,
    )
    _check_report_number_matches(
        absorption,
        "trap_band_case_count",
        recomputed["trap_case_count"],
        "external_recompute_absorption_trap_count",
        checks,
    )

    if (
        absorption.get("all_modes_present") is True
        and recomputed["all_modes_present"] is True
        and absorption.get("all_modes_scored") is True
        and recomputed["all_modes_scored"] is True
    ):
        checks.append(
            SmokeCheck(
                "external_recompute_absorption_modes",
                "pass",
                "External absorption source report confirms all modes are present and scored.",
            )
        )
    else:
        checks.append(
            SmokeCheck(
                "external_recompute_absorption_modes",
                "fail",
                "External absorption source report or saved summary has missing or unscored modes.",
            )
        )


def _check_external_transfer_recompute(
    run_path: Path, checks: list[SmokeCheck]
) -> None:
    transfer_path = run_path / "reports" / "transfer_summary.json"
    if not transfer_path.exists():
        return

    try:
        transfer = load_json(transfer_path)
    except ValueError as exc:
        checks.append(SmokeCheck("external_recompute_transfer", "fail", str(exc)))
        return

    selector_report_ref = _nested(
        transfer, "source_artifacts", "selector_report"
    )
    if not isinstance(selector_report_ref, str) or not selector_report_ref.strip():
        return

    selector_report_path = _resolve_external_artifact_path(
        run_path, selector_report_ref
    )
    if selector_report_path is None:
        checks.append(
            SmokeCheck(
                "external_recompute_transfer_source",
                "fail",
                f"External transfer source report not found: {selector_report_ref}.",
            )
        )
        return

    try:
        selector_report = load_json(selector_report_path)
    except ValueError as exc:
        checks.append(SmokeCheck("external_recompute_transfer_source", "fail", str(exc)))
        return

    recomputed = _summarize_startup_yc_selector_report(selector_report)
    if recomputed is None:
        checks.append(
            SmokeCheck(
                "external_recompute_transfer_source",
                "fail",
                "Startup YC selector report must include scored results.",
            )
        )
        return

    checks.append(
        SmokeCheck(
            "external_recompute_transfer_source",
            "pass",
            f"Loaded external transfer source report: {selector_report_path}.",
        )
    )
    _check_report_number_matches(
        transfer,
        "scenario_count",
        recomputed["scenario_count"],
        "external_recompute_transfer_scenario_count",
        checks,
    )
    _check_report_number_matches(
        transfer,
        "baseline_score",
        recomputed["baseline_score"],
        "external_recompute_transfer_baseline_score",
        checks,
    )
    _check_report_number_matches(
        transfer,
        "transfer_score",
        recomputed["transfer_score"],
        "external_recompute_transfer_score",
        checks,
    )
    _check_report_number_matches(
        transfer,
        "delta",
        recomputed["delta"],
        "external_recompute_transfer_delta",
        checks,
    )
    _check_report_number_matches(
        transfer,
        "min_delta",
        recomputed["min_delta"],
        "external_recompute_transfer_min_delta",
        checks,
    )
    _check_report_number_matches(
        transfer,
        "max_delta",
        recomputed["max_delta"],
        "external_recompute_transfer_max_delta",
        checks,
    )

    constraints_passed = transfer.get("constraints_passed")
    if constraints_passed is True and recomputed["constraints_passed"] is True:
        checks.append(
            SmokeCheck(
                "external_recompute_transfer_constraints",
                "pass",
                "External transfer source report confirms all rows passed constraints.",
            )
        )
    else:
        checks.append(
            SmokeCheck(
                "external_recompute_transfer_constraints",
                "fail",
                "External transfer source report or saved transfer summary has failing constraints.",
            )
    )


def _check_external_swarm_packet_recompute(
    run_path: Path,
    reports: dict[str, dict[str, Any]],
    checks: list[SmokeCheck],
) -> None:
    packet_path = run_path / "swarm" / "contribution_packet.json"
    if not packet_path.exists():
        return
    try:
        packet = load_json(packet_path)
    except ValueError as exc:
        checks.append(SmokeCheck("external_recompute_swarm_packet", "fail", str(exc)))
        return

    baseline = reports["reports/baseline.json"]
    candidate = reports["reports/candidate.json"]
    absorption = reports["reports/absorption_summary.json"]
    transfer_path = run_path / "reports" / "transfer_summary.json"
    transfer: dict[str, Any] = {}
    if transfer_path.exists():
        try:
            transfer = load_json(transfer_path)
        except ValueError as exc:
            checks.append(
                SmokeCheck("external_recompute_swarm_transfer", "fail", str(exc))
            )

    _check_nested_number_matches(
        packet,
        ("evidence", "baseline_score"),
        _coerce_number(baseline.get("mean_score")),
        "external_recompute_swarm_baseline_score",
        checks,
    )
    _check_nested_number_matches(
        packet,
        ("evidence", "candidate_score"),
        _coerce_number(candidate.get("mean_score")),
        "external_recompute_swarm_candidate_score",
        checks,
    )
    _check_nested_number_matches(
        packet,
        ("evidence", "mean_delta"),
        _coerce_number(candidate.get("mean_delta")),
        "external_recompute_swarm_mean_delta",
        checks,
    )
    _check_nested_number_matches(
        packet,
        ("evidence", "fresh_agent_absorption_delta"),
        _coerce_number(absorption.get("mean_validated_pack_delta")),
        "external_recompute_swarm_absorption_delta",
        checks,
    )

    if transfer:
        transfer_fields = (
            ("scenario_count", "external_recompute_swarm_transfer_scenario_count"),
            ("baseline_score", "external_recompute_swarm_transfer_baseline_score"),
            ("transfer_score", "external_recompute_swarm_transfer_score"),
            ("delta", "external_recompute_swarm_transfer_delta"),
            ("min_delta", "external_recompute_swarm_transfer_min_delta"),
            ("max_delta", "external_recompute_swarm_transfer_max_delta"),
        )
        for field, check_name in transfer_fields:
            _check_nested_number_matches(
                packet,
                ("evidence", "simulator_or_arena_result", field),
                _coerce_number(transfer.get(field)),
                check_name,
                checks,
            )
        saved_constraints = _nested(
            packet, "evidence", "simulator_or_arena_result", "constraints_passed"
        )
        if saved_constraints is True and transfer.get("constraints_passed") is True:
            checks.append(
                SmokeCheck(
                    "external_recompute_swarm_transfer_constraints",
                    "pass",
                    "Swarm packet transfer constraints match transfer report.",
                )
            )
        else:
            checks.append(
                SmokeCheck(
                    "external_recompute_swarm_transfer_constraints",
                    "fail",
                    "Swarm packet transfer constraints must match transfer report.",
                )
            )

    report_paths = _nested(packet, "evidence", "report_paths")
    candidate_report_paths = {
        "reports/baseline.json",
        "reports/candidate.json",
        "reports/absorption_summary.json",
        "reports/evidence_ladder.md",
        "reports/transfer_summary.json",
        "reports/broad_transfer_probe.json",
    }
    required_report_paths = {
        relative_path
        for relative_path in candidate_report_paths
        if (run_path / relative_path).exists()
    }
    if isinstance(report_paths, list) and required_report_paths.issubset(
        {str(path) for path in report_paths}
    ):
        checks.append(
            SmokeCheck(
                "external_recompute_swarm_report_paths",
                "pass",
                "Swarm packet report paths cover the recomputed report bundle.",
            )
        )
    else:
        checks.append(
            SmokeCheck(
                "external_recompute_swarm_report_paths",
                "fail",
                "Swarm packet report paths must cover the recomputed report bundle.",
            )
        )

    if _nested(packet, "governance", "network_publication_allowed") is False:
        checks.append(
            SmokeCheck(
                "external_recompute_swarm_publication_boundary",
                "pass",
                "Swarm packet keeps network publication disabled.",
            )
        )
    else:
        checks.append(
            SmokeCheck(
                "external_recompute_swarm_publication_boundary",
                "fail",
                "Swarm packet must keep network publication disabled for Startup YC.",
            )
        )


def _check_external_broad_transfer_recompute(
    run_path: Path, checks: list[SmokeCheck]
) -> None:
    probe_path = run_path / "reports" / "broad_transfer_probe.json"
    if not probe_path.exists():
        return

    try:
        probe = load_json(probe_path)
    except ValueError as exc:
        checks.append(SmokeCheck("external_recompute_broad_transfer", "fail", str(exc)))
        return

    selector_report_ref = _nested(probe, "source_artifacts", "selector_report")
    if not isinstance(selector_report_ref, str) or not selector_report_ref.strip():
        try:
            transfer = load_json(run_path / "reports" / "transfer_summary.json")
        except (FileNotFoundError, ValueError):
            transfer = {}
        selector_report_ref = _nested(
            transfer, "source_artifacts", "selector_report"
        )
    if not isinstance(selector_report_ref, str) or not selector_report_ref.strip():
        return

    selector_report_path = _resolve_external_artifact_path(
        run_path, selector_report_ref
    )
    if selector_report_path is None:
        checks.append(
            SmokeCheck(
                "external_recompute_broad_transfer_source",
                "fail",
                f"External broad-transfer source report not found: {selector_report_ref}.",
            )
        )
        return

    try:
        selector_report = load_json(selector_report_path)
    except ValueError as exc:
        checks.append(
            SmokeCheck("external_recompute_broad_transfer_source", "fail", str(exc))
        )
        return

    recomputed = _summarize_startup_yc_selector_report(selector_report)
    if recomputed is None:
        checks.append(
            SmokeCheck(
                "external_recompute_broad_transfer_source",
                "fail",
                "Startup YC broad-transfer source report must include scored results.",
            )
        )
        return

    checks.append(
        SmokeCheck(
            "external_recompute_broad_transfer_source",
            "pass",
            f"Loaded external broad-transfer source report: {selector_report_path}.",
        )
    )
    _check_report_number_matches(
        probe,
        "scenario_count",
        recomputed["scenario_count"],
        "external_recompute_broad_transfer_scenario_count",
        checks,
    )
    _check_report_number_matches(
        probe,
        "baseline_score",
        recomputed["baseline_score"],
        "external_recompute_broad_transfer_baseline_score",
        checks,
    )
    _check_report_number_matches(
        probe,
        "transfer_score",
        recomputed["transfer_score"],
        "external_recompute_broad_transfer_score",
        checks,
    )
    _check_report_number_matches(
        probe,
        "delta",
        recomputed["delta"],
        "external_recompute_broad_transfer_delta",
        checks,
    )
    _check_report_number_matches(
        probe,
        "min_delta",
        recomputed["min_delta"],
        "external_recompute_broad_transfer_min_delta",
        checks,
    )
    _check_report_number_matches(
        probe,
        "max_delta",
        recomputed["max_delta"],
        "external_recompute_broad_transfer_max_delta",
        checks,
    )
    _check_report_number_matches(
        probe,
        "positive_scenarios",
        recomputed["positive_scenarios"],
        "external_recompute_broad_transfer_positive_scenarios",
        checks,
    )
    _check_report_number_matches(
        probe,
        "negative_scenarios",
        recomputed["negative_scenarios"],
        "external_recompute_broad_transfer_negative_scenarios",
        checks,
    )
    _check_report_number_matches(
        probe,
        "flat_scenarios",
        recomputed["flat_scenarios"],
        "external_recompute_broad_transfer_flat_scenarios",
        checks,
    )
    _check_report_number_matches(
        probe,
        "skipped_scenarios",
        recomputed["skipped_scenarios"],
        "external_recompute_broad_transfer_skipped_scenarios",
        checks,
    )

    if probe.get("constraints_passed") is True and recomputed["constraints_passed"] is True:
        checks.append(
            SmokeCheck(
                "external_recompute_broad_transfer_constraints",
                "pass",
                "External broad-transfer source report confirms all rows passed constraints.",
            )
        )
    else:
        checks.append(
            SmokeCheck(
                "external_recompute_broad_transfer_constraints",
                "fail",
                "External broad-transfer source report or saved probe has failing constraints.",
            )
        )
    _check_broad_transfer_rows(
        probe.get("scenario_results"),
        recomputed["scenario_results"],
        checks,
    )


def _resolve_external_artifact_path(run_path: Path, reference: str) -> Path | None:
    reference_path = Path(reference)
    run_base = run_path.resolve()
    candidates: list[Path] = []
    if reference_path.is_absolute():
        candidates.append(reference_path)
    candidates.append(run_base / reference_path)

    repo_root = _find_repo_root(run_base)
    if repo_root is not None:
        candidates.append(repo_root / reference_path)
        candidates.append(repo_root.parent / reference_path)

    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def _find_repo_root(start: Path) -> Path | None:
    for path in (start, *start.parents):
        if (path / ".git").exists():
            return path
    return None


def _summarize_startup_yc_selector_report(
    selector_report: dict[str, Any]
) -> dict[str, Any] | None:
    results = selector_report.get("results")
    if not isinstance(results, list) or not results:
        return None

    baseline_scores: list[float] = []
    transfer_scores: list[float] = []
    deltas: list[float] = []
    scenario_results: list[dict[str, Any]] = []
    constraints_passed = True
    skipped_scenarios = 0
    for result in results:
        if not isinstance(result, dict):
            return None
        if result.get("status") == "skipped":
            skipped_scenarios += 1
            continue
        baseline_score = _coerce_number(
            _nested(result, "runs", "baseline", "score", "scenario_score")
        )
        transfer_score = _coerce_number(
            _nested(result, "runs", "candidate", "score", "scenario_score")
        )
        delta = _coerce_number(_nested(result, "delta", "scenario_score"))
        if baseline_score is None or transfer_score is None:
            return None
        if delta is None:
            delta = transfer_score - baseline_score
        baseline_scores.append(baseline_score)
        transfer_scores.append(transfer_score)
        deltas.append(delta)
        scenario = _nested(result, "selection", "scenario")
        if not isinstance(scenario, dict):
            scenario = {}
        scenario_results.append(
            {
                "scenario_id": str(
                    scenario.get("scenario_id") or result.get("scenario_id") or ""
                ),
                "track": str(scenario.get("track") or result.get("track") or ""),
                "startup_yc_score": transfer_score,
                "baseline_score": baseline_score,
                "delta": delta,
                "startup_yc_pass_rate": (
                    1
                    if _nested(result, "runs", "candidate", "score", "pass") is True
                    else 0
                ),
                "baseline_pass_rate": (
                    1
                    if _nested(result, "runs", "baseline", "score", "pass") is True
                    else 0
                ),
            }
        )
        constraints_passed = constraints_passed and (
            _nested(result, "runs", "baseline", "score", "pass") is True
            and _nested(result, "runs", "candidate", "score", "pass") is True
            and result.get("status") == "ok"
        )

    if not deltas:
        return None
    scenario_count = float(len(deltas))
    return {
        "scenario_count": scenario_count,
        "baseline_score": sum(baseline_scores) / scenario_count,
        "transfer_score": sum(transfer_scores) / scenario_count,
        "delta": sum(deltas) / scenario_count,
        "min_delta": min(deltas),
        "max_delta": max(deltas),
        "positive_scenarios": float(sum(1 for delta in deltas if delta > 0)),
        "negative_scenarios": float(sum(1 for delta in deltas if delta < 0)),
        "flat_scenarios": float(sum(1 for delta in deltas if delta == 0)),
        "skipped_scenarios": float(skipped_scenarios),
        "scenario_results": scenario_results,
        "constraints_passed": constraints_passed,
    }


def _check_broad_transfer_rows(
    saved_rows: Any, recomputed_rows: Any, checks: list[SmokeCheck]
) -> None:
    if not isinstance(saved_rows, list):
        checks.append(
            SmokeCheck(
                "external_recompute_broad_transfer_rows",
                "fail",
                "Broad-transfer probe must include scenario_results rows.",
            )
        )
        return
    if not isinstance(recomputed_rows, list):
        checks.append(
            SmokeCheck(
                "external_recompute_broad_transfer_rows",
                "fail",
                "External broad-transfer source report did not produce scenario rows.",
            )
        )
        return
    saved_by_id = {
        str(row.get("scenario_id")): row for row in saved_rows if isinstance(row, dict)
    }
    recomputed_by_id = {
        str(row.get("scenario_id")): row
        for row in recomputed_rows
        if isinstance(row, dict)
    }
    if set(saved_by_id) != set(recomputed_by_id):
        checks.append(
            SmokeCheck(
                "external_recompute_broad_transfer_rows",
                "fail",
                "Saved broad-transfer scenario ids do not match external source rows.",
            )
        )
        return

    mismatches: list[str] = []
    fields = (
        "startup_yc_score",
        "baseline_score",
        "delta",
        "startup_yc_pass_rate",
        "baseline_pass_rate",
    )
    for scenario_id, saved in saved_by_id.items():
        recomputed = recomputed_by_id[scenario_id]
        for field in fields:
            saved_number = _coerce_number(saved.get(field))
            recomputed_number = _coerce_number(recomputed.get(field))
            if (
                saved_number is None
                or recomputed_number is None
                or abs(saved_number - recomputed_number) > 0.0001
            ):
                mismatches.append(f"{scenario_id}:{field}")
    if mismatches:
        checks.append(
            SmokeCheck(
                "external_recompute_broad_transfer_rows",
                "fail",
                "Broad-transfer row mismatches: " + ", ".join(mismatches[:5]),
            )
        )
    else:
        checks.append(
            SmokeCheck(
                "external_recompute_broad_transfer_rows",
                "pass",
                f"External broad-transfer source rows match {len(saved_rows)} saved scenario row(s).",
            )
        )


def _check_nested_number_matches(
    data: dict[str, Any],
    keys: tuple[str, ...],
    expected: float | None,
    check_name: str,
    checks: list[SmokeCheck],
) -> None:
    if expected is None:
        checks.append(
            SmokeCheck(check_name, "fail", "Expected recomputed value is missing.")
        )
        return
    actual = _coerce_number(_nested(data, *keys))
    path = ".".join(keys)
    if actual is None:
        checks.append(
            SmokeCheck(check_name, "fail", f"Packet is missing numeric {path}.")
        )
    elif abs(actual - expected) <= 0.0001:
        checks.append(
            SmokeCheck(
                check_name,
                "pass",
                f"Packet {path} matches recomputed value {expected:.4f}.",
            )
        )
    else:
        checks.append(
            SmokeCheck(
                check_name,
                "fail",
                f"Packet {path} {actual:.4f} does not match recomputed value {expected:.4f}.",
            )
        )


def _summarize_startup_yc_absorption_report(
    source_report: dict[str, Any]
) -> dict[str, float | bool] | None:
    summary = source_report.get("summary")
    if not isinstance(summary, dict):
        return None
    score_summary = summary.get("score_summary")
    integrity = summary.get("integrity")
    trap_integrity = summary.get("trap_integrity")
    if (
        not isinstance(score_summary, dict)
        or not isinstance(integrity, dict)
        or not isinstance(trap_integrity, dict)
    ):
        return None
    validated_buckets = score_summary.get("validated_delta_buckets")
    pass_rates = score_summary.get("pass_rates")
    if not isinstance(validated_buckets, dict) or not isinstance(pass_rates, dict):
        return None

    required_numbers = {
        "case_count": summary.get("case_count"),
        "baseline_score": score_summary.get("mean_no_pack_score"),
        "candidate_score": score_summary.get("mean_validated_pack_score"),
        "candidate_delta": score_summary.get("mean_validated_pack_delta"),
        "baseline_pass_rate": pass_rates.get("no_pack"),
        "candidate_pass_rate": pass_rates.get("validated_pack"),
        "positive_cases": validated_buckets.get("positive"),
        "negative_cases": validated_buckets.get("negative"),
        "flat_cases": validated_buckets.get("flat"),
        "trap_case_count": trap_integrity.get("trap_case_count"),
    }
    recomputed: dict[str, float | bool] = {}
    for name, value in required_numbers.items():
        number = _coerce_number(value)
        if number is None:
            return None
        recomputed[name] = number
    recomputed["all_modes_present"] = integrity.get("all_modes_present") is True
    recomputed["all_modes_scored"] = integrity.get("all_modes_scored") is True
    return recomputed


def _check_report_number_matches(
    report: dict[str, Any],
    field: str,
    expected: float,
    check_name: str,
    checks: list[SmokeCheck],
) -> None:
    actual = _coerce_number(report.get(field))
    if actual is None:
        checks.append(
            SmokeCheck(check_name, "fail", f"Report is missing numeric {field}.")
        )
    elif abs(actual - expected) <= 0.0001:
        checks.append(
            SmokeCheck(
                check_name,
                "pass",
                f"Saved {field} matches recomputed value {expected:.4f}.",
            )
        )
    else:
        checks.append(
            SmokeCheck(
                check_name,
                "fail",
                f"Saved {field} {actual:.4f} does not match recomputed value {expected:.4f}.",
            )
        )


def _check_report_json_matches(
    report: dict[str, Any],
    field: str,
    expected: Any,
    check_name: str,
    checks: list[SmokeCheck],
) -> None:
    actual = report.get(field)
    if actual == expected:
        checks.append(
            SmokeCheck(
                check_name,
                "pass",
                f"Saved {field} matches recomputed structured value.",
            )
        )
    else:
        checks.append(
            SmokeCheck(
                check_name,
                "fail",
                f"Saved {field} does not match recomputed structured value.",
            )
        )


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        try:
            row = json.loads(stripped)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path} line {line_number} is not valid JSON: {exc}") from exc
        if not isinstance(row, dict):
            raise ValueError(f"{path} line {line_number} must be a JSON object")
        rows.append(row)
    return rows


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
