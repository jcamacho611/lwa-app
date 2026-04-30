from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from fastapi.testclient import TestClient

from app.main import app
from app.worlds.dependencies import get_demo_user_id, get_optional_actor_id, get_worlds_store
from app.worlds.models import SubmissionStatus
from app.worlds.repositories import WorldsStore
from app.worlds.services import MarketplaceService
from app.worlds.schemas import CampaignCreateRequest, SubmissionCreateRequest
from app.worlds.xp import FIRST_CAMPAIGN_BADGE, XpService


class WorldsBackendTests(unittest.TestCase):
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

    def create_campaign(self) -> str:
        response = self.client.post(
            "/worlds/marketplace/campaigns",
            json={
                "title": "Founder interview shorts",
                "description": "Create clips from a founder interview.",
                "target_platform": "TikTok",
                "source_type": "video_url",
                "budget_amount": 300,
                "clip_count": 10,
                "rights_required": "Buyer receives usage rights for approved deliverables.",
            },
        )
        self.assertEqual(response.status_code, 200)
        return response.json()["public_id"]

    def test_worlds_health_route_exists(self) -> None:
        response = self.client.get("/worlds/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")
        self.assertEqual(response.json()["service"], "lwa-worlds")

    def test_create_campaign_validates_budget_and_records_progress(self) -> None:
        bad_response = self.client.post(
            "/worlds/marketplace/campaigns",
            json={
                "title": "Bad budget",
                "description": "Should fail",
                "target_platform": "TikTok",
                "source_type": "video_url",
                "budget_amount": 0,
                "clip_count": 5,
                "rights_required": "Usage rights required.",
            },
        )
        self.assertEqual(bad_response.status_code, 400)

        campaign_id = self.create_campaign()
        profile = self.client.get("/worlds/profile/me").json()
        ledger = self.client.get("/worlds/ledger/me").json()

        self.assertTrue(campaign_id.startswith("camp_"))
        self.assertEqual(profile["creator_reputation"], 5)
        self.assertEqual(profile["marketplace_reputation"], 5)
        self.assertTrue(any(entry["event_type"] == "campaign_created" for entry in ledger))
        self.assertTrue(any(entry["event_type"] == "xp_awarded" for entry in ledger))
        self.assertTrue(any(entry["event_type"] == "badge_awarded" for entry in ledger))

    def test_submission_requires_rights_and_review_awards_once(self) -> None:
        campaign_id = self.create_campaign()
        rejected = self.client.post(
            "/worlds/marketplace/submissions",
            json={
                "campaign_public_id": campaign_id,
                "title": "Test submission",
                "hook": "Hook",
                "caption": "Caption",
                "estimated_earnings_amount": 25,
                "rights_confirmed": False,
            },
        )
        self.assertEqual(rejected.status_code, 400)

        submission_response = self.client.post(
            "/worlds/marketplace/submissions",
            json={
                "campaign_public_id": campaign_id,
                "title": "Test submission",
                "hook": "Hook",
                "caption": "Caption",
                "estimated_earnings_amount": 25,
                "rights_confirmed": True,
            },
        )
        self.assertEqual(submission_response.status_code, 200)
        submission_id = submission_response.json()["public_id"]

        review_response = self.client.post(
            f"/worlds/marketplace/submissions/{submission_id}/review",
            json={"action": "approve", "review_note": "Approved in test."},
        )
        self.assertEqual(review_response.status_code, 200)
        self.assertEqual(review_response.json()["status"], "approved")

        repeat_review = self.client.post(
            f"/worlds/marketplace/submissions/{submission_id}/review",
            json={"action": "approve", "review_note": "Approved again."},
        )
        self.assertEqual(repeat_review.status_code, 200)

        with self.store.connect() as connection:
            badge_count = connection.execute(
                """
                SELECT COUNT(*) FROM user_badges
                WHERE user_id = ? AND badge_public_id = ?
                """,
                ("test_user", "badge_approved_earner"),
            ).fetchone()[0]
            approval_rep_events = connection.execute(
                """
                SELECT COUNT(*) FROM reputation_events
                WHERE user_id = ? AND source_public_id = ? AND reason = ?
                """,
                ("test_user", submission_id, "Marketplace submission approved"),
            ).fetchone()[0]

        self.assertEqual(badge_count, 1)
        self.assertEqual(approval_rep_events, 1)

    def test_invalid_review_action_fails(self) -> None:
        campaign_id = self.create_campaign()
        submission = self.client.post(
            "/worlds/marketplace/submissions",
            json={
                "campaign_public_id": campaign_id,
                "title": "Test submission",
                "hook": "Hook",
                "caption": "Caption",
                "estimated_earnings_amount": 25,
                "rights_confirmed": True,
            },
        ).json()

        response = self.client.post(
            f"/worlds/marketplace/submissions/{submission['public_id']}/review",
            json={"action": "pay_now"},
        )

        self.assertEqual(response.status_code, 400)

    def test_forbidden_paid_submission_transition_fails(self) -> None:
        service = MarketplaceService(self.store)
        campaign = service.create_campaign(
            payload=CampaignCreateRequest(
                title="Direct service campaign",
                description="Service path.",
                budget_amount=100,
                clip_count=1,
            ),
            buyer_user_id="buyer",
        )
        submission = service.create_submission(
            payload=SubmissionCreateRequest(
                campaign_public_id=campaign.public_id,
                title="Submission",
                rights_confirmed=True,
            ),
            clipper_user_id="clipper",
        )
        submission.status = SubmissionStatus.paid
        service.submissions.save(submission)

        response = self.client.post(
            f"/worlds/marketplace/submissions/{submission.public_id}/review",
            json={"action": "reject"},
        )

        self.assertEqual(response.status_code, 409)

    def test_badge_award_is_idempotent(self) -> None:
        service = XpService(self.store)

        first = service.award_badge_once(user_id="test_user", badge_data=FIRST_CAMPAIGN_BADGE)
        second = service.award_badge_once(user_id="test_user", badge_data=FIRST_CAMPAIGN_BADGE)

        self.assertTrue(first)
        self.assertFalse(second)

    def test_integrations_sync_and_admin_audit_log(self) -> None:
        self.create_campaign()

        integrations = self.client.post("/worlds/integrations/sync")
        audit_log = self.client.get("/worlds/admin/audit-log")

        self.assertEqual(integrations.status_code, 200)
        self.assertTrue(any(item["integration_key"] == "openai" for item in integrations.json()))
        self.assertEqual(audit_log.status_code, 200)
        self.assertTrue(any(item["action_type"] == "campaign_created" for item in audit_log.json()))


if __name__ == "__main__":
    unittest.main()
