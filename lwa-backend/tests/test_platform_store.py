from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from app.models.schemas import CampaignRequirementCheck, ClipBatchResponse, ClipResult, ProcessingSummary, ScoreBreakdown
from app.services.platform_store import PlatformStore


class PlatformStoreClipMetadataTests(unittest.TestCase):
    def test_persist_clip_batch_round_trips_caption_and_campaign_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = PlatformStore(str(Path(temp_dir) / "platform.sqlite3"))
            user = store.create_user(
                email="creator@example.com",
                password_hash="hash",
                plan="pro",
            )

            response = ClipBatchResponse(
                request_id="req_store_001",
                video_url="https://example.com/source",
                status="success",
                source_type="url",
                source_title="Episode 12",
                source_platform="YouTube",
                transcript="Full transcript",
                visual_summary="Two speakers at a desk.",
                processing_summary=ProcessingSummary(
                    plan_name="Pro",
                    credits_remaining=7,
                    estimated_turnaround="45 seconds",
                    recommended_next_step="Post the lead clip first.",
                    ai_provider="anthropic",
                    target_platform="TikTok",
                    sources_considered=["google"],
                    processing_mode="real",
                    selection_strategy="timeline",
                ),
                trend_context=[],
                clips=[
                    ClipResult(
                        id="clip_store_001",
                        title="Lead clip",
                        hook="Stop posting random clips.",
                        caption="Use this first.",
                        start_time="00:03",
                        end_time="00:18",
                        score=91,
                        rank=1,
                        clip_url="https://backend.example.com/generated/req_store_001/clip.mp4",
                        download_url="https://backend.example.com/generated/req_store_001/clip.mp4",
                        caption_txt_url="https://backend.example.com/generated/req_store_001/captions/clip_store_001/lead-tiktok.txt",
                        caption_srt_url="https://backend.example.com/generated/req_store_001/captions/clip_store_001/lead-tiktok.srt",
                        caption_vtt_url="https://backend.example.com/generated/req_store_001/captions/clip_store_001/lead-tiktok.vtt",
                        burned_caption_url="https://backend.example.com/generated/req_store_001/clip.mp4",
                        export_filename="lead-tiktok.mp4",
                        hook_score=84,
                        score_breakdown=ScoreBreakdown(
                            hook_score=84,
                            retention_score=81,
                            emotional_spike_score=76,
                            clarity_score=80,
                            platform_fit_score=83,
                            visual_energy_score=68,
                            audio_energy_score=70,
                            controversy_score=50,
                            educational_value_score=62,
                            share_comment_score=60,
                            render_readiness_score=88,
                            commercial_value_score=58,
                        ),
                        scoring_explanation="Hook strength and platform fit carry this clip.",
                        render_readiness_score=88,
                        trend_match_score=64,
                        trend_alignment_reason="Partially aligned to the selected trend through shared creator-language.",
                        reuse_potential=82,
                        evergreen_status="evergreen",
                        time_sensitivity="low",
                        approval_state="approved",
                        campaign_requirement_checks=[
                            CampaignRequirementCheck(
                                status="pass",
                                requirement="Playable asset",
                                message="Rendered media is ready to publish now.",
                            )
                        ],
                    )
                ],
            )

            store.persist_clip_batch(
                request_id=response.request_id,
                user_id=user.id,
                campaign_id=None,
                response=response,
            )

            clip = store.get_clip(clip_id="cliprec_missing", user_id=user.id)
            self.assertIsNone(clip)

            pack = store.get_clip_pack(user_id=user.id, request_id="req_store_001")
            self.assertEqual(len(pack["clips"]), 1)
            stored_clip = pack["clips"][0]
            self.assertEqual(stored_clip["caption_txt_url"], "https://backend.example.com/generated/req_store_001/captions/clip_store_001/lead-tiktok.txt")
            self.assertEqual(stored_clip["caption_srt_url"], "https://backend.example.com/generated/req_store_001/captions/clip_store_001/lead-tiktok.srt")
            self.assertEqual(stored_clip["caption_vtt_url"], "https://backend.example.com/generated/req_store_001/captions/clip_store_001/lead-tiktok.vtt")
            self.assertEqual(stored_clip["burned_caption_url"], "https://backend.example.com/generated/req_store_001/clip.mp4")
            self.assertEqual(stored_clip["export_filename"], "lead-tiktok.mp4")
            self.assertEqual(stored_clip["hook_score"], 84)
            self.assertEqual(stored_clip["render_readiness_score"], 88)
            self.assertEqual(stored_clip["trend_match_score"], 64)
            self.assertEqual(stored_clip["reuse_potential"], 82)
            self.assertEqual(stored_clip["evergreen_status"], "evergreen")
            self.assertEqual(stored_clip["time_sensitivity"], "low")
            self.assertEqual(stored_clip["approval_state"], "approved")
            self.assertEqual(stored_clip["score_breakdown"]["platform_fit_score"], 83)
            self.assertEqual(stored_clip["campaign_requirement_checks"][0]["requirement"], "Playable asset")

    def test_batch_summaries_roll_up_render_review_and_evergreen_counts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = PlatformStore(str(Path(temp_dir) / "platform.sqlite3"))
            user = store.create_user(
                email="ops@example.com",
                password_hash="hash",
                plan="scale",
            )

            batch = store.create_batch(
                user_id=user.id,
                title="Agency batch",
                target_platform="TikTok",
                selected_trend="creator growth",
                sources=[{"source_kind": "url", "video_url": "https://example.com/source"}],
            )
            source_id = next(iter(store.get_batch(batch_id=batch["id"], user_id=user.id)["sources"]))["id"]
            store.attach_batch_source_request(
                batch_id=batch["id"],
                source_id=source_id,
                request_id="req_batch_001",
                status="completed",
            )
            store.update_batch_progress(batch_id=batch["id"], completed_increment=1, status="completed")

            response = ClipBatchResponse(
                request_id="req_batch_001",
                video_url="https://example.com/source",
                status="success",
                source_type="url",
                source_title="Agency source",
                source_platform="YouTube",
                processing_summary=ProcessingSummary(
                    plan_name="Scale",
                    credits_remaining=32,
                    estimated_turnaround="45 seconds",
                    recommended_next_step="Queue the approved clip first.",
                    ai_provider="anthropic",
                    target_platform="TikTok",
                    sources_considered=["google"],
                    processing_mode="real",
                    selection_strategy="timeline",
                ),
                trend_context=[],
                clips=[
                    ClipResult(
                        id="clip_batch_approved",
                        title="Approved clip",
                        hook="Lead with this one.",
                        caption="Approved caption",
                        score=88,
                        clip_url="https://backend.example.com/generated/req_batch_001/approved.mp4",
                        approval_state="approved",
                        evergreen_status="evergreen",
                    ),
                    ClipResult(
                        id="clip_batch_review",
                        title="Review clip",
                        hook="Review this before publishing.",
                        caption="Needs one more pass.",
                        score=75,
                        approval_state="needs_review",
                        evergreen_status="time_sensitive",
                    ),
                ],
            )

            store.persist_clip_batch(
                request_id="req_batch_001",
                user_id=user.id,
                campaign_id=None,
                response=response,
            )

            summaries = store.list_batches(user_id=user.id)
            self.assertEqual(len(summaries), 1)
            summary = summaries[0]
            self.assertEqual(summary["request_count"], 1)
            self.assertEqual(summary["clip_count"], 2)
            self.assertEqual(summary["rendered_clip_count"], 1)
            self.assertEqual(summary["strategy_only_clip_count"], 1)
            self.assertEqual(summary["approved_clip_count"], 1)
            self.assertEqual(summary["needs_review_clip_count"], 1)
            self.assertEqual(summary["evergreen_clip_count"], 1)
            self.assertEqual(summary["trend_tied_clip_count"], 1)

            detail = store.get_batch(batch_id=batch["id"], user_id=user.id)
            self.assertEqual(detail["batch"]["top_clip_score"], 88)
            self.assertEqual(detail["sources"][0]["clip_count"], 2)


if __name__ == "__main__":
    unittest.main()
