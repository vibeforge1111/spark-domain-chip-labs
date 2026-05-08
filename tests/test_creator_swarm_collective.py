from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from chip_labs.creator_swarm_collective import build_creator_swarm_collective_payload


STARTUP_YC_RUN = Path("docs/creator_system/examples/startup-yc-creator-run")


def test_creator_swarm_collective_dry_run_payload_is_private_and_thin() -> None:
    payload = build_creator_swarm_collective_payload(
        STARTUP_YC_RUN,
        workspace_id="workspace-private-1",
        agent_id="agent-creator-1",
        emitted_at="2026-05-05T00:00:00+00:00",
    )

    assert payload["workspaceId"] == "workspace-private-1"
    assert payload["agentId"] == "agent-creator-1"
    assert payload["runtimeSource"]["kind"] == "spark_researcher"
    assert payload["runtimeSource"]["loopKind"] == "benchmark"
    assert payload["runtimeSource"]["sourceInstanceId"] == "agent-creator-1"
    assert payload["runtimeSource"]["sourceRunId"].startswith("spark-researcher:creator-system-dry-run:")
    assert payload["runtimeSource"]["sourcePacketId"] == "swarm-packet-2026-05-01-startup-yc"
    assert payload["specialization"]["memoryPolicy"] == "isolated"
    assert payload["runtimePulse"]["runtimeState"] == "idle"
    assert payload["runtimePulse"]["stageKey"] == "ready_for_swarm_packet"
    assert payload["intelligencePulse"]["pendingUpgradeCount"] == 0
    assert payload["evolutionPaths"] == []
    assert payload["patterns"] == []
    assert payload["contradictions"] == []
    assert payload["upgrades"] == []
    assert payload["upgradeDeliveries"] == []
    assert payload["masteries"][0]["shareScope"] == "private"
    assert payload["masteries"][0]["status"] == "transfer_supported"
    assert payload["masteryReviews"][0]["decision"] == "defer"
    assert "does not publish" in payload["masteryReviews"][0]["reason"]
    assert payload["outcomes"][0]["verdict"] == "improved"

    assert payload["artifactRefs"]
    assert all(ref["path"] and not Path(ref["path"]).is_absolute() for ref in payload["artifactRefs"])
    assert all(ref["hash"] and len(ref["hash"]) == 64 for ref in payload["artifactRefs"])
    assert "creator-intent.json" in {ref["path"] for ref in payload["artifactRefs"]}
    assert "swarm/contribution_packet.json" in {
        ref["path"] for ref in payload["artifactRefs"]
    }


def test_creator_swarm_collective_dry_run_has_no_network_approval_tokens() -> None:
    payload = build_creator_swarm_collective_payload(
        STARTUP_YC_RUN,
        workspace_id="workspace-private-1",
        agent_id="agent-creator-1",
        emitted_at="2026-05-05T00:00:00+00:00",
    )
    serialized = json.dumps(payload, sort_keys=True)

    assert "network_absorbable\": true" not in serialized
    assert "network_publication_allowed\": true" not in serialized
    assert "approved_for_network" not in serialized
    assert "published" not in serialized
    assert "C:\\\\" not in serialized
    assert "private_key" not in serialized.lower()


def test_creator_swarm_collective_dry_run_cli_writes_payload(tmp_path: Path) -> None:
    output = tmp_path / "collective-payload.json"
    env = {**os.environ, "PYTHONPATH": str(Path.cwd() / "src")}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "chip_labs.cli",
            "creator-swarm-collective-dry-run",
            str(STARTUP_YC_RUN),
            "--workspace-id",
            "workspace-private-cli",
            "--agent-id",
            "agent-cli",
            "--output",
            str(output),
        ],
        cwd=Path.cwd(),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["workspaceId"] == "workspace-private-cli"
    assert payload["agentId"] == "agent-cli"
    assert payload["artifactRefs"]
