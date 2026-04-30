from __future__ import annotations

import asyncio
import os
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

from fastapi import HTTPException

from app.core.config import Settings
from app.job_store import RequestThrottle
from app.models.schemas import ProcessRequest
from app.services.clip_service import maybe_prune_generated_assets
from app.services.entitlements import EntitlementContext, build_free_launch_plan
from app.services.fallbacks import build_degraded_clip_response


class RuntimeHardeningTests(unittest.TestCase):
    def test_generated_asset_prune_removes_only_expired_entries(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            generated_root = Path(temp_dir) / "generated"
            generated_root.mkdir(parents=True, exist_ok=True)

            old_request_dir = generated_root / "req_old"
            old_request_dir.mkdir()
            (old_request_dir / "clip_001.mp4").write_bytes(b"old")

            recent_request_dir = generated_root / "req_recent"
            recent_request_dir.mkdir()
            (recent_request_dir / "clip_002.mp4").write_bytes(b"new")

            now = time.time()
            old_timestamp = now - (80 * 3600)
            recent_timestamp = now - (2 * 3600)
            os.utime(old_request_dir, (old_timestamp, old_timestamp))
            os.utime(old_request_dir / "clip_001.mp4", (old_timestamp, old_timestamp))
            os.utime(recent_request_dir, (recent_timestamp, recent_timestamp))
            os.utime(recent_request_dir / "clip_002.mp4", (recent_timestamp, recent_timestamp))

            with mock.patch.dict(
                os.environ,
                {
                    "LWA_GENERATED_ASSETS_DIR": str(generated_root),
                    "LWA_GENERATED_ASSET_RETENTION_HOURS": "72",
                    "LWA_GENERATED_ASSET_PRUNE_INTERVAL_SECONDS": "1",
                },
                clear=False,
            ):
                stats = maybe_prune_generated_assets(Settings(), force=True)

            self.assertEqual(stats["removed"], 1)
            self.assertFalse(old_request_dir.exists())
            self.assertTrue(recent_request_dir.exists())

    def test_request_throttle_blocks_short_window_flooding(self) -> None:
        throttle = RequestThrottle(window_seconds=60, max_requests=2)

        async def exercise() -> None:
            await throttle.enforce(subject="client:test")
            await throttle.enforce(subject="client:test")
            with self.assertRaises(HTTPException) as context:
                await throttle.enforce(subject="client:test")
            self.assertEqual(context.exception.status_code, 429)

        asyncio.run(exercise())

    def test_degraded_fallback_response_is_strategy_only_and_ranked(self) -> None:
        settings = Settings()
        plan = build_free_launch_plan(settings)
        entitlement = EntitlementContext(
            subject="free_launch_ip:test",
            subject_source="free_launch_ip",
            usage_day="2026-04-29",
            plan=plan,
            credits_remaining=9999,
            user_id=None,
        )
        response = build_degraded_clip_response(
            request_id="req_test",
            request=ProcessRequest(
                video_url="https://example.com/blocked-video",
                source_type="url",
                target_platform="TikTok",
                clip_count=3,
            ),
            entitlement=entitlement,
            reason="Public source blocked server access.",
            error_class="platform_blocked",
            trend_context=[],
        )

        self.assertEqual(response.status, "degraded")
        self.assertEqual(response.status_reason, "Public source blocked server access.")
        self.assertEqual(response.processing_summary.processing_mode, "degraded")
        self.assertEqual(response.processing_summary.rendered_clip_count, 0)
        self.assertEqual(response.processing_summary.strategy_only_clip_count, 3)
        self.assertTrue(all(clip.is_strategy_only for clip in response.clips))
        self.assertFalse(any(clip.is_rendered for clip in response.clips))
        self.assertEqual([clip.score for clip in response.clips], [64, 60, 56])
        self.assertEqual([clip.rank for clip in response.clips], [1, 2, 3])


if __name__ == "__main__":
    unittest.main()
