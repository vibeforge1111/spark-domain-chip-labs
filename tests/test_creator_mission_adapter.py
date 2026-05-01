from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from chip_labs.creator_mission_adapter import build_creator_mission_status


STARTUP_VALIDATION = Path(
    "docs/creator_system/examples/startup-yc-operator-validation/validation_plan.json"
)


def _smoke(verdict: str = "ready_for_swarm_packet") -> dict[str, object]:
    blocked = verdict == "blocked"
    return {
        "schema_version": "adaptive_creator_loop.smoke_result.v1",
        "run_dir": "runs/demo",
        "verdict": verdict,
        "evidence_tier": "transfer_supported",
        "status_counts": {"pass": 68, "warn": 0, "fail": 0 if not blocked else 1},
        "blocking_checks": [] if not blocked else ["candidate_delta"],
        "warning_checks": [],
        "automation": {
            "blocked": blocked,
            "ci_exit_code": 1 if blocked else 0,
            "recommended_next_command": "Review provenance, privacy, rollback, and claim boundaries before publication.",
        },
        "checks": [],
        "missing_paths": [],
        "next_actions": [
            "Review provenance, trap status, rollback, and privacy boundary before network publication."
        ],
    }


def test_creator_mission_status_emits_read_only_surface_adapters() -> None:
    status = build_creator_mission_status(
        mission_id="mission-1",
        smoke=_smoke(),
        startup_validation=json.loads(STARTUP_VALIDATION.read_text(encoding="utf-8")),
    )

    assert status["schema_version"] == "adaptive_creator_loop.creator_mission_status.v1"
    assert status["read_only"] is True
    assert status["canonical"]["verdict"] == "ready_for_swarm_packet"
    assert status["canonical"]["stage_status"] == "review_required"
    assert status["publication"]["network_absorbable"] is False
    assert status["publication"]["swarm_shared_allowed"] is False
    assert set(status["surface_adapters"]) == {
        "builder",
        "telegram",
        "spawner",
        "canvas",
        "kanban",
    }
    assert status["surface_adapters"]["builder"]["may_mutate_state"] is False
    assert status["surface_adapters"]["spawner"]["may_execute"] is False
    assert status["surface_adapters"]["canvas"]["may_edit_artifacts"] is False
    assert status["surface_adapters"]["kanban"]["may_change_verdict"] is False


def test_creator_mission_status_preserves_blockers_from_canonical_packets() -> None:
    status = build_creator_mission_status(
        smoke=_smoke("blocked"),
        doctor={
            "schema_version": "adaptive_creator_loop.doctor_result.v1",
            "verdict": "blocked",
            "repair_steps": [
                {
                    "action": "Regenerate benchmark reports, then rerun smoke.",
                }
            ],
            "smoke": {},
        },
    )

    assert status["canonical"]["stage_status"] == "blocked"
    assert status["blockers"][0]["source"] == "smoke"
    assert "Regenerate benchmark reports" in status["next_actions"][0]
    assert status["surface_adapters"]["kanban"]["columns"]["blocked"]


def test_creator_mission_status_blocks_swarm_publication_request() -> None:
    status = build_creator_mission_status(
        smoke=_smoke(),
        publish_mode="swarm_shared",
        startup_validation=json.loads(STARTUP_VALIDATION.read_text(encoding="utf-8")),
    )

    assert status["publication"]["requested_network_absorption"] is True
    assert status["publication"]["swarm_shared_allowed"] is False
    assert "publication_gate" in {blocker["source"] for blocker in status["blockers"]}
    assert "publication approval" in status["publication"]["blocked_reason"]
    assert "Network absorption is not approved" in status["surface_adapters"]["telegram"]["text"]


def test_cli_creator_mission_status_outputs_read_only_packet(tmp_path: Path) -> None:
    smoke_path = tmp_path / "smoke.json"
    output_path = tmp_path / "mission.json"
    smoke_path.write_text(json.dumps(_smoke(), indent=2) + "\n", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "chip_labs.cli",
            "creator-mission-status",
            "--smoke",
            str(smoke_path),
            "--startup-validation",
            str(STARTUP_VALIDATION),
            "--mission-id",
            "mission-cli",
            "--output",
            str(output_path),
        ],
        cwd=Path.cwd(),
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["mission_id"] == "mission-cli"
    assert payload["surface_adapters"]["telegram"]["may_request_secret_paste"] is False
