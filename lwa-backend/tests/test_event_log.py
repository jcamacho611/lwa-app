from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from app.core.config import Settings
from app.services.event_log import emit_event


class EventLogTests(unittest.TestCase):
    def test_emit_event_writes_jsonl_and_redacts_sensitive_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            settings = Settings()
            settings.event_log_path = str(Path(temp_dir) / "events.jsonl")
            settings.event_log_enabled = True
            settings.event_log_max_metadata_chars = 48

            emit_event(
                settings=settings,
                event="generation_requested",
                request_id="req_123",
                plan_code="free",
                subject_source="client_id",
                metadata={
                    "video_url": "https://example.com/watch?v=topsecret",
                    "api_key": "super-secret-key",
                    "notes": "x" * 80,
                },
            )

            payload = json.loads(Path(settings.event_log_path).read_text(encoding="utf-8").strip())
            self.assertEqual(payload["event"], "generation_requested")
            self.assertEqual(payload["metadata"]["api_key"], "[redacted]")
            self.assertTrue(str(payload["metadata"]["video_url"]).startswith("url_hash:"))
            self.assertTrue(str(payload["metadata"]["notes"]).endswith("…"))

    def test_emit_event_is_nonfatal_when_logging_is_disabled(self) -> None:
        settings = Settings()
        settings.event_log_enabled = False
        emit_event(settings=settings, event="generation_completed")

    def test_emit_event_trims_oversized_log_before_append(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            settings = Settings()
            log_path = Path(temp_dir) / "events.jsonl"
            settings.event_log_path = str(log_path)
            settings.event_log_enabled = True
            settings.event_log_max_bytes = 512
            log_path.write_text(("x" * 900) + "\n", encoding="utf-8")

            emit_event(
                settings=settings,
                event="job_completed",
                request_id="req_trimmed",
                metadata={"notes": "kept"},
            )

            content = log_path.read_text(encoding="utf-8")
            self.assertLess(log_path.stat().st_size, 700)
            self.assertIn("job_completed", content)
            self.assertNotIn("x" * 200, content)


if __name__ == "__main__":
    unittest.main()
