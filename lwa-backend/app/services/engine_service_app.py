"""Generic LWA engine service app.

Single FastAPI app that serves exactly one engine, chosen at boot via
the LWA_ENGINE_SERVICE_ID environment variable. Designed to be deployed
as a Railway service per engine — same image, different env var. Zero
duplicated code across the 10 engine deployments.

Routes:
    GET  /              — Service banner + current selection.
    GET  /health        — Liveness; never raises on engine state.
    GET  /engine        — Full engine record (id, name, status, capabilities).
    GET  /engine/health — Engine health snapshot.
    POST /engine/demo   — Run the engine demo path with the supplied payload.

This service:
    - performs no paid provider calls,
    - executes no payouts,
    - posts to no external platform,
    - mutates no real money,
    - mutates no /generate behavior.

Railway start command:
    cd lwa-backend && uvicorn app.services.engine_service_app:app --host 0.0.0.0 --port $PORT

Railway healthcheck path:
    /health
"""

from __future__ import annotations

from typing import Any

from fastapi import Body, FastAPI, HTTPException

from .engine_runtime import (
    DEFAULT_ENGINE_ID,
    ENGINE_SERVICE_ENV_VAR,
    EngineSelectionError,
    get_selected_engine_id,
    run_selected_engine_demo,
    runtime_snapshot,
    selected_engine_health,
    selected_engine_metadata,
)


def create_engine_service_app() -> FastAPI:
    """Build the per-engine FastAPI service app.

    The selected engine id is resolved lazily on each request so that
    tests can patch the env var between calls.
    """
    app = FastAPI(
        title="LWA Engine Service",
        version="0.1.0",
        description=(
            "Single-engine LWA service. Selects an engine via the "
            f"{ENGINE_SERVICE_ENV_VAR} environment variable. No paid "
            "providers, no payouts, no external posting."
        ),
    )

    @app.get("/")
    def root() -> dict[str, Any]:
        try:
            engine_id = get_selected_engine_id()
            error: str | None = None
        except EngineSelectionError as exc:
            engine_id = ""
            error = str(exc)
        return {
            "service": "lwa-engine-service",
            "selected_engine_id": engine_id or None,
            "selection_error": error,
            "default_engine_id": DEFAULT_ENGINE_ID,
            "env_var": ENGINE_SERVICE_ENV_VAR,
            "routes": ["/health", "/engine", "/engine/health", "/engine/demo"],
        }

    @app.get("/health")
    def health() -> dict[str, Any]:
        # Never raises. Reports configuration status alongside liveness.
        snapshot = runtime_snapshot()
        return {
            "status": "ok",
            "service": "lwa-engine-service",
            "selected_engine_id": snapshot["selected_engine_id"] or None,
            "selection_error": snapshot["selection_error"],
            "default_engine_id": DEFAULT_ENGINE_ID,
            "env_var": ENGINE_SERVICE_ENV_VAR,
            "known_engine_ids": snapshot["known_engine_ids"],
            "engines_loaded": snapshot["engines_loaded"],
            "healthy_count": snapshot["healthy_count"],
        }

    @app.get("/engine")
    def engine() -> dict[str, Any]:
        try:
            return selected_engine_metadata()
        except EngineSelectionError as exc:
            raise HTTPException(status_code=503, detail=str(exc))

    @app.get("/engine/health")
    def engine_health() -> dict[str, Any]:
        try:
            return selected_engine_health()
        except EngineSelectionError as exc:
            raise HTTPException(status_code=503, detail=str(exc))

    @app.post("/engine/demo")
    def engine_demo(payload: dict[str, Any] | None = Body(default=None)) -> dict[str, Any]:
        try:
            return run_selected_engine_demo(payload or {})
        except EngineSelectionError as exc:
            raise HTTPException(status_code=503, detail=str(exc))
        except KeyError as exc:
            # Belt-and-suspenders: should not happen because the runtime
            # validates the engine id before invoking the registry.
            raise HTTPException(status_code=503, detail=f"engine_not_found: {exc}")

    return app


# Module-level app for uvicorn / Railway start command.
app = create_engine_service_app()
