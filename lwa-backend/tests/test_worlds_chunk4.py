from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from fastapi.testclient import TestClient

from app.main import app
from app.worlds.dependencies import get_demo_user_id, get_optional_actor_id, get_worlds_store
from app.worlds.pricing import quote_marketplace_fee
from app.worlds.repositories import WorldsStore


class WorldsChunk4Tests(unittest.TestCase):
    def setUp(self) -> None:
        self._temp_dir = tempfile.TemporaryDirectory()
        self.store = WorldsStore(str(Path(self._temp_dir.name) / "worlds.sqlite3"))
        app.dependency_overrides[get_worlds_store] = lambda: self.store
        app.dependency_overrides[get_demo_user_id] = lambda: "test_user"
        app.dependency_overrides[get_optional_actor_id] = lambda: "admin_user"
        self.client = TestClient(app)

    def tearDown(self) -> None:
        app.dependency_overrides.clear()
        self._temp_dir.cleanup()

    def test_marketplace_fee_quote_policy(self) -> None:
        free = quote_marketplace_fee(100, "free")
        pro = quote_marketplace_fee(100, "pro")

        self.assertEqual(free["platform_fee_amount"], 30)
        self.assertEqual(free["net_amount"], 70)
        self.assertEqual(pro["platform_fee_amount"], 20)
        self.assertEqual(pro["net_amount"], 80)

    def test_billing_plans_and_entitlement_routes(self) -> None:
        plans = self.client.get("/worlds/billing/plans")
        entitlement = self.client.get("/worlds/billing/entitlement/me")

        self.assertEqual(plans.status_code, 200)
        self.assertTrue(any(item["plan_key"] == "free" for item in plans.json()))
        self.assertEqual(entitlement.status_code, 200)
        self.assertEqual(entitlement.json()["plan_key"], "free")

    def test_admin_entitlement_grant(self) -> None:
        response = self.client.post(
            "/worlds/admin/billing/entitlements/grant",
            json={
                "user_id": "test_user",
                "plan_key": "pro",
                "source": "manual",
                "reason": "Unit test grant.",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["plan_key"], "pro")

    def test_credit_routes_grant_spend_and_list(self) -> None:
        grant = self.client.post(
            "/worlds/admin/credits/grant",
            json={"user_id": "test_user", "amount": 50, "reason": "Testing grant."},
        )
        self.assertEqual(grant.status_code, 200)
        self.assertGreaterEqual(grant.json()["balance"], 50)

        spend = self.client.post(
            "/worlds/credits/spend",
            json={"amount": 10, "feature_key": "clip_generation", "reason": "Testing spend."},
        )
        self.assertEqual(spend.status_code, 200)

        transactions = self.client.get("/worlds/credits/transactions/me")
        self.assertEqual(transactions.status_code, 200)
        self.assertTrue(any(item["transaction_type"] == "spend" for item in transactions.json()))

    def test_invalid_credit_spend_is_rejected(self) -> None:
        response = self.client.post(
            "/worlds/credits/spend",
            json={"amount": -1, "feature_key": "clip_generation"},
        )

        self.assertEqual(response.status_code, 422)

    def test_submission_approval_records_earning_event_without_payout(self) -> None:
        campaign = self.client.post(
            "/worlds/marketplace/campaigns",
            json={
                "title": "Founder interview shorts",
                "description": "Create clips from a founder interview.",
                "target_platform": "TikTok",
                "source_type": "video_url",
                "budget_amount": 300,
                "clip_count": 10,
            },
        )
        self.assertEqual(campaign.status_code, 200)

        submission = self.client.post(
            "/worlds/marketplace/submissions",
            json={
                "campaign_public_id": campaign.json()["public_id"],
                "title": "Approved clip",
                "estimated_earnings_amount": 100,
                "rights_confirmed": True,
            },
        )
        self.assertEqual(submission.status_code, 200)

        approved = self.client.post(
            f"/worlds/marketplace/submissions/{submission.json()['public_id']}/review",
            json={"action": "approve", "review_note": "Approved."},
        )
        self.assertEqual(approved.status_code, 200)

        account = self.client.get("/worlds/earnings/account/me")
        events = self.client.get("/worlds/earnings/events/me")
        payouts = self.client.get("/worlds/payouts/placeholders/me")

        self.assertEqual(account.status_code, 200)
        self.assertEqual(account.json()["approved_amount"], 80)
        self.assertEqual(events.status_code, 200)
        self.assertEqual(events.json()[0]["net_amount"], 80)
        self.assertEqual(payouts.status_code, 200)
        self.assertEqual(payouts.json(), [])

    def test_stripe_connect_readiness_is_not_ready(self) -> None:
        response = self.client.get("/worlds/payouts/stripe-connect/readiness")

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["ready"])


if __name__ == "__main__":
    unittest.main()
