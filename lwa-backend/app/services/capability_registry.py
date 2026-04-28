from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

CapabilityStatus = Literal["live", "partial", "planned", "blocked", "intentionally_unsupported"]
PublicClaim = Literal["allowed", "careful", "not_allowed"]
Priority = Literal["P0", "P1", "P2", "P3"]


class CapabilityRecord(BaseModel):
    id: str
    name: str
    category: str
    status: CapabilityStatus
    public_claim: PublicClaim
    current_truth: str
    missing_piece: str
    next_step: str
    owner_role: str
    backend_needed: bool
    frontend_needed: bool
    ios_needed: bool
    railway_service_needed: bool
    recommended_service_name: str | None = None
    priority: Priority
    user_facing_copy: str
    internal_notes: str


class RailwayServiceRecommendation(BaseModel):
    service_name: str
    status: Literal["current", "future", "unknown"]
    when_to_add: str
    purpose: list[str]
    required_now: bool = False
    capability_ids: list[str] = Field(default_factory=list)


class RailwayServicePlan(BaseModel):
    current_services: list[RailwayServiceRecommendation]
    future_services: list[RailwayServiceRecommendation]
    current_assessment: str
    generated_asset_warning: str
    next_check: str


class CapabilityCatalogResponse(BaseModel):
    items: list[CapabilityRecord]
    count: int
    status_counts: dict[str, int]
    public_claim_counts: dict[str, int]


class CapabilityStatusResponse(BaseModel):
    status: CapabilityStatus
    items: list[CapabilityRecord]
    count: int


class PublicClaimsResponse(BaseModel):
    allowed: list[CapabilityRecord]
    careful: list[CapabilityRecord]
    not_allowed: list[CapabilityRecord]
    summary: dict[str, int]


_CAPABILITY_PATH = Path(__file__).resolve().parents[1] / "data" / "capabilities" / "lwa_capabilities.json"
_VALID_STATUSES: tuple[CapabilityStatus, ...] = (
    "live",
    "partial",
    "planned",
    "blocked",
    "intentionally_unsupported",
)


def clear_capability_cache() -> None:
    load_capabilities.cache_clear()


def validate_capabilities(records: list[CapabilityRecord]) -> None:
    seen_ids: set[str] = set()
    for record in records:
        if record.id in seen_ids:
            raise ValueError(f"Duplicate capability id: {record.id}")
        seen_ids.add(record.id)
        if record.status == "intentionally_unsupported" and record.public_claim == "allowed":
            raise ValueError(
                f"Capability {record.id} cannot be intentionally unsupported and publicly allowed"
            )
        if record.railway_service_needed and not record.recommended_service_name:
            raise ValueError(
                f"Capability {record.id} needs a Railway service recommendation"
            )


@lru_cache(maxsize=1)
def load_capabilities() -> list[CapabilityRecord]:
    payload = json.loads(_CAPABILITY_PATH.read_text(encoding="utf-8"))
    records = [CapabilityRecord.model_validate(item) for item in payload]
    validate_capabilities(records)
    return records


def list_capabilities() -> list[CapabilityRecord]:
    return list(load_capabilities())


def get_capability(capability_id: str) -> CapabilityRecord | None:
    return next((item for item in load_capabilities() if item.id == capability_id), None)


def known_statuses() -> tuple[CapabilityStatus, ...]:
    return _VALID_STATUSES


def list_capabilities_by_status(status: CapabilityStatus) -> list[CapabilityRecord]:
    return [item for item in load_capabilities() if item.status == status]


def public_claim_groups() -> dict[PublicClaim, list[CapabilityRecord]]:
    grouped: dict[PublicClaim, list[CapabilityRecord]] = {
        "allowed": [],
        "careful": [],
        "not_allowed": [],
    }
    for item in load_capabilities():
        grouped[item.public_claim].append(item)
    return grouped


def capability_catalog() -> CapabilityCatalogResponse:
    items = list_capabilities()
    status_counts = {status: len([item for item in items if item.status == status]) for status in _VALID_STATUSES}
    public_claim_counts = {
        claim: len([item for item in items if item.public_claim == claim])
        for claim in ("allowed", "careful", "not_allowed")
    }
    return CapabilityCatalogResponse(
        items=items,
        count=len(items),
        status_counts=status_counts,
        public_claim_counts=public_claim_counts,
    )


def capability_status_payload(status: CapabilityStatus) -> CapabilityStatusResponse:
    items = list_capabilities_by_status(status)
    return CapabilityStatusResponse(status=status, items=items, count=len(items))


def public_claim_payload() -> PublicClaimsResponse:
    grouped = public_claim_groups()
    return PublicClaimsResponse(
        allowed=grouped["allowed"],
        careful=grouped["careful"],
        not_allowed=grouped["not_allowed"],
        summary={
            "allowed": len(grouped["allowed"]),
            "careful": len(grouped["careful"]),
            "not_allowed": len(grouped["not_allowed"]),
        },
    )


def _capability_ids_for_service(service_name: str) -> list[str]:
    return [
        item.id
        for item in load_capabilities()
        if item.recommended_service_name == service_name
    ]


def railway_service_plan() -> RailwayServicePlan:
    return RailwayServicePlan(
        current_services=[
            RailwayServiceRecommendation(
                service_name="lwa the god app",
                status="current",
                when_to_add="Already online as the frontend experience.",
                purpose=["Next.js web app", "homepage", "workspace pages", "operator-facing UI"],
                required_now=True,
            ),
            RailwayServiceRecommendation(
                service_name="lwa-backend",
                status="current",
                when_to_add="Already online as the API and clipping engine.",
                purpose=["FastAPI routes", "generation", "uploads", "quota", "campaign and wallet APIs"],
                required_now=True,
                capability_ids=[
                    item.id
                    for item in load_capabilities()
                    if item.backend_needed and not item.recommended_service_name
                ],
            ),
            RailwayServiceRecommendation(
                service_name="function-bun",
                status="unknown",
                when_to_add="Inspect before using or deleting.",
                purpose=["Unknown legacy or experimental worker/function slot"],
                required_now=False,
            ),
        ],
        future_services=[
            RailwayServiceRecommendation(
                service_name="lwa-worker-render",
                status="future",
                when_to_add="When FFmpeg and export rendering begin to block the API or queue length grows.",
                purpose=["video rendering", "caption burn-in", "thumbnail jobs", "export profiles"],
                capability_ids=_capability_ids_for_service("lwa-worker-render"),
            ),
            RailwayServiceRecommendation(
                service_name="lwa-worker-ingest",
                status="future",
                when_to_add="When Twitch, YouTube, or authorized imports need background ingestion.",
                purpose=["source downloads", "stream/chat collectors", "authorized imports"],
                capability_ids=_capability_ids_for_service("lwa-worker-ingest"),
            ),
            RailwayServiceRecommendation(
                service_name="lwa-scheduler",
                status="future",
                when_to_add="When recurring cleanup, trend refresh, and reporting need their own schedule.",
                purpose=["asset cleanup", "usage cleanup", "trend refresh", "daily reports"],
                capability_ids=_capability_ids_for_service("lwa-scheduler"),
            ),
            RailwayServiceRecommendation(
                service_name="lwa-webhooks",
                status="future",
                when_to_add="When Whop, Twitch, or external webhook traffic becomes meaningful.",
                purpose=["webhook verification", "membership events", "ingestion callbacks"],
                capability_ids=_capability_ids_for_service("lwa-webhooks"),
            ),
            RailwayServiceRecommendation(
                service_name="postgres",
                status="future",
                when_to_add="When accounts, workspaces, and campaigns require durable relational state.",
                purpose=["users", "workspaces", "campaigns", "team state"],
                capability_ids=_capability_ids_for_service("postgres"),
            ),
            RailwayServiceRecommendation(
                service_name="redis",
                status="future",
                when_to_add="When shared queues, rate limits, and worker coordination need fast shared state.",
                purpose=["queue coordination", "shared rate limiting", "worker orchestration"],
                capability_ids=_capability_ids_for_service("redis"),
            ),
        ],
        current_assessment=(
            "Three visible Railway services are not automatically a problem. "
            "What matters now is frontend/backend health, generated-asset retention, and whether the sleeping function-bun service is still needed."
        ),
        generated_asset_warning=(
            "Treat the backend generated-asset volume warning as P0 until retention is verified in production. "
            "Keep asset retention, storage monitoring, and cleanup env vars in the deployment checklist."
        ),
        next_check=(
            "Verify generated asset cleanup on Railway, inspect function-bun usage, and only add workers when load or integration scope requires it."
        ),
    )
