from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

from .models import VideoProbeResult


def check_ffmpeg_available(ffmpeg_binary: str = "ffmpeg", ffprobe_binary: str = "ffprobe") -> bool:
    return shutil.which(ffmpeg_binary) is not None and shutil.which(ffprobe_binary) is not None


def _safe_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _safe_int(value: Any) -> int | None:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _parse_fraction(value: str | None) -> float | None:
    if not value or value in {"0/0", "N/A"}:
        return None
    if "/" in value:
        numerator, denominator = value.split("/", 1)
        try:
            denominator_value = float(denominator)
            if denominator_value == 0:
                return None
            return float(numerator) / denominator_value
        except ValueError:
            return None
    return _safe_float(value)


def probe_video(
    path: str | Path,
    *,
    ffprobe_binary: str = "ffprobe",
    ffmpeg_binary: str = "ffmpeg",
) -> VideoProbeResult:
    input_path = Path(path)
    warnings: list[str] = []
    errors: list[str] = []
    ffmpeg_available = check_ffmpeg_available(ffmpeg_binary=ffmpeg_binary, ffprobe_binary=ffprobe_binary)
    ffprobe_available = shutil.which(ffprobe_binary) is not None

    if not input_path.exists() or not input_path.is_file():
        return VideoProbeResult(
            input_path=str(input_path),
            available=False,
            ffprobe_available=ffprobe_available,
            ffmpeg_available=ffmpeg_available,
            duration_seconds=0.0,
            warnings=["Input video file does not exist."],
            errors=["missing_input_file"],
        )

    if not ffprobe_available:
        return VideoProbeResult(
            input_path=str(input_path),
            available=False,
            ffprobe_available=False,
            ffmpeg_available=ffmpeg_available,
            duration_seconds=0.0,
            warnings=["ffprobe is not available on this system."],
            errors=["ffprobe_unavailable"],
        )

    command = [
        ffprobe_binary,
        "-v",
        "error",
        "-print_format",
        "json",
        "-show_format",
        "-show_streams",
        str(input_path),
    ]

    try:
        completed = subprocess.run(command, check=False, capture_output=True, text=True)
    except FileNotFoundError:
        return VideoProbeResult(
            input_path=str(input_path),
            available=False,
            ffprobe_available=False,
            ffmpeg_available=ffmpeg_available,
            duration_seconds=0.0,
            warnings=["ffprobe binary could not be executed."],
            errors=["ffprobe_unavailable"],
        )
    except Exception as exc:  # pragma: no cover - defensive fallback
        return VideoProbeResult(
            input_path=str(input_path),
            available=False,
            ffprobe_available=True,
            ffmpeg_available=ffmpeg_available,
            duration_seconds=0.0,
            warnings=["ffprobe failed unexpectedly."],
            errors=[type(exc).__name__],
        )

    if completed.returncode != 0:
        stderr_text = (completed.stderr or "").strip()
        return VideoProbeResult(
            input_path=str(input_path),
            available=False,
            ffprobe_available=True,
            ffmpeg_available=ffmpeg_available,
            duration_seconds=0.0,
            warnings=[stderr_text or "ffprobe returned a non-zero exit code."],
            errors=["ffprobe_failed"],
        )

    try:
        payload = json.loads(completed.stdout or "{}")
    except json.JSONDecodeError:
        return VideoProbeResult(
            input_path=str(input_path),
            available=False,
            ffprobe_available=True,
            ffmpeg_available=ffmpeg_available,
            duration_seconds=0.0,
            warnings=["ffprobe returned malformed JSON metadata."],
            errors=["probe_parse_failed"],
        )

    format_section = payload.get("format") or {}
    streams = payload.get("streams") or []
    video_stream = next((stream for stream in streams if stream.get("codec_type") == "video"), {})
    audio_stream = next((stream for stream in streams if stream.get("codec_type") == "audio"), {})

    duration_seconds = _safe_float(format_section.get("duration")) or 0.0
    width = _safe_int(video_stream.get("width"))
    height = _safe_int(video_stream.get("height"))
    bitrate_kbps = None
    if format_section.get("bit_rate") is not None:
        bitrate_value = _safe_float(format_section.get("bit_rate"))
        if bitrate_value is not None:
            bitrate_kbps = bitrate_value / 1000.0

    result = VideoProbeResult(
        input_path=str(input_path),
        available=True,
        ffprobe_available=True,
        ffmpeg_available=ffmpeg_available,
        duration_seconds=duration_seconds,
        width=width,
        height=height,
        has_audio=bool(audio_stream),
        has_video=bool(video_stream),
        format_name=format_section.get("format_name"),
        video_codec=video_stream.get("codec_name"),
        audio_codec=audio_stream.get("codec_name"),
        frame_rate=_parse_fraction(video_stream.get("r_frame_rate")),
        bitrate_kbps=bitrate_kbps,
        stream_count=len(streams),
        raw_metadata=payload,
        warnings=warnings,
        errors=errors,
    )
    if duration_seconds <= 0:
        result.warnings.append("Probe completed but duration could not be determined.")
        result.available = False
    return result
