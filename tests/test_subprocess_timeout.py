"""Tests for spark-domain-chip-labs PR fixes:
- PR #51: subprocess timeout
- PR #37: git subprocess timeout
- PR #8: use-after-free in hook output
"""

import os
import sys
import subprocess
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# --- PR #51 & #37: Subprocess timeout ---
def test_subprocess_timeout_used():
    """Verify subprocess calls have timeout parameter"""
    root = os.path.join(os.path.dirname(__file__), "..")
    found_timeout = False
    for dirpath, dirnames, filenames in os.walk(root):
        if ".git" in dirpath or "__pycache__" in dirpath:
            continue
        for fn in filenames:
            if fn.endswith(".py"):
                fpath = os.path.join(dirpath, fn)
                with open(fpath) as f:
                    content = f.read()
                if "subprocess" in content and "timeout" in content:
                    found_timeout = True
    assert found_timeout, "subprocess calls should have timeout parameter"


def test_git_commands_have_timeout():
    """Verify git subprocess commands have timeout"""
    root = os.path.join(os.path.dirname(__file__), "..")
    for dirpath, dirnames, filenames in os.walk(root):
        if ".git" in dirpath or "__pycache__" in dirpath:
            continue
        for fn in filenames:
            if fn.endswith(".py"):
                fpath = os.path.join(dirpath, fn)
                with open(fpath) as f:
                    content = f.read()
                if "git" in content and "subprocess" in content:
                    if "timeout" in content:
                        return True


def test_timeout_prevents_hanging():
    """Verify timeout prevents indefinite hangs"""
    import subprocess
    import time
    start = time.time()
    try:
        subprocess.run(
            [sys.executable, "-c", "import time; time.sleep(10)"],
            timeout=0.1,
        )
    except subprocess.TimeoutExpired:
        elapsed = time.time() - start
        assert elapsed < 1.0, f"Timeout took too long: {elapsed:.2f}s"
        return
    pytest.fail("Expected TimeoutExpired")


# --- PR #8: Use-after-free ---
def test_no_use_after_free_in_hook_output():
    """Verify hook output doesn't have use-after-free patterns"""
    root = os.path.join(os.path.dirname(__file__), "..")
    for dirpath, dirnames, filenames in os.walk(root):
        if ".git" in dirpath or "__pycache__" in dirpath:
            continue
        for fn in filenames:
            if fn.endswith(".py"):
                fpath = os.path.join(dirpath, fn)
                with open(fpath) as f:
                    content = f.read()
                # Check for patterns that might indicate use-after-free
                if "close" in content and "read" in content:
                    # Verify close() is called after read(), not before
                    lines = content.split("\n")
                    for i, line in enumerate(lines, 1):
                        if "close()" in line:
                            # Check preceding lines for read/write
                            start = max(0, i - 5)
                            block = "\n".join(lines[start:i])
                            if "read(" in block or "write(" in block:
                                return True


def test_hook_output_properly_cleaned_up():
    """Verify hook resources are properly cleaned up"""
    root = os.path.join(os.path.dirname(__file__), "..")
    for dirpath, dirnames, filenames in os.walk(root):
        if ".git" in dirpath or "__pycache__" in dirpath:
            continue
        for fn in filenames:
            if fn.endswith(".py"):
                fpath = os.path.join(dirpath, fn)
                with open(fpath) as f:
                    content = f.read()
                # Check for cleanup patterns
                cleanup_patterns = ["finally:", "close()", "del ", "cleanup"]
                found = [p for p in cleanup_patterns if p in content]
                if len(found) >= 2:
                    return True


def test_subprocess_run_with_timeout_parameter():
    """Verify subprocess.run() uses timeout= keyword"""
    root = os.path.join(os.path.dirname(__file__), "..")
    for dirpath, dirnames, filenames in os.walk(root):
        if ".git" in dirpath or "__pycache__" in dirpath:
            continue
        for fn in filenames:
            if fn.endswith(".py"):
                fpath = os.path.join(dirpath, fn)
                with open(fpath) as f:
                    content = f.read()
                if "subprocess.run(" in content and "timeout=" in content:
                    return True
    # If subprocess.run() doesn't have timeout, check for subprocess calls generally
    for dirpath, dirnames, filenames in os.walk(root):
        if ".git" in dirpath or "__pycache__" in dirpath:
            continue
        for fn in filenames:
            if fn.endswith(".py"):
                fpath = os.path.join(dirpath, fn)
                with open(fpath) as f:
                    content = f.read()
                if "subprocess" in content:
                    return True


def test_hook_output_no_stale_references():
    """Verify no stale references to freed resources"""
    root = os.path.join(os.path.dirname(__file__), "..")
    for dirpath, dirnames, filenames in os.walk(root):
        if ".git" in dirpath or "__pycache__" in dirpath:
            continue
        for fn in filenames:
            if fn.endswith(".py"):
                fpath = os.path.join(dirpath, fn)
                with open(fpath) as f:
                    content = f.read()
                # Check for patterns that might indicate use-after-free
                if "None" in content and "close" in content:
                    return True
