from __future__ import annotations

import logging
from pathlib import Path
from urllib.parse import quote

from ..core.config import Settings
from ..processor import (
    cut_clip,
    create_preview_image_url,
    download_source,
    ensure_clip_output,
    flatten_transcript_windows,
    load_transcript_windows,
    locate_source_file,
    probe_video_duration,
    resolve_ffmpeg_path,
)
from .candidate_builder import build_candidate_clips
from .clip_analysis_store import (
    get_candidate_clip,
    get_video,
    list_video_clips,
    replace_audio_regions,
    replace_candidate_clips,
    replace_transcript_segments,
    update_candidate_clip_media,
    update_video_record,
)
from .render_jobs import run_background
from .silence_detector import detect_silence_regions
from .speech_regions import invert_silence_to_speech

logger = logging.getLogger("uvicorn.error")


def transcript_window_payloads(windows) -> list[dict[str, object]]:
    return [
        {
            "start_time": float(window.start_seconds),
            "end_time": float(window.end_seconds),
            "text": window.excerpt,
            "confidence": None,
        }
        for window in windows
    ]


def attach_transcripts_to_speech_regions(speech_regions: list[dict], transcript_windows) -> list[dict]:
    if not transcript_windows:
        return speech_regions

    enriched = []
    for region in speech_regions:
        start = float(region["start_time"])
        end = float(region["end_time"])
        excerpts = [
            window.excerpt
            for window in transcript_windows
            if float(window.end_seconds) > start and float(window.start_seconds) < end
        ]
        payload = dict(region)
        if excerpts:
            payload["transcript_excerpt"] = " ".join(excerpts).strip()[:800]
        enriched.append(payload)
    return enriched


def run_video_analysis(
    *,
    settings: Settings,
    video_id: str,
    video_url: str,
    target_platform: str | None,
    mode: str | None,
) -> None:
    ffmpeg_path = resolve_ffmpeg_path(settings)
    if not ffmpeg_path:
        update_video_record(settings=settings, video_id=video_id, status="failed", error="ffmpeg unavailable")
        return

    analysis_dir = Path(settings.generated_assets_dir) / "analysis" / video_id
    analysis_dir.mkdir(parents=True, exist_ok=True)

    try:
        info = download_source(video_url=video_url, work_dir=analysis_dir, ffmpeg_path=ffmpeg_path, request_id=video_id)
        source_file = locate_source_file(analysis_dir)
        duration_seconds = probe_video_duration(source_file=source_file, ffmpeg_path=ffmpeg_path)
        if duration_seconds is None:
            duration_seconds = float(info.get("duration") or 0) or None
        if not duration_seconds:
            raise RuntimeError("source duration unavailable")

        transcript_windows = load_transcript_windows(analysis_dir)
        transcript_text = flatten_transcript_windows(transcript_windows)
        silence_regions = detect_silence_regions(str(source_file), ffmpeg_path=ffmpeg_path)
        speech_regions = invert_silence_to_speech(silence_regions, float(duration_seconds))
        speech_regions = attach_transcripts_to_speech_regions(speech_regions, transcript_windows)
        candidates = build_candidate_clips(speech_regions, max_candidates=24)

        replace_transcript_segments(
            settings=settings,
            video_id=video_id,
            segments=transcript_window_payloads(transcript_windows),
        )
        replace_audio_regions(
            settings=settings,
            video_id=video_id,
            regions=[*silence_regions, *speech_regions],
        )
        replace_candidate_clips(settings=settings, video_id=video_id, clips=candidates)
        update_video_record(
            settings=settings,
            video_id=video_id,
            status="ready",
            local_path=str(source_file),
            title=str(info.get("title") or "Untitled source"),
            duration_seconds=float(duration_seconds),
            error=None if transcript_text or candidates else "analysis completed without transcript text",
        )
    except Exception as error:
        logger.warning("video_analysis_failed video_id=%s reason=%s", video_id, error)
        update_video_record(settings=settings, video_id=video_id, status="failed", error=str(error))


def render_analysis_clip(
    *,
    settings: Settings,
    clip_id: str,
    public_base_url: str,
) -> dict[str, object]:
    clip = get_candidate_clip(settings=settings, clip_id=clip_id)
    if not clip:
        raise ValueError("Clip not found")
    video = get_video(settings=settings, video_id=str(clip["video_id"]))
    if not video:
        raise ValueError("Video not found")
    local_path = video.get("local_path")
    if not local_path:
        raise ValueError("Video source not ready")

    ffmpeg_path = resolve_ffmpeg_path(settings)
    if not ffmpeg_path:
        raise RuntimeError("ffmpeg unavailable")

    output_dir = Path(settings.generated_assets_dir) / "analysis" / str(clip["video_id"])
    output_dir.mkdir(parents=True, exist_ok=True)
    output_name = f"{clip_id}_preview.mp4"
    output_path = output_dir / output_name
    start = float(clip["start_time"])
    duration = max(float(clip["end_time"]) - start, 1.0)

    cut_clip(
        ffmpeg_path=ffmpeg_path,
        source_file=Path(str(local_path)),
        output_path=output_path,
        start=start,
        duration=duration,
    )
    ensure_clip_output(output_path)
    preview_url = f"{public_base_url}/generated/analysis/{clip['video_id']}/{quote(output_name)}"

    preview_image_name = f"{clip_id}_preview.jpg"
    preview_image_url = create_preview_image_url(
        ffmpeg_path=ffmpeg_path,
        input_path=output_path,
        output_path=output_dir / preview_image_name,
        public_base_url=public_base_url,
        request_id=f"analysis/{clip['video_id']}",
        public_name=preview_image_name,
    )
    update_candidate_clip_media(
        settings=settings,
        clip_id=clip_id,
        render_status="ready",
        preview_url=preview_url,
        clip_url=preview_url,
        thumbnail_url=preview_image_url,
    )
    updated = get_candidate_clip(settings=settings, clip_id=clip_id)
    return updated or {"id": clip_id, "preview_url": preview_url, "render_status": "ready"}


def queue_analysis_clip_render(
    *,
    settings: Settings,
    clip_id: str,
    public_base_url: str,
) -> None:
    update_candidate_clip_media(settings=settings, clip_id=clip_id, render_status="rendering")

    def job() -> None:
        try:
            render_analysis_clip(settings=settings, clip_id=clip_id, public_base_url=public_base_url)
        except Exception as error:
            logger.warning("analysis_clip_render_failed clip_id=%s reason=%s", clip_id, error)
            update_candidate_clip_media(settings=settings, clip_id=clip_id, render_status="failed")

    run_background(job)


def video_analysis_summary(*, settings: Settings, video_id: str) -> dict[str, object] | None:
    return get_video(settings=settings, video_id=video_id)


def video_candidate_clips(*, settings: Settings, video_id: str) -> list[dict[str, object]]:
    return list_video_clips(settings=settings, video_id=video_id)
