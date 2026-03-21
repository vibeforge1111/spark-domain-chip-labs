"""Internal namespace for the intelligence-serving surface."""

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


def __getattr__(name: str) -> object:
    """Resolve serving-surface exports lazily to avoid import cycles."""
    if name not in __all__:
        msg = f"module {__name__!r} has no attribute {name!r}"
        raise AttributeError(msg)

    from . import api

    return getattr(api, name)
