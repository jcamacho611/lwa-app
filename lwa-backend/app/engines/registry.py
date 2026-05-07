"""
Engine Registry — Factory and lookup functions for all LWA backend engines.

Functions:
  get_engine_registry()     — returns metadata for all engines
  get_engine(engine_id)     — returns a single engine instance (or None)
  get_engine_health()       — returns health for all engines
  run_engine_demo(id, payload) — runs demo for a named engine
  engine_ids()              — returns list of all engine IDs
"""

from __future__ import annotations

from typing import Any

from .base import EngineDemoResult, EngineHealth, LwaEngine
from .brain import BrainEngine
from .creator import CreatorEngine
from .marketplace import MarketplaceEngine
from .operator_admin import OperatorAdminEngine
from .proof_history import ProofHistoryEngine
from .render import RenderEngine
from .safety import SafetyEngine
from .social_distribution import SocialDistributionEngine
from .wallet_entitlements import WalletEntitlementsEngine
from .world_game import WorldGameEngine

# ---------------------------------------------------------------------------
# Registry — ordered list of all engine instances
# ---------------------------------------------------------------------------

_ENGINES: list[LwaEngine] = [
    CreatorEngine(),
    BrainEngine(),
    RenderEngine(),
    MarketplaceEngine(),
    WalletEntitlementsEngine(),
    ProofHistoryEngine(),
    WorldGameEngine(),
    SafetyEngine(),
    SocialDistributionEngine(),
    OperatorAdminEngine(),
]

_ENGINE_MAP: dict[str, LwaEngine] = {e.engine_id: e for e in _ENGINES}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def engine_ids() -> list[str]:
    """Return the list of all registered engine IDs."""
    return [e.engine_id for e in _ENGINES]


def get_engine(engine_id: str) -> LwaEngine | None:
    """Return the engine instance for the given ID, or None if not found."""
    return _ENGINE_MAP.get(engine_id)


def get_engine_registry() -> list[dict[str, Any]]:
    """Return metadata dicts for all registered engines."""
    return [e.metadata() for e in _ENGINES]


def get_engine_health() -> list[EngineHealth]:
    """Return health snapshots for all registered engines."""
    return [e.health() for e in _ENGINES]


def run_engine_demo(engine_id: str, payload: dict[str, Any]) -> EngineDemoResult:
    """
    Run the demo for the named engine.

    Raises:
        KeyError: if engine_id is not registered.
    """
    engine = _ENGINE_MAP.get(engine_id)
    if engine is None:
        raise KeyError(f"Engine '{engine_id}' not found in registry. "
                       f"Available: {list(_ENGINE_MAP.keys())}")
    return engine.demo_run(payload)
