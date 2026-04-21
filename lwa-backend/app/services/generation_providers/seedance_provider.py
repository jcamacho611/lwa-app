from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union
from uuid import uuid4

from ..generation_providers.base_provider import BaseGenerationProvider
from ...core.config import Settings
from ...models.schemas import ClipResult, GenerationRequest, GenerationResponse

logger = logging.getLogger("uvicorn.error")


class SeedanceProvider(BaseGenerationProvider):
    """Seedance provider for text-to-video and image-to-video generation."""
    
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.api_key = settings.seedance_api_key
        self.base_url = settings.seedance_base_url or "https://api.seedance.ai/v1"
    
    async def generate_from_text(
        self,
        *,
        text_prompt: str,
        duration: Optional[float] = 30.0,
        style: Optional[str] = None,
        aspect_ratio: str = "9:16",
        **kwargs: Any,
    ) -> GenerationResponse:
        """Generate video from text prompt using Seedance."""
        try:
            # Prepare Seedance API request
            payload = {
                "prompt": text_prompt,
                "duration": duration,
                "aspect_ratio": aspect_ratio,
                "model": "seedance-v2",
                "quality": "high",
                "output_format": "mp4",
            }
            
            if style:
                payload["style"] = style
            
            # Call Seedance API
            response = await self._make_api_request(
                endpoint="/generate/text-to-video",
                payload=payload
            )
            
            # Normalize to LWA-style output
            return self._normalize_response(response, generation_type="text_to_video")
            
        except Exception as error:
            logger.error(f"seedance_text_generation_failed prompt={text_prompt[:50]}... error={str(error)}")
            raise ValueError(f"Seedance text generation failed: {str(error)}")
    
    async def generate_from_image(
        self,
        *,
        image_path: Union[str, Path],
        prompt: Optional[str] = None,
        duration: Optional[float] = 30.0,
        motion_strength: str = "medium",
        **kwargs: Any,
    ) -> GenerationResponse:
        """Generate video from image using Seedance."""
        try:
            # Prepare Seedance API request
            payload = {
                "image_path": str(image_path),
                "duration": duration,
                "motion_strength": motion_strength,
                "model": "seedance-v2",
                "quality": "high",
                "output_format": "mp4",
            }
            
            if prompt:
                payload["prompt"] = prompt
            
            # Call Seedance API
            response = await self._make_api_request(
                endpoint="/generate/image-to-video",
                payload=payload
            )
            
            # Normalize to LWA-style output
            return self._normalize_response(response, generation_type="image_to_video")
            
        except Exception as error:
            logger.error(f"seedance_image_generation_failed image={image_path} error={str(error)}")
            raise ValueError(f"Seedance image generation failed: {str(error)}")
    
    async def _make_api_request(self, *, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Make API request to Seedance."""
        import httpx
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        url = f"{self.base_url}{endpoint}"
        
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
    
    def _normalize_response(self, response: Dict[str, Any], *, generation_type: str) -> GenerationResponse:
        """Normalize Seedance response to LWA-style output."""
        try:
            # Extract video URL and metadata
            video_url = response.get("output_url")
            video_id = response.get("id", f"seedance_{uuid4().hex[:12]}")
            
            # Create LWA-style clip result
            clip = ClipResult(
                id=video_id,
                request_id=video_id,
                title=response.get("title", "Generated Video"),
                hook=response.get("prompt", "")[:100],  # First 100 chars as hook
                caption=response.get("description", ""),
                start_time=0.0,
                end_time=float(response.get("duration", 30.0)),
                preview_url=video_url,
                clip_url=video_url,
                raw_clip_url=video_url,
                thumbnail_url=response.get("thumbnail_url"),
                render_status="ready",
                status="ready",
                score=1.0,
                confidence=1.0,
                generation_type=generation_type,
                generation_provider="seedance",
                metadata={
                    "seedance_response": response,
                    "original_prompt": response.get("prompt"),
                    "model": response.get("model"),
                    "quality": response.get("quality"),
                },
            )
            
            return GenerationResponse(
                clips=[clip],
                request_id=video_id,
                generation_type=generation_type,
                provider="seedance",
                total_clips=1,
                processing_summary={
                    "total_candidates": 1,
                    "processing_time": response.get("processing_time", 0),
                    "feature_flags": {},
                    "target_platform": "TikTok",
                    "recommended_platform": "TikTok",
                    "credits_remaining": 999,
                },
                metadata=response,
            )
            
        except Exception as error:
            logger.error(f"seedance_response_normalization_failed error={str(error)}")
            raise ValueError(f"Failed to normalize Seedance response: {str(error)}")
    
    async def get_generation_status(self, *, generation_id: str) -> Dict[str, Any]:
        """Get status of ongoing generation."""
        try:
            import httpx
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            
            url = f"{self.base_url}/status/{generation_id}"
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                return response.json()
                
        except Exception as error:
            logger.error(f"seedance_status_check_failed generation_id={generation_id} error={str(error)}")
            raise ValueError(f"Failed to check generation status: {str(error)}")
    
    async def cancel_generation(self, *, generation_id: str) -> bool:
        """Cancel ongoing generation."""
        try:
            import httpx
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            
            url = f"{self.base_url}/cancel/{generation_id}"
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, headers=headers)
                return response.status_code == 200
                
        except Exception as error:
            logger.error(f"seedance_cancel_failed generation_id={generation_id} error={str(error)}")
            return False
