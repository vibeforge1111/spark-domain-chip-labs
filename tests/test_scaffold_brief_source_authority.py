from __future__ import annotations

import ast
import json
from pathlib import Path
import tomllib
from typing import Any

import pytest

from chip_labs.chip_factory.scaffold import scaffold_chip, validate_brief


def _brief(**overrides: Any) -> dict[str, Any]:
    brief: dict[str, Any] = {
        "domain_id": "safe-domain",
        "domain_name": "Safe Domain",
        "description": "A useful generated domain chip.",
        "category": "agent tooling",
        "primary_metric": "quality_score",
        "mutation_axes": [
            {"name": "strategy", "values": ["baseline", "frontier"]},
        ],
    }
    brief.update(overrides)
    return brief


@pytest.mark.parametrize(
    "domain_id",
    [
        None,
        7,
        "",
        "../escape",
        "9starts-with-digit",
        "class",
        "con",
        "a.b",
        "-dash",
        "a" * 65,
    ],
)
def test_scaffold_rejects_nonportable_domain_identity_before_writing(
    tmp_path: Path,
    domain_id: object,
) -> None:
    brief = _brief(domain_id=domain_id)

    assert validate_brief(brief)
    with pytest.raises(ValueError, match="Invalid brief"):
        scaffold_chip(brief, tmp_path)

    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize(
    "overrides",
    [
        {"domain_name": 7},
        {"primary_metric": []},
        {"description": {"nested": "value"}},
        {"category": ["unsafe"]},
        {"mutation_axes": "strategy"},
        {"mutation_axes": [{}]},
        {"mutation_axes": [{"name": "strategy", "values": "baseline"}]},
        {"mutation_axes": [{"name": "strategy", "values": ["ok", 7]}]},
    ],
)
def test_scaffold_rejects_non_text_source_shapes(
    tmp_path: Path,
    overrides: dict[str, object],
) -> None:
    brief = _brief(**overrides)

    assert validate_brief(brief)
    with pytest.raises(ValueError, match="Invalid brief"):
        scaffold_chip(brief, tmp_path)

    assert list(tmp_path.iterdir()) == []


def test_scaffold_encodes_adversarial_text_as_data_in_every_output_context(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    marker = tmp_path / "executed.txt"
    monkeypatch.chdir(tmp_path)
    payload = (
        '"""\n__import__("pathlib").Path("executed.txt").write_text("owned")'
        "\n# <script>alert(1)</script> `code`"
    )
    brief = _brief(
        domain_name=payload,
        description=payload,
        category=payload,
        primary_metric=payload,
        mutation_axes=[{"name": payload, "values": [payload]}],
    )

    chip_dir = scaffold_chip(brief, tmp_path)

    python_sources = sorted(chip_dir.rglob("*.py"))
    assert python_sources
    for path in python_sources:
        ast.parse(
            path.read_text(encoding="utf-8"),
            filename=str(path),
            feature_version=(3, 10),
        )
    tomllib.loads((chip_dir / "pyproject.toml").read_text(encoding="utf-8"))

    evaluate_namespace: dict[str, Any] = {}
    exec(
        compile(
            (chip_dir / "src" / "safe_domain" / "evaluate.py").read_text(encoding="utf-8"),
            "<generated-evaluate>",
            "exec",
        ),
        evaluate_namespace,
    )
    result = evaluate_namespace["evaluate"]({payload: payload})
    assert payload in result["metrics"]
    assert evaluate_namespace["DIMENSIONS"] == {payload: {payload: 2}}

    watchtower_namespace: dict[str, Any] = {}
    exec(
        compile(
            (chip_dir / "src" / "safe_domain" / "watchtower.py").read_text(encoding="utf-8"),
            "<generated-watchtower>",
            "exec",
        ),
        watchtower_namespace,
    )
    pages = watchtower_namespace["generate_watchtower_pages"]({})
    assert "&lt;script&gt;" in pages[0]["content"]
    assert "<script>" not in pages[0]["content"]

    manifest = json.loads((chip_dir / "spark-chip.json").read_text(encoding="utf-8"))
    assert manifest["name"] == payload
    for path in chip_dir.rglob("*.md"):
        assert "<script>" not in path.read_text(encoding="utf-8")
    assert not marker.exists()
