# Tomorrow Focus: 2026-03-22

## Goal

Keep momentum without drifting into decorative work or another large refactor.

Tomorrow should focus on tasks that are:

1. small enough to finish in one session
2. directly tied to product behavior or portfolio clarity
3. still inside the current mutable-target rules

## What We Already Accomplished

### Chip Labs Own Repo

- Stabilized the current contract across runtime, CLI, v2, and v3.
- Cleared the repo-local serving gaps so:
  - `serve` works in the active workspace
  - `serve-intelligence` returns repo-local context
  - explicit `advise --domain chip-labs` consults only `domain-chip-labs`
  - unhinted repo-local `advise` falls back to the active workspace chip instead of returning empty
- Grounded `evaluate.py` in actual repo state instead of placeholder constants.
- Created real internal package seams for the four surfaces:
  - hooks
  - factory
  - transfer
  - intelligence serving
- Moved the main implementation files behind those seams while preserving compatibility aliases.
- Made the package-boundary decision explicit:
  - keep one repo/package for now
  - revisit a split only if later triggers are met
- Reached a defensible self-score checkpoint:
  - `score-v2 = 100/100`
  - `score-v3 = 87.0/100`
- Captured a current portfolio audit and a top-tier leadership deep dive.

### Startup YC

- Improved doctrine context selection so it is more task-aware and startup-aware.
- Added metadata-aware routing for pricing, sales, founder-fit, PMF, and pivot-style questions.
- Added a doctrine-backed fallback path so the advisor still produces structured output when the DSPy model is unavailable or weak.
- Improved memory retrieval so same-task startup history is preferred over generic conversational residue.
- Sharpened fallback synthesis so enterprise/pricing/process answers are less likely to anchor on the wrong broad doctrine.
- Tried an explicit multi-option idea-ranking system, then reverted it after deciding it may drift the product before the surrounding system is ready.

## Tomorrow: Tasks We Can Actually Finish

### 1. Tighten Multi-Chip Advisory Ranking In Chip Labs

Why this is worth doing:

- Repo-local serving is now healthy.
- The remaining serving weakness is broader cross-chip ranking quality.
- This is a product behavior issue, not another paperwork issue.

Concrete deliverable:

- Improve ranking in `src/chip_labs/intelligence_serving/chip_advisor.py` and, if needed, `src/chip_labs/intelligence_serving/chip_context_injector.py`.
- Capture before/after validation artifacts under `research/meta/`.

Definition of done:

- A small prompt set shows the right chips are being consulted for non-local, multi-chip questions.
- False matches caused by vague token overlap are reduced.

### 2. Convert The Top-Tier Audit Into A Weakest-Dimension Matrix

Why this is worth doing:

- We already know the top 6 leadership chips.
- The next useful view is not "which chip is best", but "which deep dimension is still weakest across the leaders".

Concrete deliverable:

- Produce one matrix artifact in `research/meta/` covering the top 6 chips across:
  - doctrine quality
  - contradiction rigor
  - realworld/evidence depth
- End each row with one concrete next action:
  - keep
  - strengthen
  - validate
  - stop overclaiming

Definition of done:

- We can see where the leadership tier is actually thin without rereading six repos from scratch.

### 3. Tighten Startup-YC Task Classification

Why this is worth doing:

- The idea-ranking experiment was reverted.
- The next non-drifting improvement is better routing, not a bigger feature.

Concrete deliverable:

- Improve `TaskTypeClassifier` in `domain-chip-startup-yc` so it better detects:
  - choose-between / versus prompts
  - pivot-versus-persist prompts
  - wedge-selection prompts
  - cofounder/team prompts
  - pricing/process/procurement prompts

Definition of done:

- Manual smoke prompts route to the intended task type more consistently.
- No new doctrine format or scoring surface is introduced.

### 4. Run One Focused Startup-YC Scenario Batch

Why this is worth doing:

- We need one small proof batch after the recent routing, fallback, and memory work.
- This keeps the work evidence-seeking instead of purely architectural.

Concrete deliverable:

- Run a short manual scenario batch across a small set of founder prompts:
  - pricing
  - procurement
  - PMF ambiguity
  - founder-fit
  - pivot timing
- Save the outputs as a lightweight validation note.

Definition of done:

- We can say whether startup-yc is visibly better on real founder-style prompts, not just structurally cleaner in code.

## Not Tomorrow

- Expanding `obsidian-vault/` for chip-labs watchtower depth.
  - That is outside the current mutable-target scope.
- Deep doctrine/evidence/contradiction rewrites in `startup-yc`.
  - Its current mutable targets do not include the doctrine/evidence surfaces that most affect deep scoring.
- Another package refactor in chip-labs.
  - The internal seam work is already in a good place; tomorrow's value is product behavior and audit clarity.

## Preferred Order

1. Chip-labs multi-chip advisory ranking
2. Top-tier weakest-dimension matrix
3. Startup-yc task classification
4. Startup-yc short scenario batch

## Exit Criteria For Tomorrow

- One real chip-labs serving improvement is shipped and validated.
- One portfolio-level audit artifact becomes more decision-useful.
- Startup-yc gets one smaller, safer intelligence improvement instead of another large conceptual feature.
- No scope expansion is needed to claim progress honestly.
