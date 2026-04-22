from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from ...core.config import get_settings
from ...services.visual_generation_service import (
    VisualGenerationError,
    VisualGenerationRequest,
    VisualGenerationService,
)

router = APIRouter(prefix="/v1/visual-generation", tags=["visual-generation"])
settings = get_settings()
logger = logging.getLogger("uvicorn.error")
service = VisualGenerationService(settings)


class VisualGenerationPayload(BaseModel):
    mode: str = Field(default="idea")
    prompt: str | None = None
    image_url: str | None = None
    reference_image_url: str | None = None
    source_clip_url: str | None = None
    source_asset_id: str | None = None
    style_preset: str | None = None
    motion_profile: str | None = None
    duration_seconds: int = 8
    aspect_ratio: str = "9:16"
    seed: int | None = None
    target_platform: str | None = None


def _actor_id_from_request(request: Request) -> str:
    header_name = getattr(settings, "client_id_header_name", "x-lwa-client-id")
    client_id = (request.headers.get(header_name) or "").strip()
    safe_id = "".join(ch if ch.isalnum() or ch in {"_", "-"} else "_" for ch in client_id)
    return f"guest_{safe_id[:64] or 'first_use'}"


@router.get("/health")
async def visual_generation_health() -> dict[str, Any]:
    return {
        "ok": True,
        "service": "visual_generation",
        "provider": "lwa",
    }


@router.post("/generate")
async def generate_visual(payload: VisualGenerationPayload, request: Request) -> dict[str, Any]:
    actor_id = _actor_id_from_request(request)

    try:
        result = await service.generate(
            VisualGenerationRequest(
                mode=payload.mode,
                prompt=payload.prompt,
                image_url=payload.image_url,
                reference_image_url=payload.reference_image_url,
                source_clip_url=payload.source_clip_url,
                source_asset_id=payload.source_asset_id,
                style_preset=payload.style_preset,
                motion_profile=payload.motion_profile,
                duration_seconds=payload.duration_seconds,
                aspect_ratio=payload.aspect_ratio,
                seed=payload.seed,
                target_platform=payload.target_platform,
            ),
            actor_id=actor_id,
        )
        return result
    except VisualGenerationError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:  # pragma: no cover
        logger.exception("visual_generation_failed actor_id=%s mode=%s", actor_id, payload.mode)
        raise HTTPException(status_code=500, detail=f"Visual generation failed: {error}") from error
