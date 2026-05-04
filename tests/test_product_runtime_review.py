from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from chip_labs.product_runtime_review import (
    REQUIRED_SURFACES,
    build_open_product_runtime_review_packet,
    check_product_runtime_review_packet,
    load_product_runtime_review_packet,
)


PACKET_SCHEMA = Path(
    "docs/creator_system/schemas/product-runtime-review-packet.schema.json"
)
CHECK_SCHEMA = Path(
    "docs/creator_system/schemas/product-runtime-review-check.schema.json"
)
OPEN_REVIEW = Path("docs/creator_system/examples/product-runtime-review/open-review.json")
READ_ONLY_REVIEW = Path(
    "docs/creator_system/examples/product-runtime-review/review-complete-read-only.json"
)


def _validate(schema_path: Path, payload: dict[str, object]) -> None:
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(payload)


def _complete_packet() -> dict[str, object]:
    packet = build_open_product_runtime_review_packet(review_id="product-review-pass")
    packet["surfaces"] = {
        surface: {
            "status": "passed",
            "reviewer": f"{surface}-reviewer",
            "evidence_ref": f"product-runtime/{surface}.md",
            "runtime_wiring_reviewed": True,
            "read_only_adapter_preserved": True,
            "blocked_states_visible": True,
            "evidence_mode_preserved": True,
            "creator_controls_enabled": False,
            "network_publication_allowed": True,
            "rollback_plan_ref": f"rollback/{surface}.md",
        }
        for surface in REQUIRED_SURFACES
    }
    return packet


def test_product_runtime_review_template_blocks_every_surface() -> None:
    packet = build_open_product_runtime_review_packet(review_id="product-review-open")

    _validate(PACKET_SCHEMA, packet)
    checked = check_product_runtime_review_packet(packet)
    _validate(CHECK_SCHEMA, checked)
    assert checked["verdict"] == "blocked"
    assert checked["network_absorbable"] is False
    assert set(checked["missing_surfaces"]) == set(REQUIRED_SURFACES)
    assert "surface_failure:builder:not_passed" in checked["blocking_checks"]


def test_saved_product_runtime_open_review_blocks_every_surface() -> None:
    packet = load_product_runtime_review_packet(OPEN_REVIEW)

    _validate(PACKET_SCHEMA, packet)
    checked = check_product_runtime_review_packet(packet)
    _validate(CHECK_SCHEMA, checked)
    assert checked["verdict"] == "blocked"
    assert checked["network_absorbable"] is False
    assert set(checked["missing_surfaces"]) == set(REQUIRED_SURFACES)


def test_saved_product_runtime_read_only_review_passes_review_phase_only() -> None:
    packet = load_product_runtime_review_packet(READ_ONLY_REVIEW)

    _validate(PACKET_SCHEMA, packet)
    checked = check_product_runtime_review_packet(packet)
    _validate(CHECK_SCHEMA, checked)
    assert checked["verdict"] == "pass"
    assert checked["network_absorbable"] is False
    assert packet["product_runtime_controls_wired"] is False
    assert all(
        surface["creator_controls_enabled"] is False
        for surface in packet["surfaces"].values()
    )


def test_product_runtime_review_passes_complete_review_without_absorption() -> None:
    packet = _complete_packet()

    _validate(PACKET_SCHEMA, packet)
    checked = check_product_runtime_review_packet(packet)
    _validate(CHECK_SCHEMA, checked)
    assert checked["verdict"] == "pass"
    assert checked["blocking_checks"] == []
    assert checked["missing_surfaces"] == []
    assert checked["network_absorbable"] is False


def test_product_runtime_review_blocks_controls_wired_in_methodology_repo() -> None:
    packet = _complete_packet()
    packet["product_runtime_controls_wired"] = True
    packet["surfaces"]["builder"]["creator_controls_enabled"] = True

    checked = check_product_runtime_review_packet(packet)

    assert checked["verdict"] == "blocked"
    assert "product_runtime_controls_must_not_be_wired_here" in checked[
        "blocking_checks"
    ]
    assert (
        "surface_failure:builder:creator_controls_enabled_must_be_false_in_methodology_repo"
        in checked["blocking_checks"]
    )
    assert checked["network_absorbable"] is False


def test_cli_product_runtime_review_check_fails_on_open_packet(tmp_path: Path) -> None:
    packet_path = tmp_path / "product-runtime-review.json"
    output_path = tmp_path / "product-runtime-review.check.json"
    packet_path.write_text(
        json.dumps(
            build_open_product_runtime_review_packet(review_id="product-review-cli"),
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
            "product-runtime-review-check",
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
    _validate(CHECK_SCHEMA, payload)
    assert payload["verdict"] == "blocked"
    assert payload["network_absorbable"] is False


def test_cli_product_runtime_review_template_emits_schema_valid_packet(
    tmp_path: Path,
) -> None:
    output_path = tmp_path / "product-runtime-review.json"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "chip_labs.cli",
            "product-runtime-review-template",
            "--review-id",
            "product-review-template",
            "--output",
            str(output_path),
        ],
        cwd=Path.cwd(),
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    _validate(PACKET_SCHEMA, payload)
    assert payload["network_absorbable"] is False
