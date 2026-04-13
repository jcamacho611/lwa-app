from pathlib import Path
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .api.routes.auth import router as auth_router
from .api.routes.batches import router as batches_router
from .api.routes.campaigns import router as campaigns_router
from .api.routes.clips import router as clips_router
from .api.routes.edit import router as edit_router
from .api.routes.generate import router as generate_router
from .api.routes.me import router as me_router
from .api.routes.posting import router as posting_router
from .api.routes.upload import router as upload_router
from .api.routes.wallet import router as wallet_router
from .api.routes.web import router as web_router
from .core.config import get_settings

settings = get_settings()
logger = logging.getLogger("uvicorn.error")

def create_app() -> FastAPI:
    Path(settings.generated_assets_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.uploads_dir).mkdir(parents=True, exist_ok=True)
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
    app.include_router(auth_router)
    app.include_router(upload_router)
    app.include_router(me_router)
    app.include_router(batches_router)
    app.include_router(campaigns_router)
    app.include_router(wallet_router)
    app.include_router(posting_router)
    app.include_router(clips_router)
    app.include_router(edit_router)
    app.include_router(web_router)
    logger.info(
        "app_ready generated_assets_dir=%s generated_mount=/generated uploads_dir=%s uploads_mount=/uploads log_level=%s",
        settings.generated_assets_dir,
        settings.uploads_dir,
        settings.log_level,
    )
    return app


app = create_app()
