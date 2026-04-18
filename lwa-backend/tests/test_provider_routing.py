from __future__ import annotations

import os
import unittest
from unittest import mock

from app.core.config import Settings
from app.generation import determine_provider
from app.services.ai_service import resolve_attention_mode


class ProviderRoutingTests(unittest.TestCase):
    def build_settings(self, **overrides: str) -> Settings:
        base = {
            "LWA_AI_PROVIDER": "auto",
            "OPENAI_API_KEY": "",
            "OLLAMA_BASE_URL": "",
            "ANTHROPIC_API_KEY": "",
            "LWA_ENABLE_ANTHROPIC": "true",
            "LWA_PREMIUM_REASONING_PROVIDER": "anthropic",
        }
        base.update(overrides)
        with mock.patch.dict(os.environ, base, clear=False):
            return Settings()

    def test_auto_prefers_anthropic_when_enabled_and_available(self) -> None:
        settings = self.build_settings(
            ANTHROPIC_API_KEY="test-anthropic-key",
            OPENAI_API_KEY="test-openai-key",
        )
        with mock.patch("app.services.anthropic_service.Anthropic", new=object):
            self.assertEqual(determine_provider(settings), "anthropic")
            self.assertEqual(resolve_attention_mode(settings), "anthropic")

    def test_auto_falls_back_to_openai_when_anthropic_is_unavailable(self) -> None:
        settings = self.build_settings(OPENAI_API_KEY="test-openai-key")
        with mock.patch("app.services.anthropic_service.Anthropic", new=None):
            self.assertEqual(determine_provider(settings), "openai")
            self.assertEqual(resolve_attention_mode(settings), "openai")

    def test_auto_falls_back_cleanly_when_no_provider_is_configured(self) -> None:
        settings = self.build_settings()
        with mock.patch("app.services.anthropic_service.Anthropic", new=None):
            self.assertEqual(determine_provider(settings), "heuristic")
            self.assertEqual(resolve_attention_mode(settings), "fallback")


if __name__ == "__main__":
    unittest.main()
