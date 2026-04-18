from __future__ import annotations

from typing import List, Optional

from ..core.config import Settings
from ..generation import generate_clips
from ..models.schemas import ClipResult, TrendItem
from ..processor import SourceContext
from .anthropic_service import anthropic_available


def resolve_attention_mode(settings: Settings, *, premium_reasoning: bool = False) -> str:
    provider = settings.ai_provider.lower()

    if provider == "anthropic":
        return "anthropic" if anthropic_available(settings) else "fallback"
    if provider == "openai":
        return "openai" if settings.openai_api_key else "fallback"
    if provider == "ollama":
        return "ollama" if settings.ollama_base_url else "fallback"
    if provider == "fallback":
        return "fallback"
    if provider == "heuristic":
        return "fallback"
    if provider == "auto":
        if anthropic_available(settings):
            return "anthropic"
        if settings.openai_api_key:
            return "openai"
        if settings.ollama_base_url:
            return "ollama"
        return "fallback"

    if premium_reasoning and anthropic_available(settings) and settings.premium_reasoning_provider == "anthropic":
        return "anthropic"
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
    premium_reasoning: bool = False,
) -> tuple[List[ClipResult], str]:
    return await generate_clips(
        settings=settings,
        video_url=video_url,
        target_platform=target_platform,
        selected_trend=selected_trend,
        content_angle=content_angle,
        trend_context=trend_context,
        source_context=source_context,
        premium_reasoning=premium_reasoning,
    )
