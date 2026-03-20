"""DSPy slot framework -- generates DSPy-compatible training/inference scripts.

This module does NOT import dspy. It GENERATES runnable Python scripts that
any domain chip can plug into for structured LLM optimization via DSPy.

Slot types:
  - packet_extractor: Extract structured evidence packets from research docs
  - doctrine_evaluator: Evaluate whether doctrine improves decisions
  - contradiction_detector: Detect contradictions between beliefs

Zero external dependencies.
"""

from __future__ import annotations

import json
import re
import textwrap
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Configuration dataclass
# ---------------------------------------------------------------------------

@dataclass
class DSpySlotConfig:
    """Configuration for a DSPy slot script."""

    slot_name: str
    model: str = "openai/gpt-4o-mini"
    task_description: str = ""
    input_fields: dict[str, str] = field(default_factory=dict)
    output_fields: dict[str, str] = field(default_factory=dict)
    training_data_path: str = "data/training.jsonl"
    max_bootstrapped_demos: int = 4
    metric_name: str = "accuracy"


# ---------------------------------------------------------------------------
# Pre-built slot types
# ---------------------------------------------------------------------------

SLOT_TYPES: dict[str, dict[str, Any]] = {
    "packet_extractor": {
        "description": "Extract structured evidence packets from research documents",
        "task_description": (
            "Given a research document and an evidence lane, extract a structured "
            "evidence packet with claim, mechanism, boundary, and confidence."
        ),
        "input_fields": {
            "document": "The full text of the research document to extract from",
            "evidence_lane": "Which evidence lane to target (research_grounded, benchmark_grounded, exploratory_frontier, realworld_validated)",
        },
        "output_fields": {
            "claim": "The core factual claim extracted from the document",
            "mechanism": "The causal mechanism or reasoning behind the claim",
            "boundary": "Known limitations or boundary conditions of the claim",
            "confidence": "Confidence level from 0.0 to 1.0 based on evidence strength",
        },
    },
    "doctrine_evaluator": {
        "description": "Evaluate whether doctrine improves decisions",
        "task_description": (
            "Given a doctrine statement and domain context, evaluate whether "
            "the doctrine would improve decision quality in that context."
        ),
        "input_fields": {
            "doctrine": "The doctrine statement to evaluate",
            "context": "The domain context in which the doctrine would be applied",
        },
        "output_fields": {
            "verdict": "One of: approve, defer, reject",
            "reasoning": "Detailed reasoning for the verdict",
            "improvement_suggestion": "How the doctrine could be improved if not approved",
        },
    },
    "contradiction_detector": {
        "description": "Detect contradictions between beliefs",
        "task_description": (
            "Given two belief statements, determine whether they contradict "
            "each other and if so, suggest a resolution."
        ),
        "input_fields": {
            "belief_a": "The first belief statement",
            "belief_b": "The second belief statement",
        },
        "output_fields": {
            "is_contradictory": "yes or no",
            "explanation": "Explanation of why the beliefs do or do not contradict",
            "resolution": "Suggested resolution if contradictory, or N/A",
        },
    },
}


# ---------------------------------------------------------------------------
# Code generation helpers
# ---------------------------------------------------------------------------

def _sanitize_name(name: str) -> str:
    """Convert a slot name to a valid Python identifier."""
    return re.sub(r"[^a-z0-9_]", "_", name.lower().replace("-", "_"))


def _class_name(name: str) -> str:
    """Convert a slot name to PascalCase class name."""
    parts = re.split(r"[_\-\s]+", name)
    return "".join(p.capitalize() for p in parts if p)


# ---------------------------------------------------------------------------
# Script generation
# ---------------------------------------------------------------------------

def generate_slot_script(config: DSpySlotConfig) -> str:
    """Generate a complete runnable DSPy Python script from a slot config.

    The generated script includes:
      - dspy import and LM configuration
      - A Signature class with configured input/output fields
      - A Module class using ChainOfThought
      - train() using BootstrapFewShot
      - evaluate() for metric evaluation
      - run() for single inference
      - CLI with argparse (train / evaluate / run subcommands)

    Returns:
        A string containing syntactically valid Python source code.

    Raises:
        ValueError: If the generated code fails to compile.
    """
    safe_name = _sanitize_name(config.slot_name)
    cls_name = _class_name(config.slot_name)
    sig_cls = f"{cls_name}Signature"
    mod_cls = f"{cls_name}Module"

    # Build signature field lines (already at class-body indent level)
    input_field_lines = []
    for fname, fdesc in config.input_fields.items():
        input_field_lines.append(
            f'    {fname}: str = dspy.InputField(desc="{fdesc}")'
        )

    output_field_lines = []
    for fname, fdesc in config.output_fields.items():
        output_field_lines.append(
            f'    {fname}: str = dspy.OutputField(desc="{fdesc}")'
        )

    input_block = "\n".join(input_field_lines) if input_field_lines else "    pass"
    output_block = "\n".join(output_field_lines) if output_field_lines else "    pass"

    # Build example loading keys
    input_keys = list(config.input_fields.keys())

    # Build the run() keyword args
    run_kwargs = ", ".join(f'{k}=args.{k}' for k in input_keys) if input_keys else ""

    # Build argparse arguments for the run subcommand (at function-body indent)
    run_arg_lines = []
    for k in input_keys:
        run_arg_lines.append(
            f'    run_parser.add_argument("--{k}", required=True, help="{config.input_fields[k]}")'
        )
    run_args_block = "\n".join(run_arg_lines) if run_arg_lines else "    pass  # no input fields"

    # Build metric comparison
    output_keys = list(config.output_fields.keys())
    if output_keys:
        metric_checks = " and ".join(
            f"pred.{k} == example.{k}" for k in output_keys
        )
    else:
        metric_checks = "True"

    task_desc_escaped = config.task_description.replace('"', '\\"')

    # Build the with_inputs() call argument
    with_inputs_arg = ", ".join(f'"{k}"' for k in input_keys)

    # Assemble script parts -- no textwrap.dedent, just raw top-level code
    parts: list[str] = []

    parts.append(f'#!/usr/bin/env python3\n"""DSPy slot script: {config.slot_name}\n\n{config.task_description}\n\nGenerated by spark-domain-chip-labs dspy_slot framework.\n"""')
    parts.append("")
    parts.append("import argparse")
    parts.append("import json")
    parts.append("import os")
    parts.append("import sys")
    parts.append("")
    parts.append("import dspy")
    parts.append("")
    parts.append("")
    parts.append("# ---------------------------------------------------------------------------")
    parts.append("# Configuration")
    parts.append("# ---------------------------------------------------------------------------")
    parts.append("")
    parts.append(f'SLOT_NAME = "{safe_name}"')
    parts.append(f'MODEL = os.environ.get("DSPY_MODEL", "{config.model}")')
    parts.append(f'TRAINING_DATA_PATH = "{config.training_data_path}"')
    parts.append(f"MAX_BOOTSTRAPPED_DEMOS = {config.max_bootstrapped_demos}")
    parts.append(f'TASK_DESCRIPTION = "{task_desc_escaped}"')
    parts.append("")
    parts.append("")
    parts.append("# ---------------------------------------------------------------------------")
    parts.append("# Signature")
    parts.append("# ---------------------------------------------------------------------------")
    parts.append("")
    parts.append(f"class {sig_cls}(dspy.Signature):")
    parts.append(f'    """{config.task_description or config.slot_name}"""')
    parts.append("")
    parts.append(input_block)
    parts.append(output_block)
    parts.append("")
    parts.append("")
    parts.append("# ---------------------------------------------------------------------------")
    parts.append("# Module")
    parts.append("# ---------------------------------------------------------------------------")
    parts.append("")
    parts.append(f"class {mod_cls}(dspy.Module):")
    parts.append(f'    """DSPy module for {config.slot_name}."""')
    parts.append("")
    parts.append("    def __init__(self):")
    parts.append("        super().__init__()")
    parts.append(f"        self.chain = dspy.ChainOfThought({sig_cls})")
    parts.append("")
    parts.append("    def forward(self, **kwargs):")
    parts.append("        return self.chain(**kwargs)")
    parts.append("")
    parts.append("")
    parts.append("# ---------------------------------------------------------------------------")
    parts.append("# Metric")
    parts.append("# ---------------------------------------------------------------------------")
    parts.append("")
    parts.append(f"def {config.metric_name}(example, pred, trace=None):")
    parts.append('    """Metric function for evaluating predictions."""')
    parts.append(f"    return {metric_checks}")
    parts.append("")
    parts.append("")
    parts.append("# ---------------------------------------------------------------------------")
    parts.append("# Data loading")
    parts.append("# ---------------------------------------------------------------------------")
    parts.append("")
    parts.append("def load_training_data(path=None):")
    parts.append('    """Load training examples from JSONL file."""')
    parts.append("    path = path or TRAINING_DATA_PATH")
    parts.append("    examples = []")
    parts.append('    with open(path, "r", encoding="utf-8") as f:')
    parts.append("        for line in f:")
    parts.append("            line = line.strip()")
    parts.append("            if not line:")
    parts.append("                continue")
    parts.append("            data = json.loads(line)")
    parts.append(f"            examples.append(dspy.Example(**data).with_inputs({with_inputs_arg}))")
    parts.append("    return examples")
    parts.append("")
    parts.append("")
    parts.append("# ---------------------------------------------------------------------------")
    parts.append("# Train")
    parts.append("# ---------------------------------------------------------------------------")
    parts.append("")
    parts.append("def train(data_path=None, save_path=None):")
    parts.append('    """Train the module using BootstrapFewShot."""')
    parts.append("    lm = dspy.LM(MODEL)")
    parts.append("    dspy.configure(lm=lm)")
    parts.append("")
    parts.append("    trainset = load_training_data(data_path)")
    parts.append(f"    module = {mod_cls}()")
    parts.append("")
    parts.append("    optimizer = dspy.BootstrapFewShot(")
    parts.append(f"        metric={config.metric_name},")
    parts.append("        max_bootstrapped_demos=MAX_BOOTSTRAPPED_DEMOS,")
    parts.append("    )")
    parts.append("    compiled = optimizer.compile(module, trainset=trainset)")
    parts.append("")
    parts.append("    if save_path:")
    parts.append("        compiled.save(save_path)")
    parts.append('        print(f"Saved compiled module to {save_path}")')
    parts.append("")
    parts.append("    return compiled")
    parts.append("")
    parts.append("")
    parts.append("# ---------------------------------------------------------------------------")
    parts.append("# Evaluate")
    parts.append("# ---------------------------------------------------------------------------")
    parts.append("")
    parts.append("def evaluate(data_path=None, module_path=None):")
    parts.append('    """Evaluate the module against a dataset."""')
    parts.append("    lm = dspy.LM(MODEL)")
    parts.append("    dspy.configure(lm=lm)")
    parts.append("")
    parts.append("    dataset = load_training_data(data_path)")
    parts.append("")
    parts.append("    if module_path:")
    parts.append(f"        module = {mod_cls}()")
    parts.append("        module.load(module_path)")
    parts.append("    else:")
    parts.append(f"        module = {mod_cls}()")
    parts.append("")
    parts.append("    evaluator = dspy.Evaluate(")
    parts.append("        devset=dataset,")
    parts.append(f"        metric={config.metric_name},")
    parts.append("        display_progress=True,")
    parts.append("    )")
    parts.append("    score = evaluator(module)")
    parts.append('    print(f"Evaluation score: {score}")')
    parts.append("    return score")
    parts.append("")
    parts.append("")
    parts.append("# ---------------------------------------------------------------------------")
    parts.append("# Run (single inference)")
    parts.append("# ---------------------------------------------------------------------------")
    parts.append("")
    parts.append("def run(**kwargs):")
    parts.append('    """Run a single inference."""')
    parts.append("    lm = dspy.LM(MODEL)")
    parts.append("    dspy.configure(lm=lm)")
    parts.append("")
    parts.append(f"    module = {mod_cls}()")
    parts.append("    result = module(**kwargs)")
    parts.append("    return result")
    parts.append("")
    parts.append("")
    parts.append("# ---------------------------------------------------------------------------")
    parts.append("# CLI")
    parts.append("# ---------------------------------------------------------------------------")
    parts.append("")
    parts.append("def main():")
    parts.append("    parser = argparse.ArgumentParser(")
    parts.append("        prog=SLOT_NAME,")
    parts.append("        description=TASK_DESCRIPTION,")
    parts.append("    )")
    parts.append('    subparsers = parser.add_subparsers(dest="command", required=True)')
    parts.append("")
    parts.append("    # train")
    parts.append('    train_parser = subparsers.add_parser("train", help="Train the module")')
    parts.append('    train_parser.add_argument("--data", default=TRAINING_DATA_PATH, help="Path to training JSONL")')
    parts.append('    train_parser.add_argument("--save", default=None, help="Path to save compiled module")')
    parts.append("")
    parts.append("    # evaluate")
    parts.append('    eval_parser = subparsers.add_parser("evaluate", help="Evaluate the module")')
    parts.append('    eval_parser.add_argument("--data", default=TRAINING_DATA_PATH, help="Path to evaluation JSONL")')
    parts.append('    eval_parser.add_argument("--module", default=None, help="Path to saved compiled module")')
    parts.append("")
    parts.append("    # run")
    parts.append('    run_parser = subparsers.add_parser("run", help="Run single inference")')
    parts.append(run_args_block)
    parts.append("")
    parts.append("    args = parser.parse_args()")
    parts.append("")
    parts.append('    if args.command == "train":')
    parts.append("        train(data_path=args.data, save_path=args.save)")
    parts.append('    elif args.command == "evaluate":')
    parts.append("        evaluate(data_path=args.data, module_path=args.module)")
    parts.append('    elif args.command == "run":')
    parts.append(f"        result = run({run_kwargs})")
    parts.append(f"        print(json.dumps({{k: getattr(result, k, None) for k in {output_keys!r}}}, indent=2))")
    parts.append("")
    parts.append("")
    parts.append('if __name__ == "__main__":')
    parts.append("    main()")
    parts.append("")

    script = "\n".join(parts)

    # Validate syntax
    try:
        compile(script, f"<dspy_slot:{config.slot_name}>", "exec")
    except SyntaxError as exc:
        raise ValueError(
            f"Generated script for slot '{config.slot_name}' has a syntax error: {exc}"
        ) from exc

    return script


# ---------------------------------------------------------------------------
# Training data template
# ---------------------------------------------------------------------------

def generate_training_data_template(config: DSpySlotConfig) -> str:
    """Generate a JSONL string with 3 placeholder training examples.

    Each line is valid JSON with keys matching both input and output field names.

    Returns:
        A multi-line JSONL string.
    """
    all_fields = list(config.input_fields.keys()) + list(config.output_fields.keys())
    lines = []
    for i in range(1, 4):
        example: dict[str, str] = {}
        for f in all_fields:
            example[f] = f"example_{i}_{f}"
        lines.append(json.dumps(example, ensure_ascii=False))
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Config serialization
# ---------------------------------------------------------------------------

def generate_slot_config_json(config: DSpySlotConfig) -> str:
    """Serialize a DSpySlotConfig to a JSON string.

    Returns:
        Pretty-printed JSON string.
    """
    return json.dumps(asdict(config), indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Detection
# ---------------------------------------------------------------------------

def detect_dspy_integration(chip_path: Path) -> dict[str, Any]:
    """Check whether a chip directory has DSPy integration.

    Looks for:
      - Files matching dspy_slot*.py
      - A dspy_config.json file
      - 'import dspy' in any src/*.py file

    Args:
        chip_path: Root directory of a domain chip.

    Returns:
        Dict with keys: has_dspy, slots, config_path, scripts.
    """
    chip_path = Path(chip_path)
    result: dict[str, Any] = {
        "has_dspy": False,
        "slots": [],
        "config_path": None,
        "scripts": [],
    }

    # Check for dspy_config.json
    config_path = chip_path / "dspy_config.json"
    if config_path.is_file():
        result["has_dspy"] = True
        result["config_path"] = str(config_path)
        # Try to extract slot names from config
        try:
            config_data = json.loads(config_path.read_text(encoding="utf-8"))
            if isinstance(config_data, dict) and "slot_name" in config_data:
                result["slots"].append(config_data["slot_name"])
            elif isinstance(config_data, list):
                for item in config_data:
                    if isinstance(item, dict) and "slot_name" in item:
                        result["slots"].append(item["slot_name"])
        except (json.JSONDecodeError, OSError):
            pass

    # Look for dspy_slot*.py files anywhere in the tree
    for py_file in chip_path.rglob("dspy_slot*.py"):
        result["has_dspy"] = True
        result["scripts"].append(str(py_file))
        # Derive slot name from filename: dspy_slot_foo.py -> foo
        stem = py_file.stem
        slot_suffix = stem.replace("dspy_slot_", "").replace("dspy_slot", "")
        if slot_suffix and slot_suffix not in result["slots"]:
            result["slots"].append(slot_suffix)

    # Check for 'import dspy' in src/**/*.py
    src_dir = chip_path / "src"
    if src_dir.is_dir():
        for py_file in src_dir.rglob("*.py"):
            try:
                content = py_file.read_text(encoding="utf-8")
            except OSError:
                continue
            if "import dspy" in content:
                result["has_dspy"] = True
                script_str = str(py_file)
                if script_str not in result["scripts"]:
                    result["scripts"].append(script_str)

    return result


# ---------------------------------------------------------------------------
# Scaffold
# ---------------------------------------------------------------------------

def _detect_module_name(chip_path: Path) -> str:
    """Detect the Python module name for a chip from its project structure.

    Tries in order:
      1. pyproject.toml [project] name -> sanitized
      2. First directory under src/ that has __init__.py
      3. Fallback to chip directory name, sanitized
    """
    # 1. Try pyproject.toml
    pyproject = chip_path / "pyproject.toml"
    if pyproject.is_file():
        try:
            text = pyproject.read_text(encoding="utf-8")
            # Simple regex extraction -- no toml dependency
            match = re.search(r'name\s*=\s*["\']([^"\']+)["\']', text)
            if match:
                raw_name = match.group(1)
                # Convert package name to module: domain-chip-foo -> domain_chip_foo
                return re.sub(r"[^a-z0-9_]", "_", raw_name.lower().replace("-", "_"))
        except OSError:
            pass

    # 2. Try src/ directory
    src_dir = chip_path / "src"
    if src_dir.is_dir():
        for child in sorted(src_dir.iterdir()):
            if child.is_dir() and (child / "__init__.py").is_file():
                return child.name

    # 3. Fallback
    return re.sub(r"[^a-z0-9_]", "_", chip_path.name.lower().replace("-", "_"))


def scaffold_dspy_slot(
    chip_path: Path,
    slot_type: str,
    config_overrides: dict[str, Any] | None = None,
) -> dict[str, Path]:
    """Scaffold a DSPy slot into a chip directory.

    Creates (without overwriting existing files):
      - src/{module}/dspy_slot_{type}.py  (the runnable script)
      - data/dspy_training_{type}.jsonl   (placeholder training data)
      - dspy_config.json                  (slot configuration)

    Args:
        chip_path: Root directory of the chip.
        slot_type: One of the pre-built SLOT_TYPES keys, or a custom name.
        config_overrides: Optional dict to override default config values.

    Returns:
        Dict mapping role strings to Paths of created (or existing) files.

    Raises:
        ValueError: If slot_type is not recognized and no overrides provide
                    the required fields.
    """
    chip_path = Path(chip_path)
    module_name = _detect_module_name(chip_path)

    # Build config
    if slot_type in SLOT_TYPES:
        slot_def = SLOT_TYPES[slot_type]
        config = DSpySlotConfig(
            slot_name=slot_type,
            task_description=slot_def["task_description"],
            input_fields=dict(slot_def["input_fields"]),
            output_fields=dict(slot_def["output_fields"]),
            training_data_path=f"data/dspy_training_{slot_type}.jsonl",
        )
    else:
        # Custom slot -- require overrides to supply fields
        config = DSpySlotConfig(
            slot_name=slot_type,
            training_data_path=f"data/dspy_training_{slot_type}.jsonl",
        )

    # Apply overrides
    if config_overrides:
        for key, val in config_overrides.items():
            if hasattr(config, key):
                setattr(config, key, val)

    created: dict[str, Path] = {}

    # 1. Script file
    src_dir = chip_path / "src" / module_name
    src_dir.mkdir(parents=True, exist_ok=True)
    script_path = src_dir / f"dspy_slot_{slot_type}.py"
    if not script_path.exists():
        script_path.write_text(generate_slot_script(config), encoding="utf-8")
    created["script"] = script_path

    # 2. Training data
    data_dir = chip_path / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    training_path = data_dir / f"dspy_training_{slot_type}.jsonl"
    if not training_path.exists():
        training_path.write_text(
            generate_training_data_template(config), encoding="utf-8"
        )
    created["training_data"] = training_path

    # 3. Config JSON
    config_path = chip_path / "dspy_config.json"
    if not config_path.exists():
        config_path.write_text(
            generate_slot_config_json(config), encoding="utf-8"
        )
    created["config"] = config_path

    return created


# ---------------------------------------------------------------------------
# Listing
# ---------------------------------------------------------------------------

def list_available_slot_types() -> list[dict[str, str]]:
    """List all pre-built slot types with their descriptions.

    Returns:
        A list of dicts, each with 'name' and 'description' keys.
    """
    return [
        {"name": name, "description": slot["description"]}
        for name, slot in SLOT_TYPES.items()
    ]
