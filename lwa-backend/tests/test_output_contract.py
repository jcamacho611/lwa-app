from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from app.core.config import Settings
from app.models.schemas import ClipResult
from app.services.clip_service import apply_plan_feature_flags
from app.services.confidence_engine import build_confidence_label, resolve_confidence_score
from app.services.entitlements import EntitlementContext, build_free_plan
from app.services.export_bundle import create_export_bundle
from app.services.response_normalizer import normalize_response


class OutputContractTests(unittest.TestCase):
    def test_confidence_labels_are_creator_facing(self) -> None:
        self.assertEqual(build_confidence_label({"confidence_score": 91}), "High viral potential")
        self.assertEqual(build_confidence_label({"confidence_score": 80}), "Strong early signal")
        self.assertEqual(build_confidence_label({"confidence_score": 70}), "Worth testing")
        self.assertEqual(build_confidence_label({"confidence_score": 45}), "Needs stronger packaging")
        self.assertEqual(resolve_confidence_score({"confidence": 0.88}), 88)

    def test_response_normalizer_adds_render_state_and_fallback_reason(self) -> None:
        normalized = normalize_response(
            [
                {
                    "id": "clip_1",
                    "hook": "This is the opener.",
                    "score": 91,
                    "preview_url": "https://example.com/preview.mp4",
                },
                {
                    "id": "clip_2",
                    "hook": "This idea needs media.",
                    "score": 72,
                },
            ]
        )

        self.assertEqual(normalized["rendered_count"], 1)
        self.assertEqual(normalized["strategy_count"], 1)
        self.assertTrue(normalized["clips"][0]["is_rendered"])
        self.assertFalse(normalized["clips"][0]["is_strategy_only"])
        self.assertFalse(normalized["clips"][1]["is_rendered"])
        self.assertTrue(normalized["clips"][1]["is_strategy_only"])
        self.assertEqual(normalized["clips"][0]["confidence_label"], "High viral potential")
        self.assertIn("posting plan", normalized["clips"][1]["reason"])

    def test_plan_output_contract_includes_confidence_and_state_flags(self) -> None:
        settings = Settings()
        entitlement = EntitlementContext(
            subject="client:test",
            subject_source="client_id",
            usage_day="2026-04-21",
            plan=build_free_plan(settings),
            credits_remaining=1,
        )
        clip = ClipResult(
            id="clip_001",
            title="Lead clip",
            hook="This clip opens fast.",
            caption="Use this first.",
            start_time="00:03",
            end_time="00:18",
            score=92,
            confidence=0.9,
            rank=1,
            format="Hook First",
            clip_url="https://example.com/clip.mp4",
        )

        gated = apply_plan_feature_flags(clips=[clip], entitlement=entitlement)

        self.assertEqual(gated[0].confidence_score, 90)
        self.assertEqual(gated[0].confidence_label, "High viral potential")
        self.assertTrue(gated[0].is_rendered)
        self.assertFalse(gated[0].is_strategy_only)

    def test_export_bundle_writes_json_and_returns_public_download_url(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            settings = Settings()
            settings.generated_assets_dir = temp_dir
            bundle = create_export_bundle(
                settings=settings,
                public_base_url="https://backend.example.com",
                source_url="https://example.com/source",
                clips=[{"id": "clip_1", "title": "Lead Clip"}],
            )

            self.assertEqual(bundle["clip_count"], 1)
            self.assertTrue(bundle["download_url"].startswith("https://backend.example.com/generated/export-bundles/"))
            self.assertTrue((Path(temp_dir) / "export-bundles" / bundle["file_name"]).exists())


if __name__ == "__main__":
    unittest.main()
