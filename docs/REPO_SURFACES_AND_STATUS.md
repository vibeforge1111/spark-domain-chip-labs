# Repo Surfaces And Status

This repo contains four overlapping surfaces. The code has already grown into all four, but the documentation previously treated them too loosely.

## 1. Meta-Chip Hooks

Scope:
- `evaluate`
- `suggest`
- `packets`
- `watchtower`

What it is:
- The lab as a Spark-compatible chip that can be run by `spark-researcher`

Current status:
- Shipped
- Contract-aligned with the current `spark-chip.v1` manifest shape
- Backed by v2 and v3 self-scoring plus targeted tests

What users get:
- A bounded lab chip that can score portfolio health, suggest research directions, emit packets, and render observability surfaces

## 2. Chip Factory

Scope:
- scaffolding
- gap analysis
- loop control
- creation helpers

What it is:
- Internal productization of chip creation and repair workflows

Current status:
- Working
- Strong structurally
- Still documented mainly as lab infrastructure rather than a separately positioned product

What users get:
- Faster chip creation, repeatable templates, clearer failure analysis, and less manual setup drift

## 3. Transfer And Recursive Improvement

Scope:
- transfer patterns
- bounded self-edit support
- doctrine promotion
- recursive improvement governance

What it is:
- The layer that tries to turn single-chip wins into portfolio-level methodology

Current status:
- Guarded beta
- The rules and evidence lanes are strong
- The remaining gap is repeated, real multi-chip transfer success, not more prose

What users get:
- Better odds that one chip's proven pattern becomes reusable infrastructure instead of isolated craft knowledge

## 4. Intelligence Serving

Scope:
- runtime execution
- hook delivery
- MCP server
- advisory/intelligence serving paths

What it is:
- The layer that makes chip intelligence available to agents and surrounding systems

Current status:
- Integrated
- Operationally useful
- Still under-defined as a standalone surface compared with the meta-chip itself

What users get:
- A practical way to serve chip intelligence into agent workflows without manually wiring every research artifact

## Shipped Vs Experimental Vs Aspirational

Shipped:
- Current manifest/runtime/rubric contract
- Meta-chip hook surface
- Core scoring, packeting, suggestion, and runtime paths

Experimental:
- Transfer-derived methodology promotion at larger portfolio scale
- Richer intelligence serving expectations beyond current runtime and MCP integrations
- Deeper self-improvement flywheel claims that depend on longer run history

Aspirational:
- A clean package boundary between lab chip, chip factory, and serving layer
- Strong watchtower depth inside the sanctioned mutable surface
- A finished portfolio flywheel where repeated transfer wins and long-run empirical history compound into durable moats

## Decision Rule

When changing this repo, first decide which surface the change belongs to. A patch is lower risk when it improves one surface without accidentally changing the product claim of another.

The migration baseline for future package separation lives in `docs/PACKAGE_BOUNDARY_MIGRATION_PLAN.md`.
