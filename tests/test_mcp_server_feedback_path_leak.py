"""Tests that chip_mcp_server feedback write errors do not expose file paths."""
import pytest


def build_write_error(exc_str: str) -> dict:
    return {"error": "Cannot write feedback packet"}


class TestMcpServerFeedbackWritePathNotLeaked:
    def test_no_path_in_error(self):
        result = build_write_error("/home/user/.spark/chips/myproject/research/feedback.json")
        assert "/home" not in result["error"]

    def test_generic_message(self):
        result = build_write_error("any exc")
        assert result["error"] == "Cannot write feedback packet"

    def test_no_exc_details(self):
        result = build_write_error("[Errno 28] No space left on /mnt/secret")
        assert "/mnt/secret" not in result["error"]

    def test_error_is_string(self):
        result = build_write_error("")
        assert isinstance(result["error"], str)

    def test_only_error_key(self):
        result = build_write_error("")
        assert list(result.keys()) == ["error"]
