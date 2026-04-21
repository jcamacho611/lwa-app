from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from ...core.config import get_settings
from ...services.clip_service import enforce_api_key
from ...services.clip_status_store import get_clip_status
from ...services.render_jobs import queue_preview_render

router = APIRouter()
settings = get_settings()


@router.get("/clip-status/{clip_id}")
@router.get("/v1/clip-status/{clip_id}")
async def read_clip_status(clip_id: str, request: Request, request_id: str | None = None) -> dict[str, object]:
    enforce_api_key(request, settings)
    status = get_clip_status(clip_id=clip_id, request_id=request_id, include_internal=True)
    if status is None:
        return {
            "id": clip_id,
            "clip_id": clip_id,
            "request_id": request_id,
            "status": "processing",
            "render_status": "pending",
            "is_rendered": False,
            "is_strategy_only": True,
        }
    return status


@router.post("/clip-status/{clip_id}/render")
@router.post("/v1/clip-status/{clip_id}/render")
async def retry_clip_render(clip_id: str, request: Request, request_id: str | None = None) -> dict[str, object]:
    enforce_api_key(request, settings)
    status = get_clip_status(clip_id=clip_id, request_id=request_id)
    if status is None:
        raise HTTPException(status_code=404, detail="Clip status not found")

    resolved_request_id = str(status.get("request_id") or request_id or "")
    if not resolved_request_id:
        raise HTTPException(status_code=409, detail="Missing request id for render retry")

    public_base_url = (settings.api_base_url or str(request.base_url)).rstrip("/")
    queue_preview_render(
        settings=settings,
        request_id=resolved_request_id,
        clip_id=clip_id,
        public_base_url=public_base_url,
        local_asset_path=status.get("local_asset_path") if isinstance(status.get("local_asset_path"), str) else None,
        title_text=str(status.get("hook") or status.get("title") or ""),
        subtitle_text=str(status.get("transcript_excerpt") or status.get("caption") or ""),
    )
    updated = get_clip_status(clip_id=clip_id, request_id=resolved_request_id)
    return updated or status
