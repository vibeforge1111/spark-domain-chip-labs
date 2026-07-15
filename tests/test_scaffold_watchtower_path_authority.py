from __future__ import annotations

import argparse
import ast
from pathlib import Path, PureWindowsPath
from types import SimpleNamespace
from typing import Any

import pytest

from chip_labs.chip_factory.scaffold import _gen_cli


BRIEF = {
    "domain_id": "vault-authority",
    "domain_name": "Vault Authority",
    "primary_metric": "quality_score",
}


def _generated_namespace(*function_names: str) -> tuple[str, dict[str, Any]]:
    source = _gen_cli(BRIEF)
    tree = ast.parse(source)
    selected = [
        node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name in function_names
    ]
    assert {node.name for node in selected} == set(function_names)
    namespace: dict[str, Any] = {
        "Any": Any,
        "Path": Path,
        "PureWindowsPath": PureWindowsPath,
        "argparse": argparse,
    }
    exec(compile(ast.Module(body=selected, type_ignores=[]), "<generated-cli>", "exec"), namespace)
    return source, namespace


@pytest.mark.parametrize(
    "vault_dir",
    ["", "   ", "../outside", "vault/../../outside", "/tmp/outside", r"C:\\outside"],
)
def test_generated_vault_resolver_rejects_nonlocal_paths(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    vault_dir: str,
) -> None:
    _source, namespace = _generated_namespace("_resolve_vault_path")
    monkeypatch.chdir(tmp_path)

    with pytest.raises(ValueError, match="invalid vault directory"):
        namespace["_resolve_vault_path"](vault_dir)


def test_generated_vault_resolver_rejects_symlink_escape(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _source, namespace = _generated_namespace("_resolve_vault_path")
    outside = tmp_path.parent / f"{tmp_path.name}-outside"
    outside.mkdir()
    link = tmp_path / "vault"
    try:
        link.symlink_to(outside, target_is_directory=True)
    except OSError as exc:
        outside.rmdir()
        pytest.skip(f"symlinks unavailable: {exc}")
    monkeypatch.chdir(tmp_path)
    try:
        with pytest.raises(ValueError, match="invalid vault directory"):
            namespace["_resolve_vault_path"]("vault")
    finally:
        link.unlink(missing_ok=True)
        outside.rmdir()


def test_generated_watchtower_rejects_page_escape_before_write(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    source, namespace = _generated_namespace(
        "_resolve_vault_path",
        "_resolve_vault_page_path",
        "cmd_watchtower",
    )
    monkeypatch.chdir(tmp_path)
    namespace["_load_input"] = lambda _path: {"mutations": {}, "vault_dir": "vault"}
    namespace["generate_watchtower_pages"] = lambda _mutations, *, vault_dir: [
        {"path": "../outside.md", "content": "nope"}
    ]
    namespace["_write_output"] = lambda _path, _data: None

    with pytest.raises(ValueError, match="invalid watchtower page path"):
        namespace["cmd_watchtower"](SimpleNamespace(input=None, output=None))

    assert not (tmp_path / "outside.md").exists()
    assert "startswith(" not in source


def test_generated_watchtower_writes_valid_nested_page(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _source, namespace = _generated_namespace(
        "_resolve_vault_path",
        "_resolve_vault_page_path",
        "cmd_watchtower",
    )
    monkeypatch.chdir(tmp_path)
    namespace["_load_input"] = lambda _path: {"mutations": {}, "vault_dir": "vault"}
    namespace["generate_watchtower_pages"] = lambda _mutations, *, vault_dir: [
        {"path": "dashboards/Home.md", "content": "safe"}
    ]
    written: list[dict[str, Any]] = []
    namespace["_write_output"] = lambda _path, data: written.append(data)

    namespace["cmd_watchtower"](SimpleNamespace(input=None, output=None))

    assert (tmp_path / "vault" / "dashboards" / "Home.md").read_text() == "safe"
    assert written == [{"pages": ["dashboards/Home.md"], "count": 1}]
