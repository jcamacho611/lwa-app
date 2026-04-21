from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from app.core.config import Settings
from app.models.schemas import ClipResult
from app.processor import ClipSeed, create_social_exports
from app.services.clip_service import apply_plan_feature_flags
from app.services.entitlements import EntitlementContext, build_free_plan


class RenderPreviewPipelineTests(unittest.TestCase):
    def build_clip(self, **overrides: object) -> ClipResult:
        payload = {
            "id": "clip_001",
            "title": "Lead clip",
            "hook": "Start with the surprising line.",
            "caption": "Use this first.",
            "start_time": "00:03",
            "end_time": "00:18",
            "score": 91,
            "rank": 1,
            "format": "Hook First",
        }
        payload.update(overrides)
        return ClipResult(**payload)

    def test_social_export_missing_seed_preserves_playable_preview(self) -> None:
        clip = self.build_clip(clip_url="https://cdn.example.com/raw.mp4")

        with tempfile.TemporaryDirectory() as temp_dir:
            exported, edited_count = create_social_exports(
                settings=Settings(),
                clip_results=[clip],
                clip_seeds=[],
                generated_dir=Path(temp_dir),
                request_id="req_123",
                public_base_url="https://backend.example.com",
                ffmpeg_path="/missing/ffmpeg",
            )

        self.assertEqual(edited_count, 0)
        self.assertEqual(exported[0].clip_url, "https://cdn.example.com/raw.mp4")
        self.assertEqual(exported[0].preview_url, "https://cdn.example.com/raw.mp4")
        self.assertEqual(exported[0].raw_clip_url, "https://cdn.example.com/raw.mp4")
        self.assertEqual(exported[0].aspect_ratio, "source")

    def test_social_export_failure_falls_back_to_raw_preview_and_thumbnail(self) -> None:
        clip = self.build_clip()

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            raw_asset = temp_path / "clip_001_raw.mp4"
            raw_asset.write_bytes(b"not a real video, but it exists")
            seed = ClipSeed(
                id="clip_001",
                start_time="00:03",
                end_time="00:18",
                asset_path=raw_asset,
                clip_url="https://cdn.example.com/raw.mp4",
                raw_clip_url="https://cdn.example.com/raw.mp4",
                preview_image_url="https://cdn.example.com/raw.jpg",
                format="Hook First",
                transcript_excerpt="Start with the surprising line.",
                duration=15,
            )

            exported, edited_count = create_social_exports(
                settings=Settings(),
                clip_results=[clip],
                clip_seeds=[seed],
                generated_dir=temp_path,
                request_id="req_123",
                public_base_url="https://backend.example.com",
                ffmpeg_path="/missing/ffmpeg",
            )

        self.assertEqual(edited_count, 0)
        self.assertEqual(exported[0].clip_url, "https://cdn.example.com/raw.mp4")
        self.assertEqual(exported[0].preview_url, "https://cdn.example.com/raw.mp4")
        self.assertEqual(exported[0].raw_clip_url, "https://cdn.example.com/raw.mp4")
        self.assertEqual(exported[0].preview_image_url, "https://cdn.example.com/raw.jpg")
        self.assertEqual(exported[0].aspect_ratio, "source")

    def test_plan_feature_flags_preserve_explicit_preview_url(self) -> None:
        settings = Settings()
        entitlement = EntitlementContext(
            subject="client:test",
            subject_source="client_id",
            usage_day="2026-04-21",
            plan=build_free_plan(settings),
            credits_remaining=1,
        )
        clip = self.build_clip(
            preview_url="https://cdn.example.com/preview.mp4",
            clip_url="https://cdn.example.com/clip.mp4",
            raw_clip_url="https://cdn.example.com/raw.mp4",
        )

        gated = apply_plan_feature_flags(clips=[clip], entitlement=entitlement)

        self.assertEqual(gated[0].preview_url, "https://cdn.example.com/preview.mp4")
        self.assertTrue(gated[0].is_rendered)
        self.assertFalse(gated[0].is_strategy_only)


if __name__ == "__main__":
    unittest.main()
