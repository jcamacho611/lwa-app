from __future__ import annotations

import unittest

from app.core.config import Settings
from app.models.schemas import ClipResult, ProcessRequest
from app.services.clip_service import (
    apply_operational_metadata,
    build_campaign_notes,
    resolve_requested_clip_limit,
)
from app.services.entitlements import EntitlementContext, build_free_plan, build_scale_plan


class CampaignFoundationTests(unittest.TestCase):
    def build_clip(self) -> ClipResult:
        return ClipResult(
            id="clip_001",
            title="Lead clip",
            hook="Stop opening with the wrong beat.",
            caption="Lead with the payoff.",
            score=88,
            clip_url="https://example.com/generated/clip.mp4",
            why_this_matters="Open with this because the payoff lands fast.",
            packaging_angle="value",
            detected_category="business_strategy",
            post_rank=1,
            render_status="ready",
        )

    def test_clip_limit_request_clamps_to_plan_limit(self) -> None:
        requested, reason = resolve_requested_clip_limit(
            requested_clip_count=9,
            plan_clip_limit=3,
            hard_max_clip_limit=12,
        )

        self.assertEqual(requested, 3)
        self.assertIn("Requested 9 clips", reason or "")

    def test_clip_limit_without_request_uses_plan_limit(self) -> None:
        requested, reason = resolve_requested_clip_limit(
            requested_clip_count=None,
            plan_clip_limit=6,
            hard_max_clip_limit=12,
        )

        self.assertEqual(requested, 6)
        self.assertIsNone(reason)

    def test_campaign_notes_always_include_manual_review_disclaimer(self) -> None:
        notes = build_campaign_notes(
            request=ProcessRequest(
                video_url="https://example.com/source",
                campaign_brief="Promote the offer.",
                campaign_goal="drive clicks",
            ),
            campaign_enabled=False,
        )

        self.assertIn("Review campaign rules manually before posting.", notes)
        self.assertIn("This package does not submit to any campaign automatically.", notes)

    def test_free_plan_campaign_request_stays_basic(self) -> None:
        settings = Settings()
        entitlement = EntitlementContext(
            subject="client:test",
            subject_source="client_id",
            usage_day="2026-04-28",
            plan=build_free_plan(settings),
            credits_remaining=1,
        )
        request = ProcessRequest(
            video_url="https://example.com/source",
            campaign_brief="Launch a creator offer.",
            campaign_goal="drive clicks",
            required_hashtags=["#launch", "#creator"],
            allowed_platforms=["TikTok"],
        )

        updated = apply_operational_metadata(
            clips=[self.build_clip()],
            request_id="req_campaign_free",
            source_label="Source 1",
            request=request,
            entitlement=entitlement,
            target_platform="TikTok",
        )[0]

        self.assertIsNone(updated.campaign_fit_score)
        self.assertEqual(updated.required_hashtag_suggestions, [])
        self.assertTrue(updated.platform_notes)

    def test_scale_plan_campaign_request_unlocks_campaign_packaging(self) -> None:
        settings = Settings()
        entitlement = EntitlementContext(
            subject="user:test",
            subject_source="user",
            usage_day="2026-04-28",
            plan=build_scale_plan(settings),
            credits_remaining=10,
            user_id="user_123",
        )
        request = ProcessRequest(
            video_url="https://example.com/source",
            campaign_brief="Launch a creator offer.",
            campaign_goal="drive clicks",
            required_hashtags=["#launch", "#creator"],
            allowed_platforms=["TikTok"],
        )

        updated = apply_operational_metadata(
            clips=[self.build_clip()],
            request_id="req_campaign_scale",
            source_label="Source 1",
            request=request,
            entitlement=entitlement,
            target_platform="TikTok",
        )[0]

        self.assertIsNotNone(updated.campaign_fit_score)
        self.assertTrue(updated.required_hashtag_suggestions)
        self.assertTrue(updated.export_ready)
        self.assertEqual(updated.rendered_status, "raw_only")


if __name__ == "__main__":
    unittest.main()
