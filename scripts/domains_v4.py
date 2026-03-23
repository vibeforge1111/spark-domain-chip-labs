"""MiroFish v4: 250 new domains (total portfolio: 500).

Fills critical gaps identified in v3 analysis:
- AI Survival Skills (people losing jobs to AI)
- Blue Collar / Physical World AI
- Healthcare & Medical
- Government / Civic Tech
- Enterprise / B2B Infrastructure
- Advanced Finance (Trad-Fi)
- Legal Tech
- Real Estate Tech
- Transportation & Logistics
- Education & Reskilling (2026 urgency)
- Defense & Security
- Senior / Accessibility
- Local Small Business
- Food & Agriculture
- Emerging Verticals

Each domain has v4 fields:
- retention_score (0-1): How habitual/sticky is this use case?
- urgency_score (0-1): How time-sensitive given 2026 macro context?
"""

from __future__ import annotations

from typing import Any


def _d(
    domain_id: str, label: str, composite: float,
    scores: dict[str, float], sources: list[str],
    tags: list[str], related: list[str] | None = None,
    retention: float = 0.5, urgency: float = 0.5,
    status: str = "candidate",
) -> dict[str, Any]:
    """Helper to construct a domain dict with v4 fields."""
    return {
        "domain_id": domain_id,
        "label": label,
        "composite_score": composite,
        "scores": scores,
        "evidence_sources": sources,
        "related_chips": related or [],
        "domain_tags": tags,
        "status": status,
        "retention_score": retention,
        "urgency_score": urgency,
    }


# Default score templates by category
_ai_surv = {"community_demand": 0.85, "data_availability": 0.6, "market_size": 0.8, "monetization_potential": 0.7, "benchmark_feasibility": 0.6, "spark_ecosystem_fit": 0.5}
_health = {"community_demand": 0.7, "data_availability": 0.5, "market_size": 0.85, "monetization_potential": 0.8, "benchmark_feasibility": 0.5, "spark_ecosystem_fit": 0.4}
_gov = {"community_demand": 0.5, "data_availability": 0.6, "market_size": 0.7, "monetization_potential": 0.6, "benchmark_feasibility": 0.5, "spark_ecosystem_fit": 0.4}
_enter = {"community_demand": 0.65, "data_availability": 0.7, "market_size": 0.8, "monetization_potential": 0.8, "benchmark_feasibility": 0.6, "spark_ecosystem_fit": 0.5}
_fintech = {"community_demand": 0.7, "data_availability": 0.75, "market_size": 0.8, "monetization_potential": 0.85, "benchmark_feasibility": 0.65, "spark_ecosystem_fit": 0.5}
_blue = {"community_demand": 0.6, "data_availability": 0.5, "market_size": 0.75, "monetization_potential": 0.65, "benchmark_feasibility": 0.5, "spark_ecosystem_fit": 0.35}
_legal = {"community_demand": 0.6, "data_availability": 0.6, "market_size": 0.7, "monetization_potential": 0.75, "benchmark_feasibility": 0.55, "spark_ecosystem_fit": 0.4}
_realestate = {"community_demand": 0.65, "data_availability": 0.6, "market_size": 0.8, "monetization_potential": 0.75, "benchmark_feasibility": 0.55, "spark_ecosystem_fit": 0.4}
_transport = {"community_demand": 0.6, "data_availability": 0.65, "market_size": 0.75, "monetization_potential": 0.7, "benchmark_feasibility": 0.55, "spark_ecosystem_fit": 0.35}
_food = {"community_demand": 0.6, "data_availability": 0.5, "market_size": 0.7, "monetization_potential": 0.65, "benchmark_feasibility": 0.5, "spark_ecosystem_fit": 0.35}
_senior = {"community_demand": 0.7, "data_availability": 0.5, "market_size": 0.75, "monetization_potential": 0.65, "benchmark_feasibility": 0.5, "spark_ecosystem_fit": 0.4}
_defense = {"community_demand": 0.5, "data_availability": 0.4, "market_size": 0.7, "monetization_potential": 0.8, "benchmark_feasibility": 0.4, "spark_ecosystem_fit": 0.3}
_local = {"community_demand": 0.75, "data_availability": 0.55, "market_size": 0.7, "monetization_potential": 0.7, "benchmark_feasibility": 0.55, "spark_ecosystem_fit": 0.45}
_emerging = {"community_demand": 0.55, "data_availability": 0.45, "market_size": 0.65, "monetization_potential": 0.7, "benchmark_feasibility": 0.4, "spark_ecosystem_fit": 0.35}

# ============================================================================
# AI SURVIVAL SKILLS (30 domains) - People facing AI displacement
# ============================================================================
AI_SURVIVAL_DOMAINS: list[dict[str, Any]] = [
    _d("resume-ai", "AI Resume Builder", 0.82, _ai_surv, ["community", "producthunt"], ["career", "reskill", "easy_start", "quick_wins"], retention=0.3, urgency=0.9),
    _d("career-pivot-ai", "AI Career Pivot Coach", 0.80, _ai_surv, ["community", "x_twitter"], ["career", "reskill", "ai_survival", "low_learning_curve"], retention=0.6, urgency=0.95),
    _d("layoff-preparation-ai", "Layoff Preparation Toolkit", 0.78, _ai_surv, ["community"], ["career", "ai_survival", "quick_wins", "time_leverage"], retention=0.3, urgency=0.95),
    _d("interview-prep-ai", "AI Interview Coach", 0.81, _ai_surv, ["community", "producthunt"], ["career", "reskill", "quick_wins", "outcompete"], retention=0.4, urgency=0.9),
    _d("linkedin-optimizer", "LinkedIn Profile Optimizer", 0.79, _ai_surv, ["community", "x_twitter"], ["career", "audience_growth", "easy_start"], retention=0.4, urgency=0.85),
    _d("upskill-path-ai", "AI Upskilling Path Planner", 0.80, _ai_surv, ["community", "github"], ["reskill", "career", "low_learning_curve", "productivity"], retention=0.7, urgency=0.9),
    _d("freelance-ai-coach", "Freelance AI Business Coach", 0.77, _ai_surv, ["community", "x_twitter"], ["career", "reskill", "roi", "time_leverage"], retention=0.5, urgency=0.8),
    _d("ai-skill-assessment", "AI Skills Gap Assessment", 0.76, _ai_surv, ["community"], ["reskill", "career", "quick_wins", "ai_survival"], retention=0.3, urgency=0.85),
    _d("remote-job-matcher", "AI Remote Job Matcher", 0.78, _ai_surv, ["community", "producthunt"], ["career", "easy_start", "speed"], retention=0.5, urgency=0.85),
    _d("salary-negotiator-ai", "AI Salary Negotiation Coach", 0.75, _ai_surv, ["community"], ["career", "roi", "outcompete"], retention=0.2, urgency=0.7),
    _d("ai-proof-career", "AI-Proof Career Planner", 0.82, _ai_surv, ["community", "x_twitter"], ["career", "ai_survival", "reskill", "low_learning_curve"], retention=0.6, urgency=0.95),
    _d("coding-bootcamp-ai", "AI Coding Bootcamp", 0.80, _ai_surv, ["community", "github"], ["reskill", "code_quality", "easy_start", "career"], retention=0.7, urgency=0.85),
    _d("ai-literacy-course", "AI Literacy for Non-Tech", 0.79, _ai_surv, ["community"], ["reskill", "easy_start", "low_learning_curve", "ai_survival"], retention=0.5, urgency=0.9),
    _d("portfolio-builder-ai", "AI Project Portfolio Builder", 0.77, _ai_surv, ["community", "github"], ["career", "reskill", "speed_to_ship", "outcompete"], retention=0.4, urgency=0.8),
    _d("gig-economy-ai", "Gig Economy AI Optimizer", 0.74, _ai_surv, ["community"], ["career", "roi", "time_leverage", "quick_wins"], retention=0.6, urgency=0.8),
    _d("human-skills-trainer", "Human Skills Differentiator", 0.78, _ai_surv, ["community", "x_twitter"], ["career", "ai_survival", "outcompete", "creative_control"], retention=0.6, urgency=0.85),
    _d("ai-collaboration-coach", "AI Collaboration Skills", 0.77, _ai_surv, ["community"], ["reskill", "productivity", "easy_start"], retention=0.5, urgency=0.8),
    _d("creative-differentiator", "Creative AI Differentiator", 0.76, _ai_surv, ["community", "x_twitter"], ["creative_control", "ai_survival", "outcompete", "uniqueness"], retention=0.5, urgency=0.8),
    _d("trade-skill-ai", "Trades & Manual Skill AI", 0.73, _ai_surv, ["community"], ["reskill", "career", "ai_survival", "infrastructure"], retention=0.5, urgency=0.75),
    _d("ai-mentor-matcher", "AI Mentor Matching", 0.75, _ai_surv, ["community"], ["career", "reskill", "easy_start"], retention=0.5, urgency=0.7),
    _d("side-hustle-ai", "AI Side Hustle Finder", 0.77, _ai_surv, ["community", "x_twitter"], ["career", "roi", "quick_wins", "speed"], retention=0.4, urgency=0.85),
    _d("ai-certification-prep", "AI Certification Prep", 0.78, _ai_surv, ["community"], ["reskill", "career", "outcompete", "low_learning_curve"], retention=0.4, urgency=0.8),
    _d("workplace-ai-trainer", "Workplace AI Integration", 0.76, _ai_surv, ["community"], ["productivity", "reskill", "easy_start", "compliance"], retention=0.6, urgency=0.8),
    _d("ai-writing-for-jobs", "AI Writing for Job Apps", 0.79, _ai_surv, ["community", "producthunt"], ["career", "easy_start", "quick_wins", "content_quality"], retention=0.3, urgency=0.9),
    _d("tech-transition-ai", "Non-Tech to Tech AI Bridge", 0.80, _ai_surv, ["community"], ["reskill", "career", "ai_survival", "low_learning_curve"], retention=0.6, urgency=0.9),
    _d("ai-tutoring-income", "AI Tutoring Income Stream", 0.74, _ai_surv, ["community"], ["career", "roi", "easy_start", "reskill"], retention=0.5, urgency=0.75),
    _d("prompt-job-skills", "Prompt Engineering for Jobs", 0.81, _ai_surv, ["community", "github"], ["reskill", "career", "outcompete", "productivity"], retention=0.5, urgency=0.85),
    _d("ai-entrepreneurship", "AI Entrepreneurship 101", 0.78, _ai_surv, ["community", "x_twitter"], ["career", "speed_to_ship", "reskill", "market_fit"], retention=0.5, urgency=0.8),
    _d("automation-proof-role", "Automation-Proof Role Design", 0.76, _ai_surv, ["community"], ["career", "ai_survival", "infrastructure", "compliance"], retention=0.5, urgency=0.85),
    _d("ai-networking-tool", "AI Professional Networking", 0.74, _ai_surv, ["community", "x_twitter"], ["career", "audience_growth", "easy_start"], retention=0.4, urgency=0.7),
]

# ============================================================================
# HEALTHCARE & MEDICAL (25 domains)
# ============================================================================
HEALTHCARE_DOMAINS: list[dict[str, Any]] = [
    _d("ai-therapy-companion", "AI Therapy Companion", 0.78, _health, ["community", "producthunt"], ["easy_start", "low_learning_curve", "quick_wins"], retention=0.8, urgency=0.8),
    _d("anxiety-management-ai", "AI Anxiety Management", 0.76, _health, ["community"], ["easy_start", "quick_wins", "low_learning_curve"], retention=0.7, urgency=0.8),
    _d("telemedicine-builder", "Telemedicine Platform Builder", 0.77, _health, ["github", "community"], ["infrastructure", "compliance", "roi"], retention=0.7, urgency=0.7),
    _d("medical-coding-ai", "AI Medical Coding & Billing", 0.79, _health, ["community"], ["productivity", "compliance", "roi", "time_leverage"], retention=0.8, urgency=0.6),
    _d("patient-engagement-ai", "Patient Engagement AI", 0.75, _health, ["community"], ["audience_growth", "roi", "simplicity"], retention=0.7, urgency=0.6),
    _d("clinical-decision-ai", "Clinical Decision Support", 0.74, _health, ["arxiv", "community"], ["infrastructure", "compliance", "code_quality"], retention=0.8, urgency=0.5),
    _d("health-insurance-nav", "Health Insurance Navigator AI", 0.76, _health, ["community"], ["easy_start", "roi", "simplicity", "compliance"], retention=0.5, urgency=0.7),
    _d("mental-health-chatbot", "Mental Health Chatbot Builder", 0.77, _health, ["community", "github"], ["easy_start", "infrastructure", "compliance"], retention=0.6, urgency=0.8),
    _d("pharmacy-optimizer", "Pharmacy Workflow Optimizer", 0.73, _health, ["community"], ["productivity", "compliance", "roi", "time_leverage"], retention=0.8, urgency=0.5),
    _d("fitness-ai-coach", "AI Fitness Coach", 0.78, _health, ["community", "producthunt"], ["easy_start", "quick_wins", "low_learning_curve"], retention=0.7, urgency=0.5),
    _d("nutrition-planner-ai", "AI Nutrition Planner Pro", 0.75, _health, ["community"], ["easy_start", "quick_wins", "simplicity"], retention=0.7, urgency=0.5),
    _d("sleep-optimizer-ai", "AI Sleep Optimizer", 0.74, _health, ["community", "producthunt"], ["easy_start", "quick_wins", "low_learning_curve"], retention=0.6, urgency=0.5),
    _d("caregiver-ai", "AI Caregiver Support", 0.73, _health, ["community"], ["easy_start", "time_leverage", "simplicity", "low_learning_curve"], retention=0.7, urgency=0.7),
    _d("health-data-analyst", "Health Data Analytics", 0.74, _health, ["github", "community"], ["infrastructure", "roi", "code_quality"], retention=0.7, urgency=0.5),
    _d("addiction-recovery-ai", "AI Addiction Recovery Coach", 0.72, _health, ["community"], ["easy_start", "low_learning_curve", "compliance"], retention=0.7, urgency=0.7),
    _d("burnout-detector-ai", "AI Burnout Detection", 0.76, _health, ["community", "x_twitter"], ["productivity", "quick_wins", "easy_start", "ai_survival"], retention=0.5, urgency=0.85),
    _d("medical-research-ai", "Medical Research Assistant", 0.73, _health, ["arxiv", "github"], ["code_quality", "infrastructure", "productivity"], retention=0.7, urgency=0.5),
    _d("chronic-disease-mgr", "Chronic Disease Manager AI", 0.74, _health, ["community"], ["easy_start", "compliance", "simplicity"], retention=0.85, urgency=0.6),
    _d("drug-interaction-ai", "Drug Interaction Checker AI", 0.75, _health, ["arxiv", "community"], ["compliance", "infrastructure", "quick_wins"], retention=0.6, urgency=0.5),
    _d("fertility-tracker-ai", "AI Fertility Tracker", 0.72, _health, ["community", "producthunt"], ["easy_start", "simplicity"], retention=0.8, urgency=0.5),
    _d("pt-exercise-ai", "Physical Therapy Exercise AI", 0.73, _health, ["community"], ["easy_start", "quick_wins", "low_learning_curve"], retention=0.6, urgency=0.5),
    _d("healthcare-compliance", "Healthcare Compliance AI", 0.76, _health, ["community"], ["compliance", "audit", "infrastructure", "roi"], retention=0.8, urgency=0.6),
    _d("symptom-checker-ai", "AI Symptom Checker", 0.77, _health, ["community", "producthunt"], ["easy_start", "quick_wins", "low_learning_curve"], retention=0.4, urgency=0.6),
    _d("elderly-health-monitor", "Elderly Health Monitor AI", 0.73, _health, ["community"], ["easy_start", "simplicity", "infrastructure"], retention=0.8, urgency=0.7),
    _d("therapist-note-ai", "AI Therapist Note Taker", 0.74, _health, ["community"], ["productivity", "compliance", "time_leverage"], retention=0.8, urgency=0.5),
]

# ============================================================================
# GOVERNMENT & CIVIC (15 domains)
# ============================================================================
GOVERNMENT_DOMAINS: list[dict[str, Any]] = [
    _d("city-planning-ai", "City Planning AI", 0.70, _gov, ["community", "arxiv"], ["infrastructure", "compliance", "roi"], retention=0.7, urgency=0.5),
    _d("emergency-response-ai", "Emergency Response AI", 0.72, _gov, ["community"], ["infrastructure", "speed", "compliance"], retention=0.7, urgency=0.6),
    _d("public-records-ai", "Public Records Analysis AI", 0.68, _gov, ["community"], ["productivity", "compliance", "audit"], retention=0.5, urgency=0.4),
    _d("grant-navigator-ai", "Government Grant Navigator", 0.75, _gov, ["community"], ["roi", "easy_start", "quick_wins", "compliance"], retention=0.4, urgency=0.7),
    _d("policy-analyzer-ai", "AI Policy Analyzer", 0.69, _gov, ["community", "arxiv"], ["compliance", "audit", "infrastructure"], retention=0.5, urgency=0.5),
    _d("civic-engagement-ai", "Civic Engagement Platform", 0.67, _gov, ["community", "x_twitter"], ["audience_growth", "easy_start", "simplicity"], retention=0.4, urgency=0.5),
    _d("voting-info-ai", "Voting Information Assistant", 0.66, _gov, ["community"], ["easy_start", "simplicity", "compliance"], retention=0.3, urgency=0.6),
    _d("municipal-services-ai", "Municipal Services Optimizer", 0.68, _gov, ["community"], ["infrastructure", "roi", "time_leverage"], retention=0.7, urgency=0.4),
    _d("tax-filing-ai", "AI Tax Filing Assistant", 0.77, _gov, ["community", "producthunt"], ["easy_start", "roi", "compliance", "quick_wins"], retention=0.4, urgency=0.8),
    _d("permit-navigator-ai", "Building Permit Navigator", 0.70, _gov, ["community"], ["compliance", "time_leverage", "easy_start"], retention=0.3, urgency=0.5),
    _d("public-safety-ai", "Public Safety Analytics", 0.69, _gov, ["community"], ["infrastructure", "compliance", "audit"], retention=0.6, urgency=0.5),
    _d("disaster-prep-ai", "Disaster Preparedness AI", 0.71, _gov, ["community"], ["easy_start", "infrastructure", "compliance"], retention=0.4, urgency=0.6),
    _d("immigration-assist-ai", "Immigration Process AI", 0.73, _gov, ["community"], ["compliance", "easy_start", "simplicity"], retention=0.4, urgency=0.8),
    _d("environmental-monitor", "Environmental Monitor AI", 0.68, _gov, ["community", "arxiv"], ["infrastructure", "compliance", "audit"], retention=0.6, urgency=0.5),
    _d("transparency-audit-ai", "Government Transparency AI", 0.67, _gov, ["community", "x_twitter"], ["audit", "compliance", "infrastructure"], retention=0.4, urgency=0.5),
]

# ============================================================================
# ENTERPRISE & B2B (25 domains)
# ============================================================================
ENTERPRISE_DOMAINS: list[dict[str, Any]] = [
    _d("supply-chain-ai", "Supply Chain Intelligence", 0.78, _enter, ["community", "github"], ["infrastructure", "roi", "time_leverage"], retention=0.8, urgency=0.6),
    _d("procurement-ai", "AI Procurement Optimizer", 0.75, _enter, ["community"], ["roi", "time_leverage", "compliance"], retention=0.7, urgency=0.5),
    _d("vendor-management-ai", "Vendor Management AI", 0.73, _enter, ["community"], ["roi", "compliance", "infrastructure"], retention=0.7, urgency=0.5),
    _d("enterprise-search-ai", "Enterprise Knowledge Search", 0.79, _enter, ["community", "github"], ["productivity", "infrastructure", "time_leverage"], retention=0.8, urgency=0.6),
    _d("it-asset-manager-ai", "IT Asset Management AI", 0.72, _enter, ["community"], ["infrastructure", "roi", "compliance", "audit"], retention=0.7, urgency=0.5),
    _d("change-management-ai", "Change Management AI", 0.71, _enter, ["community"], ["productivity", "infrastructure", "roi"], retention=0.5, urgency=0.5),
    _d("business-continuity-ai", "Business Continuity Planner", 0.73, _enter, ["community"], ["infrastructure", "compliance", "audit", "roi"], retention=0.5, urgency=0.6),
    _d("hr-analytics-ai", "HR Analytics & Retention AI", 0.76, _enter, ["community", "producthunt"], ["roi", "productivity", "infrastructure"], retention=0.7, urgency=0.7),
    _d("employee-onboarding-ai", "AI Employee Onboarding", 0.74, _enter, ["community"], ["easy_start", "productivity", "time_leverage"], retention=0.6, urgency=0.5),
    _d("corporate-training-ai", "Corporate AI Training", 0.77, _enter, ["community"], ["reskill", "productivity", "roi", "compliance"], retention=0.6, urgency=0.8),
    _d("board-deck-ai", "Board Deck Generator AI", 0.73, _enter, ["community", "producthunt"], ["productivity", "roi", "speed"], retention=0.4, urgency=0.5),
    _d("competitive-intel-ai", "Competitive Intelligence AI", 0.76, _enter, ["community", "x_twitter"], ["alpha", "roi", "speed"], retention=0.6, urgency=0.6),
    _d("sop-generator-ai", "SOP & Process Doc AI", 0.74, _enter, ["community", "producthunt"], ["productivity", "compliance", "time_leverage", "simplicity"], retention=0.5, urgency=0.5),
    _d("enterprise-chatbot-ai", "Enterprise Chatbot Builder", 0.77, _enter, ["community", "github"], ["infrastructure", "productivity", "roi"], retention=0.7, urgency=0.6),
    _d("data-governance-ai", "Data Governance & Privacy AI", 0.75, _enter, ["community"], ["compliance", "audit", "infrastructure"], retention=0.7, urgency=0.7),
    _d("contract-review-ai", "AI Contract Review", 0.78, _enter, ["community", "producthunt"], ["compliance", "roi", "time_leverage", "audit"], retention=0.6, urgency=0.6),
    _d("risk-assessment-ai", "Enterprise Risk Assessment", 0.74, _enter, ["community"], ["compliance", "audit", "infrastructure", "roi"], retention=0.6, urgency=0.6),
    _d("meeting-summarizer-ai", "Meeting Summarizer Pro", 0.79, _enter, ["community", "producthunt"], ["productivity", "time_leverage", "easy_start", "quick_wins"], retention=0.8, urgency=0.5),
    _d("knowledge-base-ai", "AI Knowledge Base Builder", 0.76, _enter, ["community", "github"], ["infrastructure", "productivity", "dx"], retention=0.8, urgency=0.5),
    _d("sales-enablement-ai", "AI Sales Enablement", 0.77, _enter, ["community", "producthunt"], ["roi", "conversion", "speed"], retention=0.6, urgency=0.6),
    _d("customer-success-ai", "Customer Success AI", 0.75, _enter, ["community"], ["roi", "conversion", "time_leverage"], retention=0.7, urgency=0.5),
    _d("internal-comms-ai", "Internal Communications AI", 0.72, _enter, ["community"], ["productivity", "simplicity", "easy_start"], retention=0.5, urgency=0.4),
    _d("workspace-analytics", "Workspace Productivity Analytics", 0.73, _enter, ["community"], ["productivity", "roi", "infrastructure"], retention=0.6, urgency=0.5),
    _d("talent-acquisition-ai", "AI Talent Acquisition", 0.76, _enter, ["community", "producthunt"], ["roi", "speed", "productivity"], retention=0.6, urgency=0.7),
    _d("expense-management-ai", "AI Expense Management", 0.74, _enter, ["community"], ["roi", "compliance", "time_leverage", "easy_start"], retention=0.7, urgency=0.5),
]

# ============================================================================
# BLUE COLLAR & PHYSICAL WORLD (20 domains)
# ============================================================================
BLUE_COLLAR_DOMAINS: list[dict[str, Any]] = [
    _d("construction-ai", "Construction Project AI", 0.72, _blue, ["community"], ["infrastructure", "roi", "time_leverage", "compliance"], retention=0.7, urgency=0.5),
    _d("farming-ai", "Smart Farming AI", 0.70, _blue, ["community", "arxiv"], ["infrastructure", "roi", "productivity"], retention=0.7, urgency=0.5),
    _d("fleet-manager-ai", "Fleet Management AI", 0.73, _blue, ["community"], ["roi", "time_leverage", "infrastructure", "speed"], retention=0.8, urgency=0.5),
    _d("warehouse-optimizer", "Warehouse Optimization AI", 0.72, _blue, ["community"], ["roi", "productivity", "infrastructure", "speed"], retention=0.8, urgency=0.5),
    _d("predictive-maintenance", "Predictive Maintenance AI", 0.74, _blue, ["community", "github"], ["infrastructure", "roi", "productivity"], retention=0.8, urgency=0.5),
    _d("quality-inspection-ai", "Quality Inspection AI", 0.71, _blue, ["community"], ["infrastructure", "compliance", "roi"], retention=0.7, urgency=0.5),
    _d("field-service-ai", "Field Service Management AI", 0.72, _blue, ["community"], ["time_leverage", "roi", "infrastructure", "speed"], retention=0.7, urgency=0.5),
    _d("hvac-optimizer-ai", "HVAC System Optimizer", 0.69, _blue, ["community"], ["roi", "infrastructure", "simplicity"], retention=0.7, urgency=0.4),
    _d("plumbing-estimator-ai", "Plumbing Estimate AI", 0.67, _blue, ["community"], ["roi", "quick_wins", "easy_start", "simplicity"], retention=0.4, urgency=0.4),
    _d("electrician-helper-ai", "Electrician Helper AI", 0.68, _blue, ["community"], ["easy_start", "compliance", "simplicity", "quick_wins"], retention=0.4, urgency=0.4),
    _d("landscaping-planner-ai", "Landscaping Planner AI", 0.66, _blue, ["community"], ["easy_start", "creative_control", "simplicity"], retention=0.4, urgency=0.3),
    _d("iot-device-manager", "IoT Device Manager", 0.74, _blue, ["github", "community"], ["infrastructure", "code_quality", "dx"], retention=0.7, urgency=0.5),
    _d("smart-home-builder", "Smart Home Orchestration", 0.73, _blue, ["community", "github"], ["infrastructure", "easy_start", "dx"], retention=0.6, urgency=0.4),
    _d("manufacturing-ai", "Manufacturing Process AI", 0.73, _blue, ["community"], ["infrastructure", "roi", "productivity", "compliance"], retention=0.8, urgency=0.5),
    _d("solar-installer-ai", "Solar Installation Planner", 0.71, _blue, ["community"], ["roi", "compliance", "infrastructure"], retention=0.4, urgency=0.5),
    _d("safety-compliance-ai", "Workplace Safety Compliance", 0.72, _blue, ["community"], ["compliance", "audit", "infrastructure"], retention=0.6, urgency=0.6),
    _d("inventory-tracker-ai", "Inventory Tracking AI", 0.73, _blue, ["community", "producthunt"], ["roi", "productivity", "simplicity", "time_leverage"], retention=0.8, urgency=0.5),
    _d("delivery-route-ai", "Delivery Route Optimizer", 0.74, _blue, ["community"], ["roi", "speed", "time_leverage", "productivity"], retention=0.7, urgency=0.5),
    _d("equipment-rental-ai", "Equipment Rental Optimizer", 0.68, _blue, ["community"], ["roi", "time_leverage", "simplicity"], retention=0.4, urgency=0.4),
    _d("waste-management-ai", "Waste Management Optimizer", 0.67, _blue, ["community"], ["infrastructure", "compliance", "roi"], retention=0.6, urgency=0.4),
]

# ============================================================================
# ADVANCED FINANCE (20 domains)
# ============================================================================
FINANCE_DOMAINS: list[dict[str, Any]] = [
    _d("algo-trading-equities", "Algo Trading (Equities)", 0.78, _fintech, ["github", "community"], ["alpha", "speed", "code_quality", "edge"], retention=0.8, urgency=0.5),
    _d("risk-modeling-ai", "Risk Modeling Engine", 0.76, _fintech, ["github", "arxiv"], ["infrastructure", "compliance", "code_quality", "audit"], retention=0.8, urgency=0.5),
    _d("ma-intelligence-ai", "M&A Intelligence AI", 0.74, _fintech, ["community"], ["alpha", "roi", "speed", "infrastructure"], retention=0.5, urgency=0.5),
    _d("venture-debt-ai", "Venture Debt Analyzer", 0.72, _fintech, ["community"], ["roi", "alpha", "compliance"], retention=0.4, urgency=0.5),
    _d("private-credit-ai", "Private Credit Platform AI", 0.73, _fintech, ["community"], ["roi", "compliance", "infrastructure", "alpha"], retention=0.5, urgency=0.5),
    _d("smb-financial-planning", "SMB Financial Planner AI", 0.77, _fintech, ["community", "producthunt"], ["roi", "easy_start", "simplicity", "time_leverage"], retention=0.7, urgency=0.6),
    _d("treasury-management-ai", "Treasury Management AI", 0.74, _fintech, ["community"], ["infrastructure", "compliance", "roi", "audit"], retention=0.7, urgency=0.5),
    _d("credit-scoring-ai", "AI Credit Scoring Engine", 0.75, _fintech, ["github", "community"], ["infrastructure", "compliance", "code_quality"], retention=0.7, urgency=0.5),
    _d("insurance-underwrite-ai", "Insurance Underwriting AI", 0.74, _fintech, ["community"], ["compliance", "roi", "infrastructure", "audit"], retention=0.7, urgency=0.5),
    _d("tax-optimization-ai", "AI Tax Optimization", 0.78, _fintech, ["community", "producthunt"], ["roi", "compliance", "quick_wins", "easy_start"], retention=0.5, urgency=0.7),
    _d("wealth-advisor-ai", "AI Wealth Advisor", 0.76, _fintech, ["community"], ["roi", "compliance", "simplicity", "easy_start"], retention=0.7, urgency=0.5),
    _d("expense-tracker-ai", "Smart Expense Tracker", 0.75, _fintech, ["community", "producthunt"], ["easy_start", "roi", "quick_wins", "simplicity"], retention=0.7, urgency=0.5),
    _d("invoice-factoring-ai", "Invoice Factoring AI", 0.71, _fintech, ["community"], ["roi", "speed", "infrastructure"], retention=0.5, urgency=0.5),
    _d("financial-report-ai", "Financial Report Generator", 0.76, _fintech, ["community", "producthunt"], ["productivity", "compliance", "roi", "time_leverage"], retention=0.6, urgency=0.5),
    _d("fraud-detection-ai", "AI Fraud Detection", 0.77, _fintech, ["github", "community"], ["infrastructure", "compliance", "code_quality", "audit"], retention=0.8, urgency=0.6),
    _d("payment-processor-ai", "Payment Processing AI", 0.75, _fintech, ["community", "github"], ["infrastructure", "compliance", "roi", "speed"], retention=0.8, urgency=0.5),
    _d("budget-planner-ai", "Personal Budget Planner AI", 0.76, _fintech, ["community", "producthunt"], ["easy_start", "roi", "simplicity", "quick_wins"], retention=0.7, urgency=0.6),
    _d("mortgage-analyzer-ai", "Mortgage Analyzer AI", 0.74, _fintech, ["community"], ["roi", "easy_start", "compliance", "simplicity"], retention=0.4, urgency=0.6),
    _d("stock-sentiment-ai", "Stock Sentiment Analyzer", 0.76, _fintech, ["community", "x_twitter"], ["alpha", "speed", "edge", "trend_spotting"], retention=0.5, urgency=0.5),
    _d("crypto-tax-ai", "Crypto Tax Calculator AI", 0.77, _fintech, ["community", "producthunt"], ["compliance", "roi", "easy_start", "defi"], retention=0.4, urgency=0.7),
]

# ============================================================================
# LEGAL TECH (15 domains)
# ============================================================================
LEGAL_DOMAINS: list[dict[str, Any]] = [
    _d("ip-portfolio-ai", "IP Portfolio Manager AI", 0.72, _legal, ["community"], ["compliance", "roi", "infrastructure"], retention=0.6, urgency=0.5),
    _d("legal-research-ai", "Legal Research Assistant", 0.76, _legal, ["community", "producthunt"], ["productivity", "time_leverage", "compliance", "code_quality"], retention=0.7, urgency=0.5),
    _d("litigation-analytics", "Litigation Analytics AI", 0.73, _legal, ["community"], ["roi", "infrastructure", "compliance", "audit"], retention=0.5, urgency=0.5),
    _d("corporate-governance-ai", "Corporate Governance AI", 0.71, _legal, ["community"], ["compliance", "audit", "infrastructure", "roi"], retention=0.6, urgency=0.5),
    _d("immigration-law-ai", "Immigration Law Assistant", 0.74, _legal, ["community"], ["compliance", "easy_start", "simplicity"], retention=0.4, urgency=0.8),
    _d("contract-draft-ai", "AI Contract Drafter", 0.77, _legal, ["community", "producthunt"], ["productivity", "compliance", "time_leverage"], retention=0.6, urgency=0.5),
    _d("trademark-search-ai", "Trademark Search AI", 0.71, _legal, ["community"], ["compliance", "quick_wins", "easy_start"], retention=0.3, urgency=0.4),
    _d("legal-billing-ai", "Legal Billing Optimizer", 0.72, _legal, ["community"], ["roi", "time_leverage", "productivity"], retention=0.7, urgency=0.4),
    _d("court-filing-ai", "Court Filing Assistant", 0.70, _legal, ["community"], ["compliance", "productivity", "time_leverage"], retention=0.5, urgency=0.5),
    _d("gdpr-compliance-ai", "GDPR Compliance Automator", 0.76, _legal, ["community", "github"], ["compliance", "audit", "infrastructure"], retention=0.7, urgency=0.7),
    _d("estate-planning-ai", "Estate Planning AI", 0.71, _legal, ["community"], ["compliance", "easy_start", "simplicity"], retention=0.3, urgency=0.4),
    _d("employment-law-ai", "Employment Law Navigator", 0.73, _legal, ["community"], ["compliance", "easy_start", "roi"], retention=0.4, urgency=0.7),
    _d("legal-doc-analyzer", "Legal Document Analyzer", 0.75, _legal, ["community", "producthunt"], ["productivity", "compliance", "time_leverage", "quick_wins"], retention=0.5, urgency=0.5),
    _d("mediation-ai", "AI Mediation Assistant", 0.69, _legal, ["community"], ["easy_start", "compliance", "simplicity"], retention=0.3, urgency=0.4),
    _d("regulatory-tracker-ai", "Regulatory Change Tracker", 0.74, _legal, ["community"], ["compliance", "audit", "infrastructure", "alpha"], retention=0.7, urgency=0.6),
]

# ============================================================================
# REAL ESTATE (15 domains)
# ============================================================================
REAL_ESTATE_DOMAINS: list[dict[str, Any]] = [
    _d("property-management-ai", "Property Management AI", 0.75, _realestate, ["community"], ["roi", "time_leverage", "infrastructure"], retention=0.8, urgency=0.5),
    _d("lease-analyzer-ai", "Lease Analysis AI", 0.73, _realestate, ["community"], ["compliance", "roi", "time_leverage"], retention=0.4, urgency=0.5),
    _d("commercial-re-analytics", "Commercial RE Analytics", 0.74, _realestate, ["community"], ["roi", "alpha", "infrastructure"], retention=0.5, urgency=0.5),
    _d("home-renovation-ai", "Home Renovation Planner", 0.73, _realestate, ["community", "producthunt"], ["easy_start", "roi", "creative_control", "simplicity"], retention=0.4, urgency=0.4),
    _d("re-development-model", "RE Development Modeler", 0.71, _realestate, ["community"], ["roi", "infrastructure", "compliance"], retention=0.5, urgency=0.4),
    _d("appraisal-ai", "Property Appraisal AI", 0.72, _realestate, ["community"], ["roi", "compliance", "speed", "quick_wins"], retention=0.4, urgency=0.4),
    _d("rental-pricing-ai", "Rental Pricing Optimizer", 0.74, _realestate, ["community"], ["roi", "alpha", "speed", "quick_wins"], retention=0.6, urgency=0.5),
    _d("tenant-screening-ai", "AI Tenant Screening", 0.73, _realestate, ["community"], ["compliance", "roi", "speed", "easy_start"], retention=0.5, urgency=0.5),
    _d("mortgage-broker-ai", "Mortgage Broker AI", 0.74, _realestate, ["community"], ["roi", "compliance", "easy_start"], retention=0.4, urgency=0.6),
    _d("home-buyer-ai", "AI Home Buyer Assistant", 0.75, _realestate, ["community", "producthunt"], ["easy_start", "roi", "simplicity"], retention=0.3, urgency=0.5),
    _d("re-market-predictor", "Real Estate Market Predictor", 0.72, _realestate, ["community", "x_twitter"], ["alpha", "roi", "trend_spotting"], retention=0.5, urgency=0.5),
    _d("airbnb-optimizer-ai", "Airbnb/STR Optimizer AI", 0.76, _realestate, ["community", "producthunt"], ["roi", "time_leverage", "quick_wins", "conversion"], retention=0.7, urgency=0.5),
    _d("building-inspector-ai", "Building Inspection AI", 0.70, _realestate, ["community"], ["compliance", "infrastructure", "quick_wins"], retention=0.4, urgency=0.4),
    _d("zoning-navigator-ai", "Zoning & Permits Navigator", 0.69, _realestate, ["community"], ["compliance", "easy_start", "time_leverage"], retention=0.3, urgency=0.4),
    _d("interior-design-ai", "Interior Design AI", 0.75, _realestate, ["community", "producthunt"], ["creative_control", "easy_start", "visual_impact"], retention=0.4, urgency=0.3),
]

# ============================================================================
# TRANSPORTATION & LOGISTICS (15 domains)
# ============================================================================
TRANSPORT_DOMAINS: list[dict[str, Any]] = [
    _d("route-optimizer-ai", "Route Optimization AI", 0.74, _transport, ["community", "github"], ["roi", "speed", "time_leverage"], retention=0.7, urgency=0.5),
    _d("last-mile-delivery-ai", "Last Mile Delivery AI", 0.73, _transport, ["community"], ["roi", "speed", "infrastructure"], retention=0.7, urgency=0.5),
    _d("freight-matching-ai", "Freight Matching AI", 0.72, _transport, ["community"], ["roi", "speed", "alpha"], retention=0.6, urgency=0.5),
    _d("parking-optimizer-ai", "Parking Optimization AI", 0.68, _transport, ["community"], ["roi", "infrastructure", "easy_start"], retention=0.5, urgency=0.3),
    _d("public-transit-ai", "Public Transit Planner", 0.67, _transport, ["community"], ["infrastructure", "easy_start", "simplicity"], retention=0.5, urgency=0.4),
    _d("ev-charging-planner", "EV Charging Network Planner", 0.71, _transport, ["community"], ["infrastructure", "roi", "compliance"], retention=0.5, urgency=0.5),
    _d("trucking-dispatch-ai", "Trucking Dispatch AI", 0.73, _transport, ["community"], ["roi", "speed", "time_leverage", "infrastructure"], retention=0.7, urgency=0.5),
    _d("drone-delivery-ai", "Drone Delivery Planner", 0.68, _transport, ["community", "arxiv"], ["infrastructure", "compliance", "first_mover"], retention=0.3, urgency=0.3),
    _d("vehicle-maintenance-ai", "Vehicle Maintenance Predictor", 0.72, _transport, ["community"], ["roi", "time_leverage", "infrastructure"], retention=0.7, urgency=0.4),
    _d("shipping-cost-ai", "Shipping Cost Optimizer", 0.74, _transport, ["community", "producthunt"], ["roi", "speed", "quick_wins", "easy_start"], retention=0.6, urgency=0.5),
    _d("ride-share-optimizer", "Ride Share Revenue Optimizer", 0.71, _transport, ["community"], ["roi", "time_leverage", "quick_wins"], retention=0.5, urgency=0.5),
    _d("supply-chain-visibility", "Supply Chain Visibility AI", 0.75, _transport, ["community", "github"], ["infrastructure", "roi", "compliance", "audit"], retention=0.7, urgency=0.5),
    _d("customs-clearance-ai", "Customs Clearance AI", 0.70, _transport, ["community"], ["compliance", "speed", "time_leverage"], retention=0.5, urgency=0.5),
    _d("logistics-forecaster", "Logistics Demand Forecaster", 0.73, _transport, ["community"], ["roi", "infrastructure", "alpha"], retention=0.6, urgency=0.5),
    _d("carbon-footprint-ai", "Carbon Footprint Tracker", 0.70, _transport, ["community", "x_twitter"], ["compliance", "audit", "roi"], retention=0.5, urgency=0.5),
]

# ============================================================================
# DEFENSE & SECURITY (12 domains)
# ============================================================================
DEFENSE_DOMAINS: list[dict[str, Any]] = [
    _d("cybersecurity-ai", "Cybersecurity AI Platform", 0.78, _defense, ["github", "community"], ["infrastructure", "compliance", "code_quality", "audit"], retention=0.8, urgency=0.7),
    _d("threat-intelligence-ai", "Threat Intelligence AI", 0.76, _defense, ["github", "community"], ["infrastructure", "alpha", "speed", "compliance"], retention=0.7, urgency=0.6),
    _d("incident-response-ai", "Incident Response AI", 0.75, _defense, ["github", "community"], ["speed", "infrastructure", "compliance"], retention=0.6, urgency=0.7),
    _d("vulnerability-scanner-ai", "AI Vulnerability Scanner", 0.77, _defense, ["github"], ["code_quality", "infrastructure", "compliance", "audit"], retention=0.7, urgency=0.6),
    _d("soc-analyst-ai", "SOC Analyst AI Assistant", 0.74, _defense, ["github", "community"], ["productivity", "infrastructure", "speed"], retention=0.7, urgency=0.6),
    _d("penetration-test-ai", "AI Penetration Testing", 0.73, _defense, ["github"], ["code_quality", "infrastructure", "compliance"], retention=0.5, urgency=0.5),
    _d("identity-access-ai", "Identity & Access Mgmt AI", 0.75, _defense, ["github", "community"], ["infrastructure", "compliance", "audit"], retention=0.8, urgency=0.6),
    _d("data-loss-prevention", "Data Loss Prevention AI", 0.73, _defense, ["community"], ["compliance", "infrastructure", "audit"], retention=0.7, urgency=0.6),
    _d("phishing-detector-ai", "AI Phishing Detector", 0.76, _defense, ["github", "community"], ["infrastructure", "compliance", "quick_wins"], retention=0.6, urgency=0.6),
    _d("zero-trust-architect", "Zero Trust Architecture AI", 0.74, _defense, ["github"], ["infrastructure", "compliance", "code_quality"], retention=0.7, urgency=0.6),
    _d("security-awareness-ai", "Security Awareness Trainer", 0.71, _defense, ["community"], ["compliance", "easy_start", "reskill"], retention=0.5, urgency=0.5),
    _d("osint-investigator-ai", "OSINT Investigation AI", 0.72, _defense, ["github", "community"], ["infrastructure", "alpha", "speed"], retention=0.5, urgency=0.5),
]

# ============================================================================
# SENIOR & ACCESSIBILITY (12 domains)
# ============================================================================
SENIOR_DOMAINS: list[dict[str, Any]] = [
    _d("elder-care-ai", "Elder Care Coordination AI", 0.73, _senior, ["community"], ["easy_start", "simplicity", "time_leverage"], retention=0.7, urgency=0.7),
    _d("cognitive-assistant-ai", "Cognitive Assistant AI", 0.72, _senior, ["community", "arxiv"], ["easy_start", "simplicity", "low_learning_curve"], retention=0.8, urgency=0.6),
    _d("accessibility-checker", "Accessibility Checker AI", 0.74, _senior, ["github", "community"], ["compliance", "code_quality", "audit"], retention=0.6, urgency=0.5),
    _d("voice-assistant-senior", "Senior Voice Assistant", 0.71, _senior, ["community"], ["easy_start", "simplicity", "low_learning_curve"], retention=0.7, urgency=0.5),
    _d("medication-reminder-ai", "Medication Reminder AI", 0.73, _senior, ["community"], ["easy_start", "simplicity", "compliance"], retention=0.8, urgency=0.6),
    _d("fall-detection-ai", "Fall Detection & Alert AI", 0.72, _senior, ["community"], ["infrastructure", "easy_start", "simplicity"], retention=0.7, urgency=0.6),
    _d("social-companion-ai", "AI Social Companion", 0.70, _senior, ["community"], ["easy_start", "simplicity", "low_learning_curve"], retention=0.7, urgency=0.6),
    _d("vision-assist-ai", "Vision Assistance AI", 0.71, _senior, ["community", "arxiv"], ["easy_start", "simplicity", "infrastructure"], retention=0.7, urgency=0.5),
    _d("hearing-assist-ai", "Hearing Assistance AI", 0.70, _senior, ["community"], ["easy_start", "simplicity", "infrastructure"], retention=0.7, urgency=0.5),
    _d("memory-aid-ai", "Memory Aid AI", 0.71, _senior, ["community"], ["easy_start", "simplicity", "low_learning_curve"], retention=0.8, urgency=0.6),
    _d("digital-literacy-senior", "Senior Digital Literacy AI", 0.69, _senior, ["community"], ["easy_start", "low_learning_curve", "simplicity", "reskill"], retention=0.5, urgency=0.5),
    _d("estate-organizer-ai", "Estate & Document Organizer", 0.70, _senior, ["community"], ["simplicity", "compliance", "easy_start"], retention=0.4, urgency=0.4),
]

# ============================================================================
# LOCAL SMALL BUSINESS (15 domains)
# ============================================================================
LOCAL_BIZ_DOMAINS: list[dict[str, Any]] = [
    _d("local-seo-ai", "Local SEO AI", 0.77, _local, ["community", "producthunt"], ["roi", "conversion", "easy_start", "quick_wins"], retention=0.6, urgency=0.6),
    _d("appointment-scheduler-ai", "AI Appointment Scheduler", 0.76, _local, ["community", "producthunt"], ["time_leverage", "easy_start", "roi", "simplicity"], retention=0.8, urgency=0.5),
    _d("review-manager-ai", "Review Management AI", 0.75, _local, ["community"], ["roi", "conversion", "audience_growth", "easy_start"], retention=0.6, urgency=0.5),
    _d("menu-optimizer-ai", "Restaurant Menu Optimizer", 0.71, _local, ["community"], ["roi", "quick_wins", "easy_start"], retention=0.5, urgency=0.4),
    _d("pos-analytics-ai", "POS Analytics AI", 0.73, _local, ["community"], ["roi", "productivity", "infrastructure", "quick_wins"], retention=0.7, urgency=0.5),
    _d("local-ads-ai", "Local Advertising AI", 0.75, _local, ["community", "producthunt"], ["roi", "conversion", "audience_growth", "easy_start"], retention=0.5, urgency=0.5),
    _d("salon-booking-ai", "Salon Booking Optimizer", 0.71, _local, ["community"], ["roi", "time_leverage", "easy_start", "simplicity"], retention=0.7, urgency=0.4),
    _d("inventory-smb-ai", "SMB Inventory AI", 0.72, _local, ["community"], ["roi", "productivity", "simplicity"], retention=0.7, urgency=0.5),
    _d("loyalty-program-ai", "AI Loyalty Program Builder", 0.73, _local, ["community"], ["roi", "conversion", "audience_growth"], retention=0.6, urgency=0.4),
    _d("food-delivery-partner", "Food Delivery Optimizer", 0.74, _local, ["community"], ["roi", "speed", "quick_wins"], retention=0.6, urgency=0.5),
    _d("contractor-bid-ai", "Contractor Bid Optimizer", 0.71, _local, ["community"], ["roi", "speed", "easy_start", "quick_wins"], retention=0.4, urgency=0.5),
    _d("daycare-manager-ai", "Daycare Management AI", 0.70, _local, ["community"], ["compliance", "time_leverage", "simplicity"], retention=0.7, urgency=0.4),
    _d("auto-repair-ai", "Auto Repair Estimator AI", 0.70, _local, ["community"], ["roi", "quick_wins", "easy_start", "simplicity"], retention=0.4, urgency=0.4),
    _d("cleaning-service-ai", "Cleaning Service Optimizer", 0.69, _local, ["community"], ["roi", "time_leverage", "simplicity"], retention=0.5, urgency=0.4),
    _d("pet-care-business-ai", "Pet Care Business AI", 0.70, _local, ["community"], ["roi", "easy_start", "simplicity", "time_leverage"], retention=0.5, urgency=0.4),
]

# ============================================================================
# FOOD & AGRICULTURE (12 domains)
# ============================================================================
FOOD_AG_DOMAINS: list[dict[str, Any]] = [
    _d("restaurant-management-ai", "Restaurant Management AI", 0.74, _food, ["community"], ["roi", "productivity", "time_leverage"], retention=0.7, urgency=0.5),
    _d("farm-management-ai", "Farm Management AI", 0.71, _food, ["community"], ["roi", "infrastructure", "productivity"], retention=0.7, urgency=0.5),
    _d("food-supply-chain-ai", "Food Supply Chain AI", 0.72, _food, ["community"], ["infrastructure", "compliance", "roi"], retention=0.7, urgency=0.5),
    _d("recipe-dev-commercial", "Commercial Recipe Developer", 0.69, _food, ["community"], ["creative_control", "roi", "productivity"], retention=0.5, urgency=0.3),
    _d("crop-yield-predictor", "Crop Yield Predictor AI", 0.70, _food, ["community", "arxiv"], ["infrastructure", "roi", "alpha"], retention=0.6, urgency=0.5),
    _d("food-safety-ai", "Food Safety Compliance AI", 0.73, _food, ["community"], ["compliance", "audit", "infrastructure"], retention=0.7, urgency=0.5),
    _d("wine-sommelier-ai", "AI Wine Sommelier", 0.67, _food, ["community"], ["easy_start", "creative_control", "simplicity"], retention=0.4, urgency=0.2),
    _d("livestock-monitor-ai", "Livestock Monitoring AI", 0.69, _food, ["community"], ["infrastructure", "roi", "productivity"], retention=0.7, urgency=0.4),
    _d("food-waste-reducer", "Food Waste Reduction AI", 0.71, _food, ["community", "x_twitter"], ["roi", "compliance", "infrastructure"], retention=0.6, urgency=0.5),
    _d("vertical-farming-ai", "Vertical Farming AI", 0.68, _food, ["community", "arxiv"], ["infrastructure", "first_mover", "roi"], retention=0.6, urgency=0.4),
    _d("food-truck-optimizer", "Food Truck Business AI", 0.69, _food, ["community"], ["roi", "easy_start", "speed", "quick_wins"], retention=0.5, urgency=0.4),
    _d("catering-planner-ai", "Catering Event Planner AI", 0.68, _food, ["community"], ["productivity", "roi", "time_leverage"], retention=0.4, urgency=0.4),
]

# ============================================================================
# EDUCATION & RESKILLING (15 domains) -- complementing existing education
# ============================================================================
EDUCATION_DOMAINS: list[dict[str, Any]] = [
    _d("micro-credential-ai", "Micro-Credential Platform AI", 0.76, _ai_surv, ["community", "producthunt"], ["reskill", "career", "easy_start", "quick_wins"], retention=0.5, urgency=0.8),
    _d("ai-lab-assistant", "AI Lab Assistant", 0.73, _ai_surv, ["github", "community"], ["code_quality", "easy_start", "reskill"], retention=0.6, urgency=0.6),
    _d("language-immersion-ai", "Language Immersion AI", 0.75, _ai_surv, ["community", "producthunt"], ["easy_start", "low_learning_curve", "quick_wins"], retention=0.7, urgency=0.5),
    _d("stem-tutor-ai", "STEM Tutor AI", 0.74, _ai_surv, ["community"], ["easy_start", "low_learning_curve", "reskill"], retention=0.6, urgency=0.6),
    _d("research-paper-ai", "Research Paper Writer AI", 0.73, _ai_surv, ["community", "arxiv"], ["productivity", "content_quality", "time_leverage"], retention=0.5, urgency=0.5),
    _d("study-group-ai", "AI Study Group Facilitator", 0.70, _ai_surv, ["community"], ["easy_start", "low_learning_curve", "simplicity"], retention=0.4, urgency=0.5),
    _d("flashcard-generator-ai", "AI Flashcard Generator", 0.74, _ai_surv, ["community", "producthunt"], ["easy_start", "quick_wins", "low_learning_curve"], retention=0.5, urgency=0.6),
    _d("thesis-advisor-ai", "AI Thesis Advisor", 0.71, _ai_surv, ["community"], ["productivity", "content_quality", "time_leverage"], retention=0.5, urgency=0.5),
    _d("corporate-lms-ai", "Corporate LMS AI", 0.76, _enter, ["community"], ["infrastructure", "reskill", "compliance", "roi"], retention=0.7, urgency=0.7),
    _d("teacher-assistant-ai", "AI Teacher Assistant", 0.75, _ai_surv, ["community"], ["productivity", "time_leverage", "easy_start"], retention=0.7, urgency=0.6),
    _d("parent-homework-ai", "Parent Homework Helper AI", 0.73, _ai_surv, ["community"], ["easy_start", "low_learning_curve", "simplicity", "quick_wins"], retention=0.5, urgency=0.5),
    _d("special-education-ai", "Special Education AI Tools", 0.72, _ai_surv, ["community"], ["easy_start", "simplicity", "low_learning_curve", "compliance"], retention=0.7, urgency=0.6),
    _d("skill-verification-ai", "AI Skill Verification", 0.74, _ai_surv, ["community", "github"], ["reskill", "career", "compliance", "audit"], retention=0.4, urgency=0.7),
    _d("bootcamp-recommender", "Bootcamp Recommender AI", 0.72, _ai_surv, ["community"], ["career", "reskill", "easy_start", "roi"], retention=0.3, urgency=0.8),
    _d("continuing-ed-ai", "Continuing Education AI", 0.73, _ai_surv, ["community"], ["reskill", "career", "compliance", "easy_start"], retention=0.5, urgency=0.7),
]

# ============================================================================
# EMERGING VERTICALS (19 domains)
# ============================================================================
EMERGING_DOMAINS: list[dict[str, Any]] = [
    _d("carbon-credit-ai", "Carbon Credit Trading AI", 0.71, _emerging, ["community", "x_twitter"], ["compliance", "roi", "alpha", "first_mover"], retention=0.5, urgency=0.5),
    _d("circular-economy-ai", "Circular Economy Platform", 0.68, _emerging, ["community"], ["infrastructure", "compliance", "roi"], retention=0.5, urgency=0.4),
    _d("digital-twin-builder", "Digital Twin Builder AI", 0.73, _emerging, ["github", "community"], ["infrastructure", "code_quality", "first_mover", "dx"], retention=0.6, urgency=0.4),
    _d("longevity-tech-ai", "Longevity & Anti-Aging AI", 0.69, _emerging, ["community", "arxiv"], ["first_mover", "alpha", "infrastructure"], retention=0.5, urgency=0.4),
    _d("space-data-ai", "Space Data Analytics", 0.68, _emerging, ["arxiv", "github"], ["infrastructure", "code_quality", "first_mover"], retention=0.5, urgency=0.3),
    _d("quantum-app-builder", "Quantum Computing App Builder", 0.65, _emerging, ["arxiv", "github"], ["code_quality", "first_mover", "infrastructure", "dx"], retention=0.4, urgency=0.3),
    _d("synthetic-biology-ai", "Synthetic Biology Design AI", 0.66, _emerging, ["arxiv"], ["infrastructure", "code_quality", "first_mover"], retention=0.5, urgency=0.3),
    _d("materials-discovery-ai", "Advanced Materials Discovery", 0.67, _emerging, ["arxiv", "github"], ["infrastructure", "code_quality", "first_mover"], retention=0.5, urgency=0.3),
    _d("metaverse-builder-ai", "Metaverse Experience Builder", 0.70, _emerging, ["community", "github"], ["creative_control", "first_mover", "dx"], retention=0.4, urgency=0.3),
    _d("brain-interface-ai", "Brain-Computer Interface AI", 0.64, _emerging, ["arxiv"], ["first_mover", "infrastructure", "code_quality"], retention=0.4, urgency=0.2),
    _d("climate-modeling-ai", "Climate Modeling AI", 0.69, _emerging, ["arxiv", "github"], ["infrastructure", "compliance", "code_quality"], retention=0.6, urgency=0.5),
    _d("energy-trading-ai", "Energy Trading AI", 0.73, _emerging, ["community"], ["alpha", "roi", "speed", "compliance"], retention=0.6, urgency=0.5),
    _d("water-management-ai", "Water Resource Management AI", 0.67, _emerging, ["community", "arxiv"], ["infrastructure", "compliance", "roi"], retention=0.6, urgency=0.5),
    _d("autonomous-vehicle-ai", "Autonomous Vehicle Stack", 0.70, _emerging, ["github", "arxiv"], ["infrastructure", "code_quality", "first_mover"], retention=0.5, urgency=0.3),
    _d("ar-commerce-ai", "AR Commerce Builder", 0.71, _emerging, ["community", "github"], ["first_mover", "creative_control", "conversion", "dx"], retention=0.4, urgency=0.4),
    _d("edge-computing-ai", "Edge Computing AI Platform", 0.73, _emerging, ["github"], ["infrastructure", "code_quality", "dx", "speed"], retention=0.6, urgency=0.5),
    _d("biotech-research-ai", "Biotech Research AI", 0.68, _emerging, ["arxiv", "github"], ["infrastructure", "code_quality", "first_mover"], retention=0.6, urgency=0.4),
    _d("drone-analytics-ai", "Drone Data Analytics", 0.70, _emerging, ["community", "github"], ["infrastructure", "roi", "first_mover"], retention=0.5, urgency=0.4),
    _d("regenerative-ag-ai", "Regenerative Agriculture AI", 0.67, _emerging, ["community", "arxiv"], ["infrastructure", "compliance", "roi", "first_mover"], retention=0.6, urgency=0.4),
]


# ============================================================================
# AGGREGATE ALL V4 DOMAINS
# ============================================================================
NEW_250_V4_DOMAINS: list[dict[str, Any]] = (
    AI_SURVIVAL_DOMAINS
    + HEALTHCARE_DOMAINS
    + GOVERNMENT_DOMAINS
    + ENTERPRISE_DOMAINS
    + BLUE_COLLAR_DOMAINS
    + FINANCE_DOMAINS
    + LEGAL_DOMAINS
    + REAL_ESTATE_DOMAINS
    + TRANSPORT_DOMAINS
    + DEFENSE_DOMAINS
    + SENIOR_DOMAINS
    + LOCAL_BIZ_DOMAINS
    + FOOD_AG_DOMAINS
    + EDUCATION_DOMAINS
    + EMERGING_DOMAINS
)

# V4 relationships between new domains
NEW_V4_RELATIONSHIPS: list[dict[str, Any]] = [
    # AI Survival ecosystem
    {"source": "resume-ai", "target": "interview-prep-ai", "relationship": "EXTENDS", "weight": 0.8},
    {"source": "career-pivot-ai", "target": "upskill-path-ai", "relationship": "EXTENDS", "weight": 0.9},
    {"source": "ai-proof-career", "target": "human-skills-trainer", "relationship": "EXTENDS", "weight": 0.8},
    {"source": "coding-bootcamp-ai", "target": "prompt-job-skills", "relationship": "EXTENDS", "weight": 0.7},
    {"source": "layoff-preparation-ai", "target": "freelance-ai-coach", "relationship": "ENABLES", "weight": 0.7},

    # Healthcare connections
    {"source": "ai-therapy-companion", "target": "anxiety-management-ai", "relationship": "EXTENDS", "weight": 0.9},
    {"source": "telemedicine-builder", "target": "patient-engagement-ai", "relationship": "ENABLES", "weight": 0.7},
    {"source": "burnout-detector-ai", "target": "ai-therapy-companion", "relationship": "ENABLES", "weight": 0.6},

    # Enterprise ecosystem
    {"source": "enterprise-search-ai", "target": "knowledge-base-ai", "relationship": "EXTENDS", "weight": 0.8},
    {"source": "corporate-training-ai", "target": "employee-onboarding-ai", "relationship": "EXTENDS", "weight": 0.7},
    {"source": "contract-review-ai", "target": "contract-draft-ai", "relationship": "EXTENDS", "weight": 0.9},

    # Finance connections
    {"source": "algo-trading-equities", "target": "risk-modeling-ai", "relationship": "EXTENDS", "weight": 0.7},
    {"source": "fraud-detection-ai", "target": "cybersecurity-ai", "relationship": "ENABLES", "weight": 0.6},

    # Competition edges
    {"source": "resume-ai", "target": "linkedin-optimizer", "relationship": "COMPETES_WITH", "weight": 0.6},
    {"source": "ai-therapy-companion", "target": "mental-health-chatbot", "relationship": "COMPETES_WITH", "weight": 0.7},
    {"source": "algo-trading-equities", "target": "stock-sentiment-ai", "relationship": "COMPETES_WITH", "weight": 0.5},
]


if __name__ == "__main__":
    print(f"Total new v4 domains: {len(NEW_250_V4_DOMAINS)}")
    categories = {
        "AI Survival": len(AI_SURVIVAL_DOMAINS),
        "Healthcare": len(HEALTHCARE_DOMAINS),
        "Government": len(GOVERNMENT_DOMAINS),
        "Enterprise": len(ENTERPRISE_DOMAINS),
        "Blue Collar": len(BLUE_COLLAR_DOMAINS),
        "Finance": len(FINANCE_DOMAINS),
        "Legal": len(LEGAL_DOMAINS),
        "Real Estate": len(REAL_ESTATE_DOMAINS),
        "Transport": len(TRANSPORT_DOMAINS),
        "Defense": len(DEFENSE_DOMAINS),
        "Senior": len(SENIOR_DOMAINS),
        "Local Biz": len(LOCAL_BIZ_DOMAINS),
        "Food & Ag": len(FOOD_AG_DOMAINS),
        "Education": len(EDUCATION_DOMAINS),
        "Emerging": len(EMERGING_DOMAINS),
    }
    for cat, count in categories.items():
        print(f"  {cat:20s}: {count}")
    print(f"  {'TOTAL':20s}: {sum(categories.values())}")

    # Verify no duplicate IDs
    ids = [d["domain_id"] for d in NEW_250_V4_DOMAINS]
    dupes = [x for x in ids if ids.count(x) > 1]
    if dupes:
        print(f"\nDUPLICATES: {set(dupes)}")
    else:
        print(f"\nNo duplicate IDs. {len(ids)} unique domains.")
