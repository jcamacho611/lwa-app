from __future__ import annotations

import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from ..core.config import Settings

DEFAULT_ARTIFACT_TYPES = ["package_json", "caption_txt", "subtitle_srt", "subtitle_vtt"]


def _safe_name(value: str) -> str:
    normalized = "".join(character.lower() if character.isalnum() else "-" for character in value)
    normalized = "-".join(part for part in normalized.split("-") if part)
    return normalized[:72] or "clip-pack"


def _safe_clip_id(value: str) -> str:
    cleaned = "".join(character if character.isalnum() or character in {"_", "-"} else "_" for character in value)
    return cleaned[:80] or "clip"


def _public_generated_url(*, settings: Settings, public_base_url: str, path: Path) -> str:
    generated_dir = Path(settings.generated_assets_dir).resolve()
    try:
        relative = path.resolve().relative_to(generated_dir)
    except ValueError:
        relative = Path(path.name)
    public_path = f"/generated/{relative.as_posix()}"
    base = (public_base_url or settings.api_base_url or "").rstrip("/")
    return f"{base}{public_path}" if base else public_path


def _local_asset_path(value: object) -> Path | None:
    if not isinstance(value, str) or not value.strip():
        return None
    candidate = value.strip()
    if candidate.startswith(("http://", "https://", "/generated/", "/uploads/")):
        return None
    path = Path(candidate)
    return path if path.exists() and path.is_file() else None


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
        numbers = [float(part) for part in parts]
    except ValueError:
        return 0.0
    if len(numbers) == 2:
        return (numbers[0] * 60.0) + numbers[1]
    if len(numbers) == 3:
        return (numbers[0] * 3600.0) + (numbers[1] * 60.0) + numbers[2]
    return 0.0


def _derive_duration_seconds(clip: dict[str, Any]) -> float:
    start = _parse_timestamp(clip.get("timestamp_start") or clip.get("start_time"))
    end = _parse_timestamp(clip.get("timestamp_end") or clip.get("end_time"))
    if end > start:
        return max(end - start, 1.0)
    explicit = clip.get("duration")
    if isinstance(explicit, (int, float)) and explicit > 0:
        return float(explicit)
    return 6.0


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


def _build_subtitle_content(text: str, duration_seconds: float, *, format_name: str) -> str:
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


def _build_clip_package(clip: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": clip.get("id"),
        "title": clip.get("title"),
        "hook": clip.get("hook"),
        "caption": clip.get("caption"),
        "cta": clip.get("cta") or clip.get("cta_suggestion"),
        "thumbnail_text": clip.get("thumbnail_text"),
        "platform_fit": clip.get("platform_fit"),
        "packaging_angle": clip.get("packaging_angle"),
        "caption_style": clip.get("caption_style"),
        "post_rank": clip.get("post_rank"),
        "score": clip.get("score"),
        "hook_score": clip.get("hook_score"),
        "render_readiness_score": clip.get("render_readiness_score") or clip.get("render_quality_score"),
        "score_breakdown": clip.get("score_breakdown"),
        "scoring_explanation": clip.get("scoring_explanation"),
        "caption_txt_url": clip.get("caption_txt_url"),
        "caption_srt_url": clip.get("caption_srt_url"),
        "caption_vtt_url": clip.get("caption_vtt_url"),
        "burned_caption_url": clip.get("burned_caption_url"),
        "export_filename": clip.get("export_filename"),
    }


def _build_readme(*, request_id: str | None, bundle_id: str, clip_entries: list[dict[str, Any]], created_at: str) -> str:
    lines = [
        f"# Clip Bundle {bundle_id}",
        "",
        f"Generated: {created_at}",
        f"Request: {request_id or 'adhoc export'}",
        f"Total clips: {len(clip_entries)}",
        "",
        "## Included artifacts",
        "1. `manifest.json` with bundle metadata and per-clip artifact paths.",
        "2. `clips/<clip_id>/package.json` with hook, caption, CTA, scores, and packaging metadata.",
        "3. `clips/<clip_id>/caption.txt` with the post caption.",
        "4. `clips/<clip_id>/subtitle.srt` and `subtitle.vtt` built from the transcript or caption.",
        "5. `media/` assets when a local rendered file was available during export.",
        "",
    ]
    for index, clip in enumerate(clip_entries, start=1):
        lines.extend(
            [
                f"## Clip {index}",
                f"- ID: {clip.get('id', '')}",
                f"- Title: {clip.get('title', 'Untitled')}",
                f"- Score: {clip.get('score', '')}",
                f"- Post rank: {clip.get('post_rank', '')}",
                f"- Artifacts: {', '.join(sorted((clip.get('artifact_paths') or {}).keys()))}",
                "",
            ]
        )
    return "\n".join(lines)


def create_export_bundle(
    *,
    settings: Settings,
    public_base_url: str,
    source_url: str,
    clips: list[dict[str, Any]],
    request_id: str | None = None,
) -> dict[str, Any]:
    export_root = Path(settings.generated_assets_dir) / "export-bundles"
    request_root = export_root / _safe_name(request_id or "adhoc")
    request_root.mkdir(parents=True, exist_ok=True)

    bundle_id = f"bundle_{uuid4().hex[:12]}"
    created_at = datetime.now(timezone.utc).isoformat()
    title_seed = str((clips[0] or {}).get("title") or "clip-pack") if clips else "clip-pack"
    bundle_dir = request_root / bundle_id
    bundle_dir.mkdir(parents=True, exist_ok=True)

    clip_entries: list[dict[str, Any]] = []
    artifact_counts = {
        "package_json": 0,
        "caption_txt": 0,
        "subtitle_srt": 0,
        "subtitle_vtt": 0,
        "media_files": 0,
    }

    for index, clip in enumerate([clip for clip in clips if isinstance(clip, dict)], start=1):
        safe_clip_id = _safe_clip_id(str(clip.get("id") or f"clip_{index:03d}"))
        clip_dir = bundle_dir / "clips" / safe_clip_id
        clip_dir.mkdir(parents=True, exist_ok=True)

        caption_text = _coalesce_text(clip.get("caption"), clip.get("hook"), clip.get("title"))
        subtitle_text = _coalesce_text(
            clip.get("transcript_excerpt"),
            clip.get("transcript"),
            clip.get("caption"),
            clip.get("hook"),
            clip.get("title"),
        )
        duration_seconds = _derive_duration_seconds(clip)

        package_relative = f"clips/{safe_clip_id}/package.json"
        caption_relative = f"clips/{safe_clip_id}/caption.txt"
        srt_relative = f"clips/{safe_clip_id}/subtitle.srt"
        vtt_relative = f"clips/{safe_clip_id}/subtitle.vtt"

        (bundle_dir / package_relative).write_text(
            json.dumps(_build_clip_package(clip), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        (bundle_dir / caption_relative).write_text(caption_text + "\n", encoding="utf-8")
        (bundle_dir / srt_relative).write_text(
            _build_subtitle_content(subtitle_text, duration_seconds, format_name="srt"),
            encoding="utf-8",
        )
        (bundle_dir / vtt_relative).write_text(
            _build_subtitle_content(subtitle_text, duration_seconds, format_name="vtt"),
            encoding="utf-8",
        )
        artifact_counts["package_json"] += 1
        artifact_counts["caption_txt"] += 1
        artifact_counts["subtitle_srt"] += 1
        artifact_counts["subtitle_vtt"] += 1

        artifact_paths = {
            "package_json": package_relative,
            "caption_txt": caption_relative,
            "subtitle_srt": srt_relative,
            "subtitle_vtt": vtt_relative,
        }

        media_files: list[dict[str, str]] = []
        for field_name, suffix in (
            ("preview_url", "preview"),
            ("download_url", "download"),
            ("edited_clip_url", "edited"),
            ("clip_url", "clip"),
            ("raw_clip_url", "raw"),
        ):
            asset_path = _local_asset_path(clip.get(field_name))
            if not asset_path:
                continue
            relative_media_path = f"media/{safe_clip_id}_{suffix}{asset_path.suffix}"
            media_files.append({"type": suffix, "path": relative_media_path})
            artifact_counts["media_files"] += 1

        clip_entries.append(
            {
                "id": clip.get("id") or safe_clip_id,
                "title": clip.get("title") or "Untitled clip",
                "score": clip.get("score"),
                "post_rank": clip.get("post_rank"),
                "artifact_paths": artifact_paths,
                "artifact_urls": {
                    field_name: clip.get(field_name)
                    for field_name in (
                        "caption_txt_url",
                        "caption_srt_url",
                        "caption_vtt_url",
                        "burned_caption_url",
                    )
                    if clip.get(field_name)
                },
                "media_files": media_files,
                "source_asset_urls": {
                    field_name: clip.get(field_name)
                    for field_name in ("preview_url", "download_url", "edited_clip_url", "clip_url", "raw_clip_url")
                    if clip.get(field_name)
                },
            }
        )

    manifest = {
        "bundle_id": bundle_id,
        "request_id": request_id,
        "created_at": created_at,
        "source_url": source_url,
        "clip_count": len(clip_entries),
        "bundle_format": "zip",
        "artifact_types": DEFAULT_ARTIFACT_TYPES,
        "artifact_counts": artifact_counts,
        "clips": clip_entries,
    }

    manifest_path = bundle_dir / "manifest.json"
    readme_path = bundle_dir / "README.md"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    readme_path.write_text(
        _build_readme(request_id=request_id, bundle_id=bundle_id, clip_entries=clip_entries, created_at=created_at),
        encoding="utf-8",
    )

    file_name = f"{_safe_name(title_seed)}-{bundle_id[-8:]}.zip"
    bundle_path = request_root / file_name
    with zipfile.ZipFile(bundle_path, "w", zipfile.ZIP_DEFLATED) as bundle_zip:
        for bundle_file in bundle_dir.rglob("*"):
            if bundle_file.is_file():
                bundle_zip.write(bundle_file, bundle_file.relative_to(bundle_dir).as_posix())

        for clip_entry in clip_entries:
            for media_file in clip_entry["media_files"]:
                asset_key = media_file["type"]
                original_clip = next((clip for clip in clips if str(clip.get("id") or "") == str(clip_entry["id"])), None)
                if not original_clip:
                    continue
                source_field = {
                    "preview": "preview_url",
                    "download": "download_url",
                    "edited": "edited_clip_url",
                    "clip": "clip_url",
                    "raw": "raw_clip_url",
                }.get(asset_key)
                if not source_field:
                    continue
                asset_path = _local_asset_path(original_clip.get(source_field))
                if asset_path:
                    bundle_zip.write(asset_path, media_file["path"])

    return {
        "bundle_id": bundle_id,
        "download_url": _public_generated_url(settings=settings, public_base_url=public_base_url, path=bundle_path),
        "manifest_url": _public_generated_url(settings=settings, public_base_url=public_base_url, path=manifest_path),
        "file_name": file_name,
        "clip_count": len(clip_entries),
        "created_at": created_at,
        "bundle_format": "zip",
        "artifact_types": DEFAULT_ARTIFACT_TYPES,
        "artifact_counts": artifact_counts,
        "bundle_path": str(bundle_path),
        "bundle_dir": str(bundle_dir),
        "manifest_path": str(manifest_path),
        "readme_path": str(readme_path),
        "size_bytes": bundle_path.stat().st_size if bundle_path.exists() else 0,
    }
