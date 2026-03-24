"""Operator-curated frontier packet generation for MiroFish.

This module builds a hand-picked 500-domain source set around hot-now themes
so simulation can focus on selection instead of invention.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .discovery import canonicalize_raw_candidate


CURATED_FRONTIER_FORMATS = [
    {
        "label": "Copilot",
        "specialization_suffix": "guided recommendations, drafting, and execution help",
        "loop_suffix": "review suggestions, pick the best move, and reuse what works",
    },
    {
        "label": "Engine",
        "specialization_suffix": "automated scoring, ranking, and prioritization",
        "loop_suffix": "score inputs, rank the best options, and refresh the leaderboard",
    },
    {
        "label": "Loop",
        "specialization_suffix": "repeatable operating cadence and feedback capture",
        "loop_suffix": "run the loop, learn from the outcome, and tighten the next cycle",
    },
    {
        "label": "Lab",
        "specialization_suffix": "structured testing, comparison, and experiment tracking",
        "loop_suffix": "test variants, compare outcomes, and promote the winners",
    },
    {
        "label": "OS",
        "specialization_suffix": "one place to run the full recurring workflow",
        "loop_suffix": "capture inputs, route the work, and keep the operating system updated",
    },
]


CURATED_FRONTIER_CLUSTERS: list[dict[str, Any]] = [
    {
        "cluster_id": "creator-growth-systems",
        "label": "Creator Growth Systems",
        "focus": "High-frequency creator loops around hooks, packaging, audience growth, monetization, and launch rituals.",
        "audience": "creators, operators, and growth-minded media teams",
        "seed_domains": ["tiktok-creator", "xcontent", "youtube-remixer"],
        "domain_tags": ["viral", "creator", "attention"],
        "evidence_sources": ["x_twitter", "community", "producthunt"],
        "subjects": [
            {"label": "Hook Angle Test", "surface": "testing hooks and opening lines", "value_loop": "collect draft hooks and compare retention", "observation": "Creators obsess over hooks because that first line decides whether the post lives or dies."},
            {"label": "Thumbnail Package", "surface": "iterating titles and thumbnail packages", "value_loop": "draft packages, review click winners, and reuse the best patterns", "observation": "The thumbnail and title package often matters more than the raw clip."},
            {"label": "Clip Calendar", "surface": "planning clip drops across platforms", "value_loop": "schedule clips, watch performance, and rebalance the calendar", "observation": "Creators need a rhythm for posting clips instead of improvising every day."},
            {"label": "Comment Signal", "surface": "turning comments into content prompts and offers", "value_loop": "mine comments, cluster demand, and ship the next post", "observation": "Comments reveal what the audience wants more clearly than abstract brainstorming."},
            {"label": "Brand Deal Fit", "surface": "matching sponsorships to audience taste and creator style", "value_loop": "score deals, shortlist fits, and learn from campaign outcomes", "observation": "Most creators waste time on deals that damage trust or underpay."},
            {"label": "Collab Pipeline", "surface": "finding and sequencing creator collaborations", "value_loop": "source creators, prep collabs, and reuse outreach that converts", "observation": "Collabs compound growth when they are treated like a repeatable pipeline."},
            {"label": "Membership Flywheel", "surface": "turning casual followers into paid members", "value_loop": "shape offers, run launches, and keep the membership sticky", "observation": "Membership revenue needs a repeatable ladder, not one-off hype."},
            {"label": "Trend Riff Response", "surface": "turning live trends into on-brand creator riffs", "value_loop": "spot trends, draft riffs, and publish before the window closes", "observation": "Creators win by responding fast without sounding like everyone else."},
            {"label": "Series Planning", "surface": "building recurring content series that people come back for", "value_loop": "plan arcs, publish episodes, and track which series hold attention", "observation": "Series beat one-off posts when the creator wants repeat demand."},
            {"label": "Shopping Drop", "surface": "coordinating product drops, affiliate pushes, and storefront moments", "value_loop": "stage the drop, monitor conversion, and refine the next launch", "observation": "Commerce creators need drop discipline instead of random affiliate spam."},
        ],
    },
    {
        "cluster_id": "gaming-npc-community",
        "label": "Gaming / NPC / Community Worlds",
        "focus": "Social gaming loops around servers, NPCs, guilds, UGC, tournaments, and streamer communities.",
        "audience": "gaming communities, server operators, creators, and mod-friendly studios",
        "seed_domains": ["ai-npc-dialog", "discord-community", "streamer-overlay-ai"],
        "domain_tags": ["viral", "gaming", "community"],
        "evidence_sources": ["x_twitter", "community", "github"],
        "subjects": [
            {"label": "NPC Quest Memory", "surface": "persistent NPC memory for quest and dialogue loops", "value_loop": "capture player actions, evolve the NPC state, and reuse the lore", "observation": "Players love NPCs that remember what happened instead of resetting every time."},
            {"label": "Guild Recruiting", "surface": "sourcing and qualifying new guild or clan members", "value_loop": "screen applicants, score fit, and keep the roster healthy", "observation": "Communities grow or die based on whether they can recruit the right people."},
            {"label": "Server Event Ops", "surface": "planning and running community events on Discord and game servers", "value_loop": "announce events, route signups, and learn which formats stick", "observation": "Community events work when the operator flow is tight and repeatable."},
            {"label": "Modpack Launch", "surface": "shipping modpacks and custom worlds without breaking the player experience", "value_loop": "assemble packs, test installs, and publish stable builds", "observation": "Modded communities need a real release process, not chaos."},
            {"label": "Clip Review", "surface": "spotting standout gameplay clips and sharing them fast", "value_loop": "collect clips, rank highlights, and post the best moments", "observation": "Clip loops drive community growth because everyone wants to be featured."},
            {"label": "Raid Prep", "surface": "coordinating raid roles, builds, and prep rituals", "value_loop": "assign roles, collect loadouts, and update prep checklists", "observation": "Raid groups repeat the same prep pain before every serious push."},
            {"label": "Economy Balance Patch", "surface": "monitoring in-game economy drift and patch effects", "value_loop": "watch inflation, test changes, and ship balance adjustments", "observation": "Game economies need ongoing operator tooling, especially for live communities."},
            {"label": "Roleplay Lore Thread", "surface": "keeping roleplay canon, character arcs, and shared lore coherent", "value_loop": "log events, resolve contradictions, and extend the world", "observation": "Roleplay communities thrive when the lore feels alive and organized."},
            {"label": "Tournament Watch Party", "surface": "turning tournaments into recurring community watch events", "value_loop": "collect match schedules, prep watch flows, and keep the chat energized", "observation": "Watch parties spread because they give communities a recurring social ritual."},
            {"label": "UGC Map Testing", "surface": "testing user-generated maps, modes, and game experiences before launch", "value_loop": "gather testers, compare feedback, and promote the best builds", "observation": "UGC scenes need better ways to separate real hits from noisy launches."},
        ],
    },
    {
        "cluster_id": "agentic-builders",
        "label": "AI Agent Builders",
        "focus": "Builder loops around agent orchestration, evals, handoffs, safety, memory, browser flows, and shipping.",
        "audience": "AI builders, agent operators, startup engineers, and technical founders",
        "seed_domains": ["ai-agent-builder", "mcp-server-builder", "cursor-copilot"],
        "domain_tags": ["builders", "ai-agents", "tools"],
        "evidence_sources": ["github", "x_twitter", "community"],
        "subjects": [
            {"label": "Spec To Ship Decomposition", "surface": "breaking big product asks into agent-ready execution slices", "value_loop": "split the spec, assign the work, and track what actually ships", "observation": "Builder teams want agents to handle real decomposition instead of shallow autocomplete."},
            {"label": "Agent Eval Triage", "surface": "finding which eval failures matter and which do not", "value_loop": "scan failures, prioritize fixes, and rerun the eval set", "observation": "Most agent teams drown in eval output and need triage, not more logs."},
            {"label": "Prompt Regression", "surface": "tracking prompt changes that quietly break working flows", "value_loop": "compare prompts, catch regressions, and restore the best behavior", "observation": "Prompt regressions waste time because they surface late and look random."},
            {"label": "Tool Permission Audit", "surface": "reviewing dangerous tool permissions across agents and environments", "value_loop": "scan permissions, flag risky paths, and approve the right boundaries", "observation": "As agents get more capable, permission boundaries become part of the product."},
            {"label": "Multi Agent Handoff", "surface": "managing work handoffs between planning, coding, research, and QA agents", "value_loop": "route ownership, preserve context, and resolve stale handoffs", "observation": "Multi-agent systems fail when handoffs are vague or badly timed."},
            {"label": "Workflow Replay", "surface": "replaying failed agent sessions to isolate where the workflow broke", "value_loop": "replay the run, mark breakpoints, and compare alternate decisions", "observation": "Replay is one of the fastest ways to debug agent systems honestly."},
            {"label": "Agent Memory Inspection", "surface": "seeing what an agent remembered, forgot, or overfit to", "value_loop": "inspect memory, prune noise, and promote the useful beliefs", "observation": "Memory systems feel magical until they start storing junk."},
            {"label": "MCP Launch", "surface": "shipping MCP servers and integrations without losing distribution quality", "value_loop": "package the server, verify integrations, and launch the docs", "observation": "Protocol-native tooling wins when the launch path is simple and credible."},
            {"label": "Browser Agent QA", "surface": "dogfooding agents that act inside real browser flows", "value_loop": "run the browser task, collect failures, and patch the weak steps", "observation": "Browser agents need QA loops closer to real user behavior."},
            {"label": "Agent Cost Governance", "surface": "controlling model spend, tool use, and task overrun across agent fleets", "value_loop": "track spend, cap overruns, and tune the expensive flows", "observation": "Teams want more agents, but they panic when the bill gets weird."},
        ],
    },
]

CURATED_FRONTIER_CLUSTERS.extend([
    {
        "cluster_id": "startup-founder-systems",
        "label": "Startup Founder Systems",
        "focus": "Founder loops around validation, launch, GTM, pricing, fundraising, hiring, and community traction.",
        "audience": "founders, startup teams, and operators building in public",
        "seed_domains": ["startup-yc", "indie-hacker", "agentic-marketing"],
        "domain_tags": ["startup", "founders", "growth"],
        "evidence_sources": ["x_twitter", "community", "producthunt"],
        "subjects": [
            {"label": "Idea Triage", "surface": "sorting product ideas by pain, timing, and founder fit", "value_loop": "collect ideas, rank them, and kill the weak ones quickly", "observation": "Founders waste weeks because every new idea feels exciting in the moment."},
            {"label": "Problem Interview Review", "surface": "scoring customer interview quality and extracting signals", "value_loop": "log interviews, tag pain, and reuse what converts into demand", "observation": "Problem interviews are only useful if the team can read them honestly."},
            {"label": "Launch Week Changelog", "surface": "turning every launch week into a repeatable content and release ritual", "value_loop": "ship updates, package proof, and keep launch momentum alive", "observation": "Startups with a launch rhythm compound distribution faster than quiet builders."},
            {"label": "Cold Start Distribution", "surface": "finding the first repeatable channels before the product has momentum", "value_loop": "test channels, log response, and double down on the few that move", "observation": "Cold start distribution is where most startups actually die."},
            {"label": "Pricing Call Review", "surface": "reviewing sales and pricing calls to tighten packaging and objections", "value_loop": "tag objections, test pricing, and adjust the pitch", "observation": "Pricing feels fuzzy until the team studies real call patterns."},
            {"label": "Investor Update Draft", "surface": "turning weekly progress into sharp investor and advisor updates", "value_loop": "collect wins, write the update, and follow up on asks", "observation": "Good update loops strengthen the network without becoming a chore."},
            {"label": "Waitlist Conversion", "surface": "turning hype and waitlists into committed users", "value_loop": "score signups, sequence outreach, and learn which users activate", "observation": "A big waitlist means little if nobody converts when the doors open."},
            {"label": "GTM Experiment Tracker", "surface": "running and comparing go-to-market experiments without losing the learning", "value_loop": "log the experiment, capture the result, and reuse the winning playbooks", "observation": "Founders repeat failed GTM ideas because they forget why they failed."},
            {"label": "Founder Hiring Score", "surface": "screening early hires for slope, ownership, and startup fit", "value_loop": "compare candidates, log references, and tighten the hiring rubric", "observation": "Early startup hiring is a status and survival game at the same time."},
            {"label": "Pivot Decision", "surface": "deciding when to persist, narrow, or pivot the startup thesis", "value_loop": "collect evidence, debate options, and commit to the next move", "observation": "Teams need a real pivot process instead of emotional swings."},
        ],
    },
    {
        "cluster_id": "productivity-builder-ops",
        "label": "Builder Productivity Systems",
        "focus": "Execution loops for shipping, planning, coordination, focus, routines, and async work.",
        "audience": "builders, operators, indie hackers, and ambitious teams",
        "seed_domains": ["cursor-copilot", "web-designer", "task-agent-ai"],
        "domain_tags": ["productivity", "builders", "execution"],
        "evidence_sources": ["x_twitter", "community", "github"],
        "subjects": [
            {"label": "Deep Work Sprint", "surface": "time-boxed work sprints that protect real maker time", "value_loop": "plan the sprint, execute the block, and review what got shipped", "observation": "Builders talk constantly about focus but rarely have systems that survive real life."},
            {"label": "Meeting To Tasks", "surface": "turning meetings into clean next steps without manual cleanup", "value_loop": "capture notes, route actions, and close the loop on ownership", "observation": "Most meeting pain is not the meeting itself but the messy aftermath."},
            {"label": "Personal Ops Review", "surface": "weekly operator reviews across tasks, projects, and energy", "value_loop": "scan the week, rank priorities, and reset the next cycle", "observation": "People want a founder-style weekly review for their own operating system."},
            {"label": "Weekly Reset", "surface": "resetting calendars, inboxes, tasks, and priorities every week", "value_loop": "clear noise, sort commitments, and start the week clean", "observation": "The weekly reset is a sticky ritual for high-agency people."},
            {"label": "Knowledge Inbox", "surface": "processing saved links, notes, clips, and loose ideas into useful systems", "value_loop": "capture inputs, tag the good stuff, and reuse the best insights", "observation": "People accumulate more digital clutter than they can metabolize."},
            {"label": "Task Debt Cleanup", "surface": "pruning stale tasks and reviving only what matters", "value_loop": "scan the backlog, cut dead work, and keep the list trustworthy", "observation": "Task debt kills momentum because nobody trusts their own system anymore."},
            {"label": "Calendar Energy Mapping", "surface": "aligning work blocks with energy, not just empty slots", "value_loop": "observe energy, place work, and learn which rhythms sustain output", "observation": "A calendar becomes a weapon when it reflects energy, not just appointments."},
            {"label": "Async Team Standup", "surface": "running async standups that actually keep teams aligned", "value_loop": "collect updates, surface blockers, and route follow-ups quickly", "observation": "Remote teams need better daily coordination without more meetings."},
            {"label": "Builder Habit Tracking", "surface": "tracking the habits that correlate with real shipping", "value_loop": "log habits, compare streaks, and reinforce what leads to output", "observation": "Builders like quantified self tools when they tie back to actual shipping."},
            {"label": "Shipping Ritual", "surface": "standardizing how projects move from messy idea to public launch", "value_loop": "prepare the ship list, publish, and review the outcome", "observation": "Shipping rituals work because they compress anxiety into a known pattern."},
        ],
    },
    {
        "cluster_id": "career-status-social-proof",
        "label": "Career / Status / Social Proof",
        "focus": "Career loops for resumes, interviews, portfolios, networking, proof, and promotion readiness.",
        "audience": "ambitious professionals, job switchers, and status-aware operators",
        "seed_domains": ["resume-ai", "linkedin-optimizer", "interview-prep-ai"],
        "domain_tags": ["career", "status", "social-proof"],
        "evidence_sources": ["x_twitter", "community", "producthunt"],
        "subjects": [
            {"label": "Resume Refresh", "surface": "rewriting resumes around current market expectations and proof", "value_loop": "update wins, repackage the story, and test interview response", "observation": "People constantly tweak resumes because hiring markets keep moving."},
            {"label": "LinkedIn Authority", "surface": "building a public profile that signals competence and momentum", "value_loop": "publish proof, tighten positioning, and watch who reaches out", "observation": "Career status increasingly compounds through public internet proof."},
            {"label": "Interview Story Bank", "surface": "building and refining reusable interview stories", "value_loop": "capture stories, rehearse them, and promote the ones that land", "observation": "Strong candidates repeat the same proven stories across many interviews."},
            {"label": "Offer Negotiation Prep", "surface": "preparing negotiation scripts, anchors, and decision frameworks", "value_loop": "collect leverage, rehearse the ask, and review the negotiation result", "observation": "Negotiation feels high stakes enough that people want structure, not vibes."},
            {"label": "Public Proof Portfolio", "surface": "turning projects and wins into visible proof of taste and capability", "value_loop": "collect artifacts, package the proof, and refresh the portfolio", "observation": "A portfolio is now a social proof machine, not just a gallery."},
            {"label": "Layoff Pivot Plan", "surface": "navigating layoffs or stalled careers into a sharper next move", "value_loop": "assess options, run outreach, and choose the strongest pivot", "observation": "Career volatility makes transition tooling emotionally and practically useful."},
            {"label": "Manager Update Draft", "surface": "writing clear status updates that improve visibility and trust", "value_loop": "capture wins, package updates, and track how they land internally", "observation": "Visibility is career leverage, but many people undersell their real output."},
            {"label": "Career Moat Mapping", "surface": "figuring out what makes a person unusually valuable in the market", "value_loop": "inventory strengths, test positioning, and sharpen the moat", "observation": "People want help defining a career edge they can actually defend."},
            {"label": "Freelance Credibility", "surface": "building trust signals for freelancers and consultants", "value_loop": "collect testimonials, package work, and improve close rates", "observation": "Independent talent wins more deals when the proof is easy to trust."},
            {"label": "Promotion Packet", "surface": "assembling the evidence, narrative, and manager alignment needed for promotion", "value_loop": "capture impact, shape the case, and time the push well", "observation": "Promotion cases are repeated internal sales processes."},
        ],
    },
])

CURATED_FRONTIER_CLUSTERS.extend([
    {
        "cluster_id": "developer-distribution-tools",
        "label": "Developer Distribution Tools",
        "focus": "Dev-facing growth loops around launches, docs, examples, community, and open-source distribution.",
        "audience": "developer tool founders, open-source maintainers, and devrel operators",
        "seed_domains": ["github-growth-ai", "devrel-copilot", "open-source-launch-ai"],
        "domain_tags": ["developers", "distribution", "launch"],
        "evidence_sources": ["github", "x_twitter", "community"],
        "subjects": [
            {"label": "Changelog To Launch", "surface": "turning changelogs into launches people actually notice", "value_loop": "collect changes, package the story, and ship the update publicly", "observation": "Many great dev tools disappear because nobody packages each release well."},
            {"label": "Repo Positioning", "surface": "making GitHub repos legible, desirable, and easy to trust", "value_loop": "refresh the README, sharpen proof, and compare conversion", "observation": "The repo page is often the real landing page for developer products."},
            {"label": "Docs Funnel Review", "surface": "finding where docs lose developers before activation", "value_loop": "track doc paths, compare drop-off, and fix the weak steps", "observation": "Documentation is a growth surface, not just a support asset."},
            {"label": "Open Source Release Cadence", "surface": "running repeatable releases without losing community momentum", "value_loop": "prepare the release, package the updates, and watch contributor response", "observation": "Sustained open-source attention comes from cadence, not just code quality."},
            {"label": "API Landing Page", "surface": "improving API pages that need to convert skeptical technical users", "value_loop": "compare messaging, tighten examples, and reuse what drives signups", "observation": "Developer landing pages win when they feel credible in under a minute."},
            {"label": "Community Seeding", "surface": "starting and nurturing early developer communities around a tool", "value_loop": "source conversations, answer pain, and promote the strongest community rituals", "observation": "A dev tool with a real community gets stronger distribution over time."},
            {"label": "Example App Pack", "surface": "shipping example apps and starter repos that accelerate adoption", "value_loop": "publish examples, track reuse, and expand the winning patterns", "observation": "Examples often convert better than polished marketing copy."},
            {"label": "Integration Storytelling", "surface": "showing how a tool fits into real stacks and workflows", "value_loop": "package integrations, share use cases, and learn what resonates", "observation": "Developers adopt faster when they can see the tool inside their stack."},
            {"label": "Product Hunt Build", "surface": "turning launches into durable developer distribution instead of one-day spikes", "value_loop": "prep the launch, gather proof, and retain the users who show up", "observation": "Launches matter more when they feed a longer dev-distribution loop."},
            {"label": "DevRel Content Funnel", "surface": "building a repeatable devrel content system that feeds product adoption", "value_loop": "plan topics, publish tutorials, and tie content back to activation", "observation": "Developer education is a recurring distribution engine when run deliberately."},
        ],
    },
])


def build_curated_frontier_packet(
    target_count: int = 500,
    profile: str = "hot_now",
) -> dict[str, Any]:
    """Build a hand-curated frontier packet to use as the simulator's source set."""
    if profile != "hot_now":
        raise ValueError("Only the `hot_now` curated frontier profile is currently supported.")

    candidates_by_cluster: list[list[dict[str, Any]]] = []
    for cluster in CURATED_FRONTIER_CLUSTERS:
        cluster_candidates: list[dict[str, Any]] = []
        for subject in cluster["subjects"]:
            for format_spec in CURATED_FRONTIER_FORMATS:
                candidate = canonicalize_raw_candidate({
                    "label": f"{subject['label']} {format_spec['label']}",
                    "description": (
                        f"{cluster['label']} workflow for {cluster['audience']} centered on {subject['surface']}, "
                        f"with {format_spec['specialization_suffix']}."
                    ),
                    "specialization_surface": (
                        f"{subject['surface']} for {cluster['audience']}, with {format_spec['specialization_suffix']}"
                    ),
                    "mastery_surface": (
                        f"Turning {subject['surface']} into a repeatable advantage for {cluster['audience']}"
                    ),
                    "user_value_loop": f"{subject['value_loop']}, then {format_spec['loop_suffix']}",
                    "domain_tags": [cluster["cluster_id"], *cluster.get("domain_tags", [])],
                    "evidence_sources": list(cluster.get("evidence_sources", [])),
                    "evidence_summary": subject["observation"],
                    "adjacent_domains": list(cluster.get("seed_domains", [])),
                    "duplicate_aliases": [],
                    "confidence_read": "high",
                    "promotion_status": "curated_candidate",
                    "raw_observation": subject["observation"],
                })
                candidate["classification"] = "clear_domain_chip"
                candidate["classification_reasons"] = [
                    "Curated by the operator as part of the hand-built hot-now frontier.",
                    "Contains a repeated specialization loop, mastery loop, and obvious user-value cadence.",
                ]
                cluster_candidates.append(candidate)
        candidates_by_cluster.append(cluster_candidates)

    selected = _slice_curated_frontier_candidates(candidates_by_cluster, target_count=target_count)
    selected_map: dict[str, list[dict[str, Any]]] = {}
    for candidate in selected:
        selected_map.setdefault(_primary_cluster_tag(candidate), []).append(candidate)

    cluster_summary = [
        {
            "cluster_id": cluster["cluster_id"],
            "label": cluster["label"],
            "count": len(selected_map.get(cluster["cluster_id"], [])),
            "seed_domains": list(cluster.get("seed_domains", [])),
            "sample_domain_ids": [
                item["domain_id"] for item in selected_map.get(cluster["cluster_id"], [])[:5]
            ],
        }
        for cluster in CURATED_FRONTIER_CLUSTERS
    ]

    return {
        "packet_kind": "mirofish_curated_frontier_packet",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "evidence_lane": "operator_curated_frontier",
        "profile": profile,
        "target_domain_count": target_count,
        "summary": {
            "accepted_count": len(selected),
            "cluster_count": len(cluster_summary),
            "format_count_per_subject": len(CURATED_FRONTIER_FORMATS),
            "subject_count": sum(len(cluster["subjects"]) for cluster in CURATED_FRONTIER_CLUSTERS),
        },
        "cluster_summary": cluster_summary,
        "accepted_candidates": selected,
        "merged_candidates": [],
        "rejected_candidates": [],
        "governance_note": (
            "This packet is operator-curated. It is meant to be the source set that MiroFish selects from, "
            "instead of relying on a synthetic broad-agent discovery pool."
        ),
        "next_actions": [
            "Run MiroFish selection on this curated 500-domain frontier instead of the synthetic 1000-agent frontier.",
            "Use the legacy graph UI to inspect which curated domains survive choice and retention.",
            "Trim or replace weak themes only after reviewing simulator outcomes on the curated set.",
        ],
    }


def format_curated_frontier_markdown(packet: dict[str, Any], title: str = "MiroFish Curated Frontier 500") -> str:
    """Render the curated frontier packet as operator-facing markdown."""
    lines = [
        f"# {title}",
        "",
        f"- Packet kind: `{packet.get('packet_kind', 'unknown')}`",
        f"- Profile: `{packet.get('profile', 'unknown')}`",
        f"- Accepted domains: `{packet.get('summary', {}).get('accepted_count', 0)}`",
        f"- Clusters: `{packet.get('summary', {}).get('cluster_count', 0)}`",
        "",
        "## Cluster Breakdown",
        "",
    ]
    for cluster in packet.get("cluster_summary", []):
        lines.append(f"- `{cluster['cluster_id']}`: {cluster['count']} domains")
        samples = ", ".join(f"`{domain_id}`" for domain_id in cluster.get("sample_domain_ids", []))
        if samples:
            lines.append(f"  Samples: {samples}")
    lines.extend([
        "",
        "## Next Actions",
        "",
    ])
    for action in packet.get("next_actions", []):
        lines.append(f"- {action}")
    return "\n".join(lines).rstrip() + "\n"


def _slice_curated_frontier_candidates(
    candidates_by_cluster: list[list[dict[str, Any]]],
    target_count: int,
) -> list[dict[str, Any]]:
    """Keep frontier selection diverse if the operator asks for fewer than the full 500."""
    selected: list[dict[str, Any]] = []
    max_cluster_size = max((len(cluster) for cluster in candidates_by_cluster), default=0)
    for index in range(max_cluster_size):
        for cluster in candidates_by_cluster:
            if len(selected) >= target_count:
                return selected
            if index < len(cluster):
                selected.append(cluster[index])
    return selected


def _primary_cluster_tag(candidate: dict[str, Any]) -> str:
    """Return the first cluster tag from a curated frontier candidate."""
    tags = list(candidate.get("domain_tags", []))
    if not tags:
        return "untagged"
    return str(tags[0])

CURATED_FRONTIER_CLUSTERS.extend([
    {
        "cluster_id": "consumer-agent-utilities",
        "label": "Consumer Agent Utilities",
        "focus": "Useful consumer loops for planning, shopping, households, life admin, and everyday optimization.",
        "audience": "consumers who want leverage over everyday life admin and decisions",
        "seed_domains": ["trip-planner-ai", "shopping-deal-finder", "family-coordinator-ai"],
        "domain_tags": ["consumer", "utilities", "lifestyle"],
        "evidence_sources": ["community", "producthunt", "x_twitter"],
        "subjects": [
            {"label": "Weekend Trip Plan", "surface": "planning fast trips that balance cost, weather, and vibe", "value_loop": "collect constraints, build itineraries, and refine after the trip", "observation": "Travel planning is one of the clearest repeated personal-agent use cases."},
            {"label": "Household Chore Routing", "surface": "routing chores, reminders, and recurring home tasks", "value_loop": "assign tasks, track completion, and rebalance the routine", "observation": "Home coordination gets messy because nobody wants to be the human operating system."},
            {"label": "Grocery Price Rotation", "surface": "timing grocery buys, swaps, and bulk decisions around price drift", "value_loop": "watch prices, plan the list, and improve the next trip", "observation": "Households feel inflation every week and want a smarter loop."},
            {"label": "Personal Finance Reset", "surface": "resetting budgets, subscriptions, and spending leaks every month", "value_loop": "scan expenses, cut waste, and track how much changed", "observation": "Financial self-control gets easier when it becomes a recurring ritual."},
            {"label": "Parenting Schedule", "surface": "coordinating school, sports, routines, and childcare handoffs", "value_loop": "capture events, route responsibilities, and keep the week coherent", "observation": "Parenting ops are a real operating system problem."},
            {"label": "Apartment Hunt Filter", "surface": "sorting rental or housing options around commute, price, and fit", "value_loop": "compare listings, shortlist visits, and learn what matters most", "observation": "Housing search is a painful repeated evaluation loop with high stakes."},
            {"label": "Commute Optimizer", "surface": "choosing routes, times, and transport modes around changing conditions", "value_loop": "compare routes, test patterns, and lock in the better routine", "observation": "Daily commute decisions are repetitive enough to support a real agent."},
            {"label": "Subscription Cleanup", "surface": "finding and cancelling stale digital subscriptions and leak paths", "value_loop": "scan charges, rank waste, and confirm the cleanup", "observation": "People love obvious savings more than abstract finance coaching."},
            {"label": "Meal Rotation Planner", "surface": "running household meal rotations that fit time, taste, and budget", "value_loop": "build the week, adapt to constraints, and save the best plans", "observation": "Meal planning is boring enough that a strong utility can win quickly."},
            {"label": "Friend Hangout Planner", "surface": "turning vague social plans into actual outings that happen", "value_loop": "propose options, coordinate schedules, and save the formats people repeat", "observation": "The social friction is usually in coordination, not desire."},
        ],
    },
    {
        "cluster_id": "crypto-defi-trading",
        "label": "Crypto / DeFi / Trading",
        "focus": "Crypto-native loops around trading, onchain research, governance, airdrops, and token operations.",
        "audience": "crypto traders, researchers, governance participants, and onchain operators",
        "seed_domains": ["trading-crypto", "defi-architect", "onchain-research-ai"],
        "domain_tags": ["crypto", "defi", "trading"],
        "evidence_sources": ["x_twitter", "community", "github"],
        "subjects": [
            {"label": "Airdrop Hunting", "surface": "tracking protocols, tasks, and wallet activity tied to airdrop speculation", "value_loop": "score opportunities, execute tasks, and review which hunts paid off", "observation": "Airdrop hunting is one of the stickiest repeated crypto workflows."},
            {"label": "Yield Rotation", "surface": "comparing where capital should move as yields and risks change", "value_loop": "scan yields, rotate positions, and track the outcome", "observation": "Yield rotation is the cleanest repeatable DeFi operator loop."},
            {"label": "Governance Vote Brief", "surface": "summarizing governance proposals into fast decision briefs", "value_loop": "collect proposals, rank impact, and archive the decision quality", "observation": "Governance is noisy enough that people want compression, not more reading."},
            {"label": "Wallet Risk Review", "surface": "reviewing exposures, approvals, bridges, and wallet hygiene", "value_loop": "scan risks, revoke exposures, and keep the wallet clean", "observation": "Wallet ops are fragile and repeat often for active users."},
            {"label": "Onchain Narrative Radar", "surface": "spotting onchain themes before they fully hit the timeline", "value_loop": "track flows, cluster stories, and refresh the narrative map", "observation": "Crypto attention often rotates before most people notice why."},
            {"label": "Perp Position Review", "surface": "reviewing open perp trades for risk, funding, and momentum changes", "value_loop": "scan positions, adjust risk, and learn from the trade history", "observation": "Active traders want a discipline layer more than another signal firehose."},
            {"label": "Token Unlock Watch", "surface": "tracking vesting, unlocks, and supply events that move sentiment", "value_loop": "monitor calendars, prep decisions, and review the market reaction", "observation": "Unlock calendars are repeated attention points for serious traders."},
            {"label": "DAO Treasury Review", "surface": "helping DAOs understand runway, allocation, and treasury decisions", "value_loop": "review assets, model scenarios, and package recommendations", "observation": "DAO treasury work repeats but is still surprisingly manual."},
            {"label": "Smart Money Follow", "surface": "tracking wallets, moves, and thesis clusters from respected onchain actors", "value_loop": "watch wallets, compare moves, and score which signals matter", "observation": "People love following smart money but need cleaner filters."},
            {"label": "Liquidity Migration", "surface": "tracking when liquidity and users are moving between chains or venues", "value_loop": "watch flows, score migration, and act before the crowd", "observation": "Liquidity shifts are one of the clearest structural signals in crypto."},
        ],
    },
    {
        "cluster_id": "x-native-persona-tools",
        "label": "X-Native Persona Tools",
        "focus": "Public-internet loops around posting, replies, threads, clout, audience reading, and account resets.",
        "audience": "X-native founders, creators, operators, and people building in public",
        "seed_domains": ["xcontent", "personal-brand-ai", "reply-guy-ai"],
        "domain_tags": ["x-native", "social", "viral"],
        "evidence_sources": ["x_twitter", "community", "producthunt"],
        "subjects": [
            {"label": "Reply Ladder", "surface": "turning replies into consistent reach and relationship growth", "value_loop": "spot reply targets, draft responses, and monitor which replies travel", "observation": "A lot of growth on X still starts in replies, not in original posts."},
            {"label": "Post Hook Workshop", "surface": "refining post openings before they hit the timeline", "value_loop": "draft hooks, compare reactions, and save the best patterns", "observation": "Founders want a faster way to feel whether a post will land."},
            {"label": "Quote Tweet Opportunity", "surface": "finding the best quote-tweet moments without becoming generic", "value_loop": "scan live posts, draft responses, and reuse the winning frames", "observation": "Quote tweets are a social-leverage tool when the timing is sharp."},
            {"label": "Thread Packaging", "surface": "turning messy ideas into threads that feel native to X", "value_loop": "outline threads, package proofs, and track what earns saves", "observation": "Threads still work when they are concrete, sharp, and status-aware."},
            {"label": "DM To Call Routing", "surface": "turning inbound DMs into real conversations or deals", "value_loop": "score messages, route follow-up, and review close quality", "observation": "A lot of internet opportunities die in messy DMs."},
            {"label": "Mutual Map", "surface": "seeing who matters in the network and which relationships to deepen", "value_loop": "map connections, spot overlap, and act on the strongest ties", "observation": "People on X want leverage over their network, not just vanity metrics."},
            {"label": "Clout Calendar", "surface": "planning when to post around launches, events, and discourse waves", "value_loop": "mark moments, prepare content, and review which timing wins", "observation": "Public builders often win by timing, not by writing harder."},
            {"label": "Public Build Log", "surface": "running shipping-in-public as an operating system instead of random updates", "value_loop": "capture progress, publish proof, and build audience continuity", "observation": "Shipping in public compounds only when it becomes a rhythm."},
            {"label": "Audience Persona Mining", "surface": "reading who actually responds to the account and why", "value_loop": "cluster responders, spot audience shifts, and adjust the content", "observation": "Audience feel matters more than raw follower counts for many builders."},
            {"label": "Account Relaunch", "surface": "resetting a stale account with a sharper identity and posting cadence", "value_loop": "reposition the account, relaunch it, and review what traction returns", "observation": "Many people want a fresh start on X without losing their accumulated graph."},
        ],
    },
])
