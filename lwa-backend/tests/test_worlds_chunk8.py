from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from fastapi.testclient import TestClient

from app.main import app
from app.worlds.dependencies import get_demo_user_id, get_optional_actor_id, get_worlds_store
from app.worlds.jobs.policies import can_retry, can_transition, clamp_progress, default_max_attempts
from app.worlds.jobs.worker import JobWorker
from app.worlds.repositories import WorldsStore


class WorldsChunk8Tests(unittest.TestCase):
    def setUp(self) -> None:
        self._temp_dir = tempfile.TemporaryDirectory()
        self.store = WorldsStore(str(Path(self._temp_dir.name) / "worlds.sqlite3"))
        app.dependency_overrides[get_worlds_store] = lambda: self.store
        app.dependency_overrides[get_demo_user_id] = lambda: "test_user"
        app.dependency_overrides[get_optional_actor_id] = lambda: "admin_user"
        self.client = TestClient(app)

    def tearDown(self) -> None:
        app.dependency_overrides.clear()
        self._temp_dir.cleanup()

    def test_job_policies(self) -> None:
        self.assertTrue(can_transition("queued", "running"))
        self.assertFalse(can_transition("succeeded", "running"))
        self.assertTrue(can_retry("failed", 1, 3))
        self.assertFalse(can_retry("failed", 3, 3))
        self.assertEqual(clamp_progress(-10), 0)
        self.assertEqual(clamp_progress(50), 50)
        self.assertEqual(clamp_progress(999), 100)
        self.assertEqual(default_max_attempts("render_generation"), 3)

    def test_create_job_route_shape_and_events(self) -> None:
        response = self.client.post(
            "/worlds/jobs",
            json={
                "job_type": "clip_generation",
                "title": "Generate clips",
                "description": "Create clips from source.",
                "priority": "normal",
                "source_public_id": "source_demo",
                "target_type": "source_file",
                "target_public_id": "source_demo",
                "input_json": "{}",
            },
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["job_type"], "clip_generation")
        self.assertEqual(body["status"], "queued")

        events = self.client.get(f"/worlds/jobs/{body['public_id']}/events")
        self.assertEqual(events.status_code, 200)
        self.assertTrue(any(item["event_type"] == "job_created" for item in events.json()))

    def test_create_job_rejects_bad_type(self) -> None:
        response = self.client.post("/worlds/jobs", json={"job_type": "not_real", "title": "Bad job"})

        self.assertEqual(response.status_code, 400)

    def test_run_once_worker_placeholder_succeeds(self) -> None:
        job = self.client.post(
            "/worlds/jobs",
            json={"job_type": "upload_processing", "title": "Process upload"},
        ).json()

        response = self.client.post(f"/worlds/jobs/{job['public_id']}/run-once")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "succeeded")

        attempts = self.client.get(f"/worlds/jobs/{job['public_id']}/attempts")
        self.assertEqual(attempts.status_code, 200)
        self.assertEqual(len(attempts.json()), 1)

    def test_dashboard_route_counts_jobs(self) -> None:
        self.client.post("/worlds/jobs", json={"job_type": "clip_generation", "title": "Queued"})

        response = self.client.get("/worlds/jobs/admin/dashboard")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["queued"], 1)
        self.assertEqual(len(response.json()["recent_jobs"]), 1)

    def test_worker_class_exists(self) -> None:
        self.assertIsNotNone(JobWorker)


if __name__ == "__main__":
    unittest.main()
