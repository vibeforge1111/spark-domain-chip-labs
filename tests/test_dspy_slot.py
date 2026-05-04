"""Tests for the DSPy slot framework.

Covers:
  - DSpySlotConfig dataclass
  - Script generation and syntax validation
  - Training data template generation
  - Config JSON serialization
  - DSPy integration detection
  - Scaffold into chip directories
  - Slot type listing
"""

from __future__ import annotations

import json
import textwrap
from pathlib import Path

import pytest

from chip_labs.dspy_slot import (
    DSpySlotConfig,
    SLOT_TYPES,
    detect_dspy_integration,
    generate_slot_config_json,
    generate_slot_script,
    generate_training_data_template,
    list_available_slot_types,
    scaffold_dspy_slot,
)


# =========================================================================
# TestDSpySlotConfig
# =========================================================================

class TestDSpySlotConfig:
    """Tests for the DSpySlotConfig dataclass."""

    def test_default_values(self):
        cfg = DSpySlotConfig(slot_name="test")
        assert cfg.slot_name == "test"
        assert cfg.model == "openai/gpt-4o-mini"
        assert cfg.task_description == ""
        assert cfg.input_fields == {}
        assert cfg.output_fields == {}
        assert cfg.training_data_path == "data/training.jsonl"
        assert cfg.max_bootstrapped_demos == 4
        assert cfg.metric_name == "accuracy"

    def test_custom_values(self):
        cfg = DSpySlotConfig(
            slot_name="custom",
            model="anthropic/claude-3",
            task_description="A custom task",
            input_fields={"query": "search query"},
            output_fields={"answer": "the answer"},
            training_data_path="custom/train.jsonl",
            max_bootstrapped_demos=8,
            metric_name="f1",
        )
        assert cfg.slot_name == "custom"
        assert cfg.model == "anthropic/claude-3"
        assert cfg.task_description == "A custom task"
        assert cfg.input_fields == {"query": "search query"}
        assert cfg.output_fields == {"answer": "the answer"}
        assert cfg.training_data_path == "custom/train.jsonl"
        assert cfg.max_bootstrapped_demos == 8
        assert cfg.metric_name == "f1"

    def test_all_field_types_present(self):
        """Every attribute on the dataclass is accessible."""
        cfg = DSpySlotConfig(slot_name="t")
        expected_attrs = [
            "slot_name", "model", "task_description",
            "input_fields", "output_fields", "training_data_path",
            "max_bootstrapped_demos", "metric_name",
        ]
        for attr in expected_attrs:
            assert hasattr(cfg, attr), f"Missing attribute: {attr}"

    def test_mutable_defaults_are_independent(self):
        """Each instance gets its own dict, not a shared reference."""
        a = DSpySlotConfig(slot_name="a")
        b = DSpySlotConfig(slot_name="b")
        a.input_fields["x"] = "y"
        assert "x" not in b.input_fields


# =========================================================================
# TestGenerateSlotScript
# =========================================================================

class TestGenerateSlotScript:
    """Tests for generate_slot_script()."""

    @pytest.fixture()
    def basic_config(self) -> DSpySlotConfig:
        return DSpySlotConfig(
            slot_name="test_slot",
            task_description="A basic test slot",
            input_fields={"question": "the question"},
            output_fields={"answer": "the answer"},
        )

    def test_valid_python_syntax(self, basic_config):
        code = generate_slot_script(basic_config)
        # Must not raise
        compile(code, "<test>", "exec")

    def test_contains_import_dspy(self, basic_config):
        code = generate_slot_script(basic_config)
        assert "import dspy" in code

    def test_contains_input_fields(self, basic_config):
        code = generate_slot_script(basic_config)
        assert "question" in code

    def test_contains_output_fields(self, basic_config):
        code = generate_slot_script(basic_config)
        assert "answer" in code

    def test_has_train_function(self, basic_config):
        code = generate_slot_script(basic_config)
        assert "def train(" in code

    def test_has_evaluate_function(self, basic_config):
        code = generate_slot_script(basic_config)
        assert "def evaluate(" in code

    def test_has_run_function(self, basic_config):
        code = generate_slot_script(basic_config)
        assert "def run(" in code

    def test_has_argparse_cli(self, basic_config):
        code = generate_slot_script(basic_config)
        assert "argparse" in code
        assert "ArgumentParser" in code
        assert "add_subparsers" in code

    def test_has_all_subcommands(self, basic_config):
        code = generate_slot_script(basic_config)
        assert '"train"' in code
        assert '"evaluate"' in code
        assert '"run"' in code

    def test_contains_chain_of_thought(self, basic_config):
        code = generate_slot_script(basic_config)
        assert "ChainOfThought" in code

    def test_contains_bootstrap_few_shot(self, basic_config):
        code = generate_slot_script(basic_config)
        assert "BootstrapFewShot" in code

    def test_uses_env_var_for_model(self, basic_config):
        code = generate_slot_script(basic_config)
        assert "DSPY_MODEL" in code

    def test_contains_signature_class(self, basic_config):
        code = generate_slot_script(basic_config)
        assert "class TestSlotSignature(dspy.Signature):" in code

    def test_contains_module_class(self, basic_config):
        code = generate_slot_script(basic_config)
        assert "class TestSlotModule(dspy.Module):" in code

    def test_multiple_input_output_fields(self):
        cfg = DSpySlotConfig(
            slot_name="multi",
            input_fields={"a": "field a", "b": "field b", "c": "field c"},
            output_fields={"x": "result x", "y": "result y"},
        )
        code = generate_slot_script(cfg)
        compile(code, "<test>", "exec")
        for f in ["a", "b", "c", "x", "y"]:
            assert f in code

    def test_empty_fields_still_compiles(self):
        cfg = DSpySlotConfig(slot_name="empty")
        code = generate_slot_script(cfg)
        compile(code, "<test>", "exec")

    def test_slot_types_all_compile(self):
        """Every pre-built slot type produces valid Python."""
        for slot_name, slot_def in SLOT_TYPES.items():
            cfg = DSpySlotConfig(
                slot_name=slot_name,
                task_description=slot_def["task_description"],
                input_fields=dict(slot_def["input_fields"]),
                output_fields=dict(slot_def["output_fields"]),
            )
            code = generate_slot_script(cfg)
            compile(code, f"<test:{slot_name}>", "exec")

    def test_custom_metric_name(self):
        cfg = DSpySlotConfig(
            slot_name="custom_metric",
            input_fields={"q": "query"},
            output_fields={"a": "answer"},
            metric_name="custom_f1",
        )
        code = generate_slot_script(cfg)
        assert "def custom_f1(" in code
        compile(code, "<test>", "exec")

    def test_custom_model(self):
        cfg = DSpySlotConfig(
            slot_name="model_test",
            model="anthropic/claude-opus-4-6",
            input_fields={"q": "query"},
            output_fields={"a": "answer"},
        )
        code = generate_slot_script(cfg)
        assert "anthropic/claude-opus-4-6" in code

    def test_main_block(self, basic_config):
        code = generate_slot_script(basic_config)
        assert 'if __name__ == "__main__":' in code
        assert "main()" in code


# =========================================================================
# TestGenerateTrainingData
# =========================================================================

class TestGenerateTrainingData:
    """Tests for generate_training_data_template()."""

    @pytest.fixture()
    def config_with_fields(self) -> DSpySlotConfig:
        return DSpySlotConfig(
            slot_name="train_test",
            input_fields={"doc": "document text", "lane": "evidence lane"},
            output_fields={"claim": "extracted claim", "confidence": "score"},
        )

    def test_valid_jsonl(self, config_with_fields):
        data = generate_training_data_template(config_with_fields)
        lines = [line for line in data.strip().split("\n") if line.strip()]
        for line in lines:
            parsed = json.loads(line)
            assert isinstance(parsed, dict)

    def test_fields_match_config(self, config_with_fields):
        data = generate_training_data_template(config_with_fields)
        expected_keys = set(config_with_fields.input_fields) | set(config_with_fields.output_fields)
        lines = [line for line in data.strip().split("\n") if line.strip()]
        for line in lines:
            parsed = json.loads(line)
            assert set(parsed.keys()) == expected_keys

    def test_has_three_examples(self, config_with_fields):
        data = generate_training_data_template(config_with_fields)
        lines = [line for line in data.strip().split("\n") if line.strip()]
        assert len(lines) == 3

    def test_empty_fields_produces_empty_objects(self):
        cfg = DSpySlotConfig(slot_name="empty")
        data = generate_training_data_template(cfg)
        lines = [line for line in data.strip().split("\n") if line.strip()]
        assert len(lines) == 3
        for line in lines:
            parsed = json.loads(line)
            assert parsed == {}

    def test_values_are_strings(self, config_with_fields):
        data = generate_training_data_template(config_with_fields)
        for line in data.strip().split("\n"):
            if not line.strip():
                continue
            parsed = json.loads(line)
            for v in parsed.values():
                assert isinstance(v, str)


# =========================================================================
# TestGenerateSlotConfigJson
# =========================================================================

class TestGenerateSlotConfigJson:
    """Tests for generate_slot_config_json()."""

    def test_valid_json(self):
        cfg = DSpySlotConfig(slot_name="json_test")
        result = generate_slot_config_json(cfg)
        parsed = json.loads(result)
        assert isinstance(parsed, dict)

    def test_contains_all_fields(self):
        cfg = DSpySlotConfig(
            slot_name="full",
            input_fields={"a": "aa"},
            output_fields={"b": "bb"},
        )
        result = generate_slot_config_json(cfg)
        parsed = json.loads(result)
        assert parsed["slot_name"] == "full"
        assert parsed["input_fields"] == {"a": "aa"}
        assert parsed["output_fields"] == {"b": "bb"}
        assert "model" in parsed
        assert "metric_name" in parsed


# =========================================================================
# TestDetectDspyIntegration
# =========================================================================

class TestDetectDspyIntegration:
    """Tests for detect_dspy_integration()."""

    def test_no_dspy(self, tmp_path):
        """Chip with no DSPy artifacts returns has_dspy=False."""
        (tmp_path / "src" / "mymod").mkdir(parents=True)
        (tmp_path / "src" / "mymod" / "__init__.py").write_text("")
        (tmp_path / "src" / "mymod" / "evaluate.py").write_text("def evaluate(): pass")

        result = detect_dspy_integration(tmp_path)
        assert result["has_dspy"] is False
        assert result["slots"] == []
        assert result["config_path"] is None
        assert result["scripts"] == []

    def test_detects_config_json(self, tmp_path):
        """Finds dspy_config.json and sets has_dspy=True."""
        config = {"slot_name": "my_slot", "model": "openai/gpt-4o-mini"}
        (tmp_path / "dspy_config.json").write_text(json.dumps(config))

        result = detect_dspy_integration(tmp_path)
        assert result["has_dspy"] is True
        assert result["config_path"] is not None
        assert "my_slot" in result["slots"]

    def test_detects_import_in_src(self, tmp_path):
        """Finds 'import dspy' in src/**/*.py."""
        src = tmp_path / "src" / "mymod"
        src.mkdir(parents=True)
        (src / "__init__.py").write_text("")
        (src / "slot.py").write_text("import dspy\n\nclass MySig(dspy.Signature):\n    pass\n")

        result = detect_dspy_integration(tmp_path)
        assert result["has_dspy"] is True
        assert len(result["scripts"]) >= 1

    def test_detects_dspy_slot_files(self, tmp_path):
        """Finds dspy_slot_*.py files."""
        src = tmp_path / "src" / "mymod"
        src.mkdir(parents=True)
        (src / "dspy_slot_extractor.py").write_text("# placeholder")

        result = detect_dspy_integration(tmp_path)
        assert result["has_dspy"] is True
        assert "extractor" in result["slots"]

    def test_empty_directory(self, tmp_path):
        result = detect_dspy_integration(tmp_path)
        assert result["has_dspy"] is False

    def test_config_json_with_list(self, tmp_path):
        """Config JSON can be a list of slot configs."""
        config = [
            {"slot_name": "slot_a"},
            {"slot_name": "slot_b"},
        ]
        (tmp_path / "dspy_config.json").write_text(json.dumps(config))

        result = detect_dspy_integration(tmp_path)
        assert result["has_dspy"] is True
        assert "slot_a" in result["slots"]
        assert "slot_b" in result["slots"]


# =========================================================================
# TestScaffoldDspySlot
# =========================================================================

class TestScaffoldDspySlot:
    """Tests for scaffold_dspy_slot()."""

    def _make_chip(self, tmp_path: Path, module_name: str = "mymod") -> Path:
        """Create a minimal chip directory."""
        chip = tmp_path / "domain-chip-test"
        chip.mkdir(parents=True, exist_ok=True)
        src = chip / "src" / module_name
        src.mkdir(parents=True)
        (src / "__init__.py").write_text('"""test chip"""')
        (chip / "pyproject.toml").write_text(
            textwrap.dedent("""\
                [project]
                name = "domain-chip-test"
                version = "0.1.0"
            """)
        )
        return chip

    def test_creates_expected_files(self, tmp_path):
        chip = self._make_chip(tmp_path)
        result = scaffold_dspy_slot(chip, "packet_extractor")
        assert "script" in result
        assert "training_data" in result
        assert "config" in result
        assert result["script"].exists()
        assert result["training_data"].exists()
        assert result["config"].exists()

    def test_packet_extractor_slot(self, tmp_path):
        chip = self._make_chip(tmp_path)
        result = scaffold_dspy_slot(chip, "packet_extractor")
        script_content = result["script"].read_text(encoding="utf-8")
        compile(script_content, "<test>", "exec")
        assert "document" in script_content
        assert "evidence_lane" in script_content

    def test_doctrine_evaluator_slot(self, tmp_path):
        chip = self._make_chip(tmp_path)
        result = scaffold_dspy_slot(chip, "doctrine_evaluator")
        script_content = result["script"].read_text(encoding="utf-8")
        compile(script_content, "<test>", "exec")
        assert "doctrine" in script_content
        assert "verdict" in script_content

    def test_contradiction_detector_slot(self, tmp_path):
        chip = self._make_chip(tmp_path)
        result = scaffold_dspy_slot(chip, "contradiction_detector")
        script_content = result["script"].read_text(encoding="utf-8")
        compile(script_content, "<test>", "exec")
        assert "belief_a" in script_content
        assert "is_contradictory" in script_content

    def test_idempotent(self, tmp_path):
        """Second scaffold call does not crash or overwrite."""
        chip = self._make_chip(tmp_path)
        result1 = scaffold_dspy_slot(chip, "packet_extractor")
        content1 = result1["script"].read_text(encoding="utf-8")
        # Second call -- should not raise
        result2 = scaffold_dspy_slot(chip, "packet_extractor")
        content2 = result2["script"].read_text(encoding="utf-8")
        assert content1 == content2  # Not overwritten

    def test_generated_scripts_compile(self, tmp_path):
        """All built-in slot types produce compilable scripts."""
        for slot_type in SLOT_TYPES:
            chip = self._make_chip(tmp_path / slot_type)
            result = scaffold_dspy_slot(chip, slot_type)
            code = result["script"].read_text(encoding="utf-8")
            compile(code, f"<test:{slot_type}>", "exec")

    def test_training_data_is_valid_jsonl(self, tmp_path):
        chip = self._make_chip(tmp_path)
        result = scaffold_dspy_slot(chip, "packet_extractor")
        data = result["training_data"].read_text(encoding="utf-8")
        lines = [line for line in data.strip().split("\n") if line.strip()]
        assert len(lines) == 3
        for line in lines:
            json.loads(line)  # Must not raise

    def test_config_json_is_valid(self, tmp_path):
        chip = self._make_chip(tmp_path)
        result = scaffold_dspy_slot(chip, "packet_extractor")
        config = json.loads(result["config"].read_text(encoding="utf-8"))
        assert config["slot_name"] == "packet_extractor"

    def test_config_overrides(self, tmp_path):
        chip = self._make_chip(tmp_path)
        result = scaffold_dspy_slot(
            chip, "packet_extractor",
            config_overrides={"model": "anthropic/claude-3", "max_bootstrapped_demos": 10},
        )
        config = json.loads(result["config"].read_text(encoding="utf-8"))
        assert config["model"] == "anthropic/claude-3"
        assert config["max_bootstrapped_demos"] == 10

    def test_custom_slot_type(self, tmp_path):
        chip = self._make_chip(tmp_path)
        result = scaffold_dspy_slot(
            chip, "my_custom_slot",
            config_overrides={
                "task_description": "Custom task",
                "input_fields": {"inp": "input desc"},
                "output_fields": {"out": "output desc"},
            },
        )
        assert result["script"].exists()
        code = result["script"].read_text(encoding="utf-8")
        compile(code, "<test>", "exec")

    def test_detects_module_from_pyproject(self, tmp_path):
        chip = self._make_chip(tmp_path, module_name="domain_chip_test")
        result = scaffold_dspy_slot(chip, "packet_extractor")
        # Script should be under src/domain_chip_test/
        assert "domain_chip_test" in str(result["script"])


# =========================================================================
# TestListSlotTypes
# =========================================================================

class TestListSlotTypes:
    """Tests for list_available_slot_types()."""

    def test_returns_all_three(self):
        types = list_available_slot_types()
        assert len(types) == 3

    def test_has_name_and_description(self):
        types = list_available_slot_types()
        for t in types:
            assert "name" in t
            assert "description" in t
            assert isinstance(t["name"], str)
            assert isinstance(t["description"], str)
            assert len(t["description"]) > 0

    def test_expected_names(self):
        types = list_available_slot_types()
        names = {t["name"] for t in types}
        assert names == {"packet_extractor", "doctrine_evaluator", "contradiction_detector"}

    def test_descriptions_are_unique(self):
        types = list_available_slot_types()
        descriptions = [t["description"] for t in types]
        assert len(descriptions) == len(set(descriptions))
