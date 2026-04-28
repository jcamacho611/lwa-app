from __future__ import annotations

import unittest

from app.models.schemas import ClipResult
from app.services.render_quality import evaluate_render_quality
from app.services.visual_render_provider import VisualRenderProviderResult


class RenderQualityTests(unittest.TestCase):
    def test_rendered_clip_grades_ready_now(self) -> None:
        clip = ClipResult(
            id="clip_001",
            title="Rendered clip",
            hook="This one is ready to post.",
            caption="Ready now.",
            score=90,
            confidence_score=86,
            preview_url="https://example.com/preview.mp4",
            thumbnail_text="Ready Now",
        )

        evaluation = evaluate_render_quality(clip=clip)

        self.assertEqual(evaluation.visual_engine_status, "ready_now")
        self.assertGreaterEqual(evaluation.render_quality_score, 72)
        self.assertEqual(evaluation.render_readiness_score, evaluation.render_quality_score)
        self.assertIsNone(evaluation.strategy_only_reason)

    def test_disabled_provider_keeps_strategy_only_with_recovery_path(self) -> None:
        clip = ClipResult(
            id="clip_002",
            title="Strategy clip",
            hook="Keep the shot plan even without render access.",
            caption="Strategy only.",
            score=72,
        )
        provider_result = VisualRenderProviderResult(
            provider_state="disabled",
            message="Visual rendering is turned off. Keep the clip strategy-only and preserve the shot plan.",
        )

        evaluation = evaluate_render_quality(clip=clip, render_result=provider_result)

        self.assertEqual(evaluation.visual_engine_status, "strategy_only")
        self.assertEqual(evaluation.render_readiness_score, 46)
        self.assertIn("Shot plan ready", evaluation.strategy_only_reason or "")
        self.assertIn("Turn the visual engine back on", evaluation.recovery_recommendation or "")

    def test_failed_provider_returns_recoverable_state(self) -> None:
        clip = ClipResult(
            id="clip_003",
            title="Recoverable clip",
            hook="This clip should be recoverable.",
            caption="Try again later.",
            score=64,
        )
        provider_result = VisualRenderProviderResult(
            provider_state="failed",
            attempted=True,
            message="Visual rendering is not wired yet. Preserve the director plan and return a recoverable strategy-only clip.",
            error="provider not wired yet",
        )

        evaluation = evaluate_render_quality(clip=clip, render_result=provider_result)

        self.assertEqual(evaluation.visual_engine_status, "recoverable")
        self.assertEqual(evaluation.render_quality_score, 30)
        self.assertEqual(evaluation.render_readiness_score, 30)
        self.assertIn("retry", (evaluation.recovery_recommendation or "").lower())


if __name__ == "__main__":
    unittest.main()
