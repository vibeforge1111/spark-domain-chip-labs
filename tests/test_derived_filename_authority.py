"""Regression coverage for identifiers embedded in generated filenames."""

from __future__ import annotations

import json
from pathlib import Path

from chip_labs.cli import _write_discovery_cluster_materialization
from chip_labs.hooks import _write_feedback_packet
from chip_labs.mirofish.discovery import (
    build_discovery_program_scaffold,
    split_discovery_program_scaffold,
)


def _cluster_bundle(cluster_ids: list[str]) -> dict[str, object]:
    bundle = split_discovery_program_scaffold(build_discovery_program_scaffold())
    bundle["cluster_packets"] = bundle["cluster_packets"][: len(cluster_ids)]
    for packet, cluster_id in zip(bundle["cluster_packets"], cluster_ids, strict=True):
        packet["cluster_id"] = cluster_id
    return bundle


def test_feedback_packet_contains_tool_identity_without_path_authority(tmp_path: Path) -> None:
    chip_path = tmp_path / "chip"
    chip_path.mkdir()

    first = _write_feedback_packet(chip_path, "action", "../../outside", "result")
    second = _write_feedback_packet(chip_path, "action", r"..\..\outside", "result")

    assert first is not None and second is not None
    root = (chip_path / "research" / "realworld_validated").resolve()
    assert first.resolve().is_relative_to(root)
    assert second.resolve().is_relative_to(root)
    assert first.name != second.name
    assert json.loads(first.read_text(encoding="utf-8"))["tool_name"] == "../../outside"
    assert json.loads(second.read_text(encoding="utf-8"))["tool_name"] == r"..\..\outside"
    assert not (tmp_path / "outside.json").exists()


def test_feedback_packet_filename_is_bounded(tmp_path: Path) -> None:
    chip_path = tmp_path / "chip"
    chip_path.mkdir()

    result = _write_feedback_packet(chip_path, "action", "x" * 10_000, "result")

    assert result is not None
    assert len(result.name) <= 100


def test_cluster_materialization_contains_identifiers_without_path_authority(
    tmp_path: Path,
) -> None:
    output = tmp_path / "materialized"
    (output / "01_..").mkdir(parents=True)
    (output / "02_..").mkdir()
    cluster_ids = ["../../../outside", "../../../../outside"]
    result = _write_discovery_cluster_materialization(
        output,
        _cluster_bundle(cluster_ids),
        "Clusters",
    )

    cluster_files = [Path(value) for value in result["files"] if value.endswith(".json")]
    assert len(cluster_files) == 2
    assert len({path.name for path in cluster_files}) == 2
    assert all(path.resolve().is_relative_to(output.resolve()) for path in cluster_files)
    assert [json.loads(path.read_text(encoding="utf-8"))["cluster_id"] for path in cluster_files] == cluster_ids
    assert not (tmp_path / "outside.json").exists()


def test_cluster_materialization_preserves_portable_filename(tmp_path: Path) -> None:
    output = tmp_path / "materialized"

    _write_discovery_cluster_materialization(
        output,
        _cluster_bundle(["creator-growth-systems"]),
        "Clusters",
    )

    assert (output / "01_creator-growth-systems.json").is_file()
