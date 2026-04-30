from __future__ import annotations

import unittest

from app.models.schemas import ClipResult
from app.services.director_brain import build_director_brain_plan, profile_for_platform


class DirectorBrainTests(unittest.TestCase):
    def build_clip(self, **overrides) -> ClipResult:
        payload = {
            "id": "clip_001",
            "title": "Stop losing the first three seconds",
            "hook": "Stop losing the first three seconds",
            "caption": "This workflow makes the payoff obvious before the viewer scrolls.",
            "score": 82,
            "confidence_score": 78,
            "rank": 1,
            "duration": 24,
            "transcript_excerpt": "Stop losing the first three seconds by hiding the payoff after setup.",
        }
        payload.update(overrides)
        return ClipResult(**payload)

    def test_platform_profiles_are_distinct(self) -> None:
        self.assertEqual(profile_for_platform("TikTok").primary_signal, "completion and rewatch")
        self.assertEqual(profile_for_platform("Instagram Reels").primary_signal, "DM shares")
        self.assertEqual(profile_for_platform("YouTube Shorts").primary_signal, "engaged views")
        self.assertEqual(profile_for_platform("LinkedIn").primary_signal, "dwell and comment depth")

    def test_tiktok_plan_prioritizes_fast_hook_and_strategy_truth(self) -> None:
        plan = build_director_brain_plan(
            self.build_clip(clip_url=None, preview_url=None),
            target_platform="TikTok",
            category="coaching",
        )

        self.assertEqual(plan.platform, "TikTok")
        self.assertEqual(plan.rendered_state, "strategy_only")
        self.assertIn("completion", plan.explanation)
        self.assertTrue(any("Strategy-only" in note for note in plan.platform_notes))
        self.assertGreaterEqual(len(plan.hook_variants), 3)

    def test_reels_plan_uses_dm_share_caption(self) -> None:
        plan = build_director_brain_plan(
            self.build_clip(caption="Send this to the creator still burying the payoff."),
            target_platform="Reels",
            category="podcast",
        )

        self.assertEqual(plan.platform, "Instagram Reels")
        self.assertIn("Send this", plan.caption)
        self.assertIn("DM shares", plan.platform_notes[0])

    def test_shorts_plan_prefers_swipe_away_reduction(self) -> None:
        plan = build_director_brain_plan(
            self.build_clip(),
            target_platform="YouTube Shorts",
            category="education",
        )

        self.assertEqual(plan.platform, "YouTube Shorts")
        self.assertIn("swipe", plan.platform_notes[0])
        self.assertLessEqual(len(plan.hook_variants[0].split()), 10)

    def test_linkedin_plan_uses_professional_dwell_prompt(self) -> None:
        plan = build_director_brain_plan(
            self.build_clip(caption="This team workflow fixes the review loop."),
            target_platform="LinkedIn",
            category="ai_tech",
        )

        self.assertEqual(plan.platform, "LinkedIn")
        self.assertIn("workflow", plan.caption.lower())
        self.assertIn("dwell", plan.platform_notes[0])

    def test_rendered_state_is_derived_from_playable_media_only(self) -> None:
        rendered = build_director_brain_plan(
            self.build_clip(preview_url="https://cdn.example.com/clip.mp4"),
            target_platform="TikTok",
        )
        strategy = build_director_brain_plan(
            self.build_clip(thumbnail_url="https://cdn.example.com/thumb.jpg"),
            target_platform="TikTok",
        )

        self.assertEqual(rendered.rendered_state, "rendered")
        self.assertEqual(strategy.rendered_state, "strategy_only")


if __name__ == "__main__":
    unittest.main()
