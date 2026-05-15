from __future__ import annotations

import copy
import json
from pathlib import Path

import jsonschema
import pytest

from chip_labs.specialization_loop_status import (
    CHECK_SCHEMA_VERSION,
    INSIGHT_CHECK_SCHEMA_VERSION,
    INSIGHT_SCHEMA_VERSION,
    SCHEMA_VERSION,
    build_specialization_loop_insight_packet,
    build_specialization_loop_status,
    check_specialization_loop_insight_packet,
    check_specialization_loop_status,
    improvement_proof_blockers,
)


SCHEMA_PATH = Path("docs/creator_system/schemas/specialization-loop-status.schema.json")
INSIGHT_SCHEMA_PATH = Path(
    "docs/creator_system/schemas/specialization-loop-insight-packet.schema.json"
)


def _load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _load_insight_schema() -> dict:
    return json.loads(INSIGHT_SCHEMA_PATH.read_text(encoding="utf-8"))


def _proof(status: str, artifact_ref: str | None = "reports/proof.json") -> dict:
    return {
        "status": status,
        "artifact_ref": artifact_ref,
        "summary": f"{status} proof",
        "sha256": "a" * 64 if artifact_ref else None,
        "metrics": {"score": 0.91},
    }


def _valid_packet() -> dict:
    return build_specialization_loop_status(
        loop_id="memory-doctor-telegram-specialization",
        path_id="telegram-memory-doctor",
        domain_chip_id="domain-chip-memory-doctor",
        domain_chip_name="Memory Doctor",
        benchmark_pack_id="memory-doctor-telegram-v1",
        stage="decision",
        status="ready_for_review",
        evidence_state="complete",
        baseline=_proof("present", "reports/baseline.json"),
        candidate=_proof("present", "reports/candidate.json"),
        comparison={**_proof("pass", "reports/comparison.json"), "delta": 0.12},
        held_out=_proof("pass", "reports/held-out.json"),
        trap=_proof("not_required", None),
        decision="improved",
        next_move="Send the bounded improved claim for human review.",
        workspace_links=[
            {
                "label": "creator run",
                "href": "runs/memory-doctor-telegram-specialization",
            }
        ],
        raw_artifact_refs=[
            {
                "label": "baseline report",
                "path": "runs/memory-doctor-telegram-specialization/reports/baseline.json",
                "sha256": "b" * 64,
            }
        ],
        updated_at="2026-05-15T00:00:00Z",
    )


def _insight_proof(label: str, role: str, sha: str = "c") -> dict:
    return {
        "label": label,
        "evidence_role": role,
        "artifact_ref": f"reports/{label}.json",
        "sha256": sha * 64,
    }


def _valid_insight_packet() -> dict:
    return build_specialization_loop_insight_packet(
        packet_id="insight:memory-doctor-telegram-specialization:held-out-fix",
        loop_id="memory-doctor-telegram-specialization",
        source_status_ref="reports/specialization-loop-status.json",
        source_status_sha256="d" * 64,
        source_decision="improved",
        source_improved_claim_allowed=True,
        evidence_tier="candidate_review",
        insight_title="Held-out memory repair prompt should cite fresh state.",
        insight_summary=(
            "The candidate improved only when it anchored answers to fresh "
            "runtime evidence."
        ),
        reusable_lesson=(
            "Require the memory-doctor lane to name the fresh source before "
            "using prior memory."
        ),
        applies_to=["Spark Telegram memory-doctor responses"],
        does_not_apply_to=["network doctrine", "durable memory promotion"],
        proof_refs=[
            _insight_proof("baseline", "baseline"),
            _insight_proof("candidate", "candidate"),
            _insight_proof("comparison", "comparison"),
        ],
        privacy_reviewed=True,
        updated_at="2026-05-15T00:00:00Z",
    )


def test_specialization_loop_status_accepts_proven_improved_packet() -> None:
    packet = _valid_packet()

    jsonschema.Draft202012Validator(_load_schema()).validate(packet)
    check = check_specialization_loop_status(packet)

    assert packet["schema_version"] == SCHEMA_VERSION
    assert check["schema_version"] == CHECK_SCHEMA_VERSION
    assert check["effective_decision"] == "improved"
    assert check["improved_claim_allowed"] is True
    assert check["blocking_checks"] == []


def test_specialization_loop_insight_accepts_local_private_packet() -> None:
    status_packet = _valid_packet()
    packet = _valid_insight_packet()

    jsonschema.Draft202012Validator(_load_insight_schema()).validate(packet)
    check = check_specialization_loop_insight_packet(
        packet,
        status_packet=status_packet,
    )

    assert packet["schema_version"] == INSIGHT_SCHEMA_VERSION
    assert check["schema_version"] == INSIGHT_CHECK_SCHEMA_VERSION
    assert check["verdict"] == "pass"
    assert check["local_private_safe"] is True
    assert check["network_absorbable"] is False
    assert check["blocking_checks"] == []


@pytest.mark.parametrize(
    ("field", "value", "blocker"),
    [
        ("baseline", _proof("missing", None), "baseline_proof_missing"),
        (
            "candidate",
            _proof("fail", "reports/candidate.json"),
            "candidate_proof_missing",
        ),
        (
            "comparison",
            _proof("present", "reports/comparison.json"),
            "comparison_proof_missing",
        ),
        ("held_out", _proof("missing", None), "held_out_proof_missing"),
        ("trap", _proof("fail", "reports/trap.json"), "trap_proof_missing"),
    ],
)
def test_improved_claim_requires_full_proof(
    field: str,
    value: dict,
    blocker: str,
) -> None:
    packet = _valid_packet()
    packet[field] = value

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(_load_schema()).validate(packet)

    check = check_specialization_loop_status(packet)
    assert blocker in check["blocking_checks"]
    assert check["effective_decision"] == "unproven"
    assert check["improved_claim_allowed"] is False


@pytest.mark.parametrize("field", ["held_out", "trap"])
def test_improved_claim_requires_pass_artifact_ref_for_held_out_and_trap(
    field: str,
) -> None:
    packet = _valid_packet()
    packet[field] = _proof("pass", None)

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(_load_schema()).validate(packet)

    check = check_specialization_loop_status(packet)
    assert f"{field}_proof_missing" in check["blocking_checks"]


@pytest.mark.parametrize(
    ("field", "value", "blocker"),
    [
        ("network_absorbable", True, "promotion_network_absorbable_must_be_false"),
        (
            "network_publication_allowed",
            True,
            "promotion_network_publication_allowed_must_be_false",
        ),
        (
            "memory_promotion_allowed",
            True,
            "promotion_memory_promotion_allowed_must_be_false",
        ),
        (
            "product_runtime_wiring_allowed",
            True,
            "promotion_product_runtime_wiring_allowed_must_be_false",
        ),
    ],
)
def test_specialization_loop_insight_rejects_promotion_flags(
    field: str,
    value: bool,
    blocker: str,
) -> None:
    packet = _valid_insight_packet()
    packet["promotion"][field] = value

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(_load_insight_schema()).validate(packet)

    check = check_specialization_loop_insight_packet(packet)
    assert blocker in check["blocking_checks"]
    assert check["verdict"] == "blocked"
    assert check["network_absorbable"] is False


def test_specialization_loop_insight_review_candidate_requires_privacy_review() -> None:
    packet = _valid_insight_packet()
    packet["share_state"] = "review_candidate"
    packet["privacy"]["reviewed"] = False

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(_load_insight_schema()).validate(packet)

    check = check_specialization_loop_insight_packet(packet)
    assert "privacy_review_required_for_review_candidate" in check["blocking_checks"]


def test_specialization_loop_insight_binds_to_allowed_improved_status() -> None:
    packet = _valid_insight_packet()
    packet["source_status"]["improved_claim_allowed"] = False

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(_load_insight_schema()).validate(packet)

    check = check_specialization_loop_insight_packet(packet)
    assert "source_status_improved_claim_not_allowed" in check["blocking_checks"]


def test_specialization_loop_insight_detects_status_packet_mismatch() -> None:
    packet = _valid_insight_packet()
    status_packet = _valid_packet()
    status_packet["loop_id"] = "other-loop"

    check = check_specialization_loop_insight_packet(
        packet,
        status_packet=status_packet,
    )

    assert "source_status_loop_id_mismatch" in check["blocking_checks"]
    assert check["verdict"] == "blocked"


def test_unproven_packet_may_carry_missing_proof() -> None:
    packet = _valid_packet()
    packet["decision"] = "unproven"
    packet["evidence_state"] = "partial"
    packet["held_out"] = _proof("missing", None)

    jsonschema.Draft202012Validator(_load_schema()).validate(packet)
    check = check_specialization_loop_status(packet)

    assert check["decision"] == "unproven"
    assert check["effective_decision"] == "unproven"
    assert check["improved_claim_allowed"] is False
    assert check["blocking_checks"] == []


def test_domain_chip_labs_ownership_is_required() -> None:
    packet = copy.deepcopy(_valid_packet())
    packet["domain_chip"]["owner_repo"] = "spark-runtime"

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(_load_schema()).validate(packet)

    check = check_specialization_loop_status(packet)
    assert "domain_chip_owner_repo" in check["blocking_checks"]


def test_improvement_proof_allows_explicit_not_required_for_trap_or_held_out() -> None:
    packet = _valid_packet()
    packet["held_out"] = _proof("not_required", None)
    packet["trap"] = _proof("not_required", None)

    jsonschema.Draft202012Validator(_load_schema()).validate(packet)
    assert improvement_proof_blockers(packet) == []
