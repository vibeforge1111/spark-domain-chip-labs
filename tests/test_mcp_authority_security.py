"""Production-coupled regressions for the MCP authority PR family.

The cases preserve useful findings from PRs #267, #270, #354, and #403 while
pinning standard stdio behavior against the incompatible auth proposal in #268.
"""

from __future__ import annotations

import io
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from chip_labs.intelligence_serving.chip_mcp_server import (
    MAX_REQUEST_BYTES,
    ChipMCPServer,
)


class TrackingBytesIO(io.BytesIO):
    """Record every bound passed to readline()."""

    def __init__(self, value: bytes) -> None:
        super().__init__(value)
        self.readline_sizes: list[int] = []

    def readline(self, size: int = -1) -> bytes:
        self.readline_sizes.append(size)
        return super().readline(size)


def _server_with_chip(search_root: Path, chip_path: Path) -> ChipMCPServer:
    server = ChipMCPServer(search_dir=search_root)
    server._portfolio = [
        SimpleNamespace(chip_name="domain-chip-test", chip_path=chip_path)
    ]
    server._ensure_portfolio = lambda: None
    return server


def _run_server(payload: bytes) -> tuple[list[dict[str, object]], str, TrackingBytesIO]:
    stdin = TrackingBytesIO(payload)
    stdout = io.StringIO()
    stderr = io.StringIO()
    ChipMCPServer().run(stdin=stdin, stdout=stdout, stderr=stderr)
    responses = [json.loads(line) for line in stdout.getvalue().splitlines()]
    return responses, stderr.getvalue(), stdin


def test_feedback_rejects_chip_symlink_outside_search_root(tmp_path: Path) -> None:
    search_root = tmp_path / "chips"
    outside = tmp_path / "outside"
    search_root.mkdir()
    outside.mkdir()
    chip_link = search_root / "domain-chip-test"
    chip_link.symlink_to(outside, target_is_directory=True)
    server = _server_with_chip(search_root, chip_link)

    response = server._handle_chip_feedback({"chip_name": "domain-chip-test"})

    assert response == {"error": "Chip feedback path is not authorized"}
    assert not (outside / "research").exists()


def test_feedback_rejects_destination_symlink_escape(tmp_path: Path) -> None:
    search_root = tmp_path / "chips"
    chip_root = search_root / "domain-chip-test"
    outside = tmp_path / "outside"
    (chip_root / "research").mkdir(parents=True)
    outside.mkdir()
    (chip_root / "research" / "realworld_validated").symlink_to(
        outside,
        target_is_directory=True,
    )
    server = _server_with_chip(search_root, chip_root)

    response = server._handle_chip_feedback({"chip_name": "domain-chip-test"})

    assert response == {"error": "Chip feedback path is not authorized"}
    assert list(outside.iterdir()) == []


def test_oversized_request_is_bounded_before_parse_and_next_request_survives() -> None:
    oversized = b'{"padding":"' + (b"x" * (MAX_REQUEST_BYTES + 64)) + b'"}\n'
    valid = b'{"jsonrpc":"2.0","id":7,"method":"tools/list","params":{}}\n'

    responses, stderr, stdin = _run_server(oversized + valid)

    assert [response["id"] for response in responses] == [7]
    assert len(responses[0]["result"]["tools"]) == 7  # type: ignore[index]
    assert "oversized request rejected" in stderr
    assert "padding" not in stderr
    assert stdin.readline_sizes
    assert all(0 < size <= MAX_REQUEST_BYTES + 1 for size in stdin.readline_sizes)


def test_request_limit_counts_utf8_bytes() -> None:
    oversized_unicode = b'"' + ("é" * (MAX_REQUEST_BYTES // 2 + 1)).encode() + b'"\n'

    responses, stderr, _stdin = _run_server(oversized_unicode)

    assert responses == []
    assert "oversized request rejected" in stderr


def test_nonstandard_auth_environment_does_not_change_stdio_protocol(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CHIP_MCP_AUTH_TOKEN", "must-not-change-standard-mcp")
    tools = b'{"jsonrpc":"2.0","id":8,"method":"tools/list","params":{}}\n'
    auth = b'{"jsonrpc":"2.0","id":9,"method":"auth","params":{"token":"x"}}\n'

    responses, _stderr, _stdin = _run_server(tools + auth)

    assert len(responses[0]["result"]["tools"]) == 7  # type: ignore[index]
    assert responses[1]["error"]["code"] == -32601  # type: ignore[index]


def test_security_policy_uses_private_reporting_without_unfunded_sla() -> None:
    policy = Path("SECURITY.md").read_text(encoding="utf-8").lower()

    assert "private vulnerability reporting" in policy
    assert "do not open a public issue" in policy
    assert "48 hours" not in policy
    assert "5 business days" not in policy
