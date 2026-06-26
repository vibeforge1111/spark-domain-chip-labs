"""MCP feedback response path-redaction tests."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from chip_labs.intelligence_serving.chip_mcp_server import ChipMCPServer


def _server_with_chip(tmp_path: Path) -> ChipMCPServer:
    server = ChipMCPServer(search_dir=tmp_path)
    server._portfolio = [
        SimpleNamespace(
            chip_name="domain-chip-test",
            chip_path=tmp_path / "domain-chip-test",
        )
    ]
    server._ensure_portfolio = lambda: None
    return server


def test_feedback_directory_error_does_not_expose_path(tmp_path: Path, monkeypatch) -> None:
    server = _server_with_chip(tmp_path)

    def boom(*args, **kwargs):
        raise OSError("/private/secret/path")

    monkeypatch.setattr(Path, "mkdir", boom)

    response = server._handle_chip_feedback({"chip_name": "domain-chip-test"})

    assert response == {"error": "Cannot create feedback directory"}


def test_feedback_write_error_does_not_expose_path(tmp_path: Path, monkeypatch) -> None:
    server = _server_with_chip(tmp_path)

    def boom(*args, **kwargs):
        raise OSError("/private/secret/path")

    monkeypatch.setattr(Path, "write_text", boom)

    response = server._handle_chip_feedback({"chip_name": "domain-chip-test"})

    assert response == {"error": "Cannot write feedback packet"}


def test_feedback_success_response_does_not_expose_filesystem_path(tmp_path: Path) -> None:
    server = _server_with_chip(tmp_path)

    response = server._handle_chip_feedback(
        {
            "chip_name": "domain-chip-test",
            "doctrine_confirmed": ["one"],
            "doctrine_contradicted": [],
        }
    )

    assert response["success"] is True
    assert response["feedback_written"] is True
    assert "feedback_path" not in response
    assert response["doctrine_confirmed_count"] == 1
