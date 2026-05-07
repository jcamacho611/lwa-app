"""Tests for app.services.engine_runtime.

Cover: env-driven selection, default fallback, invalid id safety, and
the per-engine safety contract (no payouts, no external posting, no
paid provider calls).
"""

from __future__ import annotations

import os
import unittest

from app.services.engine_runtime import (
    DEFAULT_ENGINE_ID,
    ENGINE_SERVICE_ENV_VAR,
    EngineSelectionError,
    get_selected_engine,
    get_selected_engine_id,
    list_known_engine_ids,
    run_selected_engine_demo,
    runtime_snapshot,
    selected_engine_health,
    selected_engine_metadata,
)


EXPECTED_ENGINE_IDS = (
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
)


class _RuntimeEnvScope:
    """Context manager that scopes a value for ENGINE_SERVICE_ENV_VAR."""

    def __init__(self, value: str | None) -> None:
        self.value = value
        self.previous: str | None = None
        self.had_previous: bool = False

    def __enter__(self) -> "_RuntimeEnvScope":
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


class EngineRuntimeSelectionTests(unittest.TestCase):
    def test_known_ids_match_expected_set(self) -> None:
        self.assertEqual(set(list_known_engine_ids()), set(EXPECTED_ENGINE_IDS))
        self.assertEqual(len(list_known_engine_ids()), 10)

    def test_default_fallback_when_unset(self) -> None:
        with _RuntimeEnvScope(None):
            self.assertEqual(get_selected_engine_id(), DEFAULT_ENGINE_ID)

    def test_default_fallback_when_empty_string(self) -> None:
        with _RuntimeEnvScope(""):
            self.assertEqual(get_selected_engine_id(), DEFAULT_ENGINE_ID)

    def test_each_known_engine_id_is_selectable(self) -> None:
        for engine_id in EXPECTED_ENGINE_IDS:
            with _RuntimeEnvScope(engine_id):
                self.assertEqual(get_selected_engine_id(), engine_id)
                engine = get_selected_engine()
                self.assertEqual(engine.engine_id, engine_id)

    def test_invalid_id_raises_safe_error(self) -> None:
        with _RuntimeEnvScope("not_a_real_engine"):
            with self.assertRaises(EngineSelectionError):
                get_selected_engine_id()

    def test_runtime_snapshot_reports_invalid_id_without_raising(self) -> None:
        with _RuntimeEnvScope("not_a_real_engine"):
            snap = runtime_snapshot()
            self.assertEqual(snap["selected_engine_id"], "")
            self.assertIsNotNone(snap["selection_error"])
            self.assertIn("Invalid", snap["selection_error"])
            self.assertEqual(set(snap["known_engine_ids"]), set(EXPECTED_ENGINE_IDS))


class EngineRuntimeMetadataTests(unittest.TestCase):
    def test_selected_engine_metadata_shape(self) -> None:
        with _RuntimeEnvScope("operator_admin"):
            record = selected_engine_metadata()
            self.assertEqual(record["engine_id"], "operator_admin")
            self.assertIn("name", record)
            self.assertIn("status", record)
            self.assertIn("capabilities", record)
            self.assertIn("next_required_integrations", record)
            self.assertIn("health", record)

    def test_selected_engine_health_for_each_engine(self) -> None:
        for engine_id in EXPECTED_ENGINE_IDS:
            with _RuntimeEnvScope(engine_id):
                health = selected_engine_health()
                self.assertEqual(health["engine_id"], engine_id)
                self.assertIn("status", health)
                self.assertIn("healthy", health)
                self.assertIn("warnings", health)

    def test_no_engine_falsely_claims_production_ready(self) -> None:
        with _RuntimeEnvScope("operator_admin"):
            for engine_id in EXPECTED_ENGINE_IDS:
                with _RuntimeEnvScope(engine_id):
                    record = selected_engine_metadata()
                    self.assertNotEqual(
                        record["status"],
                        "production_ready",
                        f"{engine_id} must not claim production_ready in this lane",
                    )


class EngineRuntimeDemoSafetyTests(unittest.TestCase):
    def test_each_engine_demo_runs_safely(self) -> None:
        for engine_id in EXPECTED_ENGINE_IDS:
            with _RuntimeEnvScope(engine_id):
                result = run_selected_engine_demo({})
                self.assertIn("status", result)
                self.assertIn("output", result)
                self.assertIn("warnings", result)

    def test_wallet_engine_does_not_execute_payouts(self) -> None:
        with _RuntimeEnvScope("wallet_entitlements"):
            result = run_selected_engine_demo({"credits": 999})
            output = result["output"]
            self.assertFalse(output["payouts_executed"])
            self.assertFalse(output["payment_mutation"])

    def test_social_engine_does_not_post_externally(self) -> None:
        with _RuntimeEnvScope("social_distribution"):
            result = run_selected_engine_demo({"destination": "tiktok"})
            output = result["output"]
            self.assertFalse(output["external_posted"])
            self.assertFalse(output["publish_allowed"])
            self.assertTrue(output["manual_review_required"])

    def test_render_engine_does_not_call_paid_providers(self) -> None:
        with _RuntimeEnvScope("render"):
            result = run_selected_engine_demo({"render_requested": True})
            output = result["output"]
            self.assertFalse(output["paid_provider_called"])
            self.assertFalse(output["rendered"])
            self.assertTrue(output["strategy_only"])

    def test_safety_engine_blocks_payout_request(self) -> None:
        with _RuntimeEnvScope("safety"):
            result = run_selected_engine_demo({"request_type": "payout"})
            output = result["output"]
            self.assertFalse(output["allowed"])
            self.assertIn("unsafe_request_type", output["blocked_reasons"])

    def test_marketplace_remains_teaser_only(self) -> None:
        with _RuntimeEnvScope("marketplace"):
            result = run_selected_engine_demo({})
            output = result["output"]
            self.assertTrue(output["teaser_only"])
            self.assertFalse(output["marketplace_ready"])
            self.assertFalse(output["campaign_claims_enabled"])


if __name__ == "__main__":
    unittest.main()
