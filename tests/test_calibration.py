"""Tests for mirofish calibration and outcome contracts."""


from chip_labs.mirofish.calibration import (
    create_outcome_contract,
    resolve_contract,
    brier_score,
    aggregate_brier,
    replay_calibration,
    calibration_report,
    REPLAY_CASES,
)


class TestBrierScore:
    def test_perfect_prediction_true(self):
        assert brier_score(1.0, 1.0) == 0.0

    def test_perfect_prediction_false(self):
        assert brier_score(0.0, 0.0) == 0.0

    def test_worst_prediction(self):
        assert brier_score(0.0, 1.0) == 1.0
        assert brier_score(1.0, 0.0) == 1.0

    def test_random_prediction(self):
        score = brier_score(0.5, 1.0)
        assert score == 0.25

    def test_bounded(self):
        for p in [0.0, 0.1, 0.3, 0.5, 0.7, 0.9, 1.0]:
            for a in [0.0, 1.0]:
                assert 0.0 <= brier_score(p, a) <= 1.0


class TestOutcomeContracts:
    def test_create_contract(self):
        contract = create_outcome_contract(
            question="Will defi-architect be built?",
            domain_id="defi-architect",
            predicted_probability=0.85,
        )
        assert contract["question"] == "Will defi-architect be built?"
        assert contract["predicted_probability"] == 0.85
        assert contract["status"] == "open"
        assert contract["actual_outcome"] is None

    def test_resolve_contract_true(self):
        contract = create_outcome_contract(
            question="Test?", domain_id="test",
            predicted_probability=0.8,
        )
        resolved = resolve_contract(contract, True)
        assert resolved["status"] == "resolved"
        assert resolved["actual_outcome"] is True
        assert "brier_score" in resolved
        assert resolved["brier_score"] == brier_score(0.8, 1.0)

    def test_resolve_contract_false(self):
        contract = create_outcome_contract(
            question="Test?", domain_id="test",
            predicted_probability=0.8,
        )
        resolved = resolve_contract(contract, False)
        assert resolved["brier_score"] == brier_score(0.8, 0.0)


class TestAggregateBrier:
    def test_no_contracts(self):
        assert aggregate_brier([]) == 1.0

    def test_perfect_contracts(self):
        contracts = [
            {"status": "resolved", "brier_score": 0.0},
            {"status": "resolved", "brier_score": 0.0},
        ]
        assert aggregate_brier(contracts) == 0.0

    def test_filters_unresolved(self):
        contracts = [
            {"status": "resolved", "brier_score": 0.1},
            {"status": "open", "brier_score": None},
        ]
        assert aggregate_brier(contracts) == 0.1


class TestReplayCalibration:
    def test_replay_returns_results(self):
        result = replay_calibration()
        assert "cases" in result
        assert "aggregate_brier" in result
        assert result["case_count"] == len(REPLAY_CASES)

    def test_brier_scores_bounded(self):
        result = replay_calibration()
        for case in result["cases"]:
            assert 0.0 <= case["brier_score"] <= 1.0

    def test_aggregate_reasonable(self):
        result = replay_calibration()
        # Our hand-picked predictions should beat random
        assert result["aggregate_brier"] < 0.5

    def test_baselines_computed(self):
        result = replay_calibration()
        assert "baselines" in result
        assert "constant_50" in result["baselines"]
        assert "frequency_predictor" in result["baselines"]
        assert "base_rate" in result["baselines"]

    def test_better_than_constant(self):
        result = replay_calibration()
        # Our predictions should beat always-50%
        assert result["better_than_constant"] is True

    def test_replay_cases_have_outcomes(self):
        for case in REPLAY_CASES:
            assert "actual_outcome" in case
            assert isinstance(case["actual_outcome"], bool)


class TestCalibrationReport:
    def test_report_structure(self):
        predictions = {"defi-architect": 0.85, "indie-hacker": 0.60}
        report = calibration_report(predictions)
        assert "prediction_contracts" in report
        assert report["contract_count"] == 2
        assert "historical_calibration" in report
        assert report["evidence_lane"] == "exploratory_frontier"
