"""Sample real cases with measured outcomes into a calibrated benchmark.

Template. Replace `load_records()` with your data source. The point: build an
oracle from MEASURED outcome, not your own expected answers, so the run can claim
above benchmark_signal (see BENCHMARK_AUTHORSHIP_AND_EVIDENCE_EXPIRY.md).

Outputs cases_calibrated.jsonl with rows:
    {id, input, oracle_band, outcome, source: {...}}
where oracle_band in {kill, fix, ship} is derived from the measured outcome and
`outcome` is the raw numeric signal (kept for Spearman in calibration_metrics.py).
"""
from __future__ import annotations
import json
import random
from pathlib import Path

# ---- EDIT THESE ----
OUT = Path("cases_calibrated.jsonl")
SEED = 11
PER_BAND = 40              # aim for 100+ total
MAX_PER_SUBJECT = 1        # avoid one prolific subject dominating a band
EXCLUDE_IDS = set()        # ids already used in a prior pack (no leakage)


def load_records() -> list[dict]:
    """Return [{id, input, subject, outcome (float, normalized within-subject)}].

    Normalize the outcome WITHIN subject (e.g. vs the subject's own average) so
    bands mean the same thing across subjects of different scale. Replace this
    stub with your real loader (sqlite, jsonl, api export...).
    """
    raise NotImplementedError("wire up your data source")


def band_of(outcome: float) -> str | None:
    """Map normalized outcome to a verdict band. Tune the cutoffs to your data."""
    if outcome >= 2.0:   # top decile-ish
        return "ship"
    if outcome <= 0.4:   # clearly below average
        return "kill"
    if 0.8 <= outcome <= 1.3:  # around average
        return "fix"
    return None          # ambiguous middle -> not used as an oracle case


def main():
    rng = random.Random(SEED)
    pool = {"ship": [], "fix": [], "kill": []}
    for r in load_records():
        if r["id"] in EXCLUDE_IDS:
            continue
        b = band_of(r["outcome"])
        if b and len((r.get("input") or "").strip()) >= 40:
            pool[b].append(r)

    picked = []
    for band, items in pool.items():
        rng.shuffle(items)
        per_subject, chosen = {}, []
        for it in items:
            if per_subject.get(it["subject"], 0) >= MAX_PER_SUBJECT:
                continue
            chosen.append(it)
            per_subject[it["subject"]] = per_subject.get(it["subject"], 0) + 1
            if len(chosen) >= PER_BAND:
                break
        picked.extend(chosen)
    rng.shuffle(picked)

    with OUT.open("w", encoding="utf-8") as f:
        for i, it in enumerate(picked, 1):
            f.write(json.dumps({
                "id": f"cal-{i:03d}",
                "input": it["input"],
                "oracle_band": it["outcome"] and band_of(it["outcome"]),
                "band": band_of(it["outcome"]),          # calibration_metrics.py reads .band
                "outcome": round(float(it["outcome"]), 4),  # raw signal for Spearman
                "source": {"subject": it["subject"], "id": it["id"]},  # keep local; never publish
            }, ensure_ascii=False) + "\n")

    print(json.dumps({"pool": {k: len(v) for k, v in pool.items()},
                      "picked": {b: sum(1 for p in picked if band_of(p["outcome"]) == b) for b in pool},
                      "subjects": len({p["subject"] for p in picked}), "out": str(OUT)}, indent=2))


if __name__ == "__main__":
    main()
