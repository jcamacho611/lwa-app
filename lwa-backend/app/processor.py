from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
import subprocess
import tempfile
from typing import Any, List, Optional
from urllib.parse import quote

try:
    import imageio_ffmpeg  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    imageio_ffmpeg = None

from yt_dlp import YoutubeDL

from .config import Settings


@dataclass
class ClipSeed:
    id: str
    start_time: str
    end_time: str
    clip_url: Optional[str]
    format: str


@dataclass
class SourceContext:
    title: str
    description: str
    uploader: Optional[str]
    duration_seconds: Optional[int]
    source_url: str
    clip_seeds: List[ClipSeed]
    processing_mode: str


def resolve_ffmpeg_path(settings: Settings) -> Optional[str]:
    configured = Path(settings.ffmpeg_path)
    if configured.exists():
        return str(configured)

    discovered = shutil.which("ffmpeg")
    if discovered:
        return discovered

    if imageio_ffmpeg is not None:
        try:
            return imageio_ffmpeg.get_ffmpeg_exe()
        except Exception:
            return None

    return None


def process_video_source(
    *,
    settings: Settings,
    request_id: str,
    video_url: str,
    public_base_url: str,
) -> SourceContext:
    ffmpeg_path = resolve_ffmpeg_path(settings)
    if not ffmpeg_path:
        raise RuntimeError("ffmpeg is not available")

    generated_dir = Path(settings.generated_assets_dir) / request_id
    generated_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix=f"{request_id}_", dir=settings.yt_dlp_temp_dir) as temp_dir:
        work_dir = Path(temp_dir)
        info = download_source(video_url=video_url, work_dir=work_dir, ffmpeg_path=ffmpeg_path)
        source_file = locate_source_file(work_dir)

        duration_seconds = parse_duration_seconds(info.get("duration"))
        segments = build_segment_plan(duration_seconds, info.get("chapters") or [])
        clip_seeds = create_clips(
            source_file=source_file,
            generated_dir=generated_dir,
            request_id=request_id,
            segments=segments,
            public_base_url=public_base_url,
            ffmpeg_path=ffmpeg_path,
        )

    return SourceContext(
        title=str(info.get("title") or "Untitled source"),
        description=str(info.get("description") or ""),
        uploader=string_or_none(info.get("uploader")),
        duration_seconds=duration_seconds,
        source_url=str(info.get("webpage_url") or video_url),
        clip_seeds=clip_seeds,
        processing_mode="real",
    )


def download_source(*, video_url: str, work_dir: Path, ffmpeg_path: str) -> dict[str, Any]:
    options = {
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "outtmpl": str(work_dir / "source.%(ext)s"),
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "merge_output_format": "mp4",
        "overwrites": True,
        "ffmpeg_location": str(Path(ffmpeg_path).parent),
    }

    with YoutubeDL(options) as ydl:
        return ydl.extract_info(video_url, download=True)


def locate_source_file(work_dir: Path) -> Path:
    candidates = [
        path
        for path in work_dir.iterdir()
        if path.is_file() and path.suffix.lower() in {".mp4", ".mov", ".mkv", ".webm", ".m4v"}
    ]

    if not candidates:
        raise FileNotFoundError("yt-dlp did not produce a video file")

    return max(candidates, key=lambda path: path.stat().st_size)


def build_segment_plan(duration_seconds: Optional[int], chapters: List[dict[str, Any]]) -> List[dict[str, float]]:
    clip_length = choose_clip_length(duration_seconds)
    segments = build_chapter_segments(chapters=chapters, clip_length=clip_length)
    if segments:
        return segments[:3]

    if duration_seconds is None or duration_seconds <= 0:
        return [
            {"start": 0.0, "duration": float(clip_length)},
            {"start": 15.0, "duration": float(clip_length)},
            {"start": 30.0, "duration": float(clip_length)},
        ]

    latest_start = max(float(duration_seconds - clip_length), 0.0)
    if latest_start == 0:
        return [{"start": 0.0, "duration": float(clip_length)}]

    fractions = [0.12, 0.42, 0.72]
    planned = []
    for fraction in fractions:
        start = min(latest_start, max(0.0, duration_seconds * fraction))
        planned.append({"start": round(start, 2), "duration": float(clip_length)})

    return dedupe_segments(planned)[:3]


def build_chapter_segments(chapters: List[dict[str, Any]], clip_length: int) -> List[dict[str, float]]:
    planned = []
    for chapter in chapters[:6]:
        start = float(chapter.get("start_time") or 0.0)
        end = float(chapter.get("end_time") or 0.0)
        duration = float(min(clip_length, max(end - start, clip_length)))
        planned.append({"start": round(start, 2), "duration": duration})

    return dedupe_segments(planned)


def dedupe_segments(segments: List[dict[str, float]]) -> List[dict[str, float]]:
    deduped = []
    seen = set()
    for segment in segments:
        rounded_start = round(segment["start"])
        if rounded_start in seen:
            continue
        seen.add(rounded_start)
        deduped.append(segment)
    return deduped


def choose_clip_length(duration_seconds: Optional[int]) -> int:
    if duration_seconds is None or duration_seconds <= 0:
        return 15
    if duration_seconds <= 24:
        return max(6, duration_seconds // 2)
    if duration_seconds <= 60:
        return max(8, duration_seconds // 4)
    return 18


def create_clips(
    *,
    source_file: Path,
    generated_dir: Path,
    request_id: str,
    segments: List[dict[str, float]],
    public_base_url: str,
    ffmpeg_path: str,
) -> List[ClipSeed]:
    seeds: List[ClipSeed] = []
    for index, segment in enumerate(segments[:3], start=1):
        output_name = f"clip_{index:03d}.mp4"
        output_path = generated_dir / output_name
        cut_clip(
            ffmpeg_path=ffmpeg_path,
            source_file=source_file,
            output_path=output_path,
            start=segment["start"],
            duration=segment["duration"],
        )
        clip_url = f"{public_base_url}/generated/{request_id}/{quote(output_name)}"
        seeds.append(
            ClipSeed(
                id=f"clip_{index:03d}",
                start_time=format_timestamp(segment["start"]),
                end_time=format_timestamp(segment["start"] + segment["duration"]),
                clip_url=clip_url,
                format=segment_format(index),
            )
        )
    return seeds


def cut_clip(
    *,
    ffmpeg_path: str,
    source_file: Path,
    output_path: Path,
    start: float,
    duration: float,
) -> None:
    command = [
        ffmpeg_path,
        "-y",
        "-ss",
        f"{start}",
        "-i",
        str(source_file),
        "-t",
        f"{duration}",
        "-map",
        "0:v:0",
        "-map",
        "0:a?",
        "-vf",
        "scale='min(1080,iw)':-2",
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "23",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-movflags",
        "+faststart",
        str(output_path),
    ]

    subprocess.run(command, check=True, capture_output=True, text=True)


def format_timestamp(total_seconds: float) -> str:
    safe_seconds = max(int(total_seconds), 0)
    minutes, seconds = divmod(safe_seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return f"{minutes:02d}:{seconds:02d}"


def parse_duration_seconds(value: Any) -> Optional[int]:
    try:
        if value is None:
            return None
        return int(float(value))
    except (TypeError, ValueError):
        return None


def segment_format(index: int) -> str:
    formats = {
        1: "Hook First",
        2: "Opinion",
        3: "Story CTA",
    }
    return formats.get(index, "Short Form")


def string_or_none(value: Any) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
