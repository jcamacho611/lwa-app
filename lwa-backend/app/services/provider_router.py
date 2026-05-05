"""
LWA Brain — Provider Router

Routes external AI and media provider requests safely.
Preserves deterministic output if providers fail.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from enum import Enum


class ProviderType(Enum):
    """Types of external providers LWA can use."""
    TEXT_INTELLIGENCE = "text_intelligence"  # OpenAI, Anthropic
    CAPTION_STYLE = "caption_style"  # Style enhancement
    VIDEO_GENERATION = "video_generation"  # Seedance, Replicate
    VOICE_MUSIC = "voice_music"  # ElevenLabs
    RENDER_EXPORT = "render_export"  # Video rendering
    SOCIAL_API = "social_api"  # Platform APIs


@dataclass
class ProviderStatus:
    """Health status of a provider."""
    provider_type: ProviderType
    name: str
    available: bool
    healthy: bool
    last_error: Optional[str] = None
    response_time_ms: Optional[int] = None


@dataclass
class ProviderRouterConfig:
    """Configuration for provider routing."""
    # Enable/disable provider types
    enable_text_intelligence: bool = True
    enable_video_generation: bool = True
    enable_voice_enhancement: bool = False
    
    # Failover settings
    fallback_to_deterministic: bool = True
    max_retries: int = 1
    timeout_seconds: int = 30


class ProviderRouter:
    """
    Routes enhancement requests to external providers safely.
    
    Core principle: Providers are optional enrichment paths.
    The deterministic engine is the survival requirement.
    
    Usage:
        router = ProviderRouter()
        if router.can_enhance_text():
            enhanced = router.enhance_text_clip(base_clip)
        else:
            # Deterministic output preserved automatically
            pass
    """
    
    def __init__(self, config: Optional[ProviderRouterConfig] = None):
        self.config = config or ProviderRouterConfig()
        self._provider_health: Dict[ProviderType, ProviderStatus] = {}
        self._refresh_health()
    
    def _refresh_health(self) -> None:
        """Check all provider health statuses."""
        self._provider_health = {
            ProviderType.TEXT_INTELLIGENCE: self._check_text_provider_health(),
            ProviderType.VIDEO_GENERATION: self._check_video_provider_health(),
            ProviderType.VOICE_MUSIC: self._check_voice_provider_health(),
        }
    
    def _check_text_provider_health(self) -> ProviderStatus:
        """Check if text intelligence providers are available."""
        openai_key = os.environ.get("OPENAI_API_KEY")
        anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
        
        available = bool(openai_key or anthropic_key)
        
        return ProviderStatus(
            provider_type=ProviderType.TEXT_INTELLIGENCE,
            name="Text Intelligence (OpenAI/Anthropic)",
            available=available,
            healthy=available,  # Simplified - could do actual health checks
        )
    
    def _check_video_provider_health(self) -> ProviderStatus:
        """Check if video generation providers are available."""
        seedance_key = os.environ.get("SEEDANCE_API_KEY")
        replicate_key = os.environ.get("REPLICATE_API_TOKEN")
        
        available = bool(seedance_key or replicate_key)
        
        return ProviderStatus(
            provider_type=ProviderType.VIDEO_GENERATION,
            name="Video Generation (Seedance/Replicate)",
            available=available,
            healthy=available,
        )
    
    def _check_voice_provider_health(self) -> ProviderStatus:
        """Check if voice providers are available."""
        elevenlabs_key = os.environ.get("ELEVENLABS_API_KEY")
        
        available = bool(elevenlabs_key)
        
        return ProviderStatus(
            provider_type=ProviderType.VOICE_MUSIC,
            name="Voice Enhancement (ElevenLabs)",
            available=available,
            healthy=available,
        )
    
    def check_health(self) -> Dict[ProviderType, ProviderStatus]:
        """Get health status of all providers."""
        self._refresh_health()
        return self._provider_health.copy()
    
    def can_enhance_text(self) -> bool:
        """Check if text enhancement is available."""
        status = self._provider_health.get(ProviderType.TEXT_INTELLIGENCE)
        return status.available and status.healthy if status else False
    
    def can_render_video(self) -> bool:
        """Check if video rendering is available."""
        status = self._provider_health.get(ProviderType.VIDEO_GENERATION)
        return status.available and status.healthy if status else False
    
    def can_enhance_voice(self) -> bool:
        """Check if voice enhancement is available."""
        status = self._provider_health.get(ProviderType.VOICE_MUSIC)
        return status.available and status.healthy if status else False
    
    def get_available_providers(self) -> List[ProviderStatus]:
        """Get list of all available providers."""
        return [
            status for status in self._provider_health.values()
            if status.available and status.healthy
        ]
    
    def enrich_clip_pack(
        self,
        base_output: Dict[str, Any],
        prefer_online: bool = True
    ) -> Dict[str, Any]:
        """
        Attempt to enrich clip pack with provider enhancements.
        
        If providers fail or are unavailable, returns base_output unchanged.
        This preserves the deterministic output guarantee.
        
        Args:
            base_output: Deterministic clip pack output
            prefer_online: Whether to attempt online enrichment
            
        Returns:
            Enriched output if providers succeed, base_output otherwise
        """
        if not prefer_online:
            return base_output
        
        # Check if any enhancement is possible
        available = self.get_available_providers()
        if not available:
            # No providers available - return deterministic output
            return base_output
        
        try:
            # Attempt enrichment (implement actual logic as needed)
            # For now, return base output with provider metadata
            enriched = base_output.copy()
            enriched["_provider_enhanced"] = False
            enriched["_providers_available"] = [p.name for p in available]
            return enriched
            
        except Exception as e:
            # Provider failed - preserve deterministic output
            # Log the failure but don't break the user experience
            return {
                **base_output,
                "_provider_error": str(e),
                "_fallback_used": True,
                "render_status": base_output.get("render_status", "strategy_only"),
            }
    
    def get_enhancement_summary(self) -> Dict[str, Any]:
        """Get summary of available enhancements."""
        health = self.check_health()
        
        return {
            "text_intelligence": {
                "available": self.can_enhance_text(),
                "provider": health.get(ProviderType.TEXT_INTELLIGENCE),
            },
            "video_rendering": {
                "available": self.can_render_video(),
                "provider": health.get(ProviderType.VIDEO_GENERATION),
            },
            "voice_enhancement": {
                "available": self.can_enhance_voice(),
                "provider": health.get(ProviderType.VOICE_MUSIC),
            },
            "fallback_enabled": self.config.fallback_to_deterministic,
            "offline_mode_works": True,  # LWA guarantee
        }


# Singleton instance for app-wide use
_provider_router: Optional[ProviderRouter] = None


def get_provider_router() -> ProviderRouter:
    """Get or create the singleton provider router."""
    global _provider_router
    if _provider_router is None:
        _provider_router = ProviderRouter()
    return _provider_router
