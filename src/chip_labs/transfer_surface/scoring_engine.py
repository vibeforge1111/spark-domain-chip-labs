"""Shared scoring engine for domain chips.

Extracts the additive mutation scoring pattern that all domain chips
reimplemented independently:

    score = BASE + sum(dimension_deltas) + sum(pair_bonuses) + sum(system_bonuses)

Clamped to a configurable range (default [0, 100]).

Examples from real chips:
    trading-crypto:  BASE + doctrine + strategy + regime + timeframe + venue + pairs + paper_gate
    web-designer:    BASE + 7 axis deltas + pair_bonuses + system_bonuses
    startup-yc:      BASE + factor_catalog + family_priors + quality_signal + transfer_check - contradictions

This module provides a single, tested, configurable engine that any chip
can use instead of rolling its own.

Zero external dependencies.  Uses only stdlib dataclasses + json + pathlib.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class PairBonus:
    """Bonus applied when two dimensions hold specific values simultaneously.

    Example: trading-crypto gives +5 when doctrine=trend_following AND
    regime=trending.
    """

    dim_a: str
    val_a: str
    dim_b: str
    val_b: str
    bonus: float


@dataclass
class SystemBonus:
    """Bonus (or penalty) gated by an arbitrary condition over the full
    mutation dict.

    The *condition* callable receives the mutations dict and returns True
    when the bonus should apply.

    Example: startup-yc applies a -8 contradiction penalty when
    ``business_model == 'marketplace'`` AND ``monetization == 'premium'``.
    """

    label: str
    bonus: float
    condition: Callable[[dict[str, Any]], bool]


@dataclass
class ScoringConfig:
    """Full configuration for one chip's scoring model.

    Attributes:
        base_score:  Starting score before any deltas.
        dimensions:  ``{dim_name: {value: delta, ...}, ...}``.
        pair_bonuses:  List of :class:`PairBonus` instances.
        system_bonuses:  List of :class:`SystemBonus` instances.
        clamp_range:  ``(min, max)`` for the final score.
        approve_threshold:  Score >= this yields verdict "approve".
        defer_threshold:  Score >= this (and < approve) yields "defer".
                          Below this yields "reject".
        evidence_lane_rules:  Optional mapping of mutation patterns to
                              evidence lanes.  Keys are
                              ``"dim_name=value"`` strings; values are
                              lane names.  The *first* matching rule wins.
                              Falls back to ``"exploratory_frontier"``
                              when no rule matches.
        default_evidence_lane:  Lane used when no rule matches and no
                                mutations are supplied.
    """

    base_score: float = 50
    dimensions: dict[str, dict[str, float]] = field(default_factory=dict)
    pair_bonuses: list[PairBonus] = field(default_factory=list)
    system_bonuses: list[SystemBonus] = field(default_factory=list)
    clamp_range: tuple[float, float] = (0.0, 100.0)
    approve_threshold: float = 70.0
    defer_threshold: float = 40.0
    evidence_lane_rules: dict[str, str] = field(default_factory=dict)
    default_evidence_lane: str = "benchmark_grounded"


@dataclass
class ScoringResult:
    """Outcome of scoring a single mutation dict.

    Attributes:
        total:  Final clamped score.
        breakdown:  Per-dimension ``{dim: {"value": v, "delta": d}}``.
        pair_bonus_total:  Sum of all triggered pair bonuses.
        pair_bonus_details:  List of ``{"label": ..., "bonus": ...}``
                             for each triggered pair bonus.
        system_bonus_total:  Sum of all triggered system bonuses.
        system_bonus_details:  List of ``{"label": ..., "bonus": ...}``
                               for each triggered system bonus.
        verdict:  ``"approve"`` | ``"defer"`` | ``"reject"``.
        evidence_lane:  Classified evidence lane string.
        mutations:  The input mutations dict (echo-back for tracing).
    """

    total: float
    breakdown: dict[str, dict[str, Any]]
    pair_bonus_total: float
    pair_bonus_details: list[dict[str, Any]]
    system_bonus_total: float
    system_bonus_details: list[dict[str, Any]]
    verdict: str
    evidence_lane: str
    mutations: dict[str, Any]


# ---------------------------------------------------------------------------
# Core engine
# ---------------------------------------------------------------------------

class MutationScoringEngine:
    """Deterministic additive mutation scoring engine.

    Usage::

        config = (
            ScoringConfigBuilder()
            .set_base_score(50)
            .add_dimension("regime", {"bull": 5, "bear": -3, "crisis": -10})
            .add_pair_bonus("doctrine", "trend", "regime", "bull", 5)
            .add_system_bonus("paper_gate", -20,
                              lambda m: m.get("paper_trade") == "fail")
            .build()
        )
        engine = MutationScoringEngine(config)
        result = engine.score({"regime": "bull", "doctrine": "trend"})
        print(result.total, result.verdict)
    """

    def __init__(self, config: ScoringConfig) -> None:
        self._config = config

    @property
    def config(self) -> ScoringConfig:
        return self._config

    # -- single score -------------------------------------------------------

    def score(self, mutations: dict[str, Any]) -> ScoringResult:
        """Score a single mutations dict and return a full result."""
        cfg = self._config
        running = cfg.base_score
        breakdown: dict[str, dict[str, Any]] = {}

        # 1. Dimension deltas
        for dim_name, dim_values in cfg.dimensions.items():
            val = mutations.get(dim_name)
            if val is not None and val in dim_values:
                delta = dim_values[val]
                running += delta
                breakdown[dim_name] = {"value": val, "delta": delta}

        # 2. Pair bonuses
        pair_total = 0.0
        pair_details: list[dict[str, Any]] = []
        for pb in cfg.pair_bonuses:
            if (mutations.get(pb.dim_a) == pb.val_a
                    and mutations.get(pb.dim_b) == pb.val_b):
                pair_total += pb.bonus
                pair_details.append({
                    "label": f"{pb.dim_a}={pb.val_a}+{pb.dim_b}={pb.val_b}",
                    "bonus": pb.bonus,
                })
        running += pair_total

        # 3. System bonuses
        sys_total = 0.0
        sys_details: list[dict[str, Any]] = []
        for sb in cfg.system_bonuses:
            try:
                if sb.condition(mutations):
                    sys_total += sb.bonus
                    sys_details.append({
                        "label": sb.label,
                        "bonus": sb.bonus,
                    })
            except Exception:
                # Defensive: a broken condition must never crash scoring.
                pass
        running += sys_total

        # 4. Clamp
        lo, hi = cfg.clamp_range
        total = max(lo, min(hi, running))

        # 5. Verdict
        if total >= cfg.approve_threshold:
            verdict = "approve"
        elif total >= cfg.defer_threshold:
            verdict = "defer"
        else:
            verdict = "reject"

        # 6. Evidence lane
        evidence_lane = self._classify_evidence_lane(mutations)

        return ScoringResult(
            total=total,
            breakdown=breakdown,
            pair_bonus_total=pair_total,
            pair_bonus_details=pair_details,
            system_bonus_total=sys_total,
            system_bonus_details=sys_details,
            verdict=verdict,
            evidence_lane=evidence_lane,
            mutations=dict(mutations),
        )

    # -- bulk operations ----------------------------------------------------

    def bulk_score(self, mutation_list: list[dict[str, Any]]) -> list[ScoringResult]:
        """Score a list of mutation dicts.  Order is preserved."""
        return [self.score(m) for m in mutation_list]

    def leaderboard(
        self,
        mutation_list: list[dict[str, Any]],
        top_n: int = 10,
    ) -> list[ScoringResult]:
        """Score all mutations and return the top *top_n* by total (desc)."""
        scored = self.bulk_score(mutation_list)
        scored.sort(key=lambda r: r.total, reverse=True)
        return scored[:top_n]

    # -- internal -----------------------------------------------------------

    def _classify_evidence_lane(self, mutations: dict[str, Any]) -> str:
        """Classify the evidence lane using config rules, with fallbacks."""
        if not mutations:
            return self._config.default_evidence_lane

        for pattern, lane in self._config.evidence_lane_rules.items():
            # Pattern format: "dim_name=value"
            if "=" in pattern:
                dim, val = pattern.split("=", 1)
                if mutations.get(dim) == val:
                    return lane

        return "exploratory_frontier"


# ---------------------------------------------------------------------------
# Fluent builder
# ---------------------------------------------------------------------------

class ScoringConfigBuilder:
    """Fluent builder for constructing :class:`ScoringConfig` objects.

    Usage::

        config = (
            ScoringConfigBuilder()
            .set_base_score(50)
            .add_dimension("regime", {"bull": 5, "bear": -3})
            .add_pair_bonus("a", "x", "b", "y", 4)
            .add_system_bonus("penalty", -10, lambda m: m.get("bad"))
            .set_thresholds(approve=75, defer=45)
            .build()
        )
    """

    def __init__(self) -> None:
        self._base_score: float = 50
        self._dimensions: dict[str, dict[str, float]] = {}
        self._pair_bonuses: list[PairBonus] = []
        self._system_bonuses: list[SystemBonus] = []
        self._clamp_range: tuple[float, float] = (0.0, 100.0)
        self._approve: float = 70.0
        self._defer: float = 40.0
        self._evidence_lane_rules: dict[str, str] = {}
        self._default_evidence_lane: str = "benchmark_grounded"

    # -- setters (return self for chaining) ---------------------------------

    def set_base_score(self, score: float) -> ScoringConfigBuilder:
        self._base_score = score
        return self

    def add_dimension(
        self,
        name: str,
        values: dict[str, float],
    ) -> ScoringConfigBuilder:
        """Add (or replace) a scoring dimension."""
        self._dimensions[name] = dict(values)
        return self

    def add_pair_bonus(
        self,
        dim_a: str,
        val_a: str,
        dim_b: str,
        val_b: str,
        bonus: float,
    ) -> ScoringConfigBuilder:
        self._pair_bonuses.append(PairBonus(dim_a, val_a, dim_b, val_b, bonus))
        return self

    def add_system_bonus(
        self,
        label: str,
        bonus: float,
        condition: Callable[[dict[str, Any]], bool],
    ) -> ScoringConfigBuilder:
        self._system_bonuses.append(SystemBonus(label, bonus, condition))
        return self

    def set_thresholds(
        self,
        approve: float = 70.0,
        defer: float = 40.0,
    ) -> ScoringConfigBuilder:
        self._approve = approve
        self._defer = defer
        return self

    def set_clamp_range(
        self,
        lo: float = 0.0,
        hi: float = 100.0,
    ) -> ScoringConfigBuilder:
        self._clamp_range = (lo, hi)
        return self

    def add_evidence_lane_rule(
        self,
        pattern: str,
        lane: str,
    ) -> ScoringConfigBuilder:
        """Add a ``"dim=value"`` -> lane mapping."""
        self._evidence_lane_rules[pattern] = lane
        return self

    def set_default_evidence_lane(self, lane: str) -> ScoringConfigBuilder:
        self._default_evidence_lane = lane
        return self

    # -- build --------------------------------------------------------------

    def build(self) -> ScoringConfig:
        return ScoringConfig(
            base_score=self._base_score,
            dimensions=dict(self._dimensions),
            pair_bonuses=list(self._pair_bonuses),
            system_bonuses=list(self._system_bonuses),
            clamp_range=self._clamp_range,
            approve_threshold=self._approve,
            defer_threshold=self._defer,
            evidence_lane_rules=dict(self._evidence_lane_rules),
            default_evidence_lane=self._default_evidence_lane,
        )


# ---------------------------------------------------------------------------
# Factory: from_brief
# ---------------------------------------------------------------------------

def from_brief(brief: dict[str, Any]) -> ScoringConfig:
    """Create a :class:`ScoringConfig` from a domain brief dict.

    The brief format matches what ``scaffold.py`` uses::

        {
            "domain_id": "trading-crypto",
            "domain_name": "Crypto Trading",
            "primary_metric": "risk_adjusted_return",
            "mutation_axes": [
                {"name": "regime", "values": ["bull", "bear", "crisis"]},
                ...
            ],
            "pair_bonuses": [  # optional
                {"dim_a": "doctrine", "val_a": "trend", "dim_b": "regime",
                 "val_b": "bull", "bonus": 5},
            ],
            "base_score": 50,         # optional, default 50
            "approve_threshold": 70,  # optional
            "defer_threshold": 40,    # optional
        }

    Dimension deltas are auto-generated from mutation axes when not
    explicitly supplied: each value gets an incremental delta of
    ``(index + 1) * 2`` (matching scaffold.py's ``_gen_evaluate``).
    """
    builder = ScoringConfigBuilder()

    builder.set_base_score(brief.get("base_score", 50))

    # Thresholds
    builder.set_thresholds(
        approve=brief.get("approve_threshold", 70),
        defer=brief.get("defer_threshold", 40),
    )

    # Dimensions from mutation_axes
    explicit_dims = brief.get("dimensions")
    if explicit_dims and isinstance(explicit_dims, dict):
        # Caller provided pre-built dimensions — use as-is
        for dim_name, dim_values in explicit_dims.items():
            builder.add_dimension(dim_name, dim_values)
    else:
        # Auto-generate from mutation_axes (same formula as scaffold.py)
        for axis in brief.get("mutation_axes", []):
            if isinstance(axis, dict):
                name = axis["name"]
                values = axis.get("values", [])
            else:
                name = str(axis)
                values = []
            dim_values = {v: (i + 1) * 2 for i, v in enumerate(values)}
            if dim_values:
                builder.add_dimension(name, dim_values)

    # Pair bonuses
    for pb in brief.get("pair_bonuses", []):
        if isinstance(pb, dict):
            builder.add_pair_bonus(
                pb["dim_a"], pb["val_a"],
                pb["dim_b"], pb["val_b"],
                pb.get("bonus", 0),
            )

    # Evidence lane rules
    for rule_key, lane in brief.get("evidence_lane_rules", {}).items():
        builder.add_evidence_lane_rule(rule_key, lane)

    # Default evidence lane
    if brief.get("default_evidence_lane"):
        builder.set_default_evidence_lane(brief["default_evidence_lane"])

    return builder.build()


# ---------------------------------------------------------------------------
# Factory: from_manifest
# ---------------------------------------------------------------------------

def from_manifest(manifest_path: str | Path) -> ScoringConfig:
    """Create a :class:`ScoringConfig` by reading a chip's ``spark-chip.json``.

    This extracts ``allowed_mutations`` from the manifest's ``frontier``
    section and converts them into dimensions with auto-generated deltas.

    It is intentionally a *starting point* -- chips will typically override
    pair bonuses and system bonuses after loading.
    """
    manifest_path = Path(manifest_path)
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    frontier = manifest.get("frontier", {})
    allowed_mutations = frontier.get("allowed_mutations", {})

    builder = ScoringConfigBuilder()

    for dim_name, values in allowed_mutations.items():
        if isinstance(values, list) and values:
            dim_values = {v: (i + 1) * 2 for i, v in enumerate(values)}
            builder.add_dimension(dim_name, dim_values)

    return builder.build()
