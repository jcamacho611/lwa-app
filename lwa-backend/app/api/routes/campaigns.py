from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Request

from ...dependencies.auth import get_platform_store, require_user
from ...models.schemas import (
    CampaignAssignmentCreateRequest,
    CampaignAssignmentPatchRequest,
    CampaignCreateRequest,
    CampaignPatchRequest,
)

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


@router.post("/{campaign_id}/assignments")
async def create_campaign_assignments(campaign_id: str, payload: CampaignAssignmentCreateRequest, request: Request) -> dict[str, object]:
    user = require_user(request)
    try:
        assignments = platform_store.create_campaign_assignments(
            campaign_id=campaign_id,
            user_id=user.id,
            request_id=payload.request_id,
            clip_ids=payload.clip_ids,
            target_platform=payload.target_platform,
            packaging_angle=payload.packaging_angle,
            assignee_role=payload.assignee_role or "creator",
            assignee_label=payload.assignee_label,
            note=payload.note,
            payout_amount_cents=payload.payout_amount_cents,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    logger.info("campaign_assignment_created user_id=%s campaign_id=%s assignments=%s", user.id, campaign_id, len(assignments))
    return {"assignments": assignments}


@router.patch("/{campaign_id}/assignments/{assignment_id}")
async def update_campaign_assignment(
    campaign_id: str,
    assignment_id: str,
    payload: CampaignAssignmentPatchRequest,
    request: Request,
) -> dict[str, object]:
    user = require_user(request)
    updates = payload.model_dump(exclude_none=True)
    assignment = platform_store.update_campaign_assignment(
        campaign_id=campaign_id,
        assignment_id=assignment_id,
        user_id=user.id,
        updates=updates,
    )
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    logger.info(
        "campaign_assignment_updated user_id=%s campaign_id=%s assignment_id=%s status=%s",
        user.id,
        campaign_id,
        assignment_id,
        assignment["status"],
    )
    return assignment
