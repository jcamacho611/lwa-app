from __future__ import annotations

import logging
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Request

from ...core.config import get_settings
from ...job_store import JobStore
from ...models.schemas import (
    ClipBatchResponse,
    JobCreatedResponse,
    JobStatusResponse,
    ProcessRequest,
    TrendsResponse,
)
from ...services.clip_service import (
    build_clip_response,
    dependency_health,
    enforce_api_key,
    get_live_trends,
    run_job,
)
from ...services.entitlements import UsageStore, resolve_entitlement

router = APIRouter()
settings = get_settings()
job_store = JobStore()
usage_store = UsageStore(settings.usage_store_path)
logger = logging.getLogger("uvicorn.error")


@router.get("/")
async def root() -> dict[str, object]:
    base_url = settings.api_base_url or "http://127.0.0.1:8000"
    api_key_enabled = bool(settings.api_key_secret or settings.pro_api_keys or settings.scale_api_keys)
    return {
        "status": "ok",
        "service": settings.app_name,
        "environment": settings.environment,
        "docs_url": f"{base_url}/docs",
        "health_url": f"{base_url}/health",
        "generate_url": f"{base_url}/generate",
        "jobs_url": f"{base_url}/v1/jobs",
        "trends_url": f"{base_url}/v1/trends",
        "api_key_header": settings.api_key_header_name if api_key_enabled else None,
        "client_id_header": settings.client_id_header_name,
    }


@router.get("/health")
@router.get("/v1/status/health")
async def health_check() -> dict[str, object]:
    checks = dependency_health(settings)
    required_checks = [checks["ffmpeg"], checks["yt_dlp"]]
    overall_status = "ok" if all(required_checks) else "degraded"
    return {
        "status": overall_status,
        "service": settings.app_name,
        "environment": settings.environment,
        "version": settings.service_version,
        "port": settings.port,
        "dependencies": checks,
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
    entitlement = resolve_entitlement(
        request=http_request,
        settings=settings,
        usage_store=usage_store,
    )
    request_id = f"req_{uuid4().hex[:10]}"
    public_base_url = (settings.api_base_url or str(http_request.base_url)).rstrip("/")
    logger.info(
        "route_generate request_id=%s route=%s target_platform=%s video_url=%s plan=%s subject_source=%s",
        request_id,
        http_request.url.path,
        request.target_platform or "TikTok",
        request.video_url,
        entitlement.plan.code,
        entitlement.subject_source,
    )
    try:
        return await build_clip_response(
            settings=settings,
            request_id=request_id,
            request=request,
            public_base_url=public_base_url,
            route_path=http_request.url.path,
            entitlement=entitlement,
        )
    except Exception:
        usage_store.release(subject=entitlement.subject, usage_day=entitlement.usage_day)
        raise


@router.post("/v1/jobs", response_model=JobCreatedResponse)
async def create_processing_job(request: ProcessRequest, http_request: Request) -> JobCreatedResponse:
    enforce_api_key(http_request, settings)
    entitlement = resolve_entitlement(
        request=http_request,
        settings=settings,
        usage_store=usage_store,
    )
    job_id = f"job_{uuid4().hex[:10]}"
    public_base_url = (settings.api_base_url or str(http_request.base_url)).rstrip("/")
    logger.info(
        "route_job request_id=%s route=%s target_platform=%s video_url=%s plan=%s subject_source=%s",
        job_id,
        http_request.url.path,
        request.target_platform or "TikTok",
        request.video_url,
        entitlement.plan.code,
        entitlement.subject_source,
    )
    await job_store.create(job_id, "Job queued. Starting source analysis.")
    import asyncio

    asyncio.create_task(
        run_job(
            settings=settings,
            job_store=job_store,
            usage_store=usage_store,
            job_id=job_id,
            request=request,
            public_base_url=public_base_url,
            route_path=http_request.url.path,
            entitlement=entitlement,
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
