from __future__ import annotations

import unittest

from app.job_store import JobStore
from app.models.schemas import ClipBatchResponse, ProcessingSummary


class JobStoreMetadataTests(unittest.IsolatedAsyncioTestCase):
    async def test_complete_job_sets_optional_metadata_without_breaking_result(self) -> None:
        store = JobStore()
        await store.create("job_001", "Queued", plan_code="pro", generation_mode="campaign_pack")

        result = ClipBatchResponse(
            request_id="job_001",
            video_url="https://example.com/watch",
            status="success",
            processing_summary=ProcessingSummary(
                plan_code="pro",
                plan_name="Pro",
                credits_remaining=5,
                estimated_turnaround="preview ready now",
                recommended_next_step="Open the lead preview first.",
                ai_provider="fallback",
                target_platform="TikTok",
                sources_considered=["manual"],
                processing_mode="full",
                selection_strategy="timeline",
                generation_mode="campaign_pack",
                rendered_clip_count=1,
                strategy_only_clip_count=2,
                fallback_reason="provider timeout",
            ),
            trend_context=[],
            clips=[],
        )

        record = await store.complete("job_001", result)

        self.assertIsNotNone(record)
        self.assertEqual(record.plan_code, "pro")
        self.assertEqual(record.generation_mode, "campaign_pack")
        self.assertEqual(record.rendered_clip_count, 1)
        self.assertEqual(record.strategy_only_clip_count, 2)
        self.assertTrue(record.fallback_used)
        self.assertIsNotNone(record.duration_ms)
        self.assertIsNotNone(record.completed_at)
        self.assertIs(record.result, result)

    async def test_failed_job_sets_safe_error_metadata(self) -> None:
        store = JobStore()
        await store.create("job_002", "Queued", plan_code="free", generation_mode="single_source")

        record = await store.fail("job_002", "render broke", error_type="RenderFailure")

        self.assertIsNotNone(record)
        self.assertEqual(record.status, "failed")
        self.assertEqual(record.error, "render broke")
        self.assertEqual(record.error_type, "RenderFailure")
        self.assertIsNotNone(record.duration_ms)
        self.assertIsNotNone(record.completed_at)


if __name__ == "__main__":
    unittest.main()
