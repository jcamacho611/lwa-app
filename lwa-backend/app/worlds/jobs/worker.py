from __future__ import annotations

from app.worlds.models import JobType
from app.worlds.repositories import WorldsStore

from .service import JobService


class JobWorker:
    """
    Worker scaffold.

    This does not replace a real queue. Later this can be wired to Celery, RQ,
    Dramatiq, Railway worker services, or a small BackgroundTasks bridge for
    narrow MVP work.
    """

    def __init__(self, store: WorldsStore, worker_name: str = "lwa-worlds-worker"):
        self.store = store
        self.worker_name = worker_name
        self.jobs = JobService(store)

    def run_one(self, job_public_id: str):
        job = self.jobs.get_job(job_public_id)
        attempt = self.jobs.start_attempt(job_public_id=job.public_id, worker_name=self.worker_name)
        try:
            output_json = self.dispatch(job)
            return self.jobs.complete_attempt(
                job_public_id=job.public_id,
                attempt_public_id=attempt.public_id,
                success=True,
                output_json=output_json,
            )
        except Exception as error:
            return self.jobs.complete_attempt(
                job_public_id=job.public_id,
                attempt_public_id=attempt.public_id,
                success=False,
                error_message=str(error),
            )

    def dispatch(self, job) -> str:
        job_type = job.job_type.value if hasattr(job.job_type, "value") else str(job.job_type)
        if job_type == JobType.upload_processing.value:
            return self.handle_upload_processing(job)
        if job_type == JobType.transcript_generation.value:
            return self.handle_transcript_generation(job)
        if job_type == JobType.ai_clip_score.value:
            return self.handle_ai_clip_score(job)
        if job_type == JobType.clip_generation.value:
            return self.handle_clip_generation(job)
        if job_type == JobType.render_generation.value:
            return self.handle_render_generation(job)
        if job_type == JobType.caption_generation.value:
            return self.handle_caption_generation(job)
        if job_type == JobType.social_import.value:
            return self.handle_social_import(job)
        return '{"status":"skipped","reason":"No handler implemented yet."}'

    def handle_upload_processing(self, job) -> str:
        return '{"status":"placeholder","message":"Upload processing handler not wired yet."}'

    def handle_transcript_generation(self, job) -> str:
        return '{"status":"placeholder","message":"Transcript generation handler not wired yet."}'

    def handle_ai_clip_score(self, job) -> str:
        return '{"status":"placeholder","message":"AI clip score handler not wired yet."}'

    def handle_clip_generation(self, job) -> str:
        return '{"status":"placeholder","message":"Clip generation handler not wired yet."}'

    def handle_render_generation(self, job) -> str:
        return '{"status":"placeholder","message":"Render generation handler not wired yet."}'

    def handle_caption_generation(self, job) -> str:
        return '{"status":"placeholder","message":"Caption generation handler not wired yet."}'

    def handle_social_import(self, job) -> str:
        return '{"status":"placeholder","message":"Social import handler not wired yet."}'
