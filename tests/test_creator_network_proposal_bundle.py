from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import jsonschema
import pytest


SCHEMA_PATH = Path(
    "docs/creator_system/schemas/creator-network-proposal-bundle.schema.json"
)
BLOCKED_PROPOSAL_EXAMPLE = Path(
    "docs/creator_system/examples/network-proposal-bundles/startup-yc-blocked-proposal.json"
)


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture()
def proposal_schema() -> dict:
    return _load_json(SCHEMA_PATH)


def test_blocked_network_proposal_bundle_is_schema_valid(
    proposal_schema: dict,
) -> None:
    payload = _load_json(BLOCKED_PROPOSAL_EXAMPLE)
    jsonschema.Draft202012Validator(proposal_schema).validate(payload)

    assert payload["network_absorbable"] is False
    assert payload["network_publication_allowed"] is False
    assert payload["publication_approval"]["status"] == "not_approved"
    assert payload["stop_ship"]["no_automatic_publish"] is True


def test_network_proposal_artifact_hashes_match_local_refs(
    proposal_schema: dict,
) -> None:
    payload = _load_json(BLOCKED_PROPOSAL_EXAMPLE)
    jsonschema.Draft202012Validator(proposal_schema).validate(payload)

    for artifact_ref in payload["artifact_refs"]:
        artifact_path = Path(artifact_ref["path"])
        digest = hashlib.sha256(artifact_path.read_bytes()).hexdigest()
        assert digest == artifact_ref["sha256"]


def test_network_proposal_bundle_rejects_network_absorption_claim(
    proposal_schema: dict,
) -> None:
    payload = _load_json(BLOCKED_PROPOSAL_EXAMPLE)
    unsafe = copy.deepcopy(payload)
    unsafe["network_absorbable"] = True

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(proposal_schema).validate(unsafe)


def test_network_proposal_bundle_requires_replay_commands(
    proposal_schema: dict,
) -> None:
    payload = _load_json(BLOCKED_PROPOSAL_EXAMPLE)
    unsafe = copy.deepcopy(payload)
    unsafe["replay_commands"] = []

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(proposal_schema).validate(unsafe)


def test_network_proposal_bundle_requires_artifact_hashes(
    proposal_schema: dict,
) -> None:
    payload = _load_json(BLOCKED_PROPOSAL_EXAMPLE)
    unsafe = copy.deepcopy(payload)
    unsafe["artifact_refs"][0]["sha256"] = "missing"

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(proposal_schema).validate(unsafe)


def test_network_proposal_bundle_rejects_raw_windows_paths(
    proposal_schema: dict,
) -> None:
    payload = _load_json(BLOCKED_PROPOSAL_EXAMPLE)
    unsafe = copy.deepcopy(payload)
    unsafe["artifact_refs"][0]["path"] = "C:\\Users\\USER\\secret\\packet.json"

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(proposal_schema).validate(unsafe)


def test_reviewed_candidate_requires_verified_pr_and_passed_reviews(
    proposal_schema: dict,
) -> None:
    payload = _load_json(BLOCKED_PROPOSAL_EXAMPLE)
    unsafe = copy.deepcopy(payload)
    unsafe["lane_state"] = "reviewed_candidate"

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(proposal_schema).validate(unsafe)
