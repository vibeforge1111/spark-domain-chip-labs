"""Tests for mirofish_provider_adapters manifest loader."""

from __future__ import annotations

import json
import os
import stat
from pathlib import Path

import pytest

from chip_labs.mirofish_provider_adapters import load_mirofish_provider_adapter_manifest


def test_loads_valid_manifest(tmp_path: Path) -> None:
    """A well-formed manifest file is loaded as a dict."""
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text("{\"domain\": \"MiroFish Content Simulation\"}", encoding="utf-8")
    result = load_mirofish_provider_adapter_manifest(manifest_path)
    assert isinstance(result, dict)
    assert result["domain"] == "MiroFish Content Simulation"


def test_raises_value_error_on_missing_file(tmp_path: Path) -> None:
    """Missing manifest file raises a clean ValueError (not raw FileNotFoundError)."""
    missing = tmp_path / "does_not_exist.json"
    with pytest.raises(ValueError, match="could not load provider-adapter manifest"):
        load_mirofish_provider_adapter_manifest(missing)


def test_raises_value_error_on_permission_denied(tmp_path: Path) -> None:
    """PermissionError on the manifest file is converted to a clean ValueError.

    Real-world scenario: a CI artifact directory contains manifest files that
    are readable by the build user but not by the runtime user (or vice versa).
    """
    restricted = tmp_path / "locked.json"
    restricted.write_text("{}", encoding="utf-8")
    os.chmod(restricted, 0)
    try:
        with pytest.raises(ValueError, match="could not load provider-adapter manifest"):
            load_mirofish_provider_adapter_manifest(restricted)
    finally:
        try:
            os.chmod(restricted, stat.S_IRWXU)
        except OSError:
            pass


def test_raises_value_error_on_corrupt_json(tmp_path: Path) -> None:
    """Corrupt manifest JSON raises a clean ValueError (not raw JSONDecodeError)."""
    corrupt = tmp_path / "corrupt.json"
    corrupt.write_text("not valid json {{{", encoding="utf-8")
    with pytest.raises(ValueError, match="could not load provider-adapter manifest"):
        load_mirofish_provider_adapter_manifest(corrupt)


def test_raises_value_error_on_directory_path(tmp_path: Path) -> None:
    """Passing a directory instead of a file raises a clean ValueError.

    Real-world scenario: caller accidentally passes the parent directory
    (e.g., `load_mirofish_provider_adapter_manifest(manifests_dir)`) when
    they meant a file inside it. Before the fix this propagated IsADirectoryError.
    """
    directory = tmp_path / "subdir"
    directory.mkdir()
    with pytest.raises(ValueError, match="could not load provider-adapter manifest"):
        load_mirofish_provider_adapter_manifest(directory)
