from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from app.api.routes import generate as generate_routes
from app.job_store import JobStore
from app.main import create_app
from app.models.schemas import ClipBatchResponse, ClipResult, FeatureFlags, ProcessingSummary
from app.services.platform_store import PlatformStore


def build_response(request_id: str) -> ClipBatchResponse:
    return ClipBatchResponse(
        request_id=request_id,
        video_url="https://example.com/source.mp4",
        status="completed",
        source_type="url",
        source_title="Test source",
        source_platform="YouTube",
        transcript="A source transcript",
        visual_summary="A visual summary",
        preview_asset_url="https://example.com/preview.mp4",
        download_asset_url="https://example.com/download.mp4",
        thumbnail_url="https://example.com/thumb.jpg",
        processing_summary=ProcessingSummary(
            plan_name="Free",
            credits_remaining=2,
            estimated_turnaround="preview ready now",
            recommended_next_step="Open the lead preview now.",
            ai_provider="fallback",
            target_platform="TikTok",
            sources_considered=["https://example.com/source.mp4"],
            processing_mode="test",
            selection_strategy="test",
            feature_flags=FeatureFlags(),
        ),
        trend_context=[],
        clips=[
            ClipResult(
                id="clip_001",
                title="Clip one",
                hook="Hook one",
                caption="Caption one",
                start_time="00:00:05",
                end_time="00:00:25",
                score=88,
                format="9:16",
                preview_url="https://example.com/preview.mp4",
                download_url="https://example.com/download.mp4",
            )
        ],
    )


class PersistedJobStatusTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temp_dir = tempfile.TemporaryDirectory()
        self._store = PlatformStore(str(Path(self._temp_dir.name) / "platform.db"))
        self._previous_store = generate_routes.platform_store
        self._previous_jobs = generate_routes.job_store
        generate_routes.platform_store = self._store
        generate_routes.job_store = JobStore(max_jobs=5)
        self.client = TestClient(create_app())

    def tearDown(self) -> None:
        generate_routes.platform_store = self._previous_store
        generate_routes.job_store = self._previous_jobs
        self.client.close()
        self._temp_dir.cleanup()

    def test_completed_job_loads_from_persistent_store(self) -> None:
        response = build_response("job_completed")
        self._store.create_job(
            job_id="job_completed",
            user_id=None,
            campaign_id=None,
            source_type="url",
            source_value=response.video_url,
            status="queued",
            message="Job queued.",
        )
        self._store.update_job(
            job_id="job_completed",
            status="completed",
            message="Clips ready.",
            response_json=response.model_dump_json(),
        )

        http_response = self.client.get("/v1/jobs/job_completed")
        self.assertEqual(http_response.status_code, 200)
        payload = http_response.json()
        self.assertEqual(payload["status"], "completed")
        self.assertEqual(payload["message"], "Clips ready.")
        self.assertEqual(payload["result"]["request_id"], "job_completed")
        self.assertEqual(payload["result"]["clips"][0]["id"], "clip_001")

    def test_failed_job_surfaces_persisted_error(self) -> None:
        self._store.create_job(
            job_id="job_failed",
            user_id=None,
            campaign_id=None,
            source_type="url",
            source_value="https://example.com/source.mp4",
            status="queued",
            message="Job queued.",
        )
        self._store.update_job(
            job_id="job_failed",
            status="failed",
            message="Processing failed.",
            error_text="ffmpeg exited with code 1",
        )

        http_response = self.client.get("/v1/jobs/job_failed")
        self.assertEqual(http_response.status_code, 200)
        payload = http_response.json()
        self.assertEqual(payload["status"], "failed")
        self.assertEqual(payload["message"], "Processing failed.")
        self.assertEqual(payload["error"], "ffmpeg exited with code 1")

    def test_processing_job_is_marked_interrupted_when_memory_is_gone(self) -> None:
        self._store.create_job(
            job_id="job_interrupted",
            user_id=None,
            campaign_id=None,
            source_type="url",
            source_value="https://example.com/source.mp4",
            status="queued",
            message="Job queued.",
        )
        self._store.update_job(
            job_id="job_interrupted",
            status="processing",
            message="Rendering vertical exports, overlays, and preview assets.",
        )

        http_response = self.client.get("/v1/jobs/job_interrupted")
        self.assertEqual(http_response.status_code, 200)
        payload = http_response.json()
        self.assertEqual(payload["status"], "interrupted")
        self.assertIn("backend restart", payload["message"].lower())
        self.assertIn("retry", payload["error"].lower())


if __name__ == "__main__":
    unittest.main()
