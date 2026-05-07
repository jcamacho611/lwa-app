"""Tests for app.services.engine_service_app — the Railway-ready
single-engine FastAPI service.

These tests use FastAPI's TestClient and exercise the four required
routes: GET /health, GET /engine, GET /engine/health, POST /engine/demo,
plus the root banner.
"""

from __future__ import annotations

import os
import unittest

from fastapi.testclient import TestClient

from app.services.engine_runtime import ENGINE_SERVICE_ENV_VAR
from app.services.engine_service_app import create_engine_service_app


class _EngineEnv:
    """Context manager scoping ENGINE_SERVICE_ENV_VAR for a test block."""

    def __init__(self, value: str | None) -> None:
        self.value = value
        self.previous: str | None = None
        self.had_previous: bool = False

    def __enter__(self) -> "_EngineEnv":
        self.had_previous = ENGINE_SERVICE_ENV_VAR in os.environ
        self.previous = os.environ.get(ENGINE_SERVICE_ENV_VAR)
        if self.value is None:
            os.environ.pop(ENGINE_SERVICE_ENV_VAR, None)
        else:
            os.environ[ENGINE_SERVICE_ENV_VAR] = self.value
        return self

    def __exit__(self, *_: object) -> None:
        if self.had_previous:
            assert self.previous is not None
            os.environ[ENGINE_SERVICE_ENV_VAR] = self.previous
        else:
            os.environ.pop(ENGINE_SERVICE_ENV_VAR, None)


class EngineServiceAppRouteTests(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_engine_service_app()
        self.client = TestClient(self.app)

    def test_root_banner_with_default_engine(self) -> None:
        with _EngineEnv(None):
            response = self.client.get("/")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["service"], "lwa-engine-service")
            self.assertEqual(data["selected_engine_id"], "operator_admin")
            self.assertIn("/engine/demo", data["routes"])

    def test_health_endpoint_never_raises_for_invalid_selection(self) -> None:
        with _EngineEnv("not_a_real_engine"):
            response = self.client.get("/health")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["status"], "ok")
            self.assertIsNone(data["selected_engine_id"])
            self.assertIn("Invalid", data["selection_error"] or "")

    def test_engine_endpoint_returns_record(self) -> None:
        with _EngineEnv("creator"):
            response = self.client.get("/engine")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["engine_id"], "creator")
            self.assertIn("capabilities", data)
            self.assertIn("health", data)

    def test_engine_health_endpoint_returns_health_dict(self) -> None:
        with _EngineEnv("brain"):
            response = self.client.get("/engine/health")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["engine_id"], "brain")
            self.assertIn("healthy", data)
            self.assertIn("warnings", data)

    def test_engine_endpoint_returns_503_on_invalid_selection(self) -> None:
        with _EngineEnv("not_a_real_engine"):
            response = self.client.get("/engine")
            self.assertEqual(response.status_code, 503)

    def test_engine_demo_post_returns_safe_dict(self) -> None:
        with _EngineEnv("world_game"):
            response = self.client.post("/engine/demo", json={"current_realm": "signal_realm"})
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["engine_id"], "world_game")
            self.assertIn("output", data)
            self.assertEqual(data["output"]["mission"], "Signal Sprint")

    def test_engine_demo_with_no_body(self) -> None:
        with _EngineEnv("operator_admin"):
            response = self.client.post("/engine/demo")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["engine_id"], "operator_admin")

    def test_engine_demo_invalid_selection_returns_503(self) -> None:
        with _EngineEnv("nope"):
            response = self.client.post("/engine/demo", json={})
            self.assertEqual(response.status_code, 503)


class EngineServiceAppSafetyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_engine_service_app()
        self.client = TestClient(self.app)

    def test_wallet_demo_response_does_not_execute_payouts(self) -> None:
        with _EngineEnv("wallet_entitlements"):
            response = self.client.post("/engine/demo", json={"credits": 50})
            self.assertEqual(response.status_code, 200)
            output = response.json()["output"]
            self.assertFalse(output["payouts_executed"])
            self.assertFalse(output["payment_mutation"])

    def test_social_demo_response_does_not_post_externally(self) -> None:
        with _EngineEnv("social_distribution"):
            response = self.client.post("/engine/demo", json={"destination": "tiktok"})
            self.assertEqual(response.status_code, 200)
            output = response.json()["output"]
            self.assertFalse(output["external_posted"])
            self.assertTrue(output["manual_review_required"])

    def test_render_demo_response_does_not_call_paid_providers(self) -> None:
        with _EngineEnv("render"):
            response = self.client.post("/engine/demo", json={"render_requested": True})
            self.assertEqual(response.status_code, 200)
            output = response.json()["output"]
            self.assertFalse(output["paid_provider_called"])
            self.assertTrue(output["strategy_only"])


if __name__ == "__main__":
    unittest.main()
