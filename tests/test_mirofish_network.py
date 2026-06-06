"""Tests for mirofish.network small-world topology helpers.

build_persona_network constructs a Watts-Strogatz-style influence graph
used by simulation.py to propagate adoption events between personas.
network_influence_propagation walks that graph to produce per-persona
influence scores. Both helpers are deterministic (md5+seed) but ship
without direct test coverage — a regression to symmetry, determinism, or
the small-population fallback would only surface inside a full mirofish
simulation run.
"""

from __future__ import annotations

from chip_labs.mirofish.network import (
    build_persona_network,
    network_influence_propagation,
)


def _make_personas(n: int) -> list[dict]:
    personas: list[dict] = []
    for i in range(n):
        personas.append({
            "persona_id": f"p{i}",
            "persona_type": "a" if i % 2 == 0 else "b",
            "network_reach": 0.6 if i < n // 2 else 0.8,
            "influence_score": 0.6 + (i % 3) * 0.1,
            "activity_score": 0.7,
            "adoption_state": {"domain-x": ["unaware", "aware", "adopted", "advocating"][i % 4]},
        })
    return personas


def test_build_persona_network_is_deterministic_with_same_seed() -> None:
    personas = _make_personas(10)
    a = build_persona_network(personas, seed=42)
    b = build_persona_network(personas, seed=42)
    # Adjacency lists are unordered sets logically, compare as sets.
    assert {k: set(v) for k, v in a.items()} == {k: set(v) for k, v in b.items()}


def test_build_persona_network_changes_with_different_seed() -> None:
    personas = _make_personas(10)
    a = build_persona_network(personas, seed=42)
    c = build_persona_network(personas, seed=99)
    # Seeds drive rewiring + homophily decisions deterministically — outputs
    # should not be identical across seeds for a network of this size.
    assert {k: set(v) for k, v in a.items()} != {k: set(v) for k, v in c.items()}


def test_build_persona_network_edges_are_symmetric() -> None:
    personas = _make_personas(10)
    net = build_persona_network(personas, seed=42)
    for pid, neighbors in net.items():
        for neighbor in neighbors:
            assert pid in net.get(neighbor, []), (
                f"asymmetric edge: {pid} -> {neighbor} but not back"
            )


def test_build_persona_network_returns_all_persona_ids_as_keys() -> None:
    personas = _make_personas(10)
    net = build_persona_network(personas, seed=42)
    assert set(net.keys()) == {p["persona_id"] for p in personas}


def test_build_persona_network_small_population_returns_fully_connected_excluding_self() -> None:
    personas = _make_personas(2)
    net = build_persona_network(personas)
    # Below the n<3 threshold the function returns a fully connected
    # adjacency excluding self.
    assert net == {"p0": ["p1"], "p1": ["p0"]}


def test_build_persona_network_empty_input_returns_empty_dict() -> None:
    assert build_persona_network([]) == {}


def test_network_influence_propagation_returns_score_per_persona() -> None:
    personas = _make_personas(10)
    net = build_persona_network(personas, seed=42)
    influence = network_influence_propagation(personas, net, "domain-x")
    assert set(influence.keys()) == {p["persona_id"] for p in personas}
    for v in influence.values():
        assert isinstance(v, float)


def test_network_influence_propagation_skips_missing_neighbors_safely() -> None:
    personas = _make_personas(5)
    # Add a phantom neighbor not present in personas list.
    net = build_persona_network(personas, seed=42)
    for pid in net:
        net[pid].append("ghost-persona")
    # Should not raise on the dangling neighbor.
    influence = network_influence_propagation(personas, net, "domain-x")
    assert set(influence.keys()) == {p["persona_id"] for p in personas}


def test_network_influence_propagation_zero_for_unknown_domain() -> None:
    personas = _make_personas(6)
    net = build_persona_network(personas, seed=42)
    # No persona has any state for 'novel-domain' — all stages default to
    # 'unaware' (weight=0), so total influence is 0 for everyone.
    influence = network_influence_propagation(personas, net, "novel-domain")
    assert all(v == 0.0 for v in influence.values())
