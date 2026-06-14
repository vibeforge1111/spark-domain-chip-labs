"""AP-20 spark-chip v2 schema and scaffold acceptance tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from chip_labs.chip_factory.scaffold import scaffold_chip


SCHEMA_PATH = Path("docs/creator_system/schemas/spark-chip.v2.schema.json")


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


def test_spark_chip_v2_schema_is_valid_draft_2020_12() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    jsonschema.Draft202012Validator.check_schema(schema)
    assert schema["$id"] == "https://sparkswarm.ai/schemas/spark-chip/spark-chip.v2.schema.json"


def test_scaffold_emits_spark_chip_v2_manifest_validating_against_schema(tmp_path: Path) -> None:
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    chip_dir = scaffold_chip(_brief(), tmp_path)
    manifest = json.loads((chip_dir / "spark-chip.json").read_text(encoding="utf-8"))

    jsonschema.Draft202012Validator(schema).validate(manifest)
    assert manifest["manifest_version"] == 2
    assert manifest["schema_version"] == "spark-chip.v2"
    assert manifest["chip_name"] == "agent-safety-review"
    assert manifest["requires_runtime"] == {"spark-intelligence-builder": ">=0.1.0"}
    assert isinstance(manifest["commands"]["evaluate"], list)
    assert "agent" in manifest["task_topics"]
    assert "safety" in manifest["task_keywords"]


def test_spark_chip_v2_schema_rejects_legacy_string_commands(tmp_path: Path) -> None:
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    chip_dir = scaffold_chip(_brief(), tmp_path)
    manifest = json.loads((chip_dir / "spark-chip.json").read_text(encoding="utf-8"))
    manifest["commands"]["evaluate"] = "python -m agent_safety_review evaluate"

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate(manifest)
