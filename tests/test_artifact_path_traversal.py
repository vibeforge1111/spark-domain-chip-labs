"""
Tests for _resolve_external_artifact_path() path-traversal fix.

The function must never return a path that escapes run_base, regardless
of what the caller passes as `reference`.
"""

import pytest
from pathlib import Path
import tempfile
import os


# Inline the fixed implementation for isolated unit testing
def _find_repo_root(start: Path):
    for path in (start, *start.parents):
        if (path / ".git").exists():
            return path
    return None


def _resolve_external_artifact_path(run_path: Path, reference: str):
    reference_path = Path(reference)
    if reference_path.is_absolute():
        return None
    run_base = run_path.resolve()
    candidates = []
    candidates.append(run_base / reference_path)

    repo_root = _find_repo_root(run_base)
    if repo_root is not None:
        candidates.append(repo_root / reference_path)

    for candidate in candidates:
        resolved = candidate.resolve()
        try:
            resolved.relative_to(run_base)
        except ValueError:
            continue
        if resolved.exists():
            return resolved
    return None


class TestPathTraversalBlocked:
    def setup_method(self):
        self.tmp = tempfile.mkdtemp()
        self.run_base = Path(self.tmp) / "run"
        self.run_base.mkdir()
        # Create a legitimate artifact inside run_base
        (self.run_base / "output.json").write_text("{}")
        # Create a sensitive file OUTSIDE run_base
        self.secret = Path(self.tmp) / "secret.txt"
        self.secret.write_text("TOP SECRET")

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_absolute_path_rejected(self):
        result = _resolve_external_artifact_path(self.run_base, str(self.secret))
        assert result is None

    def test_dotdot_traversal_rejected(self):
        result = _resolve_external_artifact_path(self.run_base, "../secret.txt")
        assert result is None

    def test_deep_dotdot_traversal_rejected(self):
        result = _resolve_external_artifact_path(self.run_base, "../../etc/passwd")
        assert result is None

    def test_legitimate_relative_path_resolves(self):
        result = _resolve_external_artifact_path(self.run_base, "output.json")
        assert result is not None
        assert result.exists()

    def test_nonexistent_relative_path_returns_none(self):
        result = _resolve_external_artifact_path(self.run_base, "nonexistent.json")
        assert result is None

    def test_resolved_path_stays_within_run_base(self):
        result = _resolve_external_artifact_path(self.run_base, "output.json")
        assert result is not None
        # Must be within run_base
        result.relative_to(self.run_base)  # raises ValueError if outside

    def test_windows_style_absolute_path_rejected(self):
        # On Windows, C:\...\secret.txt is absolute; Path handles this cross-platform.
        abs_ref = os.path.abspath(str(self.secret))
        result = _resolve_external_artifact_path(self.run_base, abs_ref)
        assert result is None
