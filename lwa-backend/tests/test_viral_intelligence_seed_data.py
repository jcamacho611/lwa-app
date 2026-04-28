from __future__ import annotations

import json
import unittest
from pathlib import Path


class ViralIntelligenceSeedDataTests(unittest.TestCase):
    def setUp(self) -> None:
        self.seed_dir = Path(__file__).resolve().parents[1] / "app" / "data" / "viral_intelligence"

    def load_json(self, filename: str):
        return json.loads((self.seed_dir / filename).read_text(encoding="utf-8"))

    def test_all_required_seed_files_exist(self) -> None:
        required = {
            "viral_signal_rules.json",
            "platform_rules.json",
            "platform_modifiers.json",
            "content_category_rules.json",
            "hook_formula_library.json",
            "caption_style_presets.json",
            "thumbnail_rules.json",
            "clip_scoring_weights.json",
            "frontend_badge_rules.json",
            "competitor_matrix.json",
            "sales_positioning_matrix.json",
            "twitch_signal_mapping.json",
            "campaign_readiness_rules.json",
        }
        existing = {path.name for path in self.seed_dir.glob("*.json")}
        self.assertTrue(required.issubset(existing))

    def test_viral_signal_rules_have_expected_shape(self) -> None:
        rows = self.load_json("viral_signal_rules.json")
        self.assertEqual(len(rows), 12)
        ids = [row["id"] for row in rows]
        self.assertEqual(len(ids), len(set(ids)))
        total = round(sum(float(row["weight_default"]) for row in rows), 6)
        self.assertEqual(total, 1.0)

    def test_platform_rules_include_required_platforms(self) -> None:
        rows = self.load_json("platform_rules.json")
        platforms = {row["platform"] for row in rows}
        self.assertEqual(
            platforms,
            {
                "tiktok",
                "reels_instagram",
                "youtube_shorts",
                "facebook_reels",
                "x_video",
                "linkedin_video",
                "whop_community",
            },
        )

    def test_platform_modifiers_reference_known_signal_ids(self) -> None:
        signals = {row["id"] for row in self.load_json("viral_signal_rules.json")}
        modifiers = self.load_json("platform_modifiers.json")
        self.assertEqual(set(modifiers.keys()), {"tiktok", "reels", "shorts", "linkedin", "x"})
        for mapping in modifiers.values():
            self.assertTrue(set(mapping.keys()).issubset(signals))

    def test_frontend_badges_include_required_badges(self) -> None:
        rows = self.load_json("frontend_badge_rules.json")
        badges = {row["badge"] for row in rows}
        self.assertTrue(
            {
                "Best Clip First",
                "Rendered",
                "Ideas Only",
                "Strong Hook",
                "High Shareability",
                "Platform Mismatch",
                "Captions Missing",
                "Trend Match",
                "Score Pill",
                "Provider Pill",
            }.issubset(badges)
        )


if __name__ == "__main__":
    unittest.main()
