from __future__ import annotations

import unittest

from fastapi.testclient import TestClient

from app.main import create_app
from app.services.capability_registry import (
    capability_catalog,
    capability_status_payload,
    clear_capability_cache,
    get_capability,
    public_claim_payload,
    railway_service_plan,
)


class CapabilityRegistryServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        clear_capability_cache()

    def test_capability_catalog_counts_are_consistent(self) -> None:
        catalog = capability_catalog()

        self.assertGreater(catalog.count, 0)
        self.assertEqual(catalog.count, len(catalog.items))
        self.assertEqual(sum(catalog.status_counts.values()), catalog.count)
        self.assertEqual(sum(catalog.public_claim_counts.values()), catalog.count)

    def test_get_capability_returns_expected_record(self) -> None:
        capability = get_capability("capability_registry_api")

        self.assertIsNotNone(capability)
        self.assertEqual(capability.id, "capability_registry_api")
        self.assertEqual(capability.status, "live")

    def test_status_payload_filters_to_requested_status(self) -> None:
        payload = capability_status_payload("partial")

        self.assertGreater(payload.count, 0)
        self.assertTrue(all(item.status == "partial" for item in payload.items))

    def test_public_claim_payload_groups_records(self) -> None:
        payload = public_claim_payload()

        self.assertEqual(payload.summary["allowed"], len(payload.allowed))
        self.assertEqual(payload.summary["careful"], len(payload.careful))
        self.assertEqual(payload.summary["not_allowed"], len(payload.not_allowed))
        self.assertGreater(payload.summary["not_allowed"], 0)

    def test_railway_plan_includes_capability_links(self) -> None:
        plan = railway_service_plan()

        self.assertTrue(any(service.service_name == "lwa-backend" for service in plan.current_services))
        self.assertTrue(any(service.service_name == "lwa-webhooks" for service in plan.future_services))
        webhooks = next(service for service in plan.future_services if service.service_name == "lwa-webhooks")
        self.assertIn("whop_campaign_browsing", webhooks.capability_ids)


class CapabilityRegistryRouteTests(unittest.TestCase):
    def setUp(self) -> None:
        clear_capability_cache()
        self.client = TestClient(create_app())

    def tearDown(self) -> None:
        self.client.close()

    def test_list_capabilities_endpoint(self) -> None:
        response = self.client.get("/v1/capabilities")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("items", payload)
        self.assertIn("status_counts", payload)
        self.assertGreater(payload["count"], 0)

    def test_get_capability_detail_endpoint(self) -> None:
        response = self.client.get("/v1/capabilities/capability_registry_api")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["id"], "capability_registry_api")
        self.assertEqual(payload["status"], "live")

    def test_get_capabilities_by_status_endpoint(self) -> None:
        response = self.client.get("/v1/capabilities/status/live")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "live")
        self.assertTrue(all(item["status"] == "live" for item in payload["items"]))

    def test_invalid_status_endpoint_returns_404(self) -> None:
        response = self.client.get("/v1/capabilities/status/not-real")

        self.assertEqual(response.status_code, 404)

    def test_public_claims_endpoint(self) -> None:
        response = self.client.get("/v1/capabilities/public-claims")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("allowed", payload)
        self.assertIn("careful", payload)
        self.assertIn("not_allowed", payload)
        self.assertGreater(payload["summary"]["not_allowed"], 0)

    def test_railway_plan_endpoint(self) -> None:
        response = self.client.get("/v1/capabilities/railway-plan")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("current_services", payload)
        self.assertIn("future_services", payload)
        self.assertTrue(any(item["service_name"] == "lwa-backend" for item in payload["current_services"]))


if __name__ == "__main__":
    unittest.main()
