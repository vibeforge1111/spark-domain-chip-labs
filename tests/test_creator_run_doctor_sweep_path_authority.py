from __future__ import annotations

import json
from pathlib import Path

import pytest

from chip_labs.creator_run import _apply_doctor_sweep_case


def _write_score(path: Path, score: int = 1) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"score": score}), encoding="utf-8")


def _score(path: Path) -> int:
    return int(json.loads(path.read_text(encoding="utf-8"))["score"])


def _set_score_case(path: object) -> dict[str, object]:
    return {
        "operations": [
            {"op": "set_nested", "path": path, "field": "score", "value": 2}
        ]
    }


def test_doctor_sweep_allows_nested_file_beneath_run(tmp_path: Path) -> None:
    run_path = tmp_path / "run"
    target = run_path / "reports" / "score.json"
    _write_score(target)

    errors = _apply_doctor_sweep_case(run_path, _set_score_case("reports/score.json"))

    assert errors == []
    assert _score(target) == 2


@pytest.mark.parametrize("relative_path", ["../outside.json", r"..\outside.json", r"C:\outside.json"])
def test_doctor_sweep_rejects_cross_platform_path_aliases_without_reflection(
    tmp_path: Path,
    relative_path: str,
) -> None:
    run_path = tmp_path / "run"
    run_path.mkdir()
    outside = tmp_path / "outside.json"
    _write_score(outside)

    errors = _apply_doctor_sweep_case(run_path, _set_score_case(relative_path))

    assert errors == ["invalid operation path"]
    assert relative_path not in errors[0]
    assert _score(outside) == 1


def test_doctor_sweep_rejects_absolute_path_even_inside_run(tmp_path: Path) -> None:
    run_path = tmp_path / "run"
    target = run_path / "score.json"
    _write_score(target)

    errors = _apply_doctor_sweep_case(run_path, _set_score_case(str(target)))

    assert errors == ["invalid operation path"]
    assert str(target) not in errors[0]
    assert _score(target) == 1


def test_doctor_sweep_rejects_prefix_sibling_escape(tmp_path: Path) -> None:
    run_path = tmp_path / "run"
    run_path.mkdir()
    outside = tmp_path / "run-sibling" / "score.json"
    _write_score(outside)

    errors = _apply_doctor_sweep_case(
        run_path,
        _set_score_case("../run-sibling/score.json"),
    )

    assert errors == ["invalid operation path"]
    assert _score(outside) == 1


def test_doctor_sweep_rejects_symlink_escape(tmp_path: Path) -> None:
    run_path = tmp_path / "run"
    run_path.mkdir()
    outside = tmp_path / "outside" / "score.json"
    _write_score(outside)
    link = run_path / "linked"
    try:
        link.symlink_to(outside.parent, target_is_directory=True)
    except OSError as exc:
        pytest.skip(f"symlinks unavailable: {exc}")

    errors = _apply_doctor_sweep_case(run_path, _set_score_case("linked/score.json"))

    assert errors == ["invalid operation path"]
    assert _score(outside) == 1


@pytest.mark.parametrize("relative_path", [None, 7, {}, [], "", "   ", "."])
def test_doctor_sweep_rejects_non_identity_paths(
    tmp_path: Path,
    relative_path: object,
) -> None:
    run_path = tmp_path / "run"
    run_path.mkdir()

    errors = _apply_doctor_sweep_case(run_path, _set_score_case(relative_path))

    assert errors == ["invalid operation path"]
