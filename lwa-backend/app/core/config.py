from __future__ import annotations

from functools import lru_cache
import os
from pathlib import Path


def _default_ffmpeg_path() -> str:
    candidates = [
        "/opt/homebrew/bin/ffmpeg",
        "/usr/local/bin/ffmpeg",
        "/usr/bin/ffmpeg",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return candidate
    return "/usr/bin/ffmpeg"


class Settings:
    def __init__(self) -> None:
        origins = os.getenv("LWA_ALLOWED_ORIGINS") or os.getenv("ALLOWED_ORIGINS", "*")
        self.allowed_origins = [origin.strip() for origin in origins.split(",") if origin.strip()]
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.app_name = os.getenv("LWA_APP_NAME", "LWA Backend")
        railway_public_domain = os.getenv("RAILWAY_PUBLIC_DOMAIN", "").strip()
        derived_public_base_url = f"https://{railway_public_domain}" if railway_public_domain else ""
        self.api_base_url = os.getenv("API_BASE_URL", "").strip() or derived_public_base_url
        self.port = int(os.getenv("PORT", "8000"))
        self.log_level = os.getenv("LOG_LEVEL", "info")
        self.api_key_header_name = os.getenv("LWA_API_KEY_HEADER_NAME", "x-api-key").strip() or "x-api-key"
        self.api_key_secret = os.getenv("LWA_API_KEY_SECRET", "").strip()
        self.client_id_header_name = os.getenv("LWA_CLIENT_ID_HEADER_NAME", "x-lwa-client-id").strip() or "x-lwa-client-id"
        self.default_plan_name = os.getenv("LWA_DEFAULT_PLAN_NAME", "Starter Trial")
        self.default_credits_remaining = int(os.getenv("LWA_DEFAULT_CREDITS_REMAINING", "2"))
        self.default_turnaround = os.getenv("LWA_DEFAULT_TURNAROUND", "45 seconds")
        self.free_daily_limit = int(os.getenv("LWA_FREE_DAILY_LIMIT", str(self.default_credits_remaining)))
        self.pro_daily_limit = int(os.getenv("LWA_PRO_DAILY_LIMIT", "25"))
        self.scale_daily_limit = int(os.getenv("LWA_SCALE_DAILY_LIMIT", "100"))
        self.pro_api_keys = {
            value.strip()
            for value in os.getenv("LWA_PRO_API_KEYS", "").split(",")
            if value.strip()
        }
        self.scale_api_keys = {
            value.strip()
            for value in os.getenv("LWA_SCALE_API_KEYS", "").split(",")
            if value.strip()
        }
        self.ffmpeg_path = os.getenv("FFMPEG_PATH", _default_ffmpeg_path())
        self.video_encoder = os.getenv("LWA_VIDEO_ENCODER", "auto").strip().lower() or "auto"
        self.yt_dlp_temp_dir = os.getenv("YT_DLP_TEMP_DIR", "/tmp")
        railway_volume_mount_path = os.getenv("RAILWAY_VOLUME_MOUNT_PATH", "").strip()
        default_generated_dir = (
            os.path.join(railway_volume_mount_path, "lwa-generated")
            if railway_volume_mount_path
            else os.path.join(os.getcwd(), "generated")
        )
        self.generated_assets_dir = os.getenv("LWA_GENERATED_ASSETS_DIR", default_generated_dir)
        default_usage_store = (
            os.path.join(railway_volume_mount_path, "lwa-usage.json")
            if railway_volume_mount_path
            else os.path.join(os.getcwd(), "generated", "lwa-usage.json")
        )
        self.usage_store_path = os.getenv("LWA_USAGE_STORE_PATH", default_usage_store)
        self.max_upload_mb = int(os.getenv("MAX_UPLOAD_MB", "500"))
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
        self.ai_provider = os.getenv("LWA_AI_PROVIDER", "auto")
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "llama3.2")
        self.whop_api_key = os.getenv("WHOP_API_KEY", "")
        self.whop_company_id = os.getenv("WHOP_COMPANY_ID", "")
        self.google_api_key = os.getenv("GOOGLE_API_KEY", "")
        self.youtube_api_key = os.getenv("YOUTUBE_API_KEY", "")
        self.tiktok_client_key = os.getenv("TIKTOK_CLIENT_KEY", "")
        self.tiktok_client_secret = os.getenv("TIKTOK_CLIENT_SECRET", "")
        self.meta_app_id = os.getenv("META_APP_ID", "")
        self.meta_app_secret = os.getenv("META_APP_SECRET", "")
        self.facebook_page_access_token = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN", "")
        self.instagram_access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
        self.service_version = (
            os.getenv("RENDER_GIT_COMMIT")
            or os.getenv("RAILWAY_GIT_COMMIT_SHA")
            or "local"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
