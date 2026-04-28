from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from ..core.config import Settings

PLATFORM_CAPTION_PREFERENCES: dict[str, tuple[str, ...]] = {
    "tiktok": ("short", "primary", "controversial", "story"),
    "instagram": ("story", "primary", "educational", "short"),
    "instagram_reels": ("story", "primary", "educational", "short"),
    "youtube": ("educational", "primary", "story", "short"),
    "youtube_shorts": ("educational", "primary", "story", "short"),
    "facebook": ("story", "primary", "educational", "short"),
    "facebook_reels": ("story", "primary", "educational", "short"),
    "x": ("controversial", "short", "primary", "story"),
    "twitter": ("controversial", "short", "primary", "story"),
    "linkedin": ("educational", "story", "primary", "short"),
    "whop": ("educational", "primary", "story", "short"),
    "community": ("educational", "primary", "story", "short"),
}


def _model_value(payload: Any, key: str) -> Any:
    if isinstance(payload, dict):
        return payload.get(key)
    return getattr(payload, key, None)


def _caption_mode_value(caption_modes: Any, key: str) -> str:
    if isinstance(caption_modes, dict):
        return str(caption_modes.get(key) or "").strip()
    return str(getattr(caption_modes, key, "") or "").strip()


def _safe_name(value: str, *, max_length: int = 80) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", str(value or "").strip().lower())
    cleaned = normalized.strip("-")
    return cleaned[:max_length] or "clip"


def _platform_slug(target_platform: str | None) -> str:
    normalized = _safe_name(target_platform or "short-form", max_length=32)
    if normalized in {"youtube-shorts", "youtube"}:
        return "youtube"
    if normalized in {"instagram-reels", "instagram"}:
        return "instagram"
    if normalized in {"facebook-reels", "facebook"}:
        return "facebook"
    return normalized or "short-form"


def _public_generated_url(*, settings: Settings, public_base_url: str, path: Path) -> str:
    generated_dir = Path(settings.generated_assets_dir).resolve()
    try:
        relative = path.resolve().relative_to(generated_dir)
    except ValueError:
        relative = Path(path.name)
    public_path = f"/generated/{relative.as_posix()}"
    base = (public_base_url or settings.api_base_url or "").rstrip("/")
    return f"{base}{public_path}" if base else public_path


def _coalesce_text(*values: object) -> str:
    for value in values:
        text = str(value or "").strip()
        if text:
            return text
    return ""


def _parse_timestamp(value: object) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value or "").strip()
    if not text:
        return 0.0
    parts = text.split(":")
    try:
        values = [float(part) for part in parts]
    except ValueError:
        return 0.0
    if len(values) == 2:
        return (values[0] * 60.0) + values[1]
    if len(values) == 3:
        return (values[0] * 3600.0) + (values[1] * 60.0) + values[2]
    return 0.0


def derive_duration_seconds(clip: Any) -> float:
    start = _parse_timestamp(_model_value(clip, "timestamp_start") or _model_value(clip, "start_time"))
    end = _parse_timestamp(_model_value(clip, "timestamp_end") or _model_value(clip, "end_time"))
    if end > start:
        return max(end - start, 1.0)
    explicit = _model_value(clip, "duration")
    if isinstance(explicit, (int, float)) and explicit > 0:
        return float(explicit)
    return 6.0


def subtitle_source_text(clip: Any) -> str:
    return _coalesce_text(
        _model_value(clip, "transcript_excerpt"),
        _model_value(clip, "transcript"),
        _model_value(clip, "caption"),
        _model_value(clip, "hook"),
        _model_value(clip, "title"),
    )


def select_platform_caption_text(*, clip: Any, target_platform: str | None) -> str:
    caption_modes = _model_value(clip, "caption_modes") or {}
    caption_variants = _model_value(clip, "caption_variants") or {}
    slug = _platform_slug(target_platform)
    preferences = PLATFORM_CAPTION_PREFERENCES.get(slug, ("primary", "short", "story", "educational", "controversial"))

    for key in preferences:
        mode_value = _caption_mode_value(caption_modes, key)
        if mode_value:
            return mode_value
        variant_value = str(caption_variants.get(key) or "").strip() if isinstance(caption_variants, dict) else ""
        if variant_value:
            return variant_value

    return _coalesce_text(
        _model_value(clip, "caption"),
        _model_value(clip, "hook"),
        _model_value(clip, "title"),
    )


def _subtitle_segments(text: str) -> list[str]:
    words = text.split()
    if not words:
        return []
    segments: list[str] = []
    step = 6
    for index in range(0, len(words), step):
        segments.append(" ".join(words[index : index + step]))
    return segments[:8]


def _format_srt_timestamp(seconds: float) -> str:
    total_ms = max(int(round(seconds * 1000)), 0)
    hours, remainder = divmod(total_ms, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    whole_seconds, milliseconds = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{whole_seconds:02d},{milliseconds:03d}"


def _format_vtt_timestamp(seconds: float) -> str:
    total_ms = max(int(round(seconds * 1000)), 0)
    hours, remainder = divmod(total_ms, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    whole_seconds, milliseconds = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{whole_seconds:02d}.{milliseconds:03d}"


def build_subtitle_content(text: str, duration_seconds: float, *, format_name: str) -> str:
    segments = _subtitle_segments(text)
    if not segments:
        return "WEBVTT\n" if format_name == "vtt" else ""

    cue_duration = max(duration_seconds / len(segments), 0.9)
    lines: list[str] = ["WEBVTT", ""] if format_name == "vtt" else []
    current_start = 0.0
    for index, segment in enumerate(segments, start=1):
        current_end = duration_seconds if index == len(segments) else min(current_start + cue_duration, duration_seconds)
        if format_name == "vtt":
            lines.extend(
                [
                    f"{_format_vtt_timestamp(current_start)} --> {_format_vtt_timestamp(current_end)}",
                    segment,
                    "",
                ]
            )
        else:
            lines.extend(
                [
                    str(index),
                    f"{_format_srt_timestamp(current_start)} --> {_format_srt_timestamp(current_end)}",
                    segment,
                    "",
                ]
            )
        current_start = current_end
    return "\n".join(lines).strip() + "\n"


def create_caption_artifacts(
    *,
    settings: Settings,
    public_base_url: str,
    request_id: str,
    clip: Any,
    target_platform: str | None,
) -> dict[str, str | None]:
    clip_id = _safe_name(str(_model_value(clip, "id") or "clip"))
    title_seed = _coalesce_text(_model_value(clip, "title"), _model_value(clip, "hook"), clip_id)
    platform_slug = _platform_slug(target_platform)
    base_name = f"{_safe_name(title_seed, max_length=56)}-{platform_slug}"
    artifact_dir = Path(settings.generated_assets_dir) / request_id / "captions" / clip_id
    artifact_dir.mkdir(parents=True, exist_ok=True)

    caption_text = select_platform_caption_text(clip=clip, target_platform=target_platform)
    subtitle_text = subtitle_source_text(clip) or caption_text
    duration_seconds = derive_duration_seconds(clip)

    caption_txt_path = artifact_dir / f"{base_name}.txt"
    caption_srt_path = artifact_dir / f"{base_name}.srt"
    caption_vtt_path = artifact_dir / f"{base_name}.vtt"

    caption_txt_path.write_text(caption_text + "\n", encoding="utf-8")
    caption_srt_path.write_text(
        build_subtitle_content(subtitle_text, duration_seconds, format_name="srt"),
        encoding="utf-8",
    )
    caption_vtt_path.write_text(
        build_subtitle_content(subtitle_text, duration_seconds, format_name="vtt"),
        encoding="utf-8",
    )

    burned_caption_url = _coalesce_text(
        _model_value(clip, "edited_clip_url"),
        _model_value(clip, "preview_url"),
        _model_value(clip, "clip_url"),
        _model_value(clip, "raw_clip_url"),
    ) or None

    return {
        "caption_txt_url": _public_generated_url(
            settings=settings,
            public_base_url=public_base_url,
            path=caption_txt_path,
        ),
        "caption_srt_url": _public_generated_url(
            settings=settings,
            public_base_url=public_base_url,
            path=caption_srt_path,
        ),
        "caption_vtt_url": _public_generated_url(
            settings=settings,
            public_base_url=public_base_url,
            path=caption_vtt_path,
        ),
        "burned_caption_url": burned_caption_url,
        "export_filename": f"{base_name}.mp4",
    }
