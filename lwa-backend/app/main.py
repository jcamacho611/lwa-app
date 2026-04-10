from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .api.routes.generate import router as generate_router
from .core.config import get_settings

settings = get_settings()

def create_app() -> FastAPI:
    Path(settings.generated_assets_dir).mkdir(parents=True, exist_ok=True)
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="Layered backend for the automated content economy engine.",
    )
    app.mount("/generated", StaticFiles(directory=settings.generated_assets_dir), name="generated")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(generate_router)
    return app


app = create_app()
