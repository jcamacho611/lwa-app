from __future__ import annotations

from dataclasses import dataclass

from ..models.schemas import ClipResult
from .visual_render_provider import VisualRenderProviderResult


@dataclass(frozen=True)
class RenderQualityEvaluation:
    visual_engine_status: str
    render_quality_score: int
    strategy_only_reason: str | None = None
    recovery_recommendation: str | None = None

    def as_clip_update(self) -> dict[str, object]:
        return {
            "visual_engine_status": self.visual_engine_status,
            "render_quality_score": self.render_quality_score,
            "strategy_only_reason": self.strategy_only_reason,
            "recovery_recommendation": self.recovery_recommendation,
        }


def evaluate_render_quality(
    *,
    clip: ClipResult,
    render_result: VisualRenderProviderResult | None = None,
) -> RenderQualityEvaluation:
    if has_rendered_media(clip, render_result=render_result):
        score = build_ready_score(clip)
        if score >= 72:
            return RenderQualityEvaluation(
                visual_engine_status="ready_now",
                render_quality_score=score,
            )
        return RenderQualityEvaluation(
            visual_engine_status="needs_review",
            render_quality_score=score,
            recovery_recommendation="Review the pacing, subtitle readability, and first-frame clarity before publishing.",
        )

    if render_result and render_result.provider_state == "disabled":
        return RenderQualityEvaluation(
            visual_engine_status="strategy_only",
            render_quality_score=46,
            strategy_only_reason=render_result.message,
            recovery_recommendation="Enable the visual engine when you are ready to render this clip.",
        )

    if render_result and render_result.provider_state == "missing-key":
        return RenderQualityEvaluation(
            visual_engine_status="strategy_only",
            render_quality_score=42,
            strategy_only_reason=render_result.message,
            recovery_recommendation="Add the visual engine key and retry the highest-ranked clips only.",
        )

    if render_result and render_result.provider_state == "failed":
        error = (render_result.error or render_result.message or "").lower()
        if any(keyword in error for keyword in {"retry", "timeout", "temporary", "not wired", "unavailable"}):
            return RenderQualityEvaluation(
                visual_engine_status="recoverable",
                render_quality_score=30,
                strategy_only_reason=render_result.message,
                recovery_recommendation="Keep the shot plan, surface the strategy-only output, and retry rendering later.",
            )
        return RenderQualityEvaluation(
            visual_engine_status="render_failed",
            render_quality_score=18,
            strategy_only_reason=render_result.message,
            recovery_recommendation="Review the source media and prompt plan before attempting another render.",
        )

    if clip.render_status == "failed":
        return RenderQualityEvaluation(
            visual_engine_status="recoverable",
            render_quality_score=32,
            strategy_only_reason=clip.render_error or "Visual render failed before a playable asset was created.",
            recovery_recommendation="Offer a recover render action and preserve the packaging output.",
        )

    return RenderQualityEvaluation(
        visual_engine_status="strategy_only",
        render_quality_score=38,
        strategy_only_reason=clip.strategy_only_reason or "Shot plan ready, but no visual render was attempted.",
        recovery_recommendation="Show the packaging stack now and render later if source access or credits improve.",
    )


def has_rendered_media(
    clip: ClipResult,
    *,
    render_result: VisualRenderProviderResult | None = None,
) -> bool:
    if any(
        [
            clip.preview_url,
            clip.clip_url,
            clip.edited_clip_url,
            clip.raw_clip_url,
            clip.download_url,
        ]
    ):
        return True
    if render_result and any(
        [
            render_result.asset_url,
            render_result.preview_url,
            render_result.download_url,
        ]
    ):
        return True
    return False


def build_ready_score(clip: ClipResult) -> int:
    base = int(clip.render_quality_score or clip.confidence_score or clip.score or 70)
    if clip.transcript_excerpt:
        base += 3
    if clip.hook and len(clip.hook.split()) <= 14:
        base += 2
    if clip.thumbnail_text:
        base += 2
    return max(min(base, 96), 58)
