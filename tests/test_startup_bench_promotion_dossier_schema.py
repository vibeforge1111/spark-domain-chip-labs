from __future__ import annotations

import copy
import json
from pathlib import Path

import jsonschema
import pytest

from chip_labs.startup_bench_promotion_dossier import (
    SCHEMA_VERSION,
    canonicalize_startup_bench_bound_report,
    startup_bench_dossier_blockers,
)


SCHEMA_PATH = Path("docs/creator_system/schemas/startup-bench-promotion-dossier.schema.json")
EXAMPLE_DIR = Path("docs/creator_system/examples/startup-bench-promotion-dossier")
LATEST_BOUND_REPORT = Path(
    "/Users/alchemistab/Documents/Codex/2026-05-09/does-this-spark-update-look-good/"
    "pr-work/specialization-path-spark-qa-operator/.spark-swarm/autoloop/runs/"
    "telegram-20260530t1008274/startup_bench_proof_report.bound.json"
)


def _load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _load_example(name: str) -> dict:
    return json.loads((EXAMPLE_DIR / name).read_text(encoding="utf-8"))


def _validate(packet: dict) -> None:
    jsonschema.Draft202012Validator(_load_schema()).validate(packet)


@pytest.mark.parametrize(
    "example_name",
    [
        "runner-proof-ready-blocked.json",
        "bundle-refresh-required.json",
        "score-claim-ready.json",
        "abandoned-stale-candidate.json",
    ],
)
def test_startup_bench_promotion_dossier_examples_validate(example_name: str) -> None:
    packet = _load_example(example_name)

    _validate(packet)

    assert packet["schemaVersion"] == SCHEMA_VERSION
    assert packet["schema_version"] == SCHEMA_VERSION


def test_positive_private_movement_with_blocked_gates_validates_but_cannot_claim() -> None:
    packet = _load_example("runner-proof-ready-blocked.json")

    _validate(packet)

    comparison = packet["privateScoreSummary"]["comparison"]
    assert comparison["candidateMinusBaseline"] == pytest.approx(0.2249)
    assert comparison["candidateBeatsBaseline"] is True
    assert packet["scoreClaimAllowed"] is False
    assert packet["improvementClaimAllowed"] is False
    assert startup_bench_dossier_blockers(packet) == [
        "sidecar_review_pending",
        "repeated_stability_missing",
        "wall_clock_stability_window_missing",
        "score_reconciliation_missing",
    ]


def test_hidden_heldout_and_wrapper_raw_alone_cannot_validate_as_improved() -> None:
    packet = _load_example("runner-proof-ready-blocked.json")
    packet["status"] = "score_claim_ready"
    packet["scoreClaimAllowed"] = True
    packet["score_claim_allowed"] = True
    packet["improvementClaimAllowed"] = True
    packet["improvement_claim_allowed"] = True
    packet["public_ready"] = True
    packet["publicReady"] = True
    packet["blockers"] = []
    packet["proofGateBundle"]["status"] = "passed"
    packet["promotionDossier"]["status"] = "score_claim_ready"
    packet["promotionDossier"]["scoreClaimAllowed"] = True
    packet["promotionDossier"]["improvementClaimAllowed"] = True
    packet["promotionDossier"]["public_ready"] = True
    packet["promotionDossier"]["blockers"] = []

    with pytest.raises(jsonschema.ValidationError):
        _validate(packet)

    blockers = startup_bench_dossier_blockers(packet)
    assert "score_claim_gate_not_passed:sidecarReview" in blockers
    assert "score_claim_gate_not_passed:repeatedStability" in blockers
    assert "score_claim_gate_not_passed:wallClockStability" in blockers
    assert "score_claim_gate_not_passed:scoreReconciliation" in blockers


def test_score_claim_ready_requires_positive_private_movement() -> None:
    packet = _load_example("score-claim-ready.json")
    packet["privateScoreSummary"]["comparison"]["candidateMinusBaseline"] = 0.0

    with pytest.raises(jsonschema.ValidationError):
        _validate(packet)

    assert (
        "improvement_claim_requires_positive_private_delta"
        in startup_bench_dossier_blockers(packet)
    )


def test_snake_case_and_camel_case_claim_aliases_are_compatible() -> None:
    packet = _load_example("score-claim-ready.json")

    _validate(packet)

    assert packet["scoreClaimAllowed"] is packet["score_claim_allowed"]
    assert packet["improvementClaimAllowed"] is packet["improvement_claim_allowed"]
    assert packet["public_ready"] is packet["publicReady"]
    assert packet["network_absorbable"] is packet["networkAbsorbable"]

    unsafe = copy.deepcopy(packet)
    unsafe["network_absorbable"] = False
    unsafe["networkAbsorbable"] = True
    with pytest.raises(jsonschema.ValidationError):
        _validate(unsafe)


def test_latest_bound_report_maps_explicitly_to_canonical_dossier() -> None:
    if not LATEST_BOUND_REPORT.exists():
        pytest.skip("latest Milestone 1 bound Startup Bench proof report is not present")
    bound_report = json.loads(LATEST_BOUND_REPORT.read_text(encoding="utf-8"))
    packet = canonicalize_startup_bench_bound_report(bound_report)

    _validate(packet)

    assert packet["status"] == "runner_proof_ready"
    assert packet["dossierId"] == "startup-bench-proof-f5689e266af9-473f2bad7e77"
    assert packet["scoreClaimAllowed"] is False
    assert packet["improvementClaimAllowed"] is False
    assert packet["public_ready"] is False
    assert packet["network_absorbable"] is False
    assert packet["privateScoreSummary"]["comparison"]["candidateMinusBaseline"] == pytest.approx(0.2249)
    assert packet["privateScoreSummary"]["comparison"]["candidateBeatsBaseline"] is True
    assert packet["proofGates"]["hiddenHeldout"]["pass"] is True
    assert packet["proofGates"]["wrapperRaw"]["pass"] is True
    assert packet["proofGates"]["sidecarReview"]["pass"] is False
    assert packet["proofGates"]["repeatedStability"]["pass"] is False
    assert packet["proofGates"]["wallClockStability"]["pass"] is False
    assert packet["proofGates"]["scoreReconciliation"]["pass"] is False
    assert packet["blockers"] == [
        "startup_operator_target_hash_mismatch",
        "sidecar_review_pending",
        "repeated_stability_missing",
        "wall_clock_stability_window_missing",
        "score_reconciliation_missing",
    ]
