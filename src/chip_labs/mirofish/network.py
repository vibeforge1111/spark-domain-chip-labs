"""Small-world network topology for persona influence propagation.

Models realistic social networks among personas using the Watts-Strogatz
model: each persona connects to ~6 neighbors with same-type homophily
bonus. High network_reach personas get 2x connections.

Influence propagation follows network edges instead of global aggregate,
making advocacy conversion more realistic. Opinion leaders (influence > 0.75)
get 2x advocacy weight, making skeptic conversion a high-impact event.
"""

from __future__ import annotations

import hashlib
from typing import Any


def build_persona_network(
    personas: list[dict[str, Any]],
    base_connections: int = 6,
    rewire_probability: float = 0.15,
    seed: int = 42,
) -> dict[str, list[str]]:
    """Build a small-world network among personas.

    Uses Watts-Strogatz model:
    1. Start with a ring lattice where each node connects to K nearest neighbors
    2. Rewire each edge with probability p to create shortcuts
    3. Add same-type homophily bonus (extra connections within type)
    4. High network_reach personas get extra connections

    Args:
        personas: List of persona dicts.
        base_connections: Average connections per persona (K in WS model).
        rewire_probability: Probability of rewiring (p in WS model).
        seed: Random seed for deterministic network.

    Returns:
        Adjacency list: persona_id -> list of connected persona_ids.
    """
    n = len(personas)
    if n < 3:
        # Too few personas for a network
        ids = [p["persona_id"] for p in personas]
        return {pid: [other for other in ids if other != pid] for pid in ids}

    # Index personas
    id_list = [p["persona_id"] for p in personas]
    type_map = {p["persona_id"]: p["persona_type"] for p in personas}
    reach_map = {p["persona_id"]: p.get("network_reach", 0.5) for p in personas}

    # Step 1: Ring lattice
    half_k = max(1, base_connections // 2)
    adjacency: dict[str, set[str]] = {pid: set() for pid in id_list}

    for i, pid in enumerate(id_list):
        for j in range(1, half_k + 1):
            neighbor = id_list[(i + j) % n]
            adjacency[pid].add(neighbor)
            adjacency[neighbor].add(pid)

    # Step 2: Rewire with probability p (deterministic via hash)
    for i, pid in enumerate(id_list):
        for j in range(1, half_k + 1):
            neighbor_idx = (i + j) % n
            # Deterministic "random" decision
            h = hashlib.md5(f"{seed}-rewire-{i}-{j}".encode()).hexdigest()
            roll = (int(h[:8], 16) % 10000) / 10000.0

            if roll < rewire_probability:
                # Rewire: remove old neighbor, add random new one
                old_neighbor = id_list[neighbor_idx]
                # Pick new neighbor (deterministic)
                h2 = hashlib.md5(f"{seed}-newtarget-{i}-{j}".encode()).hexdigest()
                new_idx = int(h2[:8], 16) % n
                new_neighbor = id_list[new_idx]

                if new_neighbor != pid and new_neighbor not in adjacency[pid]:
                    adjacency[pid].discard(old_neighbor)
                    adjacency[old_neighbor].discard(pid)
                    adjacency[pid].add(new_neighbor)
                    adjacency[new_neighbor].add(pid)

    # Step 3: Same-type homophily bonus (1-2 extra connections within type)
    type_groups: dict[str, list[str]] = {}
    for pid in id_list:
        ptype = type_map[pid]
        type_groups.setdefault(ptype, []).append(pid)

    for ptype, members in type_groups.items():
        for i, pid in enumerate(members):
            # Add 1-2 same-type connections
            h = hashlib.md5(f"{seed}-homophily-{pid}".encode()).hexdigest()
            extra = 1 + (int(h[:4], 16) % 2)  # 1 or 2
            for k in range(extra):
                h2 = hashlib.md5(f"{seed}-homo-{pid}-{k}".encode()).hexdigest()
                target_idx = int(h2[:8], 16) % len(members)
                target = members[target_idx]
                if target != pid:
                    adjacency[pid].add(target)
                    adjacency[target].add(pid)

    # Step 4: High network_reach personas get extra connections
    for pid in id_list:
        reach = reach_map.get(pid, 0.5)
        if reach > 0.7:
            # Extra connections proportional to reach
            extra = int((reach - 0.5) * 8)  # 1-4 extra
            for k in range(extra):
                h = hashlib.md5(f"{seed}-reach-{pid}-{k}".encode()).hexdigest()
                target_idx = int(h[:8], 16) % n
                target = id_list[target_idx]
                if target != pid:
                    adjacency[pid].add(target)
                    adjacency[target].add(pid)

    return {pid: list(neighbors) for pid, neighbors in adjacency.items()}


def network_influence_propagation(
    personas: list[dict[str, Any]],
    network: dict[str, list[str]],
    domain_id: str,
    domain_tags: list[str] | None = None,
) -> dict[str, float]:
    """Propagate influence through the network for a specific domain.

    Each persona's adoption state influences their network neighbors.
    Opinion leaders (influence_score > 0.75) get 2x advocacy weight.

    Returns a dict of persona_id -> influence_received from network.
    """
    persona_lookup = {p["persona_id"]: p for p in personas}
    influence_received: dict[str, float] = {}

    # Stage weights for influence propagation
    stage_weight = {
        "unaware": 0.0, "aware": 0.0, "interested": 0.05,
        "evaluating": 0.1, "trial": 0.15, "adopted": 0.3,
        "committed": 0.5, "advocating": 0.8, "churned": -0.1,
    }

    for pid, neighbors in network.items():
        total_influence = 0.0
        count = 0

        for neighbor_id in neighbors:
            neighbor = persona_lookup.get(neighbor_id)
            if neighbor is None:
                continue

            stage = neighbor["adoption_state"].get(domain_id, "unaware")
            weight = stage_weight.get(stage, 0.0)

            if weight == 0.0:
                continue

            # Base influence from neighbor
            inf = neighbor["influence_score"] * weight * neighbor["activity_score"]

            # Opinion leader bonus: high-influence personas who advocate
            # have 2x weight (makes skeptic conversion high-impact)
            if neighbor["influence_score"] > 0.75 and stage in ("advocating", "committed"):
                inf *= 2.0

            # Same-type trust bonus
            persona = persona_lookup.get(pid)
            if persona and neighbor["persona_type"] == persona["persona_type"]:
                inf *= 1.3

            # Churned neighbors create negative influence (social proof of failure)
            if stage == "churned":
                inf = -abs(inf) * 0.5

            total_influence += inf
            count += 1

        # Normalize by connection count to prevent large networks from dominating
        if count > 0:
            influence_received[pid] = round(total_influence / max(count, 1) * min(count, 8) / 4, 4)
        else:
            influence_received[pid] = 0.0

    return influence_received
