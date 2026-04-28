from __future__ import annotations

import os
import tempfile
import unittest
from unittest import mock

from fastapi import HTTPException
from starlette.requests import Request

from app.core.config import Settings
from app.services.clip_service import enforce_api_key
from app.services.entitlements import UsageStore, build_pro_plan, build_scale_plan, resolve_entitlement


def build_request(*, client_id: str | None = None, api_key: str | None = None) -> Request:
    headers: list[tuple[bytes, bytes]] = []
    if client_id:
        headers.append((b"x-lwa-client-id", client_id.encode("utf-8")))
    if api_key:
        headers.append((b"x-api-key", api_key.encode("utf-8")))
    scope = {
        "type": "http",
        "method": "POST",
        "path": "/generate",
        "headers": headers,
        "client": ("127.0.0.1", 8000),
    }
    return Request(scope)


class EntitlementsTests(unittest.TestCase):
    def test_settings_use_safe_env_int_fallbacks(self) -> None:
        with mock.patch.dict(
            os.environ,
            {
                "LWA_FREE_DAILY_LIMIT": "not-a-number",
                "LWA_PRO_DAILY_LIMIT": "also-bad",
                "LWA_GENERATED_ASSETS_MAX_FILES": "-9",
            },
            clear=False,
        ):
            settings = Settings()

        self.assertEqual(settings.free_daily_limit, settings.default_credits_remaining)
        self.assertEqual(settings.pro_daily_limit, 25)
        self.assertEqual(settings.generated_assets_max_files, 300)

    def test_quota_exceeded_returns_structured_detail(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            settings = Settings()
            settings.free_daily_limit = 1
            usage_store = UsageStore(f"{temp_dir}/usage.json")
            request = build_request(client_id="test-client")

            resolve_entitlement(request=request, settings=settings, usage_store=usage_store)

            with self.assertRaises(HTTPException) as context:
                resolve_entitlement(request=request, settings=settings, usage_store=usage_store)

            self.assertEqual(context.exception.status_code, 402)
            self.assertIsInstance(context.exception.detail, dict)
            self.assertEqual(context.exception.detail["code"], "quota_exceeded")
            self.assertEqual(context.exception.detail["credits_remaining"], 0)
            self.assertIn("used today's free generations", context.exception.detail["message"])
            self.assertIn("paid API key", context.exception.detail["upgrade_hint"])

    def test_paid_api_key_subjects_are_hashed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            settings = Settings()
            settings.pro_api_keys = {"pro-secret-key"}
            usage_store = UsageStore(f"{temp_dir}/usage.json")
            entitlement = resolve_entitlement(
                request=build_request(api_key="pro-secret-key"),
                settings=settings,
                usage_store=usage_store,
            )

        self.assertEqual(entitlement.subject_source, "pro_api_key")
        self.assertTrue(entitlement.subject.startswith("pro:"))
        self.assertNotIn("pro-secret-key", entitlement.subject)

    def test_paid_api_keys_bypass_route_gate_when_backend_auth_is_enabled(self) -> None:
        settings = Settings()
        settings.api_key_secret = "gate-secret"
        settings.pro_api_keys = {"pro-secret-key"}
        settings.scale_api_keys = {"scale-secret-key"}

        enforce_api_key(build_request(api_key="pro-secret-key"), settings)
        enforce_api_key(build_request(api_key="scale-secret-key"), settings)

    def test_client_id_subjects_are_hashed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            settings = Settings()
            usage_store = UsageStore(f"{temp_dir}/usage.json")
            entitlement = resolve_entitlement(
                request=build_request(client_id="client-raw-value"),
                settings=settings,
                usage_store=usage_store,
            )

        self.assertEqual(entitlement.subject_source, "client_id")
        self.assertTrue(entitlement.subject.startswith("client:"))
        self.assertNotIn("client-raw-value", entitlement.subject)

    def test_remote_ip_subjects_are_hashed_when_client_id_missing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            settings = Settings()
            usage_store = UsageStore(f"{temp_dir}/usage.json")
            entitlement = resolve_entitlement(
                request=build_request(),
                settings=settings,
                usage_store=usage_store,
            )

        self.assertEqual(entitlement.subject_source, "remote_ip")
        self.assertTrue(entitlement.subject.startswith("ip:"))
        self.assertNotIn("127.0.0.1", entitlement.subject)

    def test_paid_feature_flags_do_not_claim_unshipped_queue_or_editor_capabilities(self) -> None:
        settings = Settings()

        pro_plan = build_pro_plan(settings)
        scale_plan = build_scale_plan(settings)

        self.assertTrue(pro_plan.feature_flags.alt_hooks)
        self.assertTrue(pro_plan.feature_flags.packaging_profiles)
        self.assertTrue(pro_plan.feature_flags.premium_exports)
        self.assertTrue(pro_plan.feature_flags.export_bundle)
        self.assertFalse(pro_plan.feature_flags.campaign_mode)
        self.assertFalse(pro_plan.feature_flags.posting_queue)
        self.assertFalse(pro_plan.feature_flags.caption_editor)
        self.assertFalse(pro_plan.feature_flags.timeline_editor)
        self.assertFalse(pro_plan.feature_flags.priority_processing)
        self.assertFalse(pro_plan.feature_flags.batch_mode)
        self.assertFalse(pro_plan.feature_flags.analytics_feedback)

        self.assertTrue(scale_plan.feature_flags.alt_hooks)
        self.assertTrue(scale_plan.feature_flags.packaging_profiles)
        self.assertTrue(scale_plan.feature_flags.premium_exports)
        self.assertTrue(scale_plan.feature_flags.campaign_mode)
        self.assertTrue(scale_plan.feature_flags.export_bundle)
        self.assertFalse(scale_plan.feature_flags.posting_queue)
        self.assertFalse(scale_plan.feature_flags.caption_editor)
        self.assertFalse(scale_plan.feature_flags.timeline_editor)
        self.assertFalse(scale_plan.feature_flags.priority_processing)
        self.assertFalse(scale_plan.feature_flags.batch_mode)
        self.assertFalse(scale_plan.feature_flags.analytics_feedback)


if __name__ == "__main__":
    unittest.main()
