from __future__ import annotations

import unittest
from dataclasses import asdict

from app.offline_video.models import (
    AudioWindow,
    CaptionSegment,
    ClipScore,
    MomentCandidate,
    OfflineVideoPipelineOptions,
    OfflineVideoPipelineResult,
    RenderPlan,
    SceneBoundary,
    ThumbnailPlan,
    VideoProbeResult,
)


class OfflineVideoModelTests(unittest.TestCase):
    def test_offline_video_model_defaults_are_structured(self) -> None:
        probe = VideoProbeResult(
            input_path="/tmp/source.mp4",
            available=True,
            ffprobe_available=True,
            ffmpeg_available=True,
            duration_seconds=123.4,
            width=1920,
            height=1080,
            has_audio=True,
            has_video=True,
        )
        scene = SceneBoundary(start_seconds=0.0, end_seconds=15.0)
        audio = AudioWindow(start_seconds=0.0, end_seconds=15.0, silence_ratio=0.2, average_energy=0.8, peak_energy=0.9)
        candidate = MomentCandidate(
            candidate_id="candidate_001",
            start_seconds=5.0,
            end_seconds=20.0,
            target_duration_seconds=15.0,
            scene_indices=[0],
            audio_window_indices=[0],
            silence_ratio=0.2,
            visual_movement_proxy=0.8,
            hook_position_seconds=5.0,
            caption_readiness=0.0,
            platform_fit=0.0,
        )
        caption = CaptionSegment(start_seconds=5.0, end_seconds=10.0, text="Hello world")
        score = ClipScore(candidate_id="candidate_001", total_score=87.5, score_breakdown={"duration_fit": 100.0})
        render_plan = RenderPlan(
            candidate_id="candidate_001",
            source_path="/tmp/source.mp4",
            output_dir="/tmp/out",
            output_path="/tmp/out/candidate_001.mp4",
            thumbnail_path="/tmp/out/candidate_001.jpg",
            start_seconds=5.0,
            end_seconds=20.0,
            target_duration_seconds=15.0,
        )
        thumbnail_plan = ThumbnailPlan(
            candidate_id="candidate_001",
            source_path="/tmp/source.mp4",
            suggested_filename="candidate_001.jpg",
            timestamp_seconds=6.0,
        )
        options = OfflineVideoPipelineOptions()
        result = OfflineVideoPipelineResult(
            source_path="/tmp/source.mp4",
            output_dir="/tmp/out",
            probe=probe,
            scene_boundaries=[scene],
            audio_windows=[audio],
            candidates=[candidate],
            scored_candidates=[score],
            selected_candidates=[score],
            render_plans=[render_plan],
            render_outputs=[],
            proof={},
        )

        self.assertEqual(probe.duration_seconds, 123.4)
        self.assertEqual(scene.source, "fallback")
        self.assertEqual(audio.silence_ratio, 0.2)
        self.assertEqual(candidate.target_duration_seconds, 15.0)
        self.assertTrue(caption.placeholder)
        self.assertEqual(score.total_score, 87.5)
        self.assertTrue(render_plan.output_path.endswith(".mp4"))
        self.assertTrue(thumbnail_plan.suggested_filename.endswith(".jpg"))
        self.assertEqual(options.max_results, 3)
        self.assertEqual(result.output_dir, "/tmp/out")
        self.assertEqual(asdict(result)["source_path"], "/tmp/source.mp4")


if __name__ == "__main__":
    unittest.main()
