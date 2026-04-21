from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter, HTTPException, Request

from ...core.config import get_settings
from ...models.schemas import (
    SeedanceBackgroundRequest,
    SeedanceJobResponse,
    SeedanceJobStatusResponse,
)
from ...services.clip_service import enforce_api_key
from ...services.seedance_service import (
    SeedanceProviderError,
    generate_seedance_background,
    poll_seedance_job,
    seedance_available,
)

router = APIRouter()
settings = get_settings()


@router.post("/v1/seedance/background", response_model=SeedanceJobResponse)
async def create_seedance_background(request: SeedanceBackgroundRequest, http_request: Request) -> SeedanceJobResponse:
    enforce_api_key(http_request, settings)
    public_base_url = (settings.api_base_url or str(http_request.base_url)).rstrip("/")
    if not seedance_available(settings):
        raise HTTPException(status_code=503, detail="Seedance is disabled or incomplete. Current homepage and generation flows continue without it.")

    try:
        job = await generate_seedance_background(settings=settings, request=request)
    except SeedanceProviderError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error

    job_id = str(job.get("job_id") or f"seed_{uuid4().hex[:10]}")
    return SeedanceJobResponse(
        job_id=job_id,
        provider_job_id=job.get("provider_job_id"),
        status=str(job.get("status") or "submitted"),
        message=str(job.get("message") or "Seedance job submitted."),
        poll_url=f"{public_base_url}/v1/seedance/jobs/{job_id}",
        asset=job.get("asset"),
        metadata={"job_kind": job.get("job_kind"), "adapter": "lwa-seedance"},
    )


@router.get("/v1/seedance/jobs/{job_id}", response_model=SeedanceJobStatusResponse)
async def get_seedance_job(job_id: str, http_request: Request) -> SeedanceJobStatusResponse:
    enforce_api_key(http_request, settings)
    if not seedance_available(settings):
        raise HTTPException(status_code=503, detail="Seedance is disabled or incomplete.")

    try:
        payload = await poll_seedance_job(settings=settings, job_id=job_id)
    except SeedanceProviderError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error

    return SeedanceJobStatusResponse(
        job_id=job_id,
        provider_job_id=payload.get("provider_job_id"),
        status=str(payload.get("status") or "unknown"),
        message=str(payload.get("message") or "Seedance job status retrieved."),
        created_at=str(payload.get("created_at") or ""),
        updated_at=str(payload.get("updated_at") or ""),
        asset=payload.get("asset"),
        error=payload.get("error"),
        metadata={"job_kind": payload.get("job_kind"), "adapter": "lwa-seedance"},
    )
