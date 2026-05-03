from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from chip_labs.creator_generator import generate_creator_system_from_brief
from chip_labs.operator_review import (
    build_operator_review_packet,
    check_operator_review_packet,
)


PACKET_SCHEMA = Path("docs/creator_system/schemas/operator-review-packet.schema.json")
CHECK_SCHEMA = Path("docs/creator_system/schemas/operator-review-check.schema.json")


def _brief() -> dict[str, object]:
    return {
        "domain_id": "operator-review-demo",
        "domain_name": "Operator Review Demo",
        "goal": "Prove generated creator systems keep review gates explicit.",
        "known_limits": ["No real operator has calibrated this generated run."],
        "unsafe_claims": ["Treat review notes as publication approval."],
    }


def test_generated_creator_run_includes_open_operator_review_packet(
    tmp_path: Path,
) -> None:
    jsonschema = pytest.importorskip("jsonschema")
    generated = generate_creator_system_from_brief(tmp_path, _brief())
    packet_path = generated.run_dir / "reports" / "operator_review_packet.json"

    packet = json.loads(packet_path.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(
        json.loads(PACKET_SCHEMA.read_text(encoding="utf-8"))
    ).validate(packet)
    assert packet["network_absorbable"] is False
    assert packet["gate_status"] == {
        "human_operator_calibration": False,
        "privacy_review": False,
        "rollback_review": False,
        "publication_approval": False,
    }
    assert "network_absorbable" in packet["forbidden_claims"]
    assert "Treat review notes as publication approval." in packet["forbidden_claims"]

    checked = check_operator_review_packet(packet)
    jsonschema.Draft202012Validator(
        json.loads(CHECK_SCHEMA.read_text(encoding="utf-8"))
    ).validate(checked)
    assert checked["verdict"] == "blocked"
    assert checked["network_absorbable"] is False
    assert set(checked["missing_gates"]) == {
        "human_operator_calibration",
        "privacy_review",
        "rollback_review",
        "publication_approval",
    }


def test_operator_review_check_passes_complete_review_without_absorption() -> None:
    packet = build_operator_review_packet(
        review_id="operator-review-complete",
        creator_run_id="creator-run-1",
        domain="Complete Review",
        evidence_tier="candidate_review",
    )
    packet["gate_status"] = {
        "human_operator_calibration": True,
        "privacy_review": True,
        "rollback_review": True,
        "publication_approval": True,
    }
    packet["gates"] = {
        "human_operator_calibration": {
            "status": "passed",
            "reviewer": "operator",
            "evidence_ref": "calibration-notes-1",
            "calibration_notes": "Reviewed outputs against operator expectations.",
        },
        "privacy_review": {
            "status": "passed",
            "reviewer": "operator",
            "evidence_ref": "privacy-review-1",
            "privacy_boundary": "workspace_only",
            "privacy_decision": "No private data leaves the workspace.",
        },
        "rollback_review": {
            "status": "passed",
            "reviewer": "operator",
            "evidence_ref": "rollback-review-1",
            "rollback_rule": "Deprecate if recompute, traps, or review repeats fail.",
        },
        "publication_approval": {
            "status": "passed",
            "reviewer": "operator",
            "evidence_ref": "publication-review-1",
            "approved_claim": "network_absorbable",
            "network_publication_allowed": True,
            "publication_decision": "Approved only as one gate in the full bundle.",
        },
    }

    checked = check_operator_review_packet(packet)

    assert checked["verdict"] == "pass"
    assert checked["blocking_checks"] == []
    assert checked["missing_gates"] == []
    assert checked["network_absorbable"] is False
    assert "not sufficient for network absorption" in checked["claim_boundary"]


def test_operator_review_check_blocks_unsafe_absorption_claim() -> None:
    packet = build_operator_review_packet(
        review_id="operator-review-unsafe",
        creator_run_id="creator-run-1",
        domain="Unsafe Review",
        evidence_tier="candidate_review",
    )
    packet["network_absorbable"] = True
    packet["forbidden_claims"] = []

    checked = check_operator_review_packet(packet)

    assert checked["verdict"] == "blocked"
    assert "network_absorbable_must_be_false" in checked["blocking_checks"]
    assert "forbidden_claim_missing:network_absorbable" in checked["blocking_checks"]
    assert checked["network_absorbable"] is False


def test_operator_review_schemas_reject_network_absorbable_true() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    packet = build_operator_review_packet(
        review_id="operator-review-schema",
        creator_run_id="creator-run-1",
        domain="Schema Review",
        evidence_tier="candidate_review",
    )
    packet_schema = json.loads(PACKET_SCHEMA.read_text(encoding="utf-8"))
    check_schema = json.loads(CHECK_SCHEMA.read_text(encoding="utf-8"))

    jsonschema.Draft202012Validator(packet_schema).validate(packet)
    unsafe_packet = json.loads(json.dumps(packet))
    unsafe_packet["network_absorbable"] = True
    assert list(jsonschema.Draft202012Validator(packet_schema).iter_errors(unsafe_packet))

    checked = check_operator_review_packet(packet)
    jsonschema.Draft202012Validator(check_schema).validate(checked)
    unsafe_check = json.loads(json.dumps(checked))
    unsafe_check["network_absorbable"] = True
    assert list(jsonschema.Draft202012Validator(check_schema).iter_errors(unsafe_check))


def test_cli_operator_review_check_fails_on_open_packet(tmp_path: Path) -> None:
    packet_path = tmp_path / "operator-review.json"
    output_path = tmp_path / "operator-review.check.json"
    packet_path.write_text(
        json.dumps(
            build_operator_review_packet(
                review_id="operator-review-cli",
                creator_run_id="creator-run-1",
                domain="CLI Review",
                evidence_tier="candidate_review",
            ),
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "chip_labs.cli",
            "operator-review-check",
            "--input",
            str(packet_path),
            "--output",
            str(output_path),
            "--fail-on-blocked",
        ],
        cwd=Path.cwd(),
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["verdict"] == "blocked"
    assert payload["network_absorbable"] is False
