from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class JobCreateRequest(BaseModel):
    job_type: str
    title: str = ""
    description: str = ""
    priority: str = "normal"
    source_public_id: Optional[str] = None
    target_type: Optional[str] = None
    target_public_id: Optional[str] = None
    input_json: str = "{}"


class JobUpdateRequest(BaseModel):
    status: Optional[str] = None
    progress_percent: Optional[int] = Field(default=None, ge=0, le=100)
    output_json: Optional[str] = None
    error_message: Optional[str] = None


class JobCancelRequest(BaseModel):
    reason: str = "Cancelled by user or admin."


class JobRetryRequest(BaseModel):
    reason: str = "Manual retry requested."


class JobResponse(BaseModel):
    public_id: str
    owner_user_id: Optional[str]
    job_type: str
    status: str
    priority: str
    progress_percent: int
    title: str
    description: str
    source_public_id: Optional[str]
    target_type: Optional[str]
    target_public_id: Optional[str]
    input_json: str
    output_json: str
    error_message: Optional[str]
    max_attempts: int
    attempt_count: int
    next_retry_at: Optional[str]
    started_at: Optional[str]
    completed_at: Optional[str]
    created_at: str
    updated_at: str


class JobEventResponse(BaseModel):
    public_id: str
    job_public_id: str
    event_type: str
    message: str
    status_before: Optional[str]
    status_after: Optional[str]
    progress_percent: Optional[int]
    metadata_json: str
    created_at: str


class JobAttemptResponse(BaseModel):
    public_id: str
    job_public_id: str
    attempt_number: int
    worker_name: Optional[str]
    status: str
    error_message: Optional[str]
    started_at: str
    completed_at: Optional[str]


class JobDashboardResponse(BaseModel):
    queued: int
    running: int
    succeeded: int
    failed: int
    retrying: int
    cancelled: int
    recent_jobs: list[JobResponse]
