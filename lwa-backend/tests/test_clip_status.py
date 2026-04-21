from __future__ import annotations

import unittest

from app.models.schemas import ClipResult
from app.services.clip_status_store import get_clip_status, register_clip_batch, update_clip_status


class ClipStatusStoreTests(unittest.TestCase):
    def build_clip(self, **overrides: object) -> ClipResult:
        payload = {
            "id": "clip_status_test_001",
            "title": "Status test",
            "hook": "This should update live.",
            "caption": "Preview is coming.",
            "start_time": "00:03",
            "end_time": "00:18",
            "score": 88,
            "rank": 1,
            "format": "Hook First",
        }
        payload.update(overrides)
        return ClipResult(**payload)

    def test_register_ready_clip_status(self) -> None:
        clip = self.build_clip(preview_url="https://cdn.example.com/preview.mp4")

        registered = register_clip_batch(request_id="req_status_ready", clips=[clip])
        status = get_clip_status(clip_id=clip.id, request_id="req_status_ready")

        self.assertEqual(registered[0]["render_status"], "ready")
        self.assertIsNotNone(status)
        self.assertEqual(status["preview_url"], "https://cdn.example.com/preview.mp4")
        self.assertTrue(status["is_rendered"])
        self.assertFalse(status["is_strategy_only"])

    def test_pending_clip_can_be_updated_to_ready(self) -> None:
        clip = self.build_clip(id="clip_status_test_002")
        register_clip_batch(
            request_id="req_status_pending",
            clips=[clip],
            local_asset_paths={clip.id: "/tmp/clip_status_test_002_raw.mp4"},
        )

        pending = get_clip_status(clip_id=clip.id, request_id="req_status_pending")
        self.assertEqual(pending["render_status"], "pending")
        self.assertFalse(pending["is_rendered"])
        self.assertNotIn("local_asset_path", pending)

        updated = update_clip_status(
            clip_id=clip.id,
            request_id="req_status_pending",
            updates={"preview_url": "https://cdn.example.com/async.mp4"},
        )

        self.assertIsNotNone(updated)
        self.assertEqual(updated["render_status"], "ready")
        self.assertEqual(updated["status"], "ready")
        self.assertTrue(updated["is_rendered"])
        self.assertFalse(updated["is_strategy_only"])


if __name__ == "__main__":
    unittest.main()
