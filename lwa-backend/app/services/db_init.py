from __future__ import annotations

import logging
from pathlib import Path

from ..core.config import Settings

logger = logging.getLogger("uvicorn.error")


def initialize_databases(settings: Settings) -> None:
    """Initialize all required databases with proper schema."""
    try:
        # Initialize platform store database
        from ..dependencies.auth import get_platform_store
        platform_store = get_platform_store()
        platform_store._init_db()
        logger.info(f"platform_db_initialized path={settings.platform_db_path}")
        
        # Initialize clip analysis store database
        from ..services.clip_analysis_store import init_clip_analysis_db
        init_clip_analysis_db(settings)
        logger.info(f"clip_analysis_db_initialized path={settings.clipping_db_path}")
        
        # Initialize render job store database
        from ..services.render_job_store import RenderJobStore
        render_job_store = RenderJobStore(settings)
        render_job_store._init_db()
        logger.info(f"render_job_db_initialized path={settings.clipping_db_path}")

        # Initialize generated asset store database
        from ..services.generated_asset_store import GeneratedAssetStore
        GeneratedAssetStore(settings.generated_asset_store_path)
        logger.info(f"generated_asset_db_initialized path={settings.generated_asset_store_path}")

        # Initialize LWA Worlds marketplace/ledger database
        from ..worlds.repositories import WorldsStore
        WorldsStore(settings.worlds_db_path)
        logger.info(f"worlds_db_initialized path={settings.worlds_db_path}")
        
        # Ensure generated assets directory exists
        generated_dir = Path(settings.generated_assets_dir)
        generated_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"generated_assets_dir_created path={settings.generated_assets_dir}")
        
        # Ensure uploads directory exists
        uploads_dir = Path(settings.uploads_dir)
        uploads_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"uploads_dir_created path={settings.uploads_dir}")
        
        logger.info("all_databases_initialized_successfully")
        
    except Exception as error:
        logger.error(f"database_initialization_failed error={str(error)}")
        raise


def migrate_databases(settings: Settings) -> None:
    """Run database migrations if needed."""
    try:
        # Platform store migrations
        from ..dependencies.auth import get_platform_store
        platform_store = get_platform_store()
        platform_store._init_db()  # This handles schema migrations
        logger.info("platform_db_migrations_completed")
        
        # Clip analysis store migrations
        from ..services.clip_analysis_store import init_clip_analysis_db
        init_clip_analysis_db(settings)  # This handles schema migrations
        logger.info("clip_analysis_db_migrations_completed")
        
        # Render job store migrations
        from ..services.render_job_store import RenderJobStore
        render_job_store = RenderJobStore(settings)
        render_job_store._init_db()  # This handles schema migrations
        logger.info("render_job_db_migrations_completed")

        # Generated asset store migrations
        from ..services.generated_asset_store import GeneratedAssetStore
        GeneratedAssetStore(settings.generated_asset_store_path)
        logger.info("generated_asset_db_migrations_completed")

        # LWA Worlds store migrations
        from ..worlds.repositories import WorldsStore
        WorldsStore(settings.worlds_db_path)
        logger.info("worlds_db_migrations_completed")
        
        logger.info("all_database_migrations_completed")
        
    except Exception as error:
        logger.error(f"database_migration_failed error={str(error)}")
        raise


def cleanup_old_data(settings: Settings, days: int = 30) -> None:
    """Clean up old data from databases."""
    try:
        # Clean old render jobs
        from ..services.render_job_store import RenderJobStore
        render_job_store = RenderJobStore(settings)
        deleted_jobs = render_job_store.cleanup_old_jobs(days)
        logger.info(f"old_render_jobs_cleaned count={deleted_jobs}")
        
        # Clean old generated assets
        from ..services.clip_service import maybe_prune_generated_assets
        maybe_prune_generated_assets(settings)
        logger.info("generated_assets_cleanup_completed")
        
        logger.info(f"data_cleanup_completed days={days}")
        
    except Exception as error:
        logger.error(f"data_cleanup_failed error={str(error)}")
        raise


def get_database_status(settings: Settings) -> dict[str, object]:
    """Get status of all databases."""
    try:
        from pathlib import Path
        import sqlite3
        
        status = {}
        
        # Check platform database
        platform_db = Path(settings.platform_db_path)
        if platform_db.exists():
            with sqlite3.connect(platform_db) as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT COUNT(*) FROM users")
                user_count = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM clips")
                clip_count = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM campaigns")
                campaign_count = cursor.fetchone()[0]
                
                status["platform_db"] = {
                    "exists": True,
                    "path": str(platform_db),
                    "size_bytes": platform_db.stat().st_size,
                    "user_count": user_count,
                    "clip_count": clip_count,
                    "campaign_count": campaign_count,
                }
        else:
            status["platform_db"] = {"exists": False, "path": str(platform_db)}

        worlds_db = Path(settings.worlds_db_path)
        if worlds_db.exists():
            with sqlite3.connect(worlds_db) as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT COUNT(*) FROM marketplace_campaigns")
                worlds_campaign_count = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM internal_ledger_entries")
                worlds_ledger_count = cursor.fetchone()[0]
                status["worlds_db"] = {
                    "exists": True,
                    "path": str(worlds_db),
                    "size_bytes": worlds_db.stat().st_size,
                    "campaign_count": worlds_campaign_count,
                    "ledger_count": worlds_ledger_count,
                }
        else:
            status["worlds_db"] = {"exists": False, "path": str(worlds_db)}
        
        # Check clip analysis database
        analysis_db = Path(settings.clipping_db_path)
        if analysis_db.exists():
            with sqlite3.connect(analysis_db) as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT COUNT(*) FROM videos")
                video_count = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM candidate_clips")
                candidate_count = cursor.fetchone()[0]
                
                status["analysis_db"] = {
                    "exists": True,
                    "path": str(analysis_db),
                    "size_bytes": analysis_db.stat().st_size,
                    "video_count": video_count,
                    "candidate_count": candidate_count,
                }
        else:
            status["analysis_db"] = {"exists": False, "path": str(analysis_db)}
        
        # Check generated assets directory
        generated_dir = Path(settings.generated_assets_dir)
        status["generated_assets"] = {
            "exists": generated_dir.exists(),
            "path": str(generated_dir),
            "size_bytes": generated_dir.stat().st_size if generated_dir.exists() else 0,
        }
        
        # Check uploads directory
        uploads_dir = Path(settings.uploads_dir)
        status["uploads"] = {
            "exists": uploads_dir.exists(),
            "path": str(uploads_dir),
            "size_bytes": sum(f.stat().st_size for f in uploads_dir.iterdir() if f.is_file()) if uploads_dir.exists() else 0,
        }
        
        return status
        
    except Exception as error:
        logger.error(f"database_status_check_failed error={str(error)}")
        return {"error": str(error)}
