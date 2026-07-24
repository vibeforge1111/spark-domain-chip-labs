"""Focused behavioral proof for the packet-245 JSON and cleanup boundaries."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pytest

from chip_labs import cli, creator_production_readiness
from chip_labs.chip_factory.scaffold import load_brief
from chip_labs.content_outcome_calibration import _int_value
from chip_labs.lab_hooks import watchtower
from chip_labs.mirofish_provider_adapters import load_mirofish_provider_adapter_manifest
from chip_labs.startup_yc_promotion import _load_json


def test_integral_json_float_is_accepted_without_rounding() -> None:
    assert _int_value(3.0, default=-1) == 3
    assert _int_value(3.5, default=-1) == -1
    assert _int_value(True, default=-1) == -1


def test_brief_json_requires_valid_object(tmp_path: Path) -> None:
    invalid = tmp_path / "invalid.json"
    invalid.write_text("{", encoding="utf-8")
    with pytest.raises(ValueError, match="Invalid brief JSON"):
        load_brief(invalid)
    array = tmp_path / "array.json"
    array.write_text("[]", encoding="utf-8")
    with pytest.raises(ValueError, match="JSON object"):
        load_brief(array)


def test_generated_multi_seed_cli_reports_invalid_briefs(tmp_path: Path) -> None:
    invalid = tmp_path / "briefs.json"
    invalid.write_text("{", encoding="utf-8")
    args = argparse.Namespace(
        briefs=str(invalid),
        seeds="1",
        workspace_dir=str(tmp_path / "workspace"),
        variants_per_domain=1,
        output=None,
        fail_on_blocked=False,
    )
    with pytest.raises(SystemExit, match="not valid JSON"):
        cli.cmd_generated_multi_seed_run(args)


def test_mirofish_readouts_reject_invalid_json(monkeypatch, tmp_path: Path) -> None:
    invalid = tmp_path / "bad.json"
    invalid.write_text("{", encoding="utf-8")
    monkeypatch.setattr(
        watchtower,
        "_latest_meta_file",
        lambda pattern: invalid if "READOUT" in pattern else None,
    )
    with pytest.raises(ValueError, match="portfolio readout"):
        watchtower._mirofish_portfolio_page("now")
    with pytest.raises(ValueError, match="frontier readout"):
        watchtower._mirofish_frontier_page("now")


def test_provider_manifest_and_startup_packet_reject_invalid_json(tmp_path: Path) -> None:
    invalid = tmp_path / "bad.json"
    invalid.write_text("{", encoding="utf-8")
    with pytest.raises(ValueError, match="not valid JSON"):
        load_mirofish_provider_adapter_manifest(invalid)
    with pytest.raises(ValueError, match="Invalid JSON"):
        _load_json(invalid)


def test_auto_created_production_workspace_is_cleaned_on_failure(
    monkeypatch,
    tmp_path: Path,
) -> None:
    created: list[Path] = []
    real_temporary_directory = creator_production_readiness.tempfile.TemporaryDirectory

    class RecordingTemporaryDirectory:
        def __init__(self, *args, **kwargs):
            self._inner = real_temporary_directory(*args, **kwargs)
            self.name = self._inner.name
            created.append(Path(self.name))

        def __enter__(self):
            return self._inner.__enter__()

        def __exit__(self, exc_type, exc, traceback):
            return self._inner.__exit__(exc_type, exc, traceback)

    monkeypatch.setattr(
        creator_production_readiness.tempfile,
        "TemporaryDirectory",
        RecordingTemporaryDirectory,
    )
    monkeypatch.setattr(
        creator_production_readiness,
        "_load_briefs",
        lambda _path: (_ for _ in ()).throw(RuntimeError("brief failure")),
    )

    with pytest.raises(RuntimeError, match="brief failure"):
        creator_production_readiness.build_creator_system_production_readiness(
            generated_briefs_path=tmp_path / "unused.json",
        )
    assert created and not created[0].exists()
