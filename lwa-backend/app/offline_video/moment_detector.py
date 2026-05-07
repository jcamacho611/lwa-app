from __future__ import annotations

from typing import Iterable

from .models import AudioWindow, MomentCandidate, SceneBoundary, VideoProbeResult


def _unique_sorted(values: Iterable[float]) -> list[float]:
    return sorted(set(round(value, 3) for value in values if value >= 0))


def _overlap(start_a: float, end_a: float, start_b: float, end_b: float) -> float:
    return max(0.0, min(end_a, end_b) - max(start_a, start_b))


def _scene_overlaps(candidate_start: float, candidate_end: float, scenes: list[SceneBoundary]) -> list[int]:
    return [
        index
        for index, boundary in enumerate(scenes)
        if _overlap(candidate_start, candidate_end, boundary.start_seconds, boundary.end_seconds) > 0
    ]


def _audio_overlaps(candidate_start: float, candidate_end: float, windows: list[AudioWindow]) -> tuple[list[int], float]:
    indices: list[int] = []
    total_silence = 0.0
    for index, window in enumerate(windows):
        overlap_seconds = _overlap(candidate_start, candidate_end, window.start_seconds, window.end_seconds)
        if overlap_seconds <= 0:
            continue
        indices.append(index)
        total_silence += overlap_seconds * window.silence_ratio
    duration = max(candidate_end - candidate_start, 1e-6)
    return indices, min(1.0, max(0.0, total_silence / duration))


def _movement_proxy(scene_indices: list[int], candidate_start: float, candidate_end: float, duration_seconds: float) -> float:
    span_factor = min(1.0, len(scene_indices) / 3.0)
    intro_bonus = 0.15 if candidate_start > 0 else 0.0
    ending_bonus = 0.1 if candidate_end < duration_seconds else 0.0
    duration_bonus = 0.1 if 12.0 <= (candidate_end - candidate_start) <= 45.0 else 0.0
    return min(1.0, 0.25 + span_factor * 0.55 + intro_bonus + ending_bonus + duration_bonus)


def generate_moment_candidates(
    probe: VideoProbeResult,
    scenes: list[SceneBoundary],
    audio: list[AudioWindow],
    *,
    target_durations: tuple[int, ...] = (15, 30, 45, 60),
) -> list[MomentCandidate]:
    duration_seconds = max(0.0, probe.duration_seconds)
    if duration_seconds <= 0:
        return [
            MomentCandidate(
                candidate_id="candidate_000",
                start_seconds=0.0,
                end_seconds=0.0,
                target_duration_seconds=float(target_durations[0] if target_durations else 15),
                selection_notes=["empty_source"],
                warnings=["source_duration_unavailable"],
            )
        ]

    scene_starts = _unique_sorted(
        boundary.start_seconds
        for boundary in scenes
        if 0.0 < boundary.start_seconds < duration_seconds
    )
    audio_starts = _unique_sorted(
        window.start_seconds
        for window in audio
        if window.start_seconds > 0.0 and window.silence_ratio <= 0.55
    )

    candidates: list[MomentCandidate] = []
    seen_windows: set[tuple[float, float, int]] = set()
    candidate_counter = 0

    for target in target_durations:
        start_candidates: set[float] = set()
        if duration_seconds <= target:
            start_candidates.add(0.0)
        else:
            start_candidates.update(scene_starts)
            start_candidates.update(audio_starts)
            start_candidates.add(max(0.0, duration_seconds - float(target)))
            start_candidates.add(min(max(5.0, float(target) * 0.5), max(0.0, duration_seconds - float(target))))
            start_candidates.add(min(max(10.0, float(target) * 0.25), max(0.0, duration_seconds - float(target))))
            start_candidates.add(min(max(0.0, float(target) * 0.75), max(0.0, duration_seconds - float(target))))
            if not start_candidates:
                start_candidates.add(0.0)

        sorted_starts = sorted(start_candidates)
        if duration_seconds > target and 0.0 in sorted_starts and len(sorted_starts) > 1:
            sorted_starts = [value for value in sorted_starts if value > 0.0] or sorted_starts

        for start_seconds in sorted_starts[:8]:
            end_seconds = min(duration_seconds, start_seconds + float(target))
            if end_seconds - start_seconds <= 0.5:
                continue
            key = (round(start_seconds, 3), round(end_seconds, 3), int(target))
            if key in seen_windows:
                continue
            seen_windows.add(key)
            scene_indices = _scene_overlaps(start_seconds, end_seconds, scenes)
            audio_indices, silence_ratio = _audio_overlaps(start_seconds, end_seconds, audio)
            movement_proxy = _movement_proxy(scene_indices, start_seconds, end_seconds, duration_seconds)
            transcript_available = False
            selection_notes = []
            warnings = []

            if start_seconds > 0.0:
                selection_notes.append("starts_after_intro")
            else:
                warnings.append("starts_at_intro")
            if silence_ratio <= 0.25:
                selection_notes.append("low_silence_window")
            elif silence_ratio > 0.6:
                warnings.append("high_silence_risk")
            if len(scene_indices) > 1:
                selection_notes.append("crosses_scene_boundary")
            if end_seconds >= duration_seconds:
                selection_notes.append("uses_source_tail")

            caption_readiness = 0.0
            platform_fit = 0.0
            candidate_counter += 1
            candidates.append(
                MomentCandidate(
                    candidate_id=f"candidate_{candidate_counter:03d}",
                    start_seconds=round(start_seconds, 3),
                    end_seconds=round(end_seconds, 3),
                    target_duration_seconds=float(target),
                    scene_indices=scene_indices,
                    audio_window_indices=audio_indices,
                    silence_ratio=round(silence_ratio, 3),
                    visual_movement_proxy=round(movement_proxy, 3),
                    hook_position_seconds=round(start_seconds, 3),
                    caption_readiness=caption_readiness,
                    platform_fit=platform_fit,
                    transcript_available=transcript_available,
                    selection_notes=selection_notes,
                    warnings=warnings,
                )
            )

    if not candidates:
        fallback_end = min(duration_seconds, float(target_durations[0] if target_durations else 15))
        candidates.append(
            MomentCandidate(
                candidate_id="candidate_001",
                start_seconds=0.0,
                end_seconds=round(fallback_end, 3),
                target_duration_seconds=float(target_durations[0] if target_durations else 15),
                selection_notes=["fallback_candidate"],
                warnings=["no_scene_candidates_generated"],
            )
        )

    return candidates
