from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any, Iterator


@dataclass(frozen=True)
class GeneratedAssetRecord:
    id: str
    provider: str
    asset_type: str
    status: str
    prompt: str | None = None
    preview_url: str | None = None
    video_url: str | None = None
    thumbnail_url: str | None = None
    source_refs: dict[str, str] | None = None
    local_path: str | None = None
    provider_job_id: str | None = None
    request_id: str | None = None
    error: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


class GeneratedAssetStore:
    def __init__(self, db_path: str) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()
        self._init_db()

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _init_db(self) -> None:
        with self._lock, self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS generated_assets (
                    id TEXT PRIMARY KEY,
                    provider TEXT NOT NULL,
                    asset_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    prompt TEXT,
                    preview_url TEXT,
                    video_url TEXT,
                    thumbnail_url TEXT,
                    source_refs_json TEXT NOT NULL DEFAULT '{}',
                    local_path TEXT,
                    provider_job_id TEXT,
                    request_id TEXT,
                    error TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_generated_assets_request_id ON generated_assets(request_id)"
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_generated_assets_provider_job_id ON generated_assets(provider_job_id)"
            )

    def create_asset(
        self,
        *,
        asset_id: str,
        provider: str,
        asset_type: str,
        status: str,
        prompt: str | None = None,
        preview_url: str | None = None,
        video_url: str | None = None,
        thumbnail_url: str | None = None,
        source_refs: dict[str, str] | None = None,
        local_path: str | None = None,
        provider_job_id: str | None = None,
        request_id: str | None = None,
        error: str | None = None,
    ) -> dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        payload = {
            "id": asset_id,
            "provider": provider,
            "asset_type": asset_type,
            "status": status,
            "prompt": prompt,
            "preview_url": preview_url,
            "video_url": video_url,
            "thumbnail_url": thumbnail_url,
            "source_refs_json": json.dumps(source_refs or {}),
            "local_path": local_path,
            "provider_job_id": provider_job_id,
            "request_id": request_id,
            "error": error,
            "created_at": now,
            "updated_at": now,
        }

        with self._lock, self._connect() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO generated_assets (
                    id, provider, asset_type, status, prompt, preview_url, video_url,
                    thumbnail_url, source_refs_json, local_path, provider_job_id,
                    request_id, error, created_at, updated_at
                ) VALUES (
                    :id, :provider, :asset_type, :status, :prompt, :preview_url, :video_url,
                    :thumbnail_url, :source_refs_json, :local_path, :provider_job_id,
                    :request_id, :error,
                    COALESCE((SELECT created_at FROM generated_assets WHERE id = :id), :created_at),
                    :updated_at
                )
                """,
                payload,
            )

        return self.get_asset(asset_id) or self._payload_to_public(payload)

    def update_asset(self, asset_id: str, **updates: Any) -> dict[str, Any] | None:
        if not updates:
            return self.get_asset(asset_id)

        column_map = {
            "provider": "provider",
            "asset_type": "asset_type",
            "status": "status",
            "prompt": "prompt",
            "preview_url": "preview_url",
            "video_url": "video_url",
            "thumbnail_url": "thumbnail_url",
            "source_refs": "source_refs_json",
            "local_path": "local_path",
            "provider_job_id": "provider_job_id",
            "request_id": "request_id",
            "error": "error",
        }
        assignments: list[str] = []
        values: dict[str, Any] = {"id": asset_id, "updated_at": datetime.now(timezone.utc).isoformat()}

        for key, value in updates.items():
            if key not in column_map:
                continue
            column = column_map[key]
            if key == "source_refs":
                value = json.dumps(value or {})
            values[column] = value
            assignments.append(f"{column} = :{column}")

        if not assignments:
            return self.get_asset(asset_id)

        assignments.append("updated_at = :updated_at")
        with self._lock, self._connect() as connection:
            connection.execute(
                f"""
                UPDATE generated_assets
                SET {", ".join(assignments)}
                WHERE id = :id
                """,
                values,
            )

        return self.get_asset(asset_id)

    def get_asset(self, asset_id: str) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM generated_assets WHERE id = ?",
                (asset_id,),
            ).fetchone()
        return self._row_to_dict(row) if row else None

    def get_by_provider_job_id(self, provider_job_id: str) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM generated_assets WHERE provider_job_id = ? ORDER BY created_at DESC LIMIT 1",
                (provider_job_id,),
            ).fetchone()
        return self._row_to_dict(row) if row else None

    def list_assets_for_request(self, request_id: str) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM generated_assets WHERE request_id = ? ORDER BY created_at DESC",
                (request_id,),
            ).fetchall()
        return [self._row_to_dict(row) for row in rows]

    def _row_to_dict(self, row: sqlite3.Row) -> dict[str, Any]:
        payload = dict(row)
        return self._payload_to_public(payload)

    def _payload_to_public(self, payload: dict[str, Any]) -> dict[str, Any]:
        public = dict(payload)
        public["source_refs"] = json.loads(public.pop("source_refs_json", "{}") or "{}")
        return public
