from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Request

from ...core.config import get_settings
from ...dependencies.auth import get_platform_store, require_user
from ...models.schemas import EditClipRequest
from ...services.entitlements import require_feature_access
from ...processor import (
    build_video_encoder_args,
    drawtext_filter,
    resolve_drawtext_font,
    resolve_ffmpeg_path,
    resolve_video_encoder,
)
from ...services.video_service import ffmpeg_available
import subprocess

router = APIRouter(prefix="/edit", tags=["edit"])
settings = get_settings()
platform_store = get_platform_store()


@router.post("/clip")
async def edit_clip(payload: EditClipRequest, request: Request) -> dict[str, object]:
    user = require_user(request)
    require_feature_access(
        settings=settings,
        user=user,
        feature_name="timeline_editor",
        detail="Upgrade to Pro to unlock direct clip editing and clean export workflow.",
    )
    if not ffmpeg_available(settings):
        raise HTTPException(status_code=503, detail="ffmpeg is not available")

    clip = platform_store.get_clip(clip_id=payload.clip_id, user_id=user.id)
    if not clip:
        raise HTTPException(status_code=404, detail="Clip not found")

    local_asset_path = clip.get("local_asset_path")
    if not local_asset_path or not Path(local_asset_path).exists():
        raise HTTPException(status_code=404, detail="Local clip asset is unavailable")

    ffmpeg_path = resolve_ffmpeg_path(settings)
    if not ffmpeg_path:
        raise HTTPException(status_code=503, detail="ffmpeg is not available")

    request_dir = Path(settings.generated_assets_dir) / clip["request_id"]
    request_dir.mkdir(parents=True, exist_ok=True)
    output_name = f"{clip['clip_id']}_edit_{uuid4().hex[:8]}.mp4"
    output_path = request_dir / output_name

    command = [ffmpeg_path, "-y"]
    if payload.start_time:
        command.extend(["-ss", payload.start_time])
    command.extend(["-i", str(local_asset_path)])
    if payload.end_time:
        command.extend(["-to", payload.end_time])

    filters: list[str] = []
    caption_text = (payload.caption_text or clip.get("caption") or "").strip()
    if caption_text:
        regular_font = resolve_drawtext_font(bold=False)
        caption_path = request_dir / f"{output_name}.txt"
        caption_path.write_text(caption_text, encoding="utf-8")
        filters.append(
            drawtext_filter(
                textfile=caption_path,
                fontfile=regular_font,
                fontsize=34,
                x="42",
                y="h-th-82",
                fontcolor="white",
                line_spacing=12,
                box=True,
                boxcolor="black@0.28",
                boxborderw=18,
            )
        )
    if filters:
        command.extend(["-vf", ",".join(filters)])
    encoder = resolve_video_encoder(settings=settings, ffmpeg_path=ffmpeg_path)
    command.extend(build_video_encoder_args(encoder_name=encoder, target="social"))
    command.extend(["-c:a", "aac", "-movflags", "+faststart", str(output_path)])

    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as error:
        raise HTTPException(status_code=500, detail=error.stderr or "Clip edit failed") from error

    base_url = (settings.api_base_url or str(request.base_url)).rstrip("/")
    edited_url = f"{base_url}/generated/{clip['request_id']}/{output_name}"
    updated = platform_store.update_clip_edit(
        clip_id=payload.clip_id,
        user_id=user.id,
        caption=caption_text or clip.get("caption") or "",
        edited_clip_url=edited_url,
        local_asset_path=str(output_path),
        trim_start_seconds=parse_timestamp(payload.start_time) if payload.start_time else clip.get("trim_start_seconds"),
        trim_end_seconds=parse_timestamp(payload.end_time) if payload.end_time else clip.get("trim_end_seconds"),
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Clip not found after edit")
    return updated


def parse_timestamp(value: str) -> float:
    parts = value.split(":")
    try:
        numbers = [float(part) for part in parts]
    except ValueError as error:
        raise HTTPException(status_code=400, detail="Invalid timestamp format") from error
    if len(numbers) == 3:
        return (numbers[0] * 3600) + (numbers[1] * 60) + numbers[2]
    if len(numbers) == 2:
        return (numbers[0] * 60) + numbers[1]
    if len(numbers) == 1:
        return numbers[0]
    raise HTTPException(status_code=400, detail="Invalid timestamp format")
