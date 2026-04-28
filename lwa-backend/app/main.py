from pathlib import Path
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .api.routes.auth import router as auth_router
from .api.routes.batches import router as batches_router
from .api.routes.campaigns import router as campaigns_router
from .api.routes.clip_status import router as clip_status_router
from .api.routes.clips import router as clips_router
from .api.routes.edit import router as edit_router
from .api.routes.generate import router as generate_router
from .api.routes.generation import router as generation_router
from .api.routes.intelligence_data import router as intelligence_data_router
from .api.routes.me import router as me_router
from .api.routes.posting import router as posting_router
from .api.routes.upload import router as upload_router
from .api.routes.video_analysis import router as video_analysis_router
from .api.routes.visual_generation import router as visual_generation_router
from .api.routes.wallet import router as wallet_router
from .core.config import get_settings
from .services.asset_retention import cleanup_generated_assets_nonfatal_for_settings
from .services.db_init import initialize_databases

settings = get_settings()
logger = logging.getLogger("uvicorn.error")

def create_app() -> FastAPI:
    Path(settings.generated_assets_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.uploads_dir).mkdir(parents=True, exist_ok=True)
    if settings.asset_cleanup_on_startup:
        cleanup_stats = cleanup_generated_assets_nonfatal_for_settings(settings)
        logger.info(
            "generated_asset_startup_cleanup scanned_count=%s deleted_count=%s retained_count=%s bytes_deleted=%s store_removed=%s",
            cleanup_stats.get("scanned_count", 0),
            cleanup_stats.get("deleted_count", 0),
            cleanup_stats.get("retained_count", 0),
            cleanup_stats.get("bytes_deleted", 0),
            cleanup_stats.get("store_removed", 0),
        )
    initialize_databases(settings)
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="Layered backend for the automated content economy engine.",
    )
    app.mount("/generated", StaticFiles(directory=settings.generated_assets_dir), name="generated")
    app.mount("/uploads", StaticFiles(directory=settings.uploads_dir), name="uploads")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(generate_router)
    app.include_router(generation_router)
    app.include_router(intelligence_data_router)
    app.include_router(video_analysis_router)
    app.include_router(visual_generation_router)
    app.include_router(auth_router)
    app.include_router(upload_router)
    app.include_router(me_router)
    app.include_router(batches_router)
    app.include_router(campaigns_router)
    app.include_router(wallet_router)
    app.include_router(posting_router)
    app.include_router(clip_status_router)
    app.include_router(clips_router)
    app.include_router(edit_router)
    logger.info(
        "app_ready generated_assets_dir=%s generated_mount=/generated uploads_dir=%s uploads_mount=/uploads log_level=%s",
        settings.generated_assets_dir,
        settings.uploads_dir,
        settings.log_level,
    )
    return app


app = create_app()
