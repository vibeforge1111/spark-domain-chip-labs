"""Tests for decision driver summary generation."""


from chip_labs.mirofish.report import generate_driver_summary, format_driver_summary


def _make_persona(ptype, domain_id, stage, values=None, fit=0.5, signal=0.3, threshold=0.4, matched=None):
    """Create a persona with pre-populated decision_log."""
    return {
        "persona_id": f"{ptype}-0",
        "persona_type": ptype,
        "adoption_state": {domain_id: stage},
        "decision_log": [
            {
                "domain_id": domain_id,
                "from_stage": "unaware",
                "to_stage": stage,
                "advanced": stage != "unaware",
                "effective_signal": signal,
                "threshold": threshold,
                "fit_score": fit,
                "matched_values": matched or [],
            },
        ],
        "values": values or [],
    }


class TestGenerateDriverSummary:
    def test_basic_summary(self):
        personas = [
            _make_persona("trader", "crypto", "adopted", fit=0.9, signal=0.8, matched=["speed", "alpha"]),
            _make_persona("creative", "crypto", "aware", fit=0.3, signal=0.1),
        ]
        result = generate_driver_summary(personas, "crypto")
        assert result["domain_id"] == "crypto"
        assert len(result["type_summaries"]) == 2

    def test_adoption_rate_correct(self):
        personas = [
            _make_persona("trader", "crypto", "adopted"),
            _make_persona("trader", "crypto", "adopted"),
            _make_persona("trader", "crypto", "aware"),
        ]
        # Give unique IDs
        for i, p in enumerate(personas):
            p["persona_id"] = f"trader-{i}"
        result = generate_driver_summary(personas, "crypto")
        trader_summary = next(s for s in result["type_summaries"] if s["persona_type"] == "trader")
        assert abs(trader_summary["adoption_rate"] - 0.6667) < 0.01

    def test_matched_values_aggregated(self):
        personas = [
            _make_persona("developer", "mcp", "adopted", matched=["code_quality", "dx"]),
            _make_persona("developer", "mcp", "adopted", matched=["code_quality", "productivity"]),
        ]
        for i, p in enumerate(personas):
            p["persona_id"] = f"dev-{i}"
        result = generate_driver_summary(personas, "mcp")
        dev = next(s for s in result["type_summaries"] if s["persona_type"] == "developer")
        assert "code_quality" in dev["top_matched_values"]

    def test_stalled_tracking(self):
        personas = [
            _make_persona("ai_newcomer", "complex", "evaluating"),
            _make_persona("ai_newcomer", "complex", "interested"),
        ]
        for i, p in enumerate(personas):
            p["persona_id"] = f"newcomer-{i}"
        result = generate_driver_summary(personas, "complex")
        newcomer = next(s for s in result["type_summaries"] if s["persona_type"] == "ai_newcomer")
        assert newcomer["adoption_rate"] == 0.0
        assert len(newcomer["stalled_at"]) > 0

    def test_empty_personas(self):
        result = generate_driver_summary([], "test")
        assert result["type_summaries"] == []

    def test_reason_generated(self):
        personas = [
            _make_persona("trader", "crypto", "adopted", fit=0.9, signal=0.8, threshold=0.3, matched=["speed"]),
        ]
        result = generate_driver_summary(personas, "crypto")
        trader = result["type_summaries"][0]
        assert "reason" in trader
        assert isinstance(trader["reason"], str)
        assert len(trader["reason"]) > 5

    def test_sorted_by_adoption(self):
        personas = [
            _make_persona("creative", "test", "aware", fit=0.3),
            _make_persona("trader", "test", "adopted", fit=0.9),
            _make_persona("developer", "test", "adopted", fit=0.7),
        ]
        result = generate_driver_summary(personas, "test")
        types = [s["persona_type"] for s in result["type_summaries"]]
        # Adopted types should come first
        trader_idx = types.index("trader")
        creative_idx = types.index("creative")
        assert trader_idx < creative_idx


class TestFormatDriverSummary:
    def test_format_produces_string(self):
        summary = {
            "domain_id": "trading-crypto",
            "type_summaries": [
                {
                    "persona_type": "trader",
                    "adoption_rate": 0.92,
                    "advocacy_rate": 0.3,
                    "count": 10,
                    "avg_fit_score": 0.85,
                    "top_matched_values": ["speed", "alpha"],
                    "signal_to_threshold": 2.1,
                    "stalled_at": {},
                    "reason": "Strong adoption: values [speed, alpha] matched, signal 2.1x threshold",
                },
            ],
        }
        output = format_driver_summary(summary)
        assert "trading-crypto" in output
        assert "trader" in output
        assert "92%" in output
        assert "speed" in output

    def test_format_empty_summary(self):
        summary = {"domain_id": "test", "type_summaries": []}
        output = format_driver_summary(summary)
        assert "test" in output
