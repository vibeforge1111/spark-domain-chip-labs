import json
import pytest
from pathlib import Path
from chip_labs.transfer_surface.loop_controller import _is_synthetic_json


def _get_controller(tmp_path):
    import chip_labs.transfer_surface.loop_controller as lc
    ctrl = object.__new__(lc.LoopController)
    return ctrl


def test_baseline_has_synthetic_true(tmp_path):
    ctrl = _get_controller(tmp_path)
    bench_dir = tmp_path / "benchmark"
    bench_dir.mkdir()
    ctrl._seed_benchmark_baseline(bench_dir)
    data = json.loads((bench_dir / "baseline_benchmark.json").read_text(encoding="utf-8"))
    assert data.get("synthetic") is True


def test_baseline_score_is_none(tmp_path):
    ctrl = _get_controller(tmp_path)
    bench_dir = tmp_path / "benchmark"
    bench_dir.mkdir()
    ctrl._seed_benchmark_baseline(bench_dir)
    data = json.loads((bench_dir / "baseline_benchmark.json").read_text(encoding="utf-8"))
    assert data["result"]["score"] is None


def test_baseline_verdict_is_none(tmp_path):
    ctrl = _get_controller(tmp_path)
    bench_dir = tmp_path / "benchmark"
    bench_dir.mkdir()
    ctrl._seed_benchmark_baseline(bench_dir)
    data = json.loads((bench_dir / "baseline_benchmark.json").read_text(encoding="utf-8"))
    assert data["result"]["verdict"] is None


def test_is_synthetic_json_detects_flag(tmp_path):
    f = tmp_path / "b.json"
    f.write_text(json.dumps({"synthetic": True, "score": None}), encoding="utf-8")
    assert _is_synthetic_json(f) is True


def test_is_synthetic_json_ignores_real(tmp_path):
    f = tmp_path / "r.json"
    f.write_text(json.dumps({"score": 0.9, "verdict": "pass"}), encoding="utf-8")
    assert _is_synthetic_json(f) is False


def test_is_synthetic_json_missing_safe(tmp_path):
    assert _is_synthetic_json(tmp_path / "missing.json") is False