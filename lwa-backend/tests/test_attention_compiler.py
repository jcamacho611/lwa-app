from __future__ import annotations

import unittest

from app.models.schemas import ClipResult
from app.processor import SourceContext
from app.services.attention_compiler import compile_with_fallback, rank_compiled_clips


class AttentionCompilerTests(unittest.TestCase):
    def build_clip(
        self,
        *,
        clip_id: str,
        title: str,
        hook: str,
        caption: str,
        score: int,
        packaging_angle: str,
        transcript_excerpt: str,
        start_time: str,
        end_time: str,
    ) -> ClipResult:
        return ClipResult(
            id=clip_id,
            title=title,
            hook=hook,
            caption=caption,
            start_time=start_time,
            end_time=end_time,
            score=score,
            confidence=0.8,
            format="Hook First",
            transcript_excerpt=transcript_excerpt,
            packaging_angle=packaging_angle,
        )

    def test_rank_compiled_clips_keeps_review_rank_separate_from_post_rank(self) -> None:
        clips = [
            self.build_clip(
                clip_id="clip_story",
                title="Founder story payoff",
                hook="This is the exact moment the strategy started working.",
                caption="Story-first payoff that lands after context.",
                score=98,
                packaging_angle="story",
                transcript_excerpt="This is the moment everything finally started working.",
                start_time="00:30",
                end_time="00:45",
            ),
            self.build_clip(
                clip_id="clip_shock",
                title="Stop doing this",
                hook="Stop making this mistake if you want better clips.",
                caption="Fast interruption with a clean payoff.",
                score=92,
                packaging_angle="shock",
                transcript_excerpt="Stop doing this if you want the payoff to hit faster.",
                start_time="00:03",
                end_time="00:18",
            ),
            self.build_clip(
                clip_id="clip_contra",
                title="Most creators get this wrong",
                hook="Most creators are still clipping this the wrong way.",
                caption="Contrarian follow-up built for comments.",
                score=89,
                packaging_angle="controversy",
                transcript_excerpt="Most creators still frame this wrong and miss the point.",
                start_time="00:19",
                end_time="00:29",
            ),
        ]

        ranked = rank_compiled_clips(clips)
        by_id = {clip.id: clip for clip in ranked}

        self.assertEqual(by_id["clip_story"].rank, 1)
        self.assertEqual(by_id["clip_shock"].post_rank, 1)
        self.assertEqual(by_id["clip_contra"].post_rank, 2)
        self.assertEqual(by_id["clip_story"].post_rank, 3)
        self.assertIn("later", by_id["clip_story"].why_this_matters.lower())

    def test_compile_with_fallback_populates_packaging_fields(self) -> None:
        source_context = SourceContext(
            title="Creator growth interview",
            description="Long-form interview about content systems.",
            uploader=None,
            duration_seconds=1200,
            source_url="https://example.com/source",
            clip_seeds=[],
            processing_mode="full",
            selection_strategy="transcript",
            transcript="This is the transcript",
        )
        clips = [
            self.build_clip(
                clip_id="clip_fallback",
                title="Hook worth testing",
                hook="Why this content format is suddenly working again.",
                caption="Test this format before it gets saturated.",
                score=84,
                packaging_angle="curiosity",
                transcript_excerpt="Why this format is working again and what creators keep missing.",
                start_time="00:05",
                end_time="00:21",
            )
        ]

        compiled = compile_with_fallback(
            clips=clips,
            target_platform="TikTok",
            selected_trend="creator growth",
            content_angle=None,
            source_context=source_context,
        )

        self.assertEqual(len(compiled), 1)
        clip = compiled[0]
        self.assertIsNotNone(clip.why_this_matters)
        self.assertIsNotNone(clip.confidence_score)
        self.assertIsNotNone(clip.thumbnail_text)
        self.assertIsNotNone(clip.cta_suggestion)
        self.assertIsNotNone(clip.caption_style)
        self.assertTrue(clip.hook_variants)
        self.assertTrue(clip.caption_variants)
        self.assertEqual(clip.post_rank, 1)
        self.assertGreaterEqual(clip.confidence_score or 0, 55)
        self.assertEqual(len(clip.hook_variants), 3)
        self.assertEqual(len(set(clip.hook_variants)), len(clip.hook_variants))
        self.assertGreaterEqual(len((clip.thumbnail_text or "").split()), 2)
        self.assertLessEqual(len((clip.thumbnail_text or "").split()), 5)
        self.assertIn("Open with this", clip.why_this_matters or "")

    def test_compile_with_fallback_builds_stronger_packaging_for_contrarian_clip(self) -> None:
        clips = [
            self.build_clip(
                clip_id="clip_contra",
                title="Everyone clips this wrong",
                hook="Most creators still post this angle in the wrong order.",
                caption="This contrarian beat should spark comments and debate.",
                score=86,
                packaging_angle="controversy",
                transcript_excerpt="Most creators still clip this wrong and miss the actual payoff.",
                start_time="00:08",
                end_time="00:22",
            )
        ]

        compiled = compile_with_fallback(
            clips=clips,
            target_platform="TikTok",
            selected_trend=None,
            content_angle=None,
            source_context=None,
        )

        clip = compiled[0]
        self.assertEqual(clip.post_rank, 1)
        self.assertEqual(clip.caption_style, "Tension-led contrarian")
        self.assertIn("which side", (clip.cta_suggestion or "").lower())
        self.assertEqual(len(clip.hook_variants), 3)
        self.assertTrue(any("wrong" in variant.lower() or "contrarian" in variant.lower() for variant in clip.hook_variants))


if __name__ == "__main__":
    unittest.main()
