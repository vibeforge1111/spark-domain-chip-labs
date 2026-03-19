"""MiroFish-inspired trend prediction engine for domain chip R&D."""

from .graph import DomainGraph, build_graph_from_opportunities
from .personas import generate_personas, PERSONA_TYPES
from .simulation import run_simulation
from .signals import (
    SIGNAL_TYPES, SHOCK_TEMPLATES, create_signal, create_shock,
    signals_from_opportunities, signals_from_graph,
)
from .calibration import create_outcome_contract, brier_score, calibration_report
from .report import generate_prediction_report
