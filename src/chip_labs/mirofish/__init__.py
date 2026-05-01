"""MiroFish-inspired trend prediction engine for domain chip R&D."""

from .graph import DomainGraph, build_graph_from_opportunities
from .personas import (
    generate_personas, PERSONA_TYPES, CUSTOMER_PERSONAS,
    persona_domain_fit,
)
from .simulation import run_simulation, run_ensemble, run_sensitivity
from .signals import (
    SIGNAL_TYPES, SHOCK_TEMPLATES, create_signal, create_shock,
    signals_from_opportunities, signals_from_graph,
)
from .calibration import create_outcome_contract, brier_score, calibration_report
from .report import generate_prediction_report, generate_driver_summary, format_driver_summary
from .systems import compute_system_priority, DOMAIN_SYSTEMS, format_system_priority
from .content_simulation import simulate_content_selection, format_content_simulation_markdown
from .live_signals import (
    signals_from_twitter_search, signals_from_twitter_trends,
    signals_from_user_mentions, aggregate_live_signals,
)
