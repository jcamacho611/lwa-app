from __future__ import annotations

import unittest

from app.models.schemas import ClipResult
from app.services.shot_planner import build_shot_plan_for_clip


class ShotPlannerTests(unittest.TestCase):
    def test_build_shot_plan_for_clip_returns_four_roles_and_prompts(self) -> None:
        clip = ClipResult(
            id="clip_001",
            title="Lead clip",
            hook="Stop posting random clips if you want better retention.",
            caption="Build the stack around the strongest payoff first.",
            start_time="00:03",
            end_time="00:18",
            score=92,
            confidence_score=88,
            rank=1,
            packaging_angle="value",
            platform_fit="TikTok-ready pacing with a fast payoff.",
            transcript_excerpt="Lead with the strongest payoff and trim the setup hard.",
        )

        blueprint = build_shot_plan_for_clip(clip, target_platform="TikTok")

        self.assertEqual(blueprint.clip_type, "pattern_interrupt")
        self.assertEqual(blueprint.viral_trigger, "pattern_interrupt")
        self.assertEqual(blueprint.energy_level, "high")
        self.assertEqual([step.role for step in blueprint.shot_plan], ["hook", "context", "payoff", "loop_end"])
        self.assertGreaterEqual(blueprint.shot_plan_confidence, 55)
        self.assertIn("Stop posting random clips", blueprint.visual_engine_prompt)
        self.assertIn("Transition plan", blueprint.motion_prompt)
        self.assertEqual(blueprint.as_clip_update()["text_overlay_plan"], blueprint.text_overlay_plan)


if __name__ == "__main__":
    unittest.main()
