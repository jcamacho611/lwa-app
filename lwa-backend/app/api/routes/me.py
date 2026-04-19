from __future__ import annotations

import asyncio
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Request

from ...core.config import get_settings
from ...dependencies.auth import get_platform_store, require_user
from ...models.schemas import ClipPatchRequest, ClipRecoveryJobResponse, ClipRecoveryStatusResponse
from ...services.clip_service import clip_record_needs_recovery, run_clip_recovery_job
from ...services.entitlements import EntitlementContext, get_plan_for_user, require_feature_access, usage_day_key

router = APIRouter(prefix="/v1/me", tags=["me"])
platform_store = get_platform_store()
settings = get_settings()


@router.get("/clip-packs")
async def list_clip_packs(request: Request) -> dict[str, object]:
    user = require_user(request)
    return {"clip_packs": platform_store.list_clip_packs(user_id=user.id)}


@router.get("/clip-packs/{request_id}")
async def get_clip_pack(request_id: str, request: Request) -> dict[str, object]:
    user = require_user(request)
    payload = platform_store.get_clip_pack(user_id=user.id, request_id=request_id)
    if not payload["clips"]:
        raise HTTPException(status_code=404, detail="Clip pack not found")
    return payload


@router.patch("/clips/{clip_id}")
async def patch_clip(clip_id: str, payload: ClipPatchRequest, request: Request) -> dict[str, object]:
    user = require_user(request)
    require_feature_access(
        settings=settings,
        user=user,
        feature_name="caption_editor",
        detail="Upgrade to Pro to edit hooks, captions, packaging, and trims from saved history.",
    )
    updated = platform_store.update_clip_metadata(
        clip_id=clip_id,
        user_id=user.id,
        updates=payload.model_dump(exclude_none=True),
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Clip not found")
    return updated


@router.post("/clips/{clip_id}/recover", response_model=ClipRecoveryJobResponse)
async def recover_clip(clip_id: str, request: Request) -> ClipRecoveryJobResponse:
    user = require_user(request)
    clip = platform_store.get_clip(clip_id=clip_id, user_id=user.id)
    if not clip:
        raise HTTPException(status_code=404, detail="Clip not found")
    if not clip_record_needs_recovery(clip):
        raise HTTPException(status_code=409, detail="This clip already has media proof. Recovery is only for strategy-only clips.")

    job_id = f"recover_{uuid4().hex[:12]}"
    public_base_url = (settings.api_base_url or str(request.base_url)).rstrip("/")
    plan = get_plan_for_user(settings=settings, user=user)
    platform_store.create_job(
        job_id=job_id,
        user_id=user.id,
        campaign_id=clip.get("campaign_id"),
        source_type="clip_recovery",
        source_value=clip_id,
        status="queued",
        message="Recovery queued. Retrying media generation for this clip.",
    )
    entitlement = EntitlementContext(
        subject=f"user:{user.id}",
        subject_source="user",
        usage_day=usage_day_key(),
        plan=plan,
        credits_remaining=max(plan.daily_limit, 0),
        user_id=user.id,
    )
    asyncio.create_task(
        run_clip_recovery_job(
            settings=settings,
            platform_store=platform_store,
            clip_record=clip,
            current_user=user,
            entitlement=entitlement,
            public_base_url=public_base_url,
            route_path=request.url.path,
            job_id=job_id,
        )
    )
    return ClipRecoveryJobResponse(
        job_id=job_id,
        clip_id=clip_id,
        status="queued",
        message="Recovery queued. Poll for clip status.",
        poll_url=f"{public_base_url}/v1/me/recovery-jobs/{job_id}",
    )


@router.get("/recovery-jobs/{job_id}", response_model=ClipRecoveryStatusResponse)
async def get_recovery_job(job_id: str, request: Request) -> ClipRecoveryStatusResponse:
    user = require_user(request)
    job = platform_store.get_job(job_id=job_id, user_id=user.id)
    if not job:
        raise HTTPException(status_code=404, detail="Recovery job not found")

    response_payload = job.get("response_json") if isinstance(job.get("response_json"), dict) else {}
    recovered_clip = response_payload.get("recovered_clip") if isinstance(response_payload, dict) else None
    error = response_payload.get("error") if isinstance(response_payload, dict) else None

    return ClipRecoveryStatusResponse(
        job_id=job["id"],
        clip_id=str(job["source_value"]),
        status=str(job["status"]),
        message=str(job["message"]),
        created_at=str(job["created_at"]),
        updated_at=str(job["updated_at"]),
        recovered_clip=recovered_clip,
        error=str(error) if error else None,
    )
