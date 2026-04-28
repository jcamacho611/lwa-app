from __future__ import annotations

import os
import unittest
from unittest import mock

from app.core.config import Settings
from app.services.clip_service import dependency_health, provider_health
from app.services.whop_service import describe_whop_verification_state


class WhopVerificationStateTests(unittest.TestCase):
    def test_verification_defaults_to_disabled(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=False):
            settings = Settings()

        state = describe_whop_verification_state(settings)
        self.assertFalse(state.enabled)
        self.assertEqual(state.status, "disabled")
        self.assertIn("WHOP_API_KEY", state.missing_fields)
        self.assertIn("WHOP_COMPANY_ID", state.missing_fields)
        self.assertIn("WHOP_PRODUCT_ID", state.missing_fields)

    def test_enabled_verification_reports_missing_config(self) -> None:
        with mock.patch.dict(
            os.environ,
            {
                "LWA_ENABLE_WHOP_VERIFICATION": "true",
                "WHOP_API_KEY": "secret",
            },
            clear=False,
        ):
            settings = Settings()

        state = describe_whop_verification_state(settings)
        self.assertTrue(state.enabled)
        self.assertFalse(state.configured)
        self.assertEqual(state.status, "missing-config")
        self.assertEqual(list(state.missing_fields), ["WHOP_COMPANY_ID", "WHOP_PRODUCT_ID"])

    def test_enabled_verification_with_required_values_is_configured(self) -> None:
        with mock.patch.dict(
            os.environ,
            {
                "LWA_ENABLE_WHOP_VERIFICATION": "true",
                "WHOP_API_KEY": "secret",
                "WHOP_COMPANY_ID": "biz_123",
                "WHOP_PRODUCT_ID": "prod_123",
                "WHOP_WEBHOOK_SECRET": "hook_secret",
            },
            clear=False,
        ):
            settings = Settings()

        state = describe_whop_verification_state(settings)
        self.assertTrue(state.enabled)
        self.assertTrue(state.configured)
        self.assertEqual(state.status, "configured")
        self.assertEqual(state.missing_fields, ())
        self.assertTrue(state.webhook_secret_present)

    def test_provider_health_exposes_whop_state(self) -> None:
        with mock.patch.dict(
            os.environ,
            {
                "LWA_ENABLE_WHOP_VERIFICATION": "true",
                "WHOP_API_KEY": "secret",
                "WHOP_COMPANY_ID": "biz_123",
                "WHOP_PRODUCT_ID": "prod_123",
            },
            clear=False,
        ):
            settings = Settings()

        deps = dependency_health(settings)
        providers = provider_health(settings)

        self.assertTrue(deps["whop_verification_enabled"])
        self.assertTrue(deps["whop_verification_configured"])
        self.assertIn("whop", providers)
        self.assertEqual(providers["whop"]["status"], "configured")
        self.assertEqual(providers["whop"]["mode"], "verification")


if __name__ == "__main__":
    unittest.main()
