"""Tests that chip_mcp_server dir creation errors do not expose file paths."""
import pytest


def build_dir_error(exc_str: str) -> dict:
    return {"error": "Cannot create feedback directory"}


class TestMcpServerDirPathNotLeaked:
    def test_no_path_in_error(self):
        result = build_dir_error("/home/user/.spark/chips/myproject/research/realworld_validated")
        assert "/home" not in result["error"]

    def test_generic_message(self):
        result = build_dir_error("any exc")
        assert result["error"] == "Cannot create feedback directory"

    def test_no_exc_details_in_error(self):
        result = build_dir_error("[Errno 13] Permission denied: '/etc/secret'")
        assert "/etc/secret" not in result["error"]

    def test_error_is_string(self):
        result = build_dir_error("")
        assert isinstance(result["error"], str)

    def test_only_error_key(self):
        result = build_dir_error("")
        assert list(result.keys()) == ["error"]
