from __future__ import annotations

from pathlib import Path
from typing import List

from ..core.config import Settings
from ..models.schemas import ClipResult
from ..processor import (
    ClipSeed,
    SourceContext,
    create_social_exports,
    process_video_source,
    resolve_ffmpeg_path,
)


def build_source_context(
    *,
    settings: Settings,
    request_id: str,
    video_url: str,
    public_base_url: str,
    source_path: str | None = None,
    max_candidates: int = 20,
) -> SourceContext:
    return process_video_source(
        settings=settings,
        request_id=request_id,
        video_url=video_url,
        public_base_url=public_base_url,
        source_path=source_path,
        max_candidates=max_candidates,
    )


def ffmpeg_available(settings: Settings) -> bool:
    return resolve_ffmpeg_path(settings) is not None


def export_social_ready_clips(
    *,
    settings: Settings,
    clip_results: List[ClipResult],
    clip_seeds: List[ClipSeed],
    request_id: str,
    public_base_url: str,
) -> tuple[List[ClipResult], int]:
    ffmpeg_path = resolve_ffmpeg_path(settings)
    if not ffmpeg_path:
        return clip_results, 0

    generated_dir = Path(settings.generated_assets_dir) / request_id
    generated_dir.mkdir(parents=True, exist_ok=True)
    return create_social_exports(
        settings=settings,
        clip_results=clip_results,
        clip_seeds=clip_seeds,
        generated_dir=generated_dir,
        request_id=request_id,
        public_base_url=public_base_url,
        ffmpeg_path=ffmpeg_path,
    )
