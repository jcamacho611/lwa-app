from __future__ import annotations

from functools import lru_cache
from typing import Any

from .brain import ENGINE as brain_engine
from .creator import ENGINE as creator_engine
from .marketplace import ENGINE as marketplace_engine
from .operator_admin import ENGINE as operator_admin_engine
from .proof_history import ENGINE as proof_history_engine
from .render import ENGINE as render_engine
from .safety import ENGINE as safety_engine
from .social_distribution import ENGINE as social_distribution_engine
from .wallet_entitlements import ENGINE as wallet_entitlements_engine
from .world_game import ENGINE as world_game_engine

ENGINE_REGISTRY = (
    creator_engine,
    brain_engine,
    render_engine,
    marketplace_engine,
    wallet_entitlements_engine,
    proof_history_engine,
    world_game_engine,
    safety_engine,
    social_distribution_engine,
    operator_admin_engine,
)


@lru_cache(maxsize=1)
def get_engine_registry() -> dict[str, Any]:
    engines = {engine.engine_id: engine.to_registry_record() for engine in ENGINE_REGISTRY}
    return {
        "count": len(engines),
        "engines": engines,
        "status_summary": {
            "scaffolded": sum(1 for engine in ENGINE_REGISTRY if engine.status == "scaffolded"),
            "local_ready": sum(1 for engine in ENGINE_REGISTRY if engine.status == "local_ready"),
            "backend_ready": sum(1 for engine in ENGINE_REGISTRY if engine.status == "backend_ready"),
            "provider_ready": sum(1 for engine in ENGINE_REGISTRY if engine.status == "provider_ready"),
            "production_ready": sum(1 for engine in ENGINE_REGISTRY if engine.status == "production_ready"),
        },
        "note": "Actual backend engines are loaded from app.engines and exposed safely for demo and health checks.",
    }


def get_engine(engine_id: str):
    for engine in ENGINE_REGISTRY:
        if engine.engine_id == engine_id:
            return engine
    return None


def get_engine_health() -> dict[str, Any]:
    registry = get_engine_registry()
    health_map = {engine_id: record["health"] for engine_id, record in registry["engines"].items()}
    healthy_count = sum(1 for health in health_map.values() if health.get("healthy"))
    return {
        "count": registry["count"],
        "healthy_count": healthy_count,
        "unhealthy_count": registry["count"] - healthy_count,
        "engines": health_map,
        "status_summary": registry["status_summary"],
    }


def run_engine_demo(engine_id: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    engine = get_engine(engine_id)
    if engine is None:
        raise KeyError(engine_id)
    return engine.demo_run(payload or {})
