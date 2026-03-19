"""Tests for the packet generation module."""

from pathlib import Path

import pytest

from chip_labs.packets import generate_packets


class TestMethodologyPackets:
    """Test packet generation with research_focus='methodology'."""

    def test_methodology_returns_packets(self, tmp_path: Path) -> None:
        packets = generate_packets(
            {"research_focus": "methodology"},
            chip_search_dir=tmp_path,
        )
        assert isinstance(packets, list)
        assert len(packets) > 0

    def test_methodology_packet_kind(self, tmp_path: Path) -> None:
        packets = generate_packets(
            {"research_focus": "methodology"},
            chip_search_dir=tmp_path,
        )
        kinds = [p["packet_kind"] for p in packets]
        assert "methodology_doctrine" in kinds


class TestTransferPatternPackets:
    """Test packet generation with research_focus='transfer_patterns'."""

    def test_transfer_patterns_returns_packets(self, tmp_path: Path) -> None:
        packets = generate_packets(
            {"research_focus": "transfer_patterns"},
            chip_search_dir=tmp_path,
        )
        assert isinstance(packets, list)
        assert len(packets) > 0

    def test_transfer_pattern_packet_kind(self, tmp_path: Path) -> None:
        packets = generate_packets(
            {"research_focus": "transfer_patterns"},
            chip_search_dir=tmp_path,
        )
        kinds = [p["packet_kind"] for p in packets]
        assert "transfer_pattern" in kinds


class TestPacketRequiredFields:
    """Test that all packets have the required fields."""

    @pytest.fixture(params=["methodology", "transfer_patterns", "domain_discovery"])
    def packets(self, request, tmp_path: Path) -> list:
        return generate_packets(
            {"research_focus": request.param},
            chip_search_dir=tmp_path,
        )

    def test_has_packet_kind(self, packets: list) -> None:
        for p in packets:
            assert "packet_kind" in p

    def test_has_evidence_lane(self, packets: list) -> None:
        for p in packets:
            assert "evidence_lane" in p

    def test_has_created_at(self, packets: list) -> None:
        for p in packets:
            assert "created_at" in p
            assert len(p["created_at"]) > 0

    def test_has_content(self, packets: list) -> None:
        for p in packets:
            assert "content" in p
            assert isinstance(p["content"], dict)
