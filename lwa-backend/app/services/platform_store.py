from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any, Optional
from uuid import uuid4

from ..models.schemas import ClipBatchResponse
from ..models.user import StoredUser, UserRecord


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


class PlatformStore:
    def __init__(self, path: str) -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._path, check_same_thread=False)
        connection.row_factory = sqlite3.Row
        return connection

    def _init_db(self) -> None:
        with self._lock, self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    email TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    plan TEXT NOT NULL DEFAULT 'free',
                    balance_cents INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS uploads (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    file_name TEXT NOT NULL,
                    stored_path TEXT NOT NULL,
                    public_url TEXT NOT NULL,
                    content_type TEXT,
                    file_size INTEGER NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS campaigns (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    allowed_platforms_json TEXT NOT NULL DEFAULT '[]',
                    target_angle TEXT,
                    requirements TEXT,
                    payout_cents_per_1000_views INTEGER,
                    status TEXT NOT NULL DEFAULT 'draft',
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS batches (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    target_platform TEXT NOT NULL,
                    selected_trend TEXT,
                    status TEXT NOT NULL DEFAULT 'queued',
                    total_sources INTEGER NOT NULL DEFAULT 0,
                    completed_sources INTEGER NOT NULL DEFAULT 0,
                    failed_sources INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS batch_sources (
                    id TEXT PRIMARY KEY,
                    batch_id TEXT NOT NULL,
                    source_kind TEXT NOT NULL,
                    video_url TEXT,
                    upload_id TEXT,
                    status TEXT NOT NULL DEFAULT 'queued',
                    request_id TEXT,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS jobs (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    campaign_id TEXT,
                    source_type TEXT NOT NULL,
                    source_value TEXT NOT NULL,
                    status TEXT NOT NULL,
                    message TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    response_json TEXT
                );

                CREATE TABLE IF NOT EXISTS clips (
                    id TEXT PRIMARY KEY,
                    request_id TEXT NOT NULL,
                    clip_key TEXT NOT NULL,
                    user_id TEXT,
                    campaign_id TEXT,
                    title TEXT NOT NULL,
                    hook TEXT NOT NULL,
                    caption TEXT NOT NULL,
                    start_time TEXT,
                    end_time TEXT,
                    score INTEGER NOT NULL,
                    confidence REAL,
                    rank_value INTEGER,
                    reason TEXT,
                    packaging_angle TEXT,
                    platform_fit TEXT,
                    best_post_order INTEGER,
                    cta_suggestion TEXT,
                    thumbnail_text TEXT,
                    hook_variants_json TEXT NOT NULL,
                    clip_url TEXT,
                    raw_clip_url TEXT,
                    edited_clip_url TEXT,
                    preview_image_url TEXT,
                    local_asset_path TEXT,
                    trim_start_seconds REAL,
                    trim_end_seconds REAL,
                    caption_style_override TEXT,
                    approved INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS transactions (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    amount_cents INTEGER NOT NULL,
                    type TEXT NOT NULL,
                    note TEXT,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS payouts (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    amount_cents INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS publish_requests (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    clip_id TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    caption TEXT,
                    scheduled_for TEXT,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS posting_connections (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    account_label TEXT,
                    is_active INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL
                );
                """
            )
            self._ensure_column(connection, "clips", "trim_start_seconds", "REAL")
            self._ensure_column(connection, "clips", "trim_end_seconds", "REAL")
            self._ensure_column(connection, "clips", "caption_style_override", "TEXT")
            self._ensure_column(connection, "clips", "start_time", "TEXT")
            self._ensure_column(connection, "clips", "end_time", "TEXT")
            self._ensure_column(connection, "campaigns", "description", "TEXT")
            self._ensure_column(connection, "campaigns", "allowed_platforms_json", "TEXT NOT NULL DEFAULT '[]'")
            self._ensure_column(connection, "campaigns", "target_angle", "TEXT")
            self._ensure_column(connection, "campaigns", "requirements", "TEXT")
            self._ensure_column(connection, "campaigns", "payout_cents_per_1000_views", "INTEGER")
            self._ensure_column(connection, "publish_requests", "caption", "TEXT")
            self._ensure_column(connection, "publish_requests", "scheduled_for", "TEXT")

    def _ensure_column(self, connection: sqlite3.Connection, table: str, column: str, column_type: str) -> None:
        rows = connection.execute(f"PRAGMA table_info({table})").fetchall()
        existing = {row["name"] for row in rows}
        if column in existing:
            return
        connection.execute(f"ALTER TABLE {table} ADD COLUMN {column} {column_type}")

    def create_user(self, *, email: str, password_hash: str, plan: str = "free") -> UserRecord:
        user_id = f"user_{uuid4().hex[:12]}"
        created_at = utcnow()
        with self._lock, self._connect() as connection:
            try:
                connection.execute(
                    """
                    INSERT INTO users (id, email, password_hash, plan, balance_cents, created_at)
                    VALUES (?, ?, ?, ?, 0, ?)
                    """,
                    (user_id, email.lower(), password_hash, plan, created_at),
                )
            except sqlite3.IntegrityError as error:
                raise ValueError("Email is already registered") from error
        return UserRecord(id=user_id, email=email.lower(), plan=plan, balance_cents=0, created_at=created_at)

    def get_user_by_email(self, email: str) -> Optional[StoredUser]:
        with self._lock, self._connect() as connection:
            row = connection.execute(
                "SELECT id, email, password_hash, plan, balance_cents, created_at FROM users WHERE email = ?",
                (email.lower(),),
            ).fetchone()
        return self._user_from_row(row)

    def get_user_by_id(self, user_id: str) -> Optional[UserRecord]:
        with self._lock, self._connect() as connection:
            row = connection.execute(
                "SELECT id, email, password_hash, plan, balance_cents, created_at FROM users WHERE id = ?",
                (user_id,),
            ).fetchone()
        stored = self._user_from_row(row)
        if not stored:
            return None
        return UserRecord(
            id=stored.id,
            email=stored.email,
            plan=stored.plan,
            balance_cents=stored.balance_cents,
            created_at=stored.created_at,
        )

    def create_upload(
        self,
        *,
        user_id: str,
        file_name: str,
        stored_path: str,
        public_url: str,
        content_type: str | None,
        file_size: int,
    ) -> dict[str, Any]:
        upload_id = f"upload_{uuid4().hex[:12]}"
        created_at = utcnow()
        with self._lock, self._connect() as connection:
            connection.execute(
                """
                INSERT INTO uploads (id, user_id, file_name, stored_path, public_url, content_type, file_size, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (upload_id, user_id, file_name, stored_path, public_url, content_type, file_size, created_at),
            )
        return {
            "id": upload_id,
            "user_id": user_id,
            "file_name": file_name,
            "stored_path": stored_path,
            "public_url": public_url,
            "content_type": content_type,
            "file_size": file_size,
            "created_at": created_at,
        }

    def get_upload(self, upload_id: str, *, user_id: str | None = None) -> Optional[dict[str, Any]]:
        query = """
            SELECT id, user_id, file_name, stored_path, public_url, content_type, file_size, created_at
            FROM uploads WHERE id = ?
        """
        parameters: tuple[object, ...] = (upload_id,)
        if user_id:
            query += " AND user_id = ?"
            parameters = (upload_id, user_id)
        with self._lock, self._connect() as connection:
            row = connection.execute(query, parameters).fetchone()
        if not row:
            return None
        return dict(row)

    def list_uploads(self, *, user_id: str) -> list[dict[str, Any]]:
        with self._lock, self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id, user_id, file_name, stored_path, public_url, content_type, file_size, created_at
                FROM uploads
                WHERE user_id = ?
                ORDER BY created_at DESC
                """,
                (user_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def create_campaign(
        self,
        *,
        user_id: str,
        name: str,
        description: str | None = None,
        allowed_platforms: list[str] | None = None,
        target_angle: str | None = None,
        requirements: str | None = None,
        payout_cents_per_1000_views: int | None = None,
    ) -> dict[str, Any]:
        campaign_id = f"campaign_{uuid4().hex[:12]}"
        created_at = utcnow()
        with self._lock, self._connect() as connection:
            connection.execute(
                """
                INSERT INTO campaigns (
                    id, user_id, name, description, allowed_platforms_json, target_angle,
                    requirements, payout_cents_per_1000_views, status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'draft', ?)
                """,
                (
                    campaign_id,
                    user_id,
                    name,
                    description,
                    json.dumps(allowed_platforms or []),
                    target_angle,
                    requirements,
                    payout_cents_per_1000_views,
                    created_at,
                ),
            )
        return {
            "id": campaign_id,
            "user_id": user_id,
            "name": name,
            "description": description,
            "allowed_platforms": allowed_platforms or [],
            "target_angle": target_angle,
            "requirements": requirements,
            "payout_cents_per_1000_views": payout_cents_per_1000_views,
            "status": "draft",
            "created_at": created_at,
        }

    def list_campaigns(self, *, user_id: str) -> list[dict[str, Any]]:
        with self._lock, self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id, user_id, name, description, allowed_platforms_json, target_angle,
                       requirements, payout_cents_per_1000_views, status, created_at
                FROM campaigns
                WHERE user_id = ?
                ORDER BY created_at DESC
                """,
                (user_id,),
            ).fetchall()
        return [self._campaign_payload_from_row(row) for row in rows]

    def get_campaign(self, *, campaign_id: str, user_id: str) -> Optional[dict[str, Any]]:
        with self._lock, self._connect() as connection:
            campaign = connection.execute(
                """
                SELECT id, user_id, name, description, allowed_platforms_json, target_angle,
                       requirements, payout_cents_per_1000_views, status, created_at
                FROM campaigns
                WHERE id = ? AND user_id = ?
                """,
                (campaign_id, user_id),
            ).fetchone()
            if not campaign:
                return None
            clips = connection.execute(
                """
                SELECT id, request_id, clip_key, title, hook, caption, score, confidence, rank_value,
                       reason, packaging_angle, platform_fit, best_post_order, cta_suggestion,
                       thumbnail_text, hook_variants_json, clip_url, raw_clip_url, edited_clip_url,
                       preview_image_url, trim_start_seconds, trim_end_seconds, caption_style_override,
                       approved, created_at
                FROM clips
                WHERE campaign_id = ?
                ORDER BY rank_value ASC, score DESC, created_at DESC
                """,
                (campaign_id,),
            ).fetchall()
            jobs = connection.execute(
                """
                SELECT id, status, message, created_at, updated_at
                FROM jobs
                WHERE campaign_id = ?
                ORDER BY created_at DESC
                """,
                (campaign_id,),
            ).fetchall()
        return {
            "campaign": self._campaign_payload_from_row(campaign),
            "clips": [self._clip_payload_from_row(row) for row in clips],
            "jobs": [dict(row) for row in jobs],
        }

    def update_campaign(self, *, campaign_id: str, user_id: str, updates: dict[str, Any]) -> Optional[dict[str, Any]]:
        allowed_keys = {
            "name": "name",
            "description": "description",
            "allowed_platforms": "allowed_platforms_json",
            "target_angle": "target_angle",
            "requirements": "requirements",
            "payout_cents_per_1000_views": "payout_cents_per_1000_views",
            "status": "status",
        }
        assignments = []
        values: list[Any] = []
        for key, column in allowed_keys.items():
            if key not in updates:
                continue
            value = updates[key]
            if key == "allowed_platforms":
                value = json.dumps(value or [])
            assignments.append(f"{column} = ?")
            values.append(value)
        if not assignments:
            return self.get_campaign(campaign_id=campaign_id, user_id=user_id)
        values.extend([campaign_id, user_id])
        with self._lock, self._connect() as connection:
            result = connection.execute(
                f"UPDATE campaigns SET {', '.join(assignments)} WHERE id = ? AND user_id = ?",
                tuple(values),
            )
            if not result.rowcount:
                return None
            row = connection.execute(
                """
                SELECT id, user_id, name, description, allowed_platforms_json, target_angle,
                       requirements, payout_cents_per_1000_views, status, created_at
                FROM campaigns
                WHERE id = ? AND user_id = ?
                """,
                (campaign_id, user_id),
            ).fetchone()
        return self._campaign_payload_from_row(row) if row else None

    def create_batch(
        self,
        *,
        user_id: str,
        title: str,
        target_platform: str,
        selected_trend: str | None,
        sources: list[dict[str, Any]],
    ) -> dict[str, Any]:
        batch_id = f"batch_{uuid4().hex[:12]}"
        created_at = utcnow()
        with self._lock, self._connect() as connection:
            connection.execute(
                """
                INSERT INTO batches (
                    id, user_id, title, target_platform, selected_trend, status,
                    total_sources, completed_sources, failed_sources, created_at
                ) VALUES (?, ?, ?, ?, ?, 'queued', ?, 0, 0, ?)
                """,
                (batch_id, user_id, title, target_platform, selected_trend, len(sources), created_at),
            )
            for source in sources:
                connection.execute(
                    """
                    INSERT INTO batch_sources (id, batch_id, source_kind, video_url, upload_id, status, request_id, created_at)
                    VALUES (?, ?, ?, ?, ?, 'queued', NULL, ?)
                    """,
                    (
                        f"bsrc_{uuid4().hex[:12]}",
                        batch_id,
                        source.get("source_kind"),
                        source.get("video_url"),
                        source.get("upload_id"),
                        created_at,
                    ),
                )
        return {
            "id": batch_id,
            "owner_user_id": user_id,
            "title": title,
            "target_platform": target_platform,
            "status": "queued",
            "total_sources": len(sources),
            "completed_sources": 0,
            "failed_sources": 0,
            "selected_trend": selected_trend,
            "created_at": created_at,
        }

    def list_batches(self, *, user_id: str) -> list[dict[str, Any]]:
        with self._lock, self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id, user_id, title, target_platform, status, total_sources,
                       completed_sources, failed_sources, created_at
                FROM batches
                WHERE user_id = ?
                ORDER BY created_at DESC
                """,
                (user_id,),
            ).fetchall()
        return [
            {
                "id": row["id"],
                "owner_user_id": row["user_id"],
                "title": row["title"],
                "target_platform": row["target_platform"],
                "status": row["status"],
                "total_sources": row["total_sources"],
                "completed_sources": row["completed_sources"],
                "failed_sources": row["failed_sources"],
                "created_at": row["created_at"],
            }
            for row in rows
        ]

    def get_batch(self, *, batch_id: str, user_id: str) -> Optional[dict[str, Any]]:
        with self._lock, self._connect() as connection:
            batch = connection.execute(
                """
                SELECT id, user_id, title, target_platform, selected_trend, status, total_sources,
                       completed_sources, failed_sources, created_at
                FROM batches
                WHERE id = ? AND user_id = ?
                """,
                (batch_id, user_id),
            ).fetchone()
            if not batch:
                return None
            sources = connection.execute(
                """
                SELECT id, source_kind, video_url, upload_id, status, request_id, created_at
                FROM batch_sources
                WHERE batch_id = ?
                ORDER BY created_at ASC
                """,
                (batch_id,),
            ).fetchall()
        return {
            "batch": {
                "id": batch["id"],
                "owner_user_id": batch["user_id"],
                "title": batch["title"],
                "target_platform": batch["target_platform"],
                "selected_trend": batch["selected_trend"],
                "status": batch["status"],
                "total_sources": batch["total_sources"],
                "completed_sources": batch["completed_sources"],
                "failed_sources": batch["failed_sources"],
                "created_at": batch["created_at"],
            },
            "sources": [dict(row) for row in sources],
        }

    def attach_batch_source_request(self, *, batch_id: str, source_id: str, request_id: str, status: str) -> None:
        with self._lock, self._connect() as connection:
            connection.execute(
                "UPDATE batch_sources SET request_id = ?, status = ? WHERE id = ? AND batch_id = ?",
                (request_id, status, source_id, batch_id),
            )

    def update_batch_progress(self, *, batch_id: str, completed_increment: int = 0, failed_increment: int = 0, status: str | None = None) -> None:
        with self._lock, self._connect() as connection:
            connection.execute(
                """
                UPDATE batches
                SET completed_sources = completed_sources + ?,
                    failed_sources = failed_sources + ?,
                    status = COALESCE(?, status)
                WHERE id = ?
                """,
                (completed_increment, failed_increment, status, batch_id),
            )

    def create_job(
        self,
        *,
        job_id: str,
        user_id: str | None,
        campaign_id: str | None,
        source_type: str,
        source_value: str,
        status: str,
        message: str,
    ) -> None:
        created_at = utcnow()
        with self._lock, self._connect() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO jobs (id, user_id, campaign_id, source_type, source_value, status, message, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (job_id, user_id, campaign_id, source_type, source_value, status, message, created_at, created_at),
            )

    def update_job(
        self,
        *,
        job_id: str,
        status: str,
        message: str,
        response_json: str | None = None,
    ) -> None:
        updated_at = utcnow()
        with self._lock, self._connect() as connection:
            connection.execute(
                """
                UPDATE jobs
                SET status = ?, message = ?, updated_at = ?, response_json = COALESCE(?, response_json)
                WHERE id = ?
                """,
                (status, message, updated_at, response_json, job_id),
            )

    def persist_clip_batch(
        self,
        *,
        request_id: str,
        user_id: str | None,
        campaign_id: str | None,
        response: ClipBatchResponse,
        local_asset_paths: dict[str, str] | None = None,
    ) -> ClipBatchResponse:
        local_asset_paths = local_asset_paths or {}
        persisted_clips = []
        created_at = utcnow()
        with self._lock, self._connect() as connection:
            for clip in response.clips:
                record_id = clip.record_id or f"cliprec_{uuid4().hex[:12]}"
                connection.execute(
                    """
                    INSERT OR REPLACE INTO clips (
                        id, request_id, clip_key, user_id, campaign_id, title, hook, caption, start_time, end_time, score,
                        confidence, rank_value, reason, packaging_angle, platform_fit, best_post_order,
                        cta_suggestion, thumbnail_text, hook_variants_json, clip_url, raw_clip_url,
                        edited_clip_url, preview_image_url, local_asset_path, trim_start_seconds,
                        trim_end_seconds, caption_style_override, approved, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        record_id,
                        request_id,
                        clip.id,
                        user_id,
                        campaign_id,
                        clip.title,
                        clip.hook,
                        clip.caption,
                        clip.start_time,
                        clip.end_time,
                        clip.score,
                        clip.confidence,
                        clip.rank,
                        clip.reason or clip.why_this_matters,
                        clip.packaging_angle,
                        clip.platform_fit,
                        clip.best_post_order or clip.post_rank,
                        clip.cta_suggestion,
                        clip.thumbnail_text,
                        json.dumps(clip.hook_variants),
                        clip.clip_url,
                        clip.raw_clip_url,
                        clip.edited_clip_url,
                        clip.preview_image_url,
                        local_asset_paths.get(clip.id),
                        None,
                        None,
                        clip.caption_style,
                        0,
                        created_at,
                    ),
                )
                persisted_clips.append(clip.model_copy(update={"record_id": record_id}))
        return response.model_copy(update={"clips": persisted_clips})

    def approve_campaign(self, *, campaign_id: str, user_id: str, clip_ids: list[str] | None = None) -> int:
        with self._lock, self._connect() as connection:
            campaign = connection.execute(
                "SELECT id FROM campaigns WHERE id = ? AND user_id = ?",
                (campaign_id, user_id),
            ).fetchone()
            if not campaign:
                return 0
            if clip_ids:
                placeholders = ",".join("?" for _ in clip_ids)
                result = connection.execute(
                    f"UPDATE clips SET approved = 1 WHERE campaign_id = ? AND id IN ({placeholders})",
                    (campaign_id, *clip_ids),
                )
            else:
                result = connection.execute(
                    "UPDATE clips SET approved = 1 WHERE campaign_id = ?",
                    (campaign_id,),
                )
            connection.execute(
                "UPDATE campaigns SET status = 'approved' WHERE id = ?",
                (campaign_id,),
            )
        return int(result.rowcount or 0)

    def get_clip(self, *, clip_id: str, user_id: str | None = None) -> Optional[dict[str, Any]]:
        query = """
            SELECT id, request_id, clip_key, user_id, campaign_id, title, hook, caption, start_time, end_time, score, confidence,
                   rank_value, reason, packaging_angle, platform_fit, best_post_order, cta_suggestion,
                   thumbnail_text, hook_variants_json, clip_url, raw_clip_url, edited_clip_url, preview_image_url,
                   local_asset_path, trim_start_seconds, trim_end_seconds, caption_style_override,
                   approved, created_at
            FROM clips
            WHERE id = ?
        """
        params: tuple[object, ...] = (clip_id,)
        if user_id:
            query += " AND user_id = ?"
            params = (clip_id, user_id)
        with self._lock, self._connect() as connection:
            row = connection.execute(query, params).fetchone()
        if not row:
            return None
        return self._clip_payload_from_row(row)

    def update_clip_edit(
        self,
        *,
        clip_id: str,
        user_id: str,
        caption: str,
        edited_clip_url: str,
        local_asset_path: str,
        trim_start_seconds: float | None = None,
        trim_end_seconds: float | None = None,
        hook: str | None = None,
        cta_suggestion: str | None = None,
        thumbnail_text: str | None = None,
        caption_style_override: str | None = None,
        packaging_angle: str | None = None,
    ) -> Optional[dict[str, Any]]:
        with self._lock, self._connect() as connection:
            result = connection.execute(
                """
                UPDATE clips
                SET caption = ?, edited_clip_url = ?, clip_url = ?, local_asset_path = ?,
                    trim_start_seconds = ?, trim_end_seconds = ?,
                    hook = COALESCE(?, hook),
                    cta_suggestion = COALESCE(?, cta_suggestion),
                    thumbnail_text = COALESCE(?, thumbnail_text),
                    caption_style_override = COALESCE(?, caption_style_override),
                    packaging_angle = COALESCE(?, packaging_angle)
                WHERE id = ? AND user_id = ?
                """,
                (
                    caption,
                    edited_clip_url,
                    edited_clip_url,
                    local_asset_path,
                    trim_start_seconds,
                    trim_end_seconds,
                    hook,
                    cta_suggestion,
                    thumbnail_text,
                    caption_style_override,
                    packaging_angle,
                    clip_id,
                    user_id,
                ),
            )
            if not result.rowcount:
                return None
            row = connection.execute(
                """
                SELECT id, request_id, clip_key, user_id, campaign_id, title, hook, caption, start_time, end_time, score, confidence,
                       rank_value, reason, packaging_angle, platform_fit, best_post_order, cta_suggestion,
                       thumbnail_text, hook_variants_json, clip_url, raw_clip_url, edited_clip_url, preview_image_url,
                       local_asset_path, trim_start_seconds, trim_end_seconds, caption_style_override,
                       approved, created_at
                FROM clips WHERE id = ?
                """,
                (clip_id,),
            ).fetchone()
        return self._clip_payload_from_row(row) if row else None

    def list_public_clips(self, *, limit: int = 50) -> list[dict[str, Any]]:
        with self._lock, self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id, request_id, clip_key, user_id, campaign_id, title, hook, caption, start_time, end_time, score, confidence,
                       rank_value, reason, packaging_angle, platform_fit, best_post_order, cta_suggestion,
                       thumbnail_text, hook_variants_json, clip_url, raw_clip_url, edited_clip_url, preview_image_url,
                       local_asset_path, trim_start_seconds, trim_end_seconds, caption_style_override,
                       approved, created_at
                FROM clips
                WHERE approved = 1
                ORDER BY created_at DESC, score DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [self._clip_payload_from_row(row) for row in rows]

    def update_clip_metadata(self, *, clip_id: str, user_id: str, updates: dict[str, Any]) -> Optional[dict[str, Any]]:
        mapping = {
            "caption_override": "caption",
            "hook_override": "hook",
            "cta_override": "cta_suggestion",
            "thumbnail_text_override": "thumbnail_text",
            "caption_style_override": "caption_style_override",
            "packaging_angle_override": "packaging_angle",
            "trim_start_seconds": "trim_start_seconds",
            "trim_end_seconds": "trim_end_seconds",
        }
        assignments = []
        values: list[Any] = []
        for key, column in mapping.items():
            if key not in updates:
                continue
            assignments.append(f"{column} = ?")
            values.append(updates[key])
        if not assignments:
            return self.get_clip(clip_id=clip_id, user_id=user_id)
        values.extend([clip_id, user_id])
        with self._lock, self._connect() as connection:
            result = connection.execute(
                f"UPDATE clips SET {', '.join(assignments)} WHERE id = ? AND user_id = ?",
                tuple(values),
            )
            if not result.rowcount:
                return None
            row = connection.execute(
                """
                SELECT id, request_id, clip_key, user_id, campaign_id, title, hook, caption, start_time, end_time, score, confidence,
                       rank_value, reason, packaging_angle, platform_fit, best_post_order, cta_suggestion,
                       thumbnail_text, hook_variants_json, clip_url, raw_clip_url, edited_clip_url, preview_image_url,
                       local_asset_path, trim_start_seconds, trim_end_seconds, caption_style_override,
                       approved, created_at
                FROM clips WHERE id = ?
                """,
                (clip_id,),
            ).fetchone()
        return self._clip_payload_from_row(row) if row else None

    def list_clip_packs(self, *, user_id: str) -> list[dict[str, Any]]:
        with self._lock, self._connect() as connection:
            rows = connection.execute(
                """
                SELECT request_id, COUNT(*) AS clip_count, MAX(score) AS top_score, MAX(created_at) AS created_at
                FROM clips
                WHERE user_id = ?
                GROUP BY request_id
                ORDER BY created_at DESC
                """,
                (user_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def get_clip_pack(self, *, user_id: str, request_id: str) -> dict[str, Any]:
        with self._lock, self._connect() as connection:
            clips = connection.execute(
                """
                SELECT id, request_id, clip_key, user_id, campaign_id, title, hook, caption, start_time, end_time, score, confidence,
                       rank_value, reason, packaging_angle, platform_fit, best_post_order, cta_suggestion,
                       thumbnail_text, hook_variants_json, clip_url, raw_clip_url, edited_clip_url, preview_image_url,
                       local_asset_path, trim_start_seconds, trim_end_seconds, caption_style_override,
                       approved, created_at
                FROM clips
                WHERE user_id = ? AND request_id = ?
                ORDER BY rank_value ASC, score DESC
                """,
                (user_id, request_id),
            ).fetchall()
        return {
            "request_id": request_id,
            "clips": [self._clip_payload_from_row(row) for row in clips],
        }

    def create_publish_request(self, *, user_id: str, clip_id: str, platform: str) -> dict[str, Any]:
        publish_id = f"publish_{uuid4().hex[:12]}"
        created_at = utcnow()
        with self._lock, self._connect() as connection:
            connection.execute(
                """
                INSERT INTO publish_requests (id, user_id, clip_id, platform, caption, scheduled_for, status, created_at)
                VALUES (?, ?, ?, ?, NULL, NULL, 'queued', ?)
                """,
                (publish_id, user_id, clip_id, platform, created_at),
            )
        return {
            "id": publish_id,
            "user_id": user_id,
            "clip_id": clip_id,
            "platform": platform,
            "status": "queued",
            "created_at": created_at,
        }

    def list_posting_connections(self, *, user_id: str) -> list[dict[str, Any]]:
        with self._lock, self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id, user_id, provider, account_label, is_active, created_at
                FROM posting_connections
                WHERE user_id = ?
                ORDER BY created_at DESC
                """,
                (user_id,),
            ).fetchall()
        return [dict(row) | {"is_active": bool(row["is_active"])} for row in rows]

    def create_posting_connection(self, *, user_id: str, provider: str, account_label: str | None) -> dict[str, Any]:
        connection_id = f"pconn_{uuid4().hex[:12]}"
        created_at = utcnow()
        with self._lock, self._connect() as connection:
            connection.execute(
                """
                INSERT INTO posting_connections (id, user_id, provider, account_label, is_active, created_at)
                VALUES (?, ?, ?, ?, 1, ?)
                """,
                (connection_id, user_id, provider, account_label, created_at),
            )
        return {
            "id": connection_id,
            "user_id": user_id,
            "provider": provider,
            "account_label": account_label,
            "is_active": True,
            "created_at": created_at,
        }

    def list_scheduled_posts(self, *, user_id: str) -> list[dict[str, Any]]:
        with self._lock, self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id, user_id, clip_id, platform, caption, scheduled_for, status, created_at
                FROM publish_requests
                WHERE user_id = ?
                ORDER BY created_at DESC
                """,
                (user_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def create_scheduled_post(
        self,
        *,
        user_id: str,
        clip_id: str,
        provider: str,
        caption: str | None,
        scheduled_for: str | None,
    ) -> dict[str, Any]:
        request_id = f"spost_{uuid4().hex[:12]}"
        created_at = utcnow()
        status = "scheduled" if scheduled_for else "queued"
        with self._lock, self._connect() as connection:
            connection.execute(
                """
                INSERT INTO publish_requests (id, user_id, clip_id, platform, caption, scheduled_for, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (request_id, user_id, clip_id, provider, caption, scheduled_for, status, created_at),
            )
        return {
            "id": request_id,
            "owner_user_id": user_id,
            "provider": provider,
            "status": status,
            "scheduled_for": scheduled_for,
            "clip_id": clip_id,
            "caption": caption,
            "created_at": created_at,
        }

    def update_scheduled_post(self, *, post_id: str, user_id: str, updates: dict[str, Any]) -> Optional[dict[str, Any]]:
        allowed = {"status", "caption", "scheduled_for"}
        assignments = []
        values: list[Any] = []
        for key in allowed:
            if key not in updates:
                continue
            assignments.append(f"{key} = ?")
            values.append(updates[key])
        if not assignments:
            return None
        values.extend([post_id, user_id])
        with self._lock, self._connect() as connection:
            result = connection.execute(
                f"UPDATE publish_requests SET {', '.join(assignments)} WHERE id = ? AND user_id = ?",
                tuple(values),
            )
            if not result.rowcount:
                return None
            row = connection.execute(
                """
                SELECT id, user_id, clip_id, platform, caption, scheduled_for, status, created_at
                FROM publish_requests
                WHERE id = ? AND user_id = ?
                """,
                (post_id, user_id),
            ).fetchone()
        if not row:
            return None
        return {
            "id": row["id"],
            "owner_user_id": row["user_id"],
            "provider": row["platform"],
            "status": row["status"],
            "scheduled_for": row["scheduled_for"],
            "clip_id": row["clip_id"],
            "caption": row["caption"],
            "created_at": row["created_at"],
        }

    def add_transaction(self, *, user_id: str, amount_cents: int, transaction_type: str, note: str | None = None) -> dict[str, Any]:
        transaction_id = f"txn_{uuid4().hex[:12]}"
        created_at = utcnow()
        with self._lock, self._connect() as connection:
            connection.execute(
                """
                INSERT INTO transactions (id, user_id, amount_cents, type, note, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (transaction_id, user_id, amount_cents, transaction_type, note, created_at),
            )
            connection.execute(
                "UPDATE users SET balance_cents = balance_cents + ? WHERE id = ?",
                (amount_cents, user_id),
            )
            row = connection.execute(
                "SELECT balance_cents FROM users WHERE id = ?",
                (user_id,),
            ).fetchone()
        return {
            "id": transaction_id,
            "user_id": user_id,
            "amount_cents": amount_cents,
            "type": transaction_type,
            "note": note,
            "balance_cents": int(row["balance_cents"]) if row else 0,
            "created_at": created_at,
        }

    def request_payout(self, *, user_id: str, amount_cents: int) -> dict[str, Any]:
        payout_id = f"payout_{uuid4().hex[:12]}"
        created_at = utcnow()
        with self._lock, self._connect() as connection:
            row = connection.execute(
                "SELECT balance_cents FROM users WHERE id = ?",
                (user_id,),
            ).fetchone()
            balance = int(row["balance_cents"]) if row else 0
            if amount_cents > balance:
                raise ValueError("Insufficient balance")
            connection.execute(
                "UPDATE users SET balance_cents = balance_cents - ? WHERE id = ?",
                (amount_cents, user_id),
            )
            connection.execute(
                """
                INSERT INTO payouts (id, user_id, amount_cents, status, created_at)
                VALUES (?, ?, ?, 'pending', ?)
                """,
                (payout_id, user_id, amount_cents, created_at),
            )
            updated = connection.execute(
                "SELECT balance_cents FROM users WHERE id = ?",
                (user_id,),
            ).fetchone()
        return {
            "id": payout_id,
            "user_id": user_id,
            "amount_cents": amount_cents,
            "status": "pending",
            "balance_cents": int(updated["balance_cents"]) if updated else 0,
            "created_at": created_at,
        }

    def get_wallet(self, *, user_id: str) -> dict[str, Any]:
        with self._lock, self._connect() as connection:
            user = connection.execute(
                "SELECT balance_cents FROM users WHERE id = ?",
                (user_id,),
            ).fetchone()
            transactions = connection.execute(
                """
                SELECT id, amount_cents, type, note, created_at
                FROM transactions
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT 20
                """,
                (user_id,),
            ).fetchall()
            payouts = connection.execute(
                """
                SELECT id, amount_cents, status, created_at
                FROM payouts
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT 20
                """,
                (user_id,),
            ).fetchall()
        return {
            "balance_cents": int(user["balance_cents"]) if user else 0,
            "transactions": [dict(row) for row in transactions],
            "payouts": [dict(row) for row in payouts],
        }

    def list_ledger_entries(self, *, user_id: str, limit: int = 50) -> list[dict[str, Any]]:
        with self._lock, self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id, user_id, amount_cents, type, note, created_at
                FROM transactions
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (user_id, limit),
            ).fetchall()
        return [dict(row) for row in rows]

    def _user_from_row(self, row: sqlite3.Row | None) -> Optional[StoredUser]:
        if not row:
            return None
        return StoredUser(
            id=row["id"],
            email=row["email"],
            password_hash=row["password_hash"],
            plan=row["plan"],
            balance_cents=int(row["balance_cents"]),
            created_at=row["created_at"],
        )

    def _clip_payload_from_row(self, row: sqlite3.Row) -> dict[str, Any]:
        return {
            "record_id": row["id"],
            "request_id": row["request_id"],
            "clip_id": row["clip_key"],
            "title": row["title"],
            "hook": row["hook"],
            "caption": row["caption"],
            "start_time": row["start_time"],
            "end_time": row["end_time"],
            "score": row["score"],
            "confidence": row["confidence"],
            "rank": row["rank_value"],
            "reason": row["reason"],
            "packaging_angle": row["packaging_angle"],
            "platform_fit": row["platform_fit"],
            "best_post_order": row["best_post_order"],
            "cta_suggestion": row["cta_suggestion"],
            "thumbnail_text": row["thumbnail_text"],
            "hook_variants": json.loads(row["hook_variants_json"] or "[]"),
            "clip_url": row["clip_url"],
            "raw_clip_url": row["raw_clip_url"],
            "edited_clip_url": row["edited_clip_url"],
            "preview_image_url": row["preview_image_url"],
            "trim_start_seconds": row["trim_start_seconds"],
            "trim_end_seconds": row["trim_end_seconds"],
            "caption_style_override": row["caption_style_override"],
            "approved": bool(row["approved"]),
            "created_at": row["created_at"],
        }

    def _campaign_payload_from_row(self, row: sqlite3.Row) -> dict[str, Any]:
        return {
            "id": row["id"],
            "owner_user_id": row["user_id"],
            "title": row["name"],
            "description": row["description"],
            "allowed_platforms": json.loads(row["allowed_platforms_json"] or "[]"),
            "target_angle": row["target_angle"],
            "requirements": row["requirements"],
            "payout_cents_per_1000_views": row["payout_cents_per_1000_views"],
            "status": row["status"],
            "created_at": row["created_at"],
        }
