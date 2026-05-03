"""
Source Fallback Hardening v0

Provides graceful degradation when source ingest fails.
Ensures LWA always returns usable results even when external sources block access.
"""

import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

from ..core.config import Settings
from ..models.schemas import ProcessRequest
from ..services.source_ingest import build_strategy_source_context, infer_source_type
from ..services.source_errors import classify_source_failure, SourceFailure

logger = logging.getLogger("uvicorn.error")


class FallbackStrategy(str, Enum):
    """Fallback strategies when source ingest fails."""
    
    STRATEGY_ONLY = "strategy_only"
    MOCK_METADATA = "mock_metadata"
    USER_PROVIDED = "user_provided"
    DEGRADED_RESPONSE = "degraded_response"


@dataclass
class FallbackResult:
    """Result of fallback processing."""
    
    strategy: FallbackStrategy
    source_context: Dict[str, Any]
    fallback_reason: str
    degraded: bool = True
    metadata: Dict[str, Any] = None


class SourceFallbackService:
    """
    Provides graceful degradation when source ingest fails.
    
    Ensures LWA always returns usable results even when external sources
    block access or are unavailable.
    """
    
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
    
    async def handle_source_failure(
        self,
        request: ProcessRequest,
        error: Exception,
        source_url: Optional[str] = None
    ) -> FallbackResult:
        """
        Handle source ingest failure with graceful degradation.
        
        Args:
            request: Original process request
            error: The error that occurred
            source_url: The source URL that failed
            
        Returns:
            FallbackResult with degraded but usable response
        """
        
        try:
            # Classify the failure type
            source_failure = classify_source_failure(error)
            fallback_reason = source_failure.user_message if source_failure else str(error)
            
            # Determine best fallback strategy
            strategy = self._select_fallback_strategy(request, source_failure)
            
            # Generate fallback source context
            source_context = await self._generate_fallback_context(
                request, strategy, source_url, source_failure
            )
            
            logger.info(
                "source_fallback_applied strategy=%s reason=%s source_url=%s",
                strategy.value,
                fallback_reason,
                source_url
            )
            
            return FallbackResult(
                strategy=strategy,
                source_context=source_context,
                fallback_reason=fallback_reason,
                degraded=True,
                metadata={
                    "original_error": str(error),
                    "source_failure_code": source_failure.code.value if source_failure else None,
                    "original_source_url": source_url
                }
            )
            
        except Exception as fallback_error:
            logger.error(f"fallback_processing_failed error={str(fallback_error)}")
            
            # Last resort: return basic strategy-only response
            return await self._emergency_fallback(request, source_url, str(error))
    
    def _select_fallback_strategy(
        self, request: ProcessRequest, source_failure: Optional[SourceFailure]
    ) -> FallbackStrategy:
        """Select the best fallback strategy based on request and failure."""
        
        # If user provided sufficient context, use user-provided strategy
        has_user_context = bool(
            (request.prompt or "").strip() or
            (request.text_prompt or "").strip() or
            (request.campaign_goal or "").strip() or
            (request.campaign_brief or "").strip()
        )
        
        if has_user_context:
            return FallbackStrategy.USER_PROVIDED
        
        # For platform blocks, use strategy-only with explanation
        if source_failure and source_failure.code.value in [
            "PLATFORM_BLOCKED", "PLATFORM_PRIVATE", "PLATFORM_LIVE"
        ]:
            return FallbackStrategy.STRATEGY_ONLY
        
        # For timeouts and unavailability, try mock metadata
        if source_failure and source_failure.code.value in [
            "SOURCE_TIMEOUT", "SOURCE_UNAVAILABLE", "UNSUPPORTED_SOURCE"
        ]:
            return FallbackStrategy.MOCK_METADATA
        
        # Default to strategy-only
        return FallbackStrategy.STRATEGY_ONLY
    
    async def _generate_fallback_context(
        self,
        request: ProcessRequest,
        strategy: FallbackStrategy,
        source_url: Optional[str],
        source_failure: Optional[SourceFailure]
    ) -> Dict[str, Any]:
        """Generate fallback source context based on strategy."""
        
        if strategy == FallbackStrategy.USER_PROVIDED:
            return await self._user_provided_context(request, source_url)
        
        elif strategy == FallbackStrategy.MOCK_METADATA:
            return await self._mock_metadata_context(request, source_url, source_failure)
        
        elif strategy == FallbackStrategy.STRATEGY_ONLY:
            return await self._strategy_only_context(request, source_url, source_failure)
        
        else:
            return await self._degraded_response_context(request, source_url, source_failure)
    
    async def _user_provided_context(
        self, request: ProcessRequest, source_url: Optional[str]
    ) -> Dict[str, Any]:
        """Generate context from user-provided information."""
        
        source_type = infer_source_type(request)
        source_value = source_url or (request.prompt or "").strip() or "user provided content"
        
        return build_strategy_source_context(
            request=request,
            source_type=source_type,
            source_value=source_value
        ).__dict__
    
    async def _mock_metadata_context(
        self,
        request: ProcessRequest,
        source_url: Optional[str],
        source_failure: Optional[SourceFailure]
    ) -> Dict[str, Any]:
        """Generate context with mock metadata when source is unavailable."""
        
        source_type = infer_source_type(request)
        source_value = source_url or "unavailable source"
        
        # Create mock metadata based on source type
        if source_type in ["video", "video_upload", "url"]:
            mock_title = self._extract_title_from_request(request) or "Video Content"
            mock_duration = 120  # 2 minutes default
            mock_uploader = "Content Creator"
        elif source_type in ["audio", "audio_upload"]:
            mock_title = self._extract_title_from_request(request) or "Audio Content"
            mock_duration = 180  # 3 minutes default
            mock_uploader = "Audio Creator"
        else:
            mock_title = self._extract_title_from_request(request) or "Content"
            mock_duration = 60  # 1 minute default
            mock_uploader = "Creator"
        
        from ..processor import SourceContext
        
        context = SourceContext(
            title=mock_title,
            description=self._build_fallback_description(request, source_failure),
            uploader=mock_uploader,
            duration_seconds=mock_duration,
            source_url=source_value,
            clip_seeds=[],
            processing_mode="fallback_metadata",
            selection_strategy=f"{source_type}_fallback",
            source_type=source_type,
            source_platform="Fallback",
            transcript=self._build_fallback_transcript(request),
            visual_summary=(
                f"Source could not be processed due to {source_failure.user_message if source_failure else 'access issues'}. "
                f"LWA generated a strategy package using available context and mock metadata for {mock_title}."
            ),
        )
        
        return context.__dict__
    
    async def _strategy_only_context(
        self,
        request: ProcessRequest,
        source_url: Optional[str],
        source_failure: Optional[SourceFailure]
    ) -> Dict[str, Any]:
        """Generate strategy-only context when no source can be processed."""
        
        source_type = infer_source_type(request)
        source_value = source_url or "unavailable source"
        
        from ..processor import SourceContext
        
        context = SourceContext(
            title=self._extract_title_from_request(request) or "Strategy Package",
            description=self._build_fallback_description(request, source_failure),
            uploader=None,
            duration_seconds=None,
            source_url=source_value,
            clip_seeds=[],
            processing_mode="strategy_only",
            selection_strategy=f"{source_type}_strategy_only",
            source_type=source_type,
            source_platform="Strategy Only",
            transcript=self._build_fallback_transcript(request),
            visual_summary=(
                f"Source could not be processed due to {source_failure.user_message if source_failure else 'access issues'}. "
                "LWA generated a strategy-only package with hooks, captions, and posting guidance. "
                "Upload the source file directly or use prompt mode for complete control."
            ),
        )
        
        return context.__dict__
    
    async def _degraded_response_context(
        self,
        request: ProcessRequest,
        source_url: Optional[str],
        source_failure: Optional[SourceFailure]
    ) -> Dict[str, Any]:
        """Generate minimal degraded response context."""
        
        source_type = infer_source_type(request)
        source_value = source_url or "degraded source"
        
        from ..processor import SourceContext
        
        context = SourceContext(
            title="Degraded Response",
            description="Limited information available due to source access issues.",
            uploader=None,
            duration_seconds=None,
            source_url=source_value,
            clip_seeds=[],
            processing_mode="degraded",
            selection_strategy="degraded_fallback",
            source_type=source_type,
            source_platform="Degraded",
            transcript="Source processing failed. Limited context available.",
            visual_summary=(
                "Severe source access limitations. LWA provided minimal guidance. "
                "Consider uploading files directly or using prompt mode for better results."
            ),
        )
        
        return context.__dict__
    
    async def _emergency_fallback(
        self, request: ProcessRequest, source_url: Optional[str], error: str
    ) -> FallbackResult:
        """Emergency fallback when all other strategies fail."""
        
        logger.error(f"emergency_fallback_used error={error}")
        
        from ..processor import SourceContext
        
        context = SourceContext(
            title="Emergency Fallback",
            description="System experienced critical errors during source processing.",
            uploader=None,
            duration_seconds=None,
            source_url=source_url or "emergency",
            clip_seeds=[],
            processing_mode="emergency",
            selection_strategy="emergency_fallback",
            source_type="emergency",
            source_platform="Emergency",
            transcript="Emergency fallback activated due to system errors.",
            visual_summary=(
                "LWA experienced critical errors. Try again later or contact support "
                "if this issue persists. Consider using prompt mode for immediate results."
            ),
        )
        
        return FallbackResult(
            strategy=FallbackStrategy.DEGRADED_RESPONSE,
            source_context=context.__dict__,
            fallback_reason="Critical system error during source processing",
            degraded=True,
            metadata={"emergency_fallback": True, "original_error": error}
        )
    
    def _extract_title_from_request(self, request: ProcessRequest) -> Optional[str]:
        """Extract title from request metadata or prompts."""
        
        # Try source metadata first
        if request.source_metadata and "title" in request.source_metadata:
            return request.source_metadata["title"]
        
        # Try prompts
        for prompt_field in [request.prompt, request.text_prompt, request.campaign_goal, request.campaign_brief]:
            if prompt_field and len(prompt_field.strip()) > 0:
                # Use first 60 characters as title
                return prompt_field.strip()[:60]
        
        return None
    
    def _build_fallback_description(
        self, request: ProcessRequest, source_failure: Optional[SourceFailure]
    ) -> str:
        """Build description for fallback context."""
        
        parts = []
        
        # Add user-provided context
        for field in [request.prompt, request.text_prompt, request.campaign_goal, request.campaign_brief]:
            if field and len(field.strip()) > 0:
                parts.append(field.strip())
        
        # Add platform info
        if request.allowed_platforms:
            parts.append(f"Target platforms: {', '.join(request.allowed_platforms)}")
        
        # Add content angle
        if request.content_angle:
            parts.append(f"Content angle: {request.content_angle}")
        
        # Add failure context
        if source_failure:
            parts.append(f"Note: Source unavailable - {source_failure.user_message}")
        
        return " | ".join(parts) if parts else "Limited source information available."
    
    def _build_fallback_transcript(self, request: ProcessRequest) -> str:
        """Build transcript for fallback context."""
        
        # Combine user-provided text as transcript
        transcript_parts = []
        
        for field in [request.prompt, request.text_prompt, request.campaign_goal, request.campaign_brief]:
            if field and len(field.strip()) > 0:
                transcript_parts.append(field.strip())
        
        if transcript_parts:
            return " | ".join(transcript_parts)
        
        return "No transcript available due to source access limitations."
    
    async def validate_source_accessibility(self, source_url: str) -> Dict[str, Any]:
        """
        Validate if a source is accessible before full processing.
        
        Args:
            source_url: URL to validate
            
        Returns:
            Validation result with accessibility status
        """
        
        try:
            # Quick accessibility check
            import yt_dlp
            
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,  # Don't download, just check availability
                'socket_timeout': 10,
                'retries': 1,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(source_url, download=False)
                
                return {
                    "accessible": True,
                    "title": info.get("title"),
                    "duration": info.get("duration"),
                    "uploader": info.get("uploader"),
                    "availability": "public"
                }
                
        except Exception as error:
            source_failure = classify_source_failure(error)
            
            return {
                "accessible": False,
                "error": str(error),
                "failure_code": source_failure.code.value if source_failure else None,
                "user_message": source_failure.user_message if source_failure else "Source could not be accessed",
                "availability": "blocked"
            }


# Singleton instance
source_fallback_service = lambda settings: SourceFallbackService(settings)
