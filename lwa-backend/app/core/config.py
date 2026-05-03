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


def _env_bool(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int | str, *, minimum: int | None = None) -> int:
    default_value = int(default)
    raw_value = os.getenv(name, str(default)).strip()
    try:
        parsed = int(raw_value)
    except (TypeError, ValueError):
        parsed = default_value

    if minimum is not None and parsed < minimum:
        return default_value if default_value >= minimum else minimum
    return parsed


class Settings:
    def __init__(self) -> None:
        origins = os.getenv("LWA_ALLOWED_ORIGINS") or os.getenv("ALLOWED_ORIGINS", "*")
        self.allowed_origins = [origin.strip() for origin in origins.split(",") if origin.strip()]
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.app_name = os.getenv("LWA_APP_NAME", "LWA Backend")
        railway_public_domain = os.getenv("RAILWAY_PUBLIC_DOMAIN", "").strip()
        derived_public_base_url = f"https://{railway_public_domain}" if railway_public_domain else ""
        self.api_base_url = os.getenv("API_BASE_URL", "").strip() or derived_public_base_url
        self.port = _env_int("PORT", 8000, minimum=1)
        self.log_level = os.getenv("LOG_LEVEL", "info")
        self.free_launch_mode = _env_bool("FREE_LAUNCH_MODE", os.getenv("LWA_FREE_LAUNCH_MODE", "false"))
        self.rate_limit_guest_rpm = _env_int("RATE_LIMIT_GUEST_RPM", os.getenv("LWA_RATE_LIMIT_GUEST_RPM", "30"), minimum=1)
        self.api_key_header_name = os.getenv("LWA_API_KEY_HEADER_NAME", "x-api-key").strip() or "x-api-key"
        self.api_key_secret = os.getenv("LWA_API_KEY_SECRET", "").strip()
        self.client_id_header_name = os.getenv("LWA_CLIENT_ID_HEADER_NAME", "x-lwa-client-id").strip() or "x-lwa-client-id"
        self.default_plan_name = os.getenv("LWA_DEFAULT_PLAN_NAME", "Guest access")
        self.default_credits_remaining = _env_int("LWA_DEFAULT_CREDITS_REMAINING", 10, minimum=0)
        self.default_turnaround = os.getenv("LWA_DEFAULT_TURNAROUND", "45 seconds")
        self.free_launch_mode = _env_bool("FREE_LAUNCH_MODE", "false")
        self.rate_limit_guest_rpm = _env_int("RATE_LIMIT_GUEST_RPM", 30, minimum=1)
        self.free_daily_limit = _env_int("LWA_FREE_DAILY_LIMIT", self.default_credits_remaining, minimum=0)
        self.pro_daily_limit = _env_int("LWA_PRO_DAILY_LIMIT", 25, minimum=-1)
        self.scale_daily_limit = _env_int("LWA_SCALE_DAILY_LIMIT", 100, minimum=-1)
        self.free_clip_limit = _env_int("LWA_FREE_CLIP_LIMIT", 3, minimum=1)
        self.pro_clip_limit = _env_int("LWA_PRO_CLIP_LIMIT", 6, minimum=1)
        self.scale_clip_limit = _env_int("LWA_SCALE_CLIP_LIMIT", 12, minimum=1)
        self.max_clip_limit = _env_int("LWA_MAX_CLIP_LIMIT", 12, minimum=1)
        self.enable_high_volume_clips = _env_bool("LWA_ENABLE_HIGH_VOLUME_CLIPS", "false")
        self.high_volume_max_clips = _env_int("LWA_HIGH_VOLUME_MAX_CLIPS", 24, minimum=1)
        self.max_clips_per_job = _env_int("LWA_MAX_CLIPS_PER_JOB", self.max_clip_limit, minimum=1)
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
        self.video_encoder = os.getenv("LWA_VIDEO_ENCODER", "libx264").strip().lower() or "libx264"
        self.yt_dlp_temp_dir = os.getenv("YT_DLP_TEMP_DIR", "/tmp")
        self.yt_cookies_b64 = os.getenv("YT_COOKIES_B64", "")
        railway_volume_mount_path = os.getenv("RAILWAY_VOLUME_MOUNT_PATH", "").strip()
        default_generated_dir = (
            os.path.join(railway_volume_mount_path, "lwa-generated")
            if railway_volume_mount_path
            else os.path.join(os.getcwd(), "generated")
        )
        self.generated_assets_dir = os.getenv("LWA_GENERATED_ASSETS_DIR", default_generated_dir)
        self.generated_asset_store_path = os.getenv(
            "LWA_GENERATED_ASSET_STORE_PATH",
            os.path.join(railway_volume_mount_path, "lwa-generated-assets.sqlite3")
            if railway_volume_mount_path
            else os.path.join(os.getcwd(), "generated", "lwa-generated-assets.sqlite3"),
        )
        self.generated_asset_retention_hours = _env_int(
            "LWA_GENERATED_ASSETS_RETENTION_HOURS",
            os.getenv("LWA_GENERATED_ASSET_RETENTION_HOURS", "24"),
            minimum=1,
        )
        self.generated_assets_max_files = _env_int("LWA_GENERATED_ASSETS_MAX_FILES", 300, minimum=1)
        self.asset_cleanup_on_startup = _env_bool("LWA_ASSET_CLEANUP_ON_STARTUP", "true")
        self.generated_asset_prune_interval_seconds = _env_int(
            "LWA_GENERATED_ASSET_PRUNE_INTERVAL_SECONDS",
            1800,
            minimum=60,
        )
        default_uploads_dir = (
            os.path.join(railway_volume_mount_path, "lwa-uploads")
            if railway_volume_mount_path
            else os.path.join(os.getcwd(), "uploads")
        )
        self.uploads_dir = os.getenv("LWA_UPLOADS_DIR", default_uploads_dir)
        default_usage_store = (
            os.path.join(railway_volume_mount_path, "lwa-usage.json")
            if railway_volume_mount_path
            else os.path.join(os.getcwd(), "generated", "lwa-usage.json")
        )
        self.usage_store_path = os.getenv("LWA_USAGE_STORE_PATH", default_usage_store)
        default_event_log = (
            os.path.join(railway_volume_mount_path, "lwa-events.jsonl")
            if railway_volume_mount_path
            else os.path.join(os.getcwd(), "generated", "lwa-events.jsonl")
        )
        self.event_log_path = os.getenv("LWA_EVENT_LOG_PATH", default_event_log)
        self.event_log_enabled = _env_bool("LWA_EVENT_LOG_ENABLED", "true")
        self.event_log_max_bytes = _env_int("LWA_EVENT_LOG_MAX_BYTES", 10_485_760, minimum=1024)
        self.event_log_max_metadata_chars = _env_int("LWA_EVENT_LOG_MAX_METADATA_CHARS", 2000, minimum=256)
        self.abuse_window_seconds = _env_int("LWA_ABUSE_WINDOW_SECONDS", 300, minimum=1)
        self.abuse_max_generation_requests = _env_int("LWA_ABUSE_MAX_GENERATION_REQUESTS", 8, minimum=1)
        default_platform_db = (
            os.path.join(railway_volume_mount_path, "lwa-platform.sqlite3")
            if railway_volume_mount_path
            else os.path.join(os.getcwd(), "generated", "lwa-platform.sqlite3")
        )
        self.platform_db_path = os.getenv("LWA_PLATFORM_DB_PATH", default_platform_db)
        default_worlds_db = (
            os.path.join(railway_volume_mount_path, "lwa-worlds.sqlite3")
            if railway_volume_mount_path
            else os.path.join(os.getcwd(), "generated", "lwa-worlds.sqlite3")
        )
        self.worlds_db_path = os.getenv("LWA_WORLDS_DB_PATH", default_worlds_db)
        default_clipping_db = (
            os.path.join(railway_volume_mount_path, "lwa-clipping.sqlite3")
            if railway_volume_mount_path
            else os.path.join(os.getcwd(), "generated", "lwa-clipping.sqlite3")
        )
        self.clipping_db_path = os.getenv("LWA_CLIPPING_DB_PATH", default_clipping_db)
        self.max_upload_mb = _env_int("MAX_UPLOAD_MB", 500, minimum=1)
        self.jwt_secret = os.getenv("LWA_JWT_SECRET", "dev-secret-change-me")
        self.jwt_exp_minutes = _env_int("LWA_JWT_EXP_MINUTES", 43200, minimum=1)
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
        self.ai_provider = os.getenv("LWA_AI_PROVIDER") or os.getenv("AI_PROVIDER", "auto")
        self.enable_anthropic = _env_bool(
            "LWA_ENABLE_ANTHROPIC",
            os.getenv("ENABLE_ANTHROPIC", "true"),
        )
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")
        self.anthropic_model_opus = os.getenv("ANTHROPIC_MODEL_OPUS", "claude-opus-4-7")
        self.anthropic_model_sonnet = os.getenv("ANTHROPIC_MODEL_SONNET", "claude-sonnet-4-6")
        self.anthropic_model_haiku = os.getenv("ANTHROPIC_MODEL_HAIKU", "claude-haiku-4-5-20251001")
        self.premium_reasoning_provider = os.getenv("LWA_PREMIUM_REASONING_PROVIDER", "anthropic").strip().lower() or "anthropic"
        # AI Cost Control Settings
        self.ai_cost_control_enabled = _env_bool("LWA_AI_COST_CONTROL_ENABLED", "true")
        self.ai_daily_budget_guest = _env_int("LWA_AI_DAILY_BUDGET_GUEST", 10.0, minimum=0)
        self.ai_daily_budget_user = _env_int("LWA_AI_DAILY_BUDGET_USER", 50.0, minimum=0)
        self.ai_daily_requests_guest = _env_int("LWA_AI_DAILY_REQUESTS_GUEST", 30, minimum=1)
        self.ai_daily_requests_user = _env_int("LWA_AI_DAILY_REQUESTS_USER", 100, minimum=1)
        self.seedance_enabled = _env_bool("SEEDANCE_ENABLED", os.getenv("LWA_SEEDANCE_ENABLED", "false"))
        self.seedance_api_key = os.getenv("SEEDANCE_API_KEY", os.getenv("LWA_SEEDANCE_API_KEY", "")).strip()
        self.seedance_base_url = os.getenv("SEEDANCE_BASE_URL", os.getenv("LWA_SEEDANCE_BASE_URL", "")).strip().rstrip("/")
        self.seedance_model = os.getenv("SEEDANCE_MODEL", os.getenv("LWA_SEEDANCE_MODEL", "seedance-2.0")).strip() or "seedance-2.0"
        self.seedance_timeout_seconds = _env_int("SEEDANCE_TIMEOUT_SECONDS", os.getenv("LWA_SEEDANCE_TIMEOUT_SECONDS", "180"), minimum=1)
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "llama3.2")
        self.visual_generation_enabled = os.getenv("LWA_VISUAL_GENERATION_ENABLED", "true").strip().lower() in {"1", "true", "yes", "on"}
        self.visual_generation_model = os.getenv("LWA_VISUAL_GENERATION_MODEL", "lwa-visual-v1").strip() or "lwa-visual-v1"
        self.visual_generation_timeout_seconds = _env_int("LWA_VISUAL_GENERATION_TIMEOUT_SECONDS", 180, minimum=1)
        self.visual_generation_poll_interval_seconds = _env_int("LWA_VISUAL_GENERATION_POLL_INTERVAL_SECONDS", 3, minimum=1)
        self.visual_engine_enabled = _env_bool(
            "LWA_VISUAL_ENGINE_ENABLED",
            os.getenv("LWA_VISUAL_GENERATION_ENABLED", "true"),
        )
        self.visual_engine_api_key = os.getenv("LWA_VISUAL_ENGINE_API_KEY", "").strip()
        self.visual_engine_base_url = os.getenv("LWA_VISUAL_ENGINE_API_BASE_URL", "").strip()
        self.visual_engine_timeout_seconds = _env_int(
            "LWA_VISUAL_ENGINE_TIMEOUT_SECONDS",
            self.visual_generation_timeout_seconds,
            minimum=1,
        )
        self.visual_engine_max_renders_per_request = _env_int(
            "LWA_VISUAL_ENGINE_MAX_RENDERS_PER_REQUEST",
            1,
            minimum=1,
        )
        self.enable_whop_verification = _env_bool("LWA_ENABLE_WHOP_VERIFICATION", "false")
        self.whop_api_key = os.getenv("WHOP_API_KEY", "")
        self.whop_company_id = os.getenv("WHOP_COMPANY_ID", "")
        self.whop_product_id = os.getenv("WHOP_PRODUCT_ID", "").strip()
        self.whop_webhook_secret = os.getenv("WHOP_WEBHOOK_SECRET", "").strip()
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
        # Video OS Configuration
        self.video_os_enabled = _env_bool("LWA_VIDEO_OS_ENABLED", "false")
        self.video_provider = os.getenv("LWA_VIDEO_PROVIDER", "mock").strip() or "mock"
        self.video_max_duration_seconds = _env_int("LWA_VIDEO_MAX_DURATION_SECONDS", "30", minimum=1)
        self.video_max_inputs = _env_int("LWA_VIDEO_MAX_INPUTS", "10", minimum=1)
        self.video_max_resolution = os.getenv("LWA_VIDEO_MAX_RESOLUTION", "1080p").strip() or "1080p"
        self.video_allow_live_providers = _env_bool("LWA_VIDEO_ALLOW_LIVE_PROVIDERS", "false")
        self.video_storage_provider = os.getenv("LWA_VIDEO_STORAGE_PROVIDER", "local_placeholder").strip() or "local_placeholder"
        # Ingest Engine Configuration
        self.ingest_engine_enabled = _env_bool("LWA_INGEST_ENGINE_ENABLED", "true")
        self.ingest_storage_provider = os.getenv("LWA_INGEST_STORAGE_PROVIDER", "local_placeholder").strip() or "local_placeholder"
        self.ingest_max_file_size_mb = _env_int("LWA_INGEST_MAX_FILE_SIZE_MB", "100", minimum=1)
        self.ingest_max_assets_per_user = _env_int("LWA_INGEST_MAX_ASSETS_PER_USER", "50", minimum=1)
        self.ingest_allowed_file_types = os.getenv("LWA_INGEST_ALLOWED_FILE_TYPES", "mp4,mov,avi,mkv,mp3,wav,m4a,jpg,jpeg,png,gif,txt,md").strip() or "mp4,mov,avi,mkv,mp3,wav,m4a,jpg,jpeg,png,gif,txt,md"


@lru_cache
def get_settings() -> Settings:
    return Settings()
