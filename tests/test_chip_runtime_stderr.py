"""Tests: chip subprocess stderr not returned verbatim in API response (HookResult)."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from chip_labs.intelligence_serving.chip_runtime import HookResult, execute_hook


def _make_chip(tmp_path: Path) -> object:
    from chip_labs.intelligence_serving.chip_runtime import ChipHandle
    return ChipHandle(
        chip_path=tmp_path,
        chip_name="test-chip",
        domain="test",
        version="0.0.1",
        commands={"test_hook": ["python", "-c", "import sys; sys.stderr.write('INTERNAL PATH /etc/secret\n'); sys.exit(1)"]},
        quality_score=50.0,
    )


def test_full_stderr_not_returned_in_hook_result(tmp_path):
    chip = _make_chip(tmp_path)
    result = execute_hook(chip, "test_hook", mutations={})
    assert not result.success
    stderr_in_result = result.result.get("stderr", "")
    assert "/etc/secret" not in stderr_in_result


def test_truncated_safe_excerpt_returned_if_needed(tmp_path):
    chip = _make_chip(tmp_path)
    result = execute_hook(chip, "test_hook", mutations={})
    assert "returncode" in result.result
    if "stderr_excerpt" in result.result:
        assert len(result.result["stderr_excerpt"]) <= 200


def test_internal_paths_not_exposed_in_result(tmp_path):
    chip = _make_chip(tmp_path)
    result = execute_hook(chip, "test_hook", mutations={})
    result_str = json.dumps(result.result)
    assert "/etc/secret" not in result_str


def test_python_tracebacks_not_exposed(tmp_path):
    from chip_labs.intelligence_serving.chip_runtime import ChipHandle
    chip = ChipHandle(
        chip_path=tmp_path,
        chip_name="trace-chip",
        domain="test",
        version="0.0.1",
        commands={"hook": ["python", "-c", "raise RuntimeError('secret traceback at /internal/model.py')"]},
        quality_score=50.0,
    )
    result = execute_hook(chip, "hook", mutations={})
    result_str = json.dumps(result.result)
    assert "/internal/model.py" not in result_str


def test_full_stderr_still_logged_server_side(tmp_path, caplog):
    import logging
    chip = _make_chip(tmp_path)
    with caplog.at_level(logging.WARNING, logger="chip_labs.intelligence_serving.chip_runtime"):
        result = execute_hook(chip, "test_hook", mutations={})
    assert not result.success
    assert any("INTERNAL PATH" in record.message or "/etc/secret" in str(record) for record in caplog.records)
