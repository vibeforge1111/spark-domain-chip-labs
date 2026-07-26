from __future__ import annotations

import json
from pathlib import Path

from chip_labs.file_scan import ScanBudget, iter_bounded_files, read_text_bounded
from chip_labs.intelligence_serving.intelligence_server import (
    _count_evidence_files,
    _count_packets,
    _detect_dspy,
    _extract_all_doctrines,
    _extract_benchmarks,
)
from chip_labs.source_analysis import has_scoring_function


def test_file_walk_obeys_one_shared_entry_and_file_budget(tmp_path: Path) -> None:
    for index in range(8):
        folder = tmp_path / f"d{index}"
        folder.mkdir()
        (folder / f"f{index}.py").write_text("pass\n", encoding="utf-8")

    budget = ScanBudget(max_entries=7, max_files=3, max_bytes=64)
    found = list(iter_bounded_files([tmp_path], suffixes={".py"}, budget=budget))

    assert len(found) <= 3
    assert budget.entries_seen <= 7
    assert budget.files_seen == len(found)


def test_file_walk_does_not_follow_directory_or_leaf_symlinks(tmp_path: Path) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    secret = outside / "secret.py"
    secret.write_text("SECRET = True\n", encoding="utf-8")
    root = tmp_path / "root"
    root.mkdir()
    (root / "safe.py").write_text("SAFE = True\n", encoding="utf-8")
    try:
        (root / "linked-dir").symlink_to(outside, target_is_directory=True)
        (root / "linked-file.py").symlink_to(secret)
    except OSError:
        return

    found = list(iter_bounded_files([root], suffixes={".py"}))

    assert found == [root / "safe.py"]
    assert list(iter_bounded_files([root / "linked-dir"], suffixes={".py"})) == []


def test_text_reads_share_a_cumulative_byte_budget(tmp_path: Path) -> None:
    first = tmp_path / "first.txt"
    second = tmp_path / "second.txt"
    first.write_text("12345", encoding="utf-8")
    second.write_text("67890", encoding="utf-8")
    budget = ScanBudget(max_entries=10, max_files=10, max_bytes=7)

    assert read_text_bounded(first, budget=budget) == "12345"
    assert read_text_bounded(second, budget=budget) == ""
    assert budget.bytes_read == 7


def test_scoring_detection_uses_python_structure_not_multiline_regex(tmp_path: Path) -> None:
    src = tmp_path / "src"
    src.mkdir()
    (src / "decoy.py").write_text(
        'TEXT = "def score(value):\\n    return 100"\n'
        "def score(value):\n"
        "    def nested():\n"
        "        return value\n",
        encoding="utf-8",
    )
    assert has_scoring_function(src) is False

    (src / "real.py").write_text(
        "def evaluate(\n"
        "    value: float,\n"
        ") -> float:\n"
        "    if value > 0:\n"
        "        return value\n"
        "    raise ValueError('negative')\n",
        encoding="utf-8",
    )
    assert has_scoring_function(src) is True


def test_intelligence_scans_do_not_use_unbounded_rglob(
    tmp_path: Path, monkeypatch
) -> None:
    chip = tmp_path / "chip"
    packet_dir = chip / "research" / "packets"
    lane_dir = chip / "research" / "research_grounded"
    bench_dir = chip / "research" / "benchmark_grounded"
    src_dir = chip / "src"
    for directory in (packet_dir, lane_dir, bench_dir, src_dir):
        directory.mkdir(parents=True, exist_ok=True)
    (packet_dir / "claim.json").write_text(
        json.dumps({"claim": "bounded", "confidence": "high"}),
        encoding="utf-8",
    )
    (lane_dir / "evidence.md").write_text("evidence\n", encoding="utf-8")
    (bench_dir / "score.md").write_text("Score: 91\n", encoding="utf-8")
    (src_dir / "provider.py").write_text("import dspy\n", encoding="utf-8")

    def reject_rglob(self: Path, pattern: str):
        raise AssertionError(f"unbounded rglob used for {self}:{pattern}")

    monkeypatch.setattr(Path, "rglob", reject_rglob)

    assert [row["claim"] for row in _extract_all_doctrines(chip)] == ["bounded"]
    assert _count_evidence_files(chip)["research_grounded"] == 1
    assert _extract_benchmarks(chip)[0]["score"] == 91.0
    assert _count_packets(chip) == 1
    assert _detect_dspy(chip) is True
