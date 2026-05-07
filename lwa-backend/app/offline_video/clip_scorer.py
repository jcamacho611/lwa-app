from __future__ import annotations

from typing import Sequence

from .models import AudioWindow, CaptionSegment, ClipScore, MomentCandidate, VideoProbeResult


def _clamp(value: float, minimum: float = 0.0, maximum: float = 100.0) -> float:
    return max(minimum, min(maximum, value))


def _aspect_ratio_score(probe: VideoProbeResult) -> tuple[float, str]:
    if not probe.width or not probe.height:
        return 72.0, "unknown aspect ratio; using neutral compatibility"
    ratio = probe.width / max(probe.height, 1)
    if 0.52 <= ratio <= 0.68:
        return 100.0, "portrait framing is platform-friendly"
    if 0.8 <= ratio <= 1.2:
        return 86.0, "square-ish framing is acceptable"
    if ratio > 1.2:
        return 74.0, "landscape source may need crop awareness"
    return 80.0, "non-standard aspect ratio"


def _hook_position_score(candidate: MomentCandidate) -> tuple[float, str]:
    if candidate.start_seconds <= 0.5 and candidate.target_duration_seconds > 15:
        return 68.0, "clip starts at the source intro"
    if candidate.start_seconds <= 5.0:
        return 92.0, "clip enters quickly without feeling abrupt"
    if candidate.start_seconds <= 30.0:
        return 96.0, "clip starts after a short setup"
    if candidate.start_seconds <= 60.0:
        return 84.0, "clip starts later in the source with a strong hook"
    return 70.0, "clip starts late and may need stronger context"


def _caption_score(captions: Sequence[CaptionSegment]) -> tuple[float, str]:
    if not captions:
        return 55.0, "captions unavailable"
    if captions[0].placeholder or not captions[0].transcript_available:
        return 58.0, "captions are placeholder text"
    return 100.0, "captions are transcript-backed"


def score_candidate(
    candidate: MomentCandidate,
    probe: VideoProbeResult,
    audio: Sequence[AudioWindow],
    captions: Sequence[CaptionSegment],
) -> ClipScore:
    actual_duration = max(candidate.end_seconds - candidate.start_seconds, 0.0)
    target_duration = max(candidate.target_duration_seconds, 1.0)
    duration_delta = abs(actual_duration - target_duration)
    duration_fit = _clamp(100.0 - (duration_delta / target_duration) * 90.0)

    silence_fit = _clamp(100.0 - candidate.silence_ratio * 125.0)
    movement_fit = _clamp(candidate.visual_movement_proxy * 100.0)
    platform_fit, platform_reason = _aspect_ratio_score(probe)
    hook_fit, hook_reason = _hook_position_score(candidate)
    caption_fit, caption_reason = _caption_score(captions)

    if audio:
        matching_windows = [
            window for window in audio if window.start_seconds <= candidate.end_seconds and window.end_seconds >= candidate.start_seconds
        ]
    else:
        matching_windows = []

    audio_bonus = 0.0
    if matching_windows:
        avg_energy = sum(window.average_energy for window in matching_windows) / len(matching_windows)
        audio_bonus = _clamp(avg_energy * 20.0, 0.0, 20.0)

    total_score = (
        duration_fit * 0.20
        + silence_fit * 0.25
        + movement_fit * 0.20
        + platform_fit * 0.15
        + hook_fit * 0.10
        + caption_fit * 0.10
        + audio_bonus * 0.05
    )

    reasons = [
        f"Duration fit {duration_fit:.0f}/100 against target {target_duration:.0f}s.",
        f"Silence risk fit {silence_fit:.0f}/100 from silence ratio {candidate.silence_ratio:.2f}.",
        f"Visual movement proxy {movement_fit:.0f}/100 from {len(candidate.scene_indices)} scene span(s).",
        f"Platform fit {platform_fit:.0f}/100 because {platform_reason}.",
        f"Hook position fit {hook_fit:.0f}/100 because {hook_reason}.",
        f"Caption readiness fit {caption_fit:.0f}/100 because {caption_reason}.",
    ]
    warnings: list[str] = list(candidate.warnings)
    if candidate.silence_ratio > 0.35:
        warnings.append("high_silence_risk")
    if not captions or captions[0].placeholder:
        warnings.append("captions_placeholder")
    if candidate.start_seconds <= 0.5:
        warnings.append("starts_at_intro")

    breakdown = {
        "duration_fit": round(duration_fit, 2),
        "silence_fit": round(silence_fit, 2),
        "visual_movement": round(movement_fit, 2),
        "platform_fit": round(platform_fit, 2),
        "hook_fit": round(hook_fit, 2),
        "caption_fit": round(caption_fit, 2),
        "audio_bonus": round(audio_bonus, 2),
    }

    render_ready = total_score >= 70.0 and caption_fit >= 58.0 and silence_fit >= 55.0

    return ClipScore(
        candidate_id=candidate.candidate_id,
        total_score=round(total_score, 2),
        score_breakdown=breakdown,
        reasons=reasons,
        warnings=warnings,
        render_ready=render_ready,
    )


def rank_scored_candidates(scores: Sequence[ClipScore]) -> list[ClipScore]:
    ranked = sorted(scores, key=lambda score: (-score.total_score, score.candidate_id))
    for index, score in enumerate(ranked, start=1):
        score.rank = index
        score.post_rank = index
        score.is_best_clip = index == 1 and score.total_score >= 70.0
    return list(ranked)
