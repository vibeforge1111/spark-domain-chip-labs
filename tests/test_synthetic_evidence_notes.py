import pytest
from pathlib import Path
from chip_labs.transfer_surface.loop_controller import _is_synthetic_md


def test_synthetic_marker_detected(tmp_path):
    f = tmp_path / "placeholder.md"
    f.write_text("<!-- synthetic: true -->\n# placeholder\n", encoding="utf-8")
    assert _is_synthetic_md(f) is True


def test_real_md_not_flagged(tmp_path):
    f = tmp_path / "evidence.md"
    f.write_text("# Real evidence\nSome content here\n", encoding="utf-8")
    assert _is_synthetic_md(f) is False


def test_missing_md_safe_returns_false(tmp_path):
    assert _is_synthetic_md(tmp_path / "nonexistent.md") is False


def test_synthetic_md_excluded_from_count(tmp_path):
    lane_dir = tmp_path / "lane"
    lane_dir.mkdir()
    (lane_dir / "real.md").write_text("# Real\nContent\n", encoding="utf-8")
    (lane_dir / "synth.md").write_text("<!-- synthetic: true -->\n# placeholder\n", encoding="utf-8")
    existing_md = [p for p in lane_dir.glob("*.md") if not _is_synthetic_md(p)]
    assert len(existing_md) == 1
    assert existing_md[0].name == "real.md"


def test_all_synthetic_mds_leaves_empty_list(tmp_path):
    lane_dir = tmp_path / "lane2"
    lane_dir.mkdir()
    (lane_dir / "a.md").write_text("<!-- synthetic: true -->\n", encoding="utf-8")
    (lane_dir / "b.md").write_text("<!-- synthetic: true -->\n", encoding="utf-8")
    existing_md = [p for p in lane_dir.glob("*.md") if not _is_synthetic_md(p)]
    assert len(existing_md) == 0