from pathlib import Path
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .api.routes.ai_costs import router as ai_costs_router
from .api.routes.auth import router as auth_router
from .api.routes.opportunity_engine import router as opportunity_engine_router
from .api.routes.proof_graph import router as proof_graph_router
from .api.routes.render_engine import router as render_engine_router
from .api.routes.source_assets import router as source_assets_router
from .api.routes.video_jobs import router as video_jobs_router
from .api.routes.creative_engines import router as creative_engines_router
from .api.routes.character_system import router as character_system_router
from .api.routes.game_world import router as game_world_router
from .api.routes.marketplace import router as marketplace_router
from .api.routes.campaign_export import router as campaign_export_router
from .api.routes.feedback_learning import router as feedback_learning_router
from .api.routes.safety import router as safety_router
from .api.routes.captions import router as captions_router
from .api.routes.audio import router as audio_router
from .api.routes.batches import router as batches_router
from .api.routes.capabilities import router as capabilities_router
from .api.routes.campaigns import router as campaigns_router
from .api.routes.clip_status import router as clip_status_router
from .api.routes.clips import router as clips_router
from .api.routes.edit import router as edit_router
from .api.routes.generate import router as generate_router
from .api.routes.generation import router as generation_router
from .api.routes.intelligence_data import router as intelligence_data_router
from .api.routes.me import router as me_router
from .api.routes.posting import router as posting_router
from .api.routes.seedance import router as seedance_router
from .api.routes.twitch_intelligence import router as twitch_intelligence_router
from .api.routes.upload import router as upload_router
from .api.routes.video_analysis import router as video_analysis_router
from .api.routes.visual_generation import router as visual_generation_router
from .api.routes.wallet import router as wallet_router
from .api.routes.whop_webhooks import router as whop_webhooks_router
from .core.config import get_settings
from .services.asset_retention import cleanup_generated_assets_nonfatal_for_settings
from .services.db_init import initialize_databases
from .worlds.clipping.router import router as worlds_clipping_router
from .worlds.jobs.router import router as worlds_jobs_router
from .worlds.router import router as worlds_router

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
    app.include_router(ai_costs_router)
    app.include_router(opportunity_engine_router)
    app.include_router(proof_graph_router)
    app.include_router(render_engine_router)
    app.include_router(source_assets_router)
    app.include_router(video_jobs_router)
    app.include_router(creative_engines_router)
    app.include_router(character_system_router)
    app.include_router(game_world_router)
    app.include_router(marketplace_router)
    app.include_router(campaign_export_router)
    app.include_router(feedback_learning_router)
    app.include_router(safety_router)
    app.include_router(captions_router)
    app.include_router(audio_router)
    app.include_router(generate_router)
    app.include_router(generation_router)
    app.include_router(capabilities_router)
    app.include_router(intelligence_data_router)
    app.include_router(twitch_intelligence_router)
    app.include_router(video_analysis_router)
    app.include_router(visual_generation_router)
    app.include_router(seedance_router)
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
    app.include_router(whop_webhooks_router)
    app.include_router(worlds_router)
    app.include_router(worlds_jobs_router)
    app.include_router(worlds_clipping_router)
    logger.info(
        "app_ready generated_assets_dir=%s generated_mount=/generated uploads_dir=%s uploads_mount=/uploads log_level=%s",
        settings.generated_assets_dir,
        settings.uploads_dir,
        settings.log_level,
    )
    return app


app = create_app()
