from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from app.core.config import Settings
from app.models.schemas import CaptionModes, ClipResult
from app.services.caption_artifacts import create_caption_artifacts


class CaptionArtifactTests(unittest.TestCase):
    def test_platform_specific_caption_artifacts_are_written_with_urls(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            settings = Settings()
            settings.generated_assets_dir = temp_dir
            settings.api_base_url = "https://backend.example.com"

            clip = ClipResult(
                id="clip_caption_001",
                title="Lead clip",
                hook="Stop posting random clips.",
                caption="Use this as the main caption.",
                transcript_excerpt="Stop posting random clips if you want viewers to stay for the payoff.",
                start_time="00:03",
                end_time="00:18",
                score=90,
                caption_modes=CaptionModes(
                    primary="Use this as the main caption.",
                    short="Stop random clips. Test this format.",
                    story="This is the clip I would post after the lead lands.",
                    educational="Here is the exact retention breakdown behind this moment.",
                    controversial="Most creators still cut this part wrong.",
                ),
            )

            artifacts = create_caption_artifacts(
                settings=settings,
                public_base_url="https://backend.example.com",
                request_id="req_caption_001",
                clip=clip,
                target_platform="LinkedIn",
            )

            self.assertTrue(artifacts["caption_txt_url"])
            self.assertTrue(artifacts["caption_srt_url"])
            self.assertTrue(artifacts["caption_vtt_url"])
            self.assertEqual(artifacts["export_filename"], "lead-clip-linkedin.mp4")

            caption_dir = Path(temp_dir) / "req_caption_001" / "captions" / "clip-caption-001"
            txt_files = list(caption_dir.glob("*.txt"))
            srt_files = list(caption_dir.glob("*.srt"))
            vtt_files = list(caption_dir.glob("*.vtt"))

            self.assertEqual(len(txt_files), 1)
            self.assertEqual(len(srt_files), 1)
            self.assertEqual(len(vtt_files), 1)
            self.assertIn("exact retention breakdown", txt_files[0].read_text(encoding="utf-8"))
            self.assertIn("WEBVTT", vtt_files[0].read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
