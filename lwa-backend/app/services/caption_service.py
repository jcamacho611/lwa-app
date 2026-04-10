from __future__ import annotations

from typing import List, Optional

from ..mock_data import build_mock_clips
from ..models.schemas import ClipResult, TrendItem


def build_fallback_clips(
    *,
    video_url: str,
    target_platform: str,
    selected_trend: Optional[str],
    trend_context: List[TrendItem],
    clip_urls: Optional[List[str]] = None,
    start_end_pairs: Optional[List[tuple[str, str]]] = None,
    source_title: Optional[str] = None,
    transcript_excerpts: Optional[List[Optional[str]]] = None,
) -> List[ClipResult]:
    return build_mock_clips(
        video_url=video_url,
        target_platform=target_platform,
        selected_trend=selected_trend,
        trend_context=trend_context,
        clip_urls=clip_urls,
        start_end_pairs=start_end_pairs,
        source_title=source_title,
        transcript_excerpts=transcript_excerpts,
    )

