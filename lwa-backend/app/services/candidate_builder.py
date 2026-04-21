from __future__ import annotations

from typing import Any, Dict, List

from .clip_intelligence import build_category, build_reason, score_clip


def build_candidate_clips(
    speech_regions: List[Dict],
    *,
    min_clip_duration: float = 12.0,
    max_clip_duration: float = 45.0,
    max_candidates: int = 20,
) -> List[Dict[str, Any]]:
    candidates: List[Dict[str, Any]] = []

    for region in speech_regions:
        region_start = float(region.get("start_time", 0.0))
        region_end = float(region.get("end_time", region_start))
        region_duration = max(region_end - region_start, 0.0)
        if region_duration < min_clip_duration:
            continue

        window_start = region_start
        while window_start < region_end and len(candidates) < max_candidates:
            window_end = min(region_end, window_start + max_clip_duration)
            duration = window_end - window_start
            if duration >= min_clip_duration:
                clip = {
                    "id": f"clip_{len(candidates) + 1:03d}",
                    "start_time": round(window_start, 2),
                    "end_time": round(window_end, 2),
                    "duration": round(duration, 2),
                    "status": "detected",
                    "render_status": "pending",
                    "transcript_excerpt": region.get("transcript_excerpt"),
                    "transcript": region.get("transcript_excerpt"),
                }
                clip["category"] = build_category(clip)
                clip["reason"] = build_reason(clip)
                clip["score"] = score_clip(clip)
                clip["confidence_score"] = clip["score"]
                candidates.append(clip)

            if region_end - window_end < min_clip_duration:
                break
            window_start = window_end - min(max_clip_duration * 0.18, 6.0)

    return sorted(candidates, key=lambda item: float(item.get("score") or 0), reverse=True)[:max_candidates]


def candidates_to_segment_plan(candidates: List[Dict[str, Any]]) -> List[dict[str, float]]:
    return [
        {
            "start": float(candidate["start_time"]),
            "duration": float(candidate["duration"]),
            "format": "Speech Tight Cut",
            "transcript_excerpt": candidate.get("transcript_excerpt"),
        }
        for candidate in candidates
    ]
