from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter, HTTPException, Request

from ...core.config import get_settings
from ...models.schemas import GenerationAssetResponse, GenerationBackgroundRequest, GenerationJobResponse, GenerationJobStatusResponse
from ...services.clip_service import enforce_api_key
from ...services.seedance_service import (
    SeedanceProviderError,
    generate_seedance_background,
    poll_seedance_job,
    seedance_available,
)

router = APIRouter()
settings = get_settings()


@router.post("/v1/seedance/background", response_model=GenerationJobResponse)
async def create_seedance_background(request: GenerationBackgroundRequest, http_request: Request) -> GenerationJobResponse:
    enforce_api_key(http_request, settings)
    public_base_url = (settings.api_base_url or str(http_request.base_url)).rstrip("/")
    if not seedance_available(settings):
        raise HTTPException(
            status_code=503,
            detail="Seedance is disabled or incomplete. Current homepage and generation flows continue without it.",
        )

    try:
        asset = await generate_seedance_background(settings=settings, request=request)
    except SeedanceProviderError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error

    job_id = f"seed_{uuid4().hex[:10]}"
    return GenerationJobResponse(
        job_id=job_id,
        status="completed",
        message="Seedance background asset is ready.",
        poll_url=f"{public_base_url}/v1/seedance/jobs/{job_id}",
        asset=asset,
        metadata={"provider": "seedance"},
    )


@router.get("/v1/seedance/jobs/{job_id}", response_model=GenerationJobStatusResponse)
async def get_seedance_job(job_id: str, http_request: Request) -> GenerationJobStatusResponse:
    enforce_api_key(http_request, settings)
    if not seedance_available(settings):
        raise HTTPException(status_code=503, detail="Seedance is disabled or incomplete.")

    try:
        payload = await poll_seedance_job(settings=settings, job_id=job_id)
    except SeedanceProviderError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error

    asset_payload = payload.get("asset")
    asset = GenerationAssetResponse(**asset_payload) if isinstance(asset_payload, dict) else None
    return GenerationJobStatusResponse(
        job_id=job_id,
        status=str(payload.get("status") or "unknown"),
        message=str(payload.get("message") or "Seedance job status retrieved."),
        created_at=str(payload.get("created_at") or ""),
        updated_at=str(payload.get("updated_at") or ""),
        asset=asset,
        error=payload.get("error") if isinstance(payload.get("error"), str) else None,
        metadata={"provider": "seedance"},
    )
