"""Validation script: Scaffold 3 chips, score them, run doctor.

Tests the entire pipeline end-to-end:
1. Scaffold chips from briefs across 3 categories
2. Score each immediately
3. Run doctor (auto-fix) on each
4. Verify score improvements
"""

import json
import sys
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from chip_labs.scaffold import scaffold_chip, validate_brief
from chip_labs.quality_rubric import score_chip
from chip_labs.gap_analyzer import analyze_gaps, improve_chip
from chip_labs.category_templates import apply_template, detect_category


# ---------------------------------------------------------------------------
# Test briefs across 3 categories
# ---------------------------------------------------------------------------

BRIEFS = [
    {
        "domain_id": "quantum-computing",
        "domain_name": "Quantum Computing Research",
        "category": "science",
        "description": "Evaluate quantum computing approaches, algorithms, and hardware platforms",
        "mutation_axes": [
            {"name": "algorithm_class", "values": ["variational", "grover", "shor", "qaoa", "vqe"]},
            {"name": "hardware_platform", "values": ["superconducting", "trapped_ion", "photonic", "topological"]},
            {"name": "error_correction", "values": ["surface_code", "repetition", "concatenated", "none"]},
        ],
        "primary_metric": "quantum_advantage_score",
    },
    {
        "domain_id": "cybersecurity-red-team",
        "domain_name": "Cybersecurity Red Team",
        "category": "technology",
        "description": "Evaluate offensive security techniques, vulnerability assessment, and defense strategies",
        "mutation_axes": [
            {"name": "attack_vector", "values": ["network", "application", "social", "physical"]},
            {"name": "target_tier", "values": ["web_app", "infrastructure", "cloud", "iot"]},
            {"name": "defense_posture", "values": ["minimal", "standard", "hardened", "zero_trust"]},
        ],
        "primary_metric": "security_posture_score",
    },
    {
        "domain_id": "indie-game-design",
        "domain_name": "Indie Game Design",
        "category": "gaming",
        "description": "Evaluate indie game design patterns, player engagement, and creative mechanics",
        "mutation_axes": [
            {"name": "genre", "values": ["platformer", "roguelike", "narrative", "puzzle", "sandbox"]},
            {"name": "art_style", "values": ["pixel", "hand_drawn", "low_poly", "abstract"]},
            {"name": "core_loop", "values": ["explore", "collect", "build", "survive", "compete"]},
        ],
        "primary_metric": "game_feel_score",
    },
]


def run_validation():
    """Run full validation pipeline."""
    print("=" * 70)
    print("CHIP FACTORY VALIDATION")
    print("=" * 70)

    results = []

    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        for brief in BRIEFS:
            print(f"\n{'-' * 70}")
            print(f"CHIP: {brief['domain_id']} ({brief['category']})")
            print(f"{'-' * 70}")

            # 1. Validate brief
            errors = validate_brief(brief)
            assert not errors, f"Brief validation failed: {errors}"
            print(f"  Brief valid: YES")

            # 2. Apply category template
            enhanced = apply_template(brief)
            print(f"  Category template applied: {enhanced.get('_template_applied')}")

            # 3. Scaffold chip
            chip_dir = scaffold_chip(enhanced, tmppath)
            print(f"  Scaffolded to: {chip_dir.name}")

            # 4. Verify directory structure
            expected_files = [
                "spark-chip.json",
                "spark-researcher.project.json",
                "pyproject.toml",
                "README.md",
            ]
            for f in expected_files:
                assert (chip_dir / f).exists(), f"Missing: {f}"
            print(f"  Core files present: YES")

            # 5. Verify src directory
            module = brief["domain_id"].replace("-", "_")
            src_dir = chip_dir / "src" / module
            assert src_dir.exists(), f"Missing src/{module}"
            for hook in ["cli.py", "evaluate.py", "suggest.py", "packets.py", "watchtower.py"]:
                assert (src_dir / hook).exists(), f"Missing hook: {hook}"
            print(f"  All hooks generated: YES")

            # 6. Verify tests
            test_dir = chip_dir / "tests"
            assert test_dir.exists(), "Missing tests/"
            test_count = len(list(test_dir.glob("test_*.py")))
            print(f"  Test files generated: {test_count}")

            # 7. Score the scaffold
            score_result = score_chip(chip_dir)
            scaffold_score = score_result["total_score"]
            scaffold_verdict = score_result["verdict"]
            passed = len(score_result["passed_checks"])
            failed = len(score_result["failed_checks"])
            print(f"\n  SCAFFOLD SCORE: {scaffold_score}/100 ({scaffold_verdict})")
            print(f"  Passed: {passed}/30 | Failed: {failed}/30")

            for dim in score_result["dimensions"]:
                print(f"    {dim['label']}: {dim['score']}/{dim['max_points']}")

            # 8. Analyze gaps
            gaps = analyze_gaps(score_result)
            auto_fixable = [g for g in gaps if g.auto_fixable]
            print(f"\n  Gaps found: {len(gaps)} ({len(auto_fixable)} auto-fixable)")

            # 9. Run doctor (improve_chip)
            report = improve_chip(chip_dir, target_score=60, max_iterations=20)
            final_score = report["final_score"]
            final_result = report.get("final_result", {})
            final_verdict = final_result.get("verdict", "unknown")
            fixes_count = len(report.get("fixes_applied", []))
            iterations = report.get("iterations", 0)
            print(f"\n  AFTER DOCTOR:")
            print(f"  Score: {final_score}/100 ({final_verdict})")
            print(f"  Iterations: {iterations}")
            print(f"  Fixes applied: {fixes_count}")
            print(f"  Score delta: +{final_score - scaffold_score}")

            results.append({
                "domain_id": brief["domain_id"],
                "category": brief["category"],
                "scaffold_score": scaffold_score,
                "final_score": final_score,
                "delta": final_score - scaffold_score,
                "scaffold_verdict": scaffold_verdict,
                "final_verdict": final_verdict,
                "fixes_applied": fixes_count,
            })

    # Summary
    print(f"\n{'=' * 70}")
    print("VALIDATION SUMMARY")
    print(f"{'=' * 70}")
    print(f"\n{'Chip':<30} {'Category':<12} {'Scaffold':>8} {'Doctor':>8} {'Delta':>6} {'Verdict':<15}")
    print("-" * 80)
    for r in results:
        print(f"{r['domain_id']:<30} {r['category']:<12} {r['scaffold_score']:>8} {r['final_score']:>8} {'+' + str(r['delta']):>6} {r['final_verdict']:<15}")

    # Assertions
    all_pass = True
    for r in results:
        if r["scaffold_score"] < 35:
            print(f"\nFAIL: {r['domain_id']} scaffold score {r['scaffold_score']} < 35")
            all_pass = False
        if r["final_score"] < r["scaffold_score"]:
            print(f"\nFAIL: {r['domain_id']} doctor made score worse")
            all_pass = False

    if all_pass:
        print(f"\nALL VALIDATIONS PASSED")
    else:
        print(f"\nSOME VALIDATIONS FAILED")
        sys.exit(1)


if __name__ == "__main__":
    run_validation()
