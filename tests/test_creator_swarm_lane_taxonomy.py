from __future__ import annotations

import copy
import json
from pathlib import Path

import jsonschema
import pytest


SCHEMA_PATH = Path(
    "docs/creator_system/schemas/creator-swarm-lane-taxonomy.schema.json"
)
PRIVATE_WORKSPACE_EXAMPLE = Path(
    "docs/creator_system/examples/swarm-lane-taxonomy/startup-yc-private-workspace.json"
)
BLOCKED_PROPOSAL_EXAMPLE = Path(
    "docs/creator_system/examples/swarm-lane-taxonomy/startup-yc-network-proposal-blocked.json"
)


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture()
def lane_schema() -> dict:
    return _load_json(SCHEMA_PATH)


def test_creator_swarm_lane_taxonomy_examples_are_schema_valid(lane_schema: dict) -> None:
    validator = jsonschema.Draft202012Validator(lane_schema)

    for path in (PRIVATE_WORKSPACE_EXAMPLE, BLOCKED_PROPOSAL_EXAMPLE):
        payload = _load_json(path)
        validator.validate(payload)
        assert payload["network_absorbable"] is False
        assert payload["network_publication_allowed"] is False
        assert payload["stop_ship"]["no_automatic_publish"] is True


def test_private_workspace_lane_cannot_be_network_publication(lane_schema: dict) -> None:
    payload = _load_json(PRIVATE_WORKSPACE_EXAMPLE)
    unsafe = copy.deepcopy(payload)
    unsafe["network_absorbable"] = True

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(lane_schema).validate(unsafe)


def test_private_share_class_cannot_jump_to_reviewed_candidate(lane_schema: dict) -> None:
    payload = _load_json(PRIVATE_WORKSPACE_EXAMPLE)
    unsafe = copy.deepcopy(payload)
    unsafe["swarm_lane_state"] = "reviewed_candidate"

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(lane_schema).validate(unsafe)


def test_network_scope_requires_proposal_review(lane_schema: dict) -> None:
    payload = _load_json(BLOCKED_PROPOSAL_EXAMPLE)
    unsafe = copy.deepcopy(payload)
    unsafe["proposal_review"]["required"] = False

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(lane_schema).validate(unsafe)


def test_lane_taxonomy_requires_forbidden_transition_markers(lane_schema: dict) -> None:
    payload = _load_json(BLOCKED_PROPOSAL_EXAMPLE)
    unsafe = copy.deepcopy(payload)
    unsafe["lane_mapping"]["forbidden_transitions"] = [
        "ready_for_swarm_packet_to_network_absorbable",
        "workspace_sync_to_network_absorbable",
    ]

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(lane_schema).validate(unsafe)
