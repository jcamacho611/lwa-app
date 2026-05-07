"""Engine runtime — selects which backend engine the current process serves.

Designed for Railway-style deployments where one process serves exactly
one engine. The engine is chosen at boot via the LWA_ENGINE_SERVICE_ID
environment variable. The full engine registry remains discoverable
inside the main backend service (see app/api/routes/engines.py); this
runtime is the thin selection layer used by the per-engine service app
in app/services/engine_service_app.py.

This runtime performs no paid provider calls, no payouts, no external
posting, and mutates no real money. The selected engine's demo path is
the only mutation surface, and it is constrained by each engine's
deterministic local _demo() function.
"""

from __future__ import annotations

import os
from typing import Any

from app.engines.registry import (
    ENGINE_REGISTRY,
    get_engine,
    get_engine_health,
    get_engine_registry,
    run_engine_demo,
)

# Environment variable name. Constant so tests can patch it.
ENGINE_SERVICE_ENV_VAR: str = "LWA_ENGINE_SERVICE_ID"

# Fallback engine id when the env var is unset. operator_admin is the
# safest read-only roll-up engine and never claims any external action.
DEFAULT_ENGINE_ID: str = "operator_admin"


class EngineSelectionError(RuntimeError):
    """Raised when the configured engine id is invalid."""


def _known_engine_ids() -> tuple[str, ...]:
    """Return the canonical, ordered tuple of engine ids."""
    return tuple(engine.engine_id for engine in ENGINE_REGISTRY)


def _resolve_engine_id(raw: str | None) -> str:
    if raw is None or raw.strip() == "":
        return DEFAULT_ENGINE_ID
    return raw.strip()


def get_selected_engine_id() -> str:
    """Return the engine id this process is configured to serve.

    Falls back to DEFAULT_ENGINE_ID if the env var is unset. Raises
    EngineSelectionError if the configured id is not a valid engine id.
    """
    engine_id = _resolve_engine_id(os.environ.get(ENGINE_SERVICE_ENV_VAR))
    known = _known_engine_ids()
    if engine_id not in known:
        raise EngineSelectionError(
            f"Invalid {ENGINE_SERVICE_ENV_VAR}={engine_id!r}. "
            f"Expected one of: {', '.join(known)}."
        )
    return engine_id


def get_selected_engine() -> Any:
    """Return the BackendEngine instance this process is configured to serve."""
    engine_id = get_selected_engine_id()
    engine = get_engine(engine_id)
    if engine is None:
        # Should not happen — get_selected_engine_id validated against the
        # same registry. Defensive raise keeps types tight.
        raise EngineSelectionError(f"Engine not found in registry: {engine_id!r}")
    return engine


def selected_engine_metadata() -> dict[str, Any]:
    """Return the full registry record for the selected engine."""
    return get_selected_engine().to_registry_record()


def selected_engine_health() -> dict[str, Any]:
    """Return the health snapshot for the selected engine."""
    return get_selected_engine().health()


def run_selected_engine_demo(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Run the selected engine's demo path. Always returns a dict; never
    posts externally, never moves money, never calls paid providers.
    """
    engine_id = get_selected_engine_id()
    return run_engine_demo(engine_id, payload or {})


def list_known_engine_ids() -> list[str]:
    """Helper for diagnostics — list all engine ids known to the registry."""
    return list(_known_engine_ids())


def runtime_snapshot() -> dict[str, Any]:
    """One-shot snapshot of the runtime: selection, defaults, and totals."""
    try:
        selected = get_selected_engine_id()
        error: str | None = None
    except EngineSelectionError as exc:
        selected = ""
        error = str(exc)
    registry = get_engine_registry()
    health = get_engine_health()
    return {
        "env_var": ENGINE_SERVICE_ENV_VAR,
        "default_engine_id": DEFAULT_ENGINE_ID,
        "selected_engine_id": selected,
        "selection_error": error,
        "known_engine_ids": list(_known_engine_ids()),
        "engines_loaded": registry["count"],
        "healthy_count": health["healthy_count"],
        "unhealthy_count": health["unhealthy_count"],
    }
