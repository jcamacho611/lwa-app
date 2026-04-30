from __future__ import annotations

from datetime import datetime, timedelta, timezone


RETRYABLE_STATUSES = {"failed", "expired"}
TERMINAL_STATUSES = {"succeeded", "cancelled", "failed", "expired"}
ACTIVE_STATUSES = {"queued", "running", "waiting", "retrying"}

ALLOWED_STATUS_TRANSITIONS = {
    "queued": {"running", "cancelled", "expired"},
    "running": {"waiting", "succeeded", "failed", "cancelled", "retrying"},
    "waiting": {"running", "failed", "cancelled", "expired"},
    "retrying": {"queued", "running", "failed", "cancelled", "expired"},
    "failed": {"retrying", "cancelled"},
    "succeeded": set(),
    "cancelled": set(),
    "expired": {"retrying", "cancelled"},
}


def can_transition(before: str, after: str) -> bool:
    return after in ALLOWED_STATUS_TRANSITIONS.get(before, set())


def is_terminal(status: str) -> bool:
    return status in TERMINAL_STATUSES


def is_active(status: str) -> bool:
    return status in ACTIVE_STATUSES


def can_retry(status: str, attempt_count: int, max_attempts: int) -> bool:
    return status in RETRYABLE_STATUSES and attempt_count < max_attempts


def next_retry_time(attempt_count: int) -> str:
    minutes = min(30, 2 ** max(0, attempt_count - 1))
    return (datetime.now(timezone.utc) + timedelta(minutes=minutes)).isoformat()


def clamp_progress(progress_percent: int) -> int:
    return max(0, min(100, progress_percent))


def default_max_attempts(job_type: str) -> int:
    if job_type in {"render_generation", "clip_generation", "transcript_generation"}:
        return 3
    if job_type in {"social_import", "trend_import"}:
        return 2
    if job_type in {"ugc_moderation_scan", "ai_clip_score"}:
        return 2
    return 3
