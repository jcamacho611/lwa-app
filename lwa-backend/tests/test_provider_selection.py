"""Tests for provider selection, fallback behavior, and schema normalization."""
import os
import sys
from unittest.mock import patch, MagicMock

import pytest

# Add the backend to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ---------------------------------------------------------------------------
# Config / Provider selection tests
# ---------------------------------------------------------------------------


class TestDetermineProvider:
    """Test determine_provider logic in generation.py."""

    def _make_settings(self, **overrides):
        """Build a Settings-like object with sensible defaults."""
        defaults = {
            "ai_provider": "auto",
            "openai_api_key": "",
            "ollama_base_url": "",
            "ollama_model": "llama3.2",
            "anthropic_api_key": "",
            "enable_anthropic": True,
            "anthropic_model_sonnet": "claude-sonnet-4-20250514",
            "anthropic_model_opus": "claude-opus-4-20250514",
            "anthropic_model_haiku": "claude-haiku-3-20240307",
            "premium_reasoning_provider": "anthropic",
        }
        defaults.update(overrides)
        m = MagicMock()
        for k, v in defaults.items():
            setattr(m, k, v)
        return m

    @patch("app.services.anthropic_service._load_sdk", return_value=MagicMock())
    def test_auto_prefers_anthropic_when_key_present(self, mock_sdk):
        from app.generation import determine_provider
        settings = self._make_settings(anthropic_api_key="sk-ant-xxx")
        assert determine_provider(settings) == "anthropic"

    @patch("app.services.anthropic_service._load_sdk", return_value=None)
    def test_auto_falls_to_openai_when_anthropic_sdk_missing(self, mock_sdk):
        from app.generation import determine_provider
        settings = self._make_settings(
            anthropic_api_key="sk-ant-xxx",
            openai_api_key="sk-xxx",
        )
        assert determine_provider(settings) == "openai"

    @patch("app.services.anthropic_service._load_sdk", return_value=MagicMock())
    def test_auto_falls_to_openai_when_anthropic_disabled(self, mock_sdk):
        from app.generation import determine_provider
        settings = self._make_settings(
            anthropic_api_key="sk-ant-xxx",
            enable_anthropic=False,
            openai_api_key="sk-xxx",
        )
        assert determine_provider(settings) == "openai"

    def test_auto_falls_to_ollama(self):
        from app.generation import determine_provider
        settings = self._make_settings(ollama_base_url="http://localhost:11434")
        assert determine_provider(settings) == "ollama"

    def test_auto_falls_to_heuristic(self):
        from app.generation import determine_provider
        settings = self._make_settings()
        assert determine_provider(settings) == "heuristic"

    def test_explicit_provider_is_respected(self):
        from app.generation import determine_provider
        settings = self._make_settings(ai_provider="openai", openai_api_key="sk-xxx")
        assert determine_provider(settings) == "openai"


# ---------------------------------------------------------------------------
# Anthropic service tests
# ---------------------------------------------------------------------------


class TestAnthropicService:

    def _make_settings(self, **overrides):
        defaults = {
            "anthropic_api_key": "",
            "enable_anthropic": True,
            "anthropic_model_sonnet": "claude-sonnet-4-20250514",
            "anthropic_model_opus": "claude-opus-4-20250514",
            "anthropic_model_haiku": "claude-haiku-3-20240307",
            "premium_reasoning_provider": "anthropic",
        }
        defaults.update(overrides)
        m = MagicMock()
        for k, v in defaults.items():
            setattr(m, k, v)
        return m

    @patch("app.services.anthropic_service._load_sdk", return_value=None)
    def test_unavailable_when_sdk_missing(self, mock_sdk):
        from app.services.anthropic_service import anthropic_available
        settings = self._make_settings(anthropic_api_key="sk-ant-xxx")
        assert anthropic_available(settings) is False

    @patch("app.services.anthropic_service._load_sdk", return_value=MagicMock())
    def test_unavailable_when_key_missing(self, mock_sdk):
        from app.services.anthropic_service import anthropic_available
        settings = self._make_settings(anthropic_api_key="")
        assert anthropic_available(settings) is False

    @patch("app.services.anthropic_service._load_sdk", return_value=MagicMock())
    def test_unavailable_when_disabled(self, mock_sdk):
        from app.services.anthropic_service import anthropic_available
        settings = self._make_settings(
            anthropic_api_key="sk-ant-xxx",
            enable_anthropic=False,
        )
        assert anthropic_available(settings) is False

    @patch("app.services.anthropic_service._load_sdk", return_value=MagicMock())
    def test_available_when_configured(self, mock_sdk):
        from app.services.anthropic_service import anthropic_available
        settings = self._make_settings(anthropic_api_key="sk-ant-xxx")
        assert anthropic_available(settings) is True

    def test_resolve_tier_premium(self):
        from app.services.anthropic_service import resolve_anthropic_tier_for_plan
        settings = self._make_settings()
        assert resolve_anthropic_tier_for_plan(settings, "pro") == "opus"

    def test_resolve_tier_default(self):
        from app.services.anthropic_service import resolve_anthropic_tier_for_plan
        settings = self._make_settings()
        assert resolve_anthropic_tier_for_plan(settings, "free") == "sonnet"

    def test_resolve_tier_non_anthropic_provider(self):
        from app.services.anthropic_service import resolve_anthropic_tier_for_plan
        settings = self._make_settings(premium_reasoning_provider="openai")
        assert resolve_anthropic_tier_for_plan(settings, "pro") == "sonnet"


# ---------------------------------------------------------------------------
# Seedance service tests
# ---------------------------------------------------------------------------


class TestSeedanceService:

    def _make_settings(self, **overrides):
        defaults = {
            "seedance_enabled": False,
            "seedance_api_key": "",
            "seedance_base_url": "",
            "seedance_model": "seedance-1-lite",
            "seedance_timeout_seconds": 120,
            "seedance_poll_interval_seconds": 5,
        }
        defaults.update(overrides)
        m = MagicMock()
        for k, v in defaults.items():
            setattr(m, k, v)
        return m

    def test_unavailable_when_disabled(self):
        from app.services.seedance_service import seedance_available
        settings = self._make_settings(
            seedance_api_key="xxx",
            seedance_base_url="https://api.seedance.ai",
        )
        assert seedance_available(settings) is False

    def test_unavailable_when_no_key(self):
        from app.services.seedance_service import seedance_available
        settings = self._make_settings(
            seedance_enabled=True,
            seedance_base_url="https://api.seedance.ai",
        )
        assert seedance_available(settings) is False

    def test_unavailable_when_no_url(self):
        from app.services.seedance_service import seedance_available
        settings = self._make_settings(
            seedance_enabled=True,
            seedance_api_key="xxx",
        )
        assert seedance_available(settings) is False

    def test_available_when_fully_configured(self):
        from app.services.seedance_service import seedance_available
        settings = self._make_settings(
            seedance_enabled=True,
            seedance_api_key="xxx",
            seedance_base_url="https://api.seedance.ai",
        )
        assert seedance_available(settings) is True

    @pytest.mark.asyncio
    async def test_submit_raises_when_disabled(self):
        from app.services.seedance_service import (
            SeedanceJobRequest,
            SeedanceUnavailableError,
            submit_seedance_job,
        )
        settings = self._make_settings()
        with pytest.raises(SeedanceUnavailableError):
            await submit_seedance_job(
                settings=settings,
                request=SeedanceJobRequest(prompt="test"),
            )

    @pytest.mark.asyncio
    async def test_poll_raises_when_disabled(self):
        from app.services.seedance_service import (
            SeedanceUnavailableError,
            poll_seedance_job,
        )
        settings = self._make_settings()
        with pytest.raises(SeedanceUnavailableError):
            await poll_seedance_job(settings=settings, job_id="test-id")


# ---------------------------------------------------------------------------
# Schema normalization tests
# ---------------------------------------------------------------------------


class TestSchemaNormalization:

    def test_seedance_background_request_defaults(self):
        from app.models.schemas import SeedanceBackgroundRequest
        req = SeedanceBackgroundRequest(prompt="test prompt")
        assert req.style_preset == "mythic-void"
        assert req.motion_profile == "slow-drift"
        assert req.duration_seconds == 8
        assert req.aspect_ratio == "16:9"

    def test_seedance_background_request_custom(self):
        from app.models.schemas import SeedanceBackgroundRequest
        req = SeedanceBackgroundRequest(
            prompt="custom",
            style_preset="cinematic",
            duration_seconds=15,
        )
        assert req.style_preset == "cinematic"
        assert req.duration_seconds == 15

    def test_seedance_job_response_minimal(self):
        from app.models.schemas import SeedanceJobResponse
        resp = SeedanceJobResponse(job_id="j-1", status="queued")
        assert resp.job_id == "j-1"
        assert resp.asset_url is None

    def test_seedance_status_disabled(self):
        from app.models.schemas import SeedanceStatusResponse
        resp = SeedanceStatusResponse(enabled=False, message="Seedance not enabled")
        assert resp.enabled is False
        assert resp.job is None


# ---------------------------------------------------------------------------
# Fallback / malformed output tests
# ---------------------------------------------------------------------------


class TestMalformedOutputFallback:
    """Verify that parse_generated_clips falls back on garbage model output."""

    def test_invalid_json_falls_back(self):
        from app.generation import parse_generated_clips
        result = parse_generated_clips(
            raw="this is not json at all!!!",
            video_url="https://example.com/video.mp4",
            target_platform="tiktok",
            selected_trend=None,
            content_angle=None,
            trend_context=[],
            source_context=None,
        )
        assert isinstance(result, list)
        assert len(result) > 0

    def test_empty_clips_array_falls_back(self):
        from app.generation import parse_generated_clips
        result = parse_generated_clips(
            raw='{"clips": []}',
            video_url="https://example.com/video.mp4",
            target_platform="instagram",
            selected_trend=None,
            content_angle=None,
            trend_context=[],
            source_context=None,
        )
        assert isinstance(result, list)
        assert len(result) > 0


# ---------------------------------------------------------------------------
# Startup / import safety tests
# ---------------------------------------------------------------------------


class TestStartupSafety:
    """Verify all modules can be imported without crashing."""

    def test_import_anthropic_service(self):
        import app.services.anthropic_service  # noqa: F401

    def test_import_seedance_service(self):
        import app.services.seedance_service  # noqa: F401

    def test_import_generation(self):
        import app.generation  # noqa: F401

    def test_import_schemas(self):
        import app.models.schemas  # noqa: F401

    def test_import_seedance_routes(self):
        import app.api.routes.seedance  # noqa: F401
