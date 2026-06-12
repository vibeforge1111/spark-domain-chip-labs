# Memory Doctor Telegram Doctrine

Memory Doctor is a diagnostic specialization, not a repair agent. It should make memory failures easier to understand without turning historical traces into something that can silently rewrite active truth.

## Operating Principles

- Active current-state memory outranks historical trace mentions.
- A topic appearing in trace logs is evidence, not automatically a bug.
- Multi-delete user intent must preserve one requested deletion per matched fact.
- Telegram replies must be short enough to act on, while JSON and CLI output can carry the full report.
- Repair commands require a separate authority gate before they can mutate memory.

## Failure Modes

- Instruction forgetting captures a memory-forget request and deletes unrelated saved instructions.
- A multi-delete turn only writes the first deletion.
- Historical test residue such as "Maya" is treated as the user's active name.
- The context capsule drops the immediately previous user correction.
- A dashboard count says memory is healthy while per-request lineage shows a partial write.

## Claim Boundary

This prototype proves local diagnosis and Telegram routing. It does not claim autonomous memory repair, full context-capsule recovery, or network-safe Swarm publication.
