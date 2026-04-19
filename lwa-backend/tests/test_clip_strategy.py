from __future__ import annotations

import unittest

from app.models.schemas import ClipResult
from app.processor import SourceContext
from app.services.clip_service import clip_has_rendered_media, recommend_platform_strategy


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

        self.assertTrue(clip_has_rendered_media(rendered_clip))
        self.assertFalse(clip_has_rendered_media(strategy_only_clip))


if __name__ == "__main__":
    unittest.main()
