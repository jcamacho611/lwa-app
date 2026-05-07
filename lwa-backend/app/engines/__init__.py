"""
LWA Backend Engine Foundation
Modular, testable, local-safe engine architecture.
"""

from .base import (
    EngineCapability,
    EngineDemoResult,
    EngineHealth,
    EngineStatus,
    LwaEngine,
)
from .registry import (
    engine_ids,
    get_engine,
    get_engine_health,
    get_engine_registry,
    run_engine_demo,
)

__all__ = [
    # Base
    "EngineCapability",
    "EngineDemoResult",
    "EngineHealth",
    "EngineStatus",
    "LwaEngine",
    # Registry
    "engine_ids",
    "get_engine",
    "get_engine_health",
    "get_engine_registry",
    "run_engine_demo",
]
