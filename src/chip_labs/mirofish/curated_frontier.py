"""Curated frontier source packets for MiroFish selection."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


_BANNED_SUFFIXES = ("-copilot", "-engine", "-loop", "-lab", "-os")


def _parse_ideas(block: str) -> list[dict[str, str]]:
    ideas: list[dict[str, str]] = []
    for raw_line in block.strip().splitlines():
        line = raw_line.strip()
        if not line:
            continue
        slug, label, observation = [part.strip() for part in line.split("|", 2)]
        ideas.append({"slug": slug, "label": label, "observation": observation})
    return ideas


_CURATED_CLUSTER_SPECS: list[dict[str, Any]] = [
    {
        "cluster_id": "creator-growth-systems",
        "label": "Creator Growth Systems",
        "seed_domains": ["tiktok-creator", "xcontent", "youtube-remixer"],
        "tags": ["viral", "creator", "attention"],
        "evidence_sources": ["x_twitter", "community", "producthunt"],
        "audience": "creators, operators, and growth-minded media teams",
        "loop_template": "capture signals around {focus}, choose the best move, publish, and reuse what converts",
        "ideas": _parse_ideas("""
hook-angle-testing|Hook Angle Testing|Creators keep rerunning the same post with sharper openings because the first sentence still decides distribution.
thumbnail-thesis-board|Thumbnail Thesis Board|Video creators want a way to test visual promises before wasting a full upload on the wrong package.
comment-funnel-builder|Comment Funnel Builder|Top creators increasingly treat comment sections like distribution channels, not just audience residue.
clip-ladder-planner|Clip Ladder Planner|Short-form teams want one system that turns one long recording into a ladder of clips with escalating hooks.
series-payoff-calendar|Series Payoff Calendar|Audience retention rises when creators can stage an arc instead of posting disconnected one-offs.
trend-response-studio|Trend Response Studio|Fast creators need a place to react to trends before they cool without losing their own voice.
creator-collab-matchmaking|Creator Collab Matchmaking|Crossovers work when audiences overlap in tone and payoff, not just when follower counts match.
audience-heatmap-review|Audience Heatmap Review|Creators obsess over where people drop, replay, or screenshot because that reveals what actually landed.
content-remix-planner|Content Remix Planner|The best creators squeeze multiple formats out of one idea and want a cleaner way to design those branches.
newsletter-to-shorts-bridge|Newsletter to Shorts Bridge|Writers moving into video want their best ideas translated into short-form without feeling like recycled spam.
format-portfolio-manager|Format Portfolio Manager|Creators are managing multiple repeatable formats at once and need to know which ones deserve another episode.
hook-swap-library|Hook Swap Library|High-performing teams reuse proven opening structures across topics but need cleaner retrieval than random notes.
fan-reply-amplifier|Fan Reply Amplifier|The most useful audience replies often become the next post or the next product insight.
creative-burnout-radar|Creative Burnout Radar|Solo creators can feel when content gets stale before analytics make it obvious.
distribution-lane-scheduler|Distribution Lane Scheduler|A lot of creator growth comes from posting the right asset in the right lane, not just making more assets.
launch-teaser-sequencer|Launch Teaser Sequencer|Product launches work better when creators drip anticipation instead of dropping everything in one post.
viral-analogy-finder|Viral Analogy Finder|A sharp analogy often turns a niche point into something broadly shareable.
camera-script-draftboard|Camera Script Draftboard|Many creator scripts die because spoken delivery needs tighter phrasing than written drafts.
fan-community-promptbook|Fan Community Promptbook|Community-led creators benefit from recurring prompts that get fans to submit usable stories and clips.
creator-pricing-page-doctor|Creator Pricing Page Doctor|Monetizing creators still struggle to explain sponsorships, memberships, and offers without killing trust.
title-rewrite-bench|Title Rewrite Bench|Titles are getting iterated like ad copy, but creators need a faster way to compare them against channel context.
retention-rebound-planner|Retention Rebound Planner|When a format slips, creators want to recover it before the algorithm learns the wrong lesson.
quote-card-extractor|Quote Card Extractor|Good soundbites should not require manual fishing after every podcast or interview.
creator-offer-funnel-map|Creator Offer Funnel Map|Growth creators increasingly need one view of how content ladders into newsletter, membership, course, or product.
comment-voice-calibrator|Comment Voice Calibrator|Reply tone matters because creators are performing brand identity in public every day.
micro-series-generator|Micro Series Generator|A recurring micro-series often outperforms disconnected posts because audiences know what to expect next.
audience-lore-builder|Audience Lore Builder|Strong communities form around inside jokes, references, and shared mythology that need active shaping.
creator-case-study-studio|Creator Case Study Studio|Breakdown-style content works because creators can prove taste and competence at the same time.
guest-appearance-router|Guest Appearance Router|Creators want better ways to find the right show, stream, or podcast appearance for a given thesis.
community-reward-designer|Community Reward Designer|Audience contribution improves when rewards feel identity-driven rather than generic.
hook-fatigue-detector|Hook Fatigue Detector|The same opening formula can stop working once the audience sees it too many times.
creator-brand-gap-audit|Creator Brand Gap Audit|The biggest mismatch is often between the creator's actual strengths and what the profile currently signals.
platform-risk-dash|Platform Risk Dash|Creators want an early warning system when one platform starts dominating too much of their reach.
evergreen-recut-planner|Evergreen Recut Planner|Old hits often deserve a new cut when the framing can be updated for the current moment.
audience-question-bank|Audience Question Bank|The best future content inputs are often buried in audience questions that never got organized.
creator-proofwall|Creator Proofwall|Social proof converts better when creators can show outcomes, receipts, and transformations without looking desperate.
postmortem-reel-builder|Postmortem Reel Builder|Transparent postmortems consistently get attention because they mix vulnerability with usable tactics.
creator-challenge-launcher|Creator Challenge Launcher|Challenges can create compounding participation loops when the structure is simple and status-bearing.
commentary-angle-mixer|Commentary Angle Mixer|Reaction and commentary creators win when they can quickly choose the sharpest angle on a live topic.
format-sunset-manager|Format Sunset Manager|A mature creator stack needs a way to retire stale formats without confusing the audience.
creator-asset-vault|Creator Asset Vault|Visuals, hooks, stories, and receipts become more valuable when creators can reuse them across formats.
story-beat-checker|Story Beat Checker|Narrative pacing is a hidden growth lever for educational and commentary creators.
audience-segment-broadcaster|Audience Segment Broadcaster|Different audience slices respond to different framings of the same core idea.
creator-partnership-ranker|Creator Partnership Ranker|Brand and collaborator fit matters more than raw size once a creator has some leverage.
distribution-gap-finder|Distribution Gap Finder|Many creators are underposting to high-fit channels simply because nobody mapped the gap.
creator-funnel-qa|Creator Funnel QA|Audience attention leaks happen at profile, link, landing, and offer layers all at once.
community-revival-kit|Community Revival Kit|Dormant communities can wake back up if the creator restarts the right rituals.
audience-proof-clusterer|Audience Proof Clusterer|Testimonials and replies become more useful when grouped by promise, identity, and outcome.
monetization-window-planner|Monetization Window Planner|Creators need to know when audience trust is high enough to make an offer without overcooking it.
creator-pivot-simulator|Creator Pivot Simulator|A big content pivot is scary because creators rarely see how it will affect existing audience trust.
"""),
    },
    {
        "cluster_id": "gaming-npc-community",
        "label": "Gaming / NPC / Community Worlds",
        "seed_domains": ["ai-npc-dialog", "discord-community", "streamer-overlay-ai"],
        "tags": ["viral", "gaming", "community"],
        "evidence_sources": ["x_twitter", "community", "github"],
        "audience": "game builders, moderators, streamers, and community operators",
        "loop_template": "track {focus}, update the world state, trigger the next interaction, and keep the community engaged",
        "ideas": _parse_ideas("""
npc-memory-rail|NPC Memory Rail|Players care when an NPC remembers earlier behavior instead of resetting every interaction.
quest-branch-editor|Quest Branch Editor|Game teams want to design branching outcomes without turning every quest into spreadsheet hell.
guild-ritual-scheduler|Guild Ritual Scheduler|Online communities stay alive when there are recurring rituals instead of random bursts of activity.
patch-notes-translator|Patch Notes Translator|Most players do not read patch notes until someone explains what actually matters.
raid-prep-draftboard|Raid Prep Draftboard|Coordinated groups need cleaner prep flow than scattered Discord messages before a raid night.
clan-identity-kit|Clan Identity Kit|A lot of community retention comes from identity markers, rituals, and inside language.
stream-hype-conductor|Stream Hype Conductor|Livestream energy is easier to sustain when planned beats and interaction prompts exist ahead of time.
drop-economy-watcher|Drop Economy Watcher|Loot or drop systems create chaos when nobody can tell what is scarce, inflated, or worth chasing.
lore-drop-calendar|Lore Drop Calendar|Story-driven worlds perform better when lore releases follow a rhythm instead of random dumps.
ugc-event-builder|UGC Event Builder|Community-made content grows when events are structured tightly enough to invite participation.
npc-voice-consistency-check|NPC Voice Consistency Check|Immersion breaks fast when the same character sounds different scene to scene.
server-culture-radar|Server Culture Radar|Large Discord or game servers drift into cliques unless someone can see the culture changing early.
roleplay-scene-planner|Roleplay Scene Planner|Roleplay communities want scene prompts, continuity, and stakes without heavy moderator overhead.
quest-reward-balancer|Quest Reward Balancer|Players feel manipulation quickly when quest rewards do not match the time or emotional stakes.
moderator-escalation-map|Moderator Escalation Map|Community mods need clearer escalation paths before conflict turns public and ugly.
boss-strategy-memory|Boss Strategy Memory|Guilds repeat the same mistakes because lessons from earlier attempts are not packaged well.
fandom-theory-board|Fandom Theory Board|Theorycraft and speculation are part of the fun when they can be organized into live threads.
npc-relationship-meter|NPC Relationship Meter|Players like feeling that their social choices reshape a world, not just a single dialogue box.
community-migration-guide|Community Migration Guide|When players move from one platform to another, most communities lose energy in the handoff.
player-story-hub|Player Story Hub|The best community content is often player-created stories that deserve better surfacing.
esports-watchparty-kit|Esports Watchparty Kit|Watch parties work when organizers can structure predictions, reactions, and recap moments.
world-state-broadcast|World State Broadcast|Live worlds feel real when players can see what changed between sessions.
questline-reentry-guide|Questline Reentry Guide|Players returning after a break need a concise way back into the story.
voice-chat-chemistry-map|Voice Chat Chemistry Map|Group play quality changes a lot depending on which personalities are placed together.
community-joke-archivist|Community Joke Archivist|Inside jokes are part of community glue, but they disappear if nobody curates them.
guild-recruitment-lens|Guild Recruitment Lens|Guild recruitment fails when the pitch sounds generic instead of matching actual culture.
meta-shift-briefing|Meta Shift Briefing|Players want faster understanding of what changed after a balance update or new strategy wave.
streamer-lobby-director|Streamer Lobby Director|Large creator lobbies need structure to keep chaos entertaining instead of dead air.
npc-rumor-network|NPC Rumor Network|Rumor systems make a world feel alive when information spreads unevenly and reactively.
faction-choice-advisor|Faction Choice Advisor|Players hesitate on faction or class picks when long-term tradeoffs stay opaque.
community-bounty-board|Community Bounty Board|Communities get more active when contribution asks are visible, lightweight, and rewarding.
spectator-moment-clipper|Spectator Moment Clipper|Esports and streams create highlight moments that disappear if nobody cuts them fast.
quest-salvage-tool|Quest Salvage Tool|A half-broken questline can often be rescued with a better recap and next-step framing.
guild-conflict-mediator|Guild Conflict Mediator|Guild drama is usually predictable before it becomes a full split.
fan-art-prompt-orbit|Fan Art Prompt Orbit|Creative fandoms grow when there is a constant stream of strong prompts and themes.
matchmaking-lobby-balancer|Matchmaking Lobby Balancer|Unbalanced lobbies kill fun even when the core game is good.
community-leveling-ladder|Community Leveling Ladder|People contribute more when there is a visible path from newcomer to trusted regular.
npc-backstory-weaver|NPC Backstory Weaver|Richer backstories help game characters feel designed instead of generated.
challenge-run-crafter|Challenge Run Crafter|Challenge formats work when they are legible, hard enough, and shareable.
server-event-aftercare|Server Event Aftercare|Communities retain more energy when someone packages the aftermath of a big event.
lore-contradiction-scanner|Lore Contradiction Scanner|Large worldbuilding projects regularly ship contradictions by accident.
raid-debrief-summarizer|Raid Debrief Summarizer|Teams improve faster when lessons from a hard session become a usable memo the same night.
character-build-bench|Character Build Bench|Players love experimenting with builds but hate scattered notes and outdated advice.
game-night-orchestrator|Game Night Orchestrator|Community play nights are stronger when matchups, prompts, and pacing are planned.
ugc-reward-market|UGC Reward Market|Creators contribute more worldbuilding when recognition and rewards are consistent.
discord-entry-funnel|Discord Entry Funnel|New members bounce when onboarding is messy or overcomplicated.
npc-emotion-director|NPC Emotion Director|Emotionally consistent characters make even simple dialogue feel more memorable.
spectator-quest-overlay|Spectator Quest Overlay|Viewers engage more when streams give them a participatory layer instead of passive watching.
fandom-recap-reporter|Fandom Recap Reporter|Busy fans need a clean way to catch up on what happened in the world and the community.
world-event-simulator|World Event Simulator|Live-ops teams want to preview how a big event could ripple through the community before launch.
"""),
    },
    {
        "cluster_id": "agentic-builders",
        "label": "AI Agent Builders",
        "seed_domains": ["ai-agent-builder", "mcp-server-builder", "cursor-copilot"],
        "tags": ["builders", "agents", "developer"],
        "evidence_sources": ["github", "x_twitter", "community"],
        "audience": "AI builders, infra teams, and agent operators",
        "loop_template": "define {focus}, run the agent, inspect failure modes, and harden the next iteration",
        "ideas": _parse_ideas("""
spec-breaker-workbench|Spec Breaker Workbench|Builders want a better way to break vague product specs into executable agent tasks without manual babysitting.
agent-handoff-tracer|Agent Handoff Tracer|Multi-agent systems fail quietly at the handoff layer, not just inside single prompts.
tool-permission-guard|Tool Permission Guard|Agent builders need a cleaner safety boundary around what tools can be called and when.
mcp-surface-mapper|MCP Surface Mapper|Developers need an easy way to see which MCP surfaces are missing, overlapping, or weakly documented.
agent-failure-replay|Agent Failure Replay|The fastest debugging path is replaying the exact failure path instead of guessing from logs.
plan-diff-inspector|Plan Diff Inspector|When agents revise a plan, teams need to see what changed and why.
prompt-contract-tester|Prompt Contract Tester|Prompt changes keep breaking implicit assumptions because very few teams test them like interfaces.
workflow-sandbox-runner|Workflow Sandbox Runner|Agent workflows need a safe local loop before they touch real tools or real customer state.
context-budget-auditor|Context Budget Auditor|A lot of agent weirdness is just bad context packing masquerading as intelligence.
agent-evals-router|Agent Evals Router|Builders want a direct path from observed failure to the exact eval or benchmark it should live in.
retrieval-grounding-check|Retrieval Grounding Check|Bad retrieval still poisons output even when the agent policy looks good on paper.
agent-state-timeline|Agent State Timeline|Time-based inspection makes it easier to see where an agent lost the plot.
tool-schema-linter|Tool Schema Linter|Poor schema design is still one of the biggest hidden sources of agent execution failure.
delegation-depth-meter|Delegation Depth Meter|Over-delegation creates thrash while under-delegation wastes agent leverage.
plan-to-run-bridge|Plan to Run Bridge|Teams want plans to convert into executable runs without a second manual rewrite.
agent-memory-auditor|Agent Memory Auditor|Long-lived agents drift when memory intake is noisy or overpromoted.
prompt-version-release|Prompt Version Release|Prompt rollouts need release notes, rollback paths, and blameability just like code.
execution-branch-viewer|Execution Branch Viewer|Complex agent runs need a way to visualize branches and discarded paths.
agent-cost-profiler|Agent Cost Profiler|A surprising amount of optimization starts with understanding where the spend actually came from.
tool-call-simulator|Tool Call Simulator|Dry-running tool calls catches obvious integration failures before production damage happens.
agent-review-inbox|Agent Review Inbox|Teams need one place to review strange, valuable, or risky agent outputs before they vanish.
state-reset-advisor|State Reset Advisor|Builders lose time because it is hard to tell when a workflow should reset versus recover.
agent-latency-breakdown|Agent Latency Breakdown|Per-step latency visibility matters when a workflow feels smart but too slow to use.
goal-persistence-check|Goal Persistence Check|Agents often appear flaky because the goal representation mutates too much during long runs.
guardrail-contradiction-scan|Guardrail Contradiction Scan|Multiple safety rules can conflict and produce broken behavior rather than safer behavior.
human-in-loop-router|Human in Loop Router|The real challenge is inserting humans at the right decision boundary without killing throughput.
workflow-ownership-map|Workflow Ownership Map|Shared agent systems fail when nobody owns the exact slice that broke.
agent-branch-merger|Agent Branch Merger|Parallel branches are useful only if there is a clean way to reconcile them afterward.
execution-proof-recorder|Execution Proof Recorder|Teams want auditable evidence of what happened during a run, not just a final answer.
failure-taxonomy-builder|Failure Taxonomy Builder|A stable failure language helps teams stop rediscovering the same bug class every week.
agent-skill-registry|Agent Skill Registry|Reusable skills need a stronger registry than folders full of prompts and vague notes.
benchmark-gap-finder|Benchmark Gap Finder|Most teams still do not know which important agent behaviors they are not measuring.
agent-queue-prioritizer|Agent Queue Prioritizer|Operations get messy when many agent jobs compete for the same limited tool surfaces.
context-pruning-director|Context Pruning Director|The cheapest fix is often deciding what the agent should stop seeing.
verification-lane-router|Verification Lane Router|Not every step deserves the same verification budget, and builders need a policy for that.
agent-governance-checklist|Agent Governance Checklist|Shipping agent systems cleanly requires more operational governance than most teams admit.
execution-anomaly-detector|Execution Anomaly Detector|Weird runs become easier to debug when anomalies are surfaced as they happen.
agent-capability-card|Agent Capability Card|Teams need a durable artifact describing what an agent can reliably do right now.
stateful-loop-stress-test|Stateful Loop Stress Test|Stateful agents need pressure tests that reflect real repeated use rather than one-off demos.
tooling-dependency-map|Tooling Dependency Map|Agent reliability depends heavily on understanding which tools are critical-path dependencies.
instruction-precedence-check|Instruction Precedence Check|Many failures are just ambiguous hierarchy between user, system, and workflow instructions.
agent-jailbreak-review|Agent Jailbreak Review|Builders need a routine way to probe bad behavior without turning every review into a red-team epic.
artifact-trace-publisher|Artifact Trace Publisher|Useful agent work should leave behind a structured artifact trail for later diagnosis.
agent-release-candidate-board|Agent Release Candidate Board|Teams need a clearer pre-ship gate for agent workflows that are almost ready but still risky.
workflow-observability-pack|Workflow Observability Pack|Agent observability still lags far behind normal backend observability.
prompt-drift-detector|Prompt Drift Detector|Prompt stacks drift over time as patches accumulate and original intent gets blurry.
multi-agent-conflict-lens|Multi Agent Conflict Lens|Parallel agents often disagree in ways that reveal structure, not just noise.
agent-oncall-console|Agent Oncall Console|Once agents touch real operations, somebody needs an oncall-grade control surface.
eval-to-patch-bridge|Eval to Patch Bridge|The useful unit is not just a failed eval but the concrete patch path it implies.
tool-abuse-throttle|Tool Abuse Throttle|Runaway tool use is still one of the most expensive and embarrassing failure modes.
"""),
    },
    {
        "cluster_id": "startup-founder-systems",
        "label": "Startup Founder Systems",
        "seed_domains": ["startup-yc", "indie-hacker", "agentic-marketing"],
        "tags": ["startup", "founder", "builder"],
        "evidence_sources": ["x_twitter", "community", "producthunt"],
        "audience": "founders, operators, and startup teams",
        "loop_template": "capture evidence around {focus}, tighten the decision, ship the next move, and learn from the market",
        "ideas": _parse_ideas("""
idea-triage-board|Idea Triage Board|Founders need to kill or narrow ideas faster before they burn weeks building the wrong thing.
pain-interview-cutter|Pain Interview Cutter|User interviews get better when founders can quickly strip polite noise from real pain.
icp-friction-mapper|ICP Friction Mapper|A startup usually stalls because it still does not know which exact user pain it owns.
waitlist-signal-ranker|Waitlist Signal Ranker|Most waitlists are vanity until someone can score intent and seriousness properly.
founder-update-writer|Founder Update Writer|Good investor and team updates sharpen thinking because they force a narrative about reality.
pricing-objection-bank|Pricing Objection Bank|Pricing clarity improves when founders organize real objections instead of inventing them in a vacuum.
founder-storyline-tester|Founder Storyline Tester|A startup story should get sharper across homepage, demo, pitch, and X, not drift apart.
launch-sequence-planner|Launch Sequence Planner|Launches work better when momentum is staged rather than exhausted in one announcement.
problem-proof-wall|Problem Proof Wall|Founders gain conviction faster when real user evidence is clustered into a visible proof wall.
beta-user-cadence|Beta User Cadence|Early products improve faster when founders maintain a structured rhythm with beta users.
competitor-angle-radar|Competitor Angle Radar|Positioning gets easier when you can see which market angles are getting crowded or stale.
founder-decision-log|Founder Decision Log|The best founders can revisit why they made a call rather than arguing from memory.
churn-exit-clusterer|Churn Exit Clusterer|Startup learning accelerates when churn reasons are turned into recurring buckets and not forgotten.
founder-conviction-meter|Founder Conviction Meter|Teams can feel when strategy is weak long before metrics fully reveal it.
offer-stack-designer|Offer Stack Designer|Early revenue often comes from packaging the right combination of offer, proof, and urgency.
case-study-request-flow|Case Study Request Flow|Winning more social proof requires a repeatable way to ask, capture, and publish it.
channel-experiment-ledger|Channel Experiment Ledger|Startups repeat failed acquisition tests because nobody keeps a clean experiment memory.
onboarding-friction-ladder|Onboarding Friction Ladder|The first session still kills many promising products because the steps feel heavier than they should.
sales-call-pattern-finder|Sales Call Pattern Finder|Patterns from founder-led sales should compound into better product and positioning choices.
category-definition-drafter|Category Definition Drafter|A strong category frame can make a weird startup feel inevitable instead of confusing.
demo-pain-compiler|Demo Pain Compiler|Live demos improve when founders can sequence pains, proof, and payoff more deliberately.
founder-energy-audit|Founder Energy Audit|A startup can be directionally right and still die because the founders are allocating energy badly.
referral-loop-designer|Referral Loop Designer|Word-of-mouth usually needs structure before it becomes a real growth channel.
product-gap-prioritizer|Product Gap Prioritizer|Teams need a way to separate missing basics from distracting feature requests.
landing-page-claim-check|Landing Page Claim Check|A homepage should make bolder claims only when the proof can support them.
funnel-leak-tracker|Funnel Leak Tracker|Founders need one place to inspect where attention dies between content, site, signup, and use.
community-demand-reader|Community Demand Reader|Founder intuition improves when recurring requests from public communities are grouped and ranked.
pilot-readiness-review|Pilot Readiness Review|A product is not really pilot-ready until expectations, onboarding, and proof all line up.
objection-rebuttal-studio|Objection Rebuttal Studio|The best rebuttals turn into better product copy, not just better calls.
activation-moment-finder|Activation Moment Finder|Products grow faster when the team knows the exact moment users first feel the payoff.
founder-trust-dashboard|Founder Trust Dashboard|Trust compounds when promises, behavior, and product quality stay consistent in public.
narrative-pivot-simulator|Narrative Pivot Simulator|Messaging pivots are risky because teams cannot easily preview second-order effects.
upsell-timing-check|Upsell Timing Check|Upsells land best when the user has already crossed a visible value threshold.
market-map-notebook|Market Map Notebook|Founders need a durable place to connect adjacent markets, wedges, and future expansion paths.
trial-feedback-collector|Trial Feedback Collector|Most trial feedback disappears into chats instead of becoming structured learning.
founder-priority-freezer|Founder Priority Freezer|Context switching destroys progress when a team has no hard freeze on what matters this week.
funnel-proof-sequencer|Funnel Proof Sequencer|Proof converts better when the right story appears at the right stage of the funnel.
retention-cohort-explainer|Retention Cohort Explainer|Early retention is easier to fix when the team can narrate what each cohort actually did.
expansion-wedge-planner|Expansion Wedge Planner|Good second wedges are adjacent enough to sell but different enough to grow the market.
customer-language-harvester|Customer Language Harvester|The best homepage and pitch copy still comes from real user phrasing.
founder-meeting-sharpening|Founder Meeting Sharpening|Founding teams need cleaner meeting structure so strategy doesn’t dissolve into vague talk.
win-loss-board|Win Loss Board|Teams get sharper when they can study why each deal was won, lost, or stalled.
founder-focus-window|Founder Focus Window|Not every startup deserves the same operating cadence every week.
offer-proof-alignment|Offer Proof Alignment|Revenue improves when the offer being sold matches the proof already available.
launch-postmortem-desk|Launch Postmortem Desk|A launch only compounds if the team captures what actually worked and why.
investor-question-brief|Investor Question Brief|Preparation gets better when likely investor concerns are turned into prewritten answer surfaces.
community-seeding-playbook|Community Seeding Playbook|Communities form more reliably when founders know the first few rituals to seed.
revenue-urgency-scan|Revenue Urgency Scan|A startup often needs to know whether to optimize growth, retention, or immediate cash.
customer-success-trigger-map|Customer Success Trigger Map|Success motions should begin before churn becomes visible, not after.
founder-public-building-compass|Founder Public Building Compass|Founders shipping in public need to know what to reveal, what to hold, and why.
"""),
    },
    {
        "cluster_id": "productivity-builder-ops",
        "label": "Builder Productivity Systems",
        "seed_domains": ["cursor-copilot", "web-designer", "task-agent-ai"],
        "tags": ["productivity", "builder", "workflow"],
        "evidence_sources": ["x_twitter", "github", "community"],
        "audience": "builders, operators, and high-output solo teams",
        "loop_template": "capture work around {focus}, reduce friction, execute the next block, and keep momentum",
        "ideas": _parse_ideas("""
deep-work-blocker|Deep Work Blocker|Builders need a stronger system for defending uninterrupted focus than generic calendars provide.
meeting-to-action-bridge|Meeting to Action Bridge|A lot of operational drag comes from meetings that never become clear next actions.
context-switch-meter|Context Switch Meter|People underestimate how much throughput they lose to scattered tabs, chats, and half-open tasks.
priority-stack-board|Priority Stack Board|A useful productivity system makes tradeoffs visible instead of pretending everything is urgent.
task-energy-matcher|Task Energy Matcher|Different work types demand different cognitive energy, and builders rarely schedule with that in mind.
inbox-triage-ladder|Inbox Triage Ladder|Inbox cleanup works best when messages are routed by consequence rather than just recency.
async-brief-composer|Async Brief Composer|Better async communication reduces meetings only when the briefs are high quality.
workday-reset-ritual|Workday Reset Ritual|A clean end-of-day reset keeps tomorrow from starting with invisible clutter.
execution-friction-audit|Execution Friction Audit|Teams need a better way to spot recurring friction in how work actually gets done.
sprint-shape-designer|Sprint Shape Designer|Short planning cycles work only when the work is shaped tightly enough to finish.
ship-logbook|Ship Logbook|Momentum improves when teams can see what actually shipped instead of what was merely discussed.
decision-queue-cleaner|Decision Queue Cleaner|Stalled work often hides behind unresolved small decisions that nobody owns.
builder-routine-calibrator|Builder Routine Calibrator|Good routines are more about matching energy and task type than copying gurus.
deadline-risk-scanner|Deadline Risk Scanner|Projects slip quietly long before anyone says the date is in danger.
focus-sprint-scoreboard|Focus Sprint Scoreboard|People work differently when short bursts of focused execution are visible and measurable.
handoff-clarity-check|Handoff Clarity Check|A task handoff fails when the next person cannot act without chasing context.
operator-command-center|Operator Command Center|Solo operators want one control layer for priorities, followups, blockers, and ongoing bets.
commitment-overload-radar|Commitment Overload Radar|Teams overcommit because their visible work list excludes hidden obligations.
followup-guarantee-flow|Followup Guarantee Flow|A lot of trust comes from reliable followthrough, not just fast replies.
task-scope-pruner|Task Scope Pruner|Small scope decisions often create the difference between shipping and spinning.
output-rhythm-tracker|Output Rhythm Tracker|Consistency matters more when builders can see their actual shipping rhythm over time.
execution-window-router|Execution Window Router|The best next task depends on available time, energy, and context depth.
blocking-issue-escalator|Blocking Issue Escalator|Work stalls too long because blockers do not cross the line into visible escalation.
note-to-action-parser|Note to Action Parser|Many useful ideas die in notes because nobody extracts the action hidden inside them.
maintenance-drag-meter|Maintenance Drag Meter|Operational upkeep can quietly consume the time that should go to new work.
task-resurrection-desk|Task Resurrection Desk|Old half-started tasks need a better reentry path than reading old notes and guessing.
decision-fatigue-buffer|Decision Fatigue Buffer|Productivity systems should reduce tiny repetitive decisions before they eat attention.
builder-shutdown-checklist|Builder Shutdown Checklist|A clean shutdown ritual improves the next morning more than another late-night half hour.
calendar-pressure-audit|Calendar Pressure Audit|Calendar crowding often hides why high-priority work never gets deep attention.
execution-proof-trail|Execution Proof Trail|Teams make better decisions when they can inspect evidence of work done, not just claims.
priority-conflict-detector|Priority Conflict Detector|Many planning failures are just two incompatible priorities being treated as compatible.
async-approval-lane|Async Approval Lane|Lightweight approvals help teams move faster without dragging everything into a meeting.
builder-recovery-cycle|Builder Recovery Cycle|Sustained output needs deliberate recovery instead of accidental burnout.
deadline-compression-coach|Deadline Compression Coach|Sometimes the issue is not time but poor sequence and weak scoping.
task-gravity-watcher|Task Gravity Watcher|Big ambiguous tasks attract avoidance until someone reframes the first concrete move.
execution-environment-reset|Execution Environment Reset|People start cleaner work when their operating environment is reset intentionally.
operator-response-batch|Operator Response Batch|Batching responses preserves focus better than living inside reactive channels.
small-win-compiler|Small Win Compiler|Visible progress helps teams keep shipping through messy middle phases.
planning-entropy-reader|Planning Entropy Reader|A plan decays when its assumptions are no longer true but nobody updated the shape.
builder-focus-fence|Builder Focus Fence|The highest performers often protect a clear fence around what they will not do this week.
recurrence-automation-map|Recurrence Automation Map|Repeated small tasks deserve automation earlier than most teams realize.
signal-vs-admin-splitter|Signal vs Admin Splitter|Builder calendars get healthier when signal work is separated from administrative residue.
time-leak-dossier|Time Leak Dossier|A serious productivity system should show where hours disappeared, not just where they were meant to go.
handoff-memory-bank|Handoff Memory Bank|Teams lose time because knowledge about recurring handoffs is rarely preserved.
builder-scorecard-weekly|Builder Scorecard Weekly|A weekly scorecard helps keep outputs and learning visible, not just busyness.
task-sequence-optimizer|Task Sequence Optimizer|Order matters because some tasks unlock others while some just consume good attention.
execution-clarity-lens|Execution Clarity Lens|People move faster when ambiguity is made explicit rather than ignored.
focus-reentry-guide|Focus Reentry Guide|Returning to deep work after interruptions should not require rebuilding context from scratch.
operator-overhead-trimmer|Operator Overhead Trimmer|The best ops systems cut invisible drag before asking people to work harder.
workflow-fracture-alert|Workflow Fracture Alert|A workflow often breaks slowly through tiny fractures rather than one big incident.
"""),
    },
    {
        "cluster_id": "career-status-social-proof",
        "label": "Career / Status / Social Proof",
        "seed_domains": ["resume-ai", "linkedin-optimizer", "interview-prep-ai"],
        "tags": ["career", "status", "social-proof"],
        "evidence_sources": ["x_twitter", "community", "producthunt"],
        "audience": "job seekers, ambitious operators, and status-conscious professionals",
        "loop_template": "collect proof around {focus}, package the signal, present it well, and reuse what opens doors",
        "ideas": _parse_ideas("""
resume-signal-rewrite|Resume Signal Rewrite|Most resumes hide real signal because they read like duty lists instead of evidence of leverage.
portfolio-proof-grid|Portfolio Proof Grid|A portfolio is stronger when proof is organized by claim, artifact, and outcome.
interview-story-bank|Interview Story Bank|People interview better when their real stories are prepared before the pressure moment.
linkedin-positioning-audit|LinkedIn Positioning Audit|Professional profiles often undersell the actual niche edge a person has built.
offer-comparison-desk|Offer Comparison Desk|Career decisions get better when compensation, learning, status, and upside are compared honestly.
status-gap-scanner|Status Gap Scanner|Professionals want to know what signal is missing between where they are and where they want to be.
career-pivot-brief|Career Pivot Brief|A pivot works when someone can clearly explain why the old background is an advantage, not baggage.
proof-of-work-publisher|Proof of Work Publisher|Public proof still beats abstract claims when trying to get attention from high-quality opportunities.
interview-objection-coach|Interview Objection Coach|Candidates need a better way to prepare for hidden objections than just rehearsing common questions.
career-capital-ledger|Career Capital Ledger|Professionals underestimate how much leverage they already have when it is scattered across years and roles.
salary-narrative-builder|Salary Narrative Builder|Compensation conversations improve when the value story is tighter than the title story.
manager-credibility-dashboard|Manager Credibility Dashboard|Leaders build internal reputation through repeated delivery, clarity, and calm under pressure.
case-study-resume-bridge|Case Study Resume Bridge|Real work examples convert better than one-line bullet points when properly packaged.
career-signal-calendar|Career Signal Calendar|A long career climb usually comes from consistent public signals rather than one heroic post.
promotion-case-writer|Promotion Case Writer|Internal promotions go better when someone can package scope, leverage, and evidence like a real case.
network-warmth-mapper|Network Warmth Mapper|Most people do not know which relationships are actually warm enough for a real ask.
authority-thread-planner|Authority Thread Planner|X and LinkedIn authority is often built by repeating one sharp lane of insight.
interview-loop-radar|Interview Loop Radar|Candidates need a better read on where they are winning or losing inside an interview sequence.
proof-cluster-resume|Proof Cluster Resume|Resume bullets become stronger when grouped into proof clusters rather than random chronology.
public-reputation-monitor|Public Reputation Monitor|Online reputation compounds quietly and deserves active tracking.
career-option-map|Career Option Map|People make better moves when they can see adjacent roles, not just the one they started with.
credibility-receipt-vault|Credibility Receipt Vault|Screenshots, launches, testimonials, and shipped work should be easier to pull into one place.
reference-request-system|Reference Request System|References are stronger when the ask gives them structure and reminders of the best evidence.
executive-presence-drill|Executive Presence Drill|A lot of perceived seniority comes from communication pattern, not just title.
application-stack-optimizer|Application Stack Optimizer|Job seekers need to know which parts of an application stack are helping versus hurting conversion.
career-storyline-editor|Career Storyline Editor|People need a coherent narrative for nonlinear careers, especially across startups and experiments.
status-benchmark-board|Status Benchmark Board|Ambitious people compare themselves to fuzzy benchmarks instead of concrete next-tier signals.
meeting-voice-calibrator|Meeting Voice Calibrator|A person's in-room status often depends on timing, framing, and brevity more than correctness.
proof-request-reminder|Proof Request Reminder|Capturing praise and outcomes near the moment is easier than reconstructing them months later.
career-visibility-system|Career Visibility System|Internal visibility should be managed deliberately instead of left to chance.
interview-postmortem-book|Interview Postmortem Book|Candidates improve faster when each interview becomes a real diagnostic.
value-claim-checker|Value Claim Checker|Career messaging gets stronger when every claim is tied to a believable proof source.
authority-surface-mapper|Authority Surface Mapper|Different platforms can signal different aspects of credibility if used intentionally.
career-intro-generator|Career Intro Generator|Short bios and intros should adapt to target audience instead of being one static paragraph everywhere.
compensation-proof-pack|Compensation Proof Pack|Negotiation improves when evidence of value is assembled before the conversation starts.
mentor-update-writer|Mentor Update Writer|Good updates keep important mentors engaged without becoming awkward or needy.
personal-brand-sharpener|Personal Brand Sharpener|A personal brand is mostly about clear repeated signal, not inspirational aesthetics.
promotion-risk-scanner|Promotion Risk Scanner|People miss promotions when invisible doubts about scope or readiness stay unaddressed.
job-search-cadence|Job Search Cadence|Searches get stronger when outreach, applications, and followups run on a deliberate rhythm.
reference-signal-clusterer|Reference Signal Clusterer|Reference themes reveal which strengths other people actually notice in you.
credibility-gap-repair|Credibility Gap Repair|Sometimes the main issue is not skill but a mismatch between signal and reality.
leadership-proofbook|Leadership Proofbook|Leadership claims land better when they show decisions, tradeoffs, and results.
career-risk-memo|Career Risk Memo|A lot of career regret comes from not naming the risk of staying put.
portfolio-relevance-ranker|Portfolio Relevance Ranker|Candidates need to know which projects are most persuasive for a given role.
interview-energy-tracker|Interview Energy Tracker|Performance changes across a loop because interview energy is not actually constant.
status-signal-prioritizer|Status Signal Prioritizer|Not every credential or post adds equal status value to a target audience.
manager-update-brief|Manager Update Brief|Internal trust improves when status updates are concise, evidence-backed, and predictable.
career-proof-remixer|Career Proof Remixer|One strong work artifact should be reusable across resume, profile, intro, and outreach.
offer-negotiation-rehearsal|Offer Negotiation Rehearsal|Candidates want practice against realistic negotiation pressure, not just tips.
long-game-career-planner|Long Game Career Planner|The strongest careers are designed as compounding arcs rather than reactive hops.
"""),
    },
    {
        "cluster_id": "developer-distribution-tools",
        "label": "Developer Distribution Tools",
        "seed_domains": ["github-growth-ai", "devrel-copilot", "open-source-launch-ai"],
        "tags": ["developer", "distribution", "open-source"],
        "evidence_sources": ["github", "x_twitter", "community"],
        "audience": "developer founders, devrel teams, and open-source maintainers",
        "loop_template": "package {focus}, publish the right artifact, distribute it across developer channels, and learn from response",
        "ideas": _parse_ideas("""
changelog-launch-writer|Changelog Launch Writer|Releases underperform because maintainers announce diffs instead of changed outcomes.
github-issue-digest|GitHub Issue Digest|Maintainers need a readable view of issue pressure, repeated asks, and user confusion.
release-snippet-studio|Release Snippet Studio|A strong launch needs multiple post and doc snippets, not one generic announcement.
devrel-feedback-router|DevRel Feedback Router|Community feedback gets lost when it is split across docs, chat, X, and repo issues.
open-source-proofboard|Open Source Proofboard|Projects grow faster when maintainers can show credibility, usage, and community momentum clearly.
readme-conversion-audit|README Conversion Audit|A repo homepage is still a landing page, and many high-signal projects waste that surface.
release-arc-planner|Release Arc Planner|Major launches work better when the team plans the education arc around the release.
doc-gap-clusterer|Doc Gap Clusterer|The same missing docs show up repeatedly in issues, but most teams do not group them well.
developer-demo-script|Developer Demo Script|Technical demos win when they show the right pain and payoff sequence.
community-ask-ranker|Community Ask Ranker|Maintainers need to know which community asks deserve action versus polite acknowledgment.
repo-storyline-editor|Repo Storyline Editor|A project narrative should stay consistent across README, website, docs, and launch posts.
feature-proof-gallery|Feature Proof Gallery|Developers convert better when a feature is tied to a visible workflow and result.
release-risk-brief|Release Risk Brief|Teams need a cleaner summary of what might break before pushing a big release live.
maintainer-update-writer|Maintainer Update Writer|Regular project updates help community trust when they stay concrete and honest.
developer-persona-mapper|Developer Persona Mapper|Different dev audiences respond to different proof, examples, and vocabulary.
integration-launch-checklist|Integration Launch Checklist|Integrations flop when the docs, examples, and distribution plan are misaligned.
docs-entrypoint-router|Docs Entrypoint Router|Good docs should route different user types to different first steps.
release-reply-console|Release Reply Console|Post-launch discussion often shapes perception more than the launch post itself.
contributor-onramp-designer|Contributor Onramp Designer|More people contribute when the path from curious user to useful contributor is explicit.
api-positioning-lens|API Positioning Lens|An API needs a clear narrative about what it replaces, improves, or unlocks.
technical-case-study-maker|Technical Case Study Maker|A good technical case study is both marketing and documentation at the same time.
demo-video-editor|Demo Video Editor|Developer video demos need tighter structure than generic screencasts.
launch-recency-decay-watch|Launch Recency Decay Watch|Attention fades faster than teams think once a launch window closes.
repo-funnel-metrics|Repo Funnel Metrics|Open-source teams need to see the path from impression to star to install to retained use.
developer-advocate-cadence|Developer Advocate Cadence|Community education compounds when its rhythm is deliberate.
issue-to-content-bridge|Issue to Content Bridge|Repeated questions should become docs or content instead of recurring one-off replies.
producthunt-for-devs|Product Hunt for Devs|Developer launches need positioning that matches how dev tools are actually discovered.
migration-guide-doctor|Migration Guide Doctor|Migrations fail when users cannot quickly see safety, sequence, and payoff.
community-proof-badges|Community Proof Badges|Social proof inside developer ecosystems works best when it is concrete and technical.
release-demo-atomizer|Release Demo Atomizer|One good launch demo should split into many smaller educational assets.
maintainer-burnout-scan|Maintainer Burnout Scan|Healthy distribution requires maintainers to protect energy, not just output.
docs-example-ranker|Docs Example Ranker|Teams need to know which examples actually help activation and which ones are ornamental.
launch-narrative-variants|Launch Narrative Variants|The same release should be framed differently for builders, managers, and curious observers.
repo-social-preview|Repo Social Preview|The first visual proof many people see is social, not the README itself.
developer-community-rituals|Developer Community Rituals|Projects grow stronger communities when recurring rituals exist beyond support threads.
ecosystem-mention-monitor|Ecosystem Mention Monitor|Maintainers need to see when the project starts surfacing in adjacent ecosystems.
roadmap-trust-calibrator|Roadmap Trust Calibrator|Roadmaps help when they balance ambition with believable delivery.
integration-case-router|Integration Case Router|Different integrations need distinct stories about value and setup burden.
release-feedback-scorecard|Release Feedback Scorecard|After launch, teams need a structured read on what landed and what confused people.
developer-testimonial-harvester|Developer Testimonial Harvester|Useful technical testimonials are rare unless somebody asks with the right framing.
adoption-proof-threader|Adoption Proof Threader|Launch threads work better when they sequence proof rather than dumping features.
maintainer-inbox-zero|Maintainer Inbox Zero|Open-source maintainers need better triage than living inside notifications.
community-demo-library|Community Demo Library|User-made demos are powerful distribution assets when curated properly.
technical-announcement-checker|Technical Announcement Checker|Technical announcements fail when they over-assume context or under-explain stakes.
version-upgrade-memo|Version Upgrade Memo|Upgrade messaging should explain what changed for real workflows, not just the diff.
ecosystem-fit-brief|Ecosystem Fit Brief|Developer products gain traction faster when they explain where they fit in the stack.
release-expectation-setter|Release Expectation Setter|A launch is stronger when it says what it is and what it is not.
maintainer-social-kit|Maintainer Social Kit|Many technical founders need help distributing without sounding like growth-hacked robots.
docs-funnel-simplifier|Docs Funnel Simplifier|Complicated docs funnel users into confusion before they ever touch the product.
open-source-story-archive|Open Source Story Archive|Projects deserve an archive of the big moments, tradeoffs, and wins that shaped them.
"""),
    },
    {
        "cluster_id": "consumer-agent-utilities",
        "label": "Consumer Agent Utilities",
        "seed_domains": ["trip-planner-ai", "shopping-deal-finder", "family-coordinator-ai"],
        "tags": ["consumer", "utility", "assistant"],
        "evidence_sources": ["x_twitter", "producthunt", "community"],
        "audience": "consumers, families, and everyday operators",
        "loop_template": "track needs around {focus}, choose the best option, act, and keep the decision memory for later reuse",
        "ideas": _parse_ideas("""
weekend-trip-matcher|Weekend Trip Matcher|People want quick trip plans that fit mood, budget, and travel fatigue without a research spiral.
grocery-price-radar|Grocery Price Radar|Households care about repeat shopping savings more than occasional one-off discounts.
family-calendar-referee|Family Calendar Referee|Family planning breaks because everyone's schedule conflicts are discovered too late.
subscription-leak-finder|Subscription Leak Finder|Consumers forget about small recurring charges until they become obvious resentment.
group-dinner-decider|Group Dinner Decider|Picking a place for multiple people is still an absurdly high-friction consumer decision.
return-window-reminder|Return Window Reminder|A lot of wasted consumer money comes from missed return windows.
household-reorder-desk|Household Reorder Desk|Routine home supplies should be easier to reorder at the right time and price.
gift-brief-builder|Gift Brief Builder|Gift shopping improves when the system remembers a person's taste, price range, and past wins.
errand-route-composer|Errand Route Composer|Local errands are annoying because each stop is planned in isolation.
travel-regret-check|Travel Regret Check|People want a sanity layer before booking something expensive or exhausting.
appointment-gap-scanner|Appointment Gap Scanner|Health, admin, and home appointments fall through because nobody tracks the true gaps.
bill-negotiation-prep|Bill Negotiation Prep|Consumers want a sharper script before calling to reduce recurring bills.
household-decision-journal|Household Decision Journal|Important recurring household calls should be easier to revisit later.
personal-admin-runway|Personal Admin Runway|Life admin feels endless because small obligations are never turned into an ordered runway.
shopping-proof-comparer|Shopping Proof Comparer|Consumers need reasons to trust a product beyond influencer hype and star averages.
vacation-pack-builder|Vacation Pack Builder|Trip packing still wastes time because context-specific pack lists are hard to reuse.
school-form-orchestrator|School Form Orchestrator|Family admin gets painful when school paperwork keeps reappearing in new formats.
friend-hangout-planner|Friend Hangout Planner|Social plans die because nobody converts vague interest into a specific plan fast enough.
household-budget-adjuster|Household Budget Adjuster|Families need a live way to adapt budget decisions when reality changes mid-month.
meal-chaos-reducer|Meal Chaos Reducer|Dinner friction is often a planning and inventory problem, not a recipe problem.
coupon-stack-checker|Coupon Stack Checker|Consumers want to know whether a deal is real before they invest time in checkout games.
commute-option-chooser|Commute Option Chooser|People regularly make the same local travel decision without enough context.
life-admin-triage|Life Admin Triage|A useful personal assistant should tell you what matters first, not just list everything.
cleaning-cycle-planner|Cleaning Cycle Planner|Households need repeatable cleaning rhythms that fit actual life rather than idealized routines.
household-receipt-vault|Household Receipt Vault|Consumers need receipts when things break, warranties matter, or disputes happen.
trip-fit-score|Trip Fit Score|A destination may be exciting but still wrong for the actual group and timing.
parent-logistics-bridge|Parent Logistics Bridge|Co-parenting and family logistics improve when there is less ambiguity around responsibilities.
closet-wear-rotator|Closet Wear Rotator|People often underuse what they already own because they cannot see good outfit possibilities quickly.
home-project-checklist|Home Project Checklist|Small home projects become bigger annoyances when material and step planning are vague.
service-provider-memory|Service Provider Memory|Finding a good local pro once should be more reusable than digging through old chats.
event-budget-splitter|Event Budget Splitter|Shared-event money decisions get awkward when nobody can see the tradeoffs clearly.
habit-trigger-planner|Habit Trigger Planner|Everyday habits stick better when the trigger design matches real routines.
price-drop-watchtower|Price Drop Watchtower|Big purchases deserve a better waiting and alerting layer than casual bookmarking.
pet-care-scheduler|Pet Care Scheduler|Pet routines fail when medication, supplies, and appointments are not coordinated.
travel-time-sanitizer|Travel Time Sanitizer|Consumers want better expectations around transit friction, not just distance.
memory-based-shopping|Memory Based Shopping|Shopping gets better when a system remembers what worked for you last time.
birthday-memory-bank|Birthday Memory Bank|Thoughtful gifting depends on remembering cues months before the event.
home-inventory-lens|Home Inventory Lens|People re-buy things because their own home inventory is effectively invisible.
queue-skip-finder|Queue Skip Finder|Small local time savings are meaningful when repeated weekly.
shared-trip-board|Shared Trip Board|Group trips need a better shared planning surface that is not just a long message thread.
digital-clutter-reducer|Digital Clutter Reducer|Personal digital clutter becomes stressful because nobody curates what still matters.
appointment-prep-brief|Appointment Prep Brief|People show up unprepared to important appointments because context gathering is annoying.
family-food-preferences|Family Food Preferences|Meal planning gets easier when preferences, allergies, and current moods are remembered together.
micro-budget-planner|Micro Budget Planner|Some people need lightweight budget planning without committing to a full finance system.
household-friction-log|Household Friction Log|Small repeated annoyances are often the best automation or purchase opportunities.
safe-purchase-checker|Safe Purchase Checker|Consumers want a quick risk check before buying from unfamiliar sellers or sketchy listings.
local-outing-suggester|Local Outing Suggester|Weekend plans improve when a system understands weather, travel time, and group vibe.
task-share-balancer|Task Share Balancer|Household tension often comes from hidden imbalance in recurring tasks.
small-claims-prep|Small Claims Prep|Consumers want clearer preparation when facing refunds, disputes, or low-stakes legal friction.
everyday-proof-assistant|Everyday Proof Assistant|Normal life decisions get easier when receipts, screenshots, and notes are easy to retrieve at the right moment.
"""),
    },
    {
        "cluster_id": "crypto-defi-trading",
        "label": "Crypto / DeFi / Trading",
        "seed_domains": ["trading-crypto", "defi-architect", "onchain-research-ai"],
        "tags": ["crypto", "defi", "trading"],
        "evidence_sources": ["x_twitter", "community", "github"],
        "audience": "traders, researchers, onchain operators, and crypto natives",
        "loop_template": "monitor {focus}, decide the position or action, execute, and fold the result back into the next playbook",
        "ideas": _parse_ideas("""
airdrop-route-planner|Airdrop Route Planner|Crypto users keep chasing fragmented airdrop paths because the opportunity graph changes constantly.
governance-vote-briefing|Governance Vote Briefing|Most token holders do not want raw forum dumps; they want the real decision and second-order effects.
wallet-risk-watch|Wallet Risk Watch|Onchain users need better warnings around approval risk, contract risk, and concentration risk.
yield-rotation-desk|Yield Rotation Desk|DeFi opportunity moves quickly enough that rotation discipline beats static yield farming.
token-unlock-pressure|Token Unlock Pressure|Unlock schedules matter because they change trader psychology well before the date arrives.
onchain-narrative-radar|Onchain Narrative Radar|Crypto attention clusters around narratives faster than fundamentals alone explain.
liquidity-migration-map|Liquidity Migration Map|Capital often moves in waves across chains and protocols, not randomly.
airdrop-receipt-vault|Airdrop Receipt Vault|People want a cleaner record of what they did, where they qualified, and what is still pending.
wallet-cluster-brief|Wallet Cluster Brief|Following wallet clusters can reveal behavior patterns earlier than public sentiment.
governance-delegate-finder|Governance Delegate Finder|Protocol voters want a faster way to identify delegates aligned with their priorities.
token-flow-monitor|Token Flow Monitor|Large token flows still move faster than most retail researchers can contextualize.
defi-strategy-postmortem|DeFi Strategy Postmortem|Serious traders need repeatable postmortems on why a strategy worked or failed.
smart-money-contrast|Smart Money Contrast|The useful question is often how notable wallets disagree, not just what they all bought.
bridge-risk-checker|Bridge Risk Checker|Bridge usage feels routine until a specific bridge becomes the point of hidden systemic risk.
wallet-hygiene-audit|Wallet Hygiene Audit|Crypto natives still need a tighter operational checklist around wallet hygiene and permissions.
dao-drama-recap|DAO Drama Recap|Governance drama often matters because it changes contributor incentives and token perception.
token-thesis-board|Token Thesis Board|A good token thesis should survive contact with supply, utility, and attention realities.
defi-stack-rebuilder|DeFi Stack Rebuilder|People need help rebuilding their stack after strategy drift, losses, or a narrative change.
staking-rotation-tracker|Staking Rotation Tracker|Yield decisions improve when staking options are compared against unlock and opportunity cost.
treasury-behavior-monitor|Treasury Behavior Monitor|Protocol treasury moves can signal hidden pressure or hidden conviction.
perp-position-journal|Perp Position Journal|Traders learn faster when they can revisit the original logic behind each position.
airdrop-farm-prioritizer|Airdrop Farm Prioritizer|The bottleneck is choosing where to spend limited onchain attention and gas.
wallet-identity-lens|Wallet Identity Lens|Wallet behavior can reveal a participant archetype long before their public profile does.
governance-proposal-diff|Governance Proposal Diff|Proposal edits matter because the decisive line often changes quietly between versions.
stablecoin-risk-brief|Stablecoin Risk Brief|Stablecoin choices deserve more scrutiny than many users currently give them.
onchain-copytrade-filter|Onchain Copytrade Filter|Blind copytrading fails because strategy, size, and timing are rarely legible.
emissions-decay-desk|Emissions Decay Desk|Protocols driven by incentives need a clearer read on what happens as emissions decay.
protocol-revival-monitor|Protocol Revival Monitor|Some dead-looking protocols revive when incentives, teams, or narratives flip.
gas-opportunity-timer|Gas Opportunity Timer|Gas cost materially changes whether a strategy is even worth running.
wallet-behavior-alerts|Wallet Behavior Alerts|A small number of wallet behaviors often matter more than generic market noise.
defi-governance-calendar|DeFi Governance Calendar|Important governance windows are still too easy to miss if you track many protocols.
token-dilution-memo|Token Dilution Memo|Retail traders regularly ignore dilution dynamics until price action already reflected them.
airdrop-civil-war-detector|Airdrop Civil War Detector|Communities turn quickly when an airdrop feels unfair, extractive, or badly messaged.
narrative-rotation-board|Narrative Rotation Board|Capital rotates across narratives faster than full research cycles can keep up.
contract-trust-score|Contract Trust Score|Users want a fast trust read before interacting with unfamiliar onchain code.
vault-performance-reader|Vault Performance Reader|Yield products are easier to trust when performance and hidden risk are explained plainly.
dao-power-map|DAO Power Map|Governance power is rarely distributed the way surface token counts imply.
wallet-approval-sweeper|Wallet Approval Sweeper|Old approvals linger because revocation is not part of most users' weekly flow.
ecosystem-quest-brief|Ecosystem Quest Brief|New chain ecosystems still rely on quest-like onboarding and incentive routes.
token-launch-smoke-test|Token Launch Smoke Test|Launches need a sober quality check before hype overwhelms reality.
airdrop-thesis-checker|Airdrop Thesis Checker|Some airdrop strategies look smart only because nobody modeled the cost and odds honestly.
liquidity-stickiness-lens|Liquidity Stickiness Lens|The key question is not where liquidity is, but whether it will stay there.
defi-income-allocator|DeFi Income Allocator|Crypto natives want to split stable income, growth bets, and degen bets with more intention.
governance-sentiment-read|Governance Sentiment Read|Forum tone and vote direction often diverge in useful ways.
bridged-asset-risk-map|Bridged Asset Risk Map|Cross-chain assets carry hidden dependencies most users do not track closely.
onchain-social-proof|Onchain Social Proof|Wallet behavior becomes more persuasive when grouped into legible patterns and explanations.
token-catalyst-watch|Token Catalyst Watch|Catalyst calendars matter because markets price anticipation, not just outcomes.
rotation-reentry-planner|Rotation Reentry Planner|A lot of traders can exit a narrative but struggle to reenter with discipline.
defi-drawdown-explainer|DeFi Drawdown Explainer|Post-loss clarity matters because confusion often causes the next bad trade.
wallet-counterparty-check|Wallet Counterparty Check|Counterparty risk remains one of the most underexplained retail crypto risks.
"""),
    },
    {
        "cluster_id": "x-native-persona-tools",
        "label": "X-Native Persona Tools",
        "seed_domains": ["xcontent", "personal-brand-ai", "reply-guy-ai"],
        "tags": ["viral", "x-native", "persona"],
        "evidence_sources": ["x_twitter", "community", "producthunt"],
        "audience": "X-native founders, posters, and social identity builders",
        "loop_template": "study {focus}, draft the sharper public move, post or reply, and keep the identity signal consistent",
        "ideas": _parse_ideas("""
reply-ladder|Reply Ladder|A lot of X growth still comes from replies, but most people have no structure for doing them well.
quote-tweet-angle-finder|Quote Tweet Angle Finder|Quote tweets work when they add a new frame instead of just agreeing or dunking.
persona-bio-rewrite|Persona Bio Rewrite|A bio should signal what someone is about in a way that attracts the right followers and opportunities.
thread-arc-checker|Thread Arc Checker|Threads perform better when each post advances tension instead of restating the hook.
hot-take-calibrator|Hot Take Calibrator|Strong opinions spread when the edge feels sharp but not stupid.
social-proof-sequencer|Social Proof Sequencer|Status posts work better when receipts appear in the right order.
x-launch-post-builder|X Launch Post Builder|Launch posts need a clearer promise, visual, and social proof package than most founders ship.
reply-conversion-map|Reply Conversion Map|Not every reply deserves equal effort because some lanes lead to followers, leads, or relationships.
persona-consistency-audit|Persona Consistency Audit|A public identity gets muddy when posts, replies, and profile signal different things.
controversy-boundary-check|Controversy Boundary Check|X-native growth often depends on staying sharp without crossing into avoidable backlash.
breakout-thread-studio|Breakout Thread Studio|Some ideas deserve a long-form thread because they need narrative buildup to land.
community-insider-language|Community Insider Language|People bond faster when the language signals in-group fluency without sounding forced.
quote-bank-for-posting|Quote Bank for Posting|Short memorable lines are reusable social assets when stored well.
public-positioning-board|Public Positioning Board|Founders and creators need to know which public lane they are actually claiming.
reply-heat-ranker|Reply Heat Ranker|Some accounts are worth replying to because the audience overlap is unusually high leverage.
thread-payoff-meter|Thread Payoff Meter|Weak endings kill threads that started strong.
x-content-remix-map|X Content Remix Map|One strong post should generate multiple followups, visuals, or threaded expansions.
status-signal-spotter|Status Signal Spotter|X is full of subtle status cues that compound when used intentionally.
persona-pivot-guide|Persona Pivot Guide|Changing how you show up online is risky when your audience expects a different character.
controversy-recovery-plan|Controversy Recovery Plan|Post-reaction matters almost as much as the original mistake when public sentiment turns.
reply-voice-match|Reply Voice Match|Replies work better when they match the vibe and power level of the original poster.
x-thread-outline|X Thread Outline|A clear outline reduces the number of threads that die halfway through drafting.
audience-polarity-scan|Audience Polarity Scan|A post can grow because it attracts love or because it attracts conflict, and the tradeoff matters.
founder-poster-rhythm|Founder Poster Rhythm|Posting rhythm shapes how credible and alive a founder feels online.
public-belief-tracker|Public Belief Tracker|Strong posters repeat a few core beliefs until the audience can predict the worldview.
reply-window-monitor|Reply Window Monitor|Timing matters because the same reply can vanish or spread depending on when it lands.
thread-hook-archive|Thread Hook Archive|A good library of opening patterns speeds up public writing without flattening voice.
persona-proof-surface|Persona Proof Surface|Online identity becomes more durable when proof and receipts are easy to surface.
reaction-post-shaper|Reaction Post Shaper|Fast reaction posts win when they add taste, not just speed.
identity-signal-clusterer|Identity Signal Clusterer|People want to know which signals are actually teaching the audience how to categorize them.
social-credibility-desk|Social Credibility Desk|Public trust grows when references, wins, and associations are packaged well.
reply-relationship-crm|Reply Relationship CRM|A lot of high-value social relationships start as repeated lightweight interactions.
thread-tone-calibrator|Thread Tone Calibrator|The same point can read insightful or embarrassing depending on tone.
memetic-angle-board|Memetic Angle Board|A post spreads more when the framing is native to internet culture instead of generic business speak.
audience-overlap-lens|Audience Overlap Lens|The best growth targets are often communities one step adjacent, not giant unrelated accounts.
social-proof-gap-audit|Social Proof Gap Audit|People can feel credible in reality and still look weak online if the proof surface is thin.
persona-tagline-workshop|Persona Tagline Workshop|A strong tagline helps audiences remember the lane you want to own.
quote-tweet-rebuttal-bench|Quote Tweet Rebuttal Bench|Rebuttals spread best when they are calm, sharp, and structure the disagreement cleanly.
online-reputation-guard|Online Reputation Guard|Public reputation can degrade slowly through accumulation of sloppy posts.
reply-funnel-recorder|Reply Funnel Recorder|The best replies should be reusable as future posts or founder narratives.
thread-social-proof-injector|Thread Social Proof Injector|Strategic proof inside a thread can change how the whole argument is received.
credibility-borrowing-map|Credibility Borrowing Map|Associations and references on X can transfer trust faster than long explanations.
persona-differentiation-lens|Persona Differentiation Lens|A lot of posters sound interchangeable because they never sharpen what makes them distinct.
debate-positioning-helper|Debate Positioning Helper|Online arguments are easier to win when you define the frame before defending the claim.
x-series-builder|X Series Builder|Recurring public series can create anticipation if the theme is strong enough.
reply-screenshot-harvester|Reply Screenshot Harvester|Great replies often become reusable proof and content artifacts outside the platform.
viral-opinion-splitter|Viral Opinion Splitter|A big idea often needs separate versions for supporters, skeptics, and bystanders.
social-capital-ledger|Social Capital Ledger|Public posting creates obligations, goodwill, and opportunity that deserve tracking.
timeline-cadence-planner|Timeline Cadence Planner|Post frequency matters because overposting and disappearing create different trust costs.
persona-endgame-planner|Persona Endgame Planner|People need to know what kind of identity they are actually compounding toward online.
"""),
    },
]


def _build_candidate(cluster: dict[str, Any], idea: dict[str, str]) -> dict[str, Any]:
    focus = idea["label"].lower()
    return {
        "cluster_id": cluster["cluster_id"],
        "label": idea["label"],
        "description": (
            f"{cluster['label']} workflow for {cluster['audience']} centered on {focus}, "
            "with a clear repeated decision and feedback loop."
        ),
        "specialization_surface": f"{focus} workflows for {cluster['audience']}",
        "mastery_surface": f"Turning {focus} into a repeatable advantage for {cluster['audience']}",
        "user_value_loop": cluster["loop_template"].format(focus=focus),
        "domain_tags": [cluster["cluster_id"], *cluster["tags"]],
        "evidence_sources": list(cluster["evidence_sources"]),
        "evidence_summary": idea["observation"],
        "adjacent_domains": list(cluster["seed_domains"]),
        "duplicate_aliases": [],
        "confidence_read": "high",
        "promotion_status": "curated_candidate",
        "raw_observation": idea["observation"],
        "domain_id": idea["slug"],
        "classification": "clear_domain_chip",
        "classification_reasons": [
            "Curated by the operator as part of a unique 500-domain frontier source set.",
            "Contains a concrete repeated specialization loop, mastery surface, and visible user-value cadence.",
        ],
    }


def _validate_curated_source(clusters: list[dict[str, Any]]) -> None:
    domain_ids: set[str] = set()
    labels: set[str] = set()
    for cluster in clusters:
        seen_in_cluster: set[str] = set()
        for idea in cluster["ideas"]:
            domain_id = idea["slug"]
            label = idea["label"]
            if domain_id in domain_ids:
                raise ValueError(f"Duplicate curated domain_id detected: {domain_id}")
            if label in labels:
                raise ValueError(f"Duplicate curated label detected: {label}")
            if domain_id in seen_in_cluster:
                raise ValueError(f"Duplicate domain_id inside cluster {cluster['cluster_id']}: {domain_id}")
            if domain_id.endswith(_BANNED_SUFFIXES):
                raise ValueError(f"Banned templated suffix detected in curated domain_id: {domain_id}")
            seen_in_cluster.add(domain_id)
            domain_ids.add(domain_id)
            labels.add(label)


def _round_robin_select(cluster_candidates: list[list[dict[str, Any]]], target_count: int) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    remaining = [list(items) for items in cluster_candidates]
    while len(selected) < target_count and any(remaining):
        for items in remaining:
            if items and len(selected) < target_count:
                selected.append(items.pop(0))
    return selected


def build_curated_frontier_packet(target_count: int = 500, profile: str = "hot_now") -> dict[str, Any]:
    """Build a hand-curated frontier source packet with real idea diversity."""
    if profile != "hot_now":
        raise ValueError(f"Unsupported curated frontier profile: {profile}")

    _validate_curated_source(_CURATED_CLUSTER_SPECS)
    cluster_candidates = [
        [_build_candidate(cluster, idea) for idea in cluster["ideas"]]
        for cluster in _CURATED_CLUSTER_SPECS
    ]

    full_count = sum(len(items) for items in cluster_candidates)
    limited_target = max(0, min(target_count, full_count))
    accepted = _round_robin_select(cluster_candidates, limited_target)

    counts_by_cluster: dict[str, int] = {}
    samples_by_cluster: dict[str, list[str]] = {}
    for candidate in accepted:
        cluster_id = candidate["cluster_id"]
        counts_by_cluster[cluster_id] = counts_by_cluster.get(cluster_id, 0) + 1
        samples_by_cluster.setdefault(cluster_id, []).append(candidate["domain_id"])

    cluster_summary: list[dict[str, Any]] = []
    for cluster in _CURATED_CLUSTER_SPECS:
        cluster_id = cluster["cluster_id"]
        cluster_summary.append({
            "cluster_id": cluster_id,
            "label": cluster["label"],
            "count": counts_by_cluster.get(cluster_id, 0),
            "seed_domains": list(cluster["seed_domains"]),
            "sample_domain_ids": samples_by_cluster.get(cluster_id, [])[:5],
        })

    return {
        "packet_kind": "mirofish_curated_frontier_packet",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "evidence_lane": "operator_curated_frontier",
        "profile": profile,
        "target_domain_count": limited_target,
        "summary": {
            "accepted_count": len(accepted),
            "cluster_count": len(_CURATED_CLUSTER_SPECS),
            "unique_idea_count": full_count,
            "banned_suffix_family_count": 0,
        },
        "cluster_summary": cluster_summary,
        "accepted_candidates": accepted,
        "governance_note": (
            "This packet is a hand-curated source pool for MiroFish selection. "
            "It is intentionally unique-idea first and avoids suffix-template family expansion."
        ),
    }


def format_curated_frontier_markdown(
    packet: dict[str, Any],
    title: str = "MiroFish Curated Frontier 500",
) -> str:
    """Render a concise markdown brief for a curated frontier packet."""
    lines = [
        f"# {title}",
        "",
        f"- Packet kind: `{packet.get('packet_kind', '')}`",
        f"- Profile: `{packet.get('profile', '')}`",
        f"- Accepted domains: `{packet.get('summary', {}).get('accepted_count', 0)}`",
        f"- Clusters: `{packet.get('summary', {}).get('cluster_count', 0)}`",
        f"- Unique source ideas: `{packet.get('summary', {}).get('unique_idea_count', 0)}`",
        "",
        "## Cluster Breakdown",
        "",
    ]
    for cluster in packet.get("cluster_summary", []):
        samples = ", ".join(f"`{item}`" for item in cluster.get("sample_domain_ids", [])) or "_none yet_"
        lines.append(f"- `{cluster.get('cluster_id', '')}`: {cluster.get('count', 0)} domains")
        lines.append(f"  Samples: {samples}")

    lines.extend([
        "",
        "## Next Actions",
        "",
        "- Run MiroFish selection on this curated 500-domain frontier instead of the synthetic frontier pool.",
        "- Keep the legacy graph UI as the primary simulator surface for reviewing which domains survive choice and retention.",
        "- Replace weak ideas only after inspecting the simulator output on this genuinely unique set.",
    ])
    return "\n".join(lines)
