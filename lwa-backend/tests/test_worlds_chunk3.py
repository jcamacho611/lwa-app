from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from fastapi.testclient import TestClient

from app.main import app
from app.worlds.dependencies import get_demo_user_id, get_optional_actor_id, get_worlds_store
from app.worlds.repositories import WorldsStore


class WorldsChunk3Tests(unittest.TestCase):
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

    def create_ugc_asset(self) -> dict:
        response = self.client.post(
            "/worlds/ugc/assets",
            json={
                "title": "Gold Thread Hook Pack",
                "asset_type": "Hook Pack",
                "description": "Original hook templates for creator campaigns.",
                "price_amount": 19,
                "license_summary": "Template usage license.",
                "rights_confirmed": True,
            },
        )
        self.assertEqual(response.status_code, 200)
        return response.json()

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

    def test_ugc_asset_requires_rights_confirmation(self) -> None:
        response = self.client.post(
            "/worlds/ugc/assets",
            json={
                "title": "Unsafe UGC Asset",
                "asset_type": "Hook Pack",
                "description": "Missing rights confirmation.",
                "price_amount": 0,
                "rights_confirmed": False,
            },
        )

        self.assertEqual(response.status_code, 400)

    def test_create_submit_and_review_ugc_asset(self) -> None:
        asset = self.create_ugc_asset()
        self.assertEqual(asset["status"], "draft")
        self.assertTrue(asset["rights_confirmed"])

        submit = self.client.post(f"/worlds/ugc/assets/{asset['public_id']}/submit-review")
        self.assertEqual(submit.status_code, 200)
        self.assertEqual(submit.json()["status"], "pending_review")

        queue = self.client.get("/worlds/admin/moderation")
        self.assertEqual(queue.status_code, 200)
        self.assertEqual(len(queue.json()), 1)

        reviewed = self.client.post(
            f"/worlds/ugc/assets/{asset['public_id']}/review",
            json={"action": "approve", "reviewer_note": "Approved in test."},
        )
        self.assertEqual(reviewed.status_code, 200)
        self.assertEqual(reviewed.json()["status"], "approved")

    def test_moderation_queue_review_route(self) -> None:
        asset = self.create_ugc_asset()
        self.client.post(f"/worlds/ugc/assets/{asset['public_id']}/submit-review")
        queue_item = self.client.get("/worlds/admin/moderation").json()[0]

        response = self.client.post(
            f"/worlds/admin/moderation/{queue_item['public_id']}/review",
            json={"action": "flag", "reviewer_note": "Needs second review."},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "flagged")
        self.assertEqual(response.json()["reviewer_user_id"], "admin_user")

    def test_fraud_flags_and_rights_claims(self) -> None:
        fraud = self.client.post(
            "/worlds/admin/fraud",
            json={
                "user_id": "test_user",
                "target_type": "submission",
                "target_public_id": "sub_demo",
                "flag_type": "duplicate_clip_risk",
                "severity": "medium",
                "evidence": "Submission appears similar to another package.",
            },
        )
        self.assertEqual(fraud.status_code, 200)
        self.assertEqual(fraud.json()["status"], "open")

        listed_fraud = self.client.get("/worlds/admin/fraud")
        self.assertEqual(len(listed_fraud.json()), 1)

        bad_claim = self.client.post(
            "/worlds/rights/claims",
            json={
                "claimant_name": "Rights Holder",
                "claimant_email": "not-an-email",
                "target_type": "ugc_asset",
                "target_public_id": "ugc_demo",
                "claim_summary": "This asset uses my material.",
            },
        )
        self.assertEqual(bad_claim.status_code, 400)

        claim = self.client.post(
            "/worlds/rights/claims",
            json={
                "claimant_name": "Rights Holder",
                "claimant_email": "rights@example.com",
                "target_type": "ugc_asset",
                "target_public_id": "ugc_demo",
                "claim_summary": "This asset uses my material.",
            },
        )
        self.assertEqual(claim.status_code, 200)
        self.assertEqual(claim.json()["status"], "open")

        listed_claims = self.client.get("/worlds/admin/rights/claims")
        self.assertEqual(len(listed_claims.json()), 1)

    def test_quests_progress_and_claim(self) -> None:
        quests = self.client.get("/worlds/quests")
        self.assertEqual(quests.status_code, 200)
        self.assertTrue(any(item["public_id"] == "quest_create_first_campaign" for item in quests.json()))

        progress = self.client.post("/worlds/quests/quest_create_first_campaign/progress")
        self.assertEqual(progress.status_code, 200)
        self.assertEqual(progress.json()["status"], "completed")

        claim = self.client.post("/worlds/quests/quest_create_first_campaign/claim")
        self.assertEqual(claim.status_code, 200)
        self.assertEqual(claim.json()["status"], "claimed")

    def test_submission_approval_unlocks_relic_title_and_rich_profile(self) -> None:
        campaign_id = self.create_campaign()
        submission = self.client.post(
            "/worlds/marketplace/submissions",
            json={
                "campaign_public_id": campaign_id,
                "title": "Approved clip",
                "hook": "Hook",
                "caption": "Caption",
                "estimated_earnings_amount": 25,
                "rights_confirmed": True,
            },
        )
        self.assertEqual(submission.status_code, 200)
        submission_id = submission.json()["public_id"]

        approved = self.client.post(
            f"/worlds/marketplace/submissions/{submission_id}/review",
            json={"action": "approve", "review_note": "Approved in test."},
        )
        self.assertEqual(approved.status_code, 200)

        relics = self.client.get("/worlds/relics/me")
        self.assertEqual(relics.status_code, 200)
        self.assertTrue(any(item["relic_public_id"] == "relic_gold_thread_fragment" for item in relics.json()))

        rich_profile = self.client.get("/worlds/profile/me/rich")
        self.assertEqual(rich_profile.status_code, 200)
        self.assertIn("Approved Earner", rich_profile.json()["titles"])


if __name__ == "__main__":
    unittest.main()
