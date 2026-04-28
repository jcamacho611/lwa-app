from __future__ import annotations

import unittest

from app.models.schemas import ClipResult, TrendItem
from app.services.trend_intelligence import build_trend_intelligence


class TrendIntelligenceTests(unittest.TestCase):
    def test_selected_trend_alignment_scores_high_when_phrase_matches(self) -> None:
        clip = ClipResult(
            id="clip_trend_001",
            title="Creator growth system",
            hook="This creator growth system still works right now.",
            caption="Use this creator growth framework before the format saturates.",
            score=88,
        )

        intelligence = build_trend_intelligence(
            clip=clip,
            selected_trend="creator growth",
            trend_context=[
                TrendItem(id="trend_1", title="creator growth", source="google", detail="High search volume"),
            ],
        )

        self.assertGreaterEqual(intelligence["trend_match_score"], 80)
        self.assertEqual(intelligence["time_sensitivity"], "high")
        self.assertIn("selected trend", str(intelligence["trend_alignment_reason"]).lower())

    def test_evergreen_clip_gets_high_reuse_potential(self) -> None:
        clip = ClipResult(
            id="clip_trend_002",
            title="Retention framework",
            hook="The 3-step retention framework every creator should test.",
            caption="Use this step-by-step system to improve watch time.",
            transcript_excerpt="Here is the exact process and checklist I use to improve retention over time.",
            score=84,
        )

        intelligence = build_trend_intelligence(
            clip=clip,
            selected_trend=None,
            trend_context=[],
        )

        self.assertLessEqual(intelligence["trend_match_score"], 20)
        self.assertGreaterEqual(intelligence["reuse_potential"], 78)
        self.assertEqual(intelligence["evergreen_status"], "evergreen")
        self.assertEqual(intelligence["time_sensitivity"], "low")


if __name__ == "__main__":
    unittest.main()
