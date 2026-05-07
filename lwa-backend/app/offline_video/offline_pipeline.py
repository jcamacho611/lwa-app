from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from .audio_analyzer import analyze_audio_windows
from .caption_engine import build_caption_segments
from .clip_scorer import rank_scored_candidates, score_candidate
from .ffmpeg_probe import check_ffmpeg_available, probe_video
from .moment_detector import generate_moment_candidates
from .models import (
    OfflineVideoPipelineOptions,
    OfflineVideoPipelineResult,
    RenderPlan,
    ThumbnailPlan,
)
from .proof_engine import build_offline_proof
from .render_engine import build_render_plan, render_clip
from .scene_detector import detect_scene_boundaries
from .thumbnail_engine import build_thumbnail_plan, generate_thumbnail


def _coerce_options(options: OfflineVideoPipelineOptions | Mapping[str, Any] | None) -> OfflineVideoPipelineOptions:
    if options is None:
        return OfflineVideoPipelineOptions()
    if isinstance(options, OfflineVideoPipelineOptions):
        return options
    payload = dict(options)
    return OfflineVideoPipelineOptions(
        render=bool(payload.get("render", False)),
        transcript=payload.get("transcript"),
        target_durations=tuple(payload.get("target_durations", (15, 30, 45, 60))),
        max_results=int(payload.get("max_results", 3)),
        generate_thumbnails=bool(payload.get("generate_thumbnails", True)),
        ffmpeg_binary=str(payload.get("ffmpeg_binary", "ffmpeg")),
        ffprobe_binary=str(payload.get("ffprobe_binary", "ffprobe")),
    )


def _validate_source_path(path: str | Path) -> Path:
    source_path = Path(path)
    if not source_path.exists():
        raise FileNotFoundError(f"Input video not found: {source_path}")
    if not source_path.is_file():
        raise ValueError(f"Input path is not a file: {source_path}")
    return source_path.resolve()


def _prepare_output_dir(path: str | Path) -> Path:
    output_dir = Path(path).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def _thumbnail_output_path(output_dir: Path, thumbnail_plan: ThumbnailPlan) -> Path:
    return output_dir / thumbnail_plan.suggested_filename


def run_offline_video_pipeline(
    input_path: str | Path,
    output_dir: str | Path,
    options: OfflineVideoPipelineOptions | Mapping[str, Any] | None = None,
) -> OfflineVideoPipelineResult:
    normalized_options = _coerce_options(options)
    source_path = _validate_source_path(input_path)
    prepared_output_dir = _prepare_output_dir(output_dir)

    ffmpeg_available = check_ffmpeg_available(
        ffmpeg_binary=normalized_options.ffmpeg_binary,
        ffprobe_binary=normalized_options.ffprobe_binary,
    )
    probe = probe_video(
        source_path,
        ffmpeg_binary=normalized_options.ffmpeg_binary,
        ffprobe_binary=normalized_options.ffprobe_binary,
    )
    scene_boundaries = detect_scene_boundaries(
        source_path,
        probe,
        ffmpeg_binary=normalized_options.ffmpeg_binary,
    )
    audio_windows = analyze_audio_windows(
        source_path,
        probe,
        ffmpeg_binary=normalized_options.ffmpeg_binary,
    )
    candidates = generate_moment_candidates(
        probe,
        scene_boundaries,
        audio_windows,
        target_durations=normalized_options.target_durations,
    )

    clip_scores = []
    captions_by_candidate: dict[str, list] = {}
    for candidate in candidates:
        captions = build_caption_segments(candidate, transcript=normalized_options.transcript)
        captions_by_candidate[candidate.candidate_id] = captions
        clip_scores.append(score_candidate(candidate, probe, audio_windows, captions))

    ranked_scores = rank_scored_candidates(clip_scores)
    selected_candidates = ranked_scores[: max(0, normalized_options.max_results)]

    render_plans: list[RenderPlan] = []
    render_outputs: list[dict[str, Any]] = []
    if normalized_options.render and ffmpeg_available:
        for score in selected_candidates:
            candidate = next((item for item in candidates if item.candidate_id == score.candidate_id), None)
            if candidate is None:
                continue
            render_plan = build_render_plan(candidate, prepared_output_dir)
            render_plan = RenderPlan(
                candidate_id=render_plan.candidate_id,
                source_path=str(source_path),
                output_dir=render_plan.output_dir,
                output_path=render_plan.output_path,
                thumbnail_path=render_plan.thumbnail_path,
                start_seconds=render_plan.start_seconds,
                end_seconds=render_plan.end_seconds,
                target_duration_seconds=render_plan.target_duration_seconds,
                crop_mode=render_plan.crop_mode,
                container_format=render_plan.container_format,
            )
            render_plans.append(render_plan)
            render_result = render_clip(source_path, render_plan, ffmpeg_binary=normalized_options.ffmpeg_binary)
            thumbnail_result: dict[str, Any] | None = None
            if normalized_options.generate_thumbnails:
                thumbnail_plan = build_thumbnail_plan(candidate)
                thumbnail_output_path = _thumbnail_output_path(prepared_output_dir, thumbnail_plan)
                thumbnail_result = generate_thumbnail(
                    source_path,
                    thumbnail_output_path,
                    thumbnail_plan.timestamp_seconds,
                    ffmpeg_binary=normalized_options.ffmpeg_binary,
                )
            render_outputs.append(
                {
                    "candidate_id": score.candidate_id,
                    "render": render_result,
                    "thumbnail": thumbnail_result,
                }
            )

    warnings: list[str] = []
    if not ffmpeg_available:
        warnings.append("ffmpeg_unavailable")
    if not probe.available:
        warnings.extend(probe.warnings)

    result = OfflineVideoPipelineResult(
        source_path=str(source_path),
        output_dir=str(prepared_output_dir),
        probe=probe,
        scene_boundaries=scene_boundaries,
        audio_windows=audio_windows,
        candidates=candidates,
        scored_candidates=ranked_scores,
        selected_candidates=selected_candidates,
        render_plans=render_plans,
        render_outputs=render_outputs,
        warnings=warnings,
        render_requested=normalized_options.render,
        ffmpeg_available=ffmpeg_available,
        success=True,
    )
    result.proof = build_offline_proof(result)
    return result
