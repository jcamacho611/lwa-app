from __future__ import annotations

import re

from .models import CaptionSegment, MomentCandidate

_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


def _chunk_words(text: str, max_chunks: int) -> list[str]:
    words = [word for word in text.split() if word]
    if not words:
        return []
    chunk_size = max(1, round(len(words) / max_chunks))
    chunks: list[str] = []
    for index in range(0, len(words), chunk_size):
        chunks.append(" ".join(words[index : index + chunk_size]).strip())
    return [chunk for chunk in chunks if chunk]


def build_caption_segments(candidate: MomentCandidate, transcript: str | None = None) -> list[CaptionSegment]:
    duration = max(candidate.end_seconds - candidate.start_seconds, 0.0)
    if not transcript or not transcript.strip():
        return [
            CaptionSegment(
                start_seconds=round(candidate.start_seconds, 3),
                end_seconds=round(candidate.end_seconds, 3),
                text="Transcript unavailable; use local captions when available.",
                source="placeholder",
                transcript_available=False,
                placeholder=True,
            )
        ]

    normalized = transcript.strip()
    sentences = [segment.strip() for segment in _SENTENCE_SPLIT_RE.split(normalized) if segment.strip()]
    if not sentences:
        sentences = _chunk_words(normalized, 3) or [normalized]

    max_segments = min(3, max(1, len(sentences)))
    if len(sentences) > max_segments:
        merged = _chunk_words(normalized, max_segments)
        if merged:
            sentences = merged

    segment_count = len(sentences)
    segment_duration = duration / segment_count if segment_count else duration
    segments: list[CaptionSegment] = []
    for index, sentence in enumerate(sentences):
        start_seconds = candidate.start_seconds + (index * segment_duration)
        end_seconds = candidate.end_seconds if index == segment_count - 1 else min(candidate.end_seconds, start_seconds + segment_duration)
        segments.append(
            CaptionSegment(
                start_seconds=round(start_seconds, 3),
                end_seconds=round(end_seconds, 3),
                text=sentence,
                source="transcript",
                transcript_available=True,
                placeholder=False,
            )
        )
    return segments
