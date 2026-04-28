from __future__ import annotations

import unittest

from app.core.config import Settings
from app.services.visual_render_provider import (
    VisualRenderPayload,
    render_visual_clip,
    resolve_visual_render_provider_state,
    visual_render_provider_status,
)


class VisualRenderProviderTests(unittest.IsolatedAsyncioTestCase):
    def test_provider_state_reports_disabled(self) -> None:
        settings = Settings()
        settings.visual_engine_enabled = False
        settings.visual_engine_api_key = ""

        self.assertEqual(resolve_visual_render_provider_state(settings), "disabled")
        status = visual_render_provider_status(settings)
        self.assertEqual(status["provider_state"], "disabled")
        self.assertEqual(status["render_provider"], "lwa_visual_engine")

    def test_provider_state_reports_missing_key(self) -> None:
        settings = Settings()
        settings.visual_engine_enabled = True
        settings.visual_engine_api_key = ""

        self.assertEqual(resolve_visual_render_provider_state(settings), "missing-key")
        status = visual_render_provider_status(settings)
        self.assertEqual(status["provider_state"], "missing-key")
        self.assertFalse(status["configured"])

    async def test_render_visual_clip_returns_failed_when_provider_not_wired(self) -> None:
        settings = Settings()
        settings.visual_engine_enabled = True
        settings.visual_engine_api_key = "env-var-present"

        result = await render_visual_clip(
            settings=settings,
            payload=VisualRenderPayload(
                clip_id="clip_001",
                title="Lead clip",
                hook="Stop the scroll fast.",
                caption="Strategy first.",
                visual_engine_prompt="Build a short-form opener.",
                motion_prompt="Punch in quickly.",
                target_platform="TikTok",
            ),
        )

        self.assertEqual(result.provider_state, "failed")
        self.assertTrue(result.attempted)
        self.assertFalse(result.success)
        self.assertEqual(result.rendered_by, "LWA Omega Visual Engine")
        self.assertIn("not wired yet", (result.error or "").lower())


if __name__ == "__main__":
    unittest.main()
