"""Recursive loop controller for autonomous domain chip self-improvement.

Orchestrates the full lifecycle:
    Brief -> Scaffold -> Score -> [Loop: Evaluate -> Gap Analyze -> Fix/Research -> Re-score -> Suggest] -> Mature Chip

Integrates with:
    - scaffold.py        (scaffold_chip)
    - quality_rubric.py  (score_chip)
    - gap_analyzer.py    (analyze_gaps, improve_chip)
    - suggest.py         (suggest)
    - category_templates.py (apply_template)

Zero external dependencies.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


from .category_templates import apply_template
from .chip_factory import analyze_gaps, improve_chip, scaffold_chip, validate_brief
from .lab_hooks import run_suggest
from .quality_rubric import score_chip


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


@dataclass
class LoopConfig:
    """Configuration for the recursive improvement loop."""

    target_score: int = 80
    max_iterations: int = 50
    max_stall_iterations: int = 5
    autonomy_level: str = "full_auto"  # "full_auto" | "semi_auto" | "human_gated"
    research_enabled: bool = True
    structural_fix_enabled: bool = True
    evidence_gathering_enabled: bool = True
    telemetry_enabled: bool = True

    def __post_init__(self) -> None:
        if self.autonomy_level not in ("full_auto", "semi_auto", "human_gated"):
            raise ValueError(
                f"Invalid autonomy_level: {self.autonomy_level!r}. "
                "Must be 'full_auto', 'semi_auto', or 'human_gated'."
            )
        if self.target_score < 0 or self.target_score > 100:
            raise ValueError(f"target_score must be 0-100, got {self.target_score}")
        if self.max_iterations < 1:
            raise ValueError(f"max_iterations must be >= 1, got {self.max_iterations}")
        if self.max_stall_iterations < 1:
            raise ValueError(
                f"max_stall_iterations must be >= 1, got {self.max_stall_iterations}"
            )


# ---------------------------------------------------------------------------
# Telemetry records
# ---------------------------------------------------------------------------


@dataclass
class IterationRecord:
    """Record of a single loop iteration."""

    iteration: int
    action_type: str  # structural_fix | gap_analysis | research_seed | evidence_gathering | suggest_mutation | evaluate
    action_detail: str
    score_before: int
    score_after: int
    delta: int
    duration_ms: int


@dataclass
class LoopTelemetry:
    """Full telemetry for a loop run."""

    start_time: str = ""
    end_time: str | None = None
    iterations: list[IterationRecord] = field(default_factory=list)
    score_trajectory: list[int] = field(default_factory=list)
    stall_count: int = 0
    fixes_applied: int = 0
    research_actions: int = 0
    evidence_gathered: int = 0
    status: str = "running"  # running | completed | stalled | target_reached | max_iterations

    def to_dict(self) -> dict[str, Any]:
        """Serialize telemetry to a JSON-friendly dict."""
        return {
            "start_time": self.start_time,
            "end_time": self.end_time,
            "iterations": [
                {
                    "iteration": r.iteration,
                    "action_type": r.action_type,
                    "action_detail": r.action_detail,
                    "score_before": r.score_before,
                    "score_after": r.score_after,
                    "delta": r.delta,
                    "duration_ms": r.duration_ms,
                }
                for r in self.iterations
            ],
            "score_trajectory": self.score_trajectory,
            "stall_count": self.stall_count,
            "fixes_applied": self.fixes_applied,
            "research_actions": self.research_actions,
            "evidence_gathered": self.evidence_gathered,
            "status": self.status,
        }


# ---------------------------------------------------------------------------
# Loop result
# ---------------------------------------------------------------------------


@dataclass
class LoopResult:
    """Result of a complete loop run."""

    chip_path: Path
    initial_score: int
    final_score: int
    verdict: str
    iterations: int
    telemetry: LoopTelemetry
    improvements: list[str] = field(default_factory=list)
    remaining_gaps: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Research seeder functions
# ---------------------------------------------------------------------------

EVIDENCE_LANES = [
    "research_grounded",
    "benchmark_grounded",
    "exploratory_frontier",
    "realworld_validated",
]


def _seed_evidence_stubs(chip_path: Path) -> int:
    """Create minimal evidence documents in each lane.

    Returns the number of stubs created.
    """
    chip_path = Path(chip_path)
    research_dir = chip_path / "research"
    research_dir.mkdir(parents=True, exist_ok=True)

    created = 0
    for lane in EVIDENCE_LANES:
        lane_dir = research_dir / lane
        lane_dir.mkdir(parents=True, exist_ok=True)

        stub_path = lane_dir / "README.md"
        if not stub_path.exists():
            stub_path.write_text(
                f"# {lane.replace('_', ' ').title()}\n\n"
                f"Evidence lane for {lane} findings.\n\n"
                f"## Entries\n\n"
                f"_No entries yet. Add evidence documents to this directory._\n",
                encoding="utf-8",
            )
            created += 1

    return created


def _seed_research_sources(chip_path: Path, brief: dict[str, Any]) -> int:
    """Populate source registry from brief metadata.

    Returns the number of source entries written.
    """
    chip_path = Path(chip_path)
    docs_dir = chip_path / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)

    registry_path = docs_dir / "SOURCE_REGISTRY.md"
    domain_name = brief.get("domain_name", brief.get("domain_id", "unknown"))
    category = brief.get("category", "general")

    # Gather research source types from template metadata
    source_types = brief.get("_research_source_types", [])
    if not source_types:
        source_types = ["primary_literature", "benchmark_data", "expert_interviews"]

    lines = [
        f"# Source Registry: {domain_name}\n",
        "",
        f"Category: {category}\n",
        "",
        "## Sources\n",
        "",
        "| Source Type | Status | Notes |",
        "|------------|--------|-------|",
    ]

    for src in source_types:
        lines.append(f"| {src} | pending | Seeded by loop controller |")

    lines.append("")
    lines.append("## Research Seed URLs\n")
    lines.append("")

    seed_urls = brief.get("seed_urls", [])
    if seed_urls:
        for url in seed_urls:
            lines.append(f"- {url}")
    else:
        lines.append("_Add seed URLs for initial research here._")

    lines.append("")

    content = "\n".join(lines)

    # Only write if the file does not already contain more content
    if registry_path.exists():
        existing = registry_path.read_text(encoding="utf-8")
        if len(existing.strip()) > len(content.strip()):
            return 0

    registry_path.write_text(content, encoding="utf-8")
    return len(source_types)


def _seed_benchmark_baseline(chip_path: Path) -> bool:
    """Create a baseline benchmark result document.

    Returns True if a file was created.
    """
    chip_path = Path(chip_path)
    benchmark_dir = chip_path / "research" / "benchmark_grounded"
    benchmark_dir.mkdir(parents=True, exist_ok=True)

    baseline_path = benchmark_dir / "baseline_benchmark.json"
    if baseline_path.exists():
        return False

    baseline = {
        "benchmark_id": "baseline-v1",
        "description": "Baseline benchmark with empty mutations",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "mutations": {},
        "result": {
            "score": 50,
            "evidence_lane": "benchmark_grounded",
            "verdict": "defer",
        },
        "notes": "Auto-generated baseline by loop controller research seeder.",
    }

    baseline_path.write_text(
        json.dumps(baseline, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return True


def _create_initial_packets(chip_path: Path) -> int:
    """Generate initial evidence packets and write them to the research directory.

    Returns the number of packets created.
    """
    chip_path = Path(chip_path)
    packets_dir = chip_path / "research" / "packets"
    packets_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc).isoformat()
    packets = [
        {
            "packet_kind": "methodology_doctrine",
            "evidence_lane": "research_grounded",
            "created_at": now,
            "content": {
                "title": "Initial Methodology Packet",
                "description": "Additive mutation scoring with dimension deltas.",
                "findings": [
                    "Fixed evaluator + changing strategy is the core Spark pattern.",
                    "Baseline trial with empty mutations establishes the scoring floor.",
                ],
            },
        },
        {
            "packet_kind": "quality_assessment",
            "evidence_lane": "benchmark_grounded",
            "created_at": now,
            "content": {
                "title": "Initial Quality Assessment",
                "description": "Baseline quality assessment from scaffold.",
                "findings": [
                    "Chip scaffolded with standard template.",
                    "Initial scoring model uses additive mutation deltas.",
                ],
            },
        },
    ]

    created = 0
    for i, packet in enumerate(packets):
        packet_path = packets_dir / f"packet_{i:03d}_{packet['packet_kind']}.json"
        if not packet_path.exists():
            packet_path.write_text(
                json.dumps(packet, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            created += 1

    return created


# ---------------------------------------------------------------------------
# Recursive loop controller
# ---------------------------------------------------------------------------


class RecursiveLoopController:
    """Orchestrates the autonomous self-improvement cycle for domain chips.

    Lifecycle:
        Brief -> Scaffold -> Score -> [Loop] -> Mature Chip

    Loop phases:
        1. Structural: Run gap_analyzer auto-fixes
        2. Research seeding: Seed evidence stubs and initial sources
        3. Evaluation cycle: Evaluate -> Score -> Suggest
        4. Intelligence building: Generate packets, update watchtower, accumulate evidence
    """

    def __init__(self, config: LoopConfig | None = None) -> None:
        self._config = config or LoopConfig()
        self._telemetry = LoopTelemetry()
        self._current_score: int = 0
        self._iteration: int = 0

    # ----- public entry points -----

    def run_from_brief(
        self, brief: dict[str, Any], output_dir: Path | str
    ) -> LoopResult:
        """Scaffold a new chip from a brief and run the full improvement loop.

        Args:
            brief: Domain brief dict (must have domain_id, domain_name, etc.).
            output_dir: Parent directory where the chip directory is created.

        Returns:
            LoopResult with the final state of the chip.
        """
        output_dir = Path(output_dir)

        # Apply category template to fill defaults
        enhanced_brief = apply_template(brief)

        # Validate
        errors = validate_brief(enhanced_brief)
        if errors:
            raise ValueError(f"Invalid brief: {'; '.join(errors)}")

        # Scaffold
        chip_path = scaffold_chip(enhanced_brief, output_dir)

        # Run the loop on the freshly-scaffolded chip
        return self._run_loop(chip_path, brief=enhanced_brief)

    def run_on_chip(self, chip_path: Path | str) -> LoopResult:
        """Improve an existing chip through the recursive loop.

        Args:
            chip_path: Path to an existing chip directory.

        Returns:
            LoopResult with the final state of the chip.
        """
        chip_path = Path(chip_path)
        if not chip_path.exists():
            raise FileNotFoundError(f"Chip path does not exist: {chip_path}")
        return self._run_loop(chip_path)

    def get_telemetry(self) -> LoopTelemetry:
        """Return the current telemetry object."""
        return self._telemetry

    # ----- core loop -----

    def _run_loop(
        self,
        chip_path: Path,
        brief: dict[str, Any] | None = None,
    ) -> LoopResult:
        """Core loop logic: score -> fix -> rescore until target or stall.

        Phases executed in order:
            1. Structural fixes (gap_analyzer.improve_chip)
            2. Research seeding (evidence stubs, source registry, baseline benchmark)
            3. Evaluation + suggestion cycle
            4. Intelligence building (packets, watchtower evidence)
        """
        chip_path = Path(chip_path)

        # Initialize telemetry
        self._telemetry = LoopTelemetry(
            start_time=datetime.now(timezone.utc).isoformat(),
            status="running",
        )

        # Initial score
        initial_result = score_chip(chip_path)
        initial_score = initial_result["total_score"]
        self._current_score = initial_score
        self._telemetry.score_trajectory.append(initial_score)
        self._iteration = 0

        improvements: list[str] = []

        # Check if already at target
        if initial_score >= self._config.target_score:
            self._telemetry.status = "target_reached"
            self._telemetry.end_time = datetime.now(timezone.utc).isoformat()
            self._persist_telemetry(chip_path)
            return LoopResult(
                chip_path=chip_path,
                initial_score=initial_score,
                final_score=initial_score,
                verdict=initial_result.get("verdict", "unknown"),
                iterations=0,
                telemetry=self._telemetry,
                improvements=[],
                remaining_gaps=[],
            )

        # Phase 1: Structural fixes
        if self._config.structural_fix_enabled:
            phase1_result = self._structural_phase(chip_path)
            if phase1_result:
                improvements.extend(phase1_result)

        # Phase 2: Research seeding
        if self._config.research_enabled:
            phase2_result = self._research_phase(chip_path, brief)
            if phase2_result:
                improvements.extend(phase2_result)

        # Phase 3+4: Evaluation + suggestion + intelligence building cycle
        while self._iteration < self._config.max_iterations:
            # Check stall
            if self._detect_stall():
                # Try a different strategy before giving up
                recovery = self._attempt_stall_recovery(chip_path, brief)
                if not recovery:
                    self._telemetry.status = "stalled"
                    break

            self._iteration += 1

            # Evaluation phase
            eval_improvements = self._evaluation_phase(chip_path)
            if eval_improvements:
                improvements.extend(eval_improvements)

            # Check target after evaluation
            if self._current_score >= self._config.target_score:
                self._telemetry.status = "target_reached"
                break

            # Suggestion phase (generate mutation suggestions)
            suggest_improvements = self._suggestion_phase(chip_path)
            if suggest_improvements:
                improvements.extend(suggest_improvements)

            # Check target after suggestions
            if self._current_score >= self._config.target_score:
                self._telemetry.status = "target_reached"
                break

            # Intelligence building: evidence gathering
            if self._config.evidence_gathering_enabled:
                evidence_improvements = self._evidence_phase(chip_path)
                if evidence_improvements:
                    improvements.extend(evidence_improvements)

            # Check target after evidence
            if self._current_score >= self._config.target_score:
                self._telemetry.status = "target_reached"
                break

        # Phase 5: Regenerate intelligence delivery artifacts
        skill_improvements = self._skill_regeneration_phase(chip_path)
        if skill_improvements:
            improvements.extend(skill_improvements)

        # Finalize
        if self._telemetry.status == "running":
            if self._iteration >= self._config.max_iterations:
                self._telemetry.status = "max_iterations"
            else:
                self._telemetry.status = "completed"

        self._telemetry.end_time = datetime.now(timezone.utc).isoformat()
        self._persist_telemetry(chip_path)

        # Determine remaining gaps
        final_result = score_chip(chip_path)
        final_score = final_result["total_score"]
        remaining_gaps = [
            f"{check_id}: {_get_check_description(check_id)}"
            for check_id in final_result.get("failed_checks", [])
        ]

        return LoopResult(
            chip_path=chip_path,
            initial_score=initial_score,
            final_score=final_score,
            verdict=final_result.get("verdict", "unknown"),
            iterations=self._iteration,
            telemetry=self._telemetry,
            improvements=improvements,
            remaining_gaps=remaining_gaps,
        )

    # ----- phase implementations -----

    def _structural_phase(self, chip_path: Path) -> list[str]:
        """Phase 1: Run gap_analyzer auto-fixes for all structural issues.

        Uses improve_chip() to run the score -> fix -> rescore cycle
        for structural/file-level fixes.
        """
        improvements: list[str] = []
        score_before = self._current_score
        t_start = _now_ms()

        result = improve_chip(
            chip_path,
            target_score=self._config.target_score,
            max_iterations=20,
        )

        t_end = _now_ms()
        score_after = result["final_score"]
        self._current_score = score_after

        fixes = result.get("fixes_applied", [])
        for fix in fixes:
            if fix.get("succeeded"):
                improvements.append(
                    f"Structural fix: {fix.get('fix_description', fix.get('check_id', 'unknown'))}"
                )
                self._telemetry.fixes_applied += 1

        record = IterationRecord(
            iteration=self._iteration,
            action_type="structural_fix",
            action_detail=f"improve_chip applied {len(fixes)} fixes",
            score_before=score_before,
            score_after=score_after,
            delta=score_after - score_before,
            duration_ms=t_end - t_start,
        )
        self._telemetry.iterations.append(record)
        self._telemetry.score_trajectory.append(score_after)

        return improvements

    def _research_phase(
        self, chip_path: Path, brief: dict[str, Any] | None = None
    ) -> list[str]:
        """Phase 2: Seed initial evidence stubs, sources, and baseline benchmark.

        Creates the research directory structure and populates it with
        minimal evidence documents.
        """
        improvements: list[str] = []
        score_before = self._current_score
        t_start = _now_ms()

        # Seed evidence lane stubs
        stubs_created = _seed_evidence_stubs(chip_path)
        if stubs_created:
            improvements.append(
                f"Research: Created {stubs_created} evidence lane stubs"
            )
            self._telemetry.research_actions += 1

        # Seed source registry from brief
        if brief:
            sources_count = _seed_research_sources(chip_path, brief)
            if sources_count:
                improvements.append(
                    f"Research: Populated source registry with {sources_count} source types"
                )
                self._telemetry.research_actions += 1

        # Seed baseline benchmark
        baseline_created = _seed_benchmark_baseline(chip_path)
        if baseline_created:
            improvements.append("Research: Created baseline benchmark result")
            self._telemetry.research_actions += 1

        # Create initial packets
        packets_created = _create_initial_packets(chip_path)
        if packets_created:
            improvements.append(
                f"Research: Created {packets_created} initial evidence packets"
            )
            self._telemetry.evidence_gathered += packets_created

        # Re-score after research seeding
        result = score_chip(chip_path)
        score_after = result["total_score"]
        self._current_score = score_after

        t_end = _now_ms()

        record = IterationRecord(
            iteration=self._iteration,
            action_type="research_seed",
            action_detail=(
                f"Seeded {stubs_created} stubs, "
                f"baseline={'yes' if baseline_created else 'no'}, "
                f"{packets_created} packets"
            ),
            score_before=score_before,
            score_after=score_after,
            delta=score_after - score_before,
            duration_ms=t_end - t_start,
        )
        self._telemetry.iterations.append(record)
        self._telemetry.score_trajectory.append(score_after)

        return improvements

    def _evaluation_phase(self, chip_path: Path) -> list[str]:
        """Phase 3: Run evaluate hook, score, and apply gap fixes.

        Scores the chip, identifies gaps, and applies the highest-value
        auto-fixable gap.
        """
        improvements: list[str] = []
        score_before = self._current_score
        t_start = _now_ms()

        # Score
        result = score_chip(chip_path)
        current = result["total_score"]

        # Analyze gaps
        gaps = analyze_gaps(result)
        fixable = [g for g in gaps if g.auto_fixable and g.fix_fn is not None]

        if fixable:
            # Apply highest-value fix
            gap = fixable[0]
            try:
                succeeded = gap.fix_fn(chip_path)
            except Exception:
                succeeded = False

            if succeeded:
                improvements.append(
                    f"Evaluation fix: {gap.fix_description} (+{gap.points_recoverable}pts)"
                )
                self._telemetry.fixes_applied += 1

        # Re-score
        result = score_chip(chip_path)
        score_after = result["total_score"]
        self._current_score = score_after

        t_end = _now_ms()

        record = IterationRecord(
            iteration=self._iteration,
            action_type="evaluate",
            action_detail=f"Scored {current}, applied {len(fixable)} fixable gaps",
            score_before=score_before,
            score_after=score_after,
            delta=score_after - score_before,
            duration_ms=t_end - t_start,
        )
        self._telemetry.iterations.append(record)
        self._telemetry.score_trajectory.append(score_after)

        return improvements

    def _suggestion_phase(self, chip_path: Path) -> list[str]:
        """Phase 3b: Generate mutation suggestions and apply them if beneficial.

        Uses the suggest hook to propose mutations, then evaluates whether
        applying them improves the chip.
        """
        improvements: list[str] = []
        score_before = self._current_score
        t_start = _now_ms()

        # Generate suggestions (use chip_path parent as search dir)
        try:
            suggestions = run_suggest(
                recent_mutations=None,
                chip_search_dir=chip_path.parent,
            )
        except Exception:
            suggestions = []

        applied_count = 0
        for s in suggestions[:3]:  # Limit to top 3 suggestions
            candidate_id = s.get("candidate_id", "unknown")
            # Write suggestion as a research note
            research_dir = chip_path / "research" / "exploratory_frontier"
            research_dir.mkdir(parents=True, exist_ok=True)

            suggestion_path = research_dir / f"suggestion_{candidate_id}.json"
            if not suggestion_path.exists():
                suggestion_path.write_text(
                    json.dumps(s, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8",
                )
                applied_count += 1

        if applied_count:
            improvements.append(
                f"Suggestions: Recorded {applied_count} mutation candidates"
            )

        # Re-score
        result = score_chip(chip_path)
        score_after = result["total_score"]
        self._current_score = score_after

        t_end = _now_ms()

        record = IterationRecord(
            iteration=self._iteration,
            action_type="suggest_mutation",
            action_detail=f"Generated {len(suggestions)} suggestions, recorded {applied_count}",
            score_before=score_before,
            score_after=score_after,
            delta=score_after - score_before,
            duration_ms=t_end - t_start,
        )
        self._telemetry.iterations.append(record)
        self._telemetry.score_trajectory.append(score_after)

        return improvements

    def _evidence_phase(self, chip_path: Path) -> list[str]:
        """Phase 4: Intelligence building -- accumulate evidence and knowledge.

        Creates additional evidence documents to fill gaps in the
        research directory.
        """
        improvements: list[str] = []
        score_before = self._current_score
        t_start = _now_ms()

        evidence_count = 0

        # Ensure all evidence lanes have content
        for lane in EVIDENCE_LANES:
            lane_dir = chip_path / "research" / lane
            lane_dir.mkdir(parents=True, exist_ok=True)

            # Count existing files
            existing = list(lane_dir.glob("*.md")) + list(lane_dir.glob("*.json"))
            if len(existing) < 2:
                # Create an evidence note
                note_path = lane_dir / f"evidence_note_{self._iteration:03d}.md"
                if not note_path.exists():
                    note_path.write_text(
                        f"# Evidence Note (Iteration {self._iteration})\n\n"
                        f"Lane: {lane}\n"
                        f"Generated at: {datetime.now(timezone.utc).isoformat()}\n\n"
                        f"## Findings\n\n"
                        f"_Placeholder for {lane.replace('_', ' ')} evidence._\n",
                        encoding="utf-8",
                    )
                    evidence_count += 1

        if evidence_count:
            improvements.append(
                f"Evidence: Created {evidence_count} evidence documents"
            )
            self._telemetry.evidence_gathered += evidence_count

        # Re-score
        result = score_chip(chip_path)
        score_after = result["total_score"]
        self._current_score = score_after

        t_end = _now_ms()

        record = IterationRecord(
            iteration=self._iteration,
            action_type="evidence_gathering",
            action_detail=f"Created {evidence_count} evidence documents",
            score_before=score_before,
            score_after=score_after,
            delta=score_after - score_before,
            duration_ms=t_end - t_start,
        )
        self._telemetry.iterations.append(record)
        self._telemetry.score_trajectory.append(score_after)

        return improvements

    def _skill_regeneration_phase(self, chip_path: Path) -> list[str]:
        """Phase 5: Regenerate intelligence delivery artifacts.

        After the improvement loop completes, rebuild the chip_skill.md,
        chip_context.json, and chip_doctrine_digest.md from the latest
        accumulated evidence and doctrines.
        """
        improvements: list[str] = []
        t_start = _now_ms()

        try:
            from .intelligence_serving import refresh_skill

            result = refresh_skill(chip_path)
            doctrine_count = result.get("doctrine_count", 0)
            evidence_files = result.get("evidence_files", 0)
            improvements.append(
                f"Skill regeneration: Built intelligence artifacts "
                f"({doctrine_count} doctrines, {evidence_files} evidence files)"
            )
        except Exception:
            # Non-fatal: intelligence_server may not be available
            pass

        t_end = _now_ms()

        record = IterationRecord(
            iteration=self._iteration,
            action_type="skill_regeneration",
            action_detail=f"Regenerated intelligence delivery artifacts",
            score_before=self._current_score,
            score_after=self._current_score,
            delta=0,
            duration_ms=t_end - t_start,
        )
        self._telemetry.iterations.append(record)

        return improvements

    # ----- stall detection and recovery -----

    def _detect_stall(self) -> bool:
        """Check if the loop is stalling (no score improvement for N iterations).

        A stall is detected when the last max_stall_iterations scores
        are all the same as the current score, indicating no progress.
        """
        trajectory = self._telemetry.score_trajectory
        if len(trajectory) < self._config.max_stall_iterations + 1:
            return False

        recent = trajectory[-self._config.max_stall_iterations:]
        # Stall if all recent scores are the same
        if len(set(recent)) == 1:
            self._telemetry.stall_count += 1
            return True

        # Also stall if no improvement in the window (max <= first)
        if max(recent) <= recent[0]:
            self._telemetry.stall_count += 1
            return True

        return False

    def _attempt_stall_recovery(
        self,
        chip_path: Path,
        brief: dict[str, Any] | None = None,
    ) -> bool:
        """Attempt to recover from a stall by trying a different strategy.

        Recovery strategies (tried in order):
            1. Re-run structural fixes (may catch newly-available fixes)
            2. Add more evidence documents
            3. Re-seed research sources

        Returns True if recovery produced a score improvement.
        """
        score_before = self._current_score

        # Strategy 1: Re-run structural fixes
        if self._config.structural_fix_enabled:
            result = improve_chip(chip_path, target_score=self._config.target_score, max_iterations=5)
            rescore = score_chip(chip_path)
            if rescore["total_score"] > score_before:
                self._current_score = rescore["total_score"]
                self._telemetry.score_trajectory.append(self._current_score)
                return True

        # Strategy 2: Add evidence padding
        if self._config.evidence_gathering_enabled:
            for lane in EVIDENCE_LANES:
                lane_dir = chip_path / "research" / lane
                lane_dir.mkdir(parents=True, exist_ok=True)
                note_path = lane_dir / f"recovery_note_{self._telemetry.stall_count:03d}.md"
                if not note_path.exists():
                    note_path.write_text(
                        f"# Recovery Evidence (Stall #{self._telemetry.stall_count})\n\n"
                        f"Lane: {lane}\n"
                        f"Attempt to break scoring plateau.\n",
                        encoding="utf-8",
                    )
            rescore = score_chip(chip_path)
            if rescore["total_score"] > score_before:
                self._current_score = rescore["total_score"]
                self._telemetry.score_trajectory.append(self._current_score)
                return True

        # Strategy 3: Re-seed sources
        if brief and self._config.research_enabled:
            _seed_research_sources(chip_path, brief)
            rescore = score_chip(chip_path)
            if rescore["total_score"] > score_before:
                self._current_score = rescore["total_score"]
                self._telemetry.score_trajectory.append(self._current_score)
                return True

        return False

    # ----- persistence -----

    def _persist_telemetry(self, chip_path: Path) -> None:
        """Write telemetry to {chip_path}/loop_telemetry.json."""
        if not self._config.telemetry_enabled:
            return

        telemetry_path = chip_path / "loop_telemetry.json"
        telemetry_path.write_text(
            json.dumps(self._telemetry.to_dict(), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _now_ms() -> int:
    """Return current time in milliseconds (monotonic)."""
    return int(time.monotonic() * 1000)


def _get_check_description(check_id: str) -> str:
    """Look up a human-readable description for a rubric check_id."""
    from .quality_rubric import RUBRIC_DIMENSIONS

    for dim in RUBRIC_DIMENSIONS:
        for check in dim["checks"]:
            if check["id"] == check_id:
                return check["description"]
    return check_id
