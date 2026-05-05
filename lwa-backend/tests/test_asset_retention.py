from __future__ import annotations

from datetime import datetime, timedelta, timezone
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from app.core.config import Settings
from app.services.asset_retention import cleanup_generated_assets
from app.services.clip_service import maybe_prune_generated_assets
from app.services.generated_asset_store import GeneratedAssetStore


class AssetRetentionTests(unittest.TestCase):
    def test_settings_reads_required_railway_retention_env_vars(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            generated_root = Path(temp_dir) / "generated"
            with mock.patch.dict(
                os.environ,
                {
                    "LWA_GENERATED_ASSETS_DIR": str(generated_root),
                    "LWA_GENERATED_ASSETS_RETENTION_HOURS": "6",
                    "LWA_GENERATED_ASSETS_MAX_FILES": "150",
                    "LWA_ASSET_CLEANUP_ON_STARTUP": "true",
                },
                clear=False,
            ):
                settings = Settings()

            self.assertEqual(settings.generated_assets_dir, str(generated_root))
            self.assertEqual(settings.generated_asset_retention_hours, 6)
            self.assertEqual(settings.generated_assets_max_files, 150)
            self.assertTrue(settings.asset_cleanup_on_startup)

    def test_old_file_is_deleted(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            now = datetime.now(timezone.utc)
            old_file = root / "old.mp4"
            old_file.write_text("old", encoding="utf-8")
            old_timestamp = (now - timedelta(hours=48)).timestamp()
            os.utime(old_file, (old_timestamp, old_timestamp))

            result = cleanup_generated_assets(root, retention_hours=24, max_files=100, now=now)

            self.assertEqual(result.deleted_count, 1)
            self.assertFalse(old_file.exists())
            self.assertGreaterEqual(result.bytes_deleted, 3)

    def test_new_file_is_kept(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            now = datetime.now(timezone.utc)
            new_file = root / "new.mp4"
            new_file.write_text("new", encoding="utf-8")

            result = cleanup_generated_assets(root, retention_hours=24, max_files=100, now=now)

            self.assertEqual(result.deleted_count, 0)
            self.assertTrue(new_file.exists())
            self.assertEqual(result.retained_count, 1)

    def test_max_file_count_trims_oldest(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            now = datetime.now(timezone.utc)

            for index in range(5):
                file_path = root / f"clip-{index}.mp4"
                file_path.write_text(str(index), encoding="utf-8")
                timestamp = (now - timedelta(minutes=10 - index)).timestamp()
                os.utime(file_path, (timestamp, timestamp))

            result = cleanup_generated_assets(root, retention_hours=24, max_files=3, now=now)

            self.assertEqual(result.deleted_count, 2)
            self.assertEqual(result.overflow_deleted_count, 2)
            remaining = sorted(path.name for path in root.glob("*.mp4"))
            self.assertEqual(len(remaining), 3)
            self.assertNotIn("clip-0.mp4", remaining)
            self.assertNotIn("clip-1.mp4", remaining)

    def test_missing_directory_is_safe(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            missing = Path(temp_dir) / "missing"
            result = cleanup_generated_assets(missing, retention_hours=24, max_files=100)

            self.assertEqual(result.scanned_count, 0)
            self.assertEqual(result.deleted_count, 0)
            self.assertEqual(result.errors, ())

    def test_outside_path_is_not_touched(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "generated"
            root.mkdir(parents=True, exist_ok=True)
            outside_file = Path(temp_dir) / "outside.mp4"
            outside_file.write_text("outside", encoding="utf-8")
            symlink_path = root / "linked.mp4"
            symlink_path.symlink_to(outside_file)
            old_timestamp = (datetime.now(timezone.utc) - timedelta(hours=48)).timestamp()
            os.utime(outside_file, (old_timestamp, old_timestamp))

            result = cleanup_generated_assets(root, retention_hours=24, max_files=100)

            self.assertTrue(outside_file.exists())
            self.assertTrue(symlink_path.exists())
            self.assertGreaterEqual(result.skipped_count, 1)

    def test_summary_tracks_protected_files_and_nested_cleanup(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "generated"
            nested = root / "req_1" / "captions"
            nested.mkdir(parents=True, exist_ok=True)
            now = datetime.now(timezone.utc)

            old_file = nested / "old.vtt"
            old_file.write_text("caption", encoding="utf-8")
            protected_file = root / "lwa-events.jsonl"
            protected_file.write_text("{}", encoding="utf-8")

            old_timestamp = (now - timedelta(hours=48)).timestamp()
            os.utime(old_file, (old_timestamp, old_timestamp))
            os.utime(protected_file, (old_timestamp, old_timestamp))

            result = cleanup_generated_assets(
                root,
                retention_hours=24,
                max_files=100,
                now=now,
                protected_paths=(protected_file,),
            )

            self.assertEqual(result.deleted_count, 1)
            self.assertEqual(result.protected_skipped_count, 1)
            self.assertFalse(old_file.exists())
            self.assertTrue(protected_file.exists())
            self.assertFalse((root / "req_1" / "captions").exists())

    def test_maybe_prune_generated_assets_removes_stale_asset_store_records(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            generated_root = Path(temp_dir) / "generated"
            generated_root.mkdir(parents=True, exist_ok=True)
            store_path = generated_root / "assets.sqlite3"
            store = GeneratedAssetStore(str(store_path))
            store.create_asset(
                asset_id="asset_old",
                provider="lwa",
                asset_type="generated_visual",
                status="completed",
                request_id="req_old",
                local_path=str(generated_root / "req_old" / "clip.mp4"),
            )
            store.create_asset(
                asset_id="asset_recent",
                provider="lwa",
                asset_type="generated_visual",
                status="completed",
                request_id="req_recent",
                local_path=str(generated_root / "req_recent" / "clip.mp4"),
            )

            old_dir = generated_root / "req_old"
            old_dir.mkdir()
            (old_dir / "clip.mp4").write_bytes(b"old")
            recent_dir = generated_root / "req_recent"
            recent_dir.mkdir()
            (recent_dir / "clip.mp4").write_bytes(b"recent")

            now = datetime.now(timezone.utc)
            old_timestamp = (now - timedelta(hours=96)).timestamp()
            recent_timestamp = (now - timedelta(hours=2)).timestamp()
            os.utime(old_dir / "clip.mp4", (old_timestamp, old_timestamp))
            os.utime(recent_dir / "clip.mp4", (recent_timestamp, recent_timestamp))

            with sqlite3.connect(store_path) as connection:
                connection.execute(
                    "UPDATE generated_assets SET created_at = ?, updated_at = ? WHERE id = ?",
                    ("2024-01-01T00:00:00+00:00", "2024-01-01T00:00:00+00:00", "asset_old"),
                )
                connection.execute(
                    "UPDATE generated_assets SET created_at = ?, updated_at = ? WHERE id = ?",
                    ("2099-01-01T00:00:00+00:00", "2099-01-01T00:00:00+00:00", "asset_recent"),
                )
                connection.commit()

            with mock.patch.dict(
                os.environ,
                {
                    "LWA_GENERATED_ASSETS_DIR": str(generated_root),
                    "LWA_GENERATED_ASSET_STORE_PATH": str(store_path),
                    "LWA_USAGE_STORE_PATH": str(generated_root / "lwa-usage.json"),
                    "LWA_PLATFORM_DB_PATH": str(generated_root / "platform.sqlite3"),
                    "LWA_CLIPPING_DB_PATH": str(generated_root / "clipping.sqlite3"),
                    "LWA_EVENT_LOG_PATH": str(generated_root / "lwa-events.jsonl"),
                    "LWA_GENERATED_ASSETS_RETENTION_HOURS": "24",
                    "LWA_GENERATED_ASSETS_MAX_FILES": "300",
                    "LWA_GENERATED_ASSET_PRUNE_INTERVAL_SECONDS": "1",
                },
                clear=False,
            ):
                stats = maybe_prune_generated_assets(Settings(), force=True)

            self.assertEqual(stats["removed"], 1)
            self.assertEqual(stats["store_removed"], 1)
            self.assertIsNone(store.get_asset("asset_old"))
            self.assertIsNotNone(store.get_asset("asset_recent"))


if __name__ == "__main__":
    unittest.main()
