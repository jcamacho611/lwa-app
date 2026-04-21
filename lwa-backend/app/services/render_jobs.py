from __future__ import annotations

import logging
from pathlib import Path
from threading import Thread
from urllib.parse import quote

from ..core.config import Settings
from ..processor import (
    build_subtitle_overlay,
    build_title_overlay,
    ensure_clip_output,
    export_social_ready_clip,
    resolve_ffmpeg_path,
)
from .clip_status_store import update_clip_status
from .render_job_store import RenderJobStore

logger = logging.getLogger("uvicorn.error")


def run_background(fn, *args, **kwargs) -> Thread:
    thread = Thread(target=fn, args=args, kwargs=kwargs, daemon=True)
    thread.start()
    return thread


def public_generated_url(*, public_base_url: str, request_id: str, asset_path: Path) -> str:
    return f"{public_base_url}/generated/{request_id}/{quote(asset_path.name)}"


def queue_preview_render(
    *,
    settings: Settings,
    request_id: str,
    clip_id: str,
    public_base_url: str,
    local_asset_path: str | None,
    title_text: str = "",
    subtitle_text: str = "",
) -> Thread | None:
    job_store = RenderJobStore(settings)
    
    if not local_asset_path:
        update_clip_status(
            clip_id=clip_id,
            request_id=request_id,
            updates={
                "render_status": "failed",
                "status": "failed",
                "render_error": "No local media asset available for preview rendering.",
            },
        )
        return None

    # Create persistent render job
    job = job_store.create_job(
        clip_id=clip_id,
        status="pending",
        output_path=local_asset_path,
    )
    
    update_clip_status(
        clip_id=clip_id,
        request_id=request_id,
        updates={"render_status": "rendering", "status": "processing", "render_error": None},
    )
    
    return run_background(
        _render_preview_job,
        settings=settings,
        request_id=request_id,
        clip_id=clip_id,
        public_base_url=public_base_url,
        local_asset_path=local_asset_path,
        title_text=title_text,
        subtitle_text=subtitle_text,
    )


def _render_preview_job(
    *,
    settings: Settings,
    request_id: str,
    clip_id: str,
    public_base_url: str,
    local_asset_path: str,
    title_text: str,
    subtitle_text: str,
) -> None:
    input_path = Path(local_asset_path)
    fallback_url = public_generated_url(public_base_url=public_base_url, request_id=request_id, asset_path=input_path)
    try:
        if not input_path.exists():
            raise FileNotFoundError(f"local asset missing: {input_path}")

        ffmpeg_path = resolve_ffmpeg_path(settings)
        if not ffmpeg_path:
            raise RuntimeError("ffmpeg unavailable")

        output_path = input_path.with_name(f"{clip_id}_async_preview.mp4")
        edit_profile = export_social_ready_clip(
            settings=settings,
            ffmpeg_path=ffmpeg_path,
            input_path=input_path,
            output_path=output_path,
            title_text=build_title_overlay(title_text, "Short Form"),
            subtitle_text=build_subtitle_overlay(subtitle_text),
        )
        ensure_clip_output(output_path)
        preview_url = public_generated_url(public_base_url=public_base_url, request_id=request_id, asset_path=output_path)
        update_clip_status(
            clip_id=clip_id,
            request_id=request_id,
            updates={
                "preview_url": preview_url,
                "edited_clip_url": preview_url,
                "clip_url": preview_url,
                "render_status": "ready",
                "status": "ready",
                "edit_profile": edit_profile,
                "aspect_ratio": "9:16",
                "render_error": None,
            },
        )
    except Exception as error:
        logger.warning(
            "async_preview_render_fallback request_id=%s clip_id=%s reason=%s",
            request_id,
            clip_id,
            error,
        )
        
        # Update job status in persistent store
        job_store = RenderJobStore(settings)
        job_store.update_job(
            job_id=job["id"],
            status="failed" if not input_path.exists() else "ready",
            error=str(error) if not input_path.exists() else None,
        )
        
        update_clip_status(
            clip_id=clip_id,
            request_id=request_id,
            updates={
                "preview_url": fallback_url if input_path.exists() else None,
                "clip_url": fallback_url if input_path.exists() else None,
                "render_status": "ready" if input_path.exists() else "failed",
                "status": "ready" if input_path.exists() else "failed",
                "render_error": str(error),
                "aspect_ratio": "source",
            },
        )
