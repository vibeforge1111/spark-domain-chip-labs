// Reusable blind runner+judge evaluation harness for a creator-run benchmark.
// Copy into a Workflow() call and edit DATA. One runner agent scores each case
// (with or without the doctrine); a SEPARATE blind judge scores the runner's
// output against the frozen rubric + oracle. Judges never know which arm they grade.
//
// Why a workflow and not inline: parallel fan-out, structured output, and the
// runner/judge separation is what stops the doctrine author from grading their
// own homework. See SKILL.md Step 10 and loop-protocol.md.
//
// Embed the benchmark DATA inline (Workflow `args` delivery to scripts has been
// unreliable). Edit MODES per round: baseline (no doctrine) vs candidate (doctrine).

export const meta = {
  name: 'creator-run-eval',
  description: 'Blind runner+judge evaluation of a creator-run benchmark across modes',
  phases: [{ title: 'Run', detail: 'runners score cases' }, { title: 'Judge', detail: 'blind judges score outputs' }],
}

const DATA = {
  doctrinePath: 'ABSOLUTE/PATH/TO/domain-chip/doctrine.md',
  rubricPath: 'ABSOLUTE/PATH/TO/benchmark/scoring_rubric.md',
  // The capability framing the runner sees. Keep it task-specific.
  task: 'Score X (the unit) and return a verdict per the output contract.',
  // Verdict vocabulary + numeric ordinal for ranking/aggregation.
  ordinal: { kill: 0, fix: 1, ship: 2 },
  lanes: ['development', 'held_out', 'regression', 'adversarial'],
  modes: [{ mode: 'baseline', useDoctrine: false }, { mode: 'candidate', useDoctrine: true }],
  // cases: [{ id, lane, input, oracle: {...} }]; traps: [{ id, input, expected_rejection }]
  cases: [],
  traps: [],
}

const RUNNER = {
  type: 'object', required: ['verdict', 'factors', 'rewrite', 'reasoning'],
  properties: {
    verdict: { type: 'string' }, factors: { type: 'array', items: { type: 'string' } },
    rewrite: { type: 'string', description: 'concrete rewrite if verdict warrants one, else ""' },
    reasoning: { type: 'string' },
  },
}
const JUDGE = {
  type: 'object', required: ['scores', 'justification'],
  properties: {
    scores: { type: 'object', description: 'one 0/1/2 per rubric dimension' },
    justification: { type: 'string' },
  },
}

const items = [
  ...DATA.cases.map(c => ({ kind: 'case', ...c })),
  ...DATA.traps.map(t => ({ kind: 'trap', id: t.id, lane: 'adversarial', input: t.input, oracle: { expected_rejection: t.expected_rejection } })),
]

const runnerPrompt = (it, useDoctrine) =>
  (useDoctrine ? `FIRST read ${DATA.doctrinePath} and treat it as ground rules that OVERRIDE generic instinct.\n\n` : '') +
  `${DATA.task}\n\nUNIT TO SCORE:\n"${it.input}"\n\nReturn a verdict, decisive factors, one concrete rewrite if warranted (else ""), and brief reasoning. Be decisive: one verdict, no hedging.`

const judgePrompt = (it, out) =>
  `You are an impartial benchmark judge. FIRST read the rubric: ${DATA.rubricPath}. Apply its anchors EXACTLY (0/1/2 per dimension, never interpolate).\n\n` +
  `UNIT:\n"${it.input}"\n\n` +
  (it.kind === 'trap' ? `ADVERSARIAL TRAP. Oracle expected rejection: ${it.oracle.expected_rejection}\n\n` : `Oracle: ${JSON.stringify(it.oracle)}\n\n`) +
  `RUNNER OUTPUT TO JUDGE:\nverdict: ${out.verdict}\nfactors: ${JSON.stringify(out.factors)}\nrewrite: ${out.rewrite || '(none)'}\nreasoning: ${out.reasoning}\n\n` +
  `Score every rubric dimension and justify each in one line.`

async function evalArm(m) {
  const rows = await pipeline(
    items,
    it => agent(runnerPrompt(it, m.useDoctrine), { label: `run:${m.mode}:${it.id}`, phase: 'Run', schema: RUNNER }),
    (out, it) => out ? agent(judgePrompt(it, out), { label: `judge:${m.mode}:${it.id}`, phase: 'Judge', schema: JUDGE })
      .then(j => ({ id: it.id, lane: it.lane, kind: it.kind, runner: out, judge: j })) : null,
  )
  const scored = rows.filter(Boolean).map(r => {
    const vals = Object.values(r.judge.scores).filter(v => typeof v === 'number')
    return { ...r, score: vals.reduce((a, b) => a + b, 0) / (vals.length || 1) }
  })
  const laneMean = {}
  for (const lane of DATA.lanes) {
    const rs = scored.filter(r => r.lane === lane)
    laneMean[lane] = rs.length ? +(rs.reduce((s, r) => s + r.score, 0) / rs.length).toFixed(4) : null
  }
  return { mode: m.mode, lane_means: laneMean, per_case: scored.map(r => ({ id: r.id, lane: r.lane, score: +r.score.toFixed(4), verdict: r.runner.verdict })) }
}

const out = await parallel(DATA.modes.map(m => () => evalArm(m)))
const byMode = {}
out.filter(Boolean).forEach(r => { byMode[r.mode] = r })
return byMode
