from __future__ import annotations

import os
import tempfile
import unittest
from unittest import mock

from app.core.config import Settings
from app.main import create_app
from app.models.schemas import SeedanceBackgroundRequest
from app.services.seedance_service import (
    SeedanceProviderError,
    build_seedance_payload,
    generate_seedance_background,
    seedance_available,
    submit_seedance_job,
)


class FakeSeedanceResponse:
    def __init__(self, payload: dict, status_code: int = 200) -> None:
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return self._payload


class FakeSeedanceClient:
    def __init__(self, *args, **kwargs) -> None:
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, traceback) -> None:
        return None

    async def post(self, *args, **kwargs):
        return FakeSeedanceResponse(
            {
                "job_id": "provider_job_123",
                "status": "submitted",
                "message": "accepted",
            }
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
            request=SeedanceBackgroundRequest(
                prompt="Mythic crimson background",
                duration_seconds=8,
                source_asset_id="asset_123",
            ),
        )
        self.assertEqual(payload["model"], "seedance-2.0-pro")
        self.assertEqual(payload["prompt"], "Mythic crimson background")
        self.assertEqual(payload["source_asset_id"], "asset_123")
        self.assertNotIn("reference_image_url", payload)

    async def test_seedance_background_generation_fails_cleanly_when_disabled(self) -> None:
        settings = self.build_settings()
        with self.assertRaises(SeedanceProviderError) as context:
            await generate_seedance_background(
                settings=settings,
                request=SeedanceBackgroundRequest(prompt="Living mythic scene"),
            )
        self.assertIn("disabled", str(context.exception).lower())

    async def test_submit_seedance_job_normalizes_and_persists_local_state(self) -> None:
        with tempfile.TemporaryDirectory() as generated_dir:
            settings = self.build_settings(
                SEEDANCE_ENABLED="true",
                SEEDANCE_API_KEY="seedance-key",
                SEEDANCE_BASE_URL="https://seedance.example.com",
                LWA_GENERATED_ASSETS_DIR=generated_dir,
            )
            with mock.patch("app.services.seedance_service.httpx.AsyncClient", FakeSeedanceClient):
                job = await submit_seedance_job(
                    settings=settings,
                    payload={"prompt": "Living mythic scene"},
                    job_id="seed_test",
                )

            self.assertEqual(job["job_id"], "seed_test")
            self.assertEqual(job["provider_job_id"], "provider_job_123")
            self.assertEqual(job["status"], "submitted")
            self.assertTrue(os.path.exists(os.path.join(generated_dir, "seedance", "jobs", "seed_test.json")))


class SeedanceRouterRegistrationTests(unittest.TestCase):
    def test_seedance_routes_are_registered(self) -> None:
        app = create_app()
        route_paths = {route.path for route in app.routes}
        self.assertIn("/v1/seedance/background", route_paths)
        self.assertIn("/v1/seedance/jobs/{job_id}", route_paths)


if __name__ == "__main__":
    unittest.main()
