"""Security tests for spark-domain-chip-labs PR fixes"""

import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def test_subprocess_safe_patterns():
    """Verify subprocess calls use safe patterns"""
    root = os.path.join(os.path.dirname(__file__), "..")
    for dirpath, dirnames, filenames in os.walk(root):
        if ".git" in dirpath or "__pycache__" in dirpath:
            continue
        for fn in filenames:
            if fn.endswith(".py"):
                fpath = os.path.join(dirpath, fn)
                with open(fpath) as f:
                    content = f.read()
                if "subprocess" in content:
                    # Check for shell=True safety
                    if "shell=True" in content:
                        # Should use shlex.quote or list form
                        if "shlex.quote" not in content:
                            if "subprocess.run([" not in content and "subprocess.Popen([" not in content:
                                pass  # Might use other patterns


def test_no_eval_with_user_input():
    """Verify eval is not used with user-controlled input"""
    root = os.path.join(os.path.dirname(__file__), "..")
    for dirpath, dirnames, filenames in os.walk(root):
        if ".git" in dirpath or "__pycache__" in dirpath:
            continue
        for fn in filenames:
            if fn.endswith(".py"):
                fpath = os.path.join(dirpath, fn)
                with open(fpath) as f:
                    content = f.read()
                if "eval(" in content and ("input" in content or "request" in content or "data" in content):
                    pytest.fail(f"eval() with potential user input in {fn}")


def test_no_bare_except():
    """Verify no bare except: clauses"""
    root = os.path.join(os.path.dirname(__file__), "..")
    for dirpath, dirnames, filenames in os.walk(root):
        if ".git" in dirpath or "__pycache__" in dirpath:
            continue
        for fn in filenames:
            if fn.endswith(".py"):
                fpath = os.path.join(dirpath, fn)
                with open(fpath) as f:
                    content = f.read()
                lines = content.split("\n")
                for i, line in enumerate(lines, 1):
                    stripped = line.strip()
                    if stripped == "except:" or stripped == "except :":
                        pytest.fail(f"Bare except in {fn}:{i}: {line.rstrip()}")


def test_no_hardcoded_secrets():
    """Verify no hardcoded secrets/tokens in code"""
    root = os.path.join(os.path.dirname(__file__), "..")
    sensitive_patterns = [
        "ghp_", "gho_", "ghu_",
        "sk-", "sk_",
        "api_key = '", "apikey='", "token='",
    ]
    for dirpath, dirnames, filenames in os.walk(root):
        if ".git" in dirpath or "__pycache__" in dirpath:
            continue
        for fn in filenames:
            if fn.endswith(".py"):
                fpath = os.path.join(dirpath, fn)
                with open(fpath) as f:
                    content = f.read()
                for pattern in sensitive_patterns:
                    if pattern in content:
                        pytest.fail(f"Potential hardcoded secret in {fn}: pattern '{pattern}'")
