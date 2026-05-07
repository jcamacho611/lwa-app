from __future__ import annotations

import unittest

from fastapi.testclient import TestClient

from app.main import create_app
from app.engines.registry import get_engine, get_engine_health, get_engine_registry, run_engine_demo


class BackendEngineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app()
        self.client = TestClient(self.app)

    def test_registry_returns_all_ten_engines(self) -> None:
        registry = get_engine_registry()
        self.assertEqual(registry["count"], 10)
        self.assertEqual(
            set(registry["engines"].keys()),
            {
                "creator",
                "brain",
                "render",
                "marketplace",
                "wallet_entitlements",
                "proof_history",
                "world_game",
                "safety",
                "social_distribution",
                "operator_admin",
            },
        )

    def test_each_engine_has_health(self) -> None:
        health = get_engine_health()
        self.assertEqual(health["count"], 10)
        self.assertEqual(len(health["engines"]), 10)
        for engine_id, record in health["engines"].items():
            self.assertEqual(record["engine_id"], engine_id)
            self.assertIn("healthy", record)
            self.assertIn("status", record)

    def test_invalid_engine_id_returns_safe_error(self) -> None:
        response = self.client.get("/engines/not-real")
        self.assertEqual(response.status_code, 404)
        self.assertIn("Engine not found", response.json()["detail"])

        demo_response = self.client.post("/engines/not-real/demo", json={"payload": {}})
        self.assertEqual(demo_response.status_code, 404)

    def test_demo_run_works_for_each_engine(self) -> None:
        for engine_id in get_engine_registry()["engines"].keys():
            result = run_engine_demo(engine_id, {"source": "demo", "request_type": "clip_review"})
            self.assertEqual(result["engine_id"], engine_id)
            self.assertTrue(result["summary"])
            self.assertIn("output", result)
            self.assertIn("warnings", result)
            self.assertIn("next_required_integrations", result)

    def test_no_engine_claims_production_ready_by_default(self) -> None:
        statuses = {record["status"] for record in get_engine_registry()["engines"].values()}
        self.assertNotIn("production_ready", statuses)

    def test_wallet_engine_does_not_execute_payouts(self) -> None:
        result = run_engine_demo("wallet_entitlements", {"credits": 25})
        self.assertFalse(result["output"]["payouts_executed"])
        self.assertFalse(result["output"]["payment_mutation"])

    def test_social_engine_does_not_post_externally(self) -> None:
        result = run_engine_demo("social_distribution", {"destination": "tiktok"})
        self.assertFalse(result["output"]["external_posted"])
        self.assertFalse(result["output"]["publish_allowed"])

    def test_render_engine_does_not_call_paid_providers(self) -> None:
        result = run_engine_demo("render", {"render_requested": True})
        self.assertFalse(result["output"]["paid_provider_called"])
        self.assertTrue(result["output"]["strategy_only"])

    def test_generate_route_untouched(self) -> None:
        paths = {route.path for route in self.app.routes}
        self.assertIn("/generate", paths)

    def test_known_engine_lookup(self) -> None:
        engine = get_engine("creator")
        self.assertIsNotNone(engine)
        self.assertEqual(engine.engine_id, "creator")


if __name__ == "__main__":
    unittest.main()
