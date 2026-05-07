"""Local-safe engine contracts for dedicated LWA Railway engine services.

This module is intentionally deterministic and provider-free. Demo endpoints must
not execute payouts, mutate balances, call paid providers, post externally, or
perform irreversible marketplace/social/crypto actions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Mapping, Optional


class EngineStatus(str, Enum):
    SCAFFOLDED = "scaffolded"
    LOCAL_READY = "local_ready"
    BACKEND_READY = "backend_ready"
    PROVIDER_READY = "provider_ready"
    PRODUCTION_READY = "production_ready"


@dataclass(frozen=True)
class EngineCapability:
    id: str
    label: str
    description: str
    local_only: bool = True
    requires_provider: bool = False
    requires_persistence: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "label": self.label,
            "description": self.description,
            "local_only": self.local_only,
            "requires_provider": self.requires_provider,
            "requires_persistence": self.requires_persistence,
        }


@dataclass(frozen=True)
class EngineHealth:
    engine_id: str
    name: str
    status: EngineStatus
    healthy: bool
    checked_at: str
    warnings: List[str] = field(default_factory=list)
    blocked_integrations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "engine_id": self.engine_id,
            "name": self.name,
            "status": self.status.value,
            "healthy": self.healthy,
            "checked_at": self.checked_at,
            "warnings": list(self.warnings),
            "blocked_integrations": list(self.blocked_integrations),
        }


@dataclass(frozen=True)
class EngineDemoResult:
    engine_id: str
    status: str
    summary: str
    input_echo: Mapping[str, Any]
    output: Mapping[str, Any]
    warnings: List[str] = field(default_factory=list)
    next_required_integrations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "engine_id": self.engine_id,
            "status": self.status,
            "summary": self.summary,
            "input_echo": dict(self.input_echo),
            "output": dict(self.output),
            "warnings": list(self.warnings),
            "next_required_integrations": list(self.next_required_integrations),
        }


class LwaEngine:
    engine_id: str = "base"
    name: str = "Base Engine"
    status: EngineStatus = EngineStatus.LOCAL_READY
    description: str = "Local-safe LWA engine."

    def health(self) -> EngineHealth:
        return EngineHealth(
            engine_id=self.engine_id,
            name=self.name,
            status=self.status,
            healthy=self.status != EngineStatus.SCAFFOLDED,
            checked_at=datetime.now(timezone.utc).isoformat(),
            warnings=self.health_warnings(),
            blocked_integrations=self.next_required_integrations(),
        )

    def health_warnings(self) -> List[str]:
        return []

    def capabilities(self) -> List[EngineCapability]:
        return [
            EngineCapability(
                id="safe_demo",
                label="Safe Demo",
                description="Returns deterministic demo data without external actions.",
            )
        ]

    def next_required_integrations(self) -> List[str]:
        return ["persistent storage", "operator dashboard", "production safety review"]

    def metadata(self) -> Dict[str, Any]:
        return {
            "engine_id": self.engine_id,
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "capabilities": [capability.to_dict() for capability in self.capabilities()],
            "next_required_integrations": self.next_required_integrations(),
            "health": self.health().to_dict(),
        }

    def demo_run(self, payload: Optional[Mapping[str, Any]] = None) -> EngineDemoResult:
        safe_payload = dict(payload or {})
        return EngineDemoResult(
            engine_id=self.engine_id,
            status="demo_only",
            summary=f"{self.name} returned a local-safe demo response.",
            input_echo=safe_payload,
            output={
                "engine_id": self.engine_id,
                "engine_name": self.name,
                "external_action_executed": False,
                "paid_provider_called": False,
                "payment_or_payout_executed": False,
                "crypto_or_blockchain_action_executed": False,
                "social_post_executed": False,
                "mode": "local_safe_demo",
            },
            warnings=self.health_warnings(),
            next_required_integrations=self.next_required_integrations(),
        )
