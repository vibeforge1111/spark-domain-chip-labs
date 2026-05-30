from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "spark-startup-bench-promotion-dossier.v1"
ARTIFACT_MANIFEST_SCHEMA_VERSION = (
    "spark-startup-bench-promotion-dossier-artifact-manifest.v1"
)


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _artifact_by_type(report: dict[str, Any], artifact_type: str) -> dict[str, Any] | None:
    for artifact in _as_list(report.get("artifacts")):
        if isinstance(artifact, dict) and artifact.get("artifactType") == artifact_type:
            return artifact
    return None


def _run_id_from_path(path: str | None) -> str:
    if not path:
        return "unknown-startup-bench-run"
    parent = Path(path).parent.name
    return parent or "unknown-startup-bench-run"


def _gate_from_report(value: Any, default_status: str) -> dict[str, Any]:
    gate = deepcopy(_as_dict(value))
    gate.setdefault("status", default_status)
    gate.setdefault("pass", gate.get("status") in {"pass", "passed", "clean", "approved"})
    gate.setdefault("blockers", [])
    gate.setdefault("scoreClaimAllowed", False)
    return gate


def _next_action(next_gate: str, blockers: list[str]) -> str:
    if next_gate == "refresh_startup_bench_proof_gate_bundle":
        return "Regenerate the immutable proof gate bundle before reading promotion state."
    if blockers:
        return (
            "Complete the remaining Startup Bench proof blockers before claiming "
            "score or improvement: "
            + ", ".join(blockers)
            + "."
        )
    return (
        "Show the bounded improvement claim and ask for an explicit keep or "
        "revert decision before exporting a reusable lesson packet."
    )


def canonicalize_startup_bench_bound_report(report: dict[str, Any]) -> dict[str, Any]:
    """Map Spark QA Operator's bound report into the Domain Chip Labs contract."""
    report = deepcopy(report)
    proof_gate_bundle = _as_dict(report.get("proofGateBundle"))
    proof_binding = _as_dict(proof_gate_bundle.get("proofBinding"))
    if not proof_binding:
        proof_binding = _as_dict(report.get("proofBinding"))
    run_signature = _as_dict(proof_binding.get("runSignature"))
    run_payload = _as_dict(run_signature.get("payload"))
    private_score_summary = _as_dict(report.get("privateScoreSummary"))
    promotion_dossier = _as_dict(report.get("promotionDossier"))
    artifacts = [
        deepcopy(artifact)
        for artifact in _as_list(report.get("artifacts"))
        if isinstance(artifact, dict)
    ]
    candidate_lock_artifact = _artifact_by_type(report, "candidate_run_lock") or {}
    blockers = [
        str(blocker)
        for blocker in _as_list(report.get("blockers") or promotion_dossier.get("blockers"))
        if str(blocker)
    ]
    next_gate = str(
        promotion_dossier.get("nextGate")
        or ("refresh_startup_bench_proof_gate_bundle" if report.get("status") == "bundle_refresh_required" else "keep_or_revert_decision")
    )
    proof_report_path = str(proof_binding.get("proofReportPath") or "")
    top_level_public_ready = bool(
        report.get("public_ready", promotion_dossier.get("public_ready", False))
    )
    top_level_network_absorbable = bool(
        report.get("network_absorbable", promotion_dossier.get("network_absorbable", False))
    )
    score_claim_allowed = report.get("scoreClaimAllowed") is True
    improvement_claim_allowed = report.get("improvementClaimAllowed") is True
    schema_status = str(report.get("status") or promotion_dossier.get("status") or "runner_proof_ready")
    if score_claim_allowed and improvement_claim_allowed:
        schema_status = "score_claim_ready"

    proof_gates = _as_dict(report.get("proofGates"))
    canonical = {
        "schemaVersion": SCHEMA_VERSION,
        "schema_version": SCHEMA_VERSION,
        "status": schema_status,
        "dossierId": str(
            proof_gate_bundle.get("bundleId")
            or proof_binding.get("proofReportSha256")
            or "startup-bench-promotion-dossier"
        ),
        "createdAt": str(report.get("generatedAt") or "1970-01-01T00:00:00Z"),
        "generatedAt": str(report.get("generatedAt") or "1970-01-01T00:00:00Z"),
        "runIdentity": {
            "runId": _run_id_from_path(proof_report_path),
            "baselineId": str(run_payload.get("baselineId") or ""),
            "startupBenchRepo": str(run_payload.get("startupBenchRepo") or ""),
            "startupOperatorRepo": str(run_payload.get("startupOperatorRepo") or ""),
            "scenarioPath": str(run_payload.get("scenarioPath") or ""),
            "scenarioSha256": str(run_payload.get("scenarioSha256") or ""),
            "toolCallsPath": str(run_payload.get("toolCallsPath") or ""),
            "toolCallsSha256": str(run_payload.get("toolCallsSha256") or ""),
            "seeds": _as_list(run_payload.get("seeds")) or [1],
            "maxTurns": int(run_payload.get("maxTurns") or 1),
        },
        "proofIdentity": {
            "proofReportPath": proof_report_path,
            "proofReportSha256": str(proof_binding.get("proofReportSha256") or ""),
            "privateScoreSummarySha256": str(
                proof_binding.get("privateScoreSummarySha256") or ""
            ),
            "runSignatureDigest": str(run_signature.get("digest") or ""),
            "proofGateBundleId": str(proof_gate_bundle.get("bundleId") or ""),
        },
        "candidateLock": {
            "lockState": "refresh_required"
            if schema_status == "bundle_refresh_required"
            else "locked",
            "targetKind": "startup_operator_tool_calls",
            "targetPath": str(run_payload.get("toolCallsPath") or ""),
            "targetSha256": str(run_payload.get("toolCallsSha256") or ""),
            "scenarioPath": str(run_payload.get("scenarioPath") or ""),
            "scenarioSha256": str(run_payload.get("scenarioSha256") or ""),
            "artifactRef": candidate_lock_artifact.get("path"),
            "artifactSha256": candidate_lock_artifact.get("sha256"),
            "createdBeforeEvaluation": schema_status != "bundle_refresh_required",
        },
        "proofBinding": proof_binding,
        "proofGateBundle": proof_gate_bundle,
        "privateScoreSummary": private_score_summary,
        "proofGates": {
            "hiddenHeldout": _gate_from_report(proof_gates.get("hiddenHeldout"), "blocked"),
            "wrapperRaw": _gate_from_report(proof_gates.get("wrapperRaw"), "blocked"),
            "sidecarReview": _gate_from_report(proof_gates.get("sidecarReview"), "blocked"),
            "repeatedStability": _gate_from_report(
                report.get("repeatedStability"), "blocked"
            ),
            "wallClockStability": _gate_from_report(
                report.get("wallClockStability"), "blocked"
            ),
            "scoreReconciliation": _gate_from_report(
                proof_gates.get("scoreReconciliation"), "blocked"
            ),
        },
        "promotionDossier": {
            **promotion_dossier,
            "status": "score_claim_ready"
            if score_claim_allowed and improvement_claim_allowed
            else str(promotion_dossier.get("status") or "blocked"),
            "scoreClaimAllowed": score_claim_allowed,
            "improvementClaimAllowed": improvement_claim_allowed,
            "public_ready": top_level_public_ready,
            "network_absorbable": top_level_network_absorbable,
            "blockers": blockers,
        },
        "scoreClaimAllowed": score_claim_allowed,
        "score_claim_allowed": score_claim_allowed,
        "improvementClaimAllowed": improvement_claim_allowed,
        "improvement_claim_allowed": improvement_claim_allowed,
        "public_ready": top_level_public_ready,
        "publicReady": top_level_public_ready,
        "network_absorbable": top_level_network_absorbable,
        "networkAbsorbable": top_level_network_absorbable,
        "blockers": blockers,
        "nextGate": next_gate,
        "nextAction": _next_action(next_gate, blockers),
        "artifacts": artifacts,
        "artifactManifest": {
            "schemaVersion": ARTIFACT_MANIFEST_SCHEMA_VERSION,
            "artifactCount": len(artifacts),
            "artifacts": artifacts,
        },
        "claimBoundary": str(
            report.get("claimBoundary")
            or "Positive private Startup Bench movement is not an improvement claim until the bound proof bundle, sidecar review, stability, and score reconciliation are all clear."
        ),
    }
    canonical["promotionDossier"].setdefault("nextGate", next_gate)
    return canonical


def startup_bench_dossier_blockers(packet: dict[str, Any]) -> list[str]:
    blockers = [str(item) for item in _as_list(packet.get("blockers")) if str(item)]
    gates = _as_dict(packet.get("proofGates"))
    if packet.get("improvementClaimAllowed") is True:
        if packet.get("scoreClaimAllowed") is not True:
            blockers.append("improvement_claim_requires_score_claim")
        comparison = _as_dict(_as_dict(packet.get("privateScoreSummary")).get("comparison"))
        if comparison.get("candidateBeatsBaseline") is not True:
            blockers.append("improvement_claim_requires_candidate_beats_baseline")
        delta = comparison.get("candidateMinusBaseline")
        if not isinstance(delta, (int, float)) or delta <= 0:
            blockers.append("improvement_claim_requires_positive_private_delta")
    if packet.get("scoreClaimAllowed") is True:
        for gate_name in (
            "hiddenHeldout",
            "wrapperRaw",
            "sidecarReview",
            "repeatedStability",
            "wallClockStability",
            "scoreReconciliation",
        ):
            if _as_dict(gates.get(gate_name)).get("pass") is not True:
                blockers.append(f"score_claim_gate_not_passed:{gate_name}")
    return list(dict.fromkeys(blockers))
