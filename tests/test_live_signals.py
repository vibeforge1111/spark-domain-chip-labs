"""Tests for live signal ingestion from X/Twitter and other platforms."""


from chip_labs.mirofish.live_signals import (
    signals_from_twitter_search,
    signals_from_twitter_trends,
    signals_from_user_mentions,
    aggregate_live_signals,
    _safe_int,
)


class TestSignalsFromTwitterSearch:
    def test_high_engagement_creates_signal(self):
        tweets = [
            {"text": "MCP servers are amazing", "favorite_count": 5000,
             "retweet_count": 2000, "reply_count": 500,
             "user": {"followers_count": 100000}},
        ]
        signals = signals_from_twitter_search(tweets, "mcp-server-builder")
        assert len(signals) >= 1
        # Should create engagement signal
        engagement_signals = [s for s in signals if "engagement" in s["signal_id"]]
        assert len(engagement_signals) == 1
        assert engagement_signals[0]["strength"] > 0.3

    def test_low_engagement_no_signal(self):
        tweets = [
            {"text": "test", "favorite_count": 1, "retweet_count": 0,
             "reply_count": 0, "user": {"followers_count": 10}},
        ]
        signals = signals_from_twitter_search(tweets, "test")
        # Low engagement should produce few or no signals
        engagement_signals = [s for s in signals if "engagement" in s["signal_id"]]
        assert len(engagement_signals) == 0

    def test_empty_results(self):
        signals = signals_from_twitter_search([], "test")
        assert signals == []

    def test_influencer_signal(self):
        tweets = [
            {"text": "Big announcement", "favorite_count": 100,
             "retweet_count": 50, "reply_count": 20,
             "user": {"followers_count": 500000}},
        ]
        signals = signals_from_twitter_search(tweets, "test")
        influencer_signals = [s for s in signals if "influencer" in s["signal_id"]]
        assert len(influencer_signals) == 1

    def test_volume_signal(self):
        tweets = [{"text": f"tweet {i}", "favorite_count": 10,
                    "retweet_count": 5, "reply_count": 2,
                    "user": {"followers_count": 100}}
                   for i in range(50)]
        signals = signals_from_twitter_search(tweets, "test")
        volume_signals = [s for s in signals if "volume" in s["signal_id"]]
        assert len(volume_signals) == 1

    def test_signal_strength_bounded(self):
        tweets = [
            {"text": "mega viral", "favorite_count": 1000000,
             "retweet_count": 500000, "reply_count": 200000,
             "user": {"followers_count": 50000000}},
        ]
        signals = signals_from_twitter_search(tweets, "test")
        for s in signals:
            assert 0.0 <= s["strength"] <= 1.0

    def test_handles_missing_fields(self):
        tweets = [{"text": "sparse tweet"}]
        signals = signals_from_twitter_search(tweets, "test")
        # Should not crash, just produce no signals
        assert isinstance(signals, list)


class TestSignalsFromTwitterTrends:
    def test_matching_trend(self):
        trends = [
            {"name": "#CryptoTrading", "tweet_volume": 50000},
        ]
        mapping = {"crypto": ["trading-crypto"]}
        signals = signals_from_twitter_trends(trends, mapping)
        assert len(signals) == 1
        assert "trading-crypto" in signals[0]["affects_domains"]

    def test_no_matching_trend(self):
        trends = [
            {"name": "#Cooking", "tweet_volume": 50000},
        ]
        mapping = {"crypto": ["trading-crypto"]}
        signals = signals_from_twitter_trends(trends, mapping)
        assert len(signals) == 0

    def test_low_volume_filtered(self):
        trends = [
            {"name": "#CryptoTrading", "tweet_volume": 10},
        ]
        mapping = {"crypto": ["trading-crypto"]}
        signals = signals_from_twitter_trends(trends, mapping)
        assert len(signals) == 0

    def test_empty_trends(self):
        signals = signals_from_twitter_trends([], {})
        assert signals == []


class TestSignalsFromUserMentions:
    def test_sufficient_mentions(self):
        mentions = [
            {"favorite_count": 100, "retweet_count": 50}
            for _ in range(10)
        ]
        signals = signals_from_user_mentions(mentions, "test-domain")
        assert len(signals) == 1
        assert signals[0]["signal_type"] == "community_request"

    def test_too_few_mentions(self):
        mentions = [{"favorite_count": 10, "retweet_count": 5}]
        signals = signals_from_user_mentions(mentions, "test")
        assert len(signals) == 0

    def test_empty_mentions(self):
        signals = signals_from_user_mentions([], "test")
        assert signals == []


class TestAggregation:
    def test_aggregate_combines_sources(self):
        twitter_data = {
            "domain-a": [
                {"text": "test", "favorite_count": 5000, "retweet_count": 2000,
                 "reply_count": 500, "user": {"followers_count": 100000}},
            ],
        }
        trends = [{"name": "#DomainB", "tweet_volume": 50000}]
        keywords = {"domainb": ["domain-b"]}

        signals = aggregate_live_signals(
            ["domain-a", "domain-b"],
            twitter_data=twitter_data,
            trends_data=trends,
            domain_keywords=keywords,
        )
        assert len(signals) >= 2  # At least one from search + one from trends

    def test_aggregate_empty(self):
        signals = aggregate_live_signals(["test"])
        assert signals == []


class TestSafeInt:
    def test_normal_int(self):
        assert _safe_int({"x": 42}, "x") == 42

    def test_none_value(self):
        assert _safe_int({"x": None}, "x") == 0

    def test_missing_key(self):
        assert _safe_int({}, "x") == 0

    def test_string_number(self):
        assert _safe_int({"x": "42"}, "x") == 42
