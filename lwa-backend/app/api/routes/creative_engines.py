"""
Creative Engines API Routes
Handles all creative AI engines: hooks, captions, thumbnails, campaign packaging.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from enum import Enum

router = APIRouter(prefix="/api/v1/creative-engines", tags=["creative_engines"])

# Enums
class EngineStatus(str, Enum):
    ACTIVE = "active"
    BETA = "beta"
    DEVELOPMENT = "development"
    MAINTENANCE = "maintenance"

class EngineType(str, Enum):
    CLIPPING = "clipping"
    HOOK = "hook"
    CAPTION = "caption"
    THUMBNAIL = "thumbnail"
    CAMPAIGN = "campaign"
    ANALYSIS = "analysis"

# Pydantic models
class CreativeEngine(BaseModel):
    id: str
    name: str
    description: str
    engine_type: EngineType
    status: EngineStatus
    version: str
    capabilities: List[str]
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    processing_time_avg: float
    success_rate: float
    metadata: Optional[Dict[str, Any]]

class EngineJob(BaseModel):
    id: str
    engine_id: str
    status: str
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]]
    created_at: str
    started_at: Optional[str]
    completed_at: Optional[str]
    error_message: Optional[str]
    processing_time: Optional[float]

class HookGenerationRequest(BaseModel):
    video_id: str
    num_hooks: int = 3
    style: str = "engaging"
    platform: str = "general"
    tone: str = "energetic"

class HookGenerationResponse(BaseModel):
    success: bool
    video_id: str
    hooks: List[Dict[str, Any]]
    generation_time: float
    generated_at: str

class CaptionGenerationRequest(BaseModel):
    video_id: str
    style: str = "standard"
    language: str = "en"
    max_duration: Optional[float] = None
    include_timestamps: bool = True

class ThumbnailTextRequest(BaseModel):
    video_id: str
    style: str = "bold"
    max_chars: int = 50
    num_variants: int = 3

class CampaignPackageRequest(BaseModel):
    video_id: str
    campaign_name: str
    platforms: List[str]
    include_hooks: bool = True
    include_captions: bool = True
    include_thumbnails: bool = True
    packaging_angle: Optional[str] = None

# Mock creative engines
MOCK_ENGINES = {
    "engine_clip_core": CreativeEngine(
        id="engine_clip_core",
        name="Clip Core Engine",
        description="Primary AI engine for video analysis and moment detection",
        engine_type=EngineType.CLIPPING,
        status=EngineStatus.ACTIVE,
        version="2.4.1",
        capabilities=["video_analysis", "moment_detection", "ranking", "trimming"],
        input_schema={"video_url": "string", "duration_limit": "number", "platform": "string"},
        output_schema={"clips": "array", "confidence_scores": "array", "timestamps": "array"},
        processing_time_avg=45.5,
        success_rate=0.94,
        metadata={"model": "lwa-clip-v2", "gpu_required": True}
    ),
    "engine_hook_writer": CreativeEngine(
        id="engine_hook_writer",
        name="Hook Writer Pro",
        description="Generates compelling opening lines and video hooks",
        engine_type=EngineType.HOOK,
        status=EngineStatus.ACTIVE,
        version="1.8.2",
        capabilities=["hook_generation", "tone_adaptation", "platform_optimization", "a_b_variants"],
        input_schema={"video_context": "string", "num_hooks": "number", "style": "string"},
        output_schema={"hooks": "array", "scores": "array", "recommended": "string"},
        processing_time_avg=3.2,
        success_rate=0.89,
        metadata={"model": "lwa-text-v1", "gpt_enhanced": True}
    ),
    "engine_caption_pro": CreativeEngine(
        id="engine_caption_pro",
        name="Caption Pro",
        description="Advanced caption generation with timing and style optimization",
        engine_type=EngineType.CAPTION,
        status=EngineStatus.BETA,
        version="1.3.0",
        capabilities=["transcription", "timing", "style_variants", "burn_in_ready"],
        input_schema={"video_url": "string", "language": "string", "style": "string"},
        output_schema={"captions": "array", "srt_content": "string", "burn_in_settings": "object"},
        processing_time_avg=12.8,
        success_rate=0.92,
        metadata={"model": "lwa-caption-v1", "whisper_based": True}
    ),
    "engine_thumbnail_text": CreativeEngine(
        id="engine_thumbnail_text",
        name="Thumbnail Text Master",
        description="Generates scroll-stopping thumbnail text overlays",
        engine_type=EngineType.THUMBNAIL,
        status=EngineStatus.BETA,
        version="1.2.1",
        capabilities=["text_generation", "font_pairing", "color_suggestions", "layout_hints"],
        input_schema={"video_frame": "string", "hook_text": "string", "style": "string"},
        output_schema={"text_variants": "array", "font_recommendations": "array", "layout": "object"},
        processing_time_avg=2.1,
        success_rate=0.87,
        metadata={"model": "lwa-visual-v1", "image_aware": True}
    ),
    "engine_campaign_packager": CreativeEngine(
        id="engine_campaign_packager",
        name="Campaign Packager",
        description="Bundles clips, hooks, captions into complete campaign exports",
        engine_type=EngineType.CAMPAIGN,
        status=EngineStatus.ACTIVE,
        version="2.1.0",
        capabilities=["bundle_creation", "format_conversion", "metadata_tagging", "delivery_optimization"],
        input_schema={"clip_ids": "array", "campaign_settings": "object"},
        output_schema={"package_url": "string", "formats": "array", "metadata": "object"},
        processing_time_avg=28.5,
        success_rate=0.96,
        metadata={"model": "lwa-package-v2", "parallel_processing": True}
    ),
    "engine_content_analyzer": CreativeEngine(
        id="engine_content_analyzer",
        name="Content Analyzer",
        description="Deep analysis of content performance and optimization suggestions",
        engine_type=EngineType.ANALYSIS,
        status=EngineStatus.DEVELOPMENT,
        version="0.9.0",
        capabilities=["performance_prediction", "trend_analysis", "optimization_suggestions", "competitor_insights"],
        input_schema={"video_url": "string", "platform": "string", "historical_data": "object"},
        output_schema={"score": "number", "suggestions": "array", "predictions": "object"},
        processing_time_avg=8.5,
        success_rate=0.78,
        metadata={"model": "lwa-analyze-v1", "experimental": True}
    )
}

MOCK_JOBS = {}

@router.get("/engines", response_model=Dict[str, Any])
async def list_engines(
    status: Optional[EngineStatus] = None,
    engine_type: Optional[EngineType] = None
):
    """List all creative engines."""
    engines = list(MOCK_ENGINES.values())
    
    if status:
        engines = [e for e in engines if e.status == status]
    
    if engine_type:
        engines = [e for e in engines if e.engine_type == engine_type]
    
    return {
        "success": True,
        "engines": [e.dict() for e in engines],
        "total_count": len(engines),
        "active_count": len([e for e in engines if e.status == EngineStatus.ACTIVE]),
        "beta_count": len([e for e in engines if e.status == EngineStatus.BETA])
    }

@router.get("/engines/{engine_id}", response_model=Dict[str, Any])
async def get_engine_details(engine_id: str):
    """Get detailed information about a specific engine."""
    if engine_id not in MOCK_ENGINES:
        raise HTTPException(status_code=404, detail="Engine not found")
    
    engine = MOCK_ENGINES[engine_id]
    
    return {
        "success": True,
        "engine": engine.dict(),
        "health": {
            "status": engine.status,
            "success_rate": engine.success_rate,
            "avg_processing_time": engine.processing_time_avg,
            "healthy": engine.success_rate > 0.8 and engine.status in [EngineStatus.ACTIVE, EngineStatus.BETA]
        }
    }

@router.post("/hooks/generate", response_model=HookGenerationResponse)
async def generate_hooks(request: HookGenerationRequest):
    """Generate video hooks/opening lines."""
    # Mock hook generation
    hooks = [
        {
            "id": f"hook_{i+1}",
            "text": f"You won't believe what happens at the {['beginning', 'middle', 'end'][i]} of this video...",
            "style": request.style,
            "tone": request.tone,
            "score": 0.95 - (i * 0.05),
            "character_count": 65,
            "estimated_ctr": 0.08 + (i * 0.01)
        }
        for i in range(request.num_hooks)
    ]
    
    return HookGenerationResponse(
        success=True,
        video_id=request.video_id,
        hooks=hooks,
        generation_time=2.3,
        generated_at=datetime.utcnow().isoformat()
    )

@router.post("/captions/generate", response_model=Dict[str, Any])
async def generate_captions(request: CaptionGenerationRequest):
    """Generate video captions with timing."""
    # Mock caption generation
    captions = [
        {
            "id": f"caption_{i}",
            "start_time": i * 3.5,
            "end_time": (i + 1) * 3.5,
            "text": f"This is caption segment {i+1} with key information",
            "style": request.style,
            "confidence": 0.92,
            "words": 6
        }
        for i in range(8)
    ]
    
    return {
        "success": True,
        "video_id": request.video_id,
        "language": request.language,
        "style": request.style,
        "captions": captions,
        "total_segments": len(captions),
        "total_duration": captions[-1]["end_time"] if captions else 0,
        "srt_content": "\n\n".join([
            f"{i+1}\\n{format_time(c['start_time'])} --> {format_time(c['end_time'])}\\n{c['text']}"
            for i, c in enumerate(captions)
        ]),
        "generation_time": 8.5,
        "generated_at": datetime.utcnow().isoformat()
    }

@router.post("/thumbnails/text", response_model=Dict[str, Any])
async def generate_thumbnail_text(request: ThumbnailTextRequest):
    """Generate thumbnail text variants."""
    # Mock thumbnail text generation
    variants = [
        {
            "id": f"thumb_text_{i+1}",
            "text": f"The TRUTH about {['content creation', 'viral clips', 'AI editing'][i]}",
            "style": request.style,
            "font": ["Impact", "Montserrat Bold", "Bebas Neue"][i],
            "color": ["#FFFFFF", "#FFD700", "#FF4444"][i],
            "outline": True,
            "shadow": i < 2,
            "score": 0.91 - (i * 0.03),
            "character_count": 35
        }
        for i in range(request.num_variants)
    ]
    
    return {
        "success": True,
        "video_id": request.video_id,
        "variants": variants,
        "recommended_variant": variants[0]["id"],
        "generation_time": 1.8,
        "generated_at": datetime.utcnow().isoformat()
    }

@router.post("/campaign/package", response_model=Dict[str, Any])
async def package_campaign(request: CampaignPackageRequest):
    """Create a complete campaign package."""
    package_id = f"pkg_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    
    package_contents = {
        "clips": 5,
        "hooks": 3 if request.include_hooks else 0,
        "captions": 8 if request.include_captions else 0,
        "thumbnail_texts": 3 if request.include_thumbnails else 0,
        "platform_variants": len(request.platforms)
    }
    
    formats = []
    for platform in request.platforms:
        formats.append({
            "platform": platform,
            "resolution": "1080x1920" if platform in ["tiktok", "instagram_reels", "youtube_shorts"] else "1920x1080",
            "aspect_ratio": "9:16" if platform in ["tiktok", "instagram_reels", "youtube_shorts"] else "16:9",
            "file_format": "mp4",
            "max_duration": 90 if platform in ["tiktok", "instagram_reels"] else 60
        })
    
    return {
        "success": True,
        "package_id": package_id,
        "campaign_name": request.campaign_name,
        "video_id": request.video_id,
        "contents": package_contents,
        "formats": formats,
        "packaging_angle": request.packaging_angle or "general",
        "download_url": f"/api/v1/creative-engines/download/{package_id}",
        "estimated_size_mb": 245.5,
        "created_at": datetime.utcnow().isoformat(),
        "expires_at": (datetime.utcnow() + timedelta(days=7)).isoformat()
    }

@router.get("/jobs", response_model=Dict[str, Any])
async def list_jobs(
    status: Optional[str] = None,
    engine_id: Optional[str] = None
):
    """List creative engine jobs."""
    jobs = list(MOCK_JOBS.values())
    
    if status:
        jobs = [j for j in jobs if j.status == status]
    
    if engine_id:
        jobs = [j for j in jobs if j.engine_id == engine_id]
    
    return {
        "success": True,
        "jobs": [j.dict() for j in jobs],
        "total_count": len(jobs),
        "pending_count": len([j for j in jobs if j.status == "pending"]),
        "completed_count": len([j for j in jobs if j.status == "completed"]),
        "failed_count": len([j for j in jobs if j.status == "failed"])
    }

@router.get("/jobs/{job_id}", response_model=Dict[str, Any])
async def get_job_status(job_id: str):
    """Get job status and results."""
    if job_id not in MOCK_JOBS:
        # Return mock job status
        return {
            "success": True,
            "job": {
                "id": job_id,
                "engine_id": "engine_clip_core",
                "status": "completed",
                "input_data": {"video_url": "https://example.com/video"},
                "output_data": {"clips": 5, "confidence": 0.92},
                "created_at": datetime.utcnow().isoformat(),
                "completed_at": datetime.utcnow().isoformat(),
                "processing_time": 45.5
            }
        }
    
    return {
        "success": True,
        "job": MOCK_JOBS[job_id].dict()
    }

@router.get("/stats", response_model=Dict[str, Any])
async def get_engine_stats():
    """Get overall creative engine statistics."""
    engines = list(MOCK_ENGINES.values())
    
    total_jobs = len(MOCK_JOBS)
    completed_jobs = len([j for j in MOCK_JOBS.values() if j.status == "completed"])
    
    return {
        "success": True,
        "stats": {
            "total_engines": len(engines),
            "active_engines": len([e for e in engines if e.status == EngineStatus.ACTIVE]),
            "beta_engines": len([e for e in engines if e.status == EngineStatus.BETA]),
            "in_development": len([e for e in engines if e.status == EngineStatus.DEVELOPMENT]),
            "avg_success_rate": sum(e.success_rate for e in engines) / len(engines) if engines else 0,
            "avg_processing_time": sum(e.processing_time_avg for e in engines) / len(engines) if engines else 0,
            "total_jobs": total_jobs,
            "completed_jobs": completed_jobs,
            "completion_rate": completed_jobs / total_jobs if total_jobs > 0 else 0
        }
    }

def format_time(seconds: float) -> str:
    """Format seconds to SRT timestamp format."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
