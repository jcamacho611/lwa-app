from __future__ import annotations

import unittest

from app.core.config import Settings
from app.models.schemas import ClipResult
from app.services.clip_service import apply_plan_feature_flags, build_upgrade_prompt
from app.services.entitlements import EntitlementContext, build_free_plan, build_pro_plan


class PlanMetadataTests(unittest.TestCase):
    def build_clip(self) -> ClipResult:
        return ClipResult(
            id="clip_001",
            title="Lead clip",
            hook="Stop posting random clips if you want better retention.",
            caption="Build the stack around the strongest payoff first.",
            start_time="00:03",
            end_time="00:18",
            score=92,
            rank=1,
            format="Hook First",
            clip_url="https://example.com/clip.mp4",
            why_this_matters="Lead with this because the payoff lands immediately.",
            thumbnail_text="Stop Random Clips",
            cta_suggestion="Ask viewers if they want the full breakdown next.",
            hook_variants=[
                "The fastest way to stop posting random clips.",
                "Why random clipping kills retention.",
            ],
            caption_variants={
                "viral": "Stop posting random clips.",
                "story": "This is the opener because it lands the payoff fast.",
            },
            caption_style="Punchy proof-first",
            platform_fit="TikTok-ready pacing with a fast payoff.",
            packaging_angle="value",
        )

    def test_free_plan_keeps_value_but_trims_premium_packaging(self) -> None:
        settings = Settings()
        entitlement = EntitlementContext(
            subject="client:test",
            subject_source="client_id",
            usage_day="2026-04-17",
            plan=build_free_plan(settings),
            credits_remaining=1,
        )

        gated = apply_plan_feature_flags(clips=[self.build_clip()], entitlement=entitlement)
        clip = gated[0]

        self.assertEqual(len(clip.hook_variants), 1)
        self.assertEqual(set(clip.caption_variants.keys()), {"viral"})
        self.assertEqual(clip.caption_style, "Standard short-form")
        self.assertIsNotNone(clip.caption_modes)
        self.assertEqual(clip.caption_modes.primary, clip.caption)
        self.assertEqual(clip.caption_modes.story, clip.caption)
        self.assertIsNotNone(clip.edit_plan)
        self.assertEqual(clip.edit_plan.posting_role, "post first")
        self.assertIsNotNone(clip.export_bundle)
        self.assertTrue(clip.export_bundle.preview_ready)
        self.assertFalse(clip.export_bundle.download_ready)
        self.assertEqual(clip.export_bundle.post_sequence_label, "post first")
        self.assertIn("Create an account", build_upgrade_prompt(entitlement=entitlement, current_user=None))

    def test_pro_plan_preserves_richer_packaging(self) -> None:
        settings = Settings()
        entitlement = EntitlementContext(
            subject="user:test",
            subject_source="user",
            usage_day="2026-04-17",
            plan=build_pro_plan(settings),
            credits_remaining=12,
            user_id="user_123",
        )

        gated = apply_plan_feature_flags(clips=[self.build_clip()], entitlement=entitlement)
        clip = gated[0]

        self.assertEqual(len(clip.hook_variants), 2)
        self.assertIn("story", clip.caption_variants)
        self.assertEqual(clip.caption_style, "Punchy proof-first")
        self.assertIsNotNone(clip.caption_modes)
        self.assertEqual(clip.caption_modes.story, clip.caption_variants["story"])
        self.assertIsNotNone(clip.edit_plan)
        self.assertEqual(clip.edit_plan.visual_focus, "Stop Random Clips")
        self.assertIsNotNone(clip.export_bundle)
        self.assertTrue(clip.export_bundle.preview_ready)
        self.assertTrue(clip.export_bundle.download_ready)
        self.assertEqual(clip.export_bundle.post_order, 1)
        self.assertIn("Scale", build_upgrade_prompt(entitlement=entitlement, current_user=object()))


if __name__ == "__main__":
    unittest.main()
