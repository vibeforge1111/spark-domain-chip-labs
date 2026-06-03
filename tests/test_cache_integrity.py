"""Tests for cache integrity verification in hooks.py."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pytest

from chip_labs.hooks import (
    _compute_cache_checksum,
    _write_cache,
    _load_from_cache,
)
from chip_labs.intelligence_server import ChipIntelligence


# ---------------------------------------------------------------------------
# Mock ChipHandle
# ---------------------------------------------------------------------------

@dataclass
class MockChipHandle:
    chip_path: Path = Path("/mock")
    chip_name: str = "test-chip"
    domain: str = "testing"
    version: str = "0.1.0"
    capabilities: list[str] = field(default_factory=lambda: ["evaluate"])
    commands: dict[str, list[str]] = field(default_factory=dict)
    frontier: dict[str, Any] = field(default_factory=dict)
    quality_score: float = 60.0
    quality_verdict: str = "beta"
    intelligence: ChipIntelligence | None = None


def _make_mock_chip(tmp_path: Path) -> MockChipHandle:
    intel = ChipIntelligence(
        chip_name="test-chip",
        domain="testing",
        version="0.1.0",
        mission="Test mission",
        doctrines=[
            {"claim": "Test doctrine", "confidence": "high", "evidence_lane": "research_grounded"},
        ],
        evidence_summary={"research_grounded": 5, "benchmark_grounded": 0, "exploratory_frontier": 1, "realworld_validated": 0},
    )
    return MockChipHandle(
        chip_path=tmp_path / "domain-chip-test",
        intelligence=intel,
    )


# ---------------------------------------------------------------------------
# TestComputeCacheChecksum
# ---------------------------------------------------------------------------

class TestComputeCacheChecksum:
    def test_returns_hex_string(self) -> None:
        result = _compute_cache_checksum({"foo": "bar"})
        assert isinstance(result, str)
        assert len(result) == 64  # SHA-256 hex length

    def test_deterministic(self) -> None:
        data = {"a": 1, "b": [2, 3]}
        assert _compute_cache_checksum(data) == _compute_cache_checksum(data)

    def test_different_data_different_checksum(self) -> None:
        assert _compute_cache_checksum({"a": 1}) != _compute_cache_checksum({"a": 2})


# ---------------------------------------------------------------------------
# TestWriteCache
# ---------------------------------------------------------------------------

class TestWriteCache:
    def test_writes_envelope_with_checksum(self, tmp_path: Path) -> None:
        cache_file = tmp_path / "portfolio_cache.json"
        chip = _make_mock_chip(tmp_path)
        _write_cache(cache_file, [chip])

        raw = json.loads(cache_file.read_text(encoding="utf-8"))
        assert "checksum" in raw
        assert "payload" in raw
        assert isinstance(raw["checksum"], str)
        assert len(raw["checksum"]) == 64

    def test_checksum_matches_payload(self, tmp_path: Path) -> None:
        cache_file = tmp_path / "portfolio_cache.json"
        chip = _make_mock_chip(tmp_path)
        _write_cache(cache_file, [chip])

        raw = json.loads(cache_file.read_text(encoding="utf-8"))
        expected = _compute_cache_checksum(raw["payload"])
        assert raw["checksum"] == expected

    def test_atomic_write_no_tmp_files_left(self, tmp_path: Path) -> None:
        cache_file = tmp_path / "portfolio_cache.json"
        chip = _make_mock_chip(tmp_path)
        _write_cache(cache_file, [chip])

        tmp_files = list(tmp_path.glob(".cache-*.tmp"))
        assert len(tmp_files) == 0


# ---------------------------------------------------------------------------
# TestLoadFromCache
# ---------------------------------------------------------------------------

class TestLoadFromCache:
    def test_loads_valid_cache(self, tmp_path: Path) -> None:
        cache_file = tmp_path / "portfolio_cache.json"
        chip = _make_mock_chip(tmp_path)
        _write_cache(cache_file, [chip])

        handles = _load_from_cache(cache_file)
        assert len(handles) == 1
        assert handles[0].chip_name == "test-chip"
        assert handles[0].domain == "testing"

    def test_rejects_tampered_checksum(self, tmp_path: Path) -> None:
        cache_file = tmp_path / "portfolio_cache.json"
        chip = _make_mock_chip(tmp_path)
        _write_cache(cache_file, [chip])

        # Tamper with the checksum
        raw = json.loads(cache_file.read_text(encoding="utf-8"))
        raw["checksum"] = "0" * 64
        cache_file.write_text(json.dumps(raw), encoding="utf-8")

        handles = _load_from_cache(cache_file)
        assert handles == []

    def test_rejects_tampered_payload(self, tmp_path: Path) -> None:
        cache_file = tmp_path / "portfolio_cache.json"
        chip = _make_mock_chip(tmp_path)
        _write_cache(cache_file, [chip])

        # Tamper with the payload (change quality_score)
        raw = json.loads(cache_file.read_text(encoding="utf-8"))
        raw["payload"]["portfolio"][0]["quality_score"] = 999.0
        # Keep original checksum (which won't match tampered payload)
        cache_file.write_text(json.dumps(raw), encoding="utf-8")

        handles = _load_from_cache(cache_file)
        assert handles == []

    def test_legacy_format_without_checksum_accepted(self, tmp_path: Path) -> None:
        """Legacy caches without envelope should still load."""
        cache_file = tmp_path / "portfolio_cache.json"
        legacy = {
            "portfolio": [{
                "chip_path": str(tmp_path / "domain-chip-test"),
                "chip_name": "test-chip",
                "domain": "testing",
                "version": "0.1.0",
                "capabilities": [],
                "quality_score": 50.0,
                "quality_verdict": "beta",
            }],
            "ts": "2025-01-01T00:00:00",
        }
        cache_file.write_text(json.dumps(legacy), encoding="utf-8")

        handles = _load_from_cache(cache_file)
        assert len(handles) == 1
        assert handles[0].chip_name == "test-chip"

    def test_rejects_entry_with_missing_chip_name(self, tmp_path: Path) -> None:
        cache_file = tmp_path / "portfolio_cache.json"
        bad_data = {
            "portfolio": [{
                "chip_path": "/some/path",
                "domain": "testing",
                "version": "0.1.0",
            }],
            "ts": "2025-01-01T00:00:00",
        }
        payload = bad_data
        checksum = _compute_cache_checksum(payload)
        envelope = {"checksum": checksum, "payload": payload}
        cache_file.write_text(json.dumps(envelope), encoding="utf-8")

        handles = _load_from_cache(cache_file)
        assert handles == []

    def test_rejects_entry_with_invalid_quality_score(self, tmp_path: Path) -> None:
        cache_file = tmp_path / "portfolio_cache.json"
        bad_data = {
            "portfolio": [{
                "chip_path": str(tmp_path / "domain-chip-test"),
                "chip_name": "test-chip",
                "domain": "testing",
                "version": "0.1.0",
                "quality_score": "not_a_number",
            }],
            "ts": "2025-01-01T00:00:00",
        }
        payload = bad_data
        checksum = _compute_cache_checksum(payload)
        envelope = {"checksum": checksum, "payload": payload}
        cache_file.write_text(json.dumps(envelope), encoding="utf-8")

        handles = _load_from_cache(cache_file)
        # Should load with quality_score defaulted to 0.0
        assert len(handles) == 1
        assert handles[0].quality_score == 0.0

    def test_rejects_non_dict_entry(self, tmp_path: Path) -> None:
        cache_file = tmp_path / "portfolio_cache.json"
        bad_data = {
            "portfolio": ["not_a_dict", 42, None],
            "ts": "2025-01-01T00:00:00",
        }
        payload = bad_data
        checksum = _compute_cache_checksum(payload)
        envelope = {"checksum": checksum, "payload": payload}
        cache_file.write_text(json.dumps(envelope), encoding="utf-8")

        handles = _load_from_cache(cache_file)
        assert handles == []

    def test_loads_multiple_chips(self, tmp_path: Path) -> None:
        cache_file = tmp_path / "portfolio_cache.json"
        chip1 = MockChipHandle(
            chip_path=tmp_path / "domain-chip-a",
            chip_name="chip-a",
            domain="alpha",
            version="0.1.0",
        )
        chip2 = MockChipHandle(
            chip_path=tmp_path / "domain-chip-b",
            chip_name="chip-b",
            domain="beta",
            version="0.2.0",
        )
        _write_cache(cache_file, [chip1, chip2])

        handles = _load_from_cache(cache_file)
        assert len(handles) == 2
        names = {h.chip_name for h in handles}
        assert names == {"chip-a", "chip-b"}
