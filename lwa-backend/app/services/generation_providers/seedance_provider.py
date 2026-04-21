from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union
from uuid import uuid4

from .base_provider import BaseGenerationProvider
from ...core.config import Settings
from ...models.schemas import ClipResult, GenerationRequest, GenerationResponse

logger = logging.getLogger("uvicorn.error")


class SeedanceProvider(BaseGenerationProvider):
    """Seedance provider for text-to-video and image-to-video generation."""
    
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.api_key = settings.seedance_api_key
        self.base_url = settings.seedance_base_url.rstrip("/")
    
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
                "model": self.settings.seedance_model,
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
                "model": self.settings.seedance_model,
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
            video_url = response.get("output_url") or response.get("video_url") or response.get("asset_url")
            video_id = response.get("id", f"seedance_{uuid4().hex[:12]}")
            duration = float(response.get("duration") or response.get("duration_seconds") or 30.0)
            prompt = str(response.get("prompt") or response.get("title") or "Generated asset").strip()
            title = str(response.get("title") or prompt or "Generated Video").strip()
            caption = str(response.get("description") or response.get("caption") or prompt).strip()
            
            # Create LWA-style clip result
            clip = ClipResult(
                id=video_id,
                request_id=video_id,
                title=title,
                hook=prompt[:140] or title,
                caption=caption,
                start_time="0:00",
                end_time=f"0:{int(duration):02d}" if duration < 60 else f"{int(duration // 60)}:{int(duration % 60):02d}",
                duration=int(duration),
                preview_url=video_url,
                clip_url=video_url,
                raw_clip_url=video_url,
                thumbnail_url=response.get("thumbnail_url"),
                preview_image_url=response.get("thumbnail_url"),
                render_status="ready" if video_url else "pending",
                is_rendered=bool(video_url),
                is_strategy_only=not bool(video_url),
                score=86 if video_url else 72,
                confidence_score=86 if video_url else 72,
                confidence_label="Strong early signal" if video_url else "Worth testing",
                confidence=1.0,
                reason="Generated from your source direction with motion-ready packaging.",
                why_this_matters="This gives you a generated asset path when no long-form source is needed.",
                category="Generated",
                format="9:16 generated",
                platform_fit="TikTok, Reels, Shorts",
                packaging_angle=response.get("style") or response.get("model") or "Generated concept",
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
