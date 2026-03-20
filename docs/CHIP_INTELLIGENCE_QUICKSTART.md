# Chip Intelligence Delivery System -- Quick Start Guide

## What It Does

Domain chips grow intelligence through autoloop flywheels (doctrines, evidence, contradictions). This system **delivers** that intelligence to AI agents in real time and **captures feedback** so chips get smarter from real usage.

---

## 1. Automatic (Claude Code Hooks -- already wired)

The hooks are configured in `~/.claude/settings.json`. Every Claude Code session now automatically:

- **SessionStart**: Injects chip doctrines + guardrails into the session
- **PreToolUse**: Advises before Bash/Edit/Write based on chip doctrines
- **PostToolUse**: Captures Bash/Edit/Write outcomes as evidence back into chips

**To test**: Start a new Claude Code session anywhere. The first call takes ~25s (builds cache), then all subsequent calls are instant (<0.1s).

**To focus on a specific domain**:
```bash
# Set domain hint before starting Claude Code
set CHIP_DOMAIN_HINT=startup
claude
```

**To disable temporarily**:
```bash
set CHIP_HOOKS_DISABLED=1
claude
```

---

## 2. CLI Commands

### Serve Intelligence

Inject chip context for a task description:

```bash
chip-labs serve-intelligence "evaluate a startup with strong distribution"
```

With options:
```bash
chip-labs serve-intelligence "evaluate founder velocity" --style detailed --max-chips 1
chip-labs serve-intelligence "plan marketing campaign" --style guardrails_only --max-chips 3
```

Styles: `concise` (default), `detailed` (full mechanisms/boundaries), `guardrails_only` (MUST/SHOULD/WATCH/UNCERTAIN)

### Get Advisory

Check a planned action against chip doctrines:

```bash
chip-labs advise "deploy new scoring model to production"
chip-labs advise "evaluate startup with weak retention" --domain startup
```

Output includes verdict (proceed/caution/reconsider), relevant guidance, contradictions, and uncertainty areas.

### Score a Chip

```bash
chip-labs score-v3 C:\Users\USER\Desktop\domain-chip-startup-yc --verbose
```

### Build Skill Artifacts

```bash
chip-labs build-skill C:\Users\USER\Desktop\domain-chip-startup-yc
```

### Start MCP Server

Expose chip intelligence as MCP tools for any Claude Code agent:

```bash
chip-labs run-mcp-server
```

This starts a JSON-RPC 2.0 server on stdio with 7 tools: `chip_query`, `chip_advise`, `chip_evaluate`, `chip_doctrines`, `chip_portfolio`, `chip_feedback`, `chip_suggest`.

---

## 3. Python API

### Load a chip and read its intelligence

```python
from chip_labs.chip_runtime import load_chip
from pathlib import Path

chip = load_chip(Path(r"C:\Users\USER\Desktop\domain-chip-startup-yc"))
print(chip.chip_name)        # domain-chip-startup-yc
print(chip.quality_score)    # 68.0
print(chip.quality_verdict)  # beta

intel = chip.intelligence
print(len(intel.doctrines))  # 47
for d in intel.doctrines[:3]:
    print(f"  [{d['confidence']}] {d['claim']}")
```

### Get advisory before an action

```python
from chip_labs.chip_advisor import AdvisoryRequest, advise_pre_action

request = AdvisoryRequest(
    action_description="Score a startup with high distribution but weak retention",
    domain_hint="startup",
)
response = advise_pre_action(request)

print(response.verdict)           # proceed / caution / reconsider
print(response.chips_consulted)   # ['domain-chip-startup-yc', ...]
for g in response.guidance[:3]:
    print(f"  [{g.confidence}] {g.claim}")
```

### Inject context into an LLM prompt

```python
from chip_labs.chip_context_injector import inject_context_for_task

# Concise mode (top 5 doctrines per chip)
context = inject_context_for_task("evaluate a YC application", style="concise")

# Guardrails mode (MUST/SHOULD/WATCH constraints)
guardrails = inject_context_for_task("build a trading bot", style="guardrails_only")

# Detailed mode (full mechanisms, boundaries, sources)
detailed = inject_context_for_task("plan startup launch", style="detailed", max_chips=1)
```

### Feed outcomes back (close the loop)

```python
from chip_labs.chip_advisor import AdvisoryRequest, advise_post_action

request = AdvisoryRequest(action_description="Evaluated startup distribution model")
outcome = {"success": True, "score": 0.78, "verdict": "strong-potential"}

result = advise_post_action(request, outcome)
print(result["feedback_written"])  # True
print(result["chip_name"])         # domain-chip-startup-yc
# -> writes to research/realworld_validated/ in the chip directory
```

---

## 4. MCP Server (for any Claude agent)

Add to your `.claude/settings.local.json` or project `.mcp.json`:

```json
{
  "mcpServers": {
    "chip-intelligence": {
      "command": "python",
      "args": ["-m", "chip_labs.chip_mcp_server"]
    }
  }
}
```

This gives any Claude agent access to 7 tools:

| Tool | What it does |
|------|-------------|
| `chip_query` | Search chip doctrines by topic |
| `chip_advise` | Pre-action advisory against doctrines |
| `chip_evaluate` | Run chip's scoring model |
| `chip_doctrines` | List doctrines sorted by confidence |
| `chip_portfolio` | Portfolio overview with quality scores |
| `chip_feedback` | Feed outcomes back into a chip |
| `chip_suggest` | Get research suggestions from gaps |

---

## How the Feedback Loop Works

```
1. Agent starts session
   -> SessionStart hook injects chip doctrines

2. Agent plans an action (Bash/Edit/Write)
   -> PreToolUse hook advises against doctrines

3. Agent executes, gets result
   -> PostToolUse hook writes feedback to research/realworld_validated/

4. Next autoloop flywheel run picks up new evidence
   -> Doctrines get re-evaluated with real-world data
   -> Score trajectory updates

5. Next agent session gets BETTER doctrines
   -> The chip learned from real usage
```

This is what makes domain chips different from static skills: they improve every time an agent uses them.

---

## Quality Gates

| Score | Verdict | Behavior |
|-------|---------|----------|
| < 35 | scaffold | Not served to agents |
| 35-59 | alpha | Served with "[alpha - moderate reliability]" warning |
| 60-79 | beta | Served normally with confidence levels |
| >= 80 | production_ready | Served as authoritative |

---

## Cache

Portfolio cache lives at `~/.cache/chip-labs/portfolio_cache.json` (10-minute TTL).

To force a refresh:
```bash
del %USERPROFILE%\.cache\chip-labs\portfolio_cache.json
```

---

## File Locations

| File | Purpose |
|------|---------|
| `~/.claude/settings.json` | Hook configuration |
| `~/.cache/chip-labs/portfolio_cache.json` | Portfolio cache (auto-created) |
| `src/chip_labs/hooks.py` | Hook handlers |
| `src/chip_labs/chip_runtime.py` | Chip loading + execution |
| `src/chip_labs/chip_advisor.py` | Advisory middleware |
| `src/chip_labs/chip_context_injector.py` | LLM prompt injection |
| `src/chip_labs/chip_mcp_server.py` | MCP server (7 tools) |
| `docs/EVALUATION_METHODOLOGY.md` | V1/V2/V3 scoring methodology |
