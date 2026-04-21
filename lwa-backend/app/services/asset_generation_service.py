from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union
from uuid import uuid4

from .generation_providers.seedance_provider import SeedanceProvider
from .generation_providers.base_provider import BaseGenerationProvider
from ..core.config import Settings
from ..models.schemas import GenerationRequest, GenerationResponse

logger = logging.getLogger("uvicorn.error")


class AssetGenerationService:
    """Service for coordinating asset generation across multiple providers."""
    
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.providers: Dict[str, BaseGenerationProvider] = {}
        self._initialize_providers()
    
    def _initialize_providers(self) -> None:
        """Initialize available generation providers."""
        # Initialize Seedance provider
        if self.settings.seedance_api_key:
            self.providers["seedance"] = SeedanceProvider(self.settings)
            logger.info("seedance_provider_initialized")
        else:
            logger.warning("seedance_provider_disabled_missing_api_key")
    
    async def generate_from_text(
        self,
        *,
        text_prompt: str,
        provider: str = "seedance",
        duration: Optional[float] = 30.0,
        style: Optional[str] = None,
        aspect_ratio: str = "9:16",
        user_id: Optional[str] = None,
        **kwargs: Any,
    ) -> GenerationResponse:
        """Generate video from text prompt using specified provider."""
        try:
            if provider not in self.providers:
                raise ValueError(f"Provider '{provider}' not available")
            
            generation_provider = self.providers[provider]
            
            logger.info(f"asset_generation_started provider={provider} prompt={text_prompt[:50]}...")
            
            # Generate using the provider
            response = await generation_provider.generate_from_text(
                text_prompt=text_prompt,
                duration=duration,
                style=style,
                aspect_ratio=aspect_ratio,
                **kwargs
            )
            
            # Add service-level metadata
            response.metadata.update({
                "service_request_id": f"gen_{uuid4().hex[:12]}",
                "user_id": user_id,
                "provider_used": provider,
                "generation_timestamp": self._get_timestamp(),
            })
            
            logger.info(f"asset_generation_completed provider={provider} clips={len(response.clips)}")
            
            return response
            
        except Exception as error:
            logger.error(f"asset_generation_failed provider={provider} error={str(error)}")
            raise ValueError(f"Asset generation failed: {str(error)}")
    
    async def generate_from_image(
        self,
        *,
        image_path: Union[str, Path],
        provider: str = "seedance",
        prompt: Optional[str] = None,
        duration: Optional[float] = 30.0,
        motion_strength: str = "medium",
        user_id: Optional[str] = None,
        **kwargs: Any,
    ) -> GenerationResponse:
        """Generate video from image using specified provider."""
        try:
            if provider not in self.providers:
                raise ValueError(f"Provider '{provider}' not available")
            
            generation_provider = self.providers[provider]
            
            logger.info(f"asset_generation_started provider={provider} image={image_path}")
            
            # Validate image path
            image_file = Path(image_path)
            if not image_file.exists():
                raise ValueError(f"Image file not found: {image_path}")
            
            # Generate using the provider
            response = await generation_provider.generate_from_image(
                image_path=image_file,
                prompt=prompt,
                duration=duration,
                motion_strength=motion_strength,
                **kwargs
            )
            
            # Add service-level metadata
            response.metadata.update({
                "service_request_id": f"gen_{uuid4().hex[:12]}",
                "user_id": user_id,
                "provider_used": provider,
                "generation_timestamp": self._get_timestamp(),
                "source_image": str(image_file),
            })
            
            logger.info(f"asset_generation_completed provider={provider} clips={len(response.clips)}")
            
            return response
            
        except Exception as error:
            logger.error(f"asset_generation_failed provider={provider} error={str(error)}")
            raise ValueError(f"Asset generation failed: {str(error)}")
    
    async def get_generation_status(self, *, generation_id: str, provider: str = "seedance") -> Dict[str, Any]:
        """Get status of ongoing generation."""
        try:
            if provider not in self.providers:
                raise ValueError(f"Provider '{provider}' not available")
            
            generation_provider = self.providers[provider]
            return await generation_provider.get_generation_status(generation_id=generation_id)
            
        except Exception as error:
            logger.error(f"generation_status_check_failed provider={provider} error={str(error)}")
            raise ValueError(f"Failed to check generation status: {str(error)}")
    
    async def cancel_generation(self, *, generation_id: str, provider: str = "seedance") -> bool:
        """Cancel ongoing generation."""
        try:
            if provider not in self.providers:
                raise ValueError(f"Provider '{provider}' not available")
            
            generation_provider = self.providers[provider]
            success = await generation_provider.cancel_generation(generation_id=generation_id)
            
            if success:
                logger.info(f"generation_cancelled provider={provider} generation_id={generation_id}")
            else:
                logger.warning(f"generation_cancel_failed provider={provider} generation_id={generation_id}")
            
            return success
            
        except Exception as error:
            logger.error(f"generation_cancel_failed provider={provider} error={str(error)}")
            return False
    
    def get_available_providers(self) -> list[str]:
        """Get list of available generation providers."""
        return list(self.providers.keys())
    
    def is_provider_available(self, provider: str) -> bool:
        """Check if a specific provider is available."""
        return provider in self.providers
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()
    
    async def validate_generation_request(self, request: GenerationRequest) -> Dict[str, Any]:
        """Validate generation request and return validation result."""
        errors = []
        warnings = []
        
        # Check provider availability
        if not self.is_provider_available(request.provider):
            errors.append(f"Provider '{request.provider}' is not available")
        
        # Validate text prompt if provided
        if request.text_prompt and len(request.text_prompt.strip()) < 10:
            warnings.append("Text prompt is very short, results may be poor")
        
        if request.text_prompt and len(request.text_prompt) > 1000:
            warnings.append("Text prompt is very long, may be truncated")
        
        # Validate image path if provided
        if request.image_path:
            image_file = Path(request.image_path)
            if not image_file.exists():
                errors.append(f"Image file not found: {request.image_path}")
            elif image_file.stat().st_size > 50 * 1024 * 1024:  # 50MB
                warnings.append("Image file is very large, processing may be slow")
        
        # Validate duration
        if request.duration and request.duration > 120:
            warnings.append("Duration over 2 minutes may take significant time")
        
        if request.duration and request.duration < 5:
            warnings.append("Duration under 5 seconds may be too short")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
        }
