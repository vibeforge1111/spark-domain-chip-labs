from __future__ import annotations

import json
from pathlib import Path

import pytest

from chip_labs.creator_run import _apply_doctor_sweep_operation


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def _read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_doctor_sweep_unknown_operation_lists_known_operations(tmp_path: Path) -> None:
    target = tmp_path / "target.json"
    _write_json(target, {"score": 1})

    with pytest.raises(ValueError) as error:
        _apply_doctor_sweep_operation(target, {"op": "set-nested", "field": "score", "value": 2})

    message = str(error.value)
    assert "unsupported operation 'set-nested'" in message
    for op in (
        "replace_text",
        "replace_line_prefix",
        "set_nested",
        "delete_nested",
        "add_to_number",
    ):
        assert op in message


@pytest.mark.parametrize(
    ("initial", "operation", "expected"),
    [
        ("old value\n", {"op": "replace_text", "old": "old", "new": "new"}, "new value\n"),
        (
            "score=1\nname=demo\n",
            {"op": "replace_line_prefix", "prefix": "score=", "replacement": "score=2"},
            "score=2\nname=demo\n",
        ),
    ],
)
def test_doctor_sweep_text_operations_still_dispatch(
    tmp_path: Path,
    initial: str,
    operation: dict[str, object],
    expected: str,
) -> None:
    target = tmp_path / "target.txt"
    target.write_text(initial, encoding="utf-8")

    _apply_doctor_sweep_operation(target, operation)

    assert target.read_text(encoding="utf-8") == expected


@pytest.mark.parametrize(
    ("initial", "operation", "expected"),
    [
        ({"score": 1}, {"op": "set_nested", "field": "score", "value": 2}, {"score": 2}),
        ({"score": 1}, {"op": "delete_nested", "field": "score"}, {}),
        ({"score": 1}, {"op": "add_to_number", "field": "score", "delta": 2}, {"score": 3}),
    ],
)
def test_doctor_sweep_json_operations_still_dispatch(
    tmp_path: Path,
    initial: dict[str, object],
    operation: dict[str, object],
    expected: dict[str, object],
) -> None:
    target = tmp_path / "target.json"
    _write_json(target, initial)

    _apply_doctor_sweep_operation(target, operation)

    assert _read_json(target) == expected
