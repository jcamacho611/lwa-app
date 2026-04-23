from __future__ import annotations

from pathlib import Path
from typing import Any

from ..processor import download_source, locate_source_file


def download_video_source(
    *,
    video_url: str,
    work_dir: Path,
    ffmpeg_path: str,
    request_id: str = "download",
) -> dict[str, Any]:
    return download_source(video_url=video_url, work_dir=work_dir, ffmpeg_path=ffmpeg_path, request_id=request_id)


def resolve_downloaded_video(work_dir: Path) -> Path:
    return locate_source_file(work_dir)
