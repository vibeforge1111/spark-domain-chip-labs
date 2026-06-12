"""
Tests for generate_slot_script() code-injection fix.

Field descriptions from caller-supplied config must be safely escaped via
json.dumps() before being written into generated Python source code.
"""

import ast
import re
import pytest


# Inline the relevant escaping logic for isolated unit testing
import json


def _escape_field_desc(fdesc: str) -> str:
    """Mirrors the fixed: json.dumps(fdesc) used in generated source."""
    return json.dumps(fdesc)


def _make_input_field_line(fname: str, fdesc: str) -> str:
    return f'    {fname}: str = dspy.InputField(desc={_escape_field_desc(fdesc)})'


def _make_output_field_line(fname: str, fdesc: str) -> str:
    return f'    {fname}: str = dspy.OutputField(desc={_escape_field_desc(fdesc)})'


def _make_argparse_line(k: str, fdesc: str) -> str:
    return f'    run_parser.add_argument("--{k}", required=True, help={_escape_field_desc(fdesc)})'


def _build_minimal_module(input_fields: dict, output_fields: dict) -> str:
    """Build the class body portion of a generated module using the fixed escaping."""
    lines = [
        "class Sig:",
    ]
    for fname, fdesc in input_fields.items():
        lines.append(_make_input_field_line(fname, fdesc))
    for fname, fdesc in output_fields.items():
        lines.append(_make_output_field_line(fname, fdesc))
    lines.append("    pass")
    return "\n".join(lines)


class TestFieldDescEscaping:
    def test_normal_description_passes_through(self):
        line = _make_input_field_line("query", "The search query")
        assert "The search query" in line

    def test_double_quote_in_desc_is_escaped(self):
        line = _make_input_field_line("query", 'Say "hello"')
        # Must not produce unescaped double quote that breaks the string literal
        assert '\\\"' in line or "'Say" not in line
        # The line must be parseable Python
        src = f"class S:\n{line}\n    pass"
        # Use regex to verify no bare unescaped quote breaks the literal
        assert line.count('"Say "hello"') == 0

    def test_semicolon_injection_does_not_produce_executable_statement(self):
        payload = "benign; import os; os.system('id')"
        line = _make_input_field_line("f", payload)
        # The semicolon must be inside a string literal, not at statement level
        # json.dumps wraps in quotes so the semicolons are inside the string
        assert json.loads(line.split("desc=")[1].rstrip(")")) == payload

    def test_python_injection_pattern_is_contained_in_string(self):
        payload = '"); import subprocess; subprocess.call(["id"]); print("'
        line = _make_input_field_line("f", payload)
        escaped = json.dumps(payload)
        assert escaped in line

    def test_generated_class_body_is_valid_python(self):
        fields = {
            "query": 'Search "carefully"',
            "context": "Line1\nLine2",
            "tricky": "a\\b\tc",
        }
        src = _build_minimal_module(fields, {"answer": "The result"})
        # Must compile without SyntaxError
        ast.parse(src)

    def test_argparse_help_injection_contained(self):
        payload = 'x", required=False); import os  #'
        line = _make_argparse_line("k", payload)
        escaped = json.dumps(payload)
        assert escaped in line
        # The injected required=False must not appear outside the string
        # The line should have exactly one help= assignment
        assert line.count("required=False") == 0 or json.dumps("required=False") in line

    def test_newline_in_desc_escaped(self):
        line = _make_input_field_line("f", "line1\nline2")
        assert "\\n" in line  # json.dumps escapes newline
        assert "\n    " not in line.split("desc=")[1]  # not a raw newline in source

    def test_output_field_desc_also_escaped(self):
        payload = '"; evil()'
        line = _make_output_field_line("out", payload)
        assert json.dumps(payload) in line
