"""Graduation criteria and workflow for lab prototypes becoming real chips."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .quality_rubric import score_chip


# ---------------------------------------------------------------------------
# Graduation criteria
# ---------------------------------------------------------------------------

GRADUATION_CRITERIA: list[dict[str, Any]] = [
    {
        "id": "working_cli",
        "label": "Working CLI with all 4 hooks",
        "description": "The chip must have evaluate, suggest, packets, and watchtower commands that execute without errors.",
        "weight": 0.20,
        "required": True,
    },
    {
        "id": "benchmark_pack",
        "label": "One successful benchmark pack",
        "description": "At least one benchmark evaluation has been run and produced valid results.",
        "weight": 0.15,
        "required": True,
    },
    {
        "id": "output_contract",
        "label": "Output contract defined",
        "description": "Schema and templates for chip output are documented.",
        "weight": 0.10,
        "required": False,
    },
    {
        "id": "quality_score",
        "label": "Quality rubric score >= 60/100",
        "description": "The chip must score at least 60 on the lab's quality rubric.",
        "weight": 0.20,
        "required": True,
    },
    {
        "id": "evidence_separation",
        "label": "Evidence lane separation",
        "description": "At least 3 of the 4 evidence lanes are structurally distinct in the chip's architecture.",
        "weight": 0.10,
        "required": True,
    },
    {
        "id": "candidate_trials",
        "label": "At least 3 candidate trials",
        "description": "The chip's project config includes a baseline and at least 2 variant trials.",
        "weight": 0.10,
        "required": True,
    },
    {
        "id": "human_approval",
        "label": "Human approval obtained",
        "description": "A human operator has reviewed and approved the chip for graduation.",
        "weight": 0.15,
        "required": True,
    },
]


def assess_graduation(chip_path: str | Path) -> dict[str, Any]:
    """Assess whether a chip is ready for graduation.

    Returns a graduation assessment with criteria results and overall readiness.
    """
    chip_path = Path(chip_path)
    results: list[dict[str, Any]] = []
    total_weight = 0.0
    weighted_score = 0.0

    # Run quality rubric
    quality_result = score_chip(chip_path)
    quality_score = quality_result["total_score"]

    for criterion in GRADUATION_CRITERIA:
        passed = _check_criterion(criterion["id"], chip_path, quality_score)
        score = 1.0 if passed else 0.0
        weighted_score += score * criterion["weight"]
        total_weight += criterion["weight"]

        results.append({
            "id": criterion["id"],
            "label": criterion["label"],
            "passed": passed,
            "required": criterion["required"],
            "weight": criterion["weight"],
        })

    readiness = round(weighted_score / total_weight, 4) if total_weight > 0 else 0.0
    all_required_passed = all(r["passed"] for r in results if r["required"])

    if all_required_passed and readiness >= 0.80:
        verdict = "ready_for_graduation"
    elif readiness >= 0.60:
        verdict = "needs_improvement"
    else:
        verdict = "not_ready"

    return {
        "chip_path": str(chip_path),
        "chip_name": chip_path.name,
        "quality_score": quality_score,
        "readiness_score": readiness,
        "verdict": verdict,
        "all_required_passed": all_required_passed,
        "criteria": results,
    }


def _check_criterion(criterion_id: str, chip_path: Path, quality_score: int) -> bool:
    """Check a single graduation criterion."""
    if criterion_id == "working_cli":
        manifest_path = chip_path / "spark-chip.json"
        if not manifest_path.exists():
            return False
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            caps = set(manifest.get("capabilities", []))
            return {"evaluate", "suggest", "packets", "watchtower"}.issubset(caps)
        except (json.JSONDecodeError, OSError):
            return False

    elif criterion_id == "benchmark_pack":
        artifacts = chip_path / "artifacts"
        return artifacts.exists() and any(artifacts.rglob("*"))

    elif criterion_id == "output_contract":
        # Check for schema docs or templates
        docs = chip_path / "docs"
        if not docs.exists():
            return False
        for md in docs.rglob("*.md"):
            try:
                content = md.read_text(encoding="utf-8", errors="ignore").lower()
                if "schema" in content or "contract" in content or "template" in content:
                    return True
            except OSError:
                pass
        return False

    elif criterion_id == "quality_score":
        return quality_score >= 60

    elif criterion_id == "evidence_separation":
        # Check quality rubric evidence dimension
        result = score_chip(chip_path)
        for dim in result.get("dimensions", []):
            if dim["name"] == "evidence_separation":
                passed_count = sum(1 for c in dim["checks"] if c["passed"])
                return passed_count >= 3
        return False

    elif criterion_id == "candidate_trials":
        project_path = chip_path / "spark-researcher.project.json"
        if not project_path.exists():
            return False
        try:
            project = json.loads(project_path.read_text(encoding="utf-8"))
            trials = project.get("candidate_trials", [])
            return len(trials) >= 3
        except (json.JSONDecodeError, OSError):
            return False

    elif criterion_id == "human_approval":
        # This can only be set manually -- always False for automated assessment
        return False

    return False
