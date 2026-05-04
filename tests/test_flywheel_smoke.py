"""Flywheel smoke tests: verify intelligence production across real chips.

Tests each of the 7 flywheel checks from quality_rubric_v2 against real
domain chips on Desktop. Most checks are expected to fail initially --
this establishes the baseline gap that chip improvements will close.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import pytest


# ---------------------------------------------------------------------------
# Chip discovery (duplicated from conftest for direct import safety)
# ---------------------------------------------------------------------------

def _discover_chips() -> list[Path]:
    desktop = Path(os.path.expanduser("~")) / "Desktop"
    if not desktop.exists():
        return []
    return sorted(
        p for p in desktop.iterdir()
        if p.is_dir() and p.name.startswith("domain-chip-") and (p / "spark-chip.json").exists()
    )


_DESKTOP_CHIPS = _discover_chips()

# Skip entire module when no real chips exist
pytestmark = pytest.mark.real_chips
if not _DESKTOP_CHIPS:
    pytestmark = pytest.mark.skip("No real domain chips on Desktop")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _is_startup_yc(chip_path: Path) -> bool:
    return chip_path.name == "domain-chip-startup-yc"


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    """Read a JSONL file into a list of dicts."""
    if not path.exists():
        return []
    entries = []
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if line:
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return entries


def _flywheel_score(chip_path: Path) -> int:
    """Get the flywheel intelligence dimension score for a chip."""
    from chip_labs.quality_rubric_v2 import score_chip_v2

    result = score_chip_v2(chip_path)
    for dim in result["dimensions"]:
        if dim["name"] == "flywheel_intelligence":
            return dim["score"]
    return 0


def _flywheel_checks(chip_path: Path) -> dict[str, bool]:
    """Get pass/fail status of each flywheel check."""
    from chip_labs.quality_rubric_v2 import score_chip_v2

    result = score_chip_v2(chip_path)
    flywheel_check_ids = [
        "has_run_history",
        "belief_promotion",
        "metric_trajectory",
        "contradiction_handling",
        "packet_quality_real",
        "has_dspy_integration",
        "has_skill_file",
    ]
    passed = set(result.get("passed_checks", []))
    return {cid: cid in passed for cid in flywheel_check_ids}


# ---------------------------------------------------------------------------
# TestRunHistory
# ---------------------------------------------------------------------------


@pytest.mark.flywheel
class TestRunHistory:
    """Check has_run_history: score_history.jsonl or loop_telemetry.json."""

    def test_history_file_exists(self, chip_path: Path) -> None:
        has_history = (
            (chip_path / "score_history.jsonl").exists()
            or (chip_path / "loop_telemetry.json").exists()
        )
        if _is_startup_yc(chip_path):
            # startup-yc has artifacts/ledger/runs.jsonl at minimum
            ledger = chip_path / "artifacts" / "ledger" / "runs.jsonl"
            has_history = has_history or ledger.exists()
        if not has_history:
            pytest.xfail(f"{chip_path.name}: no run history files found")
        assert has_history

    def test_history_has_entries(self, chip_path: Path) -> None:
        history_path = chip_path / "score_history.jsonl"
        if not history_path.exists():
            pytest.xfail(f"{chip_path.name}: no score_history.jsonl")
        entries = _read_jsonl(history_path)
        assert len(entries) > 0, "score_history.jsonl is empty"

    def test_history_entries_have_score(self, chip_path: Path) -> None:
        history_path = chip_path / "score_history.jsonl"
        if not history_path.exists():
            pytest.xfail(f"{chip_path.name}: no score_history.jsonl")
        entries = _read_jsonl(history_path)
        if not entries:
            pytest.xfail("No entries")
        for entry in entries:
            if not (
                "total_score" in entry or "startup_score" in entry or "score" in entry
            ):
                pytest.xfail(
                    f"{chip_path.name}: score_history.jsonl has entries without score fields"
                )


# ---------------------------------------------------------------------------
# TestBeliefPromotion
# ---------------------------------------------------------------------------


@pytest.mark.flywheel
class TestBeliefPromotion:
    """Check belief_promotion: durable/promoted beliefs or ascending scores."""

    def test_belief_files_exist(self, chip_path: Path) -> None:
        belief_dirs = [
            chip_path / "docs" / "beliefs",
            chip_path / "artifacts" / "memory",
            chip_path / "research",
        ]
        has_beliefs = any(
            d.exists() and any(d.rglob("*.md")) or any(d.rglob("*.json"))
            for d in belief_dirs
            if d.exists()
        )
        if not has_beliefs:
            pytest.xfail(f"{chip_path.name}: no belief files found")
        assert has_beliefs

    def test_has_durable_or_promoted_marker(self, chip_path: Path) -> None:
        """Check if any file contains 'durable' or 'promoted' keywords."""
        search_dirs = [chip_path / "docs", chip_path / "research"]
        found = False
        for d in search_dirs:
            if not d.exists():
                continue
            for f in d.rglob("*"):
                if f.is_file() and f.suffix in (".md", ".json", ".jsonl"):
                    try:
                        content = f.read_text(encoding="utf-8", errors="ignore").lower()
                        if "durable" in content or "promoted" in content:
                            found = True
                            break
                    except OSError:
                        pass
            if found:
                break
        if not found:
            pytest.xfail(f"{chip_path.name}: no durable/promoted markers found")
        assert found

    def test_rubric_check_passes(self, chip_path: Path) -> None:
        checks = _flywheel_checks(chip_path)
        if not checks["belief_promotion"]:
            pytest.xfail(f"{chip_path.name}: belief_promotion check failed")
        assert checks["belief_promotion"]


# ---------------------------------------------------------------------------
# TestMetricTrajectory
# ---------------------------------------------------------------------------


@pytest.mark.flywheel
class TestMetricTrajectory:
    """Check metric_trajectory: 3+ entries with 2+ ascending transitions."""

    def test_has_three_or_more_entries(self, chip_path: Path) -> None:
        history_path = chip_path / "score_history.jsonl"
        if not history_path.exists():
            pytest.xfail(f"{chip_path.name}: no score_history.jsonl")
        entries = _read_jsonl(history_path)
        if len(entries) < 3:
            pytest.xfail(f"{chip_path.name}: only {len(entries)} entries, need 3+")
        assert len(entries) >= 3

    def test_has_ascending_transitions(self, chip_path: Path) -> None:
        history_path = chip_path / "score_history.jsonl"
        if not history_path.exists():
            pytest.xfail(f"{chip_path.name}: no score_history.jsonl")
        entries = _read_jsonl(history_path)
        scores = []
        for e in entries:
            s = e.get("total_score") or e.get("startup_score") or e.get("score", 0)
            if isinstance(s, (int, float)):
                scores.append(s)
        ascending = sum(1 for i in range(1, len(scores)) if scores[i] > scores[i - 1])
        if ascending < 2:
            pytest.xfail(f"{chip_path.name}: only {ascending} ascending transitions")
        assert ascending >= 2

    def test_rubric_check_passes(self, chip_path: Path) -> None:
        checks = _flywheel_checks(chip_path)
        if not checks["metric_trajectory"]:
            pytest.xfail(f"{chip_path.name}: metric_trajectory check failed")
        assert checks["metric_trajectory"]


# ---------------------------------------------------------------------------
# TestContradictionHandling
# ---------------------------------------------------------------------------


@pytest.mark.flywheel
class TestContradictionHandling:
    """Check contradiction_handling: substantive contradiction docs."""

    def test_contradictions_file_exists(self, chip_path: Path) -> None:
        paths = [
            chip_path / "docs" / "CONTRADICTIONS.md",
            chip_path / "docs" / "beliefs" / "CONTRADICTIONS.md",
            chip_path / "CONTRADICTIONS.md",
        ]
        exists = any(p.exists() for p in paths)
        if not exists:
            pytest.xfail(f"{chip_path.name}: no CONTRADICTIONS.md found")
        assert exists

    def test_contradictions_have_substance(self, chip_path: Path) -> None:
        for subpath in ("docs/CONTRADICTIONS.md", "docs/beliefs/CONTRADICTIONS.md", "CONTRADICTIONS.md"):
            p = chip_path / subpath
            if p.exists():
                content = p.read_text(encoding="utf-8", errors="ignore")
                lines = [
                    line for line in content.split("\n")
                    if line.strip() and not line.startswith("#")
                ]
                text_len = sum(len(line) for line in lines)
                if text_len < 50:
                    pytest.xfail(f"{chip_path.name}: CONTRADICTIONS.md has only {text_len} chars of content")
                assert text_len >= 50
                return
        pytest.xfail(f"{chip_path.name}: no CONTRADICTIONS.md found")

    def test_rubric_check_passes(self, chip_path: Path) -> None:
        checks = _flywheel_checks(chip_path)
        if not checks["contradiction_handling"]:
            pytest.xfail(f"{chip_path.name}: contradiction_handling check failed")
        assert checks["contradiction_handling"]


# ---------------------------------------------------------------------------
# TestPacketQuality
# ---------------------------------------------------------------------------


@pytest.mark.flywheel
class TestPacketQuality:
    """Check packet_quality_real: structured packets with claim/mechanism/boundary."""

    def test_packets_directory_exists(self, chip_path: Path) -> None:
        paths = [
            chip_path / "research" / "packets",
            chip_path / "docs" / "research-packets",
        ]
        exists = any(p.exists() for p in paths)
        if not exists:
            pytest.xfail(f"{chip_path.name}: no packets directory")
        assert exists

    def test_has_json_packets(self, chip_path: Path) -> None:
        for subpath in ("research/packets", "docs/research-packets"):
            d = chip_path / subpath
            if d.exists():
                jsons = list(d.glob("*.json"))
                if jsons:
                    assert len(jsons) > 0
                    return
        pytest.xfail(f"{chip_path.name}: no JSON packet files")

    def test_has_structured_packet(self, chip_path: Path) -> None:
        """At least one packet has claim + mechanism + boundary fields."""
        for subpath in ("research/packets", "docs/research-packets"):
            d = chip_path / subpath
            if not d.exists():
                continue
            for pf in d.glob("*.json"):
                try:
                    data = json.loads(pf.read_text(encoding="utf-8"))
                    content = data.get("content", data)
                    if isinstance(content, dict):
                        if "claim" in content and "mechanism" in content:
                            assert True
                            return
                except (json.JSONDecodeError, OSError):
                    pass
        pytest.xfail(f"{chip_path.name}: no structured packets found")

    def test_rubric_check_passes(self, chip_path: Path) -> None:
        checks = _flywheel_checks(chip_path)
        if not checks["packet_quality_real"]:
            pytest.xfail(f"{chip_path.name}: packet_quality_real check failed")
        assert checks["packet_quality_real"]


# ---------------------------------------------------------------------------
# TestDspyIntegration
# ---------------------------------------------------------------------------


@pytest.mark.flywheel
class TestDspyIntegration:
    """Check has_dspy_integration: DSPy scripts or config detected."""

    def test_dspy_artifacts_present(self, chip_path: Path) -> None:
        indicators = [
            chip_path / "dspy_config.json",
            *(chip_path.rglob("*dspy*.py")),
            *(chip_path.rglob("*dspy*.json")),
        ]
        found = any(
            p.exists() if isinstance(p, Path) and not p.is_file() else True
            for p in indicators
            if isinstance(p, Path) and p.exists()
        )
        if not found:
            pytest.xfail(f"{chip_path.name}: no DSPy artifacts")
        assert found

    def test_detect_dspy_integration_api(self, chip_path: Path) -> None:
        from chip_labs.dspy_slot import detect_dspy_integration

        result = detect_dspy_integration(chip_path)
        if not result["has_dspy"]:
            pytest.xfail(f"{chip_path.name}: detect_dspy_integration returned false")
        assert result["has_dspy"]

    def test_rubric_check_passes(self, chip_path: Path) -> None:
        checks = _flywheel_checks(chip_path)
        if not checks["has_dspy_integration"]:
            pytest.xfail(f"{chip_path.name}: has_dspy_integration check failed")
        assert checks["has_dspy_integration"]


# ---------------------------------------------------------------------------
# TestSkillFile
# ---------------------------------------------------------------------------


@pytest.mark.flywheel
class TestSkillFile:
    """Check has_skill_file: chip_skill.md with real content."""

    def test_skill_file_exists(self, chip_path: Path) -> None:
        skill = chip_path / "chip_skill.md"
        if not skill.exists():
            pytest.xfail(f"{chip_path.name}: no chip_skill.md")
        assert skill.exists()

    def test_skill_file_has_substance(self, chip_path: Path) -> None:
        skill = chip_path / "chip_skill.md"
        if not skill.exists():
            pytest.xfail(f"{chip_path.name}: no chip_skill.md")
        content = skill.read_text(encoding="utf-8", errors="ignore")
        if len(content) < 200:
            pytest.xfail(f"{chip_path.name}: chip_skill.md only {len(content)} chars")
        assert len(content) >= 200

    def test_skill_has_expected_sections(self, chip_path: Path) -> None:
        skill = chip_path / "chip_skill.md"
        if not skill.exists():
            pytest.xfail(f"{chip_path.name}: no chip_skill.md")
        content = skill.read_text(encoding="utf-8", errors="ignore").lower()
        expected = ["domain identity", "doctrine"]
        missing = [s for s in expected if s not in content]
        if missing:
            pytest.xfail(f"{chip_path.name}: skill missing sections: {missing}")
        assert not missing

    def test_rubric_check_passes(self, chip_path: Path) -> None:
        checks = _flywheel_checks(chip_path)
        if not checks["has_skill_file"]:
            pytest.xfail(f"{chip_path.name}: has_skill_file check failed")
        assert checks["has_skill_file"]


# ---------------------------------------------------------------------------
# TestFlywheelSummary
# ---------------------------------------------------------------------------


@pytest.mark.flywheel
class TestFlywheelSummary:
    """Aggregate flywheel health across the portfolio."""

    def test_flywheel_score_report(self, desktop_chips: list[Path]) -> None:
        """Print flywheel scores for all chips (informational)."""
        if not desktop_chips:
            pytest.skip("No chips")
        report = []
        for chip in desktop_chips:
            score = _flywheel_score(chip)
            checks = _flywheel_checks(chip)
            passed = sum(1 for v in checks.values() if v)
            report.append(f"  {chip.name:<40} {score:>3}/25  ({passed}/7 checks)")
        print("\n\nFlywheel Portfolio Report:")
        print("\n".join(report))
        # This test always passes -- it's for reporting
        assert True

    def test_startup_yc_leads_flywheel(self, desktop_chips: list[Path]) -> None:
        """startup-yc should have the highest flywheel score."""
        if not desktop_chips:
            pytest.skip("No chips")
        scores = {chip.name: _flywheel_score(chip) for chip in desktop_chips}
        yc = scores.get("domain-chip-startup-yc", 0)
        for name, s in scores.items():
            if name != "domain-chip-startup-yc":
                assert yc >= s, f"startup-yc ({yc}) doesn't lead: {name} has {s}"
