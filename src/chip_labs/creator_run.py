"""Creator-run scaffolding and validation.

This module turns the adaptive creator-loop docs into a small executable
contract. It does not run benchmarks yet; it checks whether a creator run has
enough structure and saved evidence to move to the next gate.
"""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

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

TEMPLATE_FILENAMES = {
    "creator-intent.template.json": "creator-intent.json",
    "adapter-map.template.json": "adapter-map.json",
    "creator-run-summary.template.md": "creator-run-summary.md",
    "swarm-contribution-packet.template.json": "swarm-contribution-packet.json",
    "standard-change-proposal.template.md": "standard-change-proposal.md",
}

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

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_dir": self.run_dir,
            "verdict": self.verdict,
            "evidence_tier": self.evidence_tier,
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


def validate_creator_run(run_dir: str | Path) -> SmokeResult:
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
        _check_elevated_evidence(run_path, evidence_tier, checks)
        blocking_failures = [check for check in checks if check.status == "fail"]
    if not swarm_missing and evidence_tier in TRANSFER_EVIDENCE_TIERS:
        _check_transfer_evidence(run_path, evidence_tier, checks)
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


def _nested(data: dict[str, Any], *keys: str) -> Any:
    current: Any = data
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current
