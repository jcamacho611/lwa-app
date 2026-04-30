from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class FallbackClipResult:
    status: str
    reason: str
    clips: list[dict[str, Any]]
    fallback_used: bool = True


def transcript_fallback(*, duration_seconds: int | float | None, window_seconds: int = 30) -> list[dict[str, Any]]:
    duration = max(int(duration_seconds or window_seconds), window_seconds)
    windows: list[dict[str, Any]] = []
    start = 0
    index = 1
    while start < duration:
        end = min(start + window_seconds, duration)
        windows.append(
            {
                "index": index,
                "start": start,
                "end": end,
                "text": f"Segment {index}",
            }
        )
        start = end
        index += 1
    return windows


def moment_fallback(*, duration_seconds: int | float | None, count: int = 3, window_seconds: int = 30) -> list[dict[str, Any]]:
    duration = max(int(duration_seconds or window_seconds * count), window_seconds)
    if count <= 1:
        starts = [0]
    else:
        max_start = max(duration - window_seconds, 0)
        starts = [round((max_start * idx) / (count - 1)) for idx in range(count)]

    return [
        {
            "index": idx + 1,
            "start": int(start),
            "end": int(min(start + window_seconds, duration)),
            "reason": "Evenly spaced fallback moment",
        }
        for idx, start in enumerate(starts)
    ]


def caption_fallback(transcript_text: str | None) -> str:
    text = (transcript_text or "").strip()
    return text or "Segment ready for review."


def hook_fallback(segment_text: str | None, *, max_words: int = 7) -> str:
    words = (segment_text or "Segment ready for review").strip().split()
    return " ".join(words[:max_words])


def build_fallback_clip_result(*, reason: str, duration_seconds: int | float | None = None) -> FallbackClipResult:
    transcript_segments = transcript_fallback(duration_seconds=duration_seconds)
    moments = moment_fallback(duration_seconds=duration_seconds)
    clips = []
    for moment in moments:
        segment = transcript_segments[min(moment["index"] - 1, len(transcript_segments) - 1)]
        text = str(segment.get("text") or "")
        clips.append(
            {
                "title": hook_fallback(text),
                "hook": hook_fallback(text),
                "caption": caption_fallback(text),
                "start": moment["start"],
                "end": moment["end"],
                "score": 50,
                "status": "degraded",
                "reason": moment["reason"],
            }
        )
    return FallbackClipResult(status="degraded", reason=reason, clips=clips)
