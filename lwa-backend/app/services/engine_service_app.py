"""Dedicated FastAPI app for Railway LWA engine service boxes.

Run from the `lwa-backend` root with:

    uvicorn app.services.engine_service_app:app --host 0.0.0.0 --port $PORT

Select the served engine with:

    LWA_ENGINE_SERVICE_ID=<engine_id>

This service is intentionally demo-safe. It does not call paid providers,
execute payouts, post to social networks, mutate real balances, or require
secrets.
"""

from __future__ import annotations

from typing import Any, Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.services.engine_runtime import (
    get_runtime_selection,
    run_selected_engine_demo,
    selected_engine_health,
    selected_engine_metadata,
)


class EngineDemoRequest(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict)


def create_engine_service_app() -> FastAPI:
    app = FastAPI(
        title="LWA Dedicated Engine Service",
        version="0.1.0",
        description="Local-safe dedicated Railway service for one selected LWA engine.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health() -> Dict[str, Any]:
        selection = get_runtime_selection()
        engine_health = selected_engine_health()
        return {
            "service": "lwa-engine-service",
            "healthy": bool(selection.valid and engine_health.get("healthy", False)),
            "status": "ok" if selection.valid else "configuration_error",
            "runtime": selection.to_dict(),
            "engine_health": engine_health,
            "safe_mode": True,
        }

    @app.get("/engine")
    def engine() -> Dict[str, Any]:
        return selected_engine_metadata()

    @app.get("/engine/health")
    def engine_health() -> Dict[str, Any]:
        return selected_engine_health()

    @app.post("/engine/demo")
    def engine_demo(request: EngineDemoRequest) -> Dict[str, Any]:
        return run_selected_engine_demo(request.payload)

    return app


app = create_engine_service_app()
