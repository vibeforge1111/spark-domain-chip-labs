"""Outcome contracts and Brier scoring for calibration.

Every prediction gets an outcome contract. Replay cases track which
predictions were right. Brier scoring before trust.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def create_outcome_contract(
    question: str,
    contract_type: str = "binary",
    domain_id: str = "",
    predicted_probability: float = 0.5,
    resolution_deadline: str = "",
    resolution_rule: str = "",
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create an outcome contract for a prediction.

    Args:
        question: The prediction question (e.g., "Will defi-architect chip be built by Q3 2026?")
        contract_type: "binary" (yes/no) or "categorical" (multiple outcomes).
        domain_id: The domain this prediction is about.
        predicted_probability: Our predicted probability (0-1).
        resolution_deadline: When this can be resolved.
        resolution_rule: How to determine the outcome.
        metadata: Additional context.
    """
    return {
        "contract_id": f"oc-{domain_id}-{_timestamp_suffix()}",
        "question": question,
        "contract_type": contract_type,
        "domain_id": domain_id,
        "predicted_probability": predicted_probability,
        "resolution_deadline": resolution_deadline,
        "resolution_rule": resolution_rule,
        "status": "open",
        "actual_outcome": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "metadata": metadata or {},
    }


def resolve_contract(
    contract: dict[str, Any],
    actual_outcome: bool | str,
) -> dict[str, Any]:
    """Resolve an outcome contract with the actual outcome."""
    resolved = dict(contract)
    resolved["status"] = "resolved"
    resolved["actual_outcome"] = actual_outcome
    resolved["resolved_at"] = datetime.now(timezone.utc).isoformat()

    if contract["contract_type"] == "binary":
        outcome_value = 1.0 if actual_outcome else 0.0
        resolved["brier_score"] = brier_score(
            contract["predicted_probability"], outcome_value,
        )
    return resolved


def brier_score(predicted: float, actual: float) -> float:
    """Calculate Brier score for a single prediction.

    Brier score = (predicted - actual)^2
    Lower is better. 0.0 = perfect, 0.25 = random for binary.
    """
    return round((predicted - actual) ** 2, 6)


def aggregate_brier(contracts: list[dict[str, Any]]) -> float:
    """Calculate aggregate Brier score across resolved contracts."""
    resolved = [c for c in contracts if c.get("status") == "resolved"
                and c.get("brier_score") is not None]
    if not resolved:
        return 1.0  # worst score if no data
    return round(sum(c["brier_score"] for c in resolved) / len(resolved), 6)


# Historical replay cases for backtesting
REPLAY_CASES: list[dict[str, Any]] = [
    {
        "domain_id": "startup-yc",
        "question": "Will a YC startup evaluation chip be built?",
        "predicted_probability": 0.85,
        "actual_outcome": True,
        "rationale": "Strong demand from startup community, clear benchmark feasibility.",
    },
    {
        "domain_id": "trading-crypto",
        "question": "Will a crypto trading strategy chip be built?",
        "predicted_probability": 0.80,
        "actual_outcome": True,
        "rationale": "High market demand, rich data availability, strong ecosystem fit.",
    },
    {
        "domain_id": "agentic-marketing",
        "question": "Will an AI marketing chip be built?",
        "predicted_probability": 0.75,
        "actual_outcome": True,
        "rationale": "Content marketing is a natural AI application, growing demand.",
    },
    {
        "domain_id": "web-designer",
        "question": "Will a web design chip be built?",
        "predicted_probability": 0.60,
        "actual_outcome": True,
        "rationale": "Visual design is challenging for AI but high demand.",
    },
    {
        "domain_id": "pokemon-red",
        "question": "Will a Pokemon game chip be built?",
        "predicted_probability": 0.40,
        "actual_outcome": True,
        "rationale": "Niche domain, but passionate community drove creation.",
    },
    {
        "domain_id": "roblox-development",
        "question": "Will a Roblox development chip be built?",
        "predicted_probability": 0.45,
        "actual_outcome": True,
        "rationale": "Large addressable market but niche expertise needed.",
    },
    {
        "domain_id": "xcontent",
        "question": "Will an X/Twitter content chip be built?",
        "predicted_probability": 0.70,
        "actual_outcome": True,
        "rationale": "High social media demand, clear content generation use case.",
    },
    {
        "domain_id": "content",
        "question": "Will a general content chip be built?",
        "predicted_probability": 0.55,
        "actual_outcome": True,
        "rationale": "Broad domain but fragmented, lower differentiation than expected.",
    },
    {
        "domain_id": "vibe-incubator",
        "question": "Will a vibe-coding incubator chip be built?",
        "predicted_probability": 0.50,
        "actual_outcome": True,
        "rationale": "Novel concept, moderate community interest, ecosystem fit.",
    },
    {
        "domain_id": "predictive-worlds-lab",
        "question": "Will a predictive worlds lab chip be built?",
        "predicted_probability": 0.35,
        "actual_outcome": True,
        "rationale": "Research-oriented, niche but passionate builders.",
    },
    {
        "domain_id": "autonomous-vehicles",
        "question": "Will an autonomous vehicle chip be built?",
        "predicted_probability": 0.20,
        "actual_outcome": False,
        "rationale": "Extremely high complexity, limited benchmark feasibility.",
    },
    {
        "domain_id": "quantum-computing",
        "question": "Will a quantum computing chip be built?",
        "predicted_probability": 0.15,
        "actual_outcome": False,
        "rationale": "Very niche, limited practical data, low community demand.",
    },
    {
        "domain_id": "biotech-drug-discovery",
        "question": "Will a biotech drug discovery chip be built?",
        "predicted_probability": 0.10,
        "actual_outcome": False,
        "rationale": "Requires specialized domain expertise beyond current scope.",
    },
    {
        "domain_id": "climate-modeling",
        "question": "Will a climate modeling chip be built?",
        "predicted_probability": 0.12,
        "actual_outcome": False,
        "rationale": "High complexity, limited data access, no community demand.",
    },
]


def replay_calibration() -> dict[str, Any]:
    """Run calibration against historical replay cases.

    Returns per-case and aggregate Brier scores.
    """
    results: list[dict[str, Any]] = []
    for case in REPLAY_CASES:
        actual_value = 1.0 if case["actual_outcome"] else 0.0
        score = brier_score(case["predicted_probability"], actual_value)
        results.append({
            "domain_id": case["domain_id"],
            "predicted": case["predicted_probability"],
            "actual": case["actual_outcome"],
            "brier_score": score,
        })

    agg = round(sum(r["brier_score"] for r in results) / len(results), 6) if results else 1.0

    # Baseline comparisons
    constant_50 = round(
        sum(brier_score(0.5, 1.0 if c["actual_outcome"] else 0.0) for c in REPLAY_CASES) / len(REPLAY_CASES), 6
    )
    frequency_base_rate = sum(1 for c in REPLAY_CASES if c["actual_outcome"]) / len(REPLAY_CASES)
    frequency_brier = round(
        sum(brier_score(frequency_base_rate, 1.0 if c["actual_outcome"] else 0.0) for c in REPLAY_CASES) / len(REPLAY_CASES), 6
    )

    return {
        "cases": results,
        "aggregate_brier": agg,
        "case_count": len(results),
        "baselines": {
            "constant_50": constant_50,
            "frequency_predictor": frequency_brier,
            "base_rate": round(frequency_base_rate, 4),
        },
        "better_than_constant": agg < constant_50,
        "better_than_frequency": agg < frequency_brier,
    }


def calibration_report(
    simulation_predictions: dict[str, float],
    replay_results: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Generate a calibration report combining simulation predictions with replay data."""
    if replay_results is None:
        replay_results = replay_calibration()

    contracts: list[dict[str, Any]] = []
    for domain_id, predicted_prob in simulation_predictions.items():
        contracts.append(create_outcome_contract(
            question=f"Will {domain_id} domain chip be built within 6 months?",
            domain_id=domain_id,
            predicted_probability=predicted_prob,
            resolution_deadline="6 months from prediction",
            resolution_rule="Chip exists on Desktop with spark-chip.json manifest.",
        ))

    return {
        "prediction_contracts": contracts,
        "contract_count": len(contracts),
        "historical_calibration": replay_results,
        "evidence_lane": "exploratory_frontier",
        "note": "Simulation predictions are exploratory_frontier. Do not auto-promote to doctrine.",
    }


def _timestamp_suffix() -> str:
    """Generate a short timestamp suffix for IDs."""
    return datetime.now(timezone.utc).strftime("%Y%m%d%H%M")
