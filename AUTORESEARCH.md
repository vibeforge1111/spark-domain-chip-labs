---
schema_version: 1
repo: vibeforge1111/spark-domain-chip-labs
name: Spark Domain Chip Labs
domain: chip-research
area: meta-research-and-chip-rd
objective: Improve domain chip creation methodology, discover high-value new domains, manage portfolio quality, and research recursive self-improvement through domain specialization.
metric_name: lab_research_quality_score
metric_direction: higher
default_branch: main
mutable_targets:
  - src/chip_labs
  - docs
  - research
  - README.md
capsule_dir: .autoresearch/capsules
adoption_policy: review
absorb_merge_policy: human_review
run_command: spark-researcher loop --command research
publish_command: spark-researcher collective publish
platforms:
  - Windows
  - Python
safety_boundaries:
  - Do not auto-graduate chips without human review
  - Do not modify spark-researcher core without explicit approval
  - Do not modify other chip repos without their owner's consent
  - Keep lab research artifacts visible and inspectable
  - All methodology changes must be benchmark-tested before promotion
  - Never suppress contradictions -- they must stay visible in the observatory
---

# Spark Domain Chip Labs

## Agent

- **name**: spark-domain-chip-labs
- **model**: one-agent-per-workspace

## Repo

- **name**: spark-domain-chip-labs
- **role**: attached-specialization

## Specialization

- **key**: chip-research
- **label**: Domain Chip Labs
- **memory_policy**: selective
- **evolution_mode**: review_required
- **compatibility_mode**: allow_list
- **compatible_keys**:
  - generalist
  - startup
  - trading
  - content
  - marketing
  - web-design
  - roblox
  - pokemon
  - xcontent
  - vibe-incubator
  - predictive-worlds

## Runtime

- **core**: spark-researcher
- **specialization**: chip-research
- **chip**: domain-chip-labs

## Intent

> The Spark Domain Chip Labs is the recursive improvement engine for the Spark chip ecosystem.
> It discovers new domains, improves chip-building methodology, manages portfolio quality,
> and researches how domain specialization contributes to collective intelligence and
> recursive self-improvement.
