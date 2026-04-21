from __future__ import annotations

from pathlib import Path
from typing import Any, List, Optional

from ..core.config import Settings
from ..processor import (
    ClipSeed,
    create_social_exports,
    cut_clip,
    ensure_clip_output,
    export_social_ready_clip,
    probe_video_duration,
    resolve_ffmpeg_path,
)


def locate_ffmpeg(settings: Settings) -> Optional[str]:
    return resolve_ffmpeg_path(settings)


def trim_clip(*, ffmpeg_path: str, source_file: Path, output_path: Path, start: float, duration: float) -> None:
    cut_clip(
        ffmpeg_path=ffmpeg_path,
        source_file=source_file,
        output_path=output_path,
        start=start,
        duration=duration,
    )


def validate_output(path: Path) -> None:
    ensure_clip_output(path)


def detect_duration(*, source_file: Path, ffmpeg_path: str) -> Optional[int]:
    return probe_video_duration(source_file=source_file, ffmpeg_path=ffmpeg_path)


def render_social_export(
    *,
    settings: Settings,
    ffmpeg_path: str,
    input_path: Path,
    output_path: Path,
    title_text: str,
    subtitle_text: str,
) -> None:
    export_social_ready_clip(
        settings=settings,
        ffmpeg_path=ffmpeg_path,
        input_path=input_path,
        output_path=output_path,
        title_text=title_text,
        subtitle_text=subtitle_text,
    )


def batch_social_exports(
    *,
    settings: Settings,
    clip_results: List[Any],
    clip_seeds: List[ClipSeed],
    generated_dir: Path,
    request_id: str,
    public_base_url: str,
    ffmpeg_path: str,
) -> tuple[List[Any], int]:
    return create_social_exports(
        settings=settings,
        clip_results=clip_results,
        clip_seeds=clip_seeds,
        generated_dir=generated_dir,
        request_id=request_id,
        public_base_url=public_base_url,
        ffmpeg_path=ffmpeg_path,
    )
