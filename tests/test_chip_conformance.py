"""AP-21 read-only chip conformance tests."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

from chip_labs.chip_conformance import validate_chip_conformance
from chip_labs.chip_factory.scaffold import scaffold_chip


def _brief() -> dict[str, object]:
    return {
        "domain_id": "agent-safety-review",
        "domain_name": "Agent Safety Review",
        "category": "technology",
        "description": "Review agent plans for authority, evidence, and rollback safety.",
        "mutation_axes": [
            {"name": "review_depth", "values": ["fast", "standard", "strict"]},
            {"name": "risk_surface", "values": ["repo", "runtime", "network"]},
        ],
        "primary_metric": "safety_review_score",
    }


def _tree_fingerprint(path: Path) -> str:
    digest = hashlib.sha256()
    for item in sorted(p for p in path.rglob("*") if p.is_file()):
        digest.update(item.relative_to(path).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(item.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def test_conformance_passes_fresh_scaffold_without_mutating_tree(tmp_path: Path) -> None:
    chip_dir = scaffold_chip(_brief(), tmp_path)
    before = _tree_fingerprint(chip_dir)

    result = validate_chip_conformance(chip_dir)

    assert result["schema_version"] == "spark_chip.conformance.v1"
    assert result["read_only"] is True
    assert result["verdict"] == "pass"
    assert result["blocking_checks"] == []
    assert _tree_fingerprint(chip_dir) == before


def test_conformance_blocks_legacy_string_commands(tmp_path: Path) -> None:
    chip_dir = scaffold_chip(_brief(), tmp_path)
    manifest_path = chip_dir / "spark-chip.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["commands"]["evaluate"] = "python -m agent_safety_review evaluate"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    result = validate_chip_conformance(chip_dir)

    assert result["verdict"] == "blocked"
    assert "manifest.commands.evaluate" in result["blocking_checks"]


def test_cli_conformance_writes_json_and_fails_on_blocked(tmp_path: Path) -> None:
    chip_dir = scaffold_chip(_brief(), tmp_path)
    manifest_path = chip_dir / "spark-chip.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest.pop("requires_runtime")
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    output_path = tmp_path / "conformance.json"
    env = {**os.environ, "PYTHONPATH": str(Path.cwd() / "src")}

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "chip_labs.cli",
            "conformance",
            str(chip_dir),
            "--output",
            str(output_path),
            "--fail-on-blocked",
        ],
        cwd=Path.cwd(),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["verdict"] == "blocked"
    assert "manifest.required_keys" in payload["blocking_checks"]
