from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


def load_runner():
    module_path = Path(__file__).resolve().with_name("source_matrix_runner.py")
    spec = importlib.util.spec_from_file_location("source_matrix_runner", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load source_matrix_runner.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


runner = load_runner()


class SourceMatrixRunnerTests(unittest.TestCase):
    def test_build_cases_covers_any_source_spec_lanes(self) -> None:
        fixtures = {
            extension: Path(f"/tmp/poc-fixture.{extension}")
            for extension in [
                "mp4",
                "mov",
                "m4v",
                "webm",
                "mp3",
                "wav",
                "m4a",
                "jpg",
                "png",
                "webp",
                "heic",
                "heif",
            ]
        }

        cases = runner.build_cases(
            fixtures,
            youtube_url="https://www.youtube.com/watch?v=blocked",
            twitch_url="https://www.twitch.tv/videos/123",
            unsupported_url="https://example.com/not-supported",
        )
        cases_by_id = {case.id: case for case in cases}

        required_ids = {
            "upload_mp4",
            "upload_mov",
            "upload_m4v",
            "upload_webm",
            "upload_mp3",
            "upload_wav",
            "upload_m4a",
            "upload_jpg",
            "upload_png",
            "upload_webp",
            "upload_heic",
            "upload_heif",
            "prompt_only",
            "music_prompt",
            "campaign_objective",
            "youtube_public_url",
            "twitch_public_url",
            "unsupported_public_url",
        }

        self.assertTrue(required_ids.issubset(cases_by_id))
        self.assertTrue(cases_by_id["upload_mp4"].should_render)
        self.assertFalse(cases_by_id["upload_mp3"].should_render)
        self.assertEqual(cases_by_id["music_prompt"].expected_source_types, ["music"])
        self.assertEqual(cases_by_id["campaign_objective"].expected_source_types, ["campaign"])
        self.assertEqual(
            cases_by_id["youtube_public_url"].expected_fallback_message,
            runner.PLATFORM_BLOCKED_EXPECTED_MESSAGE,
        )

    def test_generate_payloads_preserve_source_type_contract(self) -> None:
        music_payload = runner.generate_payload_for_case(
            runner.MatrixCase(
                id="music_prompt",
                label="Music",
                kind="music",
                expected_mode="music",
                expected_source_types=["music"],
                prompt="Package this chorus.",
            )
        )
        campaign_payload = runner.generate_payload_for_case(
            runner.MatrixCase(
                id="campaign_objective",
                label="Campaign",
                kind="campaign",
                expected_mode="campaign",
                expected_source_types=["campaign"],
                prompt="Prepare a campaign package.",
            )
        )
        twitch_payload = runner.generate_payload_for_case(
            runner.MatrixCase(
                id="twitch_public_url",
                label="Twitch",
                kind="public_url",
                expected_mode="twitch",
                expected_source_types=["twitch", "stream", "url"],
                public_url="https://www.twitch.tv/videos/123",
            )
        )
        upload_payload = runner.generate_payload_for_case(
            runner.MatrixCase(
                id="upload_mp4",
                label="MP4",
                kind="upload",
                expected_mode="video",
                expected_source_types=["video_upload"],
            ),
            upload_file_id="upload_123",
        )

        self.assertEqual(music_payload["source_type"], "music")
        self.assertEqual(campaign_payload["source_type"], "campaign")
        self.assertEqual(campaign_payload["campaign_goal"], "Prepare a campaign package.")
        self.assertEqual(twitch_payload["source_type"], "twitch")
        self.assertEqual(upload_payload["upload_file_id"], "upload_123")

    def test_response_helpers_detect_media_and_raw_error_leaks(self) -> None:
        payload = {
            "preview_asset_url": "/generated/preview.mp4",
            "clips": [
                {"id": "clip_1", "clip_url": "https://cdn.example.com/clip.mp4"},
                {"id": "clip_2", "caption": "strategy only"},
                {"id": "clip_3", "download_url": "/generated/clip_3.mp3"},
            ],
        }

        self.assertEqual(runner.count_rendered_clips(payload), 2)
        self.assertEqual(
            runner.collect_media_urls(payload),
            ["/generated/clip_3.mp3", "/generated/preview.mp4", "https://cdn.example.com/clip.mp4"],
        )
        self.assertTrue(runner.source_type_matches("Video_Upload", ["video_upload"]))
        self.assertFalse(runner.source_type_matches("prompt", ["video_upload"]))
        self.assertTrue(runner.raw_error_leaked("yt-dlp says use --cookies-from-browser"))
        self.assertFalse(runner.raw_error_leaked(runner.PLATFORM_BLOCKED_EXPECTED_MESSAGE))

    def test_write_reports_records_optional_public_url_flags(self) -> None:
        original_paths = (runner.POC_DIR, runner.RESULT_JSON, runner.RESULT_MD)
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            runner.POC_DIR = root
            runner.RESULT_JSON = root / "source-matrix-results.json"
            runner.RESULT_MD = root / "source-matrix-results.md"
            try:
                runner.write_reports(
                    results=[
                        runner.MatrixResult(
                            id="prompt_only",
                            label="Prompt-only idea generation",
                            kind="prompt",
                            expected_mode="idea",
                            expected_source_types=["prompt"],
                            generate_accepted=True,
                            returned_source_type="prompt",
                            source_type_ok=True,
                            passed=True,
                        )
                    ],
                    base_url="http://127.0.0.1:8000",
                    run_client_prefix="test-client",
                    youtube_url="https://www.youtube.com/watch?v=blocked",
                    twitch_url=None,
                    unsupported_url="https://example.com/nope",
                )

                payload = json.loads(runner.RESULT_JSON.read_text(encoding="utf-8"))
                markdown = runner.RESULT_MD.read_text(encoding="utf-8")
            finally:
                runner.POC_DIR, runner.RESULT_JSON, runner.RESULT_MD = original_paths

        self.assertTrue(payload["youtube_url_tested"])
        self.assertFalse(payload["twitch_url_tested"])
        self.assertTrue(payload["unsupported_url_tested"])
        self.assertIn("Prompt-only idea generation", markdown)


if __name__ == "__main__":
    unittest.main()
