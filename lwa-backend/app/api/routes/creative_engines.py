"""
Creative Engines API Routes

Provides endpoints for all creative engines:
- Thumbnail Engine
- B-roll Engine  
- Hook Engine
- Trend Intelligence Engine
- Audience Persona Engine
- Offer CTA Engine
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List, Optional, Any
from pydantic import BaseModel

from ...services.creative.thumbnail_engine import thumbnail_engine
from ...services.creative.b_roll_engine import b_roll_engine
from ...services.creative.viral_hook_lab import viral_hook_lab
from ...services.creative.trend_intelligence_engine import trend_intelligence_engine
from ...services.creative.audience_persona_engine import audience_persona_engine
from ...services.creative.offer_cta_engine import offer_cta_engine
from ...services.creative.thumbnail_engine import ThumbnailRequest, ThumbnailStyle
from ...services.creative.b_roll_engine import BRollRequest, BRollType
from ...services.creative.trend_intelligence_engine import TrendType, Platform
from ...services.creative.audience_persona_engine import AudienceType, ContentGoal
from ...services.creative.offer_cta_engine import OfferType, ConversionGoal, ContentCategory

router = APIRouter(prefix="/v1/creative", tags=["creative"])

# Thumbnail Engine
class ThumbnailGenerateRequest(BaseModel):
    video_title: str
    video_description: str
    target_audience: str
    platform: str
    style: str
    brand_colors: List[str]
    key_moments: List[str]
    emotional_tone: str
    call_to_action: Optional[str] = None
    include_face: bool = True
    include_text: bool = True

@router.post("/thumbnail/generate")
async def generate_thumbnail(request: ThumbnailGenerateRequest) -> Dict[str, Any]:
    """Generate creative thumbnails for video content."""
    try:
        thumbnail_request = ThumbnailRequest(
            video_title=request.video_title,
            video_description=request.video_description,
            target_audience=request.target_audience,
            platform=request.platform,
            style=ThumbnailStyle(request.style),
            brand_colors=request.brand_colors,
            key_moments=request.key_moments,
            emotional_tone=request.emotional_tone,
            call_to_action=request.call_to_action,
            include_face=request.include_face,
            include_text=request.include_text
        )
        
        result = thumbnail_engine.generate_thumbnail_variants(thumbnail_request)
        return {
            "success": True,
            "thumbnails": result,
            "count": len(result)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/thumbnail/styles")
async def get_thumbnail_styles() -> Dict[str, List[str]]:
    """Get available thumbnail styles."""
    return {
        "styles": [style.value for style in ThumbnailStyle],
        "default": ThumbnailStyle.BOLD_TEXT.value
    }

# B-roll Engine
class BRollGenerateRequest(BaseModel):
    video_description: str
    content_type: str
    target_duration: int
    platform: str
    visual_style: str
    key_topics: List[str]

@router.post("/broll/generate")
async def generate_broll(request: BRollGenerateRequest) -> Dict[str, Any]:
    """Generate B-roll scenes and supplementary footage."""
    try:
        broll_request = BRollRequest(
            video_description=request.video_description,
            content_type=request.content_type,
            target_duration=request.target_duration,
            platform=request.platform,
            visual_style=request.visual_style,
            key_topics=request.key_topics
        )
        
        result = b_roll_engine.generate_broll_scenes(broll_request)
        return {
            "success": True,
            "scenes": result,
            "count": len(result)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/broll/types")
async def get_broll_types() -> Dict[str, List[str]]:
    """Get available B-roll types."""
    return {
        "types": [broll_type.value for broll_type in BRollType],
        "default": BRollType.CONTEXTUAL.value
    }

# Hook Engine
class HookGenerateRequest(BaseModel):
    content_description: str
    target_platform: str
    content_type: str
    emotional_tone: str
    target_audience: str

@router.post("/hook/generate")
async def generate_hooks(request: HookGenerateRequest) -> Dict[str, Any]:
    """Generate viral hooks for content."""
    try:
        result = viral_hook_lab.generate_hooks(
            content_description=request.content_description,
            target_platform=request.target_platform,
            content_type=request.content_type,
            emotional_tone=request.emotional_tone,
            target_audience=request.target_audience
        )
        return {
            "success": True,
            "hooks": result,
            "count": len(result)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Trend Intelligence Engine
class TrendAnalysisRequest(BaseModel):
    content_description: str
    target_platforms: List[str]
    timeframe_days: int = 7

@router.post("/trends/analyze")
async def analyze_trends(request: TrendAnalysisRequest) -> Dict[str, Any]:
    """Analyze content for trend opportunities."""
    try:
        platforms = [Platform(platform) for platform in request.target_platforms]
        opportunities = trend_intelligence_engine.analyze_content_trends(
            content_description=request.content_description,
            target_platforms=platforms,
            timeframe_days=request.timeframe_days
        )
        return {
            "success": True,
            "opportunities": opportunities,
            "count": len(opportunities)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trends/hashtags/{platform}")
async def get_trending_hashtags(platform: str, category: Optional[str] = None) -> Dict[str, List[str]]:
    """Get trending hashtags for platform."""
    try:
        platform_enum = Platform(platform)
        hashtags = trend_intelligence_engine.get_trending_hashtags(platform_enum, category)
        return {
            "platform": platform,
            "hashtags": hashtags,
            "category": category
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Audience Persona Engine
class AudienceAnalysisRequest(BaseModel):
    content_description: str
    content_goal: str
    target_platforms: List[str] = []

@router.post("/audience/analyze")
async def analyze_audience(request: AudienceAnalysisRequest) -> Dict[str, Any]:
    """Identify target audiences and get recommendations."""
    try:
        content_goal = ContentGoal(request.content_goal)
        platforms = [Platform(platform) for platform in request.target_platforms] if request.target_platforms else None
        
        target_audiences = audience_persona_engine.identify_target_audience(
            content_description=request.content_description,
            content_goal=content_goal,
            target_platforms=platforms
        )
        
        recommendations = []
        for audience_type in target_audiences:
            recommendation = audience_persona_engine.generate_personalized_content(
                target_persona=audience_type,
                content_description=request.content_description,
                content_goal=content_goal,
                platform=platforms[0] if platforms else "tiktok"
            )
            recommendations.append(recommendation)
        
        return {
            "success": True,
            "target_audiences": [audience.value for audience in target_audiences],
            "recommendations": recommendations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/audience/personas")
async def get_audience_personas() -> Dict[str, List[str]]:
    """Get available audience personas."""
    return {
        "personas": [persona.value for persona in AudienceType],
        "goals": [goal.value for goal in ContentGoal]
    }

# Offer CTA Engine
class OfferAnalysisRequest(BaseModel):
    content_description: str
    content_category: str
    target_audience: str = "general"
    platform: str = "tiktok"

@router.post("/offers/analyze")
async def analyze_offers(request: OfferAnalysisRequest) -> Dict[str, Any]:
    """Analyze content for monetization opportunities."""
    try:
        content_category = ContentCategory(request.content_category)
        platform = Platform(request.platform)
        
        recommendations = offer_cta_engine.analyze_monetization_opportunities(
            content_description=request.content_description,
            content_category=content_category,
            target_audience=request.target_audience,
            platform=platform.value
        )
        
        return {
            "success": True,
            "recommendations": recommendations,
            "count": len(recommendations)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/offers/cta")
async def generate_cta(offer_type: str, content_context: str, platform: str = "tiktok", urgency_level: str = "medium") -> Dict[str, Any]:
    """Generate effective call-to-action for specific offer type."""
    try:
        offer_enum = OfferType(offer_type)
        platform_enum = Platform(platform)
        
        cta = offer_cta_engine.generate_effective_cta(
            offer_type=offer_enum,
            content_context=content_context,
            platform=platform_enum.value,
            urgency_level=urgency_level
        )
        
        return {
            "success": True,
            "cta": {
                "text": cta.text,
                "placement": cta.placement,
                "urgency": cta.urgency,
                "visual_style": cta.visual_style,
                "button_color": cta.button_color,
                "timing": cta.timing,
                "follow_up_action": cta.follow_up_action
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/offers/types")
async def get_offer_types() -> Dict[str, List[str]]:
    """Get available offer types."""
    return {
        "types": [offer_type.value for offer_type in OfferType],
        "goals": [goal.value for goal in ConversionGoal],
        "categories": [category.value for category in ContentCategory]
    }

# Health check
@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Check health of all creative engines."""
    return {
        "status": "healthy",
        "engines": "thumbnail, broll, hook, trends, audience, offers"
    }
