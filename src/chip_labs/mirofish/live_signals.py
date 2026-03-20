"""Convert live platform data into MiroFish signals.

Provides converter functions that accept raw data from X/Twitter MCP tools,
GitHub API responses, etc. The caller is responsible for fetching the data.

Does NOT call any external APIs. Zero external dependencies. Uses only stdlib.

Usage:
    # Caller fetches via MCP tools (outside MiroFish)
    tweets = mcp__x_twitter__search_twitter(query="MCP server", count=100)
    # Convert to MiroFish signals
    live_signals = signals_from_twitter_search(tweets, "mcp-server-builder")
    # Inject into simulation alongside static signals
    result = run_simulation(graph, domains, signals=static_signals + live_signals)
"""

from __future__ import annotations

import math
from typing import Any

from .signals import create_signal


def signals_from_twitter_search(
    search_results: list[dict[str, Any]],
    domain_id: str,
    domain_keywords: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Convert X/Twitter search results into MiroFish signals.

    Args:
        search_results: List of tweet dicts from search_twitter MCP tool.
            Expected fields: text, favorite_count, retweet_count, reply_count,
            user.followers_count
        domain_id: Domain to associate signals with.
        domain_keywords: Optional keywords to filter relevance.

    Returns:
        List of MiroFish signals with strength derived from engagement.
    """
    signals: list[dict[str, Any]] = []
    if not search_results:
        return signals

    total_likes = 0
    total_retweets = 0
    total_replies = 0
    tweet_count = 0
    max_follower_count = 0

    for tweet in search_results:
        total_likes += _safe_int(tweet, "favorite_count")
        total_retweets += _safe_int(tweet, "retweet_count")
        total_replies += _safe_int(tweet, "reply_count")
        tweet_count += 1
        user = tweet.get("user", {}) or {}
        followers = _safe_int(user, "followers_count")
        max_follower_count = max(max_follower_count, followers)

    if tweet_count == 0:
        return signals

    # Engagement signal: weighted combination
    engagement = total_likes + total_retweets * 2 + total_replies * 1.5
    strength = min(1.0, math.log1p(engagement) / math.log1p(100000))

    # Volume signal: raw tweet count
    volume_strength = min(1.0, math.log1p(tweet_count) / math.log1p(1000))

    # Influencer signal: largest account talking about it
    influencer_strength = min(1.0, math.log1p(max_follower_count) / math.log1p(1000000))

    if strength > 0.2:
        signals.append(create_signal(
            f"live-twitter-engagement-{domain_id}",
            "viral_tweet",
            [domain_id],
            strength=round(strength, 4),
            label=f"Live X engagement for {domain_id} ({tweet_count} tweets, {int(engagement)} engagement)",
        ))

    if volume_strength > 0.3:
        signals.append(create_signal(
            f"live-twitter-volume-{domain_id}",
            "community_request",
            [domain_id],
            strength=round(volume_strength, 4),
            label=f"Live X volume for {domain_id} ({tweet_count} tweets)",
        ))

    if influencer_strength > 0.4:
        signals.append(create_signal(
            f"live-twitter-influencer-{domain_id}",
            "viral_tweet",
            [domain_id],
            strength=round(influencer_strength, 4),
            label=f"Influencer discussing {domain_id} ({max_follower_count:,} followers)",
        ))

    return signals


def signals_from_twitter_trends(
    trends: list[dict[str, Any]],
    domain_mapping: dict[str, list[str]],
) -> list[dict[str, Any]]:
    """Convert X/Twitter trending topics into MiroFish signals.

    Args:
        trends: List of trend dicts from get_trends MCP tool.
            Expected fields: name, tweet_volume
        domain_mapping: Maps trend keywords to domain_ids.
            e.g., {"crypto": ["trading-crypto", "defi-architect"],
                   "AI agent": ["ai-agent-builder"]}

    Returns:
        List of MiroFish signals for matching trends.
    """
    signals: list[dict[str, Any]] = []
    for trend in trends:
        name = (trend.get("name", "") or "").lower()
        volume = _safe_int(trend, "tweet_volume")

        for keyword, domain_ids in domain_mapping.items():
            if keyword.lower() in name:
                strength = min(1.0, math.log1p(volume) / math.log1p(500000))
                if strength > 0.3:
                    signals.append(create_signal(
                        f"live-trend-{_slug(name)}",
                        "viral_tweet",
                        domain_ids,
                        strength=round(strength, 4),
                        label=f"Trending: {trend.get('name', '')} ({volume:,} tweets)",
                    ))
    return signals


def signals_from_user_mentions(
    mentions: list[dict[str, Any]],
    domain_id: str,
) -> list[dict[str, Any]]:
    """Convert user mentions into demand signals.

    Useful for tracking organic interest in a product/domain.

    Args:
        mentions: List of tweet/mention dicts.
        domain_id: Domain to associate signals with.

    Returns:
        List of community demand signals.
    """
    signals: list[dict[str, Any]] = []
    if not mentions:
        return signals

    total_engagement = sum(
        _safe_int(m, "favorite_count") + _safe_int(m, "retweet_count") * 2
        for m in mentions
    )
    mention_count = len(mentions)

    if mention_count >= 5:
        strength = min(1.0, math.log1p(total_engagement) / math.log1p(50000))
        signals.append(create_signal(
            f"live-mentions-{domain_id}",
            "community_request",
            [domain_id],
            strength=max(0.3, round(strength, 4)),
            label=f"Live mentions of {domain_id} ({mention_count} mentions, {total_engagement} engagement)",
        ))

    return signals


def aggregate_live_signals(
    domain_ids: list[str],
    twitter_data: dict[str, list[dict[str, Any]]] | None = None,
    trends_data: list[dict[str, Any]] | None = None,
    domain_keywords: dict[str, list[str]] | None = None,
) -> list[dict[str, Any]]:
    """Convenience function to aggregate all live signal sources.

    Args:
        domain_ids: Domains to generate signals for.
        twitter_data: Dict mapping domain_id to search results.
        trends_data: Trending topic data.
        domain_keywords: Maps trend keywords to domain_ids for trend matching.

    Returns:
        Combined list of all live signals.
    """
    all_signals: list[dict[str, Any]] = []

    if twitter_data:
        for domain_id, tweets in twitter_data.items():
            if domain_id in domain_ids:
                all_signals.extend(signals_from_twitter_search(tweets, domain_id))

    if trends_data and domain_keywords:
        all_signals.extend(signals_from_twitter_trends(trends_data, domain_keywords))

    return all_signals


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _safe_int(d: dict[str, Any], key: str) -> int:
    """Safely extract an integer from a dict, defaulting to 0."""
    val = d.get(key, 0)
    if val is None:
        return 0
    try:
        return int(val)
    except (ValueError, TypeError):
        return 0


def _slug(text: str) -> str:
    """Convert text to a simple slug for signal IDs."""
    return "".join(c if c.isalnum() else "-" for c in text[:30]).strip("-")
