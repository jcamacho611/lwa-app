from __future__ import annotations

import unittest

from app.offline_video.caption_engine import build_caption_segments
from app.offline_video.clip_scorer import rank_scored_candidates
from app.offline_video.models import (
    AudioWindow,
    ClipScore,
    MomentCandidate,
    OfflineVideoPipelineOptions,
    SceneBoundary,
    VideoProbeResult,
)
from app.offline_video.offline_pipeline import run_offline_video_pipeline


def _probe() -> VideoProbeResult:
    return VideoProbeResult(
        input_path="/tmp/input.mp4",
        available=True,
        ffprobe_available=True,
        ffmpeg_available=False,
        duration_seconds=90.0,
        width=1080,
        height=1920,
        has_audio=True,
        has_video=True,
        format_name="mov,mp4,m4a,3gp,3g2,mj2",
        stream_count=2,
    )


def _candidate(candidate_id: str, start: float, end: float, target: float, silence_ratio: float, movement: float) -> MomentCandidate:
    return MomentCandidate(
        candidate_id=candidate_id,
        start_seconds=start,
        end_seconds=end,
        target_duration_seconds=target,
        scene_indices=[0, 1],
        audio_window_indices=[0],
        silence_ratio=silence_ratio,
        visual_movement_proxy=movement,
        hook_position_seconds=start,
        caption_readiness=0.0,
        platform_fit=0.0,
    )


class OfflineVideoPipelineTests(unittest.TestCase):
    def test_pipeline_returns_ranked_top_three_and_proof(self) -> None:
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as temp_dir:
            source_path = __import__("pathlib").Path(temp_dir) / "input.mp4"
            source_path.write_bytes(b"fake video bytes")
            output_dir = __import__("pathlib").Path(temp_dir) / "output"

            probe = _probe()
            scenes = [SceneBoundary(start_seconds=0.0, end_seconds=30.0), SceneBoundary(start_seconds=30.0, end_seconds=60.0)]
            audio = [AudioWindow(start_seconds=0.0, end_seconds=15.0, silence_ratio=0.1, average_energy=0.9, peak_energy=0.95)]
            candidates = [
                _candidate("candidate_001", 5.0, 20.0, 15.0, 0.08, 0.9),
                _candidate("candidate_002", 20.0, 50.0, 30.0, 0.15, 0.8),
                _candidate("candidate_003", 30.0, 75.0, 45.0, 0.22, 0.85),
                _candidate("candidate_004", 0.0, 60.0, 60.0, 0.30, 0.5),
            ]

            from app.offline_video import offline_pipeline as pipeline_module

            original_probe = pipeline_module.probe_video
            original_scenes = pipeline_module.detect_scene_boundaries
            original_audio = pipeline_module.analyze_audio_windows
            original_candidates = pipeline_module.generate_moment_candidates
            original_check = pipeline_module.check_ffmpeg_available
            try:
                pipeline_module.check_ffmpeg_available = lambda **kwargs: False
                pipeline_module.probe_video = lambda *args, **kwargs: probe
                pipeline_module.detect_scene_boundaries = lambda *args, **kwargs: scenes
                pipeline_module.analyze_audio_windows = lambda *args, **kwargs: audio
                pipeline_module.generate_moment_candidates = lambda *args, **kwargs: candidates

                result = run_offline_video_pipeline(
                    source_path,
                    output_dir,
                    OfflineVideoPipelineOptions(render=False, transcript="One. Two. Three.", max_results=3),
                )
            finally:
                pipeline_module.check_ffmpeg_available = original_check
                pipeline_module.probe_video = original_probe
                pipeline_module.detect_scene_boundaries = original_scenes
                pipeline_module.analyze_audio_windows = original_audio
                pipeline_module.generate_moment_candidates = original_candidates

        self.assertTrue(result.success)
        self.assertFalse(result.render_requested)
        self.assertFalse(result.ffmpeg_available)
        self.assertEqual(len(result.candidates), 4)
        self.assertEqual(len(result.scored_candidates), 4)
        self.assertEqual(len(result.selected_candidates), 3)
        self.assertEqual(result.selected_candidates[0].rank, 1)
        self.assertTrue(result.selected_candidates[0].is_best_clip)
        self.assertEqual(result.proof["provider_calls"], [])
        self.assertFalse(result.proof["paid_provider_called"])
        self.assertFalse(result.proof["external_action_executed"])
        self.assertEqual(result.proof["render_status"], "strategy_only")
        self.assertEqual(result.proof["rendered_clip_count"], 0)

    def test_pipeline_renders_when_enabled_and_ffmpeg_available(self) -> None:
        from tempfile import TemporaryDirectory
        from pathlib import Path

        with TemporaryDirectory() as temp_dir:
            source_path = Path(temp_dir) / "input.mp4"
            source_path.write_bytes(b"fake video bytes")
            output_dir = Path(temp_dir) / "rendered"

            probe = _probe()
            probe.ffmpeg_available = True
            scenes = [SceneBoundary(start_seconds=0.0, end_seconds=30.0), SceneBoundary(start_seconds=30.0, end_seconds=60.0)]
            audio = [AudioWindow(start_seconds=0.0, end_seconds=15.0, silence_ratio=0.05, average_energy=0.95, peak_energy=1.0)]
            candidates = [_candidate("candidate_001", 5.0, 35.0, 30.0, 0.05, 0.95)]

            from app.offline_video import offline_pipeline as pipeline_module

            original_probe = pipeline_module.probe_video
            original_scenes = pipeline_module.detect_scene_boundaries
            original_audio = pipeline_module.analyze_audio_windows
            original_candidates = pipeline_module.generate_moment_candidates
            original_check = pipeline_module.check_ffmpeg_available
            original_render = pipeline_module.render_clip
            original_thumbnail = pipeline_module.generate_thumbnail
            try:
                pipeline_module.check_ffmpeg_available = lambda **kwargs: True
                pipeline_module.probe_video = lambda *args, **kwargs: probe
                pipeline_module.detect_scene_boundaries = lambda *args, **kwargs: scenes
                pipeline_module.analyze_audio_windows = lambda *args, **kwargs: audio
                pipeline_module.generate_moment_candidates = lambda *args, **kwargs: candidates
                pipeline_module.render_clip = lambda *args, **kwargs: {"ok": True, "output_path": str(output_dir / "clip.mp4"), "error": None, "ffmpeg_available": True}
                pipeline_module.generate_thumbnail = lambda *args, **kwargs: {"ok": True, "output_path": str(output_dir / "clip.jpg"), "error": None, "ffmpeg_available": True}

                result = run_offline_video_pipeline(
                    source_path,
                    output_dir,
                    OfflineVideoPipelineOptions(render=True, transcript="This is a transcript.", max_results=1),
                )
            finally:
                pipeline_module.check_ffmpeg_available = original_check
                pipeline_module.probe_video = original_probe
                pipeline_module.detect_scene_boundaries = original_scenes
                pipeline_module.analyze_audio_windows = original_audio
                pipeline_module.generate_moment_candidates = original_candidates
                pipeline_module.render_clip = original_render
                pipeline_module.generate_thumbnail = original_thumbnail

        self.assertTrue(result.render_requested)
        self.assertTrue(result.ffmpeg_available)
        self.assertEqual(len(result.render_plans), 1)
        self.assertEqual(len(result.render_outputs), 1)
        self.assertEqual(result.proof["render_status"], "rendered")
        self.assertEqual(result.proof["rendered_clip_count"], 1)

    def test_ranking_helper_sets_best_clip_flag(self) -> None:
        scores = [
            ClipScore(candidate_id="candidate_b", total_score=84.0),
            ClipScore(candidate_id="candidate_a", total_score=91.0),
            ClipScore(candidate_id="candidate_c", total_score=72.0),
        ]

        ranked = rank_scored_candidates(scores)
        self.assertEqual([score.candidate_id for score in ranked], ["candidate_a", "candidate_b", "candidate_c"])
        self.assertEqual(ranked[0].rank, 1)
        self.assertEqual(ranked[0].post_rank, 1)
        self.assertTrue(ranked[0].is_best_clip)
        self.assertEqual(ranked[1].rank, 2)
        self.assertEqual(ranked[2].rank, 3)

    def test_caption_builder_uses_transcript_when_present(self) -> None:
        candidate = MomentCandidate(
            candidate_id="candidate_001",
            start_seconds=10.0,
            end_seconds=25.0,
            target_duration_seconds=15.0,
            scene_indices=[0],
            audio_window_indices=[0],
            silence_ratio=0.1,
            visual_movement_proxy=0.8,
            hook_position_seconds=10.0,
            caption_readiness=0.0,
            platform_fit=0.0,
        )

        segments = build_caption_segments(candidate, transcript="First line. Second line. Third line.")
        self.assertEqual(len(segments), 3)
        self.assertTrue(all(not segment.placeholder for segment in segments))
        self.assertTrue(all(segment.source == "transcript" for segment in segments))


if __name__ == "__main__":
    unittest.main()
