"""Seedance premium visual generation routes.

These routes are fully separate from the existing /generate, /process,
and /v1/jobs flows. They return clean disabled/misconfigured responses
when Seedance is not enabled.
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Request

from ...core.config import get_settings
from ...models.schemas import (
    SeedanceBackgroundRequest,
    SeedanceJobResponse,
    SeedanceStatusResponse,
)
from ...services.clip_service import enforce_api_key
from ...services.seedance_service import (
    SeedanceAPIError,
    SeedanceUnavailableError,
    generate_seedance_background,
    poll_seedance_job,
    seedance_available,
)

router = APIRouter(prefix="/v1/seedance", tags=["seedance"])
settings = get_settings()
logger = logging.getLogger("uvicorn.error")


@router.post("/background", response_model=SeedanceStatusResponse)
async def create_background(
    request: SeedanceBackgroundRequest,
    http_request: Request,
) -> SeedanceStatusResponse:
    """Submit a Seedance background generation job.

    Returns a disabled message when Seedance is not configured.
    """
    enforce_api_key(http_request, settings)

    if not seedance_available(settings):
        return SeedanceStatusResponse(
            enabled=False,
            message="Seedance is not enabled. Set SEEDANCE_ENABLED=true and configure SEEDANCE_API_KEY and SEEDANCE_BASE_URL.",
        )

    try:
        job = await generate_seedance_background(
            settings=settings,
            prompt=request.prompt,
            style_preset=request.style_preset,
            duration_seconds=request.duration_seconds,
            aspect_ratio=request.aspect_ratio,
        )
        return SeedanceStatusResponse(
            enabled=True,
            job=SeedanceJobResponse(
                job_id=job.job_id,
                status=job.status,
                created_at=job.created_at,
            ),
        )
    except SeedanceUnavailableError as exc:
        return SeedanceStatusResponse(enabled=False, message=str(exc))
    except SeedanceAPIError as exc:
        logger.warning("seedance_background_error status=%s detail=%s", exc.status_code, exc.detail)
        raise HTTPException(status_code=502, detail=f"Seedance API error: {exc.detail}")
    except Exception as exc:
        logger.error("seedance_background_unexpected error=%s", exc)
        raise HTTPException(status_code=502, detail="Unexpected error contacting Seedance.")


@router.get("/jobs/{job_id}", response_model=SeedanceStatusResponse)
async def get_job_status(
    job_id: str,
    http_request: Request,
) -> SeedanceStatusResponse:
    """Poll a Seedance job for completion status.

    Returns a disabled message when Seedance is not configured.
    """
    enforce_api_key(http_request, settings)

    if not seedance_available(settings):
        return SeedanceStatusResponse(
            enabled=False,
            message="Seedance is not enabled.",
        )

    try:
        job = await poll_seedance_job(settings=settings, job_id=job_id)
        return SeedanceStatusResponse(
            enabled=True,
            job=SeedanceJobResponse(
                job_id=job.job_id,
                status=job.status,
                asset_url=job.asset_url,
                error=job.error,
                updated_at=job.updated_at,
            ),
        )
    except SeedanceUnavailableError as exc:
        return SeedanceStatusResponse(enabled=False, message=str(exc))
    except SeedanceAPIError as exc:
        logger.warning("seedance_poll_error job_id=%s status=%s detail=%s", job_id, exc.status_code, exc.detail)
        raise HTTPException(status_code=502, detail=f"Seedance API error: {exc.detail}")
    except Exception as exc:
        logger.error("seedance_poll_unexpected job_id=%s error=%s", job_id, exc)
        raise HTTPException(status_code=502, detail="Unexpected error contacting Seedance.")
