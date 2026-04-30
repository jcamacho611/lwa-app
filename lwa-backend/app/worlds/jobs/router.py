from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.worlds.dependencies import get_demo_user_id, get_optional_actor_id, get_worlds_store
from app.worlds.errors import ForbiddenTransitionError, NotFoundError, RightsConfirmationRequired, ValidationError
from app.worlds.repositories import WorldsStore

from .schemas import (
    JobAttemptResponse,
    JobCancelRequest,
    JobCreateRequest,
    JobDashboardResponse,
    JobEventResponse,
    JobResponse,
    JobRetryRequest,
    JobUpdateRequest,
)
from .service import JobService
from .worker import JobWorker

router = APIRouter(prefix="/worlds/jobs", tags=["lwa-worlds-jobs"])


def handle_jobs_error(error: Exception) -> None:
    if isinstance(error, NotFoundError):
        raise HTTPException(status_code=404, detail=str(error)) from error
    if isinstance(error, RightsConfirmationRequired):
        raise HTTPException(status_code=400, detail=str(error)) from error
    if isinstance(error, ForbiddenTransitionError):
        raise HTTPException(status_code=409, detail=str(error)) from error
    if isinstance(error, ValidationError):
        raise HTTPException(status_code=400, detail=str(error)) from error
    raise error


def job_to_response(job) -> JobResponse:
    return JobResponse(
        public_id=job.public_id,
        owner_user_id=job.owner_user_id,
        job_type=job.job_type.value if hasattr(job.job_type, "value") else str(job.job_type),
        status=job.status.value if hasattr(job.status, "value") else str(job.status),
        priority=job.priority.value if hasattr(job.priority, "value") else str(job.priority),
        progress_percent=job.progress_percent,
        title=job.title,
        description=job.description,
        source_public_id=job.source_public_id,
        target_type=job.target_type,
        target_public_id=job.target_public_id,
        input_json=job.input_json,
        output_json=job.output_json,
        error_message=job.error_message,
        max_attempts=job.max_attempts,
        attempt_count=job.attempt_count,
        next_retry_at=job.next_retry_at,
        started_at=job.started_at,
        completed_at=job.completed_at,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )


def event_to_response(event) -> JobEventResponse:
    return JobEventResponse(
        public_id=event.public_id,
        job_public_id=event.job_public_id,
        event_type=event.event_type,
        message=event.message,
        status_before=event.status_before,
        status_after=event.status_after,
        progress_percent=event.progress_percent,
        metadata_json=event.metadata_json,
        created_at=event.created_at,
    )


def attempt_to_response(attempt) -> JobAttemptResponse:
    return JobAttemptResponse(
        public_id=attempt.public_id,
        job_public_id=attempt.job_public_id,
        attempt_number=attempt.attempt_number,
        worker_name=attempt.worker_name,
        status=attempt.status.value if hasattr(attempt.status, "value") else str(attempt.status),
        error_message=attempt.error_message,
        started_at=attempt.started_at,
        completed_at=attempt.completed_at,
    )


@router.post("", response_model=JobResponse)
def create_job(
    payload: JobCreateRequest,
    store: WorldsStore = Depends(get_worlds_store),
    user_id: str = Depends(get_demo_user_id),
):
    try:
        return job_to_response(JobService(store).create_job(payload=payload, owner_user_id=user_id))
    except Exception as error:
        handle_jobs_error(error)


@router.get("/me", response_model=list[JobResponse])
def list_my_jobs(
    store: WorldsStore = Depends(get_worlds_store),
    user_id: str = Depends(get_demo_user_id),
):
    return [job_to_response(job) for job in JobService(store).list_my_jobs(user_id)]


@router.get("/admin/dashboard", response_model=JobDashboardResponse)
def admin_job_dashboard(store: WorldsStore = Depends(get_worlds_store)):
    jobs = JobService(store).list_recent_jobs()
    counts = {
        "queued": 0,
        "running": 0,
        "succeeded": 0,
        "failed": 0,
        "retrying": 0,
        "cancelled": 0,
    }
    for job in jobs:
        status = job.status.value if hasattr(job.status, "value") else str(job.status)
        if status in counts:
            counts[status] += 1
    return JobDashboardResponse(
        queued=counts["queued"],
        running=counts["running"],
        succeeded=counts["succeeded"],
        failed=counts["failed"],
        retrying=counts["retrying"],
        cancelled=counts["cancelled"],
        recent_jobs=[job_to_response(job) for job in jobs[:25]],
    )


@router.get("/{job_public_id}", response_model=JobResponse)
def get_job(job_public_id: str, store: WorldsStore = Depends(get_worlds_store)):
    try:
        return job_to_response(JobService(store).get_job(job_public_id))
    except Exception as error:
        handle_jobs_error(error)


@router.patch("/{job_public_id}", response_model=JobResponse)
def update_job(
    job_public_id: str,
    payload: JobUpdateRequest,
    store: WorldsStore = Depends(get_worlds_store),
):
    try:
        return job_to_response(JobService(store).update_job(job_public_id=job_public_id, payload=payload))
    except Exception as error:
        handle_jobs_error(error)


@router.post("/{job_public_id}/cancel", response_model=JobResponse)
def cancel_job(
    job_public_id: str,
    payload: JobCancelRequest,
    store: WorldsStore = Depends(get_worlds_store),
    actor_id: str | None = Depends(get_optional_actor_id),
):
    try:
        return job_to_response(
            JobService(store).cancel_job(
                job_public_id=job_public_id,
                actor_user_id=actor_id,
                reason=payload.reason,
            )
        )
    except Exception as error:
        handle_jobs_error(error)


@router.post("/{job_public_id}/retry", response_model=JobResponse)
def retry_job(
    job_public_id: str,
    payload: JobRetryRequest,
    store: WorldsStore = Depends(get_worlds_store),
    actor_id: str | None = Depends(get_optional_actor_id),
):
    try:
        return job_to_response(
            JobService(store).retry_job(
                job_public_id=job_public_id,
                actor_user_id=actor_id,
                reason=payload.reason,
            )
        )
    except Exception as error:
        handle_jobs_error(error)


@router.get("/{job_public_id}/events", response_model=list[JobEventResponse])
def list_job_events(job_public_id: str, store: WorldsStore = Depends(get_worlds_store)):
    return [event_to_response(event) for event in JobService(store).list_job_events(job_public_id)]


@router.get("/{job_public_id}/attempts", response_model=list[JobAttemptResponse])
def list_job_attempts(job_public_id: str, store: WorldsStore = Depends(get_worlds_store)):
    return [attempt_to_response(attempt) for attempt in JobService(store).list_job_attempts(job_public_id)]


@router.post("/{job_public_id}/run-once", response_model=JobResponse)
def run_job_once_dev_only(job_public_id: str, store: WorldsStore = Depends(get_worlds_store)):
    try:
        return job_to_response(JobWorker(store).run_one(job_public_id))
    except Exception as error:
        handle_jobs_error(error)
