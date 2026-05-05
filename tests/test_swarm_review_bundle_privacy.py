from __future__ import annotations

import copy
import json
from pathlib import Path

import jsonschema
import pytest


SWARM_REVIEW_BUNDLE_SCHEMA = Path(
    "docs/creator_system/schemas/swarm-review-bundle.schema.json"
)
STARTUP_YC_SWARM_REVIEW_BUNDLE = Path(
    "docs/creator_system/examples/swarm-review-bundles/startup-yc-transfer-supported/review_bundle.json"
)


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture()
def review_bundle_schema() -> dict:
    return _load_json(SWARM_REVIEW_BUNDLE_SCHEMA)


def test_review_bundle_requires_privacy_classification(
    review_bundle_schema: dict,
) -> None:
    payload = _load_json(STARTUP_YC_SWARM_REVIEW_BUNDLE)
    jsonschema.Draft202012Validator(review_bundle_schema).validate(payload)

    for record in payload["bundle_paths"].values():
        assert record["share_class"]
        assert record["redaction_status"]
        assert record["allowed_lane"]


def test_review_bundle_rejects_missing_share_class(
    review_bundle_schema: dict,
) -> None:
    payload = _load_json(STARTUP_YC_SWARM_REVIEW_BUNDLE)
    unsafe = copy.deepcopy(payload)
    del unsafe["bundle_paths"]["creator_intent"]["share_class"]

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(review_bundle_schema).validate(unsafe)


def test_private_review_bundle_path_cannot_enter_network_absorption_lane(
    review_bundle_schema: dict,
) -> None:
    payload = _load_json(STARTUP_YC_SWARM_REVIEW_BUNDLE)
    unsafe = copy.deepcopy(payload)
    unsafe["bundle_paths"]["creator_intent"]["allowed_lane"] = (
        "blocked_network_absorption"
    )

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(review_bundle_schema).validate(unsafe)


def test_forbidden_review_bundle_path_must_be_blocked(
    review_bundle_schema: dict,
) -> None:
    payload = _load_json(STARTUP_YC_SWARM_REVIEW_BUNDLE)
    unsafe = copy.deepcopy(payload)
    unsafe["bundle_paths"]["swarm_packet"]["share_class"] = "forbidden"
    unsafe["bundle_paths"]["swarm_packet"]["redaction_status"] = "pending"

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(review_bundle_schema).validate(unsafe)
