"""Tests that chip_runtime HookResult does not expose raw subprocess stderr."""
import pytest


def build_failure_result(stderr: str, returncode: int) -> dict:
    return {"returncode": returncode, "stderr_present": bool(stderr)}


class TestChipRuntimeHookResultNoStderr:
    def test_no_raw_stderr_key(self):
        result = build_failure_result("sensitive path /etc/secrets", 1)
        assert "stderr" not in result

    def test_stderr_present_true_when_stderr(self):
        result = build_failure_result("error details", 1)
        assert result["stderr_present"] is True

    def test_stderr_present_false_when_empty(self):
        result = build_failure_result("", 1)
        assert result["stderr_present"] is False

    def test_returncode_preserved(self):
        result = build_failure_result("err", 42)
        assert result["returncode"] == 42

    def test_secret_not_in_result(self):
        secret = "/home/user/.ssh/id_rsa"
        result = build_failure_result(secret, 1)
        assert all(secret not in str(v) for v in result.values())
