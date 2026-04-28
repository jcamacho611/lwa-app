from __future__ import annotations

import unittest

from fastapi.testclient import TestClient

from app.main import create_app
from app.services.attention_compiler import (
    detect_frontend_badges,
    generate_hook_variants_from_library,
    normalize_platform_weights,
    resolve_caption_preset,
    score_clip,
)
from app.services.intelligence_registry import (
    build_clip_intelligence_context,
    build_unified_category_profile,
    build_unified_platform_profile,
    load_intelligence_tables,
    public_claim_guard,
    suggest_weight_adjustments_from_feedback,
    validate_intelligence_tables,
)


class IntelligenceTableIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(create_app())

    def tearDown(self) -> None:
        self.client.close()

    def test_registry_loads_unified_keys(self) -> None:
        tables = load_intelligence_tables()
        self.assertIn("viral", tables)
        self.assertIn("product", tables)
        self.assertIn("twitch", tables)
        self.assertIn("capabilities", tables)
        self.assertIn("runtime_sources", tables)

    def test_registry_validation_passes(self) -> None:
        validation = validate_intelligence_tables()
        self.assertTrue(validation["ok"], validation)
        self.assertEqual(validation["signal_weight_total"], 1.0)
        self.assertEqual(validation["signal_count"], 12)

    def test_platform_and_category_profiles_build(self) -> None:
        platform = build_unified_platform_profile("instagram_reels")
        category = build_unified_category_profile("podcast")
        self.assertEqual(platform["canonical_platform"], "reels")
        self.assertTrue(platform["rule"])
        self.assertEqual(category["category"], "podcast")
        self.assertTrue(category["caption_preset"])
        self.assertTrue(category["hook_formulas"])

    def test_clip_intelligence_context_builds_normalized_weights(self) -> None:
        context = build_clip_intelligence_context("tiktok", "podcast")
        weights = context["signal_weights"]
        self.assertAlmostEqual(sum(weights.values()), 1.0, places=6)
        self.assertEqual(len(weights), 12)

    def test_claim_guard_blocks_forbidden_claims_and_allows_safe_copy(self) -> None:
        blocked = public_claim_guard("This tool guarantees viral views and guaranteed revenue.")
        self.assertFalse(blocked["safe"])
        self.assertTrue(blocked["blocked_terms"])

        allowed = public_claim_guard("LWA helps prepare ranked clip packages with local fallback.")
        self.assertTrue(allowed["safe"])

    def test_feedback_recommendations_do_not_mutate_seed(self) -> None:
        result = suggest_weight_adjustments_from_feedback()
        self.assertIn("recommendations", result)
        self.assertFalse(result["seed_mutation_performed"])

    def test_attention_compiler_helpers_use_registry_data(self) -> None:
        weights = normalize_platform_weights("linkedin_video")
        self.assertAlmostEqual(sum(weights.values()), 1.0, places=6)

        score, breakdown = score_clip(
            {
                "vs_001": 0.91,
                "vs_002": 0.85,
                "vs_003": 0.62,
                "vs_004": 0.76,
                "vs_005": 0.80,
                "vs_006": 0.64,
                "vs_007": 0.55,
                "vs_008": 0.70,
                "vs_009": 0.82,
                "vs_010": 0.40,
                "vs_011": 0.45,
                "vs_012": 0.35,
            },
            "business_strategy",
            "linkedin_video",
        )
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)
        self.assertEqual(len(breakdown), 12)

    def test_hook_variants_caption_preset_and_badges(self) -> None:
        clip = {
            "id": "clip_001",
            "title": "Best clip",
            "hook": "Stop scrolling if you want better clips.",
            "caption": "Save this and send it to another creator.",
            "target_platform": "tiktok",
            "score": 88,
            "rank": 1,
            "render_status": "ready",
            "clip_url": "https://example.com/clip.mp4",
            "rendered": True,
            "signals": {"vs_001": 0.9, "vs_007": 0.85},
            "platform_compatibility": {"tiktok": True},
            "ai_provider": "fallback",
        }
        variants = generate_hook_variants_from_library(clip, "coaching_self_dev", "vs_001")
        self.assertEqual(len(variants), 3)
        self.assertTrue(all(item.get("text") for item in variants))
        self.assertEqual(resolve_caption_preset("business_strategy", "linkedin_video"), "clean_editorial")

        badges = detect_frontend_badges(clip)
        badge_names = {item["badge"] for item in badges}
        self.assertIn("Best Clip First", badge_names)
        self.assertIn("Rendered", badge_names)
        self.assertIn("Score Pill", badge_names)

    def test_intelligence_routes_respond(self) -> None:
        response = self.client.get("/v1/intelligence")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["ok"], True)

        response = self.client.get("/v1/intelligence/viral-signals")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["items"]), 12)

        response = self.client.post("/v1/intelligence/claim-check", json={"text": "guaranteed viral results"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["safe"], False)


if __name__ == "__main__":
    unittest.main()
