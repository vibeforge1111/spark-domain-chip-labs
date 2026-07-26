"""Regression coverage for bounded release-evidence Git probes."""

from __future__ import annotations

import subprocess
from pathlib import Path

from chip_labs import creator_release_evidence


def test_git_lines_bounds_runtime_and_treats_timeout_as_unavailable(
    tmp_path: Path,
    monkeypatch,
) -> None:
    observed: dict[str, object] = {}

    def timed_out(*args, **kwargs):
        observed.update(kwargs)
        raise subprocess.TimeoutExpired(args[0], kwargs["timeout"])

    monkeypatch.setattr(creator_release_evidence.subprocess, "run", timed_out)

    assert creator_release_evidence._git_lines(tmp_path, "status", "--short") == []
    assert observed["timeout"] == 30


def test_git_lines_does_not_expose_timeout_command_or_output(
    tmp_path: Path,
    monkeypatch,
) -> None:
    def timed_out(*args, **kwargs):
        raise subprocess.TimeoutExpired(
            args[0],
            kwargs["timeout"],
            output="sensitive output",
            stderr="sensitive stderr",
        )

    monkeypatch.setattr(creator_release_evidence.subprocess, "run", timed_out)

    assert creator_release_evidence._git_lines(tmp_path, "show", "secret-ref") == []
