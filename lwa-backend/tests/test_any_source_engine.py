from __future__ import annotations

import unittest

from app.api.routes.generate import resolve_request_source
from app.models.schemas import ProcessRequest
from app.services.source_ingest import (
    build_strategy_source_context,
    infer_source_type,
    normalize_source_type,
    source_type_uses_media_pipeline,
    source_value_for_request,
)


class AnySourceEngineTests(unittest.TestCase):
    def test_source_url_alias_keeps_legacy_video_url_contract(self) -> None:
        request = ProcessRequest(source_url="https://example.com/video.mp4")

        self.assertEqual(request.video_url, "https://example.com/video.mp4")
        self.assertEqual(source_value_for_request(request), "https://example.com/video.mp4")

    def test_prompt_only_source_resolves_without_media_url(self) -> None:
        request = ProcessRequest(prompt="Make three launch clips for a founder update.")
        resolved, source_path = resolve_request_source(request=request, current_user=None, base_url="https://api.example.com")

        self.assertIsNone(source_path)
        self.assertEqual(resolved.source_type, "prompt")
        self.assertEqual(source_value_for_request(resolved), "Make three launch clips for a founder update.")
        self.assertFalse(source_type_uses_media_pipeline(resolved.source_type or "", has_source_path=False, source_url=resolved.video_url))

    def test_campaign_objective_source_resolves_without_media_url(self) -> None:
        request = ProcessRequest(campaign_goal="Sell a custom clip pack to streamers", allowed_platforms=["TikTok", "Twitch"])
        resolved, source_path = resolve_request_source(request=request, current_user=None, base_url="https://api.example.com")

        self.assertIsNone(source_path)
        self.assertEqual(resolved.source_type, "campaign")
        self.assertEqual(source_value_for_request(resolved), "Sell a custom clip pack to streamers")

    def test_audio_source_with_prompt_can_fall_back_to_strategy_package(self) -> None:
        request = ProcessRequest(source_type="audio", prompt="Package this podcast intro into three clip concepts.")
        resolved, source_path = resolve_request_source(request=request, current_user=None, base_url="https://api.example.com")

        self.assertIsNone(source_path)
        self.assertEqual(resolved.source_type, "audio")
        self.assertFalse(source_type_uses_media_pipeline(resolved.source_type or "", has_source_path=False, source_url=resolved.video_url))

    def test_twitch_source_url_gets_twitch_source_type_and_media_pipeline(self) -> None:
        request = ProcessRequest(source_url="https://www.twitch.tv/videos/123456789")
        resolved, source_path = resolve_request_source(request=request, current_user=None, base_url="https://api.example.com")

        self.assertIsNone(source_path)
        self.assertEqual(resolved.source_type, "twitch")
        self.assertEqual(resolved.video_url, "https://www.twitch.tv/videos/123456789")
        self.assertTrue(source_type_uses_media_pipeline(resolved.source_type or "", has_source_path=False, source_url=resolved.video_url))

    def test_source_type_aliases_and_unknown_fallback_are_safe(self) -> None:
        self.assertEqual(normalize_source_type("idea"), "prompt")
        self.assertEqual(normalize_source_type("twitch-vod"), "twitch")
        self.assertEqual(normalize_source_type("campaign_objective"), "campaign")
        self.assertEqual(normalize_source_type("not-a-real-source"), "unknown")

    def test_strategy_context_preserves_music_prompt_without_fake_render(self) -> None:
        request = ProcessRequest(source_type="music", prompt="Turn this chorus idea into a short-form promo package.")
        source_type = infer_source_type(request)
        context = build_strategy_source_context(
            request=request,
            source_type=source_type,
            source_value=source_value_for_request(request),
        )

        self.assertEqual(context.source_type, "music")
        self.assertEqual(context.source_platform, "Music")
        self.assertEqual(context.processing_mode, "strategy_only")
        self.assertEqual(context.clip_seeds, [])
        self.assertIn("strategy package", context.visual_summary or "")


if __name__ == "__main__":
    unittest.main()
