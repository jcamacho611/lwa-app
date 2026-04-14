from __future__ import annotations

from typing import List, Optional

from ..core.config import Settings
from ..generation import generate_clips
from ..models.schemas import ClipResult, TrendItem
from ..processor import SourceContext


def resolve_attention_mode(settings: Settings) -> str:
    return "openai" if settings.openai_api_key else "fallback"


async def generate_clip_copy(
    *,
    settings: Settings,
    video_url: str,
    target_platform: str,
    selected_trend: Optional[str],
    content_angle: Optional[str],
    trend_context: List[TrendItem],
    source_context: Optional[SourceContext] = None,
) -> tuple[List[ClipResult], str]:
    return await generate_clips(
        settings=settings,
        video_url=video_url,
        target_platform=target_platform,
        selected_trend=selected_trend,
        content_angle=content_angle,
        trend_context=trend_context,
        source_context=source_context,
    )
