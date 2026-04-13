from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Request

from ...dependencies.auth import get_platform_store, require_user
from ...models.schemas import CampaignCreateRequest, CampaignPatchRequest

router = APIRouter(prefix="/v1/campaigns", tags=["campaigns"])
platform_store = get_platform_store()
logger = logging.getLogger("uvicorn.error")


@router.post("")
async def create_campaign(payload: CampaignCreateRequest, request: Request) -> dict[str, object]:
    user = require_user(request)
    campaign = platform_store.create_campaign(
        user_id=user.id,
        name=payload.title,
        description=payload.description,
        allowed_platforms=payload.allowed_platforms,
        target_angle=payload.target_angle,
        requirements=payload.requirements,
        payout_cents_per_1000_views=payload.payout_cents_per_1000_views,
    )
    logger.info("campaign_created user_id=%s campaign_id=%s", user.id, campaign["id"])
    return campaign


@router.get("")
async def list_campaigns(request: Request) -> dict[str, object]:
    user = require_user(request)
    return {"campaigns": platform_store.list_campaigns(user_id=user.id)}


@router.get("/{campaign_id}")
async def get_campaign(campaign_id: str, request: Request) -> dict[str, object]:
    user = require_user(request)
    campaign = platform_store.get_campaign(campaign_id=campaign_id, user_id=user.id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


@router.patch("/{campaign_id}")
async def update_campaign(campaign_id: str, payload: CampaignPatchRequest, request: Request) -> dict[str, object]:
    user = require_user(request)
    updates = payload.model_dump(exclude_none=True)
    if "title" in updates:
        updates["name"] = updates.pop("title")
    campaign = platform_store.update_campaign(campaign_id=campaign_id, user_id=user.id, updates=updates)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign
