"""Runtime selector for dedicated LWA Railway engine services."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, Mapping, Optional

from app.engines.registry import engine_ids, get_engine, run_engine_demo

DEFAULT_ENGINE_ID = "operator_admin"
ENV_VAR_NAME = "LWA_ENGINE_SERVICE_ID"


@dataclass(frozen=True)
class EngineRuntimeSelection:
    requested_engine_id: Optional[str]
    selected_engine_id: str
    valid: bool
    warning: Optional[str] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "env_var": ENV_VAR_NAME,
            "requested_engine_id": self.requested_engine_id,
            "selected_engine_id": self.selected_engine_id,
            "valid": self.valid,
            "warning": self.warning,
            "error": self.error,
            "available_engine_ids": engine_ids(),
        }


def get_selected_engine_id() -> str:
    raw_engine_id = os.getenv(ENV_VAR_NAME)
    if not raw_engine_id or not raw_engine_id.strip():
        return DEFAULT_ENGINE_ID
    return raw_engine_id.strip()


def get_runtime_selection() -> EngineRuntimeSelection:
    raw_engine_id = os.getenv(ENV_VAR_NAME)
    requested_engine_id = raw_engine_id.strip() if raw_engine_id and raw_engine_id.strip() else None
    selected_engine_id = requested_engine_id or DEFAULT_ENGINE_ID

    if requested_engine_id is None:
        return EngineRuntimeSelection(
            requested_engine_id=None,
            selected_engine_id=DEFAULT_ENGINE_ID,
            valid=True,
            warning=f"{ENV_VAR_NAME} is not set. Defaulting to {DEFAULT_ENGINE_ID}.",
        )

    if get_engine(selected_engine_id) is None:
        return EngineRuntimeSelection(
            requested_engine_id=requested_engine_id,
            selected_engine_id=selected_engine_id,
            valid=False,
            error=f"Unknown LWA engine service id: {selected_engine_id}",
        )

    return EngineRuntimeSelection(
        requested_engine_id=requested_engine_id,
        selected_engine_id=selected_engine_id,
        valid=True,
    )


def get_selected_engine():
    selection = get_runtime_selection()
    if not selection.valid:
        return None
    return get_engine(selection.selected_engine_id)


def selected_engine_metadata() -> Dict[str, Any]:
    selection = get_runtime_selection()
    engine = get_selected_engine()
    if engine is None:
        return {
            "runtime": selection.to_dict(),
            "engine": None,
            "status": "configuration_error",
        }
    return {
        "runtime": selection.to_dict(),
        "engine": engine.metadata(),
        "status": "ok",
    }


def selected_engine_health() -> Dict[str, Any]:
    selection = get_runtime_selection()
    engine = get_selected_engine()
    if engine is None:
        return {
            "runtime": selection.to_dict(),
            "healthy": False,
            "status": "configuration_error",
            "error": selection.error,
        }
    health = engine.health().to_dict()
    health["runtime"] = selection.to_dict()
    return health


def run_selected_engine_demo(payload: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    selection = get_runtime_selection()
    if not selection.valid:
        return {
            "runtime": selection.to_dict(),
            "status": "configuration_error",
            "summary": "Selected LWA engine is invalid.",
            "input_echo": dict(payload or {}),
            "output": {
                "external_action_executed": False,
                "paid_provider_called": False,
                "payment_or_payout_executed": False,
                "crypto_or_blockchain_action_executed": False,
                "social_post_executed": False,
            },
            "warnings": [selection.error or "Invalid engine configuration"],
            "next_required_integrations": ["Set a valid LWA_ENGINE_SERVICE_ID"],
        }

    result = run_engine_demo(selection.selected_engine_id, payload)
    response = result.to_dict()
    response["runtime"] = selection.to_dict()
    return response
