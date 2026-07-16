"""Regression coverage for stored evidence and generated output paths."""

from __future__ import annotations

from pathlib import Path

import pytest

from chip_labs.artifact_quality import _resolve_run_path
from chip_labs.intelligence_serving import intelligence_server
from chip_labs.intelligence_serving.intelligence_server import ChipIntelligence
from chip_labs.startup_yc_promotion import _resolve_related_path


def test_related_path_rejects_relative_sibling_prefix_escape(tmp_path: Path) -> None:
    plan_dir = tmp_path / "run"
    sibling = tmp_path / "run-sibling"
    plan_dir.mkdir()
    sibling.mkdir()
    (sibling / "evidence.json").write_text("{}", encoding="utf-8")

    with pytest.raises(ValueError, match=r"^invalid related path$"):
        _resolve_related_path(
            plan_dir / "plan.json",
            "../run-sibling/evidence.json",
        )


def test_related_path_rejects_symlink_escape(tmp_path: Path) -> None:
    plan_dir = tmp_path / "run"
    outside = tmp_path / "outside"
    plan_dir.mkdir()
    outside.mkdir()
    (outside / "evidence.json").write_text("{}", encoding="utf-8")
    (plan_dir / "alias").symlink_to(outside, target_is_directory=True)

    with pytest.raises(ValueError, match=r"^invalid related path$"):
        _resolve_related_path(plan_dir / "plan.json", "alias/evidence.json")


def test_related_path_allows_explicit_absolute_override(tmp_path: Path) -> None:
    plan_dir = tmp_path / "run"
    external = tmp_path / "operator-selected" / "evidence.json"
    plan_dir.mkdir()
    external.parent.mkdir()
    external.write_text("{}", encoding="utf-8")

    resolved = _resolve_related_path(
        plan_dir / "plan.json",
        str(external),
        allow_absolute=True,
    )

    assert resolved == external.resolve()


@pytest.mark.parametrize(
    "value",
    [None, 7, "", "   ", "../secret.json", "/tmp/secret.json", r"C:\secret.json", "bad\nname"],
)
def test_run_path_rejects_invalid_identity_without_reflection(
    tmp_path: Path,
    value: object,
) -> None:
    with pytest.raises(ValueError, match=r"^invalid run artifact path$") as caught:
        _resolve_run_path(tmp_path, value)  # type: ignore[arg-type]

    if str(value):
        assert str(value) not in str(caught.value)


def test_run_path_rejects_symlink_escape(tmp_path: Path) -> None:
    run_path = tmp_path / "run"
    outside = tmp_path / "outside.json"
    run_path.mkdir()
    outside.write_text("{}", encoding="utf-8")
    (run_path / "artifact.json").symlink_to(outside)

    with pytest.raises(ValueError, match=r"^invalid run artifact path$"):
        _resolve_run_path(run_path, "artifact.json")


def test_run_path_returns_canonical_in_run_file(tmp_path: Path) -> None:
    run_path = tmp_path / "run"
    artifact = run_path / "nested" / "artifact.json"
    artifact.parent.mkdir(parents=True)
    artifact.write_text("{}", encoding="utf-8")

    assert _resolve_run_path(run_path, "nested/artifact.json") == artifact.resolve()


@pytest.fixture
def minimal_intelligence(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        intelligence_server,
        "extract_intelligence",
        lambda _path: ChipIntelligence(
            chip_name="safe-chip",
            domain="testing",
            version="1.0.0",
            mission="Test safe output ownership.",
        ),
    )


def test_build_skill_rejects_leaf_symlink_escape(
    tmp_path: Path,
    minimal_intelligence: None,
) -> None:
    chip_path = tmp_path / "chip"
    outside = tmp_path / "outside.md"
    chip_path.mkdir()
    outside.write_text("do not replace", encoding="utf-8")
    (chip_path / "chip_skill.md").symlink_to(outside)

    with pytest.raises(ValueError, match=r"^invalid chip output path$"):
        intelligence_server.build_skill(chip_path)

    assert outside.read_text(encoding="utf-8") == "do not replace"


def test_build_doctrine_digest_rejects_leaf_symlink_escape(tmp_path: Path) -> None:
    chip_path = tmp_path / "chip"
    outside = tmp_path / "outside.md"
    chip_path.mkdir()
    outside.write_text("do not replace", encoding="utf-8")
    (chip_path / "chip_doctrine_digest.md").symlink_to(outside)

    with pytest.raises(ValueError, match=r"^invalid chip output path$"):
        intelligence_server.build_doctrine_digest(chip_path)

    assert outside.read_text(encoding="utf-8") == "do not replace"
