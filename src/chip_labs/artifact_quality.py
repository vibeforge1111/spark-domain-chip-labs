"""Local artifact-quality scoring for Spark design docs and PR writeups."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any
from datetime import date
import hashlib
import json


CLAIM_BOUNDARY = "artifact_quality local review only"
PROVENANCE_SOURCE = "artifact_quality_v1"
MANIFEST_PATH = "benchmark/artifact_quality_manifest.json"
CASE_EXPECTATION_ROLES = {"baseline", "candidate", "traps"}
CASE_EXPECTATION_FIELDS = {
    "verdict",
    "min_score",
    "max_score",
    "required_trap_flags",
}

CHECKS = (
    {
        "id": "acceptance_gates",
        "label": "Acceptance gates",
        "keywords": ("acceptance", "gate", "success criteria", "done when"),
        "repair": "Add explicit acceptance gates or success criteria.",
    },
    {
        "id": "runnable_evidence",
        "label": "Runnable evidence",
        "keywords": ("pytest", "creator-run-smoke", "ruff", "command", "recompute"),
        "repair": "Name the exact verification command or recompute path.",
    },
    {
        "id": "test_evidence",
        "label": "Test evidence",
        "keywords": ("test", "tests", "passed", "failed", "coverage"),
        "repair": "Add test evidence and current pass/fail state.",
    },
    {
        "id": "risk_boundary",
        "label": "Risk boundary",
        "keywords": ("risk", "failure mode", "blocker", "unsafe", "known limit"),
        "repair": "Name the main risks, known limits, or blockers.",
    },
    {
        "id": "rollback_plan",
        "label": "Rollback plan",
        "keywords": ("rollback", "revert", "deprecation", "back out"),
        "repair": "Add rollback or deprecation steps.",
    },
    {
        "id": "claim_boundary",
        "label": "Claim boundary",
        "keywords": ("claim boundary", "do not claim", "local only", "not network_absorbable"),
        "repair": "State what the artifact proves and what it does not prove.",
    },
    {
        "id": "mission_handoff",
        "label": "Mission handoff",
        "keywords": ("mission", "handoff", "owner", "next action", "operator"),
        "repair": "Add owner, next action, or mission-control handoff details.",
    },
)

POLISH_WORDS = (
    "beautiful",
    "delightful",
    "elegant",
    "frictionless",
    "game-changing",
    "intuitive",
    "magical",
    "seamless",
    "world-class",
)

PROOF_CHECKS = {"acceptance_gates", "runnable_evidence", "test_evidence", "rollback_plan"}


def score_artifact_quality(
    text: str,
    *,
    artifact_id: str = "",
    artifact_kind: str = "design_doc",
    source_path: str = "",
) -> dict[str, Any]:
    """Score a design/PR artifact for review-readiness evidence."""

    normalized = _normalize(text)
    checks = [_score_check(normalized, check) for check in CHECKS]
    passed = [check for check in checks if check["status"] == "pass"]
    failed = [check for check in checks if check["status"] == "fail"]
    score = round(len(passed) / len(checks), 4)
    failed_ids = {check["id"] for check in failed}
    polish_hits = _keyword_hits(normalized, POLISH_WORDS)
    trap_flags = []
    if polish_hits and failed_ids & PROOF_CHECKS:
        trap_flags.append("polished_but_unproven")
    verdict = _verdict(score, trap_flags, failed_ids)
    return {
        "packet_kind": "artifact_quality_report",
        "artifact_id": artifact_id,
        "artifact_kind": artifact_kind,
        "source_path": source_path,
        "verdict": verdict,
        "score": score,
        "status_counts": {
            "pass": len(passed),
            "fail": len(failed),
        },
        "checks": checks,
        "trap_flags": trap_flags,
        "polish_hits": polish_hits,
        "missing_checks": [check["id"] for check in failed],
        "repair_actions": [check["repair"] for check in failed],
        "claim_boundary": CLAIM_BOUNDARY,
        "safe_claim": "This artifact is locally reviewable for evidence completeness.",
        "unsafe_claim": "This artifact quality score does not prove product correctness or replace human review.",
    }


def score_artifact_quality_file(path: str | Path, *, artifact_kind: str = "design_doc") -> dict[str, Any]:
    """Read and score an artifact-quality input file."""

    source = Path(path)
    return score_artifact_quality(
        source.read_text(encoding="utf-8"),
        artifact_id=source.stem,
        artifact_kind=artifact_kind,
        source_path=source.as_posix(),
    )


def compute_artifact_quality_benchmark(run_dir: str | Path) -> dict[str, Any]:
    """Compute artifact-quality baseline/candidate/trap reports for a creator run."""

    run_path = Path(run_dir)
    manifest = _load_manifest(run_path / MANIFEST_PATH)
    baseline_path = _resolve_run_path(run_path, manifest["baseline_artifact"])
    candidate_path = _resolve_run_path(run_path, manifest["candidate_artifact"])
    trap_paths = [
        _resolve_run_path(run_path, relative_path)
        for relative_path in manifest.get("trap_artifacts", [])
    ]

    baseline = score_artifact_quality_file(baseline_path, artifact_kind="pr_writeup")
    candidate = score_artifact_quality_file(candidate_path, artifact_kind="pr_writeup")
    traps = [
        score_artifact_quality_file(path, artifact_kind="design_doc")
        for path in trap_paths
    ]
    expectation_checks = _evaluate_case_expectations(
        manifest,
        baseline=baseline,
        candidate=candidate,
        traps=traps,
    )
    reviewer_calibration_rows = _evaluate_reviewer_calibration(
        run_path,
        manifest.get("reviewer_calibration_cases", []),
    )
    mean_delta = round(candidate["score"] - baseline["score"], 4)
    trap_regressions = sum(
        1 for trap in traps
        if "polished_but_unproven" not in trap["trap_flags"] or trap["verdict"] != "blocked"
    )
    calibration_passed = (
        all(check["status"] == "pass" for check in expectation_checks)
        and all(row["status"] == "pass" for row in reviewer_calibration_rows)
    )
    provenance = _benchmark_provenance(
        run_path,
        [
            MANIFEST_PATH,
            str(manifest["baseline_artifact"]),
            str(manifest["candidate_artifact"]),
            *[str(path) for path in manifest.get("trap_artifacts", [])],
            *[
                str(case["artifact_path"])
                for case in manifest.get("reviewer_calibration_cases", [])
                if (
                    isinstance(case, dict)
                    and case.get("artifact_path")
                    and (run_path / str(case["artifact_path"])).exists()
                )
            ],
        ],
    )
    baseline_report = {
        "schema_version": "adaptive_creator_loop.benchmark_report.v1",
        "benchmark_family": "artifact_quality_review",
        "mean_score": baseline["score"],
        "case_count": 1,
        "artifact_report": baseline,
        "expectation_checks": [
            check for check in expectation_checks if check["case_role"] == "baseline"
        ],
        "provenance": provenance,
    }
    candidate_report = {
        "schema_version": "adaptive_creator_loop.benchmark_report.v1",
        "benchmark_family": "artifact_quality_review",
        "mean_score": candidate["score"],
        "mean_delta": mean_delta,
        "case_count": 1,
        "trap_regressions": trap_regressions,
        "artifact_report": candidate,
        "trap_reports": traps,
        "expectation_checks": expectation_checks,
        "reviewer_calibration_rows": reviewer_calibration_rows,
        "reviewer_calibration_case_count": len(reviewer_calibration_rows),
        "calibration_verdict": "pass" if calibration_passed else "blocked",
        "decision": (
            "keep"
            if mean_delta > 0 and trap_regressions == 0 and calibration_passed
            else "revert"
        ),
        "provenance": provenance,
    }
    absorption_report = {
        "schema_version": "adaptive_creator_loop.absorption_summary.v1",
        "benchmark_family": "artifact_quality_review",
        "mean_validated_pack_delta": mean_delta,
        "trap_band_case_count": len(traps),
        "trap_regressions": trap_regressions,
        "expectation_checks": expectation_checks,
        "reviewer_calibration_rows": reviewer_calibration_rows,
        "reviewer_calibration_case_count": len(reviewer_calibration_rows),
        "calibration_verdict": "pass" if calibration_passed else "blocked",
        "all_modes_present": True,
        "all_modes_scored": True,
        "provenance": provenance,
    }
    return {
        "schema_version": "artifact_quality.benchmark_result.v1",
        "verdict": "pass" if candidate_report["decision"] == "keep" else "blocked",
        "baseline": baseline_report,
        "candidate": candidate_report,
        "absorption": absorption_report,
    }


def run_artifact_quality_benchmark(run_dir: str | Path) -> dict[str, Any]:
    """Run and save artifact-quality reports for a creator run."""

    run_path = Path(run_dir)
    result = compute_artifact_quality_benchmark(run_path)
    _write_json(run_path / "reports" / "baseline.json", result["baseline"])
    _write_json(run_path / "reports" / "candidate.json", result["candidate"])
    _write_json(run_path / "reports" / "absorption_summary.json", result["absorption"])
    return result


def format_artifact_quality_markdown(report: dict[str, Any]) -> str:
    """Render an operator-facing artifact-quality report."""

    lines = [
        "# Artifact Quality Report",
        "",
        f"- Verdict: `{report.get('verdict', 'unknown')}`",
        f"- Score: `{report.get('score', 0):.2f}`",
        f"- Claim boundary: `{report.get('claim_boundary', CLAIM_BOUNDARY)}`",
        f"- Trap flags: `{', '.join(report.get('trap_flags', [])) or 'none'}`",
        "",
        "## Checks",
        "",
    ]
    for check in report.get("checks", []):
        lines.append(f"- `{check['status']}` {check['label']}: {check['message']}")
    if report.get("repair_actions"):
        lines.extend(["", "## Repair Actions", ""])
        for action in report["repair_actions"]:
            lines.append(f"- {action}")
    lines.extend([
        "",
        "## Claim Boundary",
        "",
        f"Safe: {report.get('safe_claim', '')}",
        "",
        f"Unsafe: {report.get('unsafe_claim', '')}",
    ])
    return "\n".join(lines).rstrip() + "\n"


def _score_check(normalized: str, check: dict[str, Any]) -> dict[str, str]:
    hits = _keyword_hits(normalized, check["keywords"])
    status = "pass" if hits else "fail"
    message = f"Found: {', '.join(hits)}." if hits else check["repair"]
    return {
        "id": check["id"],
        "label": check["label"],
        "status": status,
        "message": message,
        "repair": check["repair"],
    }


def _verdict(score: float, trap_flags: list[str], failed_ids: set[str]) -> str:
    if trap_flags or len(failed_ids & PROOF_CHECKS) >= 2:
        return "blocked"
    if score < 0.85:
        return "needs_revision"
    return "review_ready"


def _keyword_hits(normalized: str, keywords: tuple[str, ...]) -> list[str]:
    hits = []
    for keyword in keywords:
        pattern = r"\b" + re.escape(keyword.lower()).replace(r"\ ", r"\s+") + r"\b"
        if re.search(pattern, normalized):
            hits.append(keyword)
    return hits


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def _load_manifest(path: Path) -> dict[str, Any]:
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise FileNotFoundError(f"{path} is required for artifact-quality benchmark") from None
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path} is not valid JSON: {exc}") from exc
    if not isinstance(manifest, dict):
        raise ValueError(f"{path} must contain a JSON object")
    for key in ("baseline_artifact", "candidate_artifact"):
        if not str(manifest.get(key, "")).strip():
            raise ValueError(f"{path} must include {key}")
    if not isinstance(manifest.get("trap_artifacts"), list):
        manifest["trap_artifacts"] = []
    if manifest.get("case_expectations") is not None and not isinstance(
        manifest["case_expectations"],
        dict,
    ):
        raise ValueError(f"{path} case_expectations must be an object")
    if isinstance(manifest.get("case_expectations"), dict):
        unknown_roles = sorted(
            set(manifest["case_expectations"]) - CASE_EXPECTATION_ROLES
        )
        if unknown_roles:
            raise ValueError(
                f"{path} case_expectations has unknown role(s): "
                + ", ".join(unknown_roles)
            )
        for role, expectation in manifest["case_expectations"].items():
            if not isinstance(expectation, dict):
                raise ValueError(
                    f"{path} case_expectations.{role} must be an object"
                )
            unknown_fields = sorted(set(expectation) - CASE_EXPECTATION_FIELDS)
            if unknown_fields:
                raise ValueError(
                    f"{path} case_expectations.{role} has unknown field(s): "
                    + ", ".join(unknown_fields)
                )
    if manifest.get("reviewer_calibration_cases") is not None and not isinstance(
        manifest["reviewer_calibration_cases"],
        list,
    ):
        raise ValueError(f"{path} reviewer_calibration_cases must be a list")
    return manifest


def _evaluate_case_expectations(
    manifest: dict[str, Any],
    *,
    baseline: dict[str, Any],
    candidate: dict[str, Any],
    traps: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    expectations = manifest.get("case_expectations") or {}
    if not expectations:
        return []
    checks: list[dict[str, Any]] = []
    for case_role, report in (
        ("baseline", baseline),
        ("candidate", candidate),
    ):
        expected = expectations.get(case_role)
        if isinstance(expected, dict):
            checks.extend(_expectation_checks(case_role, report, expected))
    trap_expectations = expectations.get("traps")
    if isinstance(trap_expectations, dict):
        for index, report in enumerate(traps, start=1):
            checks.extend(_expectation_checks(f"trap:{index}", report, trap_expectations))
    return checks


def _evaluate_reviewer_calibration(
    run_path: Path,
    cases: list[Any],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, case in enumerate(cases, start=1):
        if not isinstance(case, dict):
            rows.append(_blocked_calibration_row(index, "case must be an object"))
            continue
        artifact_path = str(case.get("artifact_path", "")).strip()
        if not artifact_path:
            rows.append(_blocked_calibration_row(index, "artifact_path is required"))
            continue
        try:
            report = score_artifact_quality_file(
                _resolve_run_path(run_path, artifact_path),
                artifact_kind=str(case.get("artifact_kind", "design_doc")),
            )
        except FileNotFoundError as exc:
            rows.append(_blocked_calibration_row(index, str(exc), artifact_path=artifact_path))
            continue
        expected = {
            key: case[key]
            for key in ("min_score", "max_score", "required_trap_flags")
            if key in case
        }
        if "reviewer_verdict" in case:
            expected["verdict"] = case["reviewer_verdict"]
        checks = _expectation_checks(f"reviewer_calibration:{index}", report, expected)
        expected_missing = case.get("required_missing_checks", [])
        if isinstance(expected_missing, list):
            for missing_check in expected_missing:
                checks.append(
                    _expectation_check(
                        f"reviewer_calibration:{index}",
                        f"required_missing_check:{missing_check}",
                        missing_check in report["missing_checks"],
                        f"expected missing check {missing_check}",
                    )
                )
        rows.append({
            "case_id": str(case.get("case_id", f"reviewer-calibration-{index}")),
            "artifact_path": artifact_path,
            "artifact_kind": report["artifact_kind"],
            "reviewer_verdict": str(case.get("reviewer_verdict", "")),
            "scorer_verdict": report["verdict"],
            "score": report["score"],
            "status": "pass" if all(check["status"] == "pass" for check in checks) else "fail",
            "checks": checks,
        })
    return rows


def _blocked_calibration_row(
    index: int,
    message: str,
    *,
    artifact_path: str = "",
) -> dict[str, Any]:
    return {
        "case_id": f"reviewer-calibration-{index}",
        "artifact_path": artifact_path,
        "artifact_kind": "unknown",
        "reviewer_verdict": "",
        "scorer_verdict": "blocked",
        "score": 0.0,
        "status": "fail",
        "checks": [
            _expectation_check(
                f"reviewer_calibration:{index}",
                "case_shape",
                False,
                message,
            )
        ],
    }


def _expectation_checks(
    case_role: str,
    report: dict[str, Any],
    expected: dict[str, Any],
) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    if "verdict" in expected:
        checks.append(
            _expectation_check(
                case_role,
                "verdict",
                report["verdict"] == expected["verdict"],
                f"expected {expected['verdict']}, got {report['verdict']}",
            )
        )
    if "min_score" in expected:
        checks.append(
            _expectation_check(
                case_role,
                "min_score",
                report["score"] >= float(expected["min_score"]),
                f"expected score >= {expected['min_score']}, got {report['score']}",
            )
        )
    if "max_score" in expected:
        checks.append(
            _expectation_check(
                case_role,
                "max_score",
                report["score"] <= float(expected["max_score"]),
                f"expected score <= {expected['max_score']}, got {report['score']}",
            )
        )
    for trap_flag in expected.get("required_trap_flags", []):
        checks.append(
            _expectation_check(
                case_role,
                f"required_trap_flag:{trap_flag}",
                trap_flag in report["trap_flags"],
                f"expected trap flag {trap_flag}",
            )
        )
    return checks


def _expectation_check(
    case_role: str,
    check_id: str,
    passed: bool,
    message: str,
) -> dict[str, str]:
    return {
        "case_role": case_role,
        "check_id": check_id,
        "status": "pass" if passed else "fail",
        "message": message,
    }


def _resolve_run_path(run_path: Path, relative_path: str) -> Path:
    path = run_path / relative_path
    if not path.exists():
        raise FileNotFoundError(f"{relative_path} does not exist in {run_path}")
    return path


def _benchmark_provenance(run_path: Path, relative_paths: list[str]) -> dict[str, Any]:
    return {
        "source": PROVENANCE_SOURCE,
        "computed_at": date.today().isoformat(),
        "recomputed_from": relative_paths,
        "input_hashes": {
            relative_path: _sha256_file(run_path / relative_path)
            for relative_path in relative_paths
        },
    }


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
