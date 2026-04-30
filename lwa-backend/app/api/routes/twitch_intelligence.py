from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from ...services.twitch_intelligence_core import rank_twitch_moments

# LWA OMEGA
# CLAUDE HANDOFF
# TWITCH INTELLIGENCE FOUNDATION
# NONFATAL PIPELINE

router = APIRouter(prefix="/v1/twitch-intelligence", tags=["twitch-intelligence"])


class TwitchMomentRequest(BaseModel):
    moments: list[dict] = Field(default_factory=list)
    limit: int = 10


@router.get("")
def twitch_intelligence_index() -> dict[str, object]:
    return {
        "ok": True,
        "status": "foundation",
        "supported": ["rank_moments"],
        "note": "Local Twitch intelligence foundation only; no live Twitch ingestion or API posting.",
    }


@router.post("/rank-moments")
def rank_moments(request: TwitchMomentRequest) -> dict[str, object]:
    return {"items": rank_twitch_moments(request.moments, limit=max(1, min(request.limit, 50)))}
