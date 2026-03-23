# MiroFish Discovery Contract

## Purpose

This contract defines how open-ended discovery observations become canonical domain-chip candidates before they enter MiroFish evaluation.

The boundary is strict:

- discovery proposes
- canonicalization cleans
- evaluation scores
- humans review promotion

Raw discovery output is not allowed to score itself.

## What Counts As A Domain Chip

A candidate only qualifies as a valid domain-chip prospect if it can answer all three:

1. what repeated user job is being done
2. what repeated specialization surface the user wants to build
3. what repeated mastery surface the user wants to deepen

If one of those is missing, the candidate is either proto, workflow-only, persona-only, duplicate, or too vague.

## Required Candidate Fields

Every canonical discovery candidate should carry:

- `domain_id`
- `label`
- `description`
- `specialization_surface`
- `mastery_surface`
- `user_value_loop`
- `domain_tags`
- `evidence_sources`
- `evidence_summary`
- `adjacent_domains`
- `duplicate_aliases`
- `confidence_read`
- `promotion_status`
- `raw_observation`

## Classification Outcomes

Each raw candidate must map to exactly one class:

- `clear_domain_chip`
- `proto_domain_chip`
- `workflow_not_domain`
- `persona_only_not_domain`
- `duplicate_of_existing`
- `too_vague_to_keep`

## Classification Heuristics

### `clear_domain_chip`

Use when the candidate has:

- a stable label and description
- a real specialization surface
- a real mastery surface
- a repeated user value loop
- some evidence summary

### `proto_domain_chip`

Use when the candidate has domain shape but still lacks one of:

- complete specialization definition
- complete mastery definition
- strong enough evidence

### `workflow_not_domain`

Use when the candidate describes:

- a one-off task
- a generic workflow
- a feature cluster
- activity without a stable specialization/mastery loop

### `persona_only_not_domain`

Use when the candidate mostly describes:

- a user type
- an audience segment
- an identity claim

without a repeated operating domain.

### `duplicate_of_existing`

Use when:

- the canonical `domain_id` already exists in the known universe
- the batch contains the same domain more than once under aliases

### `too_vague_to_keep`

Use when the candidate lacks enough naming or description detail to define a real domain.

## Canonicalization Rules

### Naming

- derive `domain_id` from a lowercase slug of `label` if one is not supplied
- keep labels human-readable
- treat alias-only variations as duplicates, not new candidates

### List Fields

These fields must always normalize to deduped string lists:

- `domain_tags`
- `evidence_sources`
- `adjacent_domains`
- `duplicate_aliases`

### Confidence

`confidence_read` should stay qualitative during discovery:

- `low`
- `medium`
- `high`

### Promotion Status

Discovery-stage candidates should default to:

- `candidate`

Later human review may change that to:

- `watchlist`
- `evaluate_next`
- `needs_more_evidence`
- `rejected`

## Batch Packet Shape

Raw intake packets should use:

```json
{
  "batch_id": "mirofish-discovery-batch-001",
  "existing_domain_ids": ["known-domain-a", "known-domain-b"],
  "raw_candidates": [
    {
      "label": "AI Meeting Prep Copilot",
      "description": "Helps operators prepare for recurring customer and investor meetings.",
      "specialization_surface": "pre-meeting research and brief generation",
      "mastery_surface": "turning recurring meeting prep into a repeatable operating advantage",
      "user_value_loop": "collect context, draft brief, improve after each meeting",
      "domain_tags": ["meetings", "operator-tools"],
      "evidence_sources": ["community", "github"],
      "evidence_summary": "Repeated operator pain around recurring prep work.",
      "adjacent_domains": ["sales-copilot"],
      "duplicate_aliases": [],
      "confidence_read": "medium",
      "promotion_status": "candidate",
      "raw_observation": "Operators want a repeated prep workflow, not just note-taking."
    }
  ]
}
```

Canonicalized output packets should emit:

- `accepted_candidates`
- `merged_candidates`
- `rejected_candidates`
- `summary`
- `next_actions`

## Operator Workflow

1. collect raw discovery observations without seeding the benchmark universe
2. canonicalize the batch into accepted, merged, and rejected candidates
3. inspect the reasons for every rejection and merge
4. only pass accepted candidates into the hybrid evaluation harness
5. review promotion after the evaluation report exists

## Current CLI Path

The repo-local canonicalization command is:

```powershell
$env:PYTHONPATH='src'
python -m chip_labs.cli mirofish-discovery-batch --input research/meta/MIROFISH_DISCOVERY_BATCH_TEMPLATE_2026-03-24.json --output research/meta/MIROFISH_DISCOVERY_BATCH_TEMPLATE_RESULT_2026-03-24.json
```

## Governance

- all discovery packets remain `exploratory_frontier`
- no discovered candidate auto-enters the maintained benchmark universe
- duplicates and vague concepts must remain visible in the packet, not silently dropped
