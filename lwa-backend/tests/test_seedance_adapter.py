from __future__ import annotations

import os
import unittest
from unittest import mock

from app.core.config import Settings
from app.main import create_app
from app.models.schemas import GenerationBackgroundRequest
from app.services.seedance_service import (
    SeedanceProviderError,
    build_seedance_payload,
    generate_seedance_background,
    seedance_available,
)


class SeedanceAdapterTests(unittest.IsolatedAsyncioTestCase):
    def build_settings(self, **overrides: str) -> Settings:
        base = {
            "SEEDANCE_ENABLED": "false",
            "SEEDANCE_API_KEY": "",
            "SEEDANCE_BASE_URL": "",
            "SEEDANCE_MODEL": "seedance-2.0",
        }
        base.update(overrides)
        with mock.patch.dict(os.environ, base, clear=False):
            return Settings()

    async def test_seedance_is_disabled_by_default(self) -> None:
        settings = self.build_settings()
        self.assertFalse(seedance_available(settings))

    async def test_build_seedance_payload_uses_configured_model(self) -> None:
        settings = self.build_settings(
            SEEDANCE_ENABLED="true",
            SEEDANCE_API_KEY="seedance-key",
            SEEDANCE_BASE_URL="https://seedance.example.com",
            SEEDANCE_MODEL="seedance-2.0-pro",
        )
        payload = build_seedance_payload(
            settings=settings,
            request=GenerationBackgroundRequest(
                prompt="Mythic crimson background",
                duration_seconds=8,
                source_asset_id="asset_123",
            ),
        )
        self.assertEqual(payload["model"], "seedance-2.0-pro")
        self.assertEqual(payload["prompt"], "Mythic crimson background")
        self.assertEqual(payload["source_asset_id"], "asset_123")
        self.assertNotIn("reference_image_url", payload)

    async def test_seedance_background_generation_fails_cleanly_until_contract_is_verified(self) -> None:
        settings = self.build_settings(
            SEEDANCE_ENABLED="true",
            SEEDANCE_API_KEY="seedance-key",
            SEEDANCE_BASE_URL="https://seedance.example.com",
        )
        with self.assertRaises(SeedanceProviderError) as context:
            await generate_seedance_background(
                settings=settings,
                request=GenerationBackgroundRequest(prompt="Living mythic scene"),
            )
        self.assertIn("contract", str(context.exception).lower())


class SeedanceRouterRegistrationTests(unittest.TestCase):
    def test_seedance_routes_are_registered(self) -> None:
        app = create_app()
        route_paths = {route.path for route in app.routes}
        self.assertIn("/v1/seedance/background", route_paths)
        self.assertIn("/v1/seedance/jobs/{job_id}", route_paths)


if __name__ == "__main__":
    unittest.main()
