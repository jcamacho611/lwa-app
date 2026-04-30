from __future__ import annotations

from uuid import uuid4

from app.worlds.audit import AuditService
from app.worlds.errors import ForbiddenTransitionError, NotFoundError, ValidationError
from app.worlds.models import JobPriority, JobStatus, JobType, WorldJob, WorldJobAttempt, WorldJobEvent
from app.worlds.repositories import (
    WorldJobAttemptRepository,
    WorldJobEventRepository,
    WorldJobRepository,
    WorldsStore,
    utcnow,
)

from .policies import can_retry, can_transition, clamp_progress, default_max_attempts, next_retry_time
from .schemas import JobCreateRequest, JobUpdateRequest


class JobService:
    def __init__(self, store: WorldsStore):
        self.jobs = WorldJobRepository(store)
        self.events = WorldJobEventRepository(store)
        self.attempts = WorldJobAttemptRepository(store)
        self.audit = AuditService(store)

    def record_event(
        self,
        *,
        job_public_id: str,
        event_type: str,
        message: str,
        status_before: str | None = None,
        status_after: str | None = None,
        progress_percent: int | None = None,
        metadata_json: str = "{}",
    ) -> WorldJobEvent:
        return self.events.create(
            WorldJobEvent(
                public_id=f"jobevt_{uuid4().hex[:12]}",
                job_public_id=job_public_id,
                event_type=event_type,
                message=message,
                status_before=status_before,
                status_after=status_after,
                progress_percent=progress_percent,
                metadata_json=metadata_json,
            )
        )

    def create_job(self, *, payload: JobCreateRequest, owner_user_id: str | None) -> WorldJob:
        try:
            job_type = JobType(payload.job_type)
            priority = JobPriority(payload.priority)
        except ValueError as error:
            raise ValidationError(str(error)) from error

        job = WorldJob(
            public_id=f"job_{uuid4().hex[:12]}",
            owner_user_id=owner_user_id,
            job_type=job_type,
            status=JobStatus.queued,
            priority=priority,
            progress_percent=0,
            title=payload.title,
            description=payload.description,
            source_public_id=payload.source_public_id,
            target_type=payload.target_type,
            target_public_id=payload.target_public_id,
            input_json=payload.input_json,
            max_attempts=default_max_attempts(job_type.value),
        )
        saved = self.jobs.create(job)
        self.record_event(
            job_public_id=saved.public_id,
            event_type="job_created",
            message="Job created and queued.",
            status_after=saved.status.value,
            progress_percent=saved.progress_percent,
        )
        self.audit.record(
            actor_user_id=owner_user_id,
            action_type="job_created",
            target_type="job",
            target_public_id=saved.public_id,
            after_state=saved.status.value,
            note=saved.job_type.value,
        )
        return saved

    def get_job(self, job_public_id: str) -> WorldJob:
        job = self.jobs.get_by_public_id(job_public_id)
        if not job:
            raise NotFoundError("Job not found.")
        return job

    def update_job(self, *, job_public_id: str, payload: JobUpdateRequest) -> WorldJob:
        job = self.get_job(job_public_id)
        before = job.status

        if payload.status:
            try:
                after = JobStatus(payload.status)
            except ValueError as error:
                raise ValidationError("Invalid job status.") from error

            if after != before and not can_transition(before.value, after.value):
                raise ForbiddenTransitionError(f"Cannot move job from {before.value} to {after.value}.")

            job.status = after
            if after == JobStatus.running and not job.started_at:
                job.started_at = utcnow()
            if after in {JobStatus.succeeded, JobStatus.failed, JobStatus.cancelled, JobStatus.expired}:
                job.completed_at = utcnow()
            if after == JobStatus.succeeded:
                job.progress_percent = 100

        if payload.progress_percent is not None:
            job.progress_percent = clamp_progress(payload.progress_percent)
        if payload.output_json is not None:
            job.output_json = payload.output_json
        if payload.error_message is not None:
            job.error_message = payload.error_message

        saved = self.jobs.save(job)
        self.record_event(
            job_public_id=saved.public_id,
            event_type="job_updated",
            message="Job status/progress updated.",
            status_before=before.value,
            status_after=saved.status.value,
            progress_percent=saved.progress_percent,
        )
        return saved

    def start_attempt(self, *, job_public_id: str, worker_name: str | None = None) -> WorldJobAttempt:
        job = self.get_job(job_public_id)
        before = job.status
        job.attempt_count += 1
        job.status = JobStatus.running
        job.started_at = job.started_at or utcnow()
        self.jobs.save(job)

        attempt = self.attempts.create(
            WorldJobAttempt(
                public_id=f"jobtry_{uuid4().hex[:12]}",
                job_public_id=job.public_id,
                attempt_number=job.attempt_count,
                worker_name=worker_name,
                status=JobStatus.running,
            )
        )
        self.record_event(
            job_public_id=job.public_id,
            event_type="attempt_started",
            message=f"Attempt {attempt.attempt_number} started.",
            status_before=before.value,
            status_after=JobStatus.running.value,
            progress_percent=job.progress_percent,
        )
        return attempt

    def complete_attempt(
        self,
        *,
        job_public_id: str,
        attempt_public_id: str,
        success: bool,
        error_message: str | None = None,
        output_json: str = "{}",
    ) -> WorldJob:
        job = self.get_job(job_public_id)
        attempt = next(
            (item for item in self.attempts.list_for_job(job_public_id) if item.public_id == attempt_public_id),
            None,
        )
        if not attempt:
            raise NotFoundError("Job attempt not found.")

        attempt.completed_at = utcnow()
        attempt.status = JobStatus.succeeded if success else JobStatus.failed
        attempt.error_message = error_message
        self.attempts.save(attempt)

        if success:
            return self.update_job(
                job_public_id=job_public_id,
                payload=JobUpdateRequest(
                    status=JobStatus.succeeded.value,
                    progress_percent=100,
                    output_json=output_json,
                ),
            )

        job.error_message = error_message
        if can_retry(job.status.value, job.attempt_count, job.max_attempts) or job.attempt_count < job.max_attempts:
            before = job.status
            job.status = JobStatus.retrying
            job.next_retry_at = next_retry_time(job.attempt_count)
            saved = self.jobs.save(job)
            self.record_event(
                job_public_id=saved.public_id,
                event_type="job_retry_scheduled",
                message="Job failed and retry was scheduled.",
                status_before=before.value,
                status_after=saved.status.value,
                progress_percent=saved.progress_percent,
            )
            return saved

        return self.update_job(
            job_public_id=job_public_id,
            payload=JobUpdateRequest(status=JobStatus.failed.value, error_message=error_message),
        )

    def cancel_job(self, *, job_public_id: str, actor_user_id: str | None, reason: str) -> WorldJob:
        job = self.update_job(
            job_public_id=job_public_id,
            payload=JobUpdateRequest(status=JobStatus.cancelled.value, error_message=reason),
        )
        self.audit.record(
            actor_user_id=actor_user_id,
            action_type="job_cancelled",
            target_type="job",
            target_public_id=job.public_id,
            after_state=job.status.value,
            note=reason,
        )
        return job

    def retry_job(self, *, job_public_id: str, actor_user_id: str | None, reason: str) -> WorldJob:
        job = self.get_job(job_public_id)
        if not can_retry(job.status.value, job.attempt_count, job.max_attempts):
            raise ValidationError("Job is not retryable.")

        before = job.status
        job.status = JobStatus.retrying
        job.next_retry_at = utcnow()
        job.error_message = None
        saved = self.jobs.save(job)
        self.record_event(
            job_public_id=saved.public_id,
            event_type="manual_retry_requested",
            message=reason,
            status_before=before.value,
            status_after=saved.status.value,
            progress_percent=saved.progress_percent,
        )
        self.audit.record(
            actor_user_id=actor_user_id,
            action_type="job_retry_requested",
            target_type="job",
            target_public_id=saved.public_id,
            before_state=before.value,
            after_state=saved.status.value,
            note=reason,
        )
        return saved

    def list_my_jobs(self, user_id: str) -> list[WorldJob]:
        return self.jobs.list_for_user(user_id)

    def list_recent_jobs(self) -> list[WorldJob]:
        return self.jobs.list_recent()

    def list_job_events(self, job_public_id: str):
        return self.events.list_for_job(job_public_id)

    def list_job_attempts(self, job_public_id: str):
        return self.attempts.list_for_job(job_public_id)
