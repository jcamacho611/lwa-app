from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from app.api.routes import campaigns as campaigns_routes
from app.api.routes import me as me_routes
from app.api.routes import posting as posting_routes
from app.api.routes import upload as upload_routes
from app.api.routes import wallet as wallet_routes
from app.auth.security import create_access_token, hash_password
from app.dependencies import auth as auth_dependencies
from app.main import create_app
from app.services.entitlements import UsageStore
from app.services.platform_store import PlatformStore


class PremiumGuardTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temp_dir = tempfile.TemporaryDirectory()
        self._platform_store = PlatformStore(str(Path(self._temp_dir.name) / "platform.sqlite3"))
        self._usage_store = UsageStore(str(Path(self._temp_dir.name) / "usage.json"))
        self._uploads_dir = Path(self._temp_dir.name) / "uploads"
        self._uploads_dir.mkdir(parents=True, exist_ok=True)

        self._previous_auth_store = auth_dependencies.platform_store
        self._previous_campaign_store = campaigns_routes.platform_store
        self._previous_posting_store = posting_routes.platform_store
        self._previous_wallet_store = wallet_routes.platform_store
        self._previous_me_store = me_routes.platform_store
        self._previous_upload_store = upload_routes.platform_store
        self._previous_upload_usage = upload_routes.usage_store
        self._previous_upload_dir = upload_routes.settings.uploads_dir

        auth_dependencies.platform_store = self._platform_store
        campaigns_routes.platform_store = self._platform_store
        posting_routes.platform_store = self._platform_store
        wallet_routes.platform_store = self._platform_store
        me_routes.platform_store = self._platform_store
        upload_routes.platform_store = self._platform_store
        upload_routes.usage_store = self._usage_store
        upload_routes.settings.uploads_dir = str(self._uploads_dir)

        self.client = TestClient(create_app())
        self.free_user = self._platform_store.create_user(
            email="free@example.com",
            password_hash=hash_password("password123"),
            plan="free",
        )
        self.pro_user = self._platform_store.create_user(
            email="pro@example.com",
            password_hash=hash_password("password123"),
            plan="pro",
        )
        self.scale_user = self._platform_store.create_user(
            email="scale@example.com",
            password_hash=hash_password("password123"),
            plan="scale",
        )

    def tearDown(self) -> None:
        auth_dependencies.platform_store = self._previous_auth_store
        campaigns_routes.platform_store = self._previous_campaign_store
        posting_routes.platform_store = self._previous_posting_store
        wallet_routes.platform_store = self._previous_wallet_store
        me_routes.platform_store = self._previous_me_store
        upload_routes.platform_store = self._previous_upload_store
        upload_routes.usage_store = self._previous_upload_usage
        upload_routes.settings.uploads_dir = self._previous_upload_dir
        self.client.close()
        self._temp_dir.cleanup()

    def auth_headers(self, user_id: str, email: str, plan: str) -> dict[str, str]:
        token = create_access_token(
            secret=auth_dependencies.settings.jwt_secret,
            user_id=user_id,
            email=email,
            plan=plan,
            exp_minutes=auth_dependencies.settings.jwt_exp_minutes,
        )
        return {"Authorization": f"Bearer {token}"}

    def test_free_user_cannot_access_campaigns(self) -> None:
        response = self.client.get(
            "/v1/campaigns",
            headers=self.auth_headers(self.free_user.id, self.free_user.email, self.free_user.plan),
        )
        self.assertEqual(response.status_code, 403)
        self.assertIn("Scale", response.json()["detail"])

    def test_pro_user_can_access_wallet(self) -> None:
        response = self.client.get(
            "/v1/wallet",
            headers=self.auth_headers(self.pro_user.id, self.pro_user.email, self.pro_user.plan),
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("available_cents", response.json())

    def test_pro_user_cannot_access_posting_queue(self) -> None:
        response = self.client.get(
            "/v1/posting/connections",
            headers=self.auth_headers(self.pro_user.id, self.pro_user.email, self.pro_user.plan),
        )
        self.assertEqual(response.status_code, 403)
        self.assertIn("Scale", response.json()["detail"])

    def test_free_user_cannot_edit_saved_clip_metadata(self) -> None:
        response = self.client.patch(
            "/v1/me/clips/clip_test",
            headers=self.auth_headers(self.free_user.id, self.free_user.email, self.free_user.plan),
            json={"hook_override": "New hook"},
        )
        self.assertEqual(response.status_code, 403)
        self.assertIn("Pro", response.json()["detail"])

    def test_free_user_upload_limit_is_enforced(self) -> None:
        headers = self.auth_headers(self.free_user.id, self.free_user.email, self.free_user.plan)
        for _ in range(2):
            response = self.client.post(
                "/v1/uploads",
                headers=headers,
                files={"file": ("source.mp4", b"clip-bytes", "video/mp4")},
            )
            self.assertEqual(response.status_code, 200)

        third_response = self.client.post(
            "/v1/uploads",
            headers=headers,
            files={"file": ("source.mp4", b"clip-bytes", "video/mp4")},
        )
        self.assertEqual(third_response.status_code, 402)
        self.assertIn("Daily upload limit reached", third_response.json()["detail"])


if __name__ == "__main__":
    unittest.main()
