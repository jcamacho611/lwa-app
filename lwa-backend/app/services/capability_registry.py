from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel

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


class RailwayServicePlan(BaseModel):
    current_services: list[RailwayServiceRecommendation]
    future_services: list[RailwayServiceRecommendation]
    current_assessment: str
    generated_asset_warning: str
    next_check: str


_CAPABILITY_PATH = Path(__file__).resolve().parents[1] / "data" / "capabilities" / "lwa_capabilities.json"


@lru_cache(maxsize=1)
def load_capabilities() -> list[CapabilityRecord]:
    payload = json.loads(_CAPABILITY_PATH.read_text(encoding="utf-8"))
    return [CapabilityRecord.model_validate(item) for item in payload]


def list_capabilities() -> list[CapabilityRecord]:
    return list(load_capabilities())


def get_capability(capability_id: str) -> CapabilityRecord | None:
    return next((item for item in load_capabilities() if item.id == capability_id), None)


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
            ),
            RailwayServiceRecommendation(
                service_name="lwa-worker-ingest",
                status="future",
                when_to_add="When Twitch, YouTube, or authorized imports need background ingestion.",
                purpose=["source downloads", "stream/chat collectors", "authorized imports"],
            ),
            RailwayServiceRecommendation(
                service_name="lwa-scheduler",
                status="future",
                when_to_add="When recurring cleanup, trend refresh, and reporting need their own schedule.",
                purpose=["asset cleanup", "usage cleanup", "trend refresh", "daily reports"],
            ),
            RailwayServiceRecommendation(
                service_name="lwa-webhooks",
                status="future",
                when_to_add="When Whop, Twitch, or external webhook traffic becomes meaningful.",
                purpose=["webhook verification", "membership events", "ingestion callbacks"],
            ),
            RailwayServiceRecommendation(
                service_name="postgres",
                status="future",
                when_to_add="When accounts, workspaces, and campaigns require durable relational state.",
                purpose=["users", "workspaces", "campaigns", "team state"],
            ),
            RailwayServiceRecommendation(
                service_name="redis",
                status="future",
                when_to_add="When shared queues, rate limits, and worker coordination need fast shared state.",
                purpose=["queue coordination", "shared rate limiting", "worker orchestration"],
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
