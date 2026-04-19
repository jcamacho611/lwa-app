from __future__ import annotations

import os
import unittest
from unittest import mock

from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app
from app.services.clip_service import provider_health, seedance_status


class ProviderHealthTests(unittest.TestCase):
    def build_settings(self, **overrides: str) -> Settings:
        base = {
            "OPENAI_API_KEY": "",
            "LWA_ENABLE_ANTHROPIC": "false",
            "ANTHROPIC_API_KEY": "",
            "SEEDANCE_ENABLED": "false",
            "SEEDANCE_API_KEY": "",
            "SEEDANCE_BASE_URL": "",
        }
        base.update(overrides)
        with mock.patch.dict(os.environ, base, clear=False):
            return Settings()

    def test_health_route_exposes_dependencies_and_providers(self) -> None:
        client = TestClient(create_app())
        try:
            response = client.get("/health")
        finally:
            client.close()

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("dependencies", payload)
        self.assertIn("providers", payload)
        self.assertIn("seedance", payload["providers"])

    def test_seedance_status_is_honest_when_disabled(self) -> None:
        settings = self.build_settings()
        status = seedance_status(settings)

        self.assertFalse(status["enabled"])
        self.assertFalse(status["configured"])
        self.assertEqual(status["status"], "disabled")
        self.assertIn("internal visual engine", status["message"].lower())

    def test_seedance_status_reports_adapter_only_when_configured(self) -> None:
        settings = self.build_settings(
            SEEDANCE_ENABLED="true",
            SEEDANCE_API_KEY="seedance-key",
            SEEDANCE_BASE_URL="https://seedance.example.com",
        )
        status = seedance_status(settings)
        providers = provider_health(settings)

        self.assertTrue(status["enabled"])
        self.assertTrue(status["configured"])
        self.assertTrue(status["adapter_only"])
        self.assertEqual(status["status"], "adapter-only")
        self.assertEqual(providers["seedance"]["status"], "adapter-only")

if __name__ == "__main__":
    unittest.main()
