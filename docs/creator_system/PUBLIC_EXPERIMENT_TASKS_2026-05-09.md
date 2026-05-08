# Creator System Public Experiment Tasks - 2026-05-09

## Goal

Let people create local domain chips, benchmarks, specialization paths, and
autoloops without needing to understand internal Spark architecture.

The public path should feel like:

> Tell Spark what specialist you want. Spark creates the local standards,
> benchmark, loop policy, and review packet. Nothing becomes official until it
> passes gates and a human approves it.

## Phase 1 - Public-Safe Local Use

- Keep `spark-domain-chip-labs` public as the standards and template repo.
- Keep generated user work private by default.
- Keep all network contribution language as "review packet", not "published".
- Make `USER_QUICKSTART_BETA.md` the primary human entrypoint.
- Make `CREATOR_SYSTEM_USER_AND_AGENT_ONBOARDING.md` the primary agent entrypoint.

Done when:

- fresh clone install works
- template check passes
- beta check passes
- README explains the public/private boundary

## Phase 2 - Telegram Natural-Language Creator Flow

Primary user phrases:

- "create a QA Operator specialization path"
- "make a benchmarked autoloop for AI security questionnaires"
- "prepare Crypto Trading for review in Spark Swarm"
- "show what still blocks sharing this path"

Telegram should hide internal command complexity and reply with:

- what is being created
- whether it is private or review-ready
- the one next action
- Workspace/Canvas link only when useful

Do not show long replay commands unless the user asks for technical details.

## Phase 3 - Spark Swarm Workspace Connection

For each created path, Workspace should show:

- local/private status
- official network status, if any
- benchmark score
- latest run verdict
- review blockers
- evidence count and strongest evidence tier

Telegram should stay compact. Workspace should carry the extra detail.

## Phase 4 - First Real Public Demo Lane

Use Spark QA Operator as the first strong demo because it helps Spark improve
itself and validates the whole product loop.

Required artifacts:

- domain chip or path manifest
- benchmark pack with real product QA cases
- autoloop policy with bounded mutation surface
- Spark Swarm collective payload
- Telegram report fixtures
- review packet that remains private until approved

Current gap:

- the QA Operator benchmark is connected, but it is still a smoke benchmark.
  Build the richer product QA suite before making strong specialization claims.

## Phase 5 - Network Contribution

Only allow contribution when:

- benchmark proof exists
- private evidence has been stripped or intentionally packaged
- review blockers are clear
- rollback notes exist
- a human/operator approves the packet

Until then, generated systems are useful local work, not official Spark Swarm
network doctrine.
