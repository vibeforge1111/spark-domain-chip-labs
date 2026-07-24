from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from chip_labs import creator_generator, hooks
from chip_labs.creator_generator import _score_mutations
from chip_labs.creator_release_gate import _load_json
from chip_labs.deep_eval import _extract_scores_from_runs
from chip_labs.intelligence_serving.chip_mcp_server import ChipMCPServer
from chip_labs.intelligence_serving.intelligence_server import _extract_benchmarks
from chip_labs.mirofish.signals import create_shock, create_signal
from chip_labs.transfer_surface import transfer


def test_missing_base_score_defaults_to_zero() -> None:
    assert _score_mutations({"mutation_deltas": {}}, {}) == 0.0


def test_release_gate_reports_invalid_json_path(tmp_path: Path) -> None:
    path = tmp_path / "invalid.json"
    path.write_text("{", encoding="utf-8")

    with pytest.raises(ValueError, match=str(path)):
        _load_json(path)


def test_zero_scores_remain_authoritative(tmp_path: Path) -> None:
    benchmark_dir = tmp_path / "research" / "benchmark_grounded"
    benchmark_dir.mkdir(parents=True)
    (benchmark_dir / "zero.json").write_text(
        json.dumps({"name": "zero", "score": 0, "result": 91}),
        encoding="utf-8",
    )

    assert _extract_benchmarks(tmp_path)[0]["score"] == 0
    assert _extract_scores_from_runs(
        [{"score": 0, "metric_value": 7}, {"metric_value": 0, "total_score": 8}]
    ) == [0.0, 0.0]
    assert create_signal("zero", "vc_funding", [], strength=0)["strength"] == 0
    assert create_shock("breakout_tool", [], strength_override=0)["strength"] == 0


def test_pattern_extraction_collects_source_text_once(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    chip = tmp_path / "domain-chip-cache-proof"
    (chip / "src").mkdir(parents=True)
    (chip / "src" / "evaluate.py").write_text(
        "dimensions = {}\n# contradiction promotion cooldown\n",
        encoding="utf-8",
    )
    (chip / "spark-chip.json").write_text("{}", encoding="utf-8")
    calls = 0
    original = transfer._collect_text

    def count_calls(path: Path, patterns: list[str]) -> str:
        nonlocal calls
        calls += 1
        return original(path, patterns)

    monkeypatch.setattr(transfer, "_collect_text", count_calls)
    transfer.extract_patterns(chip)

    assert calls == 1


def test_creator_failure_cleans_only_new_run_directory(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    brief = {
        "domain_id": "cleanup-proof",
        "domain_name": "Cleanup Proof",
        "goal": "Prove cleanup ownership.",
    }

    def fail_after_creation(**kwargs: object) -> None:
        run_dir = kwargs["run_dir"]
        assert isinstance(run_dir, Path)
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "partial.txt").write_text("partial", encoding="utf-8")
        raise RuntimeError("generation failed")

    monkeypatch.setattr(creator_generator, "_generate_creator_system", fail_after_creation)

    with pytest.raises(RuntimeError):
        creator_generator.generate_creator_system_from_brief(tmp_path / "new", brief)
    assert not (tmp_path / "new" / "cleanup-proof-creator-run").exists()

    existing = tmp_path / "existing" / "cleanup-proof-creator-run"
    existing.mkdir(parents=True)
    (existing / "owner-data.txt").write_text("keep", encoding="utf-8")
    with pytest.raises(RuntimeError):
        creator_generator.generate_creator_system_from_brief(tmp_path / "existing", brief)
    assert (existing / "owner-data.txt").read_text(encoding="utf-8") == "keep"


def test_suggestion_failure_log_does_not_expose_exception_text(
    caplog: pytest.LogCaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    server = ChipMCPServer()
    server._portfolio = [SimpleNamespace(chip_name="bounded-chip", chip_path=Path("/missing"))]
    server._last_load = float("inf")

    def fail_extract(path: Path) -> None:
        raise RuntimeError("secret provider detail")

    monkeypatch.setattr(
        "chip_labs.intelligence_serving.intelligence_server.extract_intelligence",
        fail_extract,
    )
    with caplog.at_level("WARNING"):
        result = server._handle_chip_suggest({})

    assert result["failed_chips"] == [
        {"chip_name": "bounded-chip", "error_type": "RuntimeError"}
    ]
    assert "RuntimeError" in caplog.text
    assert "secret provider detail" not in caplog.text


def test_hook_main_emits_empty_mapping_result(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    written: list[dict[str, object]] = []
    monkeypatch.setattr(hooks.sys, "argv", ["hooks", "empty"])
    monkeypatch.setitem(hooks.HANDLERS, "empty", lambda payload: {})
    monkeypatch.setattr(hooks, "_read_stdin", lambda: {})
    monkeypatch.setattr(hooks, "_write_stdout", written.append)

    hooks.main()

    assert written == [{}]
