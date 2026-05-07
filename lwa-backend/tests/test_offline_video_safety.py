from __future__ import annotations

import unittest
from pathlib import Path

from app.offline_video import render_engine as render_engine_module
from app.offline_video import thumbnail_engine as thumbnail_engine_module
from app.offline_video.ffmpeg_probe import check_ffmpeg_available, probe_video
from app.offline_video.models import MomentCandidate, RenderPlan
from app.offline_video.offline_pipeline import run_offline_video_pipeline
from app.offline_video.render_engine import build_render_plan, render_clip
from app.offline_video.thumbnail_engine import generate_thumbnail


class OfflineVideoSafetyTests(unittest.TestCase):
    def test_probe_video_returns_unavailable_when_input_missing(self) -> None:
        missing = Path("/tmp/nonexistent-offline-video-input.mp4")
        result = probe_video(missing)
        self.assertFalse(result.available)
        self.assertTrue(result.errors)
        self.assertTrue("missing" in result.errors[0] or "probe" in result.errors[0])

    def test_pipeline_rejects_missing_input_file(self) -> None:
        with self.assertRaises(FileNotFoundError):
            run_offline_video_pipeline(Path("/tmp/missing-input.mp4"), Path("/tmp/output"))

    def test_render_and_thumbnail_helpers_block_unsafe_or_missing_ffmpeg(self) -> None:
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            source = temp_path / "source.mp4"
            source.write_bytes(b"video")
            candidate = MomentCandidate(
                candidate_id="candidate_unsafe",
                start_seconds=2.0,
                end_seconds=12.0,
                target_duration_seconds=10.0,
                scene_indices=[0],
                audio_window_indices=[0],
                silence_ratio=0.1,
                visual_movement_proxy=0.8,
                hook_position_seconds=2.0,
                caption_readiness=0.0,
                platform_fit=0.0,
            )
            render_plan = build_render_plan(candidate, temp_path / "renders")
            unsafe_plan = RenderPlan(
                candidate_id=render_plan.candidate_id,
                source_path=render_plan.source_path,
                output_dir=render_plan.output_dir,
                output_path=str(temp_path.parent / "outside.mp4"),
                thumbnail_path=render_plan.thumbnail_path,
                start_seconds=render_plan.start_seconds,
                end_seconds=render_plan.end_seconds,
                target_duration_seconds=render_plan.target_duration_seconds,
                crop_mode=render_plan.crop_mode,
                container_format=render_plan.container_format,
            )

            original_render_check = render_engine_module.check_ffmpeg_available
            original_thumb_check = thumbnail_engine_module.check_ffmpeg_available
            try:
                render_engine_module.check_ffmpeg_available = lambda **kwargs: False
                render_result = render_clip(source, unsafe_plan)
                self.assertFalse(render_result["ok"])
                self.assertIn(render_result["error"], {"ffmpeg_unavailable", "unsafe_output_path"})

                thumbnail_engine_module.check_ffmpeg_available = lambda **kwargs: False
                thumb_result = generate_thumbnail(source, temp_path / "thumb.jpg", 1.0)
                self.assertFalse(thumb_result["ok"])
                self.assertEqual(thumb_result["error"], "ffmpeg_unavailable")
            finally:
                render_engine_module.check_ffmpeg_available = original_render_check
                thumbnail_engine_module.check_ffmpeg_available = original_thumb_check

    def test_ffmpeg_availability_check_uses_system_binaries(self) -> None:
        import shutil

        original_which = shutil.which
        try:
            shutil.which = lambda binary: None  # type: ignore[assignment]
            self.assertFalse(check_ffmpeg_available())
        finally:
            shutil.which = original_which


if __name__ == "__main__":
    unittest.main()
