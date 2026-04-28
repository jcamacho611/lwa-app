from __future__ import annotations

import tempfile
import unittest
import zipfile
from asyncio import run
from pathlib import Path

from app.core.config import Settings
from app.models.schemas import ClipResult
from app.services.clip_service import apply_plan_feature_flags
from app.services.confidence_engine import build_confidence_label, resolve_confidence_score
from app.services.entitlements import EntitlementContext, build_free_plan
from app.services.export_bundle import create_export_bundle
from app.services.output_builder import OutputBuilder
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
        self.assertIn("hook_score", normalized["clips"][0])
        self.assertIn("score_breakdown", normalized["clips"][0])
        self.assertIn("render_readiness_score", normalized["clips"][0])
        self.assertEqual(normalized["clips"][0]["approval_state"], "approved")
        self.assertEqual(normalized["clips"][1]["approval_state"], "needs_edit")
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
        self.assertIsNotNone(gated[0].hook_score)
        self.assertIsNotNone(gated[0].score_breakdown)
        self.assertIsNotNone(gated[0].render_readiness_score)
        self.assertEqual(gated[0].approval_state, "approved")
        self.assertTrue(gated[0].campaign_requirement_checks)
        self.assertTrue(gated[0].approved)

    def test_export_bundle_writes_zip_with_caption_artifacts_and_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            settings = Settings()
            settings.generated_assets_dir = temp_dir
            bundle = create_export_bundle(
                settings=settings,
                public_base_url="https://backend.example.com",
                source_url="https://example.com/source",
                clips=[
                    {
                        "id": "clip_1",
                        "title": "Lead Clip",
                        "hook": "Stop posting random clips.",
                        "caption": "Use this first.",
                        "transcript_excerpt": "Stop posting random clips if you want better retention.",
                        "post_rank": 1,
                        "score": 91,
                        "start_time": "00:03",
                        "end_time": "00:18",
                    }
                ],
            )

            self.assertEqual(bundle["clip_count"], 1)
            self.assertEqual(bundle["bundle_format"], "zip")
            self.assertIn("manifest_url", bundle)
            self.assertEqual(bundle["artifact_counts"]["caption_txt"], 1)
            self.assertEqual(bundle["artifact_counts"]["subtitle_srt"], 1)
            self.assertEqual(bundle["artifact_counts"]["subtitle_vtt"], 1)
            self.assertTrue(bundle["download_url"].startswith("https://backend.example.com/generated/export-bundles/"))
            self.assertTrue((Path(bundle["bundle_path"])).exists())
            self.assertTrue((Path(bundle["manifest_path"])).exists())

            with zipfile.ZipFile(bundle["bundle_path"]) as bundle_zip:
                names = set(bundle_zip.namelist())
                self.assertIn("manifest.json", names)
                self.assertIn("README.md", names)
                self.assertIn("clips/clip_1/package.json", names)
                self.assertIn("clips/clip_1/caption.txt", names)
                self.assertIn("clips/clip_1/subtitle.srt", names)
                self.assertIn("clips/clip_1/subtitle.vtt", names)

    def test_output_builder_delegates_to_shared_zip_bundle_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            settings = Settings()
            settings.generated_assets_dir = temp_dir
            settings.api_base_url = "https://backend.example.com"
            output_builder = OutputBuilder(settings)

            bundle = run(
                output_builder.create_clip_bundle(
                    request_id="req_123",
                    clips=[
                        {
                            "id": "clip_1",
                            "title": "Lead Clip",
                            "caption": "Use this first.",
                            "transcript_excerpt": "Use this first for the clearest payoff.",
                            "score": 88,
                            "start_time": "00:03",
                            "end_time": "00:14",
                        }
                    ],
                )
            )

            self.assertEqual(bundle["bundle_format"], "zip")
            self.assertIn("manifest_url", bundle)
            self.assertTrue(bundle["download_url"].startswith("https://backend.example.com/generated/export-bundles/"))

    def test_output_builder_creates_export_manifest_for_bulk_export_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            settings = Settings()
            settings.generated_assets_dir = temp_dir
            settings.api_base_url = "https://backend.example.com"
            output_builder = OutputBuilder(settings)

            manifest = output_builder.create_export_manifest(
                request_id="req_456",
                clips=[{"id": "clip_1", "title": "Lead Clip"}],
            )

            self.assertEqual(manifest["clip_count"], 1)
            self.assertTrue(manifest["download_url"].startswith("https://backend.example.com/generated/req_456/"))
            self.assertTrue(Path(manifest["manifest_path"]).exists())


if __name__ == "__main__":
    unittest.main()
