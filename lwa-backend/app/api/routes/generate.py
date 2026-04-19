from __future__ import annotations

import logging
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Request

from ...core.config import get_settings
from ...dependencies.auth import get_optional_user, get_platform_store
from ...job_store import JobStore, RequestThrottle
from ...models.schemas import (
    ClipBatchResponse,
    JobCreatedResponse,
    JobStatusResponse,
    ProcessRequest,
    TrendsResponse,
)
from ...models.user import UserRecord
from ...services.clip_service import (
    build_clip_response,
    dependency_health,
    enforce_api_key,
    get_live_trends,
    provider_health,
    run_job,
)
from ...services.entitlements import UsageStore, resolve_entitlement

router = APIRouter()
settings = get_settings()
job_store = JobStore()
request_throttle = RequestThrottle(
    window_seconds=settings.abuse_window_seconds,
    max_requests=settings.abuse_max_generation_requests,
)
usage_store = UsageStore(settings.usage_store_path)
platform_store = get_platform_store()
logger = logging.getLogger("uvicorn.error")


@router.get("/")
async def root() -> dict[str, object]:
    return {
        "status": "ok",
        "service": settings.app_name,
    }


@router.get("/health")
@router.get("/v1/status/health")
async def health_check() -> dict[str, object]:
    return {
        "status": "ok",
        "dependencies": dependency_health(settings),
        "providers": provider_health(settings),
    }


@router.get("/v1/trends", response_model=TrendsResponse)
async def get_trends(http_request: Request) -> TrendsResponse:
    enforce_api_key(http_request, settings)
    return await get_live_trends()


@router.post("/generate", response_model=ClipBatchResponse)
@router.post("/process", response_model=ClipBatchResponse)
@router.post("/v1/generate", response_model=ClipBatchResponse)
async def generate_clips(request: ProcessRequest, http_request: Request) -> ClipBatchResponse:
    enforce_api_key(http_request, settings)
    current_user = get_optional_user(http_request)
    resolved_request, source_path = resolve_request_source(
        request=request,
        current_user=current_user,
        base_url=(settings.api_base_url or str(http_request.base_url)).rstrip("/"),
    )
    entitlement = resolve_entitlement(
        request=http_request,
        settings=settings,
        usage_store=usage_store,
        current_user=current_user,
    )
    await enforce_generation_throttle(entitlement=entitlement)
    request_id = f"req_{uuid4().hex[:10]}"
    public_base_url = (settings.api_base_url or str(http_request.base_url)).rstrip("/")
    logger.info(
        "route_generate request_id=%s route=%s target_platform=%s video_url=%s plan=%s subject_source=%s",
        request_id,
        http_request.url.path,
        resolved_request.target_platform or "auto",
        resolved_request.video_url,
        entitlement.plan.code,
        entitlement.subject_source,
    )
    try:
        return await build_clip_response(
            settings=settings,
            request_id=request_id,
            request=resolved_request,
            public_base_url=public_base_url,
            route_path=http_request.url.path,
            entitlement=entitlement,
            current_user=current_user,
            platform_store=platform_store,
            source_path=source_path,
        )
    except HTTPException:
        # Re-raise HTTP exceptions (including 402 quota errors) without releasing usage,
        # since the quota was already consumed by resolve_entitlement.
        raise
    except Exception:
        usage_store.release(subject=entitlement.subject, usage_day=entitlement.usage_day)
        raise


@router.post("/v1/jobs", response_model=JobCreatedResponse)
async def create_processing_job(request: ProcessRequest, http_request: Request) -> JobCreatedResponse:
    enforce_api_key(http_request, settings)
    current_user = get_optional_user(http_request)
    resolved_request, source_path = resolve_request_source(
        request=request,
        current_user=current_user,
        base_url=(settings.api_base_url or str(http_request.base_url)).rstrip("/"),
    )
    entitlement = resolve_entitlement(
        request=http_request,
        settings=settings,
        usage_store=usage_store,
        current_user=current_user,
    )
    await enforce_generation_throttle(entitlement=entitlement)
    job_id = f"job_{uuid4().hex[:10]}"
    public_base_url = (settings.api_base_url or str(http_request.base_url)).rstrip("/")
    logger.info(
        "route_job request_id=%s route=%s target_platform=%s video_url=%s plan=%s subject_source=%s",
        job_id,
        http_request.url.path,
        resolved_request.target_platform or "auto",
        resolved_request.video_url,
        entitlement.plan.code,
        entitlement.subject_source,
    )
    await job_store.create(job_id, "Job queued. Starting source analysis.")
    platform_store.create_job(
        job_id=job_id,
        user_id=current_user.id if current_user else None,
        campaign_id=None,
        source_type=resolved_request.source_type or ("upload" if resolved_request.upload_file_id else "url"),
        source_value=resolved_request.video_url or "",
        status="queued",
        message="Job queued. Starting source analysis.",
    )
    import asyncio

    asyncio.create_task(
        run_job(
            settings=settings,
            job_store=job_store,
            usage_store=usage_store,
            job_id=job_id,
            request=resolved_request,
            public_base_url=public_base_url,
            route_path=http_request.url.path,
            entitlement=entitlement,
            current_user=current_user,
            platform_store=platform_store,
            source_path=source_path,
        )
    )
    return JobCreatedResponse(
        job_id=job_id,
        status="queued",
        poll_url=f"{public_base_url}/v1/jobs/{job_id}",
        message="Job queued. Poll for results.",
    )


@router.get("/v1/jobs/{job_id}", response_model=JobStatusResponse)
async def get_processing_job(job_id: str, http_request: Request) -> JobStatusResponse:
    enforce_api_key(http_request, settings)
    record = await job_store.get(job_id)
    if not record:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobStatusResponse(
        job_id=record.id,
        status=record.status,
        message=record.message,
        created_at=record.created_at,
        updated_at=record.updated_at,
        result=record.result,
        error=record.error,
    )


def resolve_request_source(
    *,
    request: ProcessRequest,
    current_user: UserRecord | None,
    base_url: str,
) -> tuple[ProcessRequest, str | None]:
    if request.upload_file_id:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required for uploaded sources")
        upload = platform_store.get_upload(request.upload_file_id, user_id=current_user.id)
        if not upload:
            raise HTTPException(status_code=404, detail="Upload not found")
        source_type = classify_upload_source(upload)
        resolved = request.model_copy(
            update={
                "video_url": upload["public_url"],
                "source_type": source_type,
                "upload_content_type": upload.get("content_type"),
            }
        )
        return resolved, upload["stored_path"]

    if not request.video_url:
        raise HTTPException(status_code=422, detail="Provide video_url or upload_file_id")

    return request.model_copy(update={"source_type": request.source_type or "url"}), None


def classify_upload_source(upload: dict[str, object]) -> str:
    content_type = str(upload.get("content_type") or "").lower()
    filename = str(upload.get("file_name") or "")
    suffix = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""

    if content_type.startswith("audio/") or suffix in {"mp3", "wav", "m4a", "aac", "ogg", "oga", "flac"}:
        return "audio_upload"
    if content_type.startswith("image/") or suffix in {"jpg", "jpeg", "png", "webp", "heic", "heif"}:
        return "image_upload"
    return "video_upload"


async def enforce_generation_throttle(*, entitlement) -> None:
    try:
        await request_throttle.enforce(subject=entitlement.subject)
    except HTTPException:
        usage_store.release(subject=entitlement.subject, usage_day=entitlement.usage_day)
        raise
