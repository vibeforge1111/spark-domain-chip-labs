# Research Crosscheck

Date: 2026-05-09
Scope: Memory Doctor Brain design for Spark Telegram memory/context diagnostics

## Verified Sources Checked

- MemGPT paper: https://arxiv.org/abs/2310.08560
  - Verified mechanism: LLM agents benefit from hierarchical memory tiers and explicit data movement between fast/context memory and slower/external memory.
  - Spark mapping: Memory Doctor must inspect movement, not only final recalled facts.

- LangGraph memory docs: https://docs.langchain.com/oss/python/langgraph/add-memory
  - Verified mechanism: short-term thread memory and long-term cross-session memory are distinct surfaces.
  - Spark mapping: recent Telegram turn loss is a context/capsule problem even when durable current-state memory is healthy.

- OpenTelemetry trace docs: https://opentelemetry.io/docs/concepts/signals/traces/
  - Verified mechanism: traces assemble correlated spans/events across processes using shared context.
  - Spark mapping: gateway, Builder, provider capsule, memory reads/writes, and dashboard movement need correlated lineage.

- Zep graph docs: https://help.getzep.com/v2/understanding-the-graph
  - Verified mechanism: agent memory graphs separate raw episodes, entity nodes, and relationship/fact edges.
  - Spark mapping: doctor output should distinguish active current state, historical traces, episodes, and supporting graph/wiki facts.

- Graphiti docs: https://help.getzep.com/graphiti/getting-started/welcome
  - Verified mechanism: temporally aware knowledge graphs support incremental updates for evolving facts.
  - Spark mapping: future doctor improvements should evaluate temporal supersession, not just static retrieval.

- LongMemEval paper: https://arxiv.org/abs/2410.10813
  - Verified mechanism: long-term memory evaluation needs information extraction, multi-session reasoning, temporal reasoning, updates, and abstention.
  - Spark mapping: Memory Doctor Brain now lists these as eval capabilities and recommends probes by failure class.

- Convomem paper: https://arxiv.org/abs/2511.10523
  - Verified mechanism: conversational memory needs categories such as user facts, preferences, temporal changes, implicit connections, and abstention, and short histories can often benefit from fuller context before RAG.
  - Spark mapping: close-turn recall should be checked before blaming long-term memory retrieval.

## Borrowed

- Layered memory and movement visibility from MemGPT.
- Short-term vs long-term memory boundary from LangGraph.
- End-to-end correlated trace discipline from OpenTelemetry.
- Episode/entity/fact separation and temporal graph direction from Zep/Graphiti.
- Eval capability categories from LongMemEval and Convomem.

## Rejected

- No automatic repair yet. Diagnosis and improvement recommendation stay separate from write/delete authority.
- No blind graph/wiki authority. Wiki and sidecars remain supporting, not current truth for mutable user facts.
- No claim that benchmark success equals product memory success. Telegram close-turn UX remains its own probe lane.

## Improved Locally

- Memory Doctor now has a `brain` payload with weighted trace coverage, missing senses, proactive improvement candidates, LLM wiki packet visibility, LLM wiki health, SDK runtime, and dashboard movement export checks.
- Memory Doctor now records compact `memory_doctor_brain_evaluated` observability snapshots so coverage and gaps can become trendable without becoming memory truth.
- Telegram output now includes a compact brain line so the operator sees whether the doctor had enough senses to trust the diagnosis.
- Tests now cover the brain's degraded-visibility path and its connected SDK/wiki/movement/LLM-wiki path.
