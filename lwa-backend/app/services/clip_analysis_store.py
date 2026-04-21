from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any, Iterable

from ..core.config import Settings

_lock = Lock()


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_connection(settings: Settings) -> sqlite3.Connection:
    path = Path(settings.clipping_db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    return connection


SCHEMA = """
CREATE TABLE IF NOT EXISTS videos (
  id TEXT PRIMARY KEY,
  source_url TEXT NOT NULL,
  local_path TEXT,
  title TEXT,
  duration_seconds REAL,
  target_platform TEXT,
  mode TEXT,
  status TEXT NOT NULL,
  error TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS transcript_segments (
  id TEXT PRIMARY KEY,
  video_id TEXT NOT NULL,
  start_time REAL NOT NULL,
  end_time REAL NOT NULL,
  text TEXT NOT NULL,
  speaker TEXT,
  confidence REAL,
  FOREIGN KEY(video_id) REFERENCES videos(id)
);

CREATE TABLE IF NOT EXISTS audio_regions (
  id TEXT PRIMARY KEY,
  video_id TEXT NOT NULL,
  start_time REAL NOT NULL,
  end_time REAL NOT NULL,
  region_type TEXT NOT NULL,
  loudness REAL,
  FOREIGN KEY(video_id) REFERENCES videos(id)
);

CREATE TABLE IF NOT EXISTS candidate_clips (
  id TEXT PRIMARY KEY,
  video_id TEXT NOT NULL,
  start_time REAL NOT NULL,
  end_time REAL NOT NULL,
  duration REAL NOT NULL,
  score REAL,
  confidence_score REAL,
  reason TEXT,
  category TEXT,
  transcript_excerpt TEXT,
  status TEXT NOT NULL,
  render_status TEXT,
  preview_url TEXT,
  clip_url TEXT,
  thumbnail_url TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY(video_id) REFERENCES videos(id)
);

CREATE TABLE IF NOT EXISTS render_jobs (
  id TEXT PRIMARY KEY,
  clip_id TEXT NOT NULL,
  status TEXT NOT NULL,
  error TEXT,
  output_path TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY(clip_id) REFERENCES candidate_clips(id)
);

CREATE TABLE IF NOT EXISTS export_bundles (
  id TEXT PRIMARY KEY,
  video_id TEXT NOT NULL,
  bundle_path TEXT NOT NULL,
  clip_count INTEGER NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY(video_id) REFERENCES videos(id)
);
"""


def init_clip_analysis_db(settings: Settings) -> None:
    with _lock, get_connection(settings) as connection:
        connection.executescript(SCHEMA)
        connection.commit()


def create_video_record(
    *,
    settings: Settings,
    video_id: str,
    source_url: str,
    target_platform: str | None,
    mode: str | None,
) -> dict[str, Any]:
    init_clip_analysis_db(settings)
    now = utcnow()
    with _lock, get_connection(settings) as connection:
        connection.execute(
            """
            INSERT INTO videos (id, source_url, target_platform, mode, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (video_id, source_url, target_platform, mode, "processing", now, now),
        )
        connection.commit()
    return get_video(settings=settings, video_id=video_id) or {"id": video_id, "status": "processing"}


def update_video_record(
    *,
    settings: Settings,
    video_id: str,
    status: str,
    local_path: str | None = None,
    title: str | None = None,
    duration_seconds: float | None = None,
    error: str | None = None,
) -> None:
    init_clip_analysis_db(settings)
    with _lock, get_connection(settings) as connection:
        connection.execute(
            """
            UPDATE videos
            SET status = ?, local_path = COALESCE(?, local_path), title = COALESCE(?, title),
                duration_seconds = COALESCE(?, duration_seconds), error = ?, updated_at = ?
            WHERE id = ?
            """,
            (status, local_path, title, duration_seconds, error, utcnow(), video_id),
        )
        connection.commit()


def replace_transcript_segments(*, settings: Settings, video_id: str, segments: Iterable[dict[str, Any]]) -> None:
    init_clip_analysis_db(settings)
    with _lock, get_connection(settings) as connection:
        connection.execute("DELETE FROM transcript_segments WHERE video_id = ?", (video_id,))
        for index, segment in enumerate(segments, start=1):
            connection.execute(
                """
                INSERT INTO transcript_segments (id, video_id, start_time, end_time, text, speaker, confidence)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    f"{video_id}_ts_{index:04d}",
                    video_id,
                    float(segment["start_time"]),
                    float(segment["end_time"]),
                    str(segment.get("text") or ""),
                    segment.get("speaker"),
                    segment.get("confidence"),
                ),
            )
        connection.commit()


def replace_audio_regions(*, settings: Settings, video_id: str, regions: Iterable[dict[str, Any]]) -> None:
    init_clip_analysis_db(settings)
    with _lock, get_connection(settings) as connection:
        connection.execute("DELETE FROM audio_regions WHERE video_id = ?", (video_id,))
        for index, region in enumerate(regions, start=1):
            connection.execute(
                """
                INSERT INTO audio_regions (id, video_id, start_time, end_time, region_type, loudness)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    f"{video_id}_ar_{index:04d}",
                    video_id,
                    float(region["start_time"]),
                    float(region["end_time"]),
                    str(region.get("region_type") or region.get("type") or "speech"),
                    region.get("loudness"),
                ),
            )
        connection.commit()


def replace_candidate_clips(*, settings: Settings, video_id: str, clips: Iterable[dict[str, Any]]) -> None:
    init_clip_analysis_db(settings)
    now = utcnow()
    with _lock, get_connection(settings) as connection:
        connection.execute("DELETE FROM candidate_clips WHERE video_id = ?", (video_id,))
        for clip in clips:
            clip_id = f"{video_id}_{clip['id']}"
            connection.execute(
                """
                INSERT INTO candidate_clips (
                    id, video_id, start_time, end_time, duration, score, confidence_score, reason,
                    category, transcript_excerpt, status, render_status, preview_url, clip_url,
                    thumbnail_url, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    clip_id,
                    video_id,
                    float(clip["start_time"]),
                    float(clip["end_time"]),
                    float(clip["duration"]),
                    clip.get("score"),
                    clip.get("confidence_score"),
                    clip.get("reason"),
                    clip.get("category"),
                    clip.get("transcript_excerpt"),
                    clip.get("status", "detected"),
                    clip.get("render_status", "pending"),
                    clip.get("preview_url"),
                    clip.get("clip_url"),
                    clip.get("thumbnail_url"),
                    now,
                    now,
                ),
            )
        connection.commit()


def get_video(*, settings: Settings, video_id: str) -> dict[str, Any] | None:
    init_clip_analysis_db(settings)
    with _lock, get_connection(settings) as connection:
        row = connection.execute("SELECT * FROM videos WHERE id = ?", (video_id,)).fetchone()
        if not row:
            return None
        payload = dict(row)
        counts = connection.execute(
            """
            SELECT
              COUNT(*) AS candidate_count,
              SUM(CASE WHEN render_status = 'ready' THEN 1 ELSE 0 END) AS ready_count,
              SUM(CASE WHEN render_status = 'failed' THEN 1 ELSE 0 END) AS failed_count
            FROM candidate_clips
            WHERE video_id = ?
            """,
            (video_id,),
        ).fetchone()
        payload.update(
            {
                "candidate_clip_count": int(counts["candidate_count"] or 0),
                "ready_clip_count": int(counts["ready_count"] or 0),
                "failed_clip_count": int(counts["failed_count"] or 0),
            }
        )
        return payload


def list_video_clips(*, settings: Settings, video_id: str) -> list[dict[str, Any]]:
    init_clip_analysis_db(settings)
    with _lock, get_connection(settings) as connection:
        rows = connection.execute(
            "SELECT * FROM candidate_clips WHERE video_id = ? ORDER BY score DESC, start_time ASC",
            (video_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def get_candidate_clip(*, settings: Settings, clip_id: str) -> dict[str, Any] | None:
    init_clip_analysis_db(settings)
    with _lock, get_connection(settings) as connection:
        row = connection.execute("SELECT * FROM candidate_clips WHERE id = ?", (clip_id,)).fetchone()
    return dict(row) if row else None


def update_candidate_clip_media(
    *,
    settings: Settings,
    clip_id: str,
    render_status: str,
    preview_url: str | None = None,
    clip_url: str | None = None,
    thumbnail_url: str | None = None,
) -> None:
    init_clip_analysis_db(settings)
    with _lock, get_connection(settings) as connection:
        connection.execute(
            """
            UPDATE candidate_clips
            SET render_status = ?, status = ?, preview_url = COALESCE(?, preview_url),
                clip_url = COALESCE(?, clip_url), thumbnail_url = COALESCE(?, thumbnail_url),
                updated_at = ?
            WHERE id = ?
            """,
            (render_status, "ready" if render_status == "ready" else render_status, preview_url, clip_url, thumbnail_url, utcnow(), clip_id),
        )
        connection.commit()


def insert_export_bundle(
    *,
    settings: Settings,
    bundle_id: str,
    video_id: str,
    bundle_path: str,
    clip_count: int,
) -> None:
    init_clip_analysis_db(settings)
    with _lock, get_connection(settings) as connection:
        connection.execute(
            """
            INSERT INTO export_bundles (id, video_id, bundle_path, clip_count, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (bundle_id, video_id, bundle_path, clip_count, utcnow()),
        )
        connection.commit()
