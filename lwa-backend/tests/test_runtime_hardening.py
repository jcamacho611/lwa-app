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
from app.services.clip_service import maybe_prune_generated_assets


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


if __name__ == "__main__":
    unittest.main()
