"""
LWA Engine Base — Abstract foundation for all backend engines.

All engines inherit from LwaEngine and implement:
  - capabilities()
  - demo_run(payload)
  - next_required_integrations()
  - health_warnings()

No engine at SCAFFOLDED or LOCAL_READY status executes payments,
provider calls, social posting, or any external mutation.
"""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# ---------------------------------------------------------------------------
# Status enum
# ---------------------------------------------------------------------------

class EngineStatus(str, Enum):
    """Lifecycle status for a backend engine module."""

    SCAFFOLDED = "SCAFFOLDED"
    """Shape defined; no real logic yet."""

    LOCAL_READY = "LOCAL_READY"
    """Deterministic local logic works; no external provider needed."""

    BACKEND_READY = "BACKEND_READY"
    """Integrated with internal backend services (DB, job queue, etc.)."""

    PROVIDER_READY = "PROVIDER_READY"
    """Connected to at least one external provider (AI, payment, social)."""

    PRODUCTION_READY = "PRODUCTION_READY"
    """Fully tested, monitored, and safe for production traffic."""


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class EngineCapability:
    """Describes a single capability exposed by an engine."""

    name: str
    description: str
    local_safe: bool = True
    requires_provider: bool = False
    requires_payment: bool = False


@dataclass
class EngineHealth:
    """Health snapshot for an engine."""

    engine_id: str
    status: EngineStatus
    healthy: bool
    warnings: list[str] = field(default_factory=list)
    notes: str = ""


@dataclass
class EngineDemoResult:
    """Result returned by a demo_run() call."""

    engine_id: str
    status: EngineStatus
    summary: str
    input_echo: dict[str, Any]
    output: dict[str, Any]
    warnings: list[str] = field(default_factory=list)
    next_required_integrations: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Payload helpers
# ---------------------------------------------------------------------------

def safe_payload(payload: Any) -> dict[str, Any]:
    """Coerce payload to a plain dict; never raises."""
    if isinstance(payload, dict):
        return payload
    return {}


def text_value(payload: dict[str, Any], key: str, default: str = "") -> str:
    """Extract a string value from a payload dict safely."""
    val = payload.get(key, default)
    return str(val) if val is not None else default


def number_value(payload: dict[str, Any], key: str, default: float = 0.0) -> float:
    """Extract a numeric value from a payload dict safely."""
    val = payload.get(key, default)
    try:
        return float(val)
    except (TypeError, ValueError):
        return default


# ---------------------------------------------------------------------------
# Abstract base class
# ---------------------------------------------------------------------------

class LwaEngine(abc.ABC):
    """Abstract base class for all LWA backend engines."""

    @property
    @abc.abstractmethod
    def engine_id(self) -> str:
        """Unique snake_case identifier for this engine."""

    @property
    @abc.abstractmethod
    def display_name(self) -> str:
        """Human-readable name."""

    @property
    @abc.abstractmethod
    def description(self) -> str:
        """One-sentence description of what this engine does."""

    @property
    @abc.abstractmethod
    def status(self) -> EngineStatus:
        """Current lifecycle status."""

    @abc.abstractmethod
    def capabilities(self) -> list[EngineCapability]:
        """Return the list of capabilities this engine exposes."""

    @abc.abstractmethod
    def demo_run(self, payload: dict[str, Any]) -> EngineDemoResult:
        """
        Execute a safe, local, deterministic demo of this engine.

        Must NOT:
        - Execute payments or payouts
        - Call external AI providers
        - Post to social platforms
        - Write to a production database
        - Require any secrets or environment variables
        """

    @abc.abstractmethod
    def next_required_integrations(self) -> list[str]:
        """Return what integrations are needed to advance this engine's status."""

    @abc.abstractmethod
    def health_warnings(self) -> list[str]:
        """Return any current health warnings (empty list = healthy)."""

    # ------------------------------------------------------------------
    # Concrete helpers
    # ------------------------------------------------------------------

    def health(self) -> EngineHealth:
        """Return a health snapshot for this engine."""
        warnings = self.health_warnings()
        return EngineHealth(
            engine_id=self.engine_id,
            status=self.status,
            healthy=len(warnings) == 0,
            warnings=warnings,
            notes=f"Status: {self.status.value}",
        )

    def metadata(self) -> dict[str, Any]:
        """Return a serialisable metadata dict for this engine."""
        return {
            "engine_id": self.engine_id,
            "display_name": self.display_name,
            "description": self.description,
            "status": self.status.value,
            "capabilities": [
                {
                    "name": c.name,
                    "description": c.description,
                    "local_safe": c.local_safe,
                    "requires_provider": c.requires_provider,
                    "requires_payment": c.requires_payment,
                }
                for c in self.capabilities()
            ],
            "next_required_integrations": self.next_required_integrations(),
            "health_warnings": self.health_warnings(),
        }
