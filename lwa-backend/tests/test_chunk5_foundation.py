from __future__ import annotations

import os
import unittest
from unittest import mock

from app.core.config import Settings
from app.models.schemas import ClipResult, ProcessRequest, ProcessingSummary
from app.services.clip_service import apply_operational_metadata, resolve_requested_clip_limit
from app.services.entitlements import EntitlementContext, build_scale_plan


class Chunk5FoundationTests(unittest.TestCase):
    def test_scale_plan_keeps_high_volume_disabled_by_default(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=False):
            settings = Settings()

        plan = build_scale_plan(settings)

        self.assertEqual(plan.feature_flags.clip_limit, 12)
        self.assertFalse(plan.feature_flags.high_volume_clips)
        self.assertTrue(plan.feature_flags.caption_styles)
        self.assertTrue(plan.feature_flags.thumbnail_preview)
        self.assertFalse(plan.feature_flags.export_profiles)

    def test_scale_plan_can_unlock_higher_clip_limit_when_explicitly_enabled(self) -> None:
        with mock.patch.dict(
            os.environ,
            {
                "LWA_ENABLE_HIGH_VOLUME_CLIPS": "true",
                "LWA_SCALE_CLIP_LIMIT": "18",
                "LWA_HIGH_VOLUME_MAX_CLIPS": "24",
                "LWA_MAX_CLIPS_PER_JOB": "24",
            },
            clear=False,
        ):
            settings = Settings()

        plan = build_scale_plan(settings)
        requested, reason = resolve_requested_clip_limit(
            requested_clip_count=30,
            plan_clip_limit=plan.feature_flags.clip_limit,
            hard_max_clip_limit=settings.high_volume_max_clips,
            enable_high_volume_clips=settings.enable_high_volume_clips,
            high_volume_max_clips=settings.high_volume_max_clips,
            max_clips_per_job=settings.max_clips_per_job,
        )

        self.assertEqual(plan.feature_flags.clip_limit, 18)
        self.assertTrue(plan.feature_flags.high_volume_clips)
        self.assertEqual(requested, 18)
        self.assertIn("Requested 30 clips", reason or "")

    def test_processing_summary_accepts_chunk5_optional_fields(self) -> None:
        summary = ProcessingSummary(
            plan_code="scale",
            plan_name="Scale",
            credits_remaining=44,
            estimated_turnaround="preview ready now",
            recommended_next_step="Open the lead preview and export the winners.",
            ai_provider="fallback",
            target_platform="TikTok",
            sources_considered=["manual"],
            processing_mode="real",
            selection_strategy="transcript",
            clip_count_requested=18,
            clip_count_allowed=12,
            clip_count_returned=6,
            thumbnail_count=4,
            thumbnail_generation_enabled=True,
            available_caption_styles=["clean_editorial", "karaoke_bold"],
            default_caption_style="clean_editorial",
            available_export_profiles=["tiktok_reels_9_16", "strategy_only_package"],
            default_export_profile="tiktok_reels_9_16",
            render_quality_summary="rendered=2, raw_only=2, strategy_only=2, render_failed=0",
        )

        self.assertEqual(summary.clip_count_allowed, 12)
        self.assertEqual(summary.thumbnail_count, 4)
        self.assertTrue(summary.thumbnail_generation_enabled)
        self.assertEqual(summary.default_export_profile, "tiktok_reels_9_16")

    def test_operational_metadata_adds_truthful_caption_export_fields(self) -> None:
        settings = Settings()
        entitlement = EntitlementContext(
            subject="user:test",
            subject_source="user",
            usage_day="2026-04-28",
            plan=build_scale_plan(settings),
            credits_remaining=7,
            user_id="user_123",
        )
        clip = ClipResult(
            id="clip_001",
            title="Lead clip",
            hook="Stop clipping this in the wrong order.",
            caption="Lead with the payoff first.",
            score=89,
            start_time="00:05",
            end_time="00:21",
            preview_url="https://example.com/generated/clip.mp4",
            edited_clip_url="https://example.com/generated/clip.mp4",
            preview_image_url="https://example.com/generated/clip.jpg",
            caption_vtt_url="https://example.com/generated/clip.vtt",
            caption_style="clean_editorial",
            packaging_angle="value",
            render_status="ready",
        )
        request = ProcessRequest(
            video_url="https://example.com/source",
            campaign_brief="Promote a creator workflow.",
            campaign_goal="drive clicks",
        )

        updated = apply_operational_metadata(
            clips=[clip],
            request_id="req_chunk5",
            source_label="Source 1",
            request=request,
            entitlement=entitlement,
            target_platform="TikTok",
        )[0]

        self.assertEqual(updated.rendered_status, "rendered")
        self.assertEqual(updated.render_quality, "rendered")
        self.assertFalse(updated.captions_burned_in)
        self.assertEqual(updated.subtitle_url, "https://example.com/generated/clip.vtt")
        self.assertEqual(updated.thumbnail_preview_url, "https://example.com/generated/clip.jpg")
        self.assertEqual(updated.export_profile, "tiktok_reels_9_16")
        self.assertEqual(updated.resolution, "720x1280")
        self.assertTrue(updated.render_notes)
        self.assertIn("Status: Rendered", updated.package_text or "")
        self.assertIn("Export Profile: tiktok_reels_9_16", updated.package_text or "")
        self.assertEqual(updated.asset_manifest["subtitle_url"], "https://example.com/generated/clip.vtt")


if __name__ == "__main__":
    unittest.main()
