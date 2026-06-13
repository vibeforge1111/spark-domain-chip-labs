"""Hybrid verdict: a doctrine strategy gate + an external outcome predictor.

Pattern, not a finished tool. Two independent channels:
  A. strategy gate  -- deterministic hard rules (traps) + the doctrine verdict.
                       Channel A can VETO (kill) regardless of predicted reach.
  B. outcome channel -- an external predictor's forecast. Channel B can only
                       DEMOTE a ship to fix, or fast-track a fix; it never
                       overrides a strategy kill and never invents a ship.

Why this shape: a strategy violation that's forecast to go viral is still a kill
(your rules outrank reach). A clean hook forecast to underperform is a fix, not a
ship. Keep the channels separate so each stays auditable.

CRITICAL: validate the external predictor on YOUR fresh sample before trusting its
number (assets/calibration_metrics.py). A documented accuracy is a claim about a
past moment; predictors drift. Treat a stale or unvalidated forecast as advisory
color, not a gate.
"""
from __future__ import annotations
import re

# Hard strategy traps -> immediate kill, channel B irrelevant. Edit to your doctrine.
TRAP_PATTERNS = [
    (re.compile(r"\bnot clickbait\b|\(not clickbait\)", re.I), "not-clickbait tic"),
    (re.compile(r"\bsave this\b|\byou.ll thank me later\b", re.I), "bookmark bait"),
]


def trap_screen(text: str) -> list[str]:
    return [label for rx, label in TRAP_PATTERNS if rx.search(text)]


def combine(doctrine_verdict: str, outcome_tier: int | None) -> tuple[str, str]:
    """outcome_tier: 1..5 (1=bottom, 5=top) from the external predictor, or None.

    Returns (final_verdict, reason).
    """
    if doctrine_verdict == "kill":
        return "kill", "strategy gate veto"
    if doctrine_verdict == "ship":
        if outcome_tier is None or outcome_tier >= 3:
            return "ship", "strategy ship, outcome neutral-or-strong"
        return "fix", "strategy clean but outcome forecast weak; revise for reach first"
    # doctrine == fix
    if outcome_tier is not None and outcome_tier >= 4:
        return "fix-fast", "outcome forecast strong; apply the fix and ship same day"
    return "fix", "doctrine fix stands"


def hybrid_verdict(text: str, doctrine_verdict: str, outcome_tier: int | None,
                   outcome_validated: bool = False) -> dict:
    traps = trap_screen(text)
    if traps:
        return {"verdict": "kill", "reason": f"trap screen: {'; '.join(traps)} (hard veto)", "traps": traps}
    v, why = combine(doctrine_verdict, outcome_tier if outcome_validated else None)
    return {
        "verdict": v, "reason": why, "doctrine_verdict": doctrine_verdict,
        "outcome_tier": outcome_tier,
        "outcome_used": outcome_validated,
        "note": None if outcome_validated else "outcome predictor unvalidated on fresh data; tier shown but not gating",
    }


if __name__ == "__main__":
    import json
    # demo
    for dv, tier in [("kill", 5), ("ship", 2), ("ship", 4), ("fix", 5)]:
        print(json.dumps(hybrid_verdict("a clean hook", dv, tier, outcome_validated=True)))
