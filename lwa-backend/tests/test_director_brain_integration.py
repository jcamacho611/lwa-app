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

    async def test_missing_visual_key_keeps_strategy_clip_without_fake_media(self) -> None:
        settings = Settings()
        settings.visual_engine_enabled = True
        settings.visual_engine_api_key = ""

        clips = [
            ClipResult(
                id="clip_strategy",
                title="Strategy clip",
                hook="Make the payoff obvious before you render.",
                caption="Use the shot plan first, then retry render.",
                start_time="00:05",
                end_time="00:20",
                score=81,
                confidence_score=77,
                rank=1,
                platform_fit="Reels-ready structure with a direct payoff.",
            ),
        ]

        enriched, summary = await apply_director_brain_foundation(
            settings=settings,
            clips=clips,
            target_platform="Reels",
        )

        self.assertIsNone(enriched[0].preview_url)
        self.assertIsNone(enriched[0].clip_url)
        self.assertIsNone(enriched[0].download_url)
        self.assertEqual(enriched[0].visual_engine_status, "strategy_only")
        self.assertEqual(enriched[0].render_status, "pending")
        self.assertIsNotNone(enriched[0].strategy_only_reason)
        self.assertIsNotNone(enriched[0].recovery_recommendation)
        self.assertEqual(summary["visual_engine_attempted_count"], 0)
        self.assertEqual(summary["rendered_clip_count"], 0)
        self.assertEqual(summary["strategy_only_clip_count"], 1)

    async def test_existing_rendered_clip_does_not_call_unwired_provider(self) -> None:
        settings = Settings()
        settings.visual_engine_enabled = True
        settings.visual_engine_api_key = "configured-for-test"
        settings.visual_engine_max_renders_per_request = 1

        clips = [
            ClipResult(
                id="clip_rendered",
                title="Rendered clip",
                hook="Show the proof before adding more effects.",
                caption="This clip already has playable media.",
                start_time="00:02",
                end_time="00:17",
                score=88,
                confidence_score=84,
                rank=1,
                preview_url="https://cdn.example.com/clip.mp4",
                platform_fit="YouTube Shorts-ready pacing.",
            ),
        ]

        enriched, summary = await apply_director_brain_foundation(
            settings=settings,
            clips=clips,
            target_platform="YouTube Shorts",
        )

        self.assertEqual(enriched[0].preview_url, "https://cdn.example.com/clip.mp4")
        self.assertEqual(enriched[0].visual_engine_status, "ready_now")
        self.assertEqual(enriched[0].render_status, "ready")
        self.assertEqual(enriched[0].rendered_by, "LWA Omega Visual Engine")
        self.assertEqual(summary["visual_engine_attempted_count"], 0)
        self.assertEqual(summary["visual_engine_ready_count"], 1)
        self.assertEqual(summary["visual_engine_failed_count"], 0)
        self.assertEqual(summary["rendered_clip_count"], 1)
        self.assertEqual(summary["strategy_only_clip_count"], 0)


if __name__ == "__main__":
    unittest.main()
