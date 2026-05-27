"""Tests for host-safe default chip discovery paths."""

from __future__ import annotations

from pathlib import Path

from chip_labs import registry
from chip_labs.deep_eval import score_portfolio_v3
from chip_labs.registry import default_search_dir, discover_chips


def _use_home(monkeypatch, home: Path) -> None:
    monkeypatch.setattr(registry.os.path, "expanduser", lambda value: str(home) if value == "~" else value)


def test_default_search_dir_prefers_desktop_when_present(monkeypatch, tmp_path: Path) -> None:
    home = tmp_path / "home"
    desktop = home / "Desktop"
    desktop.mkdir(parents=True)
    _use_home(monkeypatch, home)

    assert default_search_dir() == desktop


def test_default_search_dir_falls_back_when_desktop_is_missing(monkeypatch, tmp_path: Path) -> None:
    home = tmp_path / "home"
    home.mkdir()
    _use_home(monkeypatch, home)

    assert default_search_dir() == home / ".spark" / "chip_labs"


def test_discover_chips_uses_fallback_when_desktop_is_missing(monkeypatch, tmp_path: Path) -> None:
    home = tmp_path / "home"
    chip = home / ".spark" / "chip_labs" / "domain-chip-test"
    chip.mkdir(parents=True)
    _use_home(monkeypatch, home)

    chips = discover_chips()

    assert [entry["name"] for entry in chips] == ["domain-chip-test"]
    assert chips[0]["path"] == str(chip)


def test_explicit_search_dir_still_wins(monkeypatch, tmp_path: Path) -> None:
    home = tmp_path / "home"
    fallback_chip = home / ".spark" / "chip_labs" / "domain-chip-fallback"
    fallback_chip.mkdir(parents=True)
    explicit = tmp_path / "explicit"
    explicit.mkdir()
    _use_home(monkeypatch, home)

    assert discover_chips(explicit) == []


def test_score_portfolio_uses_fallback_without_error(monkeypatch, tmp_path: Path) -> None:
    home = tmp_path / "home"
    fallback = home / ".spark" / "chip_labs"
    fallback.mkdir(parents=True)
    _use_home(monkeypatch, home)

    result = score_portfolio_v3()

    assert "error" not in result
    assert result["summary"]["chip_count"] == 0
