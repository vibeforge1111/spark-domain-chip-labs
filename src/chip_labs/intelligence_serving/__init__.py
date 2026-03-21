"""Internal namespace for the intelligence-serving surface."""

from .api import (
    AdvisoryRequest,
    ChipMCPServer,
    advise_pre_action,
    execute_hook,
    inject_context_for_task,
    load_portfolio,
    refresh_skill,
    serve_context,
)

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
