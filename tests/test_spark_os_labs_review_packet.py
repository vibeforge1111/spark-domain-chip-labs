from __future__ import annotations

import copy
import json
from pathlib import Path

import jsonschema
import pytest


SCHEMA_PATH = Path("docs/creator_system/schemas/spark-os-labs-review-packet.schema.json")


def _load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _valid_packet() -> dict:
    return {
        "schema_version": "adaptive_creator_loop.spark_os_labs_review_packet.v1",
        "packet_id": "labs-review:ad-proof",
        "trace_ref": "trace_ref:redacted:e0461910ccc9",
        "request_id": "request_id:redacted:b12142f3813c",
        "source_repo": "spawner-ui",
        "ownership": {
            "contract_owner_repo": "spark-domain-chip-labs",
            "contract_scope": "metadata_schema_review_only",
            "source_owner_repo": "spawner-ui",
            "labs_may_promote_memory": False,
            "labs_may_wire_product_runtime": False,
            "labs_may_publish_network": False,
        },
        "source_artifact_metadata": {
            "source_surface": "spawner_prd_auto_trace",
            "artifact_body_exported": False,
            "event_counts": {
                "request_written": 1,
                "authority_verdict_evaluated": 1,
                "deterministic_static_artifacts_written": 1,
                "fallback_analysis_written": 1,
            },
            "file_count": 2,
            "task_count": 2,
        },
        "authority_verdict_ref": {
            "schema_version": "spark.authority_verdict.v1",
            "verdict": "blocked",
            "action_family": "mission_execution",
            "source_policy": "spawner_prd_bridge_control_auth_rate_limit_auto_provider",
            "source_repo": "spawner-ui",
            "reason_code": "auto_provider_deterministic-static_not_started",
        },
        "privacy_status": {
            "status": "metadata_only",
            "raw_prompt_exported": False,
            "provider_output_exported": False,
            "chat_or_user_id_exported": False,
            "memory_body_exported": False,
            "artifact_body_exported": False,
        },
        "benchmark": {
            "status": "placeholder",
            "placeholder": "Labs benchmark review required before promotion.",
            "required_before_promotion": True,
        },
        "rollback_route": {
            "status": "review_required",
            "route": "Reject packet candidate; leave source proof local and unchanged.",
            "owner_repo": "spark-domain-chip-labs",
        },
        "human_review_required": True,
        "network_absorbable": False,
        "network_publication_allowed": False,
        "memory_promotion_allowed": False,
        "payload_export_policy": {
            "mode": "metadata_only",
            "allowed_fields_only": True,
            "forbidden_payloads": [
                "raw_prompt",
                "provider_output",
                "chat_id",
                "user_id",
                "memory_body",
                "transcript_body",
                "audio_body",
                "secret_value",
                "artifact_body",
            ],
        },
        "next_action": "Review the redacted trace candidate in Spark Operating Cockpit.",
    }


def test_spark_os_labs_review_packet_accepts_metadata_only_candidate() -> None:
    jsonschema.Draft202012Validator(_load_schema()).validate(_valid_packet())


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("network_absorbable", True),
        ("network_publication_allowed", True),
        ("memory_promotion_allowed", True),
        ("human_review_required", False),
    ],
)
def test_spark_os_labs_review_packet_rejects_promotion_claims(field: str, value: object) -> None:
    packet = _valid_packet()
    packet[field] = value

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(_load_schema()).validate(packet)


def test_spark_os_labs_review_packet_rejects_raw_identifier_shape() -> None:
    packet = _valid_packet()
    packet["request_id"] = "tg-build-raw-private-id"

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(_load_schema()).validate(packet)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("contract_owner_repo", "spawner-ui"),
        ("contract_scope", "runtime_authority"),
        ("source_owner_repo", "spark-domain-chip-labs"),
        ("labs_may_promote_memory", True),
        ("labs_may_wire_product_runtime", True),
        ("labs_may_publish_network", True),
    ],
)
def test_spark_os_labs_review_packet_rejects_labs_authority_drift(field: str, value: object) -> None:
    packet = copy.deepcopy(_valid_packet())
    packet["ownership"][field] = value

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(_load_schema()).validate(packet)


def test_spark_os_labs_review_packet_requires_ownership_block() -> None:
    packet = _valid_packet()
    del packet["ownership"]

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(_load_schema()).validate(packet)


def test_spark_os_labs_review_packet_rejects_payload_body_export() -> None:
    packet = copy.deepcopy(_valid_packet())
    packet["privacy_status"]["artifact_body_exported"] = True

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(_load_schema()).validate(packet)
