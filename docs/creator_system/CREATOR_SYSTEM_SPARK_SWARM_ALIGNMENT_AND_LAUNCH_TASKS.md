# Creator System Spark Swarm Alignment And Launch Tasks

This task system connects the creator-system beta to the current Spark Swarm
workspace/network design so creator runs can be used safely in Spark Swarm
without collapsing private workspace learning into public network absorption.

## Sources Reviewed

Spark Swarm local docs:

- `C:\Users\USER\Desktop\spark-swarm\README.md`
- `C:\Users\USER\Desktop\spark-swarm\docs\SPARK_SWARM_WORKSPACE_VS_NETWORK_CONTRIBUTION.md`
- `C:\Users\USER\Desktop\spark-swarm\docs\SPARK_SWARM_INSIGHT_PUBLICATION_SECURITY_OVERVIEW.md`
- `C:\Users\USER\Desktop\spark-swarm\docs\SPARK_SWARM_SHARED_INSIGHT_PUBLISHING_STANDARD.md`
- `C:\Users\USER\Desktop\spark-swarm\docs\SPARK_SWARM_SPECIALIZATION_PATH_AUTHORING_GUIDE.md`
- `C:\Users\USER\Desktop\spark-swarm\docs\SPARK_SWARM_RUNTIME_COLLECTIVE_PAYLOAD_SPEC.md`
- `C:\Users\USER\Desktop\spark-swarm\docs\SPARK_SWARM_STARTUP_YC_ABSORPTION_BENCHMARK_STANDARD.md`
- `C:\Users\USER\Desktop\spark-swarm\packages\contracts\src\index.ts`
- `C:\Users\USER\Desktop\spark-researcher\README.md`
- `C:\Users\USER\Desktop\spark-researcher\docs\ARCHITECTURE.md`
- `C:\Users\USER\Desktop\spark-researcher\docs\MEMORY.md`

External security and launch references:

- OWASP Top 10 for LLM Applications and GenAI Security Project:
  `https://owasp.org/www-project-top-10-for-large-language-model-applications/`
- NIST AI Risk Management Framework and Generative AI Profile:
  `https://www.nist.gov/itl/ai-risk-management-framework`
- GitHub App installation-token scoping:
  `https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/authenticating-as-a-github-app-installation`
- GitHub Actions secure use:
  `https://docs.github.com/actions/learn-github-actions/security-hardening-for-github-actions`
- OpenSSF Scorecard:
  `https://scorecard.dev/`

## Alignment Verdict

The creator system is ready for Spark Swarm's private workspace lane and local
review-bundle lane. It is not ready for Spark Swarm network absorption.

The right launch path is:

```text
creator run
  -> private workspace evidence
  -> workspace_validated local review bundle
  -> network proposal bundle
  -> verified-repo GitHub PR proof
  -> schema, replay, security, privacy, rollback, and publication review
  -> reviewed_candidate
  -> network_absorbable only after explicit approval
```

This preserves Spark Swarm's design: private workspaces learn fast, while the
shared network learns carefully.

## Product Intent Standard

Every creator-system integration with Spark Swarm must preserve these intents:

| Intent | Creator-System Interpretation | Spark Swarm Interpretation |
| --- | --- | --- |
| Fast private learning | Users can generate domain chips, benchmarks, specialization paths, autoloop policies, and local packets in a repo. | Workspace lane accepts private or workspace-scoped sync without turning it into network trust. |
| Public sharing with consent | A review bundle can be proposed, but not published automatically. | Network contribution requires deliberate proposal, verified repo proof, and review gates. |
| Privacy by default | Creator artifacts keep `network_publication_allowed=false` unless a future promotion bundle explicitly changes it. | Private sync remains workspace-scoped unless proposed for network absorption. |
| Trust by evidence | Claims are capped by smoke, doctor, recompute, release-gate, and production-readiness evidence. | Shared surfaces trust artifact references, replay commands, PR proof, signatures, and required checks. |
| Reusable intelligence | Domain chips and specialization paths are reusable when their contracts and benchmarks are explicit. | Collective records are thin summaries plus artifact references, not raw workspace dumps. |
| User experience | Users see next actions, blocked reasons, and safe claims. | Web surfaces show workspace status, Collective evidence, review state, and publication blockers. |

## Current Contract Mapping

| Creator-System Artifact | Spark Swarm Target | Lane | Rule |
| --- | --- | --- | --- |
| `creator-intent.json` | `artifactRefs` plus workspace-private intent summary | Workspace | Never publish raw private goals without redaction and proposal review. |
| `adapter-map.json` | workspace/source binding metadata | Workspace | Must not grant product runtime or global tool authority. |
| `created-artifact-manifest.json` | artifact reference set | Workspace / proposal | Include paths and hashes; avoid full artifact blobs in hot sync payloads. |
| `domain-chip/` | optional domain chip / doctrine source | Proposal | Network use requires explicit absorption scope and rollback. |
| `benchmark/` | benchmark adapter or scenario-pack evidence | Workspace / proposal | Benchmark changes need stricter review than status pulses. |
| `specialization-path/` | `specialization-path-*` compatible repo or path template | Workspace / proposal | Must fit Spark Swarm's registry and runtime-context contract. |
| `autoloop/policy.json` | evolution-path and mutation-governance reference | Workspace | No mutation widening without declared targets and review. |
| `reports/*` | `outcomes`, evidence strength, replay refs | Workspace / proposal | Reports are source evidence, not publication approval. |
| `reports/creator-mission-status.json` | read-only status projection | Workspace | Product surfaces consume status; they do not invent verdicts. |
| `swarm/contribution_packet.json` | network proposal source material | Proposal | It remains local until transformed into a Spark Swarm network proposal bundle. |
| `swarm-review-bundle.json` | review-bundle attachment or PR artifact | Proposal | Must keep `network_absorbable=false` and `network_publication_allowed=false`. |

## Security And Privacy Design Rules

1. Workspace sync is private by default.
2. Network proposal is a separate action, not a side effect of sync.
3. Heavy artifacts stay in repos or CI artifacts; Spark Swarm receives thin
   summaries and artifact references.
4. Creator-system packets must classify each artifact as private, workspace
   validated, proposal-ready, or forbidden for sharing.
5. Any prompt fragment, executable instruction, benchmark rule, memory pack, or
   doctrine packet requires stricter review than a read-only status pulse.
6. Verified-repo GitHub PR proof is required before network-visible publication.
7. Publication proof must include required checks, base branch, head SHA, merge
   commit, and content continuity.
8. Secrets, private keys, tokens, emails, phone numbers, internal URLs, and raw
   private workspace paths must be blocked or redacted before network proposal.
9. Domain chips must not own identity, channel auth, provider secrets, product
   runtime controls, or global tool authority.
10. No creator-system gate may infer `network_absorbable=true` from
    `ready_for_swarm_packet`, generated matrix artifacts, or private workspace
    sync.

## Launch Task System

| ID | Task | Owner Repo | Output | Acceptance Gate |
| --- | --- | --- | --- | --- |
| CSS-01 | Define creator-to-Swarm lane taxonomy. | `spark-domain-chip-labs` | Creator doc/schema language mapping `local_only`, `candidate_review`, and `transfer_supported` to Spark Swarm `private_draft`, `workspace_validated`, `pr_submitted`, `reviewed_candidate`, and blocked `network_absorbable`. | Docs test proves both lane systems and forbidden upgrades are visible. |
| CSS-02 | Add a network proposal bundle contract. | `spark-domain-chip-labs` first, then `spark-swarm` | `creator-network-proposal-bundle.schema.json` or equivalent. | Schema requires provenance, replay commands, privacy review, rollback review, publication approval placeholder, and `network_absorbable=false` until approval. |
| CSS-03 | Build a dry-run collective payload mapper. | `spark-domain-chip-labs` | CLI dry-run that maps a creator run to Spark Swarm `SparkResearcherCollectiveSyncPayload`-shaped JSON without syncing. | Output has `workspaceId`, `agentId`, `runtimeSource`, `specialization`, `runtimePulse`, `insights`, `masteries`, `outcomes`, and `artifactRefs`; it contains no secrets and no network approval. |
| CSS-04 | Add privacy classification to bundle paths. | `spark-domain-chip-labs` | Review-bundle fields for `share_class`, redaction status, and allowed lane. | Review bundle blocks network proposal when private or unredacted artifacts are required. |
| CSS-05 | Align specialization-path output with Spark Swarm authoring guide. | `spark-domain-chip-labs` and future `specialization-path-*` repos | Creator-generated specialization-path manifest shape compatible with Spark Swarm registry/runtime context. | A generated path can be translated into a Spark Swarm authoring checklist without path-specific hosted logic. |
| CSS-06 | Create Spark Swarm network proposal templates. | `spark-swarm` | Verified-repo PR artifact template for creator-system proposals. | Template includes schema, secret scan, policy check, replay command, and signed publication manifest compatibility. |
| CSS-07 | Add proposal-status UX copy. | `spark-swarm` | Workspace and Collective copy that separates private sync, proposal review, reviewed candidate, and network absorption. | Users can see why something is private, reviewable, blocked, or absorbable without reading raw JSON. |
| CSS-08 | Connect Startup YC absorption evidence. | `spark-domain-chip-labs`, `spark-swarm`, Startup YC path repos | Absorption report references mapped into creator-run evidence and Spark Swarm Collective cards. | Reuse score and fresh-agent improvement are visible; mastery language is blocked without reuse evidence. |
| CSS-09 | Make privacy, rollback, and publication reviews executable. | `spark-domain-chip-labs` | CLI validator for promotion review packets. | Missing privacy review, rollback review, or publication approval blocks network proposal. |
| CSS-10 | Add cross-repo launch rehearsal. | Both repos | Manual runbook: creator run -> dry-run payload -> private workspace sync -> network proposal PR -> blocked/approved status. | Rehearsal records pass/fail/blocked state, no automatic publish, and no private data leakage. |
| CSS-11 | Add supply-chain and CI hardening checks. | Both repos | Scorecard/secret/dependency/action-pin review tasks. | Launch checklist includes least-privilege GitHub tokens, pinned/allowed actions, secret scanning, and dependency audit posture. |
| CSS-12 | Define scalability guardrails. | Both repos | Payload-size, artifact-reference, pagination, and snapshot rules. | Hot Spark Swarm routes consume thin summaries and artifact refs; no full creator-run tree is fetched for normal Collective reads. |

## First Implementation Order

The phase-by-phase execution board lives in
`CREATOR_SYSTEM_SPARK_SWARM_PHASED_BUILD_PLAN.md`.

1. Add the creator-to-Swarm lane taxonomy and proposal bundle schema.
2. Build dry-run payload mapping locally in `spark-domain-chip-labs`.
3. Add privacy classification and redaction gates to review bundles.
4. Mirror the accepted bundle shape into Spark Swarm as a network proposal
   template.
5. Run a cross-repo launch rehearsal with Startup YC as the first proof domain.
6. Only then discuss changing any gate toward `network_absorbable=true`.

## Stop-Ship Gates

Do not launch creator-system reuse into Spark Swarm network surfaces if any of
these are true:

- private workspace artifacts can become network-visible without proposal
  review
- a synced private payload can set `network_absorbable=true`
- generated matrix JSON is treated as publication approval
- raw workspace paths, secrets, emails, phone numbers, private keys, or internal
  URLs can enter shared copy
- benchmark or doctrine changes skip GitHub PR proof
- Spark Swarm hot routes need to fetch full creator-run trees
- a domain chip owns identity, channel auth, provider secrets, or global tool
  authority
- product surfaces can mutate creator artifacts before read-only status is
  stable

## Launch Readiness Definition

The creator system is Spark Swarm launch-ready when:

- private workspace sync can consume a creator-run payload dry-run without
  publication authority
- network proposal bundles are schema-valid, replayable, and privacy-classified
- verified-repo PR proof is the only path to network-visible sharing
- Spark Swarm UI can explain private, workspace-validated, proposal, reviewed,
  blocked, and network-absorbable states
- Startup YC proves the full path from creator run to workspace evidence to
  reviewed network proposal
- production-readiness remains `100` for local/repo creator-system use while
  network absorption stays blocked until the proposal review actually passes
