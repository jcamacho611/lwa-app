from __future__ import annotations

import logging
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import uuid4

from ..core.config import Settings
from ..services.clip_status_store import update_clip_status

logger = logging.getLogger("uvicorn.error")


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


class RenderJobStore:
    """Persistent storage for render jobs with SQLite backend."""
    
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._init_db()

    @contextmanager
    def _connect(self):
        from pathlib import Path

        db_path = Path(self.settings.clipping_db_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(db_path)
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _init_db(self) -> None:
        """Initialize the render jobs database."""
        with self._connect() as connection:
            connection.executescript("""
                CREATE TABLE IF NOT EXISTS render_jobs (
                    id TEXT PRIMARY KEY,
                    clip_id TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    error TEXT,
                    output_path TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY(clip_id) REFERENCES candidate_clips(id)
                );
                
                CREATE TABLE IF NOT EXISTS render_job_logs (
                    id TEXT PRIMARY KEY,
                    job_id TEXT NOT NULL,
                    level TEXT NOT NULL,
                    message TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(job_id) REFERENCES render_jobs(id)
                );
            """)
            connection.commit()
    
    def create_job(
        self,
        *,
        clip_id: str,
        status: str = "pending",
        error: Optional[str] = None,
        output_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new render job."""
        job_id = f"render_job_{uuid4().hex[:12]}"
        created_at = utcnow()

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO render_jobs (
                    id, clip_id, status, error, output_path, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (job_id, clip_id, status, error, output_path, created_at, created_at),
            )
            connection.commit()
        
        logger.info(f"render_job_created job_id={job_id} clip_id={clip_id}")
        
        return {
            "id": job_id,
            "clip_id": clip_id,
            "status": status,
            "error": error,
            "output_path": output_path,
            "created_at": created_at,
            "updated_at": created_at,
        }
    
    def update_job(
        self,
        job_id: str,
        *,
        status: Optional[str] = None,
        error: Optional[str] = None,
        output_path: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Update render job status and results."""
        with self._connect() as connection:
            updates = []
            values = []
            
            if status is not None:
                updates.append("status = ?")
                values.append(status)
            
            if error is not None:
                updates.append("error = ?")
                values.append(error)
            
            if output_path is not None:
                updates.append("output_path = ?")
                values.append(output_path)
            
            if updates:
                updates.append("updated_at = ?")
                values.append(utcnow())
                
                set_clause = ", ".join(updates)
                connection.execute(
                    f"UPDATE render_jobs SET {set_clause} WHERE id = ?",
                    (*values, job_id),
                )
                connection.commit()
        
        logger.info(f"render_job_updated job_id={job_id} updates={len(updates)}")
        
        # Return updated job
        return self.get_job(job_id)
    
    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get render job by ID."""
        with self._connect() as connection:
            connection.row_factory = sqlite3.Row
            row = connection.execute(
                "SELECT * FROM render_jobs WHERE id = ?",
                (job_id,),
            ).fetchone()
        
        if row:
            return dict(row)
        return None
    
    def get_jobs_by_clip(self, clip_id: str) -> list[Dict[str, Any]]:
        """Get all render jobs for a specific clip."""
        with self._connect() as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(
                "SELECT * FROM render_jobs WHERE clip_id = ? ORDER BY created_at DESC",
                (clip_id,),
            ).fetchall()
        
        return [dict(row) for row in rows]
    
    def get_pending_jobs(self, limit: int = 50) -> list[Dict[str, Any]]:
        """Get pending render jobs."""
        with self._connect() as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(
                "SELECT * FROM render_jobs WHERE status IN ('pending', 'rendering') ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        
        return [dict(row) for row in rows]
    
    def log_job_event(self, job_id: str, level: str, message: str) -> None:
        """Log an event for a render job."""
        with self._connect() as connection:
            log_id = f"job_log_{uuid4().hex[:12]}"
            created_at = utcnow()
            
            connection.execute(
                """
                INSERT INTO render_job_logs (id, job_id, level, message, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (log_id, job_id, level, message, created_at),
            )
            connection.commit()
        
        logger.info(f"render_job_log_created job_id={job_id} level={level} message={message}")
    
    def cleanup_old_jobs(self, days: int = 7) -> int:
        """Clean up old render jobs."""
        with self._connect() as connection:
            result = connection.execute(
                "DELETE FROM render_jobs WHERE created_at < datetime('now', '-{} days')",
                (days,),
            )
            connection.commit()
        
        deleted_count = result.rowcount if result else 0
        logger.info(f"render_jobs_cleanup deleted={deleted_count} jobs older_than={days}days")
        
        return deleted_count
