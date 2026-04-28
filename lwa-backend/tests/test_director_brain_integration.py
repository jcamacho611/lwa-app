from __future__ import annotations

import unittest

from app.core.config import Settings
from app.models.schemas import ClipResult
from app.services.clip_service import apply_director_brain_foundation


class DirectorBrainIntegrationTests(unittest.IsolatedAsyncioTestCase):
    async def test_director_brain_attaches_shot_plan_and_preserves_strategy_only(self) -> None:
        settings = Settings()
        settings.visual_engine_enabled = False
        settings.visual_engine_api_key = ""

        clips = [
            ClipResult(
                id="clip_001",
                title="Lead clip",
                hook="Stop posting random clips if you want better retention.",
                caption="Build the stack around the strongest payoff first.",
                start_time="00:03",
                end_time="00:18",
                score=92,
                confidence_score=88,
                rank=1,
                clip_url="https://example.com/clip.mp4",
                packaging_angle="value",
                platform_fit="TikTok-ready pacing with a fast payoff.",
            ),
            ClipResult(
                id="clip_002",
                title="Strategy clip",
                hook="Keep the shot plan even before media is ready.",
                caption="Strategy only is still useful.",
                start_time="00:21",
                end_time="00:34",
                score=74,
                confidence_score=71,
                rank=2,
                packaging_angle="curiosity",
                platform_fit="YouTube Shorts-ready structure with a clear setup.",
            ),
        ]

        enriched, summary = await apply_director_brain_foundation(
            settings=settings,
            clips=clips,
            target_platform="TikTok",
        )

        self.assertEqual(len(enriched[0].shot_plan), 4)
        self.assertEqual(enriched[0].rendered_by, "LWA Omega Visual Engine")
        self.assertEqual(enriched[0].visual_engine_status, "ready_now")
        self.assertIsNotNone(enriched[0].render_readiness_score)
        self.assertEqual(enriched[1].visual_engine_status, "strategy_only")
        self.assertEqual(enriched[1].render_readiness_score, 46)
        self.assertIsNotNone(enriched[1].shot_plan_confidence)
        self.assertIsNotNone(enriched[1].visual_engine_prompt)
        self.assertIsNotNone(enriched[1].motion_prompt)
        self.assertIsNotNone(enriched[1].text_overlay_plan)
        self.assertIsNotNone(enriched[1].subtitle_guidance)
        self.assertIsNotNone(enriched[1].transition_plan)
        self.assertIsNotNone(enriched[1].strategy_only_reason)
        self.assertIsNotNone(enriched[1].recovery_recommendation)
        self.assertFalse(summary["visual_engine_enabled"])
        self.assertEqual(summary["visual_engine_attempted_count"], 0)
        self.assertEqual(summary["visual_engine_ready_count"], 1)
        self.assertEqual(summary["visual_engine_failed_count"], 0)
        self.assertEqual(summary["rendered_clip_count"], 1)
        self.assertEqual(summary["strategy_only_clip_count"], 1)


if __name__ == "__main__":
    unittest.main()
