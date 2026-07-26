"""Security regression tests for contributor-reported DSPy code generation flaws.

These tests exercise the public generator rather than mirroring its escaping
logic. They preserve the useful intent of PRs #55, #136, #183, #269, and #357.
"""

from __future__ import annotations

import ast

import pytest

from chip_labs.dspy_slot import DSpySlotConfig, generate_slot_script


ATTACK = '\"\"\"; import subprocess; subprocess.run(["id"]); payload = \"'


def test_all_config_strings_remain_data_in_generated_source() -> None:
    config = DSpySlotConfig(
        slot_name=ATTACK,
        model=ATTACK,
        task_description=ATTACK,
        input_fields={"question": ATTACK},
        output_fields={"answer": ATTACK},
        training_data_path=ATTACK,
    )

    script = generate_slot_script(config)
    tree = ast.parse(script)

    imported_modules = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    assert imported_modules == {"argparse", "dspy", "json", "os", "sys"}
    assert "subprocess" not in imported_modules
    assert ATTACK in {
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    }


@pytest.mark.parametrize(
    "field_name",
    [
        'question: str = dspy.InputField(); import os; x',
        "two words",
        "class",
        "9lives",
        "",
    ],
)
def test_input_field_names_must_be_unambiguous_python_identifiers(
    field_name: str,
) -> None:
    config = DSpySlotConfig(
        slot_name="safe",
        input_fields={field_name: "description"},
        output_fields={"answer": "description"},
    )

    with pytest.raises(ValueError, match="input field.*valid Python identifier"):
        generate_slot_script(config)


def test_output_field_name_must_be_an_unambiguous_python_identifier() -> None:
    config = DSpySlotConfig(
        slot_name="safe",
        input_fields={"question": "description"},
        output_fields={"answer; import os": "description"},
    )

    with pytest.raises(ValueError, match="output field.*valid Python identifier"):
        generate_slot_script(config)


@pytest.mark.parametrize("metric_name", ["score; import os", "lambda", "9score", ""])
def test_metric_name_must_be_a_python_identifier(metric_name: str) -> None:
    config = DSpySlotConfig(slot_name="safe", metric_name=metric_name)

    with pytest.raises(ValueError, match="metric name.*valid Python identifier"):
        generate_slot_script(config)


@pytest.mark.parametrize("value", ['0; import os', -1, True, 1.5])
def test_max_bootstrapped_demos_must_be_a_non_negative_integer(value: object) -> None:
    config = DSpySlotConfig(slot_name="safe", max_bootstrapped_demos=value)  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="non-negative integer"):
        generate_slot_script(config)
