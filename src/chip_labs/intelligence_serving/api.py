"""Intelligence-serving compatibility API."""

from __future__ import annotations

from ..chip_advisor import AdvisoryRequest, advise_pre_action
from ..chip_context_injector import inject_context_for_task
from ..chip_mcp_server import ChipMCPServer
from ..chip_runtime import execute_hook, load_portfolio
from .intelligence_server import refresh_skill, serve_context

__all__ = [
    "AdvisoryRequest",
    "ChipMCPServer",
    "advise_pre_action",
    "execute_hook",
    "inject_context_for_task",
    "load_portfolio",
    "refresh_skill",
    "serve_context",
]
