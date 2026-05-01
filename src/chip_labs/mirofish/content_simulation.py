"""MiroFish-style content simulation for ranking ideas, hooks, and drafts.

The first version is deterministic and local-only. It mirrors the future shape
of persona-batch plus multi-RLM judging without calling any provider. That keeps
the contract testable before real model adapters and outcome calibration exist.
"""

from __future__ import annotations

import re
from statistics import median
from typing import Any


DEFAULT_PERSONA_SEGMENTS = (
    "founder-builders",
    "technical-operators",
    "creator-economy-readers",
    "skeptical-experts",
)

DEFAULT_RLM_JUDGES = (
    "spark-local-judge",
    "frontier-reasoning-judge",
    "fast-taste-judge",
)

CLAIM_BOUNDARY = "candidate_review local simulator protocol only"

CONTENT_SELECTION_TERMS = {
    "angle",
    "angles",
    "content",
    "draft",
    "drafts",
    "hook",
    "hooks",
    "idea",
    "ideas",
    "post",
    "posts",
    "rank",
    "select",
    "title",
    "titles",
}

SELECTION_INTENT_TERMS = {
    "best",
    "better",
    "choose",
    "compare",
    "pick",
    "rank",
    "score",
    "select",
    "strongest",
    "test",
    "winner",
}

PERSONA_KEYWORDS = {
    "founder-builders": {
        "customer",
        "startup",
        "founder",
        "traction",
        "revenue",
        "sales",
        "growth",
        "wedge",
    },
    "technical-operators": {
        "system",
        "workflow",
        "agent",
        "benchmark",
        "tool",
        "automation",
        "debug",
        "proof",
    },
    "creator-economy-readers": {
        "content",
        "audience",
        "viral",
        "hook",
        "title",
        "post",
        "creator",
        "distribution",
    },
    "skeptical-experts": {
        "evidence",
        "failure",
        "risk",
        "boundary",
        "calibration",
        "proof",
        "specific",
        "tradeoff",
    },
}

VAGUE_WORDS = {
    "amazing",
    "best",
    "ultimate",
    "revolutionary",
    "game-changing",
    "secret",
    "insane",
}

UTILITY_WORDS = {
    "how",
    "why",
    "checklist",
    "framework",
    "mistake",
    "example",
    "guide",
    "playbook",
    "proof",
    "benchmark",
}


def should_invoke_content_simulation(text: str) -> bool:
    """Return true when a prompt looks like content candidate selection."""

    tokens = _tokens(text)
    has_content_surface = bool(tokens & CONTENT_SELECTION_TERMS)
    has_selection_intent = bool(tokens & SELECTION_INTENT_TERMS)
    has_multiple_candidates = len(extract_content_candidates(text)) >= 2
    return has_content_surface and (has_selection_intent or has_multiple_candidates)


def build_content_simulation_packet(
    task: str,
    *,
    candidates: list[str | dict[str, Any]] | None = None,
    persona_segments: list[str] | None = None,
    rlm_judges: list[str] | None = None,
) -> dict[str, Any]:
    """Build a simulator packet from a natural-language task plus candidates."""

    raw_candidates = candidates if candidates is not None else extract_content_candidates(task)
    return {
        "task": task,
        "triggered_by": "mirofish_content_simulation",
        "candidates": _normalize_candidates(raw_candidates),
        "persona_segments": persona_segments or list(DEFAULT_PERSONA_SEGMENTS),
        "rlm_judges": rlm_judges or list(DEFAULT_RLM_JUDGES),
        "claim_boundary": CLAIM_BOUNDARY,
    }


def extract_content_candidates(text: str) -> list[str]:
    """Extract likely content options from bullets, numbered lines, or quotes."""

    candidates: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        bullet_match = re.match(r"^(?:[-*]|\d+[.)])\s+(.+)$", stripped)
        if bullet_match:
            candidates.append(bullet_match.group(1).strip())
            continue
        quoted = re.findall(r'"([^"]{8,})"', stripped)
        candidates.extend(item.strip() for item in quoted)
    return _dedupe_preserve_order(candidates)


def simulate_content_selection(packet: dict[str, Any]) -> dict[str, Any]:
    """Rank content candidates across persona segments and judge profiles."""

    candidates = _normalize_candidates(packet.get("candidates"))
    persona_segments = _normalize_list(
        packet.get("persona_segments"), DEFAULT_PERSONA_SEGMENTS
    )
    rlm_judges = _normalize_list(packet.get("rlm_judges"), DEFAULT_RLM_JUDGES)
    if not candidates:
        return {
            "packet_kind": "mirofish_content_simulation_result",
            "verdict": "blocked",
            "blocking_checks": ["candidates_required"],
            "rankings": [],
            "next_actions": ["Provide at least one content candidate."],
            "claim_boundary": CLAIM_BOUNDARY,
        }

    rows = []
    for candidate in candidates:
        for persona in persona_segments:
            for judge in rlm_judges:
                rows.append(_score_candidate_row(candidate, persona, judge))

    rankings = _aggregate_rankings(candidates, rows, persona_segments)
    top = rankings[0]
    return {
        "packet_kind": "mirofish_content_simulation_result",
        "verdict": "ranked",
        "top_candidate_id": top["candidate_id"],
        "top_candidate_text": top["text"],
        "candidate_count": len(candidates),
        "persona_segments": persona_segments,
        "rlm_judges": rlm_judges,
        "row_count": len(rows),
        "aggregation_rule": (
            "rank by median composite predicted save/share/reply intent, "
            "then inspect weak persona segments"
        ),
        "rankings": rankings,
        "score_rows": rows,
        "claim_boundary": CLAIM_BOUNDARY,
        "requires_before_transfer": [
            "multi-seed simulator reruns",
            "human/operator calibration",
            "privacy and publication review",
            "comparison against actual content outcomes",
        ],
    }


def format_content_simulation_markdown(result: dict[str, Any]) -> str:
    """Render a compact operator-facing readout."""

    lines = [
        "# MiroFish Content Simulation",
        "",
        f"- Verdict: `{result.get('verdict', 'unknown')}`",
        f"- Claim boundary: `{result.get('claim_boundary', CLAIM_BOUNDARY)}`",
        f"- Candidates: `{result.get('candidate_count', 0)}`",
        f"- Score rows: `{result.get('row_count', 0)}`",
        "",
        "## Ranking",
        "",
    ]
    for index, ranking in enumerate(result.get("rankings", []), start=1):
        lines.append(
            f"{index}. `{ranking['candidate_id']}` "
            f"score `{ranking['median_composite']:.3f}` - {ranking['text']}"
        )
        lines.append(f"   Weak segment: `{ranking['weakest_persona']}`")
    return "\n".join(lines).rstrip() + "\n"


def _normalize_candidates(raw_candidates: Any) -> list[dict[str, str]]:
    if not isinstance(raw_candidates, list):
        return []
    candidates = []
    for index, raw_candidate in enumerate(raw_candidates, start=1):
        if isinstance(raw_candidate, dict):
            text = str(raw_candidate.get("text") or raw_candidate.get("title") or "")
            candidate_id = str(raw_candidate.get("id") or f"candidate-{index}")
        else:
            text = str(raw_candidate)
            candidate_id = f"candidate-{index}"
        if text.strip():
            candidates.append({"id": candidate_id, "text": text.strip()})
    return candidates


def _dedupe_preserve_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped = []
    for value in values:
        key = value.lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(value)
    return deduped


def _normalize_list(value: Any, default: tuple[str, ...]) -> list[str]:
    if isinstance(value, list):
        normalized = [str(item) for item in value if str(item).strip()]
        if normalized:
            return normalized
    return list(default)


def _score_candidate_row(
    candidate: dict[str, str], persona: str, judge: str
) -> dict[str, Any]:
    text = candidate["text"]
    tokens = _tokens(text)
    persona_match = _keyword_overlap(tokens, PERSONA_KEYWORDS.get(persona, set()))
    utility_match = _keyword_overlap(tokens, UTILITY_WORDS)
    vague_penalty = min(_keyword_overlap(tokens, VAGUE_WORDS) * 0.08, 0.18)
    specificity = _specificity_score(text, tokens)
    curiosity = _curiosity_score(text)
    judge_bias = _judge_bias(judge, specificity, curiosity, utility_match)

    save_intent = _clamp(
        0.35
        + specificity * 0.22
        + utility_match * 0.08
        + persona_match * 0.06
        + judge_bias
        - vague_penalty
    )
    share_intent = _clamp(
        0.30
        + curiosity * 0.20
        + persona_match * 0.08
        + specificity * 0.08
        + judge_bias
        - vague_penalty
    )
    reply_likelihood = _clamp(
        0.24
        + (0.12 if "?" in text else 0.0)
        + curiosity * 0.12
        + persona_match * 0.05
        - vague_penalty / 2
    )
    audience_specificity = _clamp(0.30 + persona_match * 0.12 + specificity * 0.25)
    composite = median(
        [save_intent, share_intent, reply_likelihood, audience_specificity]
    )

    return {
        "candidate_id": candidate["id"],
        "persona_segment": persona,
        "rlm_judge": judge,
        "predicted_save_intent": round(save_intent, 4),
        "predicted_share_intent": round(share_intent, 4),
        "reply_likelihood": round(reply_likelihood, 4),
        "audience_specificity": round(audience_specificity, 4),
        "composite_score": round(composite, 4),
    }


def _aggregate_rankings(
    candidates: list[dict[str, str]],
    rows: list[dict[str, Any]],
    persona_segments: list[str],
) -> list[dict[str, Any]]:
    rankings = []
    for candidate in candidates:
        candidate_rows = [
            row for row in rows if row["candidate_id"] == candidate["id"]
        ]
        composites = [row["composite_score"] for row in candidate_rows]
        persona_scores = {
            persona: median(
                [
                    row["composite_score"]
                    for row in candidate_rows
                    if row["persona_segment"] == persona
                ]
            )
            for persona in persona_segments
        }
        weakest_persona = min(persona_scores, key=persona_scores.get)
        rankings.append(
            {
                "candidate_id": candidate["id"],
                "text": candidate["text"],
                "median_composite": round(median(composites), 4),
                "mean_composite": round(sum(composites) / len(composites), 4),
                "weakest_persona": weakest_persona,
                "weakest_persona_score": round(persona_scores[weakest_persona], 4),
                "persona_scores": {
                    persona: round(score, 4)
                    for persona, score in persona_scores.items()
                },
            }
        )
    return sorted(
        rankings,
        key=lambda item: (
            item["median_composite"],
            item["weakest_persona_score"],
            item["candidate_id"],
        ),
        reverse=True,
    )


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9-]+", text.lower()))


def _keyword_overlap(tokens: set[str], keywords: set[str]) -> int:
    return len(tokens & keywords)


def _specificity_score(text: str, tokens: set[str]) -> float:
    has_number = any(char.isdigit() for char in text)
    useful_length = 6 <= len(tokens) <= 18
    concrete = _keyword_overlap(tokens, UTILITY_WORDS | {"specific", "real", "case"})
    return min((0.25 if has_number else 0.0) + (0.25 if useful_length else 0.0) + concrete * 0.12, 1.0)


def _curiosity_score(text: str) -> float:
    markers = ["why", "how", "mistake", "secret", "what", "vs", "?"]
    lower = text.lower()
    return min(sum(1 for marker in markers if marker in lower) * 0.18, 1.0)


def _judge_bias(
    judge: str, specificity: float, curiosity: float, utility_match: int
) -> float:
    if judge == "frontier-reasoning-judge":
        return specificity * 0.04
    if judge == "fast-taste-judge":
        return curiosity * 0.04
    if judge == "spark-local-judge":
        return min(utility_match * 0.015, 0.045)
    return 0.0


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))
