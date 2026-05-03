"""
Live AI Video Provider Adapter v0

Adapter for integrating live AI video generation providers like Runway, Pika, and others.
Provides unified interface for AI video generation within the LWA Video OS.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import json
import aiohttp
import os

from app.services.video.base_renderer import BaseRenderer, RenderContext, RenderResult
from app.core.config import settings

logger = logging.getLogger(__name__)


class AIProvider(Enum):
    """Supported AI video providers."""
    
    RUNWAY = "runway"
    PIKA = "pika"
    STABLE_DIFFUSION_VIDEO = "stable_diffusion_video"
    KAIBER = "kaiber"
    LUMA = "luma"
    GEN2 = "gen2"


@dataclass
class AIProviderConfig:
    """Configuration for AI video provider."""
    
    provider: AIProvider
    api_key: str
    api_base_url: str
    model: str
    max_duration: int
    supported_formats: List[str]
    cost_per_second: float
    rate_limit_rpm: int
    quality_levels: List[str]


@dataclass
class AIGenerationRequest:
    """Request for AI video generation."""
    
    prompt: str
    negative_prompt: Optional[str]
    duration: float
    aspect_ratio: str
    quality: str
    style_preset: Optional[str]
    seed: Optional[int]
    num_variations: int
    enhance_prompt: bool


@dataclass
class AIGenerationResult:
    """Result from AI video generation."""
    
    video_url: str
    video_id: str
    duration: float
    resolution: str
    format: str
    cost_usd: float
    generation_time_seconds: float
    metadata: Dict[str, Any]


class LiveAIAdapter(BaseRenderer):
    """
    Adapter for live AI video generation providers.
    
    Integrates with multiple AI video generation services to provide
    AI-powered video creation capabilities within the LWA Video OS.
    """
    
    def __init__(self):
        super().__init__()
        self.name = "live_ai_adapter"
        self.display_name = "Live AI Video Adapter"
        self.version = "1.0.0"
        
        # Provider configurations
        self.providers = self._initialize_providers()
        
        # Session management
        self.session = None
        self.rate_limits = {}
        
        # Capabilities
        self.capabilities = {
            "formats": ["mp4", "webm"],
            "codecs": ["h264", "vp9"],
            "effects": ["ai_generation", "style_transfer", "motion"],
            "max_resolution": "1024x1024",
            "max_duration": 30,  # Most AI providers limit to 30 seconds
            "gpu_acceleration": True,
            "parallel_processing": True,
            "ai_generation": True,
        }
        
        # Style presets for different providers
        self.style_presets = {
            "cinematic": "cinematic, film quality, dramatic lighting",
            "anime": "anime style, manga, Japanese animation",
            "realistic": "photorealistic, hyperrealistic, detailed",
            "artistic": "artistic, painterly, impressionist",
            "futuristic": "futuristic, sci-fi, cyberpunk",
            "vintage": "vintage, retro, old film",
            "minimalist": "minimalist, clean, simple",
            "abstract": "abstract, surreal, conceptual",
        }
    
    def _initialize_providers(self) -> Dict[str, AIProviderConfig]:
        """Initialize AI provider configurations."""
        
        providers = {}
        
        # Runway ML
        if settings.RUNWAY_API_KEY:
            providers["runway"] = AIProviderConfig(
                provider=AIProvider.RUNWAY,
                api_key=settings.RUNWAY_API_KEY,
                api_base_url="https://api.runwayml.com/v1",
                model="gen2",
                max_duration=30,
                supported_formats=["mp4"],
                cost_per_second=0.05,
                rate_limit_rpm=60,
                quality_levels=["standard", "high"]
            )
        
        # Pika Labs
        if settings.PIKA_API_KEY:
            providers["pika"] = AIProviderConfig(
                provider=AIProvider.PIKA,
                api_key=settings.PIKA_API_KEY,
                api_base_url="https://api.pika.art/v1",
                model="pika-1.0",
                max_duration=30,
                supported_formats=["mp4", "webm"],
                cost_per_second=0.04,
                rate_limit_rpm=30,
                quality_levels=["standard", "pro"]
            )
        
        # Stable Diffusion Video
        if settings.SDV_API_KEY:
            providers["stable_diffusion_video"] = AIProviderConfig(
                provider=AIProvider.STABLE_DIFFUSION_VIDEO,
                api_key=settings.SDV_API_KEY,
                api_base_url="https://api.stability.ai/v1",
                model="stable-video-diffusion",
                max_duration=20,
                supported_formats=["mp4"],
                cost_per_second=0.03,
                rate_limit_rpm=20,
                quality_levels=["standard", "enhanced"]
            )
        
        return providers
    
    async def render(self, context: RenderContext) -> RenderResult:
        """
        Generate video using AI provider.
        
        Args:
            context: Render context with generation parameters
            
        Returns:
            RenderResult with generated video information
        """
        
        if not self.providers:
            return RenderResult(
                success=False,
                error_message="No AI providers configured"
            )
        
        try:
            # Extract generation parameters from context
            generation_request = self._extract_generation_request(context)
            
            # Select optimal provider
            provider_name = await self._select_provider(generation_request)
            provider = self.providers[provider_name]
            
            # Check rate limits
            if not await self._check_rate_limit(provider_name):
                return RenderResult(
                    success=False,
                    error_message=f"Rate limit exceeded for {provider_name}"
                )
            
            # Generate video
            result = await self._generate_video(provider, generation_request)
            
            # Download and process video
            output_path = await self._download_and_process_video(result)
            
            # Update rate limit
            self._update_rate_limit(provider_name)
            
            return RenderResult(
                success=True,
                output_path=output_path,
                metadata={
                    "provider": provider_name,
                    "model": provider.model,
                    "generation_time": result.generation_time_seconds,
                    "cost_usd": result.cost_usd,
                    "video_id": result.video_id,
                    "ai_generated": True
                },
                duration_seconds=result.duration,
                file_size=os.path.getsize(output_path) if os.path.exists(output_path) else 0
            )
            
        except Exception as e:
            logger.error(f"AI video generation failed: {e}")
            return RenderResult(
                success=False,
                error_message=str(e)
            )
    
    def _extract_generation_request(self, context: RenderContext) -> AIGenerationRequest:
        """Extract AI generation request from render context."""
        
        job = context.job
        render_settings = context.render_settings or {}
        
        # Extract prompt from job or settings
        prompt = render_settings.get("prompt", job.style_preset or "cinematic video")
        
        # Apply style preset
        style_preset = render_settings.get("style_preset", "cinematic")
        if style_preset in self.style_presets:
            prompt += f", {self.style_presets[style_preset]}"
        
        return AIGenerationRequest(
            prompt=prompt,
            negative_prompt=render_settings.get("negative_prompt"),
            duration=min(job.duration_seconds, 30),  # Cap at 30 seconds
            aspect_ratio=job.aspect_ratio or "9:16",
            quality=render_settings.get("quality", "standard"),
            style_preset=style_preset,
            seed=render_settings.get("seed"),
            num_variations=render_settings.get("num_variations", 1),
            enhance_prompt=render_settings.get("enhance_prompt", True)
        )
    
    async def _select_provider(self, request: AIGenerationRequest) -> str:
        """Select the best provider for the generation request."""
        
        available_providers = list(self.providers.keys())
        
        if not available_providers:
            raise ValueError("No providers available")
        
        # Simple selection logic - could be enhanced
        # Prioritize providers based on availability and rate limits
        for provider_name in available_providers:
            if await self._check_rate_limit(provider_name):
                return provider_name
        
        # If all providers are rate limited, return the first one
        return available_providers[0]
    
    async def _check_rate_limit(self, provider_name: str) -> bool:
        """Check if provider is within rate limits."""
        
        if provider_name not in self.rate_limits:
            return True
        
        last_request = self.rate_limits[provider_name]
        time_since_last = datetime.utcnow() - last_request
        
        provider = self.providers[provider_name]
        min_interval = 60 / provider.rate_limit_rpm  # Convert RPM to seconds
        
        return time_since_last.total_seconds() >= min_interval
    
    def _update_rate_limit(self, provider_name: str):
        """Update rate limit timestamp for provider."""
        
        self.rate_limits[provider_name] = datetime.utcnow()
    
    async def _generate_video(
        self, provider: AIProviderConfig, request: AIGenerationRequest
    ) -> AIGenerationResult:
        """Generate video using specific AI provider."""
        
        if provider.provider == AIProvider.RUNWAY:
            return await self._generate_with_runway(provider, request)
        elif provider.provider == AIProvider.PIKA:
            return await self._generate_with_pika(provider, request)
        elif provider.provider == AIProvider.STABLE_DIFFUSION_VIDEO:
            return await self._generate_with_sdv(provider, request)
        else:
            raise ValueError(f"Unsupported provider: {provider.provider}")
    
    async def _generate_with_runway(
        self, provider: AIProviderConfig, request: AIGenerationRequest
    ) -> AIGenerationResult:
        """Generate video using Runway ML."""
        
        headers = {
            "Authorization": f"Bearer {provider.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": provider.model,
            "prompt": self._enhance_prompt(request) if request.enhance_prompt else request.prompt,
            "negative_prompt": request.negative_prompt,
            "duration": int(request.duration),
            "aspect_ratio": request.aspect_ratio,
            "quality": request.quality,
            "seed": request.seed,
            "num_outputs": request.num_variations
        }
        
        # Remove None values
        payload = {k: v for k, v in payload.items() if v is not None}
        
        start_time = datetime.utcnow()
        
        async with aiohttp.ClientSession() as session:
            # Submit generation request
            async with session.post(
                f"{provider.api_base_url}/generations",
                headers=headers,
                json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise RuntimeError(f"Runway API error: {error_text}")
                
                generation_data = await response.json()
                generation_id = generation_data["id"]
            
            # Poll for completion
            while True:
                async with session.get(
                    f"{provider.api_base_url}/generations/{generation_id}",
                    headers=headers
                ) as response:
                    if response.status != 200:
                        raise RuntimeError(f"Failed to check generation status")
                    
                    status_data = await response.json()
                    status = status_data["status"]
                    
                    if status == "completed":
                        break
                    elif status == "failed":
                        raise RuntimeError(f"Generation failed: {status_data.get('error')}")
                    
                    await asyncio.sleep(2)  # Poll every 2 seconds
            
            # Get result
            result_data = status_data
            generation_time = (datetime.utcnow() - start_time).total_seconds()
            
            return AIGenerationResult(
                video_url=result_data["output"][0]["url"],
                video_id=generation_id,
                duration=request.duration,
                resolution="1024x1024",  # Runway default
                format="mp4",
                cost_usd=request.duration * provider.cost_per_second,
                generation_time_seconds=generation_time,
                metadata={
                    "provider": "runway",
                    "model": provider.model,
                    "prompt": request.prompt,
                    "quality": request.quality
                }
            )
    
    async def _generate_with_pika(
        self, provider: AIProviderConfig, request: AIGenerationRequest
    ) -> AIGenerationResult:
        """Generate video using Pika Labs."""
        
        headers = {
            "Authorization": f"Bearer {provider.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "prompt": self._enhance_prompt(request) if request.enhance_prompt else request.prompt,
            "negative_prompt": request.negative_prompt,
            "duration": int(request.duration),
            "aspect_ratio": request.aspect_ratio,
            "quality": request.quality,
            "seed": request.seed,
            "num_outputs": request.num_variations
        }
        
        # Remove None values
        payload = {k: v for k, v in payload.items() if v is not None}
        
        start_time = datetime.utcnow()
        
        async with aiohttp.ClientSession() as session:
            # Submit generation request
            async with session.post(
                f"{provider.api_base_url}/generate",
                headers=headers,
                json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise RuntimeError(f"Pika API error: {error_text}")
                
                generation_data = await response.json()
                generation_id = generation_data["id"]
            
            # Poll for completion
            while True:
                async with session.get(
                    f"{provider.api_base_url}/generate/{generation_id}",
                    headers=headers
                ) as response:
                    if response.status != 200:
                        raise RuntimeError(f"Failed to check generation status")
                    
                    status_data = await response.json()
                    status = status_data["status"]
                    
                    if status == "completed":
                        break
                    elif status == "failed":
                        raise RuntimeError(f"Generation failed: {status_data.get('error')}")
                    
                    await asyncio.sleep(2)  # Poll every 2 seconds
            
            # Get result
            result_data = status_data
            generation_time = (datetime.utcnow() - start_time).total_seconds()
            
            return AIGenerationResult(
                video_url=result_data["output_url"],
                video_id=generation_id,
                duration=request.duration,
                resolution="1024x576",  # Pika default
                format="mp4",
                cost_usd=request.duration * provider.cost_per_second,
                generation_time_seconds=generation_time,
                metadata={
                    "provider": "pika",
                    "model": provider.model,
                    "prompt": request.prompt,
                    "quality": request.quality
                }
            )
    
    async def _generate_with_sdv(
        self, provider: AIProviderConfig, request: AIGenerationRequest
    ) -> AIGenerationResult:
        """Generate video using Stable Diffusion Video."""
        
        headers = {
            "Authorization": f"Bearer {provider.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": provider.model,
            "prompt": self._enhance_prompt(request) if request.enhance_prompt else request.prompt,
            "negative_prompt": request.negative_prompt,
            "duration": int(request.duration),
            "aspect_ratio": request.aspect_ratio,
            "seed": request.seed,
            "samples": request.num_variations
        }
        
        # Remove None values
        payload = {k: v for k, v in payload.items() if v is not None}
        
        start_time = datetime.utcnow()
        
        async with aiohttp.ClientSession() as session:
            # Submit generation request
            async with session.post(
                f"{provider.api_base_url}/text-to-video",
                headers=headers,
                json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise RuntimeError(f"Stable Diffusion Video API error: {error_text}")
                
                generation_data = await response.json()
                generation_id = generation_data["id"]
            
            # Poll for completion
            while True:
                async with session.get(
                    f"{provider.api_base_url}/text-to-video/{generation_id}",
                    headers=headers
                ) as response:
                    if response.status != 200:
                        raise RuntimeError(f"Failed to check generation status")
                    
                    status_data = await response.json()
                    status = status_data["status"]
                    
                    if status == "completed":
                        break
                    elif status == "failed":
                        raise RuntimeError(f"Generation failed: {status_data.get('error')}")
                    
                    await asyncio.sleep(3)  # Poll every 3 seconds
            
            # Get result
            result_data = status_data
            generation_time = (datetime.utcnow() - start_time).total_seconds()
            
            return AIGenerationResult(
                video_url=result_data["output"][0]["url"],
                video_id=generation_id,
                duration=request.duration,
                resolution="512x512",  # SDV default
                format="mp4",
                cost_usd=request.duration * provider.cost_per_second,
                generation_time_seconds=generation_time,
                metadata={
                    "provider": "stable_diffusion_video",
                    "model": provider.model,
                    "prompt": request.prompt,
                    "quality": request.quality
                }
            )
    
    def _enhance_prompt(self, request: AIGenerationRequest) -> str:
        """Enhance prompt for better AI generation results."""
        
        enhanced_prompt = request.prompt
        
        # Add quality modifiers
        if request.quality == "high" or request.quality == "pro":
            enhanced_prompt += ", high quality, detailed, 4K, professional"
        
        # Add motion descriptors
        enhanced_prompt += ", smooth motion, cinematic movement, fluid animation"
        
        # Add aspect ratio specific guidance
        if request.aspect_ratio == "9:16":
            enhanced_prompt += ", vertical video, mobile optimized"
        elif request.aspect_ratio == "16:9":
            enhanced_prompt += ", horizontal video, widescreen"
        
        return enhanced_prompt
    
    async def _download_and_process_video(self, result: AIGenerationResult) -> str:
        """Download and process AI-generated video."""
        
        # Create output filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"ai_generated_{result.video_id}_{timestamp}.mp4"
        output_path = os.path.join(settings.UPLOAD_DIR, "ai_videos", output_filename)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Download video
        async with aiohttp.ClientSession() as session:
            async with session.get(result.video_url) as response:
                if response.status != 200:
                    raise RuntimeError(f"Failed to download video: {response.status}")
                
                with open(output_path, "wb") as f:
                    async for chunk in response.content.iter_chunked(8192):
                        f.write(chunk)
        
        return output_path
    
    async def get_capabilities(self) -> Dict[str, Any]:
        """Get AI adapter capabilities."""
        
        available_providers = list(self.providers.keys())
        
        return {
            "name": self.name,
            "display_name": self.display_name,
            "version": self.version,
            "available": len(available_providers) > 0,
            "capabilities": self.capabilities,
            "available_providers": available_providers,
            "supported_formats": ["mp4", "webm"],
            "max_resolution": "1024x1024",
            "max_duration": 30,
            "ai_generation": True,
            "style_presets": list(self.style_presets.keys()),
            "cost_per_second": {
                name: provider.cost_per_second 
                for name, provider in self.providers.items()
            }
        }
    
    async def test_render(self, test_config: Optional[Dict[str, Any]] = None) -> bool:
        """Test AI adapter with a simple generation."""
        
        if not self.providers:
            return False
        
        try:
            # Create test request
            test_request = AIGenerationRequest(
                prompt="A simple test video with abstract shapes",
                duration=5.0,
                aspect_ratio="1:1",
                quality="standard",
                style_preset="abstract",
                seed=12345,
                num_variations=1,
                enhance_prompt=False
            )
            
            # Select provider and test
            provider_name = await self._select_provider(test_request)
            provider = self.providers[provider_name]
            
            # Test API connectivity (don't actually generate)
            headers = {
                "Authorization": f"Bearer {provider.api_key}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{provider.api_base_url}/models",
                    headers=headers
                ) as response:
                    return response.status == 200
                    
        except Exception as e:
            logger.error(f"AI adapter test failed: {e}")
            return False
    
    async def get_provider_status(self) -> Dict[str, Any]:
        """Get status of all configured providers."""
        
        status = {}
        
        for name, provider in self.providers.items():
            try:
                headers = {
                    "Authorization": f"Bearer {provider.api_key}",
                    "Content-Type": "application/json"
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"{provider.api_base_url}/models",
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as response:
                        status[name] = {
                            "available": response.status == 200,
                            "last_check": datetime.utcnow().isoformat(),
                            "rate_limited": not await self._check_rate_limit(name)
                        }
                        
            except Exception as e:
                status[name] = {
                    "available": False,
                    "error": str(e),
                    "last_check": datetime.utcnow().isoformat()
                }
        
        return status


# Singleton instance
live_ai_adapter = LiveAIAdapter()
