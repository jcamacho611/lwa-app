from __future__ import annotations

import base64
import json
from functools import lru_cache
from dataclasses import dataclass
import logging
import platform
import re
from pathlib import Path
import shutil
import subprocess
import tempfile
import textwrap
from typing import Any, List, Optional
from urllib.parse import quote, urlparse

try:
    import imageio_ffmpeg  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    imageio_ffmpeg = None

from yt_dlp import YoutubeDL

from .config import Settings
from .services.candidate_builder import build_candidate_clips, candidates_to_segment_plan
from .services.silence_detector import detect_silence_regions
from .services.speech_regions import invert_silence_to_speech

logger = logging.getLogger("uvicorn.error")

VIDEO_EXTENSIONS = {".mp4", ".mov", ".mkv", ".webm", ".m4v"}
AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".aac", ".ogg", ".oga", ".flac"}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif"}

MIN_TRANSCRIPT_CLIP_DURATION = 7.0
MAX_TRANSCRIPT_CLIP_DURATION = 18.0
TRANSCRIPT_LEAD_IN_SECONDS = 0.45
TRANSCRIPT_TAIL_SECONDS = 1.2


@dataclass
class ClipSeed:
    id: str
    start_time: str
    end_time: str
    asset_path: Path
    clip_url: Optional[str]
    raw_clip_url: Optional[str]
    preview_image_url: Optional[str]
    format: str
    transcript_excerpt: Optional[str] = None
    duration: Optional[int] = None


@dataclass
class TranscriptWindow:
    start_seconds: float
    end_seconds: float
    excerpt: str
    score: int


@dataclass
class SourceContext:
    title: str
    description: str
    uploader: Optional[str]
    duration_seconds: Optional[int]
    source_url: str
    clip_seeds: List[ClipSeed]
    processing_mode: str
    selection_strategy: str
    source_type: str = "url"
    source_platform: Optional[str] = None
    transcript: Optional[str] = None
    visual_summary: Optional[str] = None
    preview_asset_url: Optional[str] = None
    download_asset_url: Optional[str] = None
    thumbnail_url: Optional[str] = None


class YTDLPLogProxy:
    def __init__(self, request_id: str) -> None:
        self.request_id = request_id

    def debug(self, message: str) -> None:
        if message.startswith("[debug]"):
            return
        logger.debug("request_id=%s component=yt_dlp level=debug message=%s", self.request_id, message)

    def warning(self, message: str) -> None:
        logger.warning("request_id=%s component=yt_dlp level=warning message=%s", self.request_id, message)

    def error(self, message: str) -> None:
        logger.error("request_id=%s component=yt_dlp level=error message=%s", self.request_id, message)


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


def resolve_ffprobe_path(settings: Settings) -> Optional[str]:
    configured = Path(settings.ffmpeg_path)
    configured_probe = configured.with_name("ffprobe")
    if configured_probe.exists():
        return str(configured_probe)

    discovered = shutil.which("ffprobe")
    if discovered:
        return discovered

    ffmpeg_path = resolve_ffmpeg_path(settings)
    if ffmpeg_path:
        sibling = Path(ffmpeg_path).with_name("ffprobe")
        if sibling.exists():
            return str(sibling)

    return None


@lru_cache(maxsize=8)
def ffmpeg_supports_encoder(ffmpeg_path: str, encoder_name: str) -> bool:
    try:
        process = subprocess.run(
            [ffmpeg_path, "-hide_banner", "-encoders"],
            capture_output=True,
            text=True,
            check=False,
        )
    except Exception:
        return False

    combined = f"{process.stdout}\n{process.stderr}"
    return encoder_name in combined


def resolve_video_encoder(*, settings: Settings, ffmpeg_path: str) -> str:
    requested = settings.video_encoder
    if requested and requested not in {"auto", "mac"}:
        return requested

    if requested == "mac" and platform.system() == "Darwin" and ffmpeg_supports_encoder(ffmpeg_path, "h264_videotoolbox"):
        return "h264_videotoolbox"

    return "libx264"


def build_video_encoder_args(*, encoder_name: str, target: str) -> List[str]:
    if encoder_name == "h264_videotoolbox":
        bitrate = "4M" if target == "clip" else "5M"
        maxrate = "6M" if target == "clip" else "8M"
        return [
            "-c:v",
            "h264_videotoolbox",
            "-allow_sw",
            "1",
            "-b:v",
            bitrate,
            "-maxrate",
            maxrate,
            "-bufsize",
            "10M",
            "-pix_fmt",
            "yuv420p",
        ]

    return [
        "-c:v",
        "libx264",
        "-preset",
        "medium" if target == "clip" else "slow",
        "-crf",
        "22" if target == "clip" else "21",
        "-pix_fmt",
        "yuv420p",
    ]


def process_video_source(
    *,
    settings: Settings,
    request_id: str,
    video_url: str,
    public_base_url: str,
    source_path: str | None = None,
    max_candidates: int = 20,
    source_type: str = "url",
) -> SourceContext:
    ffmpeg_path = resolve_ffmpeg_path(settings)
    if not ffmpeg_path:
        raise RuntimeError("ffmpeg is not available")
    video_encoder = resolve_video_encoder(settings=settings, ffmpeg_path=ffmpeg_path)

    logger.info(
        "source_processing_start request_id=%s ffmpeg_path=%s video_encoder=%s public_base_url=%s",
        request_id,
        ffmpeg_path,
        video_encoder,
        public_base_url,
    )
    generated_dir = Path(settings.generated_assets_dir) / request_id
    generated_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix=f"{request_id}_", dir=settings.yt_dlp_temp_dir) as temp_dir:
        work_dir = Path(temp_dir)
        if source_path:
            source_file = stage_local_source(source_path=Path(source_path), work_dir=work_dir)
            info = {
                "title": source_file.stem,
                "description": "",
                "uploader": None,
                "duration": None,
                "webpage_url": video_url,
            }
        else:
            info = download_source(
                video_url=video_url,
                work_dir=work_dir,
                ffmpeg_path=ffmpeg_path,
                request_id=request_id,
            )
            source_file = locate_source_file(work_dir)
        transcript_windows = load_transcript_windows(work_dir)
        transcript = flatten_transcript_windows(transcript_windows)
        if not transcript:
            transcript_windows, transcript = transcribe_audio_source(settings=settings, source_file=source_file)

        duration_seconds = parse_duration_seconds(info.get("duration"))
        if duration_seconds is None:
            duration_seconds = probe_video_duration(source_file=source_file, ffmpeg_path=ffmpeg_path)
            if duration_seconds is None:
                logger.warning(
                    "source_probe_warning request_id=%s source_file=%s reason=duration_unavailable",
                    request_id,
                    source_file,
                )
        structure_segments: list[dict[str, float]] = []
        if duration_seconds:
            try:
                silence_regions = detect_silence_regions(str(source_file), ffmpeg_path=ffmpeg_path)
                speech_regions = invert_silence_to_speech(silence_regions, float(duration_seconds))
                structure_candidates = build_candidate_clips(speech_regions, max_candidates=max_candidates)
                structure_segments = candidates_to_segment_plan(structure_candidates)
            except Exception as error:
                logger.warning(
                    "structure_segment_fallback request_id=%s reason=%s",
                    request_id,
                    error,
                )

        segments, selection_strategy = build_segment_plan(
            duration_seconds=duration_seconds,
            chapters=info.get("chapters") or [],
            transcript_windows=transcript_windows,
            structure_segments=structure_segments,
            max_candidates=max_candidates,
        )
        logger.info(
            "segment_plan_ready request_id=%s strategy=%s segments=%s transcript_windows=%s duration_seconds=%s",
            request_id,
            selection_strategy,
            len(segments),
            len(transcript_windows),
            duration_seconds,
        )
        clip_seeds = create_clips(
            source_file=source_file,
            generated_dir=generated_dir,
            request_id=request_id,
            segments=segments,
            public_base_url=public_base_url,
            ffmpeg_path=ffmpeg_path,
            settings=settings,
            max_candidates=max_candidates,
        )
        if not clip_seeds:
            raise RuntimeError("real pipeline produced zero clip assets")
        logger.info(
            "clip_seeds_ready request_id=%s clip_seeds=%s generated_dir=%s",
            request_id,
            len(clip_seeds),
            generated_dir,
        )

    preview_asset_url = clip_seeds[0].clip_url if clip_seeds else None
    thumbnail_url = clip_seeds[0].preview_image_url if clip_seeds else None

    return SourceContext(
        title=str(info.get("title") or "Untitled source"),
        description=str(info.get("description") or ""),
        uploader=string_or_none(info.get("uploader")),
        duration_seconds=duration_seconds,
        source_url=str(info.get("webpage_url") or video_url),
        clip_seeds=clip_seeds,
        processing_mode="real",
        selection_strategy=selection_strategy,
        source_type=source_type,
        source_platform="Upload" if source_type != "url" else detect_source_platform(video_url),
        transcript=transcript or None,
        preview_asset_url=preview_asset_url,
        download_asset_url=preview_asset_url,
        thumbnail_url=thumbnail_url,
    )


def process_source(
    *,
    settings: Settings,
    request_id: str,
    video_url: str,
    public_base_url: str,
    source_path: str | None = None,
    max_candidates: int = 20,
    source_type: str | None = None,
    upload_content_type: str | None = None,
) -> SourceContext:
    warn_if_localhost_public_base_url(public_base_url=public_base_url)
    resolved_type = determine_source_type(
        source_type=source_type,
        source_path=source_path,
        content_type=upload_content_type,
    )
    if resolved_type == "audio_upload":
        return process_audio_source(
            settings=settings,
            request_id=request_id,
            source_url=video_url,
            public_base_url=public_base_url,
            source_path=source_path,
            max_candidates=max_candidates,
        )
    if resolved_type == "image_upload":
        return process_image_source(
            settings=settings,
            request_id=request_id,
            source_url=video_url,
            public_base_url=public_base_url,
            source_path=source_path,
            max_candidates=max_candidates,
        )
    return process_video_source(
        settings=settings,
        request_id=request_id,
        video_url=video_url,
        public_base_url=public_base_url,
        source_path=source_path,
        max_candidates=max_candidates,
        source_type=resolved_type,
    )


def warn_if_localhost_public_base_url(*, public_base_url: str) -> None:
    if public_base_url and "localhost" in public_base_url:
        logger.warning(
            "clip_url_warning public_base_url contains localhost - clips will not be accessible from browser",
        )


def determine_source_type(
    *,
    source_type: str | None,
    source_path: str | None,
    content_type: str | None,
) -> str:
    normalized_type = (source_type or "").strip().lower()
    if normalized_type in {"url", "video_upload", "audio_upload", "image_upload"}:
        return normalized_type

    normalized_content_type = (content_type or "").lower()
    suffix = Path(source_path or "").suffix.lower()

    if normalized_content_type.startswith("audio/") or suffix in AUDIO_EXTENSIONS:
        return "audio_upload"
    if normalized_content_type.startswith("image/") or suffix in IMAGE_EXTENSIONS:
        return "image_upload"
    if normalized_content_type.startswith("video/") or suffix in VIDEO_EXTENSIONS:
        return "video_upload" if source_path else "url"
    return "video_upload" if source_path else "url"


def process_audio_source(
    *,
    settings: Settings,
    request_id: str,
    source_url: str,
    public_base_url: str,
    source_path: str | None,
    max_candidates: int = 20,
) -> SourceContext:
    if not source_path:
        raise RuntimeError("audio uploads require a stored source path")

    ffmpeg_path = resolve_ffmpeg_path(settings)
    if not ffmpeg_path:
        raise RuntimeError("ffmpeg is not available")

    generated_dir = Path(settings.generated_assets_dir) / request_id
    generated_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix=f"{request_id}_", dir=settings.yt_dlp_temp_dir) as temp_dir:
        work_dir = Path(temp_dir)
        source_file = stage_local_source(source_path=Path(source_path), work_dir=work_dir)
        duration_seconds = probe_media_duration(source_file=source_file, settings=settings)
        transcript_windows = load_transcript_windows(work_dir)
        transcript = flatten_transcript_windows(transcript_windows)
        if not transcript:
            transcript_windows, transcript = transcribe_audio_source(settings=settings, source_file=source_file)

        segments, selection_strategy = build_segment_plan(
            duration_seconds=duration_seconds,
            chapters=[],
            transcript_windows=transcript_windows,
            max_candidates=max_candidates,
        )
        clip_seeds = create_audio_clips(
            source_file=source_file,
            generated_dir=generated_dir,
            request_id=request_id,
            segments=segments,
            public_base_url=public_base_url,
            ffmpeg_path=ffmpeg_path,
            settings=settings,
            max_candidates=max_candidates,
        )

    if not clip_seeds:
        raise RuntimeError("audio pipeline produced zero clip assets")

    preview_asset_url = clip_seeds[0].clip_url if clip_seeds else None
    thumbnail_url = clip_seeds[0].preview_image_url if clip_seeds else None
    return SourceContext(
        title=Path(source_path).stem.replace("_", " ").replace("-", " "),
        description="Audio source processed into short-form moments and waveform-ready previews.",
        uploader=None,
        duration_seconds=duration_seconds,
        source_url=source_url,
        clip_seeds=clip_seeds,
        processing_mode="real",
        selection_strategy=selection_strategy,
        source_type="audio_upload",
        source_platform="Upload",
        transcript=transcript,
        preview_asset_url=preview_asset_url,
        download_asset_url=preview_asset_url,
        thumbnail_url=thumbnail_url,
    )


def process_image_source(
    *,
    settings: Settings,
    request_id: str,
    source_url: str,
    public_base_url: str,
    source_path: str | None,
    max_candidates: int = 20,
) -> SourceContext:
    if not source_path:
        raise RuntimeError("image uploads require a stored source path")

    ffmpeg_path = resolve_ffmpeg_path(settings)
    if not ffmpeg_path:
        raise RuntimeError("ffmpeg is not available")

    generated_dir = Path(settings.generated_assets_dir) / request_id
    generated_dir.mkdir(parents=True, exist_ok=True)

    source_file = Path(source_path)
    visual_summary = analyze_image_source(settings=settings, source_file=source_file)
    width, height = probe_image_dimensions(source_file=source_file, settings=settings)
    durations = [8, 11, 14]
    segments = [
        {
            "start": 0.0,
            "duration": durations[index],
            "transcript_excerpt": visual_summary,
            "format": segment_format(index + 1),
        }
        for index in range(min(max_candidates, len(durations)))
    ]
    clip_seeds = create_image_clips(
        source_file=source_file,
        generated_dir=generated_dir,
        request_id=request_id,
        segments=segments,
        public_base_url=public_base_url,
        ffmpeg_path=ffmpeg_path,
        settings=settings,
        max_candidates=max_candidates,
    )
    if not clip_seeds:
        raise RuntimeError("image pipeline produced zero clip assets")

    orientation = describe_orientation(width=width, height=height)
    return SourceContext(
        title=source_file.stem.replace("_", " ").replace("-", " "),
        description=f"{orientation} still image processed into short-form motion previews.",
        uploader=None,
        duration_seconds=max(durations),
        source_url=source_url,
        clip_seeds=clip_seeds,
        processing_mode="real",
        selection_strategy="image-still",
        source_type="image_upload",
        source_platform="Upload",
        visual_summary=visual_summary,
        preview_asset_url=source_url,
        download_asset_url=source_url,
        thumbnail_url=source_url,
    )


def download_source(*, video_url: str, work_dir: Path, ffmpeg_path: str, request_id: str) -> dict[str, Any]:
    if video_url and not video_url.startswith("http"):
        video_url = "https://" + video_url
    is_live = "youtube.com/live/" in video_url or "/live/" in video_url
    options = {
        "quiet": True,
        "no_warnings": False,
        "noprogress": True,
        "noplaylist": True,
        "outtmpl": str(work_dir / "source.%(ext)s"),
        "merge_output_format": "mp4",
        "overwrites": True,
        "retries": 5,
        "fragment_retries": 5,
        "extractor_retries": 2,
        "file_access_retries": 2,
        "socket_timeout": 60,
        "http_chunk_size": 10485760,
        "concurrent_fragment_downloads": 1,
        "ffmpeg_location": str(Path(ffmpeg_path).parent),
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": ["en", "en-US", "en-GB", "en.*"],
        "subtitlesformat": "vtt/best",
        "extractor_args": {"youtube": {"player_client": ["android", "web"]}},
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Mobile Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        },
        "logger": YTDLPLogProxy(request_id),
    }

    if is_live:
        options["format"] = "bestvideo[height<=720]+bestaudio/best[height<=720]/best"
        options["live_from_start"] = False
        options["wait_for_video"] = None
    else:
        options["format"] = "bestvideo+bestaudio/best[height<=720]/best"

    logger.info(
        "source_download_start request_id=%s video_url=%s work_dir=%s format=%s",
        request_id,
        video_url,
        work_dir,
        options["format"],
    )
    try:
        with YoutubeDL(options) as ydl:
            info = ydl.extract_info(video_url, download=True)
    except Exception as error:
        hostname = urlparse(video_url).netloc.lower()
        is_youtube_source = "youtube" in hostname or "youtu.be" in hostname
        if not is_youtube_source:
            raise

        retry_options = {
            **options,
            "extractor_args": {"youtube": {"player_client": ["ios"]}},
        }
        logger.warning(
            "source_download_retry request_id=%s player_client=ios reason=%s",
            request_id,
            error,
        )
        with YoutubeDL(retry_options) as ydl:
            info = ydl.extract_info(video_url, download=True)
    logger.info(
        "source_download_complete request_id=%s title=%s duration=%s webpage_url=%s",
        request_id,
        info.get("title"),
        info.get("duration"),
        info.get("webpage_url") or video_url,
    )
    return info


def locate_source_file(work_dir: Path) -> Path:
    candidates = [
        path
        for path in work_dir.iterdir()
        if path.is_file() and path.suffix.lower() in VIDEO_EXTENSIONS
    ]

    if not candidates:
        raise FileNotFoundError("yt-dlp did not produce a video file")

    return max(candidates, key=lambda path: path.stat().st_size)


def stage_local_source(*, source_path: Path, work_dir: Path) -> Path:
    if not source_path.exists():
        raise FileNotFoundError(f"uploaded source not found: {source_path}")
    target = work_dir / source_path.name
    shutil.copy2(source_path, target)
    return target


def build_segment_plan(
    *,
    duration_seconds: Optional[int],
    chapters: List[dict[str, Any]],
    transcript_windows: List[TranscriptWindow],
    structure_segments: List[dict[str, float]] | None = None,
    max_candidates: int,
) -> tuple[List[dict[str, Any]], str]:
    clip_length = choose_clip_length(duration_seconds)
    transcript_segments = build_transcript_segments(transcript_windows, clip_length, max_candidates=max_candidates)
    if transcript_segments:
        return transcript_segments[:max_candidates], "transcript"

    if structure_segments:
        return dedupe_segments(structure_segments)[:max_candidates], "speech-structure"

    segments = build_chapter_segments(chapters=chapters, clip_length=clip_length, max_candidates=max_candidates)
    if segments:
        return segments[:max_candidates], "chapters"

    if duration_seconds is None or duration_seconds <= 0:
        planned = []
        for index in range(max_candidates):
            planned.append({"start": float(index * max(clip_length // 2, 5)), "duration": float(clip_length)})
        return planned, "timeline"

    latest_start = max(float(duration_seconds - clip_length), 0.0)
    if latest_start == 0:
        return [{"start": 0.0, "duration": float(clip_length)}], "timeline"

    fractions = [
        max(0.0, min(0.98, index / max(max_candidates, 1)))
        for index in range(1, max_candidates + 1)
    ]
    planned = []
    for fraction in fractions:
        start = min(latest_start, max(0.0, duration_seconds * fraction))
        planned.append({"start": round(start, 2), "duration": float(clip_length)})

    return dedupe_segments(planned)[:max_candidates], "timeline"


def build_chapter_segments(chapters: List[dict[str, Any]], clip_length: int, *, max_candidates: int) -> List[dict[str, float]]:
    planned = []
    for chapter in chapters[: max(max_candidates, 6)]:
        start = float(chapter.get("start_time") or 0.0)
        end = float(chapter.get("end_time") or 0.0)
        duration = float(min(clip_length, max(end - start, clip_length)))
        planned.append({"start": round(start, 2), "duration": duration})
        if len(planned) >= max_candidates:
            break

    return dedupe_segments(planned)[:max_candidates]


def build_transcript_segments(
    transcript_windows: List[TranscriptWindow],
    clip_length: int,
    *,
    max_candidates: int,
) -> List[dict[str, Any]]:
    if not transcript_windows:
        return []

    selected: List[TranscriptWindow] = []
    min_start_gap = max(7.0, min(14.0, float(clip_length) * 0.55))
    for window in sorted(transcript_windows, key=lambda current: current.score, reverse=True):
        if any(is_duplicate_transcript_window(window, existing, min_start_gap=min_start_gap) for existing in selected):
            continue
        selected.append(window)
        if len(selected) == max_candidates:
            break

    planned = []
    for index, window in enumerate(sorted(selected, key=lambda current: (-current.score, current.start_seconds)), start=1):
        padded_start = max(window.start_seconds - TRANSCRIPT_LEAD_IN_SECONDS, 0.0)
        window_duration = max(window.end_seconds - window.start_seconds, 1.0)
        duration_ceiling = min(MAX_TRANSCRIPT_CLIP_DURATION, max(float(clip_length), 12.0))
        duration = min(
            max(window_duration + TRANSCRIPT_LEAD_IN_SECONDS + TRANSCRIPT_TAIL_SECONDS, MIN_TRANSCRIPT_CLIP_DURATION),
            duration_ceiling,
        )
        planned.append(
            {
                "start": round(padded_start, 2),
                "duration": round(duration, 2),
                "transcript_excerpt": window.excerpt,
                "format": segment_format(index),
            }
        )

    return planned


def is_duplicate_transcript_window(candidate: TranscriptWindow, existing: TranscriptWindow, *, min_start_gap: float) -> bool:
    if abs(candidate.start_seconds - existing.start_seconds) < min_start_gap:
        return True

    candidate_tokens = significant_tokens(candidate.excerpt)
    existing_tokens = significant_tokens(existing.excerpt)
    if not candidate_tokens or not existing_tokens:
        return False

    overlap = len(candidate_tokens & existing_tokens)
    denominator = max(min(len(candidate_tokens), len(existing_tokens)), 1)
    return (overlap / denominator) >= 0.72


def significant_tokens(value: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9']+", value.lower())
        if len(token) > 3
        and token
        not in {
            "that",
            "this",
            "with",
            "from",
            "they",
            "them",
            "your",
            "have",
            "just",
            "like",
            "what",
            "when",
            "where",
            "there",
            "because",
        }
    }


def dedupe_segments(segments: List[dict[str, float]]) -> List[dict[str, float]]:
    deduped = []
    kept_starts: list[float] = []
    for segment in segments:
        start = float(segment["start"])
        duration = float(segment.get("duration", 0.0))
        min_gap = max(4.0, min(10.0, duration * 0.45))
        if any(abs(start - existing_start) < min_gap for existing_start in kept_starts):
            continue
        kept_starts.append(start)
        deduped.append(segment)
    return deduped


def choose_clip_length(duration_seconds: Optional[int]) -> int:
    if duration_seconds is None or duration_seconds <= 0:
        return 14
    if duration_seconds <= 24:
        return max(6, duration_seconds // 2)
    if duration_seconds <= 60:
        return max(8, min(14, duration_seconds // 4))
    if duration_seconds <= 180:
        return 15
    return 16


def create_clips(
    *,
    source_file: Path,
    generated_dir: Path,
    request_id: str,
    segments: List[dict[str, float]],
    public_base_url: str,
    ffmpeg_path: str,
    settings: Settings,
    max_candidates: int,
) -> List[ClipSeed]:
    seeds: List[ClipSeed] = []
    for index, segment in enumerate(segments[:max_candidates], start=1):
        output_name = f"clip_{index:03d}_raw.mp4"
        output_path = generated_dir / output_name
        try:
            cut_clip(
                settings=settings,
                ffmpeg_path=ffmpeg_path,
                source_file=source_file,
                output_path=output_path,
                start=segment["start"],
                duration=segment["duration"],
            )
            ensure_clip_output(output_path)
        except Exception:
            continue

        clip_url = f"{public_base_url}/generated/{request_id}/{quote(output_name)}"
        preview_output_name = f"clip_{index:03d}_preview.jpg"
        preview_output_path = generated_dir / preview_output_name
        preview_image_url = create_preview_image_url(
            ffmpeg_path=ffmpeg_path,
            input_path=output_path,
            output_path=preview_output_path,
            public_base_url=public_base_url,
            request_id=request_id,
            public_name=preview_output_name,
        )
        seeds.append(
            ClipSeed(
                id=f"clip_{index:03d}",
                start_time=format_timestamp(segment["start"]),
                end_time=format_timestamp(segment["start"] + segment["duration"]),
                asset_path=output_path,
                clip_url=clip_url,
                raw_clip_url=clip_url,
                preview_image_url=preview_image_url,
                format=str(segment.get("format", segment_format(index))),
                transcript_excerpt=string_or_none(segment.get("transcript_excerpt")),
                duration=max(int(round(float(segment["duration"]))), 1),
            )
        )
    return seeds


def create_audio_clips(
    *,
    source_file: Path,
    generated_dir: Path,
    request_id: str,
    segments: List[dict[str, float]],
    public_base_url: str,
    ffmpeg_path: str,
    settings: Settings,
    max_candidates: int,
) -> List[ClipSeed]:
    seeds: List[ClipSeed] = []
    for index, segment in enumerate(segments[:max_candidates], start=1):
        output_name = f"clip_{index:03d}_raw.mp4"
        output_path = generated_dir / output_name
        try:
            create_audio_preview_clip(
                settings=settings,
                ffmpeg_path=ffmpeg_path,
                source_file=source_file,
                output_path=output_path,
                start=float(segment["start"]),
                duration=float(segment["duration"]),
            )
            ensure_clip_output(output_path)
        except Exception:
            continue

        clip_url = f"{public_base_url}/generated/{request_id}/{quote(output_name)}"
        preview_output_name = f"clip_{index:03d}_preview.jpg"
        preview_output_path = generated_dir / preview_output_name
        preview_image_url = create_preview_image_url(
            ffmpeg_path=ffmpeg_path,
            input_path=output_path,
            output_path=preview_output_path,
            public_base_url=public_base_url,
            request_id=request_id,
            public_name=preview_output_name,
        )
        seeds.append(
            ClipSeed(
                id=f"clip_{index:03d}",
                start_time=format_timestamp(float(segment["start"])),
                end_time=format_timestamp(float(segment["start"]) + float(segment["duration"])),
                asset_path=output_path,
                clip_url=clip_url,
                raw_clip_url=clip_url,
                preview_image_url=preview_image_url,
                format=str(segment.get("format", segment_format(index))),
                transcript_excerpt=string_or_none(segment.get("transcript_excerpt")),
                duration=max(int(round(float(segment["duration"]))), 1),
            )
        )
    return seeds


def create_image_clips(
    *,
    source_file: Path,
    generated_dir: Path,
    request_id: str,
    segments: List[dict[str, float]],
    public_base_url: str,
    ffmpeg_path: str,
    settings: Settings,
    max_candidates: int,
) -> List[ClipSeed]:
    seeds: List[ClipSeed] = []
    for index, segment in enumerate(segments[:max_candidates], start=1):
        output_name = f"clip_{index:03d}_raw.mp4"
        output_path = generated_dir / output_name
        try:
            create_image_preview_clip(
                settings=settings,
                ffmpeg_path=ffmpeg_path,
                source_file=source_file,
                output_path=output_path,
                duration=float(segment["duration"]),
            )
            ensure_clip_output(output_path)
        except Exception:
            continue

        clip_url = f"{public_base_url}/generated/{request_id}/{quote(output_name)}"
        preview_output_name = f"clip_{index:03d}_preview.jpg"
        preview_output_path = generated_dir / preview_output_name
        preview_image_url = create_preview_image_url(
            ffmpeg_path=ffmpeg_path,
            input_path=output_path,
            output_path=preview_output_path,
            public_base_url=public_base_url,
            request_id=request_id,
            public_name=preview_output_name,
        )
        seeds.append(
            ClipSeed(
                id=f"clip_{index:03d}",
                start_time="00:00",
                end_time=format_timestamp(float(segment["duration"])),
                asset_path=output_path,
                clip_url=clip_url,
                raw_clip_url=clip_url,
                preview_image_url=preview_image_url,
                format=str(segment.get("format", segment_format(index))),
                transcript_excerpt=string_or_none(segment.get("transcript_excerpt")),
                duration=max(int(round(float(segment["duration"]))), 1),
            )
        )
    return seeds


def create_audio_preview_clip(
    *,
    settings: Settings,
    ffmpeg_path: str,
    source_file: Path,
    output_path: Path,
    start: float,
    duration: float,
) -> None:
    encoder_name = resolve_video_encoder(settings=settings, ffmpeg_path=ffmpeg_path)
    encoder_args = build_video_encoder_args(encoder_name=encoder_name, target="clip")
    command = [
        ffmpeg_path,
        "-y",
        "-ss",
        f"{start}",
        "-t",
        f"{duration}",
        "-i",
        str(source_file),
        "-filter_complex",
        "[0:a]showwaves=s=720x1280:mode=line:colors=0x22D3EE,format=yuv420p[v]",
        "-map",
        "[v]",
        "-map",
        "0:a:0",
        *encoder_args,
        "-c:a",
        "aac",
        "-movflags",
        "+faststart",
        str(output_path),
    ]
    subprocess.run(command, check=True, capture_output=True, text=True)


def create_image_preview_clip(
    *,
    settings: Settings,
    ffmpeg_path: str,
    source_file: Path,
    output_path: Path,
    duration: float,
) -> None:
    encoder_name = resolve_video_encoder(settings=settings, ffmpeg_path=ffmpeg_path)
    encoder_args = build_video_encoder_args(encoder_name=encoder_name, target="clip")
    command = [
        ffmpeg_path,
        "-y",
        "-loop",
        "1",
        "-i",
        str(source_file),
        "-t",
        f"{duration}",
        "-vf",
        "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,format=yuv420p",
        "-r",
        "30",
        *encoder_args,
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        str(output_path),
    ]
    subprocess.run(command, check=True, capture_output=True, text=True)


def cut_clip(
    *,
    settings: Settings,
    ffmpeg_path: str,
    source_file: Path,
    output_path: Path,
    start: float,
    duration: float,
) -> None:
    encoder_name = resolve_video_encoder(settings=settings, ffmpeg_path=ffmpeg_path)
    encoder_args = build_video_encoder_args(encoder_name=encoder_name, target="clip")
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
        *encoder_args,
        "-c:a",
        "aac",
        "-movflags",
        "+faststart",
        str(output_path),
    ]

    subprocess.run(command, check=True, capture_output=True, text=True)


def probe_video_duration(*, source_file: Path, ffmpeg_path: str) -> Optional[int]:
    command = [ffmpeg_path, "-i", str(source_file), "-f", "null", "-"]
    process = subprocess.run(command, capture_output=True, text=True)
    combined = f"{process.stdout}\n{process.stderr}"
    match = re.search(r"Duration:\s*(\d{2}):(\d{2}):(\d{2}(?:\.\d+)?)", combined)
    if not match:
        return None

    hours = int(match.group(1))
    minutes = int(match.group(2))
    seconds = float(match.group(3))
    return int((hours * 3600) + (minutes * 60) + seconds)


def ensure_clip_output(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"clip output missing: {path}")
    if path.stat().st_size < 8_192:
        raise RuntimeError(f"clip output too small to be valid: {path}")


def create_social_exports(
    *,
    settings: Settings,
    clip_results: List[Any],
    clip_seeds: List[ClipSeed],
    generated_dir: Path,
    request_id: str,
    public_base_url: str,
    ffmpeg_path: str,
) -> tuple[List[Any], int]:
    seed_map = {seed.id: seed for seed in clip_seeds}
    exported_results: List[Any] = []
    edited_assets_created = 0

    for clip in clip_results:
        seed = seed_map.get(getattr(clip, "id", ""))
        existing_preview_url = getattr(clip, "preview_url", None)
        existing_clip_url = getattr(clip, "clip_url", None)
        raw_clip_url = seed.raw_clip_url if seed else getattr(clip, "raw_clip_url", None) or existing_clip_url
        fallback_preview_url = existing_preview_url or raw_clip_url or existing_clip_url
        fallback_preview_image_url = (
            seed.preview_image_url if seed else getattr(clip, "preview_image_url", None)
        ) or getattr(clip, "thumbnail_url", None)

        if not seed or not seed.asset_path.exists():
            exported_results.append(
                clip.model_copy(
                    update={
                        "clip_url": fallback_preview_url,
                        "preview_url": fallback_preview_url,
                        "raw_clip_url": raw_clip_url,
                        "preview_image_url": fallback_preview_image_url,
                        "edit_profile": "Source cut fallback",
                        "aspect_ratio": "source",
                    }
                )
            )
            continue

        output_name = f"{seed.id}.mp4"
        output_path = generated_dir / output_name

        try:
            edit_profile = export_social_ready_clip(
                settings=settings,
                ffmpeg_path=ffmpeg_path,
                input_path=seed.asset_path,
                output_path=output_path,
                title_text=build_title_overlay(getattr(clip, "hook", ""), getattr(clip, "format", seed.format)),
                subtitle_text=build_subtitle_overlay(
                    getattr(clip, "transcript_excerpt", None) or getattr(clip, "caption", "")
                ),
            )
            ensure_clip_output(output_path)
            edited_url = f"{public_base_url}/generated/{request_id}/{quote(output_name)}"
            preview_output_name = f"{seed.id}_preview.jpg"
            preview_output_path = generated_dir / preview_output_name
            preview_image_url = create_preview_image_url(
                ffmpeg_path=ffmpeg_path,
                input_path=output_path,
                output_path=preview_output_path,
                public_base_url=public_base_url,
                request_id=request_id,
                public_name=preview_output_name,
            ) or fallback_preview_image_url
            exported_results.append(
                clip.model_copy(
                    update={
                        "clip_url": edited_url,
                        "preview_url": edited_url,
                        "raw_clip_url": raw_clip_url,
                        "edited_clip_url": edited_url,
                        "preview_image_url": preview_image_url,
                        "edit_profile": edit_profile,
                        "aspect_ratio": "9:16",
                    }
                )
            )
            edited_assets_created += 1
        except Exception as error:
            logger.warning(
                "social_export_fallback request_id=%s clip_id=%s reason=%s",
                request_id,
                getattr(clip, "id", "unknown"),
                error,
            )
            exported_results.append(
                clip.model_copy(
                    update={
                        "clip_url": fallback_preview_url,
                        "preview_url": fallback_preview_url,
                        "raw_clip_url": raw_clip_url,
                        "preview_image_url": fallback_preview_image_url,
                        "edit_profile": "Source cut fallback",
                        "aspect_ratio": "source",
                    }
                )
            )

    return exported_results, edited_assets_created


def export_social_ready_clip(
    *,
    settings: Settings,
    ffmpeg_path: str,
    input_path: Path,
    output_path: Path,
    title_text: str,
    subtitle_text: str,
) -> str:
    bold_font = resolve_drawtext_font(bold=True)
    regular_font = resolve_drawtext_font(bold=False)

    base_filter_steps = [
        "scale=720:1280:force_original_aspect_ratio=increase",
        "crop=720:1280",
        "drawbox=x=0:y=0:w=iw:h=228:color=black@0.28:t=fill",
        "drawbox=x=0:y=ih-342:w=iw:h=342:color=black@0.54:t=fill",
    ]

    with tempfile.TemporaryDirectory(prefix="iwa_text_") as temp_dir:
        title_path = Path(temp_dir) / "title.txt"
        subtitle_path = Path(temp_dir) / "subtitle.txt"
        title_path.write_text(title_text, encoding="utf-8")
        subtitle_path.write_text(subtitle_text, encoding="utf-8")

        overlay_filter_steps = list(base_filter_steps)
        overlay_filter_steps.append(
            drawtext_filter(
                textfile=title_path,
                fontfile=bold_font,
                fontsize=46,
                x="40",
                y="52",
                fontcolor="white",
                line_spacing=10,
            )
        )
        overlay_filter_steps.append(
            drawtext_filter(
                textfile=subtitle_path,
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

        overlay_command = build_social_export_command(
            settings=settings,
            ffmpeg_path=ffmpeg_path,
            input_path=input_path,
            output_path=output_path,
            filter_steps=overlay_filter_steps,
        )

        try:
            subprocess.run(overlay_command, check=True, capture_output=True, text=True)
            return "9:16 Smart Crop + Overlay Copy"
        except subprocess.CalledProcessError as error:
            stderr = error.stderr or ""
            if "No such filter: 'drawtext'" not in stderr:
                raise

        fallback_command = build_social_export_command(
            settings=settings,
            ffmpeg_path=ffmpeg_path,
            input_path=input_path,
            output_path=output_path,
            filter_steps=base_filter_steps,
        )
        subprocess.run(fallback_command, check=True, capture_output=True, text=True)
        return "9:16 Smart Crop"


def build_social_export_command(
    *,
    settings: Settings,
    ffmpeg_path: str,
    input_path: Path,
    output_path: Path,
    filter_steps: List[str],
) -> List[str]:
    encoder_name = resolve_video_encoder(settings=settings, ffmpeg_path=ffmpeg_path)
    encoder_args = build_video_encoder_args(encoder_name=encoder_name, target="social")
    return [
        ffmpeg_path,
        "-y",
        "-i",
        str(input_path),
        "-map",
        "0:v:0",
        "-map",
        "0:a?",
        "-vf",
        ",".join(filter_steps),
        *encoder_args,
        "-c:a",
        "aac",
        "-movflags",
        "+faststart",
        str(output_path),
    ]


def create_preview_image_url(
    *,
    ffmpeg_path: str,
    input_path: Path,
    output_path: Path,
    public_base_url: str,
    request_id: str,
    public_name: str,
) -> Optional[str]:
    command = [
        ffmpeg_path,
        "-y",
        "-ss",
        "00:00:01.000",
        "-i",
        str(input_path),
        "-frames:v",
        "1",
        "-q:v",
        "3",
        str(output_path),
    ]

    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
    except Exception:
        return None

    if not output_path.exists() or output_path.stat().st_size <= 0:
        return None

    return f"{public_base_url}/generated/{request_id}/{quote(public_name)}"


def drawtext_filter(
    *,
    textfile: Path,
    fontfile: Optional[str],
    fontsize: int,
    x: str,
    y: str,
    fontcolor: str,
    line_spacing: int,
    box: bool = False,
    boxcolor: str = "black@0.0",
    boxborderw: int = 0,
) -> str:
    parts = [
        f"textfile={escape_filter_value(str(textfile))}",
        f"fontsize={fontsize}",
        f"x={x}",
        f"y={y}",
        f"fontcolor={fontcolor}",
        f"line_spacing={line_spacing}",
        "fix_bounds=true",
    ]
    if fontfile:
        parts.append(f"fontfile={escape_filter_value(fontfile)}")
    if box:
        parts.append("box=1")
        parts.append(f"boxcolor={boxcolor}")
        parts.append(f"boxborderw={boxborderw}")

    return "drawtext=" + ":".join(parts)


def resolve_drawtext_font(*, bold: bool) -> Optional[str]:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
    ]

    for candidate in candidates:
        if Path(candidate).exists():
            return candidate

    return None


def escape_filter_value(value: str) -> str:
    return value.replace("\\", "\\\\").replace(":", "\\:").replace(" ", "\\ ")


def build_title_overlay(hook: str, fallback_label: str) -> str:
    text = hook.strip() or fallback_label.strip() or "IWA Clip"
    return wrap_overlay_text(text, max_chars_per_line=18, max_lines=3)


def build_subtitle_overlay(value: str) -> str:
    text = value.strip() or "Auto-cut for short-form review and publishing."
    return wrap_overlay_text(text, max_chars_per_line=28, max_lines=4)


def wrap_overlay_text(value: str, *, max_chars_per_line: int, max_lines: int) -> str:
    normalized = re.sub(r"\s+", " ", value).strip()
    lines = textwrap.wrap(normalized, width=max_chars_per_line)
    clipped = lines[:max_lines]

    if not clipped:
        return normalized[: max_chars_per_line * max_lines]

    remaining = lines[max_lines:]
    if remaining:
        clipped[-1] = clipped[-1].rstrip(". ") + "..."

    return "\n".join(clipped)


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


def detect_source_platform(source_url: str) -> str:
    lower = source_url.lower()
    if "youtube" in lower or "youtu.be" in lower:
        return "YouTube"
    if "tiktok" in lower:
        return "TikTok"
    if "instagram" in lower:
        return "Instagram"
    if "twitch" in lower:
        return "Twitch"
    return "Upload"


def flatten_transcript_windows(windows: List[TranscriptWindow]) -> str:
    if not windows:
        return ""
    ordered = sorted(windows, key=lambda window: window.start_seconds)
    parts: list[str] = []
    seen: set[str] = set()
    for window in ordered:
        excerpt = normalize_caption_text(window.excerpt)
        if not excerpt:
            continue
        if excerpt in seen:
            continue
        seen.add(excerpt)
        parts.append(excerpt)
    return " ".join(parts).strip()


def probe_media_duration(*, source_file: Path, settings: Settings) -> Optional[int]:
    ffprobe_path = resolve_ffprobe_path(settings)
    if ffprobe_path:
        try:
            process = subprocess.run(
                [
                    ffprobe_path,
                    "-v",
                    "error",
                    "-show_entries",
                    "format=duration",
                    "-of",
                    "default=noprint_wrappers=1:nokey=1",
                    str(source_file),
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            value = (process.stdout or "").strip()
            if value:
                return int(float(value))
        except Exception:
            pass

    ffmpeg_path = resolve_ffmpeg_path(settings)
    if ffmpeg_path:
        return probe_video_duration(source_file=source_file, ffmpeg_path=ffmpeg_path)
    return None


def transcribe_audio_source(*, settings: Settings, source_file: Path) -> tuple[List[TranscriptWindow], Optional[str]]:
    if not settings.openai_api_key:
        return [], None

    try:
        from openai import OpenAI

        client = OpenAI(api_key=settings.openai_api_key)
        with source_file.open("rb") as handle:
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=handle,
                response_format="verbose_json",
                timestamp_granularities=["segment"],
            )
    except Exception as error:
        logger.warning("audio_transcription_fallback source=%s reason=%s", source_file, error)
        return [], None

    transcript = str(getattr(response, "text", "") or "").strip() or None
    segments = getattr(response, "segments", None) or []
    windows = build_transcript_windows_from_segments(segments)
    if not windows and transcript:
        duration = probe_media_duration(source_file=source_file, settings=settings) or 15
        windows = [
            TranscriptWindow(
                start_seconds=0.0,
                end_seconds=float(min(duration, 18)),
                excerpt=transcript,
                score=score_excerpt(transcript),
            )
        ]
    return windows, transcript


def build_transcript_windows_from_segments(segments: list[object]) -> List[TranscriptWindow]:
    windows: List[TranscriptWindow] = []
    for segment in segments:
        start = float(getattr(segment, "start", 0.0) or 0.0)
        end = float(getattr(segment, "end", 0.0) or 0.0)
        text = normalize_caption_text(str(getattr(segment, "text", "") or ""))
        if not text or end <= start:
            continue
        windows.append(
            TranscriptWindow(
                start_seconds=start,
                end_seconds=end,
                excerpt=text,
                score=score_excerpt(text),
            )
        )
    return build_transcript_windows_from_cues(
        [(window.start_seconds, window.end_seconds, window.excerpt) for window in windows]
    )


def analyze_image_source(*, settings: Settings, source_file: Path) -> str:
    if settings.openai_api_key:
        summary = analyze_image_with_openai(settings=settings, source_file=source_file)
        if summary:
            return summary
    return describe_image_fallback(source_file=source_file, settings=settings)


def analyze_image_with_openai(*, settings: Settings, source_file: Path) -> Optional[str]:
    try:
        from openai import OpenAI

        mime_type = guess_image_mime_type(source_file.suffix.lower())
        encoded = base64.b64encode(source_file.read_bytes()).decode("utf-8")
        client = OpenAI(api_key=settings.openai_api_key)
        response = client.responses.create(
            model=settings.openai_model,
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": (
                                "Describe this uploaded image for a short-form content repurposing system. "
                                "Return one concise paragraph that focuses on what is visibly happening, the likely framing, "
                                "and what kind of hook or caption packaging would fit."
                            ),
                        },
                        {
                            "type": "input_image",
                            "image_url": f"data:{mime_type};base64,{encoded}",
                        },
                    ],
                }
            ],
        )
        summary = str(getattr(response, "output_text", "") or "").strip()
        return summary or None
    except Exception as error:
        logger.warning("image_analysis_fallback source=%s reason=%s", source_file, error)
        return None


def describe_image_fallback(*, source_file: Path, settings: Settings) -> str:
    width, height = probe_image_dimensions(source_file=source_file, settings=settings)
    orientation = describe_orientation(width=width, height=height)
    filename_phrase = source_file.stem.replace("_", " ").replace("-", " ").strip()
    if filename_phrase:
        return (
            f"{orientation.capitalize()} still image from {filename_phrase}. "
            "Package it with a clean, punchy hook, clear subject framing, and fast caption payoff."
        )
    return (
        f"{orientation.capitalize()} still image with a strong single-frame composition. "
        "Package it with a punchy hook and a caption that makes the subject obvious fast."
    )


def probe_image_dimensions(*, source_file: Path, settings: Settings) -> tuple[int | None, int | None]:
    ffprobe_path = resolve_ffprobe_path(settings)
    if not ffprobe_path:
        return None, None
    try:
        process = subprocess.run(
            [
                ffprobe_path,
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-show_entries",
                "stream=width,height",
                "-of",
                "json",
                str(source_file),
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        payload = json.loads(process.stdout or "{}")
        streams = payload.get("streams") or []
        if not streams:
            return None, None
        stream = streams[0]
        return int(stream.get("width") or 0) or None, int(stream.get("height") or 0) or None
    except Exception:
        return None, None


def describe_orientation(*, width: int | None, height: int | None) -> str:
    if width and height:
        if height > width:
            return "portrait"
        if width > height:
            return "landscape"
    return "square"


def guess_image_mime_type(suffix: str) -> str:
    if suffix in {".jpg", ".jpeg"}:
        return "image/jpeg"
    if suffix == ".png":
        return "image/png"
    if suffix == ".webp":
        return "image/webp"
    if suffix in {".heic", ".heif"}:
        return "image/heic"
    return "image/png"


def load_transcript_windows(work_dir: Path) -> List[TranscriptWindow]:
    subtitle_files = sorted(work_dir.rglob("*.vtt"))
    for subtitle_file in subtitle_files:
        windows = parse_vtt_windows(subtitle_file)
        if windows:
            return windows
    return []


def parse_vtt_windows(path: Path) -> List[TranscriptWindow]:
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    cues: List[tuple[float, float, str]] = []
    index = 0

    while index < len(lines):
        line = lines[index].strip()

        if not line or line.startswith("WEBVTT") or line.startswith("Kind:") or line.startswith("Language:") or line.startswith("NOTE"):
            index += 1
            continue

        if "-->" not in line:
            index += 1
            continue

        start_text, end_text = [part.strip() for part in line.split("-->", 1)]
        start_seconds = parse_vtt_timestamp(start_text.split(" ")[0])
        end_seconds = parse_vtt_timestamp(end_text.split(" ")[0])
        index += 1

        text_lines = []
        while index < len(lines) and lines[index].strip():
            text_lines.append(lines[index].strip())
            index += 1

        text = normalize_caption_text(" ".join(text_lines))
        if text and end_seconds > start_seconds:
            if not cues or cues[-1][2] != text:
                cues.append((start_seconds, end_seconds, text))

    return build_transcript_windows_from_cues(cues)


def build_transcript_windows_from_cues(cues: List[tuple[float, float, str]]) -> List[TranscriptWindow]:
    windows: List[TranscriptWindow] = []
    for start_index in range(len(cues)):
        window_start = cues[start_index][0]
        window_end = cues[start_index][1]
        parts = [cues[start_index][2]]

        for current_index in range(start_index + 1, len(cues)):
            cue_start, cue_end, cue_text = cues[current_index]
            if cue_start - window_start > 18:
                break
            window_end = cue_end
            parts.append(cue_text)
            joined = " ".join(parts)
            if len(joined.split()) >= 24 or (window_end - window_start) >= 10:
                break

        excerpt = normalize_caption_text(" ".join(parts))
        if len(excerpt.split()) < 6:
            continue
        previous_end = cues[start_index - 1][1] if start_index > 0 else None
        gap_before = max(window_start - previous_end, 0.0) if previous_end is not None else 0.0
        duration = max(window_end - window_start, 0.1)

        windows.append(
            TranscriptWindow(
                start_seconds=window_start,
                end_seconds=window_end,
                excerpt=excerpt,
                score=score_transcript_window(
                    excerpt=excerpt,
                    duration_seconds=duration,
                    gap_before_seconds=gap_before,
                ),
            )
        )

    return windows


def parse_vtt_timestamp(value: str) -> float:
    parts = value.replace(",", ".").split(":")
    parts = [part.strip() for part in parts]
    if len(parts) == 3:
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds = float(parts[2])
        return hours * 3600 + minutes * 60 + seconds
    if len(parts) == 2:
        minutes = int(parts[0])
        seconds = float(parts[1])
        return minutes * 60 + seconds
    return float(parts[0])


def normalize_caption_text(value: str) -> str:
    text = re.sub(r"<[^>]+>", " ", value)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def score_excerpt(excerpt: str) -> int:
    lower = excerpt.lower()
    words = excerpt.split()
    keyword_hits = sum(
        1
        for keyword in [
            "how",
            "why",
            "best",
            "worst",
            "first",
            "mistake",
            "secret",
            "never",
            "stop",
            "you",
            "your",
        ]
        if keyword in lower
    )
    punctuation_bonus = 3 if "?" in excerpt or "!" in excerpt else 0
    payoff_bonus = 6 if any(keyword in lower for keyword in ["but", "then", "because", "finally", "realized", "changed"]) else 0
    hook_bonus = 5 if words and words[0].lower().strip(".,!?") in {"stop", "why", "how", "this", "nobody", "never"} else 0
    return min(len(words), 35) + (keyword_hits * 4) + punctuation_bonus + payoff_bonus + hook_bonus


def score_transcript_window(*, excerpt: str, duration_seconds: float, gap_before_seconds: float) -> int:
    words = excerpt.split()
    speech_density = len(words) / max(duration_seconds, 0.1)
    density_bonus = 0
    if 2.2 <= speech_density <= 4.8:
        density_bonus = 8
    elif speech_density > 4.8:
        density_bonus = 4

    boundary_bonus = 4 if excerpt.rstrip().endswith((".", "!", "?")) else 0
    reset_bonus = 3 if 0.25 <= gap_before_seconds <= 1.8 else 0
    dead_space_penalty = 8 if gap_before_seconds > 3.0 else 0
    short_window_penalty = 6 if len(words) < 10 else 0

    return max(
        0,
        score_excerpt(excerpt)
        + density_bonus
        + boundary_bonus
        + reset_bonus
        - dead_space_penalty
        - short_window_penalty,
    )
