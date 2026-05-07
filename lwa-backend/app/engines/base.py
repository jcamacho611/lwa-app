from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Literal

EngineStatus = Literal["scaffolded", "local_ready", "backend_ready", "provider_ready", "production_ready"]


@dataclass(frozen=True)
class BackendEngineCapability:
    id: str
    label: str
    description: str
    local_only: bool = True
    requires_provider: bool = False
    requires_persistence: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def capability(
    id: str,
    label: str,
    description: str,
    *,
    local_only: bool = True,
    requires_provider: bool = False,
    requires_persistence: bool = False,
) -> BackendEngineCapability:
    return BackendEngineCapability(
        id=id,
        label=label,
        description=description,
        local_only=local_only,
        requires_provider=requires_provider,
        requires_persistence=requires_persistence,
    )


def _coerce_payload(payload: dict[str, Any] | None) -> dict[str, Any]:
    return dict(payload or {})


def build_demo_result(
    *,
    summary: str,
    output: dict[str, Any],
    warnings: list[str] | tuple[str, ...] = (),
    status: str = "demo_ready",
) -> dict[str, Any]:
    return {
        "status": status,
        "summary": summary,
        "output": output,
        "warnings": list(warnings),
    }


@dataclass(frozen=True)
class BackendEngine:
    engine_id: str
    name: str
    status: EngineStatus
    capabilities_list: tuple[BackendEngineCapability, ...]
    next_required_integrations_list: tuple[str, ...]
    demo_summary: str
    demo_runner: Callable[[dict[str, Any]], dict[str, Any]]
    demo_warning: str | None = None
    _reserved: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    def health(self) -> dict[str, Any]:
        healthy = self.status != "scaffolded"
        warnings: list[str] = []
        if self.status == "scaffolded":
            warnings.append("Scaffolded engine: local demo only.")
        if self.next_required_integrations_list:
            warnings.extend(self.next_required_integrations_list)
        if self.demo_warning:
            warnings.append(self.demo_warning)
        return {
            "engine_id": self.engine_id,
            "name": self.name,
            "status": self.status,
            "healthy": healthy,
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "warnings": warnings,
            "blocked_integrations": list(self.next_required_integrations_list),
        }

    def capabilities(self) -> list[dict[str, Any]]:
        return [item.to_dict() for item in self.capabilities_list]

    def next_required_integrations(self) -> list[str]:
        return list(self.next_required_integrations_list)

    def demo_run(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        input_echo = _coerce_payload(payload)
        result = dict(self.demo_runner(input_echo) or {})
        return {
            "engine_id": self.engine_id,
            "name": self.name,
            "status": result.get("status", "demo_ready"),
            "summary": str(result.get("summary") or self.demo_summary),
            "input_echo": input_echo,
            "output": dict(result.get("output") or {}),
            "warnings": list(result.get("warnings") or ([] if not self.demo_warning else [self.demo_warning])),
            "next_required_integrations": list(self.next_required_integrations_list),
        }

    def to_registry_record(self) -> dict[str, Any]:
        return {
            "engine_id": self.engine_id,
            "name": self.name,
            "status": self.status,
            "capabilities": self.capabilities(),
            "next_required_integrations": self.next_required_integrations(),
            "health": self.health(),
        }
