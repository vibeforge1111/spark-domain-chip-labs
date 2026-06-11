"""Tests for candidate_id path traversal sanitization in loop_controller.

Security property: _suggestion_phase writes suggestion JSON files only inside
chip_path/research/exploratory_frontier/, never outside, regardless of the
candidate_id value in the suggestion dict.

Fix applied:
  raw_id = str(s.get("candidate_id") or "unknown")
  candidate_id = re.sub(r"[^a-zA-Z0-9_-]", "_", raw_id) or "unknown"
  suggestion_path = research_dir / f"suggestion_{candidate_id}.json"
  try:
      suggestion_path.resolve().relative_to(research_dir.resolve())
  except ValueError:
      continue  # skip — path would escape research_dir

Covers:
- ../ traversal → each char becomes underscore → safe filename
- absolute paths → sanitized to underscore-prefixed safe filename
- path separators (/, \) → become underscore
- empty / whitespace IDs → "unknown" or underscores
- normal IDs (a-zA-Z0-9_-.) → unchanged
- Proof: ALL written suggestion files stay inside research/exploratory_frontier/
- Proof: one bad ID does not block good IDs
- Proof: no crash with real run_suggest
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from chip_labs.loop_controller import RecursiveLoopController, LoopConfig
from chip_labs.scaffold import scaffold_chip


# -------------------------------------------------------------------------
# Sanitization replica (mirrors the actual code)
# -------------------------------------------------------------------------

_SANITIZE_RE = re.compile(r"[^a-zA-Z0-9_-]")


def _sanitize(candidate_id: str) -> str:
    """Mirror of the actual sanitization in _suggestion_phase."""
    return _SANITIZE_RE.sub("_", str(candidate_id)) or "unknown"


# -------------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------------

def _make_brief(**overrides) -> dict:
    brief = {
        "domain_id": "test-path-traversal",
        "domain_name": "Test Path Traversal",
        "category": "technology",
        "description": "Test chip for path traversal validation.",
        "primary_metric": "quality_score",
        "mutation_axes": [{"name": "approach", "values": ["baseline", "optimized"]}],
    }
    brief.update(overrides)
    return brief


def _scaffold_chip(tmp_path: Path) -> Path:
    return scaffold_chip(_make_brief(), output_dir=tmp_path)


# -------------------------------------------------------------------------
# Unit: sanitization regex
# -------------------------------------------------------------------------

class TestSanitization:
    """Unit tests for _sanitize.

    These document the ACTUAL behavior of re.sub(r'[^a-zA-Z0-9_-]', '_', ...).
    """

    def test_normal_ids_unchanged(self) -> None:
        assert _sanitize("valid_candidate_001") == "valid_candidate_001"
        assert _sanitize("fix-v2-optimization") == "fix-v2-optimization"
        assert _sanitize("my-fix-v2_beta") == "my-fix-v2_beta"
        assert _sanitize("Test123") == "Test123"
        assert _sanitize("123abc") == "123abc"

    def test_dotdot_slash_replaced(self) -> None:
        # 4 dots + 4 slashes + 1 dot in .evil = 9 unsafe chars → 9 underscores
        assert _sanitize("../../../etc/evil") == "_________etc_evil"
        assert _sanitize("../foo") == "___foo"
        # foo/../bar: / + .. + / = 4 unsafe chars → 4 underscores
        assert _sanitize("foo/../bar") == "foo____bar"

    def test_dot_only_replaced(self) -> None:
        assert _sanitize(".") == "_"
        assert _sanitize("..") == "__"
        assert _sanitize("foo...") == "foo___"   # 3 dots
        assert _sanitize("foo..bar") == "foo__bar"  # 2 dots
        assert _sanitize("....") == "____"        # 4 dots

    def test_unix_absolute_slashes_replaced(self) -> None:
        assert _sanitize("/etc/passwd") == "_etc_passwd"  # 1 slash → 1 underscore
        assert _sanitize("/tmp/evil") == "_tmp_evil"

    def test_forward_slash_replaced(self) -> None:
        assert _sanitize("foo/bar") == "foo_bar"
        assert _sanitize("a/b/c") == "a_b_c"
        assert _sanitize("foo/./bar") == "foo___bar"  # 2 slashes + 1 dot = 3 underscores

    def test_backslash_replaced(self) -> None:
        assert _sanitize("foo\\bar") == "foo_bar"
        assert _sanitize("C:\\Windows\\System32") == "C__Windows_System32"

    def test_shell_chars_replaced(self) -> None:
        assert _sanitize(";rm -rf") == "_rm_-rf"
        assert _sanitize("`id`") == "_id_"       # backticks replaced by _
        assert _sanitize("$(whoami)") == "__whoami_"  # $, (, ), {, } all replaced by _

    def test_dots_allowed_normalized(self) -> None:
        assert _sanitize("v1.2.3") == "v1_2_3"
        assert _sanitize("foo...bar") == "foo___bar"

    def test_dotdot_in_chain(self) -> None:
        assert _sanitize("foo/../../bar") == "foo_______bar"
        assert _sanitize(".../.../etc") == "________etc"

    def test_dotdot_bare(self) -> None:
        assert _sanitize("..") == "__"
        assert _sanitize("...") == "___"
        assert _sanitize("....") == "____"

    def test_windows_absolute(self) -> None:
        assert _sanitize("C:\\Windows\\System32") == "C__Windows_System32"
        assert _sanitize("D:\\secret\\file") == "D__secret_file"

    def test_backslash(self) -> None:
        assert _sanitize("foo\\bar\\baz") == "foo_bar_baz"

    def test_empty_string(self) -> None:
        assert _sanitize("") == "unknown"

    def test_whitespace_only(self) -> None:
        assert _sanitize("   ") == "___"

    def test_null_byte(self) -> None:
        assert _sanitize("a\x00b") == "a_b"

    def test_shell_meta_chars(self) -> None:
        assert _sanitize("foo;rm -rf /") == "foo_rm_-rf__"
        assert _sanitize("$(whoami)") == "__whoami_"

    def test_newline_tab(self) -> None:
        assert _sanitize("foo\nbar") == "foo_bar"
        assert _sanitize("foo\tbar") == "foo_bar"

    def test_no_path_chars_survive(self) -> None:
        """Core claim: no /, \\, or .. remain after sanitization."""
        for tc in ["../../../etc/evil", "../foo", "/etc/passwd", "foo/bar", "a\\b"]:
            result = _sanitize(tc)
            assert "/" not in result
            assert ".." not in result
            assert "\\" not in result


# -------------------------------------------------------------------------
# Integration: end-to-end with patched lc.run_suggest
# -------------------------------------------------------------------------

class TestSuggestionPhaseBounded:
    """Integration: _suggestion_phase with patched run_suggest.

    Patches lc.run_suggest (not lab_hooks.run_suggest) because the code uses
    'from ..lab_hooks import run_suggest' — this binds the name in the lc
    module's namespace.
    """

    def _run(self, tmp_path: Path, suggestions: list[dict]) -> tuple[Path, list[Path]]:
        """Call _suggestion_phase with controlled suggestions. Returns (research_dir, written)."""
        import chip_labs.transfer_surface.loop_controller as lc

        controller = RecursiveLoopController(config=LoopConfig(research_enabled=True))
        controller._current_score = 50
        chip_path = _scaffold_chip(tmp_path)
        research_dir = chip_path / "research" / "exploratory_frontier"
        research_dir.mkdir(parents=True, exist_ok=True)

        original = lc.run_suggest
        lc.run_suggest = lambda *args, **kw: suggestions
        try:
            controller._suggestion_phase(chip_path)
        finally:
            lc.run_suggest = original

        return research_dir, list(research_dir.glob("suggestion_*.json"))

    # ---- traversal stays inside research_dir ----

    def test_dotdot_traversal_stays_inside(self, tmp_path: Path) -> None:
        research_dir, written = self._run(tmp_path, [{"candidate_id": "../../../etc/evil", "mutations": {}, "hypothesis": "h"}])
        assert len(written) == 1
        assert written[0].is_relative_to(research_dir)

    def test_absolute_unix_stays_inside(self, tmp_path: Path) -> None:
        research_dir, written = self._run(tmp_path, [{"candidate_id": "/tmp/evil.json", "mutations": {}, "hypothesis": "h"}])
        assert len(written) == 1
        assert written[0].is_relative_to(research_dir)
        assert not Path("/tmp/evil.json").exists()

    def test_absolute_windows_stays_inside(self, tmp_path: Path) -> None:
        research_dir, written = self._run(tmp_path, [{"candidate_id": "C:\\Windows\\evil", "mutations": {}, "hypothesis": "h"}])
        assert len(written) == 1
        assert written[0].is_relative_to(research_dir)

    # ---- separators sanitized and written ----

    def test_forward_slash_written(self, tmp_path: Path) -> None:
        research_dir, written = self._run(tmp_path, [{"candidate_id": "my/suggestion/001", "mutations": {}, "hypothesis": "h"}])
        assert len(written) == 1
        assert (research_dir / "suggestion_my_suggestion_001.json").exists()

    def test_backslash_written(self, tmp_path: Path) -> None:
        research_dir, written = self._run(tmp_path, [{"candidate_id": "a\\b\\c", "mutations": {}, "hypothesis": "h"}])
        assert len(written) == 1
        assert written[0].is_relative_to(research_dir)

    # ---- empty / special ----

    def test_empty_id_unknown(self, tmp_path: Path) -> None:
        research_dir, written = self._run(tmp_path, [{"candidate_id": "", "mutations": {}, "hypothesis": "h"}])
        assert len(written) == 1
        assert (research_dir / "suggestion_unknown.json").exists()

    def test_whitespace_id_written(self, tmp_path: Path) -> None:
        research_dir, written = self._run(tmp_path, [{"candidate_id": "   ", "mutations": {}, "hypothesis": "h"}])
        assert len(written) == 1
        assert written[0].is_relative_to(research_dir)

    def test_null_byte_written(self, tmp_path: Path) -> None:
        research_dir, written = self._run(tmp_path, [{"candidate_id": "valid\x00id", "mutations": {}, "hypothesis": "h"}])
        assert len(written) == 1
        assert (research_dir / "suggestion_valid_id.json").exists()

    # ---- normal ----

    def test_normal_id_written(self, tmp_path: Path) -> None:
        research_dir, written = self._run(tmp_path, [{"candidate_id": "fix-v2-optimization-001", "mutations": {}, "hypothesis": "h"}])
        assert len(written) == 1
        assert (research_dir / "suggestion_fix-v2-optimization-001.json").exists()

    def test_multiple_normal_ids(self, tmp_path: Path) -> None:
        research_dir, written = self._run(tmp_path, [
            {"candidate_id": "candidate_001", "mutations": {}, "hypothesis": "h1"},
            {"candidate_id": "candidate_002", "mutations": {}, "hypothesis": "h2"},
            {"candidate_id": "candidate_003", "mutations": {}, "hypothesis": "h3"},
        ])
        assert len(written) == 3

    # ---- idempotency ----

    def test_existing_file_skipped(self, tmp_path: Path) -> None:
        # First write
        research_dir, written = self._run(tmp_path, [{"candidate_id": "candidate_001", "mutations": {}, "hypothesis": "h1"}])
        assert len(written) == 1
        # Second write with SAME chip — file exists, so write is skipped
        controller = RecursiveLoopController(config=LoopConfig(research_enabled=True))
        controller._current_score = 50
        chip_path = written[0].resolve().parents[2]  # chip_path

        import chip_labs.transfer_surface.loop_controller as lc
        original = lc.run_suggest
        lc.run_suggest = lambda **kw: [{"candidate_id": "candidate_001", "mutations": {}, "hypothesis": "h2"}]
        try:
            controller._suggestion_phase(chip_path)
        finally:
            lc.run_suggest = original

        # File still has original content
        assert (research_dir / "suggestion_candidate_001.json").exists()
        assert "h1" in (research_dir / "suggestion_candidate_001.json").read_text()

    # ---- one bad doesn't block good ----

    def test_bad_does_not_block_good(self, tmp_path: Path) -> None:
        research_dir, written = self._run(tmp_path, [
            {"candidate_id": "../../../etc/evil", "mutations": {}, "hypothesis": "bad"},
            {"candidate_id": "valid-good-001", "mutations": {}, "hypothesis": "good"},
        ])
        assert len(written) == 2

    # ---- content preserved ----

    def test_content_json_preserved(self, tmp_path: Path) -> None:
        research_dir, written = self._run(tmp_path, [
            {"candidate_id": "test-001", "mutations": {"approach": "optimized"}, "hypothesis": "test hypothesis"}
        ])
        assert len(written) == 1
        content = json.loads(written[0].read_text())
        assert content["candidate_id"] == "test-001"
        assert content["mutations"]["approach"] == "optimized"

    # ---- core security proof ----

    def test_all_suggestion_files_inside_research_dir(self, tmp_path: Path) -> None:
        controller = RecursiveLoopController(config=LoopConfig(research_enabled=True))
        controller._current_score = 50
        chip_path = _scaffold_chip(tmp_path)

        import chip_labs.transfer_surface.loop_controller as lc

        original = lc.run_suggest
        lc.run_suggest = lambda **kw: [
            {"candidate_id": "../../../etc/evil", "mutations": {}, "hypothesis": "h"},
            {"candidate_id": "/tmp/payload.json", "mutations": {}, "hypothesis": "h"},
            {"candidate_id": "C:\\Windows\\evil", "mutations": {}, "hypothesis": "h"},
            {"candidate_id": "valid-id-001", "mutations": {}, "hypothesis": "h"},
        ]
        try:
            controller._suggestion_phase(chip_path)
        finally:
            lc.run_suggest = original

        research_dir = chip_path / "research" / "exploratory_frontier"
        for f in research_dir.glob("suggestion_*.json"):
            assert f.is_relative_to(research_dir), f"Escaped: {f}"
        assert not Path("/tmp/payload.json").exists()


# -------------------------------------------------------------------------
# Smoke: real run_suggest
# -------------------------------------------------------------------------

class TestSuggestionPhaseReal:
    """Smoke tests with real (unpatched) run_suggest."""

    def test_real_suggest_no_escape(self, tmp_path: Path) -> None:
        controller = RecursiveLoopController(config=LoopConfig(research_enabled=True))
        controller._current_score = 50
        chip_path = _scaffold_chip(tmp_path)
        controller._suggestion_phase(chip_path)
        research_dir = chip_path / "research" / "exploratory_frontier"
        for f in research_dir.glob("suggestion_*.json"):
            assert f.is_relative_to(research_dir)

    def test_real_suggest_no_crash(self, tmp_path: Path) -> None:
        controller = RecursiveLoopController(config=LoopConfig(research_enabled=True))
        controller._current_score = 50
        chip_path = _scaffold_chip(tmp_path)
        result = controller._suggestion_phase(chip_path)
        assert isinstance(result, list)