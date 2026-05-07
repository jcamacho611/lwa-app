"""
Engine Foundation Routes

Exposes the LWA backend engine registry over HTTP.

GET  /engines                    — list all engines with metadata
GET  /engines/health             — health status for all engines
GET  /engines/{engine_id}        — metadata for a single engine
POST /engines/{engine_id}/demo   — run a safe local demo for an engine

All endpoints are local-safe and require no secrets or provider calls.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.engines.registry import (
    engine_ids,
    get_engine,
    get_engine_health,
    get_engine_registry,
    run_engine_demo,
)

router = APIRouter(prefix="/engines", tags=["engines"])


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class EngineDemoRequest(BaseModel):
    payload: dict[str, Any] = {}


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get("")
async def list_engines() -> dict[str, Any]:
    """Return metadata for all registered engines."""
    registry = get_engine_registry()
    return {
        "count": len(registry),
        "engines": registry,
        "note": (
            "All engines are local-safe. "
            "No provider calls, payments, or social posting occur at SCAFFOLDED or LOCAL_READY status."
        ),
    }


@router.get("/health")
async def engines_health() -> dict[str, Any]:
    """Return health status for all registered engines."""
    health_list = get_engine_health()
    return {
        "count": len(health_list),
        "health": [
            {
                "engine_id": h.engine_id,
                "status": h.status.value,
                "healthy": h.healthy,
                "warnings": h.warnings,
                "notes": h.notes,
            }
            for h in health_list
        ],
    }


@router.get("/{engine_id}")
async def get_engine_metadata(engine_id: str) -> dict[str, Any]:
    """Return metadata for a single engine."""
    engine = get_engine(engine_id)
    if engine is None:
        raise HTTPException(
            status_code=404,
            detail={
                "error": f"Engine '{engine_id}' not found",
                "available_engines": engine_ids(),
            },
        )
    return engine.metadata()


@router.post("/{engine_id}/demo")
async def run_demo(engine_id: str, request: EngineDemoRequest) -> dict[str, Any]:
    """
    Run a safe, local, deterministic demo for the named engine.

    No external provider calls, payments, or social posting occur.
    """
    engine = get_engine(engine_id)
    if engine is None:
        raise HTTPException(
            status_code=404,
            detail={
                "error": f"Engine '{engine_id}' not found",
                "available_engines": engine_ids(),
            },
        )
    try:
        result = run_engine_demo(engine_id, request.payload)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={"error": "Demo execution failed", "detail": str(exc)},
        ) from exc

    return {
        "engine_id": result.engine_id,
        "status": result.status.value,
        "summary": result.summary,
        "input_echo": result.input_echo,
        "output": result.output,
        "warnings": result.warnings,
        "next_required_integrations": result.next_required_integrations,
    }
