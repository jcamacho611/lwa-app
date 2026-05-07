from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from ...engines.registry import get_engine, get_engine_health, get_engine_registry, run_engine_demo

router = APIRouter(prefix="/engines", tags=["engines"])


@router.get("")
def list_engines() -> dict[str, Any]:
    return get_engine_registry()


@router.get("/health")
def engines_health() -> dict[str, Any]:
    return get_engine_health()


@router.get("/{engine_id}")
def engine_detail(engine_id: str) -> dict[str, Any]:
    engine = get_engine(engine_id)
    if engine is None:
        raise HTTPException(status_code=404, detail=f"Engine not found: {engine_id}")
    return engine.to_registry_record()


@router.post("/{engine_id}/demo")
def engine_demo(engine_id: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    try:
        return run_engine_demo(engine_id, payload or {})
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Engine not found: {engine_id}") from exc
