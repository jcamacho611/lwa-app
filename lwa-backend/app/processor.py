from __future__ import annotations

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
from urllib.parse import quote

try:
    import imageio_ffmpeg  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    imageio_ffmpeg = None

from yt_dlp import YoutubeDL

from .config import Settings

logger = logging.getLogger("uvicorn.error")


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

    if platform.system() == "Darwin" and ffmpeg_supports_encoder(ffmpeg_path, "h264_videotoolbox"):
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
        "veryfast",
        "-crf",
        "23" if target == "clip" else "22",
        "-pix_fmt",
        "yuv420p",
    ]


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
        info = download_source(
            video_url=video_url,
            work_dir=work_dir,
            ffmpeg_path=ffmpeg_path,
            request_id=request_id,
        )
        source_file = locate_source_file(work_dir)
        transcript_windows = load_transcript_windows(work_dir)

        duration_seconds = parse_duration_seconds(info.get("duration"))
        if duration_seconds is None:
            duration_seconds = probe_video_duration(source_file=source_file, ffmpeg_path=ffmpeg_path)
            if duration_seconds is None:
                logger.warning(
                    "source_probe_warning request_id=%s source_file=%s reason=duration_unavailable",
                    request_id,
                    source_file,
                )
        segments, selection_strategy = build_segment_plan(
            duration_seconds=duration_seconds,
            chapters=info.get("chapters") or [],
            transcript_windows=transcript_windows,
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
        )
        if not clip_seeds:
            raise RuntimeError("real pipeline produced zero clip assets")
        logger.info(
            "clip_seeds_ready request_id=%s clip_seeds=%s generated_dir=%s",
            request_id,
            len(clip_seeds),
            generated_dir,
        )

    return SourceContext(
        title=str(info.get("title") or "Untitled source"),
        description=str(info.get("description") or ""),
        uploader=string_or_none(info.get("uploader")),
        duration_seconds=duration_seconds,
        source_url=str(info.get("webpage_url") or video_url),
        clip_seeds=clip_seeds,
        processing_mode="real",
        selection_strategy=selection_strategy,
    )


def download_source(*, video_url: str, work_dir: Path, ffmpeg_path: str, request_id: str) -> dict[str, Any]:
    options = {
        "quiet": True,
        "no_warnings": False,
        "noprogress": True,
        "noplaylist": True,
        "outtmpl": str(work_dir / "source.%(ext)s"),
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "merge_output_format": "mp4",
        "overwrites": True,
        "retries": 2,
        "fragment_retries": 2,
        "extractor_retries": 2,
        "file_access_retries": 2,
        "socket_timeout": 20,
        "concurrent_fragment_downloads": 1,
        "ffmpeg_location": str(Path(ffmpeg_path).parent),
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": ["en", "en-US", "en-GB", "en.*"],
        "subtitlesformat": "vtt/best",
        "logger": YTDLPLogProxy(request_id),
    }

    logger.info(
        "source_download_start request_id=%s video_url=%s work_dir=%s format=%s",
        request_id,
        video_url,
        work_dir,
        options["format"],
    )
    with YoutubeDL(options) as ydl:
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
        if path.is_file() and path.suffix.lower() in {".mp4", ".mov", ".mkv", ".webm", ".m4v"}
    ]

    if not candidates:
        raise FileNotFoundError("yt-dlp did not produce a video file")

    return max(candidates, key=lambda path: path.stat().st_size)


def build_segment_plan(
    *,
    duration_seconds: Optional[int],
    chapters: List[dict[str, Any]],
    transcript_windows: List[TranscriptWindow],
) -> tuple[List[dict[str, Any]], str]:
    clip_length = choose_clip_length(duration_seconds)
    transcript_segments = build_transcript_segments(transcript_windows, clip_length)
    if transcript_segments:
        return transcript_segments[:3], "transcript"

    segments = build_chapter_segments(chapters=chapters, clip_length=clip_length)
    if segments:
        return segments[:3], "chapters"

    if duration_seconds is None or duration_seconds <= 0:
        return [
            {"start": 0.0, "duration": float(clip_length)},
            {"start": 15.0, "duration": float(clip_length)},
            {"start": 30.0, "duration": float(clip_length)},
        ], "timeline"

    latest_start = max(float(duration_seconds - clip_length), 0.0)
    if latest_start == 0:
        return [{"start": 0.0, "duration": float(clip_length)}], "timeline"

    fractions = [0.12, 0.42, 0.72]
    planned = []
    for fraction in fractions:
        start = min(latest_start, max(0.0, duration_seconds * fraction))
        planned.append({"start": round(start, 2), "duration": float(clip_length)})

    return dedupe_segments(planned)[:3], "timeline"


def build_chapter_segments(chapters: List[dict[str, Any]], clip_length: int) -> List[dict[str, float]]:
    planned = []
    for chapter in chapters[:6]:
        start = float(chapter.get("start_time") or 0.0)
        end = float(chapter.get("end_time") or 0.0)
        duration = float(min(clip_length, max(end - start, clip_length)))
        planned.append({"start": round(start, 2), "duration": duration})

    return dedupe_segments(planned)


def build_transcript_segments(transcript_windows: List[TranscriptWindow], clip_length: int) -> List[dict[str, Any]]:
    if not transcript_windows:
        return []

    selected: List[TranscriptWindow] = []
    for window in sorted(transcript_windows, key=lambda current: current.score, reverse=True):
        if any(abs(window.start_seconds - existing.start_seconds) < 8 for existing in selected):
            continue
        selected.append(window)
        if len(selected) == 3:
            break

    planned = []
    for index, window in enumerate(sorted(selected, key=lambda current: current.start_seconds), start=1):
        padded_start = max(window.start_seconds - 1.0, 0.0)
        base_duration = max(window.end_seconds - window.start_seconds + 2.0, 8.0)
        duration = min(max(base_duration, float(clip_length)), 24.0)
        planned.append(
            {
                "start": round(padded_start, 2),
                "duration": round(duration, 2),
                "transcript_excerpt": window.excerpt,
                "format": segment_format(index),
            }
        )

    return planned


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
    settings: Settings,
) -> List[ClipSeed]:
    seeds: List[ClipSeed] = []
    for index, segment in enumerate(segments[:3], start=1):
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
            )
        )
    return seeds


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
        raw_clip_url = seed.raw_clip_url if seed else getattr(clip, "raw_clip_url", None) or getattr(clip, "clip_url", None)

        if not seed or not seed.asset_path.exists():
            exported_results.append(
                clip.model_copy(
                    update={
                        "raw_clip_url": raw_clip_url,
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
            ) or seed.preview_image_url
            exported_results.append(
                clip.model_copy(
                    update={
                        "clip_url": edited_url,
                        "raw_clip_url": raw_clip_url,
                        "edited_clip_url": edited_url,
                        "preview_image_url": preview_image_url,
                        "edit_profile": edit_profile,
                        "aspect_ratio": "9:16",
                    }
                )
            )
            edited_assets_created += 1
        except Exception:
            exported_results.append(
                clip.model_copy(
                    update={
                        "clip_url": raw_clip_url or getattr(clip, "clip_url", None),
                        "raw_clip_url": raw_clip_url,
                        "preview_image_url": seed.preview_image_url,
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

        windows.append(
            TranscriptWindow(
                start_seconds=window_start,
                end_seconds=window_end,
                excerpt=excerpt,
                score=score_excerpt(excerpt),
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
    return min(len(words), 35) + (keyword_hits * 4) + punctuation_bonus
