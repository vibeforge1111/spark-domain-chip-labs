from __future__ import annotations

from pathlib import Path

import pytest

import chip_labs.transfer_surface.loop_controller as loop_controller
from chip_labs.loop_controller import LoopConfig, RecursiveLoopController


def _run_suggestions(
    monkeypatch: pytest.MonkeyPatch,
    chip_path: Path,
    suggestions: list[dict[str, object]],
) -> list[str]:
    monkeypatch.setattr(loop_controller, "run_suggest", lambda **_kwargs: suggestions)
    monkeypatch.setattr(loop_controller, "score_chip", lambda _path: {"total_score": 50})
    controller = RecursiveLoopController(config=LoopConfig(research_enabled=True))
    controller._current_score = 50
    return controller._suggestion_phase(chip_path)


def test_candidate_id_traversal_is_rejected_without_blocking_valid_write(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    chip_path = tmp_path / "chip"
    research_dir = chip_path / "research" / "exploratory_frontier"
    (research_dir / "suggestion_..").mkdir(parents=True)
    escaped = tmp_path / "escaped.json"

    improvements = _run_suggestions(
        monkeypatch,
        chip_path,
        [
            {"candidate_id": "../../../../../escaped", "hypothesis": "escape"},
            {"candidate_id": "valid-candidate_1", "hypothesis": "safe"},
        ],
    )

    assert not escaped.exists()
    assert (research_dir / "suggestion_valid-candidate_1.json").is_file()
    assert improvements == ["Suggestions: Recorded 1 mutation candidates"]


def test_invalid_candidate_ids_are_rejected_instead_of_rewritten_to_aliases(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    chip_path = tmp_path / "chip"
    research_dir = chip_path / "research" / "exploratory_frontier"

    _run_suggestions(
        monkeypatch,
        chip_path,
        [
            {"candidate_id": "a/b", "hypothesis": "slash alias"},
            {"candidate_id": "a?b", "hypothesis": "punctuation alias"},
            {"candidate_id": "a_b", "hypothesis": "canonical"},
        ],
    )

    written = sorted(research_dir.glob("suggestion_*.json"))
    assert [path.name for path in written] == ["suggestion_a_b.json"]
    assert '"canonical"' in written[0].read_text(encoding="utf-8")


def test_research_directory_symlink_cannot_redirect_candidate_write(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    chip_path = tmp_path / "chip"
    research_parent = chip_path / "research"
    research_parent.mkdir(parents=True)
    outside = tmp_path / "outside"
    outside.mkdir()
    try:
        (research_parent / "exploratory_frontier").symlink_to(outside, target_is_directory=True)
    except OSError as exc:
        pytest.skip(f"symlinks unavailable: {exc}")

    improvements = _run_suggestions(
        monkeypatch,
        chip_path,
        [{"candidate_id": "valid", "hypothesis": "redirect"}],
    )

    assert not (outside / "suggestion_valid.json").exists()
    assert improvements == []


def test_broken_leaf_symlink_cannot_redirect_candidate_write(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    chip_path = tmp_path / "chip"
    research_dir = chip_path / "research" / "exploratory_frontier"
    research_dir.mkdir(parents=True)
    outside = tmp_path / "outside.json"
    try:
        (research_dir / "suggestion_valid.json").symlink_to(outside)
    except OSError as exc:
        pytest.skip(f"symlinks unavailable: {exc}")

    improvements = _run_suggestions(
        monkeypatch,
        chip_path,
        [{"candidate_id": "valid", "hypothesis": "redirect"}],
    )

    assert not outside.exists()
    assert improvements == []


def test_malformed_suggestion_is_skipped_without_blocking_valid_write(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    chip_path = tmp_path / "chip"
    suggestions: list[dict[str, object]] = [
        "not-a-suggestion",  # type: ignore[list-item]
        {"candidate_id": "valid", "hypothesis": "safe"},
    ]

    improvements = _run_suggestions(monkeypatch, chip_path, suggestions)

    written = chip_path / "research" / "exploratory_frontier" / "suggestion_valid.json"
    assert written.is_file()
    assert improvements == ["Suggestions: Recorded 1 mutation candidates"]


@pytest.mark.parametrize(
    "candidate_id",
    [None, True, 7, "", "   ", ".", "a" * 129],
)
def test_noncanonical_candidate_ids_are_skipped(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    candidate_id: object,
) -> None:
    chip_path = tmp_path / "chip"

    improvements = _run_suggestions(
        monkeypatch,
        chip_path,
        [{"candidate_id": candidate_id, "hypothesis": "invalid"}],
    )

    research_dir = chip_path / "research" / "exploratory_frontier"
    assert not list(research_dir.glob("suggestion_*.json"))
    assert improvements == []
