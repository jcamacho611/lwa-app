from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from pydantic import BaseModel, Field

from ...core.config import get_settings
from ...dependencies.auth import get_optional_user, get_platform_store, require_user
from ...models.schemas import ClipBatchResponse, GenerationRequest
from ...services.asset_generation_service import AssetGenerationService

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


def route_generation_mode(payload: GenerationRequest) -> str:
    if payload.mode == "video":
        return "video"
    if payload.mode == "image":
        return "image"
    if payload.mode == "idea":
        return "idea"
    raise ValueError(f"Unsupported mode: {payload.mode}")


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


def generation_actor(request: Request) -> tuple[object | None, str]:
    user = get_optional_user(request)
    if user:
        return user, user.id
    client_id = (request.headers.get(settings.client_id_header_name) or "").strip()
    safe_id = "".join(ch if ch.isalnum() or ch in {"_", "-"} else "_" for ch in client_id)
    return None, f"guest_{safe_id[:64] or 'first_use'}"


def validate_multimodal_payload(payload: GenerationRequest, mode: str) -> None:
    if mode == "video":
        raise HTTPException(status_code=400, detail="Video mode uses the clipping route: /process or /generate.")

    if mode == "image":
        has_image_source = any(
            (
                (payload.image_url or "").strip(),
                (payload.reference_image_url or "").strip(),
                (payload.upload_file_id or "").strip(),
            )
        )
        if not has_image_source:
            raise HTTPException(
                status_code=400,
                detail="Image mode requires image_url, reference_image_url, or upload_file_id.",
            )

    if mode == "idea":
        prompt = (payload.prompt or payload.text_prompt or "").strip()
        if not prompt:
            raise HTTPException(status_code=400, detail="Idea mode requires prompt or text_prompt.")


def build_generation_batch(
    *,
    response,
    source_label: str,
    source_type: str,
    target_platform: str,
    actor_id: str,
) -> ClipBatchResponse:
    summary = {
        "plan_code": "first_use" if actor_id.startswith("guest_") else "pro",
        "plan_name": "First run" if actor_id.startswith("guest_") else "Pro",
        "credits_remaining": 1 if actor_id.startswith("guest_") else 999,
        "estimated_turnaround": "Generation provider runtime",
        "recommended_next_step": "Review the generated asset, then export the package that fits.",
        "ai_provider": response.provider,
        "target_platform": target_platform,
        "platform_decision": "manual" if target_platform else "auto",
        "recommended_platform": target_platform,
        "platform_recommendation_reason": "Chosen for short-form review.",
        "recommended_content_type": "Generated short-form asset",
        "recommended_output_style": response.generation_type,
        "manual_platform_override": bool(target_platform),
        "sources_considered": [source_label],
        "processing_mode": "multimodal_generation",
        "selection_strategy": "provider_generation",
        "source_title": "Generated asset",
        "source_type": source_type,
        "assets_created": len(response.clips),
        "edited_assets_created": 0,
        "rendered_clip_count": sum(1 for clip in response.clips if clip.is_rendered),
        "strategy_only_clip_count": sum(1 for clip in response.clips if clip.is_strategy_only),
        "free_preview_unlocked": actor_id.startswith("guest_"),
        "persistence_requires_signup": actor_id.startswith("guest_"),
        "upgrade_prompt": "Create an account to save this run and keep generating." if actor_id.startswith("guest_") else None,
        "feature_flags": {},
    }
    return ClipBatchResponse(
        request_id=response.request_id,
        video_url=source_label,
        status="success",
        source_type=source_type,
        source_title="Generated asset",
        source_platform="LWA Generation",
        preview_asset_url=response.clips[0].preview_url if response.clips else None,
        download_asset_url=response.clips[0].download_url if response.clips else None,
        thumbnail_url=response.clips[0].thumbnail_url if response.clips else None,
        processing_summary=summary,
        trend_context=[],
        clips=response.clips,
        scripts=None,
    )


def generation_error_status(error: Exception) -> int:
    message = str(error).lower()
    if "not available" in message or "missing" in message or "api key" in message:
        return 503
    return 500


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
        batch_response = build_generation_batch(
            response=response,
            source_label=payload.text_prompt,
            source_type="idea",
            target_platform="TikTok",
            actor_id=user.id,
        )
        
        # Persist generation result
        platform_store.persist_clip_batch(
            request_id=response.request_id,
            user_id=user.id,
            campaign_id=None,
            response=batch_response,
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
        
    except HTTPException:
        raise
    except Exception as error:
        logger.error(f"text_generation_failed user_id={user.id} error={str(error)}")
        raise HTTPException(status_code=generation_error_status(error), detail=f"Text generation failed: {str(error)}")


@router.post("/image-to-video")
async def generate_from_image(
    image_file: UploadFile = File(...),
    prompt: Optional[str] = Form(default=None),
    provider: str = Form(default="seedance"),
    duration: Optional[float] = Form(default=30.0),
    motion_strength: str = Form(default="medium"),
    aspect_ratio: str = Form(default="9:16"),
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
            batch_response = build_generation_batch(
                response=response,
                source_label=image_file.filename or "uploaded image",
                source_type="image_upload",
                target_platform="TikTok",
                actor_id=user.id,
            )
            
            # Persist generation result
            platform_store.persist_clip_batch(
                request_id=response.request_id,
                user_id=user.id,
                campaign_id=None,
                response=batch_response,
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
        
    except HTTPException:
        raise
    except Exception as error:
        logger.error(f"image_generation_failed user_id={user.id} error={str(error)}")
        raise HTTPException(status_code=generation_error_status(error), detail=f"Image generation failed: {str(error)}")


@router.post("/multimodal", response_model=ClipBatchResponse)
async def generate_multimodal(
    payload: GenerationRequest,
    request: Request,
) -> ClipBatchResponse:
    """First-use multimodal generation entrypoint for Image and Idea modes."""
    user, actor_id = generation_actor(request)
    mode = route_generation_mode(payload)
    target_platform = payload.target_platform or "TikTok"
    duration = float(payload.duration or payload.duration_seconds or 30.0)
    style = payload.style or payload.style_preset
    motion_strength = payload.motion_strength or payload.motion_profile or "medium"

    try:
        validate_multimodal_payload(payload, mode)

        if not generation_service.is_provider_available(payload.provider):
            raise HTTPException(status_code=503, detail=f"Generation provider '{payload.provider}' is not configured.")

        if mode == "idea":
            prompt = (payload.text_prompt or payload.prompt or "").strip()
            generation_request = GenerationRequest(
                mode="idea",
                text_prompt=prompt,
                provider=payload.provider,
                duration=duration,
                duration_seconds=payload.duration_seconds,
                style=style,
                style_preset=payload.style_preset,
                aspect_ratio=payload.aspect_ratio,
                user_id=actor_id,
            )
            validation = await generation_service.validate_generation_request(generation_request)
            if not validation["valid"]:
                raise HTTPException(status_code=400, detail={"errors": validation["errors"], "warnings": validation["warnings"]})

            response = await generation_service.generate_from_text(
                text_prompt=prompt,
                provider=payload.provider,
                duration=duration,
                style=style,
                aspect_ratio=payload.aspect_ratio,
                user_id=actor_id,
            )
            batch = build_generation_batch(
                response=response,
                source_label=prompt,
                source_type="idea",
                target_platform=target_platform,
                actor_id=actor_id,
            )

        elif mode == "image":
            if not payload.upload_file_id:
                raise HTTPException(status_code=422, detail="Upload an image before running provider-backed Image mode.")
            upload = platform_store.get_upload(payload.upload_file_id, user_id=user.id if user else None)
            if not upload:
                raise HTTPException(status_code=404, detail="Upload not found")

            content_type = str(upload.get("content_type") or "").lower()
            file_name = str(upload.get("file_name") or "")
            suffix = file_name.rsplit(".", 1)[-1].lower() if "." in file_name else ""
            if not content_type.startswith("image/") and suffix not in {"jpg", "jpeg", "png", "webp", "heic", "heif"}:
                raise HTTPException(status_code=400, detail="Image mode requires an uploaded image.")

            image_path = Path(str(upload["stored_path"]))
            prompt = (payload.prompt or payload.text_prompt or "Animate this image into a short-form post-ready video.").strip()
            generation_request = GenerationRequest(
                mode="image",
                image_path=str(image_path),
                prompt=prompt,
                provider=payload.provider,
                duration=duration,
                duration_seconds=payload.duration_seconds,
                motion_strength=motion_strength,
                motion_profile=payload.motion_profile,
                aspect_ratio=payload.aspect_ratio,
                user_id=actor_id,
            )
            validation = await generation_service.validate_generation_request(generation_request)
            if not validation["valid"]:
                raise HTTPException(status_code=400, detail={"errors": validation["errors"], "warnings": validation["warnings"]})

            response = await generation_service.generate_from_image(
                image_path=image_path,
                provider=payload.provider,
                prompt=prompt,
                duration=duration,
                motion_strength=motion_strength,
                user_id=actor_id,
            )
            batch = build_generation_batch(
                response=response,
                source_label=str(upload.get("public_url") or file_name or "uploaded image"),
                source_type="image_upload",
                target_platform=target_platform,
                actor_id=actor_id,
            )

        if user:
            batch = platform_store.persist_clip_batch(
                request_id=batch.request_id,
                user_id=user.id,
                campaign_id=None,
                response=batch,
                local_asset_paths={},
            )

        logger.info("multimodal_generation_completed mode=%s actor_id=%s request_id=%s", mode, actor_id, batch.request_id)
        return batch

    except HTTPException:
        raise
    except Exception as error:
        logger.error("multimodal_generation_failed mode=%s actor_id=%s error=%s", mode, actor_id, str(error))
        raise HTTPException(status_code=generation_error_status(error), detail=f"Multimodal generation failed: {str(error)}")


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
