from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, Request, UploadFile
from pydantic import BaseModel, Field

from ...core.config import get_settings
from ...dependencies.auth import get_platform_store, require_user
from ...models.schemas import GenerationRequest
from ...services.asset_generation_service import AssetGenerationService
from ...dependencies.auth import get_platform_store

router = APIRouter(prefix="/v1/generation", tags=["generation"])
platform_store = get_platform_store()
settings = get_settings()
generation_service = AssetGenerationService(settings)
logger = logging.getLogger("uvicorn.error")


class TextGenerationRequest(BaseModel):
    text_prompt: str = Field(..., min_length=10, max_length=1000, description="Text prompt for video generation")
    provider: str = Field(default="seedance", description="Generation provider")
    duration: Optional[float] = Field(default=30.0, ge=5.0, le=120.0, description="Video duration in seconds")
    style: Optional[str] = Field(default=None, description="Generation style")
    aspect_ratio: str = Field(default="9:16", description="Video aspect ratio")


class ImageGenerationRequest(BaseModel):
    prompt: Optional[str] = Field(default=None, min_length=10, max_length=1000, description="Optional prompt for image-to-video")
    provider: str = Field(default="seedance", description="Generation provider")
    duration: Optional[float] = Field(default=30.0, ge=5.0, le=120.0, description="Video duration in seconds")
    motion_strength: str = Field(default="medium", description="Motion strength")
    aspect_ratio: str = Field(default="9:16", description="Video aspect ratio")


class GenerationStatusRequest(BaseModel):
    generation_id: str = Field(..., description="Generation ID to check status")
    provider: str = Field(default="seedance", description="Generation provider")


def require_generation_enabled(request: Request):
    """Check if generation features are enabled for user."""
    user = require_user(request)
    
    # Check if user has generation access
    plan = (user.plan or "free").lower()
    if plan not in ["pro", "scale"]:
        raise HTTPException(
            status_code=403,
            detail="Generation features require Pro plan or higher"
        )
    
    return user


@router.post("/text-to-video")
async def generate_from_text(
    payload: TextGenerationRequest,
    request: Request,
) -> Dict[str, Any]:
    """Generate video from text prompt."""
    user = require_generation_enabled(request)
    
    try:
        # Create generation request
        generation_request = GenerationRequest(
            text_prompt=payload.text_prompt,
            provider=payload.provider,
            duration=payload.duration,
            style=payload.style,
            aspect_ratio=payload.aspect_ratio,
            user_id=user.id,
        )
        
        # Validate request
        validation = await generation_service.validate_generation_request(generation_request)
        if not validation["valid"]:
            raise HTTPException(
                status_code=400,
                detail={"errors": validation["errors"], "warnings": validation["warnings"]}
            )
        
        # Generate video
        response = await generation_service.generate_from_text(
            text_prompt=payload.text_prompt,
            provider=payload.provider,
            duration=payload.duration,
            style=payload.style,
            aspect_ratio=payload.aspect_ratio,
            user_id=user.id,
        )
        
        # Persist generation result
        platform_store.persist_clip_batch(
            request_id=response.request_id,
            user_id=user.id,
            campaign_id=None,
            response=response,
            local_asset_paths={},
        )
        
        logger.info(f"text_generation_completed user_id={user.id} request_id={response.request_id}")
        
        return {
            "success": True,
            "request_id": response.request_id,
            "clips": [clip.model_dump() for clip in response.clips],
            "provider": response.provider,
            "generation_type": response.generation_type,
            "total_clips": response.total_clips,
            "warnings": validation.get("warnings", []),
        }
        
    except Exception as error:
        logger.error(f"text_generation_failed user_id={user.id} error={str(error)}")
        raise HTTPException(status_code=500, detail=f"Text generation failed: {str(error)}")


@router.post("/image-to-video")
async def generate_from_image(
    image_file: UploadFile,
    prompt: Optional[str] = None,
    provider: str = "seedance",
    duration: Optional[float] = 30.0,
    motion_strength: str = "medium",
    aspect_ratio: str = "9:16",
    request: Request = None,
) -> Dict[str, Any]:
    """Generate video from image."""
    user = require_generation_enabled(request)
    
    try:
        # Validate uploaded file
        if not image_file.content_type or not image_file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Save uploaded image temporarily
        import tempfile
        import uuid
        
        temp_dir = Path(tempfile.gettempdir())
        file_extension = Path(image_file.filename).suffix or ".jpg"
        temp_image_path = temp_dir / f"gen_{uuid.uuid4().hex[:12]}{file_extension}"
        
        try:
            with open(temp_image_path, "wb") as f:
                content = await image_file.read()
                f.write(content)
            
            # Create generation request
            generation_request = GenerationRequest(
                image_path=str(temp_image_path),
                prompt=prompt,
                provider=provider,
                duration=duration,
                motion_strength=motion_strength,
                aspect_ratio=aspect_ratio,
                user_id=user.id,
            )
            
            # Validate request
            validation = await generation_service.validate_generation_request(generation_request)
            if not validation["valid"]:
                raise HTTPException(
                    status_code=400,
                    detail={"errors": validation["errors"], "warnings": validation["warnings"]}
                )
            
            # Generate video
            response = await generation_service.generate_from_image(
                image_path=temp_image_path,
                provider=provider,
                prompt=prompt,
                duration=duration,
                motion_strength=motion_strength,
                user_id=user.id,
            )
            
            # Persist generation result
            platform_store.persist_clip_batch(
                request_id=response.request_id,
                user_id=user.id,
                campaign_id=None,
                response=response,
                local_asset_paths={},
            )
            
            logger.info(f"image_generation_completed user_id={user.id} request_id={response.request_id}")
            
            return {
                "success": True,
                "request_id": response.request_id,
                "clips": [clip.model_dump() for clip in response.clips],
                "provider": response.provider,
                "generation_type": response.generation_type,
                "total_clips": response.total_clips,
                "warnings": validation.get("warnings", []),
            }
            
        finally:
            # Clean up temporary file
            if temp_image_path.exists():
                temp_image_path.unlink()
        
    except Exception as error:
        logger.error(f"image_generation_failed user_id={user.id} error={str(error)}")
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(error)}")


@router.get("/status/{generation_id}")
async def get_generation_status(
    generation_id: str,
    provider: str = "seedance",
    request: Request = None,
) -> Dict[str, Any]:
    """Get status of ongoing generation."""
    user = require_generation_enabled(request)
    
    try:
        status = await generation_service.get_generation_status(
            generation_id=generation_id,
            provider=provider
        )
        
        return {
            "success": True,
            "generation_id": generation_id,
            "provider": provider,
            "status": status,
        }
        
    except Exception as error:
        logger.error(f"generation_status_check_failed user_id={user.id} error={str(error)}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(error)}")


@router.post("/cancel/{generation_id}")
async def cancel_generation(
    generation_id: str,
    provider: str = "seedance",
    request: Request = None,
) -> Dict[str, Any]:
    """Cancel ongoing generation."""
    user = require_generation_enabled(request)
    
    try:
        success = await generation_service.cancel_generation(
            generation_id=generation_id,
            provider=provider
        )
        
        return {
            "success": success,
            "generation_id": generation_id,
            "provider": provider,
            "cancelled": success,
        }
        
    except Exception as error:
        logger.error(f"generation_cancel_failed user_id={user.id} error={str(error)}")
        raise HTTPException(status_code=500, detail=f"Cancel failed: {str(error)}")


@router.get("/providers")
async def get_available_providers(request: Request = None) -> Dict[str, Any]:
    """Get list of available generation providers."""
    user = require_generation_enabled(request)
    
    providers = generation_service.get_available_providers()
    
    return {
        "success": True,
        "providers": providers,
        "total_providers": len(providers),
    }
