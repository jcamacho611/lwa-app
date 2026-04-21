from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Request

from ...core.config import get_settings
from ...models.schemas import (
    GenerationBackgroundRequest,
    GenerationJobResponse,
    GenerationJobStatusResponse,
    GenerationRequest,
)
from ...services.clip_service import enforce_api_key
from ...services.generated_asset_store import GeneratedAssetStore
from ...services.visual_generation_service import (
    VisualGenerationDisabledError,
    VisualGenerationError,
    VisualGenerationRequestError,
    download_visual_generation_asset,
    generate_lwa_background,
    poll_visual_generation_job,
    visual_generation_available,
)

router = APIRouter()
settings = get_settings()
asset_store = GeneratedAssetStore(settings.generated_asset_store_path)


@router.post("/v1/generation/background", response_model=GenerationJobResponse)
async def create_generation_background(request: GenerationRequest, http_request: Request) -> GenerationJobResponse:
    enforce_api_key(http_request, settings)
    public_base_url = (settings.api_base_url or str(http_request.base_url)).rstrip("/")
    if not visual_generation_available(settings):
        raise HTTPException(status_code=503, detail="LWA visual generation is disabled. Core clipping remains available.")

    prompt = (request.prompt or request.text_prompt or "").strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="A prompt is required.")

    background_request = GenerationBackgroundRequest(
        prompt=prompt,
        style_preset=request.style_preset or request.style,
        motion_profile=request.motion_profile or request.motion_strength,
        duration_seconds=int(request.duration_seconds or request.duration or 8),
        aspect_ratio=request.aspect_ratio or "9:16",
        seed=request.seed,
        reference_image_url=request.reference_image_url,
        source_clip_url=request.source_clip_url,
        source_asset_id=request.source_asset_id,
    )

    try:
        job = await generate_lwa_background(settings=settings, request=background_request)
    except VisualGenerationDisabledError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except VisualGenerationRequestError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error
    except VisualGenerationError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error

    job_id = str(job.get("job_id") or f"lwa_gen_{uuid4().hex[:10]}")
    asset_payload = job.get("asset") if isinstance(job.get("asset"), dict) else {}
    generated_asset = asset_store.create_asset(
        asset_id=str(asset_payload.get("asset_id") or f"asset_{uuid4().hex[:12]}"),
        provider="lwa",
        asset_type="background_video",
        status=str(job.get("status") or "completed"),
        prompt=prompt,
        preview_url=asset_payload.get("public_url") or asset_payload.get("asset_url"),
        video_url=asset_payload.get("asset_url") or asset_payload.get("public_url"),
        thumbnail_url=asset_payload.get("thumbnail_url"),
        local_path=asset_payload.get("local_path"),
        provider_job_id=job.get("provider_job_id"),
        request_id=job_id,
        source_refs={
            key: value
            for key, value in {
                "reference_image_url": request.reference_image_url,
                "source_clip_url": request.source_clip_url,
                "source_asset_id": request.source_asset_id,
                "image_url": request.image_url,
                "video_url": request.video_url,
            }.items()
            if value
        },
        error=job.get("error"),
    )
    return GenerationJobResponse(
        job_id=job_id,
        provider_job_id=job.get("provider_job_id"),
        status=str(job.get("status") or "completed"),
        message=str(job.get("message") or "LWA generation job prepared."),
        poll_url=f"{public_base_url}/v1/generation/jobs/{job_id}",
        asset=job.get("asset"),
        metadata={"job_kind": job.get("job_kind"), "runtime": "lwa-owned", "generated_asset": generated_asset},
    )


@router.get("/v1/generation/jobs/{job_id}", response_model=GenerationJobStatusResponse)
async def get_generation_job(job_id: str, http_request: Request) -> GenerationJobStatusResponse:
    enforce_api_key(http_request, settings)
    if not visual_generation_available(settings):
        raise HTTPException(status_code=503, detail="LWA visual generation is disabled. Core clipping remains available.")

    stored_asset = _find_generation_asset(job_id)
    poll_job_id = str(stored_asset.get("request_id") or job_id) if stored_asset else job_id

    try:
        payload = await poll_visual_generation_job(settings=settings, job_id=poll_job_id)
    except VisualGenerationDisabledError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except VisualGenerationRequestError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error

    asset_payload = payload.get("asset") if isinstance(payload.get("asset"), dict) else {}
    generated_asset = None
    if stored_asset:
        generated_asset = asset_store.update_asset(
            stored_asset["id"],
            status=str(payload.get("status") or stored_asset.get("status") or "unknown"),
            preview_url=asset_payload.get("public_url") or asset_payload.get("asset_url") or stored_asset.get("preview_url"),
            video_url=asset_payload.get("asset_url") or asset_payload.get("public_url") or stored_asset.get("video_url"),
            thumbnail_url=asset_payload.get("thumbnail_url") or stored_asset.get("thumbnail_url"),
            local_path=asset_payload.get("local_path") or stored_asset.get("local_path"),
            error=payload.get("error"),
        )

    return GenerationJobStatusResponse(
        job_id=poll_job_id,
        provider_job_id=payload.get("provider_job_id"),
        status=str(payload.get("status") or "unknown"),
        message=str(payload.get("message") or "LWA generation job status retrieved."),
        created_at=str(payload.get("created_at") or ""),
        updated_at=str(payload.get("updated_at") or ""),
        asset=payload.get("asset"),
        error=payload.get("error"),
        metadata={"job_kind": payload.get("job_kind"), "runtime": "lwa-owned", "generated_asset": generated_asset},
    )


@router.post("/v1/generation/jobs/{job_id}/download")
async def download_generation_job_asset(job_id: str, http_request: Request) -> dict[str, object]:
    enforce_api_key(http_request, settings)
    if not visual_generation_available(settings):
        raise HTTPException(status_code=503, detail="LWA visual generation is disabled. Core clipping remains available.")

    stored_asset = _find_generation_asset(job_id)
    if not stored_asset:
        raise HTTPException(status_code=404, detail="Generated asset not found.")

    asset_url = str(stored_asset.get("video_url") or stored_asset.get("preview_url") or "").strip()
    if not asset_url:
        raise HTTPException(status_code=409, detail="Job has no downloadable asset yet.")

    destination = Path(settings.generated_assets_dir) / "visual-generation" / f"{stored_asset['id']}.mp4"
    try:
        local_path = await download_visual_generation_asset(
            settings=settings,
            asset_url=asset_url,
            destination_path=str(destination),
        )
    except VisualGenerationDisabledError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except VisualGenerationRequestError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error

    updated = asset_store.update_asset(stored_asset["id"], local_path=local_path)
    return {
        "provider_job_id": stored_asset.get("provider_job_id") or job_id,
        "asset": updated,
        "local_path": local_path,
    }


def _find_generation_asset(job_id: str) -> dict[str, object] | None:
    return (
        asset_store.get_asset(job_id)
        or asset_store.get_by_provider_job_id(job_id)
        or next(iter(asset_store.list_assets_for_request(job_id)), None)
    )
