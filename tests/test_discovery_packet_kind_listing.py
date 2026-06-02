"""Regression tests for the discovery markdown packet_kind actionable-error message.

format_discovery_program_markdown rejects any packet_kind whose markdown
renderer is not registered. The error previously only echoed the value, with
no pointer to the supported packet_kinds. These tests pin the new message
shape and confirm each registered packet_kind still renders.
"""
from __future__ import annotations

import pytest

from chip_labs.mirofish.discovery import format_discovery_program_markdown


def test_unsupported_packet_kind_lists_supported_kinds() -> None:
    bad_packet = {"packet_kind": "mirofish_discovery_program_bogus"}
    with pytest.raises(ValueError) as excinfo:
        format_discovery_program_markdown(bad_packet)
    message = str(excinfo.value)
    assert "'mirofish_discovery_program_bogus'" in message
    for supported in (
        "mirofish_discovery_program_scaffold",
        "mirofish_discovery_program_input",
        "mirofish_discovery_program_cluster_packets",
        "mirofish_discovery_program",
    ):
        assert supported in message


def test_scaffold_packet_renders() -> None:
    packet = {
        "packet_kind": "mirofish_discovery_program_scaffold",
        "program_id": "p1",
        "stage_label": "discovery",
        "target_agent_count": 4,
        "cluster_plan": [],
    }
    markdown = format_discovery_program_markdown(packet)
    assert "Discovery" in markdown


def test_program_input_packet_renders() -> None:
    packet = {
        "packet_kind": "mirofish_discovery_program_input",
        "program_id": "p1",
        "clusters": [],
    }
    markdown = format_discovery_program_markdown(packet)
    assert "Discovery" in markdown


def test_cluster_packets_renders() -> None:
    packet = {
        "packet_kind": "mirofish_discovery_program_cluster_packets",
        "program_id": "p1",
        "cluster_packets": [],
    }
    markdown = format_discovery_program_markdown(packet)
    assert "Discovery" in markdown


def test_full_program_renders() -> None:
    packet = {
        "packet_kind": "mirofish_discovery_program",
        "program_id": "p1",
        "cluster_packets": [],
    }
    markdown = format_discovery_program_markdown(packet)
    assert "Discovery" in markdown
