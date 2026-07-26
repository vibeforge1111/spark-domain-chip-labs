"""Bounded structural analysis for generated chip source trees."""

from __future__ import annotations

import ast
from pathlib import Path

from .file_scan import ScanBudget, iter_bounded_files, read_text_bounded


_NESTED_SCOPES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)


def _has_owned_return(function: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    pending: list[ast.AST] = list(function.body)
    while pending:
        node = pending.pop()
        if isinstance(node, ast.Return):
            return True
        if isinstance(node, _NESTED_SCOPES):
            continue
        pending.extend(ast.iter_child_nodes(node))
    return False


def has_scoring_function(src_dir: Path, *, budget: ScanBudget | None = None) -> bool:
    """Return whether bounded Python ASTs contain score/evaluate with a return."""
    work = budget or ScanBudget()
    for path in iter_bounded_files([src_dir], suffixes={".py"}, budget=work):
        source = read_text_bounded(path, budget=work)
        if not source:
            continue
        try:
            tree = ast.parse(source, filename=str(path))
        except (SyntaxError, ValueError):
            continue
        for node in ast.walk(tree):
            if (
                isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                and node.name in {"score", "evaluate"}
                and _has_owned_return(node)
            ):
                return True
    return False
