from __future__ import annotations

import json
from uuid import uuid4

from app.worlds.audit import AuditService
from app.worlds.errors import NotFoundError, ValidationError
from app.worlds.jobs.schemas import JobCreateRequest
from app.worlds.jobs.service import JobService
from app.worlds.models import (
    ClipCandidateRecord,
    ClipCandidateStatus,
    ClipMomentRecord,
    ClipPackRecord,
    ClipPackStatus,
    ClipRenderContract,
)
from app.worlds.repositories import (
    ClipCandidateRepository,
    ClipMomentRepository,
    ClipPackRepository,
    ClipRenderContractRepository,
    WorldsStore,
)

from .schemas import (
    ClipCandidateCreateRequest,
    ClipCandidateScoreRequest,
    ClipMomentCreateRequest,
    ClipPackCreateRequest,
    ClipRenderContractCreateRequest,
)
from .scoring import classify_moment, score_text_signal


class ClippingService:
    def __init__(self, store: WorldsStore):
        self.moments = ClipMomentRepository(store)
        self.candidates = ClipCandidateRepository(store)
        self.packs = ClipPackRepository(store)
        self.render_contracts = ClipRenderContractRepository(store)
        self.jobs = JobService(store)
        self.audit = AuditService(store)

    def create_pack(self, *, payload: ClipPackCreateRequest, user_id: str) -> ClipPackRecord:
        pack = self.packs.create(
            ClipPackRecord(
                public_id=f"clippack_{uuid4().hex[:12]}",
                owner_user_id=user_id,
                source_public_id=payload.source_public_id,
                transcript_public_id=payload.transcript_public_id,
                title=payload.title,
                target_platform=payload.target_platform,
                desired_clip_count=payload.desired_clip_count,
                status=ClipPackStatus.draft,
            )
        )
        job = self.jobs.create_job(
            payload=JobCreateRequest(
                job_type="clip_generation",
                title=f"Build clip pack: {pack.title}",
                description="Detect moments, create candidates, score clips, and prepare render contracts.",
                priority="normal",
                source_public_id=pack.source_public_id,
                target_type="clip_pack",
                target_public_id=pack.public_id,
                input_json=json.dumps(
                    {
                        "source_public_id": pack.source_public_id,
                        "transcript_public_id": pack.transcript_public_id,
                        "desired_clip_count": pack.desired_clip_count,
                        "target_platform": pack.target_platform,
                    }
                ),
            ),
            owner_user_id=user_id,
        )
        pack.job_public_id = job.public_id
        pack.status = ClipPackStatus.detecting_moments
        saved = self.packs.save(pack)
        self.audit.record(
            actor_user_id=user_id,
            action_type="clip_pack_created",
            target_type="clip_pack",
            target_public_id=saved.public_id,
            after_state=saved.status.value,
        )
        return saved

    def create_moment(self, *, payload: ClipMomentCreateRequest, user_id: str) -> ClipMomentRecord:
        moment_type = payload.moment_type
        if moment_type == "unknown" and payload.transcript_excerpt:
            moment_type = classify_moment(payload.transcript_excerpt)
        return self.moments.create(
            ClipMomentRecord(
                public_id=f"moment_{uuid4().hex[:12]}",
                owner_user_id=user_id,
                source_public_id=payload.source_public_id,
                transcript_public_id=payload.transcript_public_id,
                start_seconds=payload.start_seconds,
                end_seconds=payload.end_seconds,
                transcript_excerpt=payload.transcript_excerpt,
                moment_type=moment_type,
                reason=payload.reason,
                confidence=payload.confidence,
            )
        )

    def create_candidate(self, *, payload: ClipCandidateCreateRequest, user_id: str) -> ClipCandidateRecord:
        scores = score_text_signal(payload.transcript_excerpt or payload.hook or payload.caption or payload.title)
        return self.candidates.create(
            ClipCandidateRecord(
                public_id=f"clipcand_{uuid4().hex[:12]}",
                owner_user_id=user_id,
                source_public_id=payload.source_public_id,
                transcript_public_id=payload.transcript_public_id,
                moment_public_id=payload.moment_public_id,
                title=payload.title,
                hook=payload.hook,
                caption=payload.caption,
                start_seconds=payload.start_seconds,
                end_seconds=payload.end_seconds,
                target_platform=payload.target_platform,
                status=ClipCandidateStatus.scored,
                score_total=scores["score_total"],
                score_hook=scores["score_hook"],
                score_retention=scores["score_retention"],
                score_clarity=scores["score_clarity"],
                score_emotion=scores["score_emotion"],
                score_shareability=scores["score_shareability"],
                score_platform_fit=scores["score_platform_fit"],
                risk_notes_json=json.dumps(["Review source rights and context before publishing."]),
            )
        )

    def score_candidate(self, *, payload: ClipCandidateScoreRequest, user_id: str) -> ClipCandidateRecord:
        candidate = self.candidates.get_by_public_id(payload.clip_candidate_public_id)
        if not candidate:
            raise NotFoundError("Clip candidate not found.")
        if candidate.owner_user_id != user_id:
            raise ValidationError("Clip candidate does not belong to this user.")

        scores = score_text_signal(payload.transcript_excerpt or candidate.hook or candidate.caption or candidate.title)
        candidate.score_total = scores["score_total"]
        candidate.score_hook = scores["score_hook"]
        candidate.score_retention = scores["score_retention"]
        candidate.score_clarity = scores["score_clarity"]
        candidate.score_emotion = scores["score_emotion"]
        candidate.score_shareability = scores["score_shareability"]
        candidate.score_platform_fit = scores["score_platform_fit"]
        candidate.status = ClipCandidateStatus.scored
        return self.candidates.save(candidate)

    def list_packs(self, user_id: str) -> list[ClipPackRecord]:
        return self.packs.list_for_user(user_id)

    def get_pack(self, pack_public_id: str, user_id: str) -> ClipPackRecord:
        pack = self.packs.get_by_public_id(pack_public_id)
        if not pack:
            raise NotFoundError("Clip pack not found.")
        if pack.owner_user_id != user_id:
            raise ValidationError("Clip pack does not belong to this user.")
        return pack

    def list_pack_moments(self, pack: ClipPackRecord) -> list[ClipMomentRecord]:
        return self.moments.list_for_source(pack.source_public_id)

    def list_pack_candidates(self, pack: ClipPackRecord) -> list[ClipCandidateRecord]:
        return self.candidates.list_for_source(pack.source_public_id)

    def create_render_contract(
        self,
        *,
        payload: ClipRenderContractCreateRequest,
        user_id: str,
    ) -> ClipRenderContract:
        candidate = self.candidates.get_by_public_id(payload.clip_candidate_public_id)
        if not candidate:
            raise NotFoundError("Clip candidate not found.")
        if candidate.owner_user_id != user_id:
            raise ValidationError("Clip candidate does not belong to this user.")
        if payload.music_enabled and payload.music_policy not in {"licensed", "user_provided", "none"}:
            raise ValidationError("Music policy must be licensed, user_provided, or none.")

        contract = self.render_contracts.create(
            ClipRenderContract(
                public_id=f"rendercontract_{uuid4().hex[:12]}",
                owner_user_id=user_id,
                clip_candidate_public_id=payload.clip_candidate_public_id,
                source_public_id=payload.source_public_id,
                output_format=payload.output_format,
                aspect_ratio=payload.aspect_ratio,
                resolution=payload.resolution,
                remove_silence=payload.remove_silence,
                captions_enabled=payload.captions_enabled,
                caption_style_json=payload.caption_style_json,
                music_enabled=payload.music_enabled,
                music_policy=payload.music_policy,
                intro_seconds=payload.intro_seconds,
                outro_seconds=payload.outro_seconds,
            )
        )
        job = self.jobs.create_job(
            payload=JobCreateRequest(
                job_type="render_generation",
                title=f"Render clip: {candidate.title or candidate.public_id}",
                description="Render vertical clip with silence removal, captions, and packaging settings.",
                priority="normal",
                source_public_id=payload.source_public_id,
                target_type="render_contract",
                target_public_id=contract.public_id,
                input_json=json.dumps(
                    {
                        "clip_candidate_public_id": payload.clip_candidate_public_id,
                        "source_public_id": payload.source_public_id,
                        "start_seconds": candidate.start_seconds,
                        "end_seconds": candidate.end_seconds,
                        "remove_silence": payload.remove_silence,
                        "captions_enabled": payload.captions_enabled,
                        "music_enabled": payload.music_enabled,
                        "music_policy": payload.music_policy,
                    }
                ),
            ),
            owner_user_id=user_id,
        )
        contract.render_job_public_id = job.public_id
        saved = self.render_contracts.save(contract)
        candidate.status = ClipCandidateStatus.render_queued
        self.candidates.save(candidate)
        return saved
