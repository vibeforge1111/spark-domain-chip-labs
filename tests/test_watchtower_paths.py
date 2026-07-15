"""Path-containment tests for watchtower and creator-run artifacts."""

from __future__ import annotations

from pathlib import Path

import pytest

from chip_labs.cli import _write_watchtower_pages
from chip_labs.creator_run import _resolve_external_artifact_path
from chip_labs.lab_hooks.watchtower import resolve_watchtower_page_path


def test_watchtower_page_path_resolves_inside_vault(tmp_path: Path) -> None:
    vault = tmp_path / "vault"

    resolved = resolve_watchtower_page_path(vault, "dashboards/Lab Home.md")

    assert resolved == (vault / "dashboards" / "Lab Home.md").resolve()


def test_watchtower_page_path_rejects_parent_traversal(tmp_path: Path) -> None:
    vault = tmp_path / "vault"

    with pytest.raises(ValueError, match="escapes the vault"):
        resolve_watchtower_page_path(vault, "../outside.md")


def test_watchtower_page_writer_rejects_absolute_path_outside_vault(tmp_path: Path) -> None:
    vault = tmp_path / "vault"
    outside = tmp_path / "outside.md"

    with pytest.raises(ValueError, match="escapes the vault"):
        _write_watchtower_pages(vault, [{"path": str(outside), "content": "nope"}])

    assert not outside.exists()


def test_creator_external_artifact_resolves_inside_run_dir(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    report = run_dir / "reports" / "summary.json"
    report.parent.mkdir(parents=True)
    report.write_text("{}", encoding="utf-8")

    assert _resolve_external_artifact_path(run_dir, "reports/summary.json") == report.resolve()


def test_creator_external_artifact_rejects_parent_traversal(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    run_dir.mkdir()

    with pytest.raises(ValueError, match="escapes the run directory"):
        _resolve_external_artifact_path(run_dir, "../outside.json")


def test_creator_external_artifact_rejects_absolute_path_outside_run_dir(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    outside = tmp_path.parent / f"{tmp_path.name}-outside.json"
    outside.write_text("{}", encoding="utf-8")

    try:
        with pytest.raises(ValueError, match="escapes the run directory"):
            _resolve_external_artifact_path(run_dir, str(outside))
    finally:
        outside.unlink(missing_ok=True)


def test_creator_external_artifact_allows_absolute_sibling_run_artifact(
    tmp_path: Path,
) -> None:
    run_dir = tmp_path / "current-run"
    run_dir.mkdir()
    sibling_report = tmp_path / "source-run" / "reports" / "summary.json"
    sibling_report.parent.mkdir(parents=True)
    sibling_report.write_text("{}", encoding="utf-8")

    assert (
        _resolve_external_artifact_path(run_dir, str(sibling_report))
        == sibling_report.resolve()
    )


def test_creator_external_artifact_rejects_relative_symlink_escape(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    outside = tmp_path / "outside.json"
    outside.write_text("{}", encoding="utf-8")
    link = run_dir / "linked.json"
    try:
        link.symlink_to(outside)
    except OSError as exc:
        pytest.skip(f"symlinks unavailable: {exc}")

    with pytest.raises(ValueError, match="escapes the run directory"):
        _resolve_external_artifact_path(run_dir, "linked.json")


def test_creator_external_artifact_rejects_absolute_sibling_symlink_escape(
    tmp_path: Path,
) -> None:
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    outside = tmp_path.parent / f"{tmp_path.name}-external.json"
    outside.write_text("{}", encoding="utf-8")
    link = tmp_path / "source-run.json"
    try:
        link.symlink_to(outside)
        with pytest.raises(ValueError, match="escapes the run directory"):
            _resolve_external_artifact_path(run_dir, str(link))
    except OSError as exc:
        pytest.skip(f"symlinks unavailable: {exc}")
    finally:
        link.unlink(missing_ok=True)
        outside.unlink(missing_ok=True)
