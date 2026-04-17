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
                    role TEXT NOT NULL DEFAULT 'creator',
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
                    source_type TEXT,
                    source_title TEXT,
                    source_platform TEXT,
                    source_transcript TEXT,
                    source_visual_summary TEXT,
                    source_preview_asset_url TEXT,
                    source_download_asset_url TEXT,
                    source_thumbnail_url TEXT,
                    title TEXT NOT NULL,
                    hook TEXT NOT NULL,
                    caption TEXT NOT NULL,
                    start_time TEXT,
                    end_time TEXT,
                    duration_seconds INTEGER,
                    score INTEGER NOT NULL,
                    virality_score INTEGER,
                    confidence REAL,
                    confidence_score INTEGER,
                    rank_value INTEGER,
                    reason TEXT,
                    why_this_matters TEXT,
                    clip_format TEXT,
                    transcript_excerpt TEXT,
                    packaging_angle TEXT,
                    platform_fit TEXT,
                    post_rank INTEGER,
                    best_post_order INTEGER,
                    cta_suggestion TEXT,
                    thumbnail_text TEXT,
                    hook_variants_json TEXT NOT NULL,
                    caption_variants_json TEXT NOT NULL DEFAULT '{}',
                    clip_url TEXT,
                    download_url TEXT,
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

                CREATE TABLE IF NOT EXISTS campaign_assignments (
                    id TEXT PRIMARY KEY,
                    campaign_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    request_id TEXT,
                    clip_id TEXT,
                    assignment_kind TEXT NOT NULL,
                    title TEXT,
                    hook TEXT,
                    target_platform TEXT,
                    packaging_angle TEXT,
                    assignee_role TEXT NOT NULL DEFAULT 'creator',
                    assignee_label TEXT,
                    status TEXT NOT NULL DEFAULT 'draft',
                    payout_state TEXT NOT NULL DEFAULT 'locked',
                    payout_amount_cents INTEGER,
                    note TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                """
            )
            self._ensure_column(connection, "users", "role", "TEXT NOT NULL DEFAULT 'creator'")
            self._ensure_column(connection, "clips", "trim_start_seconds", "REAL")
            self._ensure_column(connection, "clips", "trim_end_seconds", "REAL")
            self._ensure_column(connection, "clips", "caption_style_override", "TEXT")
            self._ensure_column(connection, "clips", "source_type", "TEXT")
            self._ensure_column(connection, "clips", "source_title", "TEXT")
            self._ensure_column(connection, "clips", "source_platform", "TEXT")
            self._ensure_column(connection, "clips", "source_transcript", "TEXT")
            self._ensure_column(connection, "clips", "source_visual_summary", "TEXT")
            self._ensure_column(connection, "clips", "source_preview_asset_url", "TEXT")
            self._ensure_column(connection, "clips", "source_download_asset_url", "TEXT")
            self._ensure_column(connection, "clips", "source_thumbnail_url", "TEXT")
            self._ensure_column(connection, "clips", "start_time", "TEXT")
            self._ensure_column(connection, "clips", "end_time", "TEXT")
            self._ensure_column(connection, "clips", "duration_seconds", "INTEGER")
            self._ensure_column(connection, "clips", "virality_score", "INTEGER")
            self._ensure_column(connection, "clips", "confidence_score", "INTEGER")
            self._ensure_column(connection, "clips", "caption_variants_json", "TEXT NOT NULL DEFAULT '{}'")
            self._ensure_column(connection, "clips", "clip_format", "TEXT")
            self._ensure_column(connection, "clips", "transcript_excerpt", "TEXT")
            self._ensure_column(connection, "clips", "download_url", "TEXT")
            self._ensure_column(connection, "clips", "why_this_matters", "TEXT")
            self._ensure_column(connection, "clips", "post_rank", "INTEGER")
            self._ensure_column(connection, "campaigns", "description", "TEXT")
            self._ensure_column(connection, "campaigns", "allowed_platforms_json", "TEXT NOT NULL DEFAULT '[]'")
            self._ensure_column(connection, "campaigns", "target_angle", "TEXT")
            self._ensure_column(connection, "campaigns", "requirements", "TEXT")
            self._ensure_column(connection, "campaigns", "payout_cents_per_1000_views", "INTEGER")
            self._ensure_column(connection, "publish_requests", "caption", "TEXT")
            self._ensure_column(connection, "publish_requests", "scheduled_for", "TEXT")
            self._ensure_column(connection, "campaign_assignments", "request_id", "TEXT")
            self._ensure_column(connection, "campaign_assignments", "clip_id", "TEXT")
            self._ensure_column(connection, "campaign_assignments", "assignment_kind", "TEXT NOT NULL DEFAULT 'clip'")
            self._ensure_column(connection, "campaign_assignments", "title", "TEXT")
            self._ensure_column(connection, "campaign_assignments", "hook", "TEXT")
            self._ensure_column(connection, "campaign_assignments", "target_platform", "TEXT")
            self._ensure_column(connection, "campaign_assignments", "packaging_angle", "TEXT")
            self._ensure_column(connection, "campaign_assignments", "assignee_role", "TEXT NOT NULL DEFAULT 'creator'")
            self._ensure_column(connection, "campaign_assignments", "assignee_label", "TEXT")
            self._ensure_column(connection, "campaign_assignments", "status", "TEXT NOT NULL DEFAULT 'draft'")
            self._ensure_column(connection, "campaign_assignments", "payout_state", "TEXT NOT NULL DEFAULT 'locked'")
            self._ensure_column(connection, "campaign_assignments", "payout_amount_cents", "INTEGER")
            self._ensure_column(connection, "campaign_assignments", "note", "TEXT")
            self._ensure_column(connection, "campaign_assignments", "created_at", "TEXT")
            self._ensure_column(connection, "campaign_assignments", "updated_at", "TEXT")

    def _ensure_column(self, connection: sqlite3.Connection, table: str, column: str, column_type: str) -> None:
        rows = connection.execute(f"PRAGMA table_info({table})").fetchall()
        existing = {row["name"] for row in rows}
        if column in existing:
            return
        connection.execute(f"ALTER TABLE {table} ADD COLUMN {column} {column_type}")

    def create_user(self, *, email: str, password_hash: str, plan: str = "free", role: str = "creator") -> UserRecord:
        user_id = f"user_{uuid4().hex[:12]}"
        created_at = utcnow()
        with self._lock, self._connect() as connection:
            try:
                connection.execute(
                    """
                    INSERT INTO users (id, email, password_hash, plan, role, balance_cents, created_at)
                    VALUES (?, ?, ?, ?, ?, 0, ?)
                    """,
                    (user_id, email.lower(), password_hash, plan, role, created_at),
                )
            except sqlite3.IntegrityError as error:
                raise ValueError("Email is already registered") from error
        return UserRecord(id=user_id, email=email.lower(), plan=plan, role=role, balance_cents=0, created_at=created_at)

    def get_user_by_email(self, email: str) -> Optional[StoredUser]:
        with self._lock, self._connect() as connection:
            row = connection.execute(
                "SELECT id, email, password_hash, plan, role, balance_cents, created_at FROM users WHERE email = ?",
                (email.lower(),),
            ).fetchone()
        return self._user_from_row(row)

    def get_user_by_id(self, user_id: str) -> Optional[UserRecord]:
        with self._lock, self._connect() as connection:
            row = connection.execute(
                "SELECT id, email, password_hash, plan, role, balance_cents, created_at FROM users WHERE id = ?",
                (user_id,),
            ).fetchone()
        stored = self._user_from_row(row)
        if not stored:
            return None
        return UserRecord(
            id=stored.id,
            email=stored.email,
            plan=stored.plan,
            role=stored.role,
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
            assignment_rows = connection.execute(
                """
                SELECT campaign_id, status, payout_state, payout_amount_cents, assignment_kind, assignee_role
                FROM campaign_assignments
                WHERE user_id = ?
                """,
                (user_id,),
            ).fetchall()
        assignments_by_campaign: dict[str, list[sqlite3.Row]] = {}
        for row in assignment_rows:
            assignments_by_campaign.setdefault(row["campaign_id"], []).append(row)
        return [self._campaign_payload_from_row(row, assignments_by_campaign.get(row["id"], [])) for row in rows]

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
                       thumbnail_text, hook_variants_json, caption_variants_json, virality_score, clip_url, raw_clip_url, edited_clip_url,
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
            assignments = connection.execute(
                """
                SELECT id, campaign_id, user_id, request_id, clip_id, assignment_kind, title, hook,
                       target_platform, packaging_angle, assignee_role, assignee_label, status,
                       payout_state, payout_amount_cents, note, created_at, updated_at
                FROM campaign_assignments
                WHERE campaign_id = ? AND user_id = ?
                ORDER BY updated_at DESC, created_at DESC
                """,
                (campaign_id, user_id),
            ).fetchall()
        assignment_payloads = [self._assignment_payload_from_row(row) for row in assignments]
        return {
            "campaign": self._campaign_payload_from_row(campaign, assignments),
            "clips": [self._clip_payload_from_row(row) for row in clips],
            "jobs": [dict(row) for row in jobs],
            "assignments": assignment_payloads,
            "submission_summary": self._submission_summary_from_rows(assignments),
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
            assignment_rows = connection.execute(
                """
                SELECT campaign_id, status, payout_state, payout_amount_cents, assignment_kind, assignee_role
                FROM campaign_assignments
                WHERE campaign_id = ? AND user_id = ?
                """,
                (campaign_id, user_id),
            ).fetchall()
        return self._campaign_payload_from_row(row, assignment_rows) if row else None

    def create_campaign_assignments(
        self,
        *,
        campaign_id: str,
        user_id: str,
        request_id: str | None,
        clip_ids: list[str],
        target_platform: str | None,
        packaging_angle: str | None,
        assignee_role: str = "creator",
        assignee_label: str | None = None,
        note: str | None = None,
        payout_amount_cents: int | None = None,
    ) -> list[dict[str, Any]]:
        created_at = utcnow()
        with self._lock, self._connect() as connection:
            campaign = connection.execute(
                """
                SELECT id, target_angle, payout_cents_per_1000_views
                FROM campaigns
                WHERE id = ? AND user_id = ?
                """,
                (campaign_id, user_id),
            ).fetchone()
            if not campaign:
                raise ValueError("Campaign not found")

            assignments: list[dict[str, Any]] = []
            effective_role = (assignee_role or "creator").strip().lower() or "creator"
            effective_angle = packaging_angle or campaign["target_angle"]
            effective_payout_amount = payout_amount_cents if payout_amount_cents is not None else campaign["payout_cents_per_1000_views"]

            if clip_ids:
                placeholders = ",".join("?" for _ in clip_ids)
                rows = connection.execute(
                    f"""
                    SELECT id, request_id, title, hook, packaging_angle, platform_fit
                    FROM clips
                    WHERE user_id = ? AND id IN ({placeholders})
                    ORDER BY created_at DESC
                    """,
                    (user_id, *clip_ids),
                ).fetchall()
                if not rows:
                    raise ValueError("No clips found for assignment")

                for row in rows:
                    assignment_id = f"casg_{uuid4().hex[:12]}"
                    resolved_request_id = request_id or row["request_id"]
                    resolved_angle = effective_angle or row["packaging_angle"]
                    resolved_platform = target_platform or row["platform_fit"]
                    connection.execute(
                        """
                        INSERT INTO campaign_assignments (
                            id, campaign_id, user_id, request_id, clip_id, assignment_kind, title, hook,
                            target_platform, packaging_angle, assignee_role, assignee_label, status,
                            payout_state, payout_amount_cents, note, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, 'clip', ?, ?, ?, ?, ?, ?, 'draft', 'locked', ?, ?, ?, ?)
                        """,
                        (
                            assignment_id,
                            campaign_id,
                            user_id,
                            resolved_request_id,
                            row["id"],
                            row["title"] or f"Clip {row['id']}",
                            row["hook"],
                            resolved_platform,
                            resolved_angle,
                            effective_role,
                            assignee_label,
                            effective_payout_amount,
                            note,
                            created_at,
                            created_at,
                        ),
                    )
                    assignments.append(
                        {
                            "id": assignment_id,
                            "campaign_id": campaign_id,
                            "request_id": resolved_request_id,
                            "clip_id": row["id"],
                            "assignment_kind": "clip",
                            "title": row["title"] or f"Clip {row['id']}",
                            "hook": row["hook"],
                            "target_platform": resolved_platform,
                            "packaging_angle": resolved_angle,
                            "assignee_role": effective_role,
                            "assignee_label": assignee_label,
                            "status": "draft",
                            "payout_state": "locked",
                            "payout_amount_cents": effective_payout_amount,
                            "note": note,
                            "created_at": created_at,
                            "updated_at": created_at,
                        }
                    )
            elif request_id:
                existing_row = connection.execute(
                    """
                    SELECT id, title, hook, platform_fit, packaging_angle
                    FROM clips
                    WHERE request_id = ? AND user_id = ?
                    ORDER BY rank_value ASC, score DESC, created_at DESC
                    LIMIT 1
                    """,
                    (request_id, user_id),
                ).fetchone()
                title = existing_row["title"] if existing_row else f"Clip pack {request_id}"
                hook = existing_row["hook"] if existing_row else None
                resolved_angle = effective_angle or (existing_row["packaging_angle"] if existing_row else None)
                resolved_platform = target_platform or (existing_row["platform_fit"] if existing_row else None)
                assignment_id = f"casg_{uuid4().hex[:12]}"
                connection.execute(
                    """
                    INSERT INTO campaign_assignments (
                        id, campaign_id, user_id, request_id, clip_id, assignment_kind, title, hook,
                        target_platform, packaging_angle, assignee_role, assignee_label, status,
                        payout_state, payout_amount_cents, note, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, NULL, 'clip_pack', ?, ?, ?, ?, ?, ?, 'draft', 'locked', ?, ?, ?, ?)
                    """,
                    (
                        assignment_id,
                        campaign_id,
                        user_id,
                        request_id,
                        title,
                        hook,
                        resolved_platform,
                        resolved_angle,
                        effective_role,
                        assignee_label,
                        effective_payout_amount,
                        note,
                        created_at,
                        created_at,
                    ),
                )
                assignments.append(
                    {
                        "id": assignment_id,
                        "campaign_id": campaign_id,
                        "request_id": request_id,
                        "clip_id": None,
                        "assignment_kind": "clip_pack",
                        "title": title,
                        "hook": hook,
                        "target_platform": resolved_platform,
                        "packaging_angle": resolved_angle,
                        "assignee_role": effective_role,
                        "assignee_label": assignee_label,
                        "status": "draft",
                        "payout_state": "locked",
                        "payout_amount_cents": effective_payout_amount,
                        "note": note,
                        "created_at": created_at,
                        "updated_at": created_at,
                    }
                )
            else:
                raise ValueError("Provide request_id or clip_ids")

        return assignments

    def list_campaign_assignments(self, *, campaign_id: str, user_id: str) -> list[dict[str, Any]]:
        with self._lock, self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id, campaign_id, user_id, request_id, clip_id, assignment_kind, title, hook,
                       target_platform, packaging_angle, assignee_role, assignee_label, status,
                       payout_state, payout_amount_cents, note, created_at, updated_at
                FROM campaign_assignments
                WHERE campaign_id = ? AND user_id = ?
                ORDER BY updated_at DESC, created_at DESC
                """,
                (campaign_id, user_id),
            ).fetchall()
        return [self._assignment_payload_from_row(row) for row in rows]

    def update_campaign_assignment(
        self,
        *,
        campaign_id: str,
        assignment_id: str,
        user_id: str,
        updates: dict[str, Any],
    ) -> Optional[dict[str, Any]]:
        allowed = {
            "status": "status",
            "assignee_role": "assignee_role",
            "assignee_label": "assignee_label",
            "note": "note",
            "payout_amount_cents": "payout_amount_cents",
        }
        assignments = []
        values: list[Any] = []
        status_value = updates.get("status")
        for key, column in allowed.items():
            if key not in updates:
                continue
            assignments.append(f"{column} = ?")
            values.append(updates[key])

        if status_value is not None:
            assignments.append("payout_state = ?")
            values.append(self._payout_state_for_status(str(status_value)))

        assignments.append("updated_at = ?")
        values.append(utcnow())
        values.extend([assignment_id, campaign_id, user_id])

        with self._lock, self._connect() as connection:
            result = connection.execute(
                f"""
                UPDATE campaign_assignments
                SET {', '.join(assignments)}
                WHERE id = ? AND campaign_id = ? AND user_id = ?
                """,
                tuple(values),
            )
            if not result.rowcount:
                return None
            row = connection.execute(
                """
                SELECT id, campaign_id, user_id, request_id, clip_id, assignment_kind, title, hook,
                       target_platform, packaging_angle, assignee_role, assignee_label, status,
                       payout_state, payout_amount_cents, note, created_at, updated_at
                FROM campaign_assignments
                WHERE id = ? AND campaign_id = ? AND user_id = ?
                """,
                (assignment_id, campaign_id, user_id),
            ).fetchone()

        return self._assignment_payload_from_row(row) if row else None

    def get_user_submission_summary(self, *, user_id: str) -> dict[str, Any]:
        with self._lock, self._connect() as connection:
            rows = connection.execute(
                """
                SELECT status, payout_state, payout_amount_cents, assignment_kind, assignee_role
                FROM campaign_assignments
                WHERE user_id = ?
                """,
                (user_id,),
            ).fetchall()
        return self._submission_summary_from_rows(rows)

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
                        id, request_id, clip_key, user_id, campaign_id, source_type, source_title, source_platform,
                        source_transcript, source_visual_summary, source_preview_asset_url, source_download_asset_url,
                        source_thumbnail_url, title, hook, caption, start_time, end_time, duration_seconds, score,
                        confidence, confidence_score, rank_value, reason, why_this_matters, clip_format, transcript_excerpt, packaging_angle, platform_fit, post_rank, best_post_order,
                        cta_suggestion, thumbnail_text, hook_variants_json, caption_variants_json, virality_score, clip_url, download_url, raw_clip_url,
                        edited_clip_url, preview_image_url, local_asset_path, trim_start_seconds,
                        trim_end_seconds, caption_style_override, approved, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        record_id,
                        request_id,
                        clip.id,
                        user_id,
                        campaign_id,
                        response.source_type,
                        response.source_title,
                        response.source_platform,
                        response.transcript,
                        response.visual_summary,
                        response.preview_asset_url,
                        response.download_asset_url,
                        response.thumbnail_url,
                        clip.title,
                        clip.hook,
                        clip.caption,
                        clip.start_time,
                        clip.end_time,
                        clip.duration,
                        clip.score,
                        clip.confidence,
                        clip.confidence_score if clip.confidence_score is not None else round((clip.confidence or 0) * 100) or None,
                        clip.rank,
                        clip.reason,
                        clip.why_this_matters,
                        clip.format,
                        clip.transcript or clip.transcript_excerpt,
                        clip.packaging_angle,
                        clip.platform_fit,
                        clip.post_rank if clip.post_rank is not None else clip.best_post_order,
                        clip.best_post_order or clip.post_rank,
                        clip.cta_suggestion,
                        clip.thumbnail_text,
                        json.dumps(clip.hook_variants),
                        json.dumps(clip.caption_variants),
                        clip.virality_score if clip.virality_score is not None else clip.score,
                        clip.clip_url,
                        clip.download_url,
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
            connection.execute(
                """
                UPDATE campaign_assignments
                SET status = 'approved', payout_state = 'eligible', updated_at = ?
                WHERE campaign_id = ? AND user_id = ?
                """,
                (utcnow(), campaign_id, user_id),
            )
        return int(result.rowcount or 0)

    def get_clip(self, *, clip_id: str, user_id: str | None = None) -> Optional[dict[str, Any]]:
        query = """
            SELECT id, request_id, clip_key, user_id, campaign_id, title, hook, caption, start_time, end_time, score, confidence,
                   confidence_score, rank_value, reason, why_this_matters, packaging_angle, platform_fit, post_rank, best_post_order, cta_suggestion,
                   thumbnail_text, hook_variants_json, caption_variants_json, virality_score, clip_url, raw_clip_url, edited_clip_url, preview_image_url,
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
                       confidence_score, rank_value, reason, why_this_matters, packaging_angle, platform_fit, post_rank, best_post_order, cta_suggestion,
                       thumbnail_text, hook_variants_json, caption_variants_json, virality_score, clip_url, download_url, raw_clip_url, edited_clip_url, preview_image_url,
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
                       confidence_score, rank_value, reason, why_this_matters, packaging_angle, platform_fit, post_rank, best_post_order, cta_suggestion,
                       thumbnail_text, hook_variants_json, caption_variants_json, virality_score, clip_url, raw_clip_url, edited_clip_url, preview_image_url,
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
                       confidence_score, rank_value, reason, why_this_matters, packaging_angle, platform_fit, post_rank, best_post_order, cta_suggestion,
                       thumbnail_text, hook_variants_json, caption_variants_json, virality_score, clip_url, raw_clip_url, edited_clip_url, preview_image_url,
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
                SELECT request_id,
                       COUNT(*) AS clip_count,
                       MAX(score) AS top_score,
                       MAX(created_at) AS created_at,
                       MAX(source_title) AS source_title,
                       MAX(source_platform) AS target_platform
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
                SELECT id, request_id, clip_key, user_id, campaign_id, source_type, source_title, source_platform,
                       source_transcript, source_visual_summary, source_preview_asset_url, source_download_asset_url,
                       source_thumbnail_url, title, hook, caption, start_time, end_time, duration_seconds, score, confidence, confidence_score,
                       rank_value, reason, why_this_matters, clip_format, transcript_excerpt, packaging_angle, platform_fit, post_rank, best_post_order, cta_suggestion,
                       thumbnail_text, hook_variants_json, caption_variants_json, virality_score, clip_url, raw_clip_url, edited_clip_url, preview_image_url,
                       local_asset_path, trim_start_seconds, trim_end_seconds, caption_style_override,
                       approved, created_at
                FROM clips
                WHERE user_id = ? AND request_id = ?
                ORDER BY COALESCE(post_rank, best_post_order, rank_value) ASC, score DESC
                """,
                (user_id, request_id),
            ).fetchall()
        first_clip = clips[0] if clips else None
        return {
            "request_id": request_id,
            "source_title": first_clip["source_title"] if first_clip and "source_title" in first_clip.keys() else None,
            "source_type": first_clip["source_type"] if first_clip and "source_type" in first_clip.keys() else None,
            "source_platform": first_clip["source_platform"] if first_clip and "source_platform" in first_clip.keys() else None,
            "transcript": first_clip["source_transcript"] if first_clip and "source_transcript" in first_clip.keys() else None,
            "visual_summary": first_clip["source_visual_summary"] if first_clip and "source_visual_summary" in first_clip.keys() else None,
            "preview_asset_url": first_clip["source_preview_asset_url"] if first_clip and "source_preview_asset_url" in first_clip.keys() else None,
            "download_asset_url": first_clip["source_download_asset_url"] if first_clip and "source_download_asset_url" in first_clip.keys() else None,
            "thumbnail_url": first_clip["source_thumbnail_url"] if first_clip and "source_thumbnail_url" in first_clip.keys() else None,
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
            role=row["role"] or "creator",
            balance_cents=int(row["balance_cents"]),
            created_at=row["created_at"],
        )

    def _clip_payload_from_row(self, row: sqlite3.Row) -> dict[str, Any]:
        preview_url = self._row_value(row, "edited_clip_url") or self._row_value(row, "clip_url") or self._row_value(row, "raw_clip_url")
        download_url = self._row_value(row, "download_url")
        return {
            "record_id": row["id"],
            "request_id": row["request_id"],
            "clip_id": row["clip_key"],
            "id": row["clip_key"],
            "title": row["title"],
            "hook": row["hook"],
            "caption": row["caption"],
            "start_time": row["start_time"],
            "end_time": row["end_time"],
            "timestamp_start": row["start_time"],
            "timestamp_end": row["end_time"],
            "duration": self._row_value(row, "duration_seconds"),
            "score": row["score"],
            "virality_score": row["virality_score"],
            "confidence": row["confidence"],
            "confidence_score": self._row_value(row, "confidence_score")
            if self._row_value(row, "confidence_score") is not None
            else (int(round((row["confidence"] or 0) * 100)) if row["confidence"] is not None else None),
            "rank": row["rank_value"],
            "reason": row["reason"],
            "why_this_matters": self._row_value(row, "why_this_matters") or row["reason"],
            "format": self._row_value(row, "clip_format") or "Short Form",
            "transcript_excerpt": self._row_value(row, "transcript_excerpt"),
            "transcript": self._row_value(row, "transcript_excerpt"),
            "packaging_angle": row["packaging_angle"],
            "platform_fit": row["platform_fit"],
            "post_rank": self._row_value(row, "post_rank") or self._row_value(row, "best_post_order"),
            "best_post_order": row["best_post_order"],
            "cta_suggestion": row["cta_suggestion"],
            "cta": row["cta_suggestion"],
            "thumbnail_text": row["thumbnail_text"],
            "hook_variants": json.loads(row["hook_variants_json"] or "[]"),
            "caption_variants": json.loads(row["caption_variants_json"] or "{}"),
            "caption_style": self._row_value(row, "caption_style_override"),
            "clip_url": row["clip_url"],
            "raw_clip_url": row["raw_clip_url"],
            "edited_clip_url": row["edited_clip_url"],
            "preview_image_url": row["preview_image_url"],
            "preview_url": preview_url,
            "download_url": download_url,
            "thumbnail_url": row["preview_image_url"],
            "trim_start_seconds": row["trim_start_seconds"],
            "trim_end_seconds": row["trim_end_seconds"],
            "caption_style_override": row["caption_style_override"],
            "approved": bool(row["approved"]),
            "created_at": row["created_at"],
        }

    def _row_value(self, row: sqlite3.Row, key: str) -> Any:
        return row[key] if key in row.keys() else None

    def _assignment_payload_from_row(self, row: sqlite3.Row) -> dict[str, Any]:
        return {
            "id": row["id"],
            "campaign_id": row["campaign_id"],
            "owner_user_id": row["user_id"],
            "request_id": row["request_id"],
            "clip_id": row["clip_id"],
            "assignment_kind": row["assignment_kind"],
            "title": row["title"],
            "hook": row["hook"],
            "target_platform": row["target_platform"],
            "packaging_angle": row["packaging_angle"],
            "assignee_role": row["assignee_role"],
            "assignee_label": row["assignee_label"],
            "status": row["status"],
            "payout_state": row["payout_state"],
            "payout_amount_cents": row["payout_amount_cents"],
            "note": row["note"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }

    def _submission_summary_from_rows(self, rows: list[sqlite3.Row]) -> dict[str, Any]:
        status_counts = {status: 0 for status in ["draft", "ready", "submitted", "approved", "rejected", "paid"]}
        role_counts = {role: 0 for role in ["creator", "clipper", "admin"]}
        assignment_counts = {"clip": 0, "clip_pack": 0}
        eligible_cents = 0
        pending_cents = 0
        paid_cents = 0

        for row in rows:
            status_counts[row["status"]] = status_counts.get(row["status"], 0) + 1
            role_counts[row["assignee_role"]] = role_counts.get(row["assignee_role"], 0) + 1
            assignment_counts[row["assignment_kind"]] = assignment_counts.get(row["assignment_kind"], 0) + 1
            amount = int(row["payout_amount_cents"] or 0)
            if row["payout_state"] == "eligible":
                eligible_cents += amount
            elif row["payout_state"] == "pending":
                pending_cents += amount
            elif row["payout_state"] == "paid":
                paid_cents += amount

        return {
            "total_assignments": len(rows),
            "status_counts": status_counts,
            "role_counts": role_counts,
            "assignment_counts": assignment_counts,
            "eligible_payout_cents": eligible_cents,
            "pending_payout_cents": pending_cents,
            "paid_payout_cents": paid_cents,
        }

    def _campaign_payload_from_row(self, row: sqlite3.Row, assignments: list[sqlite3.Row] | None = None) -> dict[str, Any]:
        submission_summary = self._submission_summary_from_rows(assignments or [])
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
            "submission_summary": submission_summary,
        }

    def _payout_state_for_status(self, status: str) -> str:
        normalized = (status or "draft").strip().lower()
        if normalized == "approved":
            return "eligible"
        if normalized == "paid":
            return "paid"
        if normalized == "submitted":
            return "pending"
        return "locked"
