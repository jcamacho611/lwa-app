from __future__ import annotations

import unittest

from fastapi import HTTPException

from app.models.schemas import ClipResult
from app.processor import SourceContext
from app.services.clip_service import (
    clip_has_rendered_media,
    clip_record_needs_recovery,
    recommend_platform_strategy,
    recovery_request_for_clip,
    select_recovery_candidate,
)


class ClipStrategyTests(unittest.TestCase):
    def build_source_context(
        self,
        *,
        title: str,
        description: str,
        transcript: str,
        visual_summary: str = "",
        source_platform: str = "YouTube",
    ) -> SourceContext:
        return SourceContext(
            title=title,
            description=description,
            uploader=None,
            duration_seconds=1200,
            source_url="https://example.com/source",
            clip_seeds=[],
            processing_mode="full",
            selection_strategy="transcript",
            transcript=transcript,
            visual_summary=visual_summary,
            source_platform=source_platform,
        )

    def test_recommend_platform_strategy_prefers_tiktok_for_anime_edits(self) -> None:
        source_context = self.build_source_context(
            title="Anime arc breakdown",
            description="AMV style edit around a character reveal.",
            transcript="This anime edit lands on the reveal beat and the fandom payoff.",
            visual_summary="High contrast character shots and fast motion.",
            source_platform="YouTube",
        )

        platform, reason, content_type, output_style = recommend_platform_strategy(
            source_context=source_context,
            detected_source_platform="YouTube",
            selected_trend=None,
            content_angle=None,
        )

        self.assertEqual(platform, "TikTok")
        self.assertEqual(content_type, "Anime / fandom edit")
        self.assertIn("cold open", output_style.lower())
        self.assertIn("anime / fandom edit", reason.lower())

    def test_recommend_platform_strategy_prefers_shorts_for_commentary(self) -> None:
        source_context = self.build_source_context(
            title="Podcast reaction clip",
            description="Long-form creator commentary and review.",
            transcript="In this podcast breakdown we react to the release and explain why it matters.",
            source_platform="YouTube",
        )

        platform, _, content_type, output_style = recommend_platform_strategy(
            source_context=source_context,
            detected_source_platform="YouTube",
            selected_trend="creator commentary",
            content_angle="value",
        )

        self.assertEqual(platform, "YouTube Shorts")
        self.assertEqual(content_type, "Reaction / commentary")
        self.assertIn("readable captions", output_style.lower())

    def test_clip_has_rendered_media_detects_preview_assets(self) -> None:
        rendered_clip = ClipResult(
            id="clip_001",
            title="Rendered clip",
            hook="Lead with the payoff.",
            caption="Preview is ready.",
            start_time="00:03",
            end_time="00:18",
            score=92,
            format="Hook First",
            preview_url="https://example.com/preview.mp4",
        )
        strategy_only_clip = ClipResult(
            id="clip_002",
            title="Strategy only",
            hook="Use the copy first.",
            caption="No media asset yet.",
            start_time="00:20",
            end_time="00:34",
            score=84,
            format="Hook First",
        )
        thumbnail_only_clip = ClipResult(
            id="clip_003",
            title="Thumbnail only",
            hook="Still image is not a playable preview.",
            caption="Needs a video render.",
            start_time="00:40",
            end_time="00:54",
            score=80,
            format="Hook First",
            preview_image_url="https://example.com/still.jpg",
        )

        self.assertTrue(clip_has_rendered_media(rendered_clip))
        self.assertFalse(clip_has_rendered_media(strategy_only_clip))
        self.assertFalse(clip_has_rendered_media(thumbnail_only_clip))

    def test_clip_record_needs_recovery_checks_missing_media(self) -> None:
        self.assertTrue(clip_record_needs_recovery({"preview_url": None, "clip_url": None}))
        self.assertTrue(clip_record_needs_recovery({"preview_image_url": "https://example.com/still.jpg"}))
        self.assertFalse(clip_record_needs_recovery({"preview_url": "https://example.com/preview.mp4"}))

    def test_recovery_request_requires_reusable_source_reference(self) -> None:
        with self.assertRaises(HTTPException) as context:
            recovery_request_for_clip({"source_video_url": "None", "source_type": "url"})

        self.assertEqual(context.exception.status_code, 409)
        self.assertIn("reusable source reference", str(context.exception.detail))

    def test_select_recovery_candidate_prefers_matching_clip_id(self) -> None:
        recovered_clip = ClipResult(
            id="clip_002",
            title="Recovered clip",
            hook="Recovered hook",
            caption="Recovered caption",
            start_time="00:10",
            end_time="00:22",
            score=91,
            format="Hook First",
            preview_url="https://example.com/recovered.mp4",
        )
        fallback_clip = ClipResult(
            id="clip_001",
            title="Fallback clip",
            hook="Fallback hook",
            caption="Fallback caption",
            start_time="00:03",
            end_time="00:14",
            score=84,
            format="Hook First",
            preview_url="https://example.com/fallback.mp4",
        )

        selected = select_recovery_candidate(
            original_clip={"clip_id": "clip_002", "start_time": "00:10", "end_time": "00:22"},
            recovered_clips=[fallback_clip, recovered_clip],
        )

        self.assertIsNotNone(selected)
        self.assertEqual(selected.id, "clip_002")


if __name__ == "__main__":
    unittest.main()
