"""Regression tests for the doctor-sweep operation actionable-error message.

The dispatcher in chip_labs.creator_run._apply_doctor_sweep_operation rejects
any op it doesn't recognize. The error message previously echoed only the bad
op, which forced operators to grep the source for the if/elif chain to find
the right verb. These tests pin the new message shape (failed value quoted,
known operations named inline) and the pure-hit path (valid ops dispatch as
before).
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from chip_labs.creator_run import _apply_doctor_sweep_operation


def _write_json(tmp_path: Path, payload: dict) -> Path:
    target = tmp_path / "case.json"
    target.write_text(json.dumps(payload), encoding="utf-8")
    return target


def test_unsupported_operation_lists_known_operations(tmp_path: Path) -> None:
    target = _write_json(tmp_path, {"score": 1})
    with pytest.raises(ValueError) as excinfo:
        _apply_doctor_sweep_operation(target, {"op": "bogus", "field": "score"})
    message = str(excinfo.value)
    assert "'bogus'" in message
    for known_op in (
        "replace_text",
        "replace_line_prefix",
        "set_nested",
        "delete_nested",
        "add_to_number",
    ):
        assert known_op in message


def test_set_nested_pure_hit_path_unchanged(tmp_path: Path) -> None:
    target = _write_json(tmp_path, {"score": 1})
    _apply_doctor_sweep_operation(
        target, {"op": "set_nested", "field": "score", "value": 42}
    )
    assert json.loads(target.read_text(encoding="utf-8"))["score"] == 42


def test_add_to_number_pure_hit_path_unchanged(tmp_path: Path) -> None:
    target = _write_json(tmp_path, {"score": 1})
    _apply_doctor_sweep_operation(
        target, {"op": "add_to_number", "field": "score", "delta": 4}
    )
    assert json.loads(target.read_text(encoding="utf-8"))["score"] == 5


def test_replace_text_pure_hit_path_unchanged(tmp_path: Path) -> None:
    target = tmp_path / "case.txt"
    target.write_text("alpha beta", encoding="utf-8")
    _apply_doctor_sweep_operation(
        target, {"op": "replace_text", "old": "alpha", "new": "gamma"}
    )
    assert target.read_text(encoding="utf-8") == "gamma beta"


def test_delete_nested_pure_hit_path_unchanged(tmp_path: Path) -> None:
    target = _write_json(tmp_path, {"score": 1, "stale": 2})
    _apply_doctor_sweep_operation(
        target, {"op": "delete_nested", "field": "stale"}
    )
    assert "stale" not in json.loads(target.read_text(encoding="utf-8"))
