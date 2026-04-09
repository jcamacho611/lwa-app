from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Optional

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
    result: Optional[ClipBatchResponse] = None
    error: Optional[str] = None


class JobStore:
    def __init__(self, max_jobs: int = 50) -> None:
        self._jobs: Dict[str, JobRecord] = {}
        self._lock = asyncio.Lock()
        self._max_jobs = max_jobs

    async def create(self, job_id: str, message: str) -> JobRecord:
        async with self._lock:
            record = JobRecord(id=job_id, message=message)
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
            return record

    async def fail(self, job_id: str, error: str) -> Optional[JobRecord]:
        async with self._lock:
            record = self._jobs.get(job_id)
            if not record:
                return None
            record.status = "failed"
            record.message = "Processing failed."
            record.error = error
            record.updated_at = timestamp()
            return record

    def _trim(self) -> None:
        if len(self._jobs) <= self._max_jobs:
            return
        overflow = len(self._jobs) - self._max_jobs
        for job_id in sorted(self._jobs.keys(), key=lambda current: self._jobs[current].created_at)[:overflow]:
            del self._jobs[job_id]
