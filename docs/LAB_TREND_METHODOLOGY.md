# Lab Trend Methodology

> How the Frontier Scout discovers domain opportunities.

---

## Purpose

The Frontier Scout workstream is responsible for identifying new domains that would benefit from a Spark chip. This document defines the scoring framework, source channels, and validation methodology used to evaluate domain opportunities.

The goal is not to chase hype. The goal is to identify domains where a structured chip would provide sustained value.

---

## Scoring Framework

Every domain opportunity is scored across 6 dimensions, each weighted by its importance to the chip ecosystem.

### Dimension Weights

| Dimension | Weight | What It Measures |
|-----------|--------|------------------|
| Market Size | 0.20 | How large is the addressable market for this domain? |
| Data Availability | 0.15 | Can we access quality training/evaluation data? |
| Benchmark Feasibility | 0.20 | Can we build meaningful quantitative benchmarks? |
| Community Demand | 0.20 | Are practitioners actively asking for help in this domain? |
| Spark Ecosystem Fit | 0.15 | Does this domain complement existing chips? |
| Monetization Potential | 0.10 | Can this chip contribute to ecosystem sustainability? |

**Total weight: 1.00**

### Dimension Scoring (0-10 scale)

#### Market Size (weight: 0.20)

| Score | Description |
|-------|-------------|
| 9-10 | Massive market: millions of practitioners, major industry vertical |
| 7-8 | Large market: hundreds of thousands of active practitioners |
| 5-6 | Medium market: tens of thousands, established but niche |
| 3-4 | Small market: thousands, specialized domain |
| 1-2 | Tiny market: hundreds, highly specialized |

#### Data Availability (weight: 0.15)

| Score | Description |
|-------|-------------|
| 9-10 | Abundant open data: public datasets, APIs, documentation, research papers |
| 7-8 | Good data: multiple sources available, some curation needed |
| 5-6 | Moderate data: sources exist but require significant curation |
| 3-4 | Limited data: few sources, proprietary, or hard to access |
| 1-2 | Scarce data: almost no public sources, domain knowledge is tacit |

#### Benchmark Feasibility (weight: 0.20)

| Score | Description |
|-------|-------------|
| 9-10 | Clear metrics: established evaluation criteria, quantitative baselines exist |
| 7-8 | Feasible metrics: can define metrics with moderate effort |
| 5-6 | Possible metrics: metrics definable but baselines require original research |
| 3-4 | Difficult metrics: domain is subjective, hard to quantify |
| 1-2 | No clear metrics: domain resists quantitative evaluation |

#### Community Demand (weight: 0.20)

| Score | Description |
|-------|-------------|
| 9-10 | Vocal demand: active communities, frequent requests, pain points widely discussed |
| 7-8 | Strong demand: regular discussion, identifiable pain points |
| 5-6 | Moderate demand: some discussion, niche communities |
| 3-4 | Low demand: occasional mentions, no organized community |
| 1-2 | No demand: domain is not discussed in AI/tooling context |

#### Spark Ecosystem Fit (weight: 0.15)

| Score | Description |
|-------|-------------|
| 9-10 | Perfect fit: fills a clear portfolio gap, complements 3+ existing chips |
| 7-8 | Good fit: fills a gap, complements 1-2 existing chips |
| 5-6 | Moderate fit: no overlap but also no strong synergy |
| 3-4 | Weak fit: partial overlap with existing chips |
| 1-2 | Poor fit: significant overlap or conflicts with existing portfolio |

#### Monetization Potential (weight: 0.10)

| Score | Description |
|-------|-------------|
| 9-10 | High value: practitioners will pay for quality tooling in this domain |
| 7-8 | Good value: willingness to pay for premium features |
| 5-6 | Moderate value: free tier viable, some premium potential |
| 3-4 | Low value: practitioners expect free tooling |
| 1-2 | No value: domain is too small or too price-sensitive |

---

## Composite Score Calculation

```
composite_score = sum(dimension_score * dimension_weight for each dimension)
```

**Example:**

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| Market Size | 7 | 0.20 | 1.40 |
| Data Availability | 8 | 0.15 | 1.20 |
| Benchmark Feasibility | 6 | 0.20 | 1.20 |
| Community Demand | 9 | 0.20 | 1.80 |
| Spark Ecosystem Fit | 7 | 0.15 | 1.05 |
| Monetization Potential | 5 | 0.10 | 0.50 |
| **Composite** | | | **7.15** |

### Score Thresholds

| Composite Score | Action |
|----------------|--------|
| >= 7.0 | **Strong candidate.** Proceed to domain brief. |
| 5.0 - 6.9 | **Watch list.** Monitor for signal strengthening. |
| < 5.0 | **Pass.** Not a current priority. |

---

## Source Channels

### Primary Sources

| Source | What to Look For | Scan Frequency |
|--------|-----------------|----------------|
| **GitHub Trending** | Repositories gaining stars rapidly in new domains; tool categories with no chip coverage | Daily |
| **Product Hunt** | New product categories; tools that solve domain-specific problems; user pain points in comments | Daily |
| **X/Twitter** | Practitioner complaints; "I wish I had..." posts; domain-specific communities; influential builders | Continuous |
| **arxiv** | New evaluation methodologies; domain benchmark papers; survey papers that map a field | Weekly |
| **VC Landscape** | Investment themes; Y Combinator batch trends; emerging verticals | Monthly |

### Source-Specific Guidance

**GitHub Trending:**
- Focus on the "trending" tab, not just popular repos
- Look for new tool categories (e.g., "AI code review" before it was mainstream)
- Track programming language trends as proxy for domain growth
- Ignore: one-time viral repos, meme projects, tutorial repos

**Product Hunt:**
- Focus on product categories, not individual products
- Look for clusters: 3+ products in the same space within a month
- Read user comments for unmet needs
- Ignore: consumer apps, hardware, lifestyle products

**X/Twitter:**
- Follow domain-specific communities and hashtags
- Look for recurring pain points (same complaint from multiple people)
- Track what influential builders are working on
- Ignore: promotional content, engagement farming, single-person complaints

**arxiv:**
- Focus on survey papers (they map entire fields)
- Look for new benchmark papers (they indicate maturing domains)
- Track evaluation methodology papers (they inform chip design)
- Ignore: incremental model improvements, domain-irrelevant theory

**VC Landscape:**
- Track investment themes, not individual companies
- Look for emerging verticals with 5+ funded companies
- Note which domains are attracting first-time funding
- Ignore: late-stage funding, acqui-hires, fund-of-funds

---

## Validation: The 2-Week Rule

> Sustained signal over 2+ weeks beats one-time hype.

### Why 2 Weeks

- **Day 1 signals** are often hype, viral moments, or marketing pushes
- **Week 1** distinguishes genuine interest from noise
- **Week 2** confirms sustained demand vs. fading curiosity
- **Beyond 2 weeks** indicates a domain worth investing in

### Validation Protocol

```
Day 0:   Signal detected (score opportunity)
         |
Day 1-3: Initial assessment (is this a real signal?)
         |
Day 7:   First validation checkpoint
         - Is the signal still present?
         - Has it strengthened or weakened?
         - Are new sources confirming it?
         |
Day 14:  Second validation checkpoint
         - Sustained or fading?
         - Multiple independent sources?
         - Community engagement growing?
         |
         +-- Sustained --> Domain Brief
         +-- Fading -----> Watch List (check again in 30 days)
         +-- Dead -------> Archive
```

### Hype Indicators (Negative Signals)

| Indicator | What It Looks Like |
|-----------|-------------------|
| Single-source signal | Only one blog post, one tweet, one product launch |
| Influencer-driven only | Signal comes from promotion, not organic discussion |
| No practitioner complaints | Nobody is asking for help -- they are just talking about it |
| No code/tools | Discussion is theoretical, no actual implementations |
| Conflicts with existing chips | Domain significantly overlaps with current portfolio |

### Sustained Demand Indicators (Positive Signals)

| Indicator | What It Looks Like |
|-----------|-------------------|
| Multi-source confirmation | GitHub, X, Product Hunt, and arxiv all show activity |
| Practitioner pain points | Real people describing real problems they face |
| Tool proliferation | Multiple independent tools being built for the domain |
| Community formation | Dedicated forums, Discord servers, X communities |
| Recurring over time | Signal persists and grows over weeks, not days |

---

## Domain Brief Output

When a domain passes validation, the Frontier Scout produces a domain brief:

```yaml
domain_brief:
  id: "brief-2024-001"
  domain: "string"
  composite_score: 7.15
  dimension_scores:
    market_size: 7
    data_availability: 8
    benchmark_feasibility: 6
    community_demand: 9
    spark_ecosystem_fit: 7
    monetization_potential: 5
  sources_consulted:
    - { type: "github", url: "...", signal: "..." }
    - { type: "twitter", url: "...", signal: "..." }
  validation:
    first_detected: "2024-01-01"
    first_checkpoint: "2024-01-07"
    second_checkpoint: "2024-01-14"
    status: "sustained"
  recommended_action: "proceed_to_architecture"
  evidence_lane: "exploratory_frontier"
  created_at: "2024-01-15T10:00:00Z"
```

The domain brief is the input to the Chip Architect workstream.
