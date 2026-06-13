"""Deterministic calibration metrics for a creator-run benchmark.

No LLM in any number this emits. Reads an oracle (per-case true band + optional
measured outcome) and predicted verdicts, reports band accuracy, Spearman vs the
measured outcome, ship precision/recall, opposite-error count, seed agreement,
and a paired bootstrap CI on the Spearman difference between two arms.

This is the headline-metric engine the calibration lane (SKILL.md Step 9b) needs.
Edit the loaders at the bottom for your file shapes.

Usage:
    python calibration_metrics.py oracle.jsonl predictions.json
where predictions.json maps arm_name -> {case_id: verdict}.
"""
from __future__ import annotations
import json
import random
import sys

ORD = {"kill": 0, "fix": 1, "ship": 2}  # edit to your verdict vocabulary


def spearman(xs, ys):
    def ranks(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            for k in range(i, j + 1):
                r[order[k]] = (i + j) / 2 + 1
            i = j + 1
        return r
    rx, ry, n = ranks(xs), ranks(ys), len(xs)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((rx[i] - mx) * (ry[i] - my) for i in range(n))
    dx = sum((rx[i] - mx) ** 2 for i in range(n)) ** 0.5
    dy = sum((ry[i] - my) ** 2 for i in range(n)) ** 0.5
    return num / (dx * dy) if dx and dy else 0.0


def arm_metrics(verdicts, oracle):
    ids = [i for i in oracle if i in verdicts]
    exact = sum(1 for i in ids if verdicts[i] == oracle[i]["band"])
    opp = sum(1 for i in ids if abs(ORD[verdicts[i]] - ORD[oracle[i]["band"]]) == 2)
    has_outcome = all("outcome" in oracle[i] for i in ids)
    rho = spearman([ORD[verdicts[i]] for i in ids], [oracle[i]["outcome"] for i in ids]) if has_outcome else None
    called = [i for i in ids if verdicts[i] == "ship"]
    true_s = [i for i in ids if oracle[i]["band"] == "ship"]
    prec = sum(1 for i in called if oracle[i]["band"] == "ship") / len(called) if called else 0.0
    rec = sum(1 for i in true_s if verdicts[i] == "ship") / len(true_s) if true_s else 0.0
    return {"n": len(ids), "band_accuracy": round(exact / len(ids), 4), "opposite_errors": opp,
            "spearman_vs_outcome": round(rho, 4) if rho is not None else None,
            "ship_precision": round(prec, 4), "ship_recall": round(rec, 4)}


def paired_bootstrap(a, b, oracle, n_boot=10000, seed=42):
    ids = [i for i in oracle if i in a and i in b and "outcome" in oracle[i]]
    if not ids:
        return None
    y = [oracle[i]["outcome"] for i in ids]
    av, bv = [ORD[a[i]] for i in ids], [ORD[b[i]] for i in ids]
    base = spearman(av, y) - spearman(bv, y)
    rng, diffs = random.Random(seed), []
    for _ in range(n_boot):
        idx = [rng.randrange(len(ids)) for _ in ids]
        ys = [y[k] for k in idx]
        diffs.append(spearman([av[k] for k in idx], ys) - spearman([bv[k] for k in idx], ys))
    diffs.sort()
    return {"diff": round(base, 4), "ci95": [round(diffs[int(.025 * n_boot)], 4), round(diffs[int(.975 * n_boot)], 4)],
            "frac_resamples_le_0": round(sum(1 for d in diffs if d <= 0) / n_boot, 4)}


def majority(arms_by_seed):
    """arms_by_seed: list of {id: verdict}; returns majority verdict per id (ties -> lower ordinal)."""
    out, ids = {}, set().union(*[set(a) for a in arms_by_seed])
    for i in ids:
        votes = [a[i] for a in arms_by_seed if i in a]
        if votes:
            out[i] = max(set(votes), key=lambda v: (votes.count(v), -ORD[v]))
    return out


if __name__ == "__main__":
    oracle = {json.loads(l)["id"]: json.loads(l) for l in open(sys.argv[1], encoding="utf-8") if l.strip()}
    preds = json.load(open(sys.argv[2], encoding="utf-8"))
    report = {"per_arm": {a: arm_metrics(v, oracle) for a, v in preds.items()}}
    names = list(preds)
    if len(names) >= 2:
        report["bootstrap_%s_minus_%s" % (names[1], names[0])] = paired_bootstrap(preds[names[1]], preds[names[0]], oracle)
    print(json.dumps(report, indent=2))
