from __future__ import annotations

import asyncio
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from time import monotonic
from typing import Deque, Dict, Optional

from fastapi import HTTPException

from .schemas import ClipBatchResponse


def timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class JobRecord:
    id: str
    status: str = "queued"
    message: str = "Job queued."
    created_at: str = field(default_factory=timestamp)
    updated_at: str = field(default_factory=timestamp)
    completed_at: Optional[str] = None
    duration_ms: Optional[int] = None
    plan_code: Optional[str] = None
    generation_mode: Optional[str] = None
    rendered_clip_count: Optional[int] = None
    strategy_only_clip_count: Optional[int] = None
    fallback_used: Optional[bool] = None
    error_type: Optional[str] = None
    result: Optional[ClipBatchResponse] = None
    error: Optional[str] = None
    _started_at_monotonic: float = field(default_factory=monotonic, repr=False)


class JobStore:
    def __init__(self, max_jobs: int = 50) -> None:
        self._jobs: Dict[str, JobRecord] = {}
        self._lock = asyncio.Lock()
        self._max_jobs = max_jobs

    async def create(
        self,
        job_id: str,
        message: str,
        *,
        plan_code: str | None = None,
        generation_mode: str | None = None,
    ) -> JobRecord:
        async with self._lock:
            record = JobRecord(
                id=job_id,
                message=message,
                plan_code=plan_code,
                generation_mode=generation_mode,
            )
            self._jobs[job_id] = record
            self._trim()
            return record

    async def get(self, job_id: str) -> Optional[JobRecord]:
        async with self._lock:
            return self._jobs.get(job_id)

    async def update(self, job_id: str, *, status: str, message: str) -> Optional[JobRecord]:
        async with self._lock:
            record = self._jobs.get(job_id)
            if not record:
                return None
            record.status = status
            record.message = message
            record.updated_at = timestamp()
            return record

    async def complete(self, job_id: str, result: ClipBatchResponse) -> Optional[JobRecord]:
        async with self._lock:
            record = self._jobs.get(job_id)
            if not record:
                return None
            record.status = "completed"
            record.message = "Clips ready."
            record.result = result
            record.error = None
            record.updated_at = timestamp()
            record.completed_at = record.updated_at
            record.duration_ms = max(int(round((monotonic() - record._started_at_monotonic) * 1000)), 0)
            record.plan_code = result.processing_summary.plan_code
            record.generation_mode = result.processing_summary.generation_mode
            record.rendered_clip_count = result.processing_summary.rendered_clip_count
            record.strategy_only_clip_count = result.processing_summary.strategy_only_clip_count
            record.fallback_used = bool(result.processing_summary.fallback_reason)
            record.error_type = None
            return record

    async def fail(self, job_id: str, error: str, *, error_type: str | None = None) -> Optional[JobRecord]:
        async with self._lock:
            record = self._jobs.get(job_id)
            if not record:
                return None
            record.status = "failed"
            record.message = "Processing failed."
            record.error = error
            record.updated_at = timestamp()
            record.completed_at = record.updated_at
            record.duration_ms = max(int(round((monotonic() - record._started_at_monotonic) * 1000)), 0)
            record.fallback_used = None
            record.error_type = error_type or "RuntimeError"
            return record

    def _trim(self) -> None:
        if len(self._jobs) <= self._max_jobs:
            return
        overflow = len(self._jobs) - self._max_jobs
        for job_id in sorted(self._jobs.keys(), key=lambda current: self._jobs[current].created_at)[:overflow]:
            del self._jobs[job_id]


class RequestThrottle:
    def __init__(self, *, window_seconds: int = 300, max_requests: int = 8) -> None:
        self._window_seconds = max(window_seconds, 1)
        self._max_requests = max(max_requests, 1)
        self._events: Dict[str, Deque[float]] = {}
        self._lock = asyncio.Lock()

    async def enforce(self, *, subject: str) -> None:
        now = monotonic()
        async with self._lock:
            bucket = self._events.setdefault(subject, deque())
            self._trim_bucket(bucket=bucket, now=now)
            if len(bucket) >= self._max_requests:
                retry_after = max(int(self._window_seconds - (now - bucket[0])), 1)
                raise HTTPException(
                    status_code=429,
                    detail=(
                        f"Too many generation requests in a short window. "
                        f"Wait about {retry_after} seconds and try again."
                    ),
                )
            bucket.append(now)
            self._trim_subjects(now=now)

    def _trim_bucket(self, *, bucket: Deque[float], now: float) -> None:
        while bucket and (now - bucket[0]) >= self._window_seconds:
            bucket.popleft()

    def _trim_subjects(self, *, now: float) -> None:
        stale_subjects = []
        for subject, bucket in self._events.items():
            self._trim_bucket(bucket=bucket, now=now)
            if not bucket:
                stale_subjects.append(subject)
        for subject in stale_subjects:
            self._events.pop(subject, None)
