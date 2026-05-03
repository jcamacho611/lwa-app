"""
Style Memory API Routes
Stores creator preferences, brand voice, and learned style patterns.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

router = APIRouter(prefix="/api/v1/style-memory", tags=["style_memory"])

class HookStyle(str, Enum):
    QUESTION = "question"
    STATEMENT = "statement"
    HOW_TO = "how_to"
    LISTICLE = "listicle"
    STORY = "story"
    CONTROVERSY = "controversy"
    CURIOSITY = "curiosity"

class CaptionStyle(str, Enum):
    MINIMAL = "minimal"
    BOLD = "bold"
    EDUCATIONAL = "educational"
    HUMOROUS = "humorous"
    PROFESSIONAL = "professional"
    CASUAL = "casual"

class VisualStyle(str, Enum):
    CLEAN = "clean"
    GRUNGY = "grungy"
    CORPORATE = "corporate"
    PLAYFUL = "playful"
    MINIMALIST = "minimalist"
    BOLD_COLORS = "bold_colors"

class CreatorStyleProfile(BaseModel):
    user_id: str
    niche: Optional[str]
    target_audience: Optional[str]
    content_vertical: Optional[str]
    brand_voice: Optional[str]
    tone_keywords: List[str]
    preferred_hook_styles: List[HookStyle]
    preferred_caption_style: Optional[CaptionStyle]
    preferred_visual_style: Optional[VisualStyle]
    signature_ctas: List[str]
    avoid_words: List[str]
    preferred_words: List[str]
    platform_defaults: Dict[str, Any]
    created_at: str
    updated_at: str

class StylePreferenceUpdate(BaseModel):
    niche: Optional[str]
    target_audience: Optional[str]
    content_vertical: Optional[str]
    brand_voice: Optional[str]
    tone_keywords: Optional[List[str]]
    preferred_hook_styles: Optional[List[HookStyle]]
    preferred_caption_style: Optional[CaptionStyle]
    preferred_visual_style: Optional[VisualStyle]
    signature_ctas: Optional[List[str]]
    avoid_words: Optional[List[str]]
    preferred_words: Optional[List[str]]

class LeeWuhRecommendation(BaseModel):
    recommendation_type: str
    title: str
    description: str
    confidence: float
    based_on: List[str]
    action: str

# Mock style memory storage
MOCK_STYLE_PROFILES: Dict[str, CreatorStyleProfile] = {
    "user_001": CreatorStyleProfile(
        user_id="user_001",
        niche="podcast_editing",
        target_audience="professionals_25_45",
        content_vertical="business_self_improvement",
        brand_voice="confident_educational",
        tone_keywords=["confident", "insightful", "direct", "premium"],
        preferred_hook_styles=[HookStyle.QUESTION, HookStyle.CURIOSITY, HookStyle.CONTROVERSY],
        preferred_caption_style=CaptionStyle.BOLD,
        preferred_visual_style=VisualStyle.CLEAN,
        signature_ctas=[
            "Follow for more insights",
            "Share with someone who needs this",
            "Save for later"
        ],
        avoid_words=["cheap", "easy", "just", "simply", "obviously"],
        preferred_words=["strategic", "proven", "exclusive", "breakthrough"],
        platform_defaults={
            "tiktok": {"duration": 15, "hook_style": "curiosity"},
            "youtube_shorts": {"duration": 45, "hook_style": "how_to"},
            "instagram_reels": {"duration": 30, "hook_style": "question"}
        },
        created_at="2025-01-15T00:00:00Z",
        updated_at="2025-05-03T00:00:00Z"
    )
}

MOCK_LEE_WUH_MEMORY: Dict[str, List[LeeWuhRecommendation]] = {
    "user_001": [
        LeeWuhRecommendation(
            recommendation_type="hook_pattern",
            title="Use Curiosity Gaps",
            description="Your top 3 winning clips all use curiosity-gap hooks. Try 'You won't believe...' or 'The truth about...'",
            confidence=0.92,
            based_on=["proof_001", "proof_003"],
            action="Apply to next clip generation"
        ),
        LeeWuhRecommendation(
            recommendation_type="caption_style",
            title="Bold Minimal Captions",
            description="Bold text with minimal words performs 34% better for your audience",
            confidence=0.88,
            based_on=["style_profile"],
            action="Set as default caption style"
        ),
        LeeWuhRecommendation(
            recommendation_type="platform_strategy",
            title="TikTok: 15s Sweet Spot",
            description="Your TikTok clips under 18s get 2x more views",
            confidence=0.85,
            based_on=["performance_data"],
            action="Trim TikTok clips to 15s"
        ),
        LeeWuhRecommendation(
            recommendation_type="cta_optimization",
            title="'Save for later' CTA",
            description="This CTA gets 3x more saves than 'Follow for more' on educational content",
            confidence=0.79,
            based_on=["proof_003"],
            action="Use for tutorial content"
        )
    ]
}

@router.get("/profile", response_model=Dict[str, Any])
async def get_style_profile(user_id: str = "user_001"):
    """Get creator's style memory profile."""
    if user_id not in MOCK_STYLE_PROFILES:
        # Return default profile
        return {
            "success": True,
            "profile": None,
            "message": "No style profile yet. One will be created as you use LWA.",
            "is_new": True
        }
    
    return {
        "success": True,
        "profile": MOCK_STYLE_PROFILES[user_id].dict(),
        "is_new": False
    }

@router.post("/profile", response_model=Dict[str, Any])
async def create_style_profile(profile: StylePreferenceUpdate, user_id: str = "user_001"):
    """Create or update style profile."""
    now = datetime.utcnow().isoformat()
    
    if user_id in MOCK_STYLE_PROFILES:
        # Update existing
        existing = MOCK_STYLE_PROFILES[user_id]
        
        if profile.niche:
            existing.niche = profile.niche
        if profile.target_audience:
            existing.target_audience = profile.target_audience
        if profile.content_vertical:
            existing.content_vertical = profile.content_vertical
        if profile.brand_voice:
            existing.brand_voice = profile.brand_voice
        if profile.tone_keywords:
            existing.tone_keywords = profile.tone_keywords
        if profile.preferred_hook_styles:
            existing.preferred_hook_styles = profile.preferred_hook_styles
        if profile.preferred_caption_style:
            existing.preferred_caption_style = profile.preferred_caption_style
        if profile.preferred_visual_style:
            existing.preferred_visual_style = profile.preferred_visual_style
        if profile.signature_ctas:
            existing.signature_ctas = profile.signature_ctas
        if profile.avoid_words:
            existing.avoid_words = profile.avoid_words
        if profile.preferred_words:
            existing.preferred_words = profile.preferred_words
        
        existing.updated_at = now
        
        return {
            "success": True,
            "profile": existing.dict(),
            "message": "Style profile updated"
        }
    else:
        # Create new
        new_profile = CreatorStyleProfile(
            user_id=user_id,
            niche=profile.niche,
            target_audience=profile.target_audience,
            content_vertical=profile.content_vertical,
            brand_voice=profile.brand_voice,
            tone_keywords=profile.tone_keywords or [],
            preferred_hook_styles=profile.preferred_hook_styles or [],
            preferred_caption_style=profile.preferred_caption_style,
            preferred_visual_style=profile.preferred_visual_style,
            signature_ctas=profile.signature_ctas or [],
            avoid_words=profile.avoid_words or [],
            preferred_words=profile.preferred_words or [],
            platform_defaults={},
            created_at=now,
            updated_at=now
        )
        
        MOCK_STYLE_PROFILES[user_id] = new_profile
        
        return {
            "success": True,
            "profile": new_profile.dict(),
            "message": "Style profile created"
        }

@router.patch("/profile", response_model=Dict[str, Any])
async def update_style_profile(updates: StylePreferenceUpdate, user_id: str = "user_001"):
    """Partial update to style profile."""
    if user_id not in MOCK_STYLE_PROFILES:
        raise HTTPException(status_code=404, detail="Style profile not found. Create one first.")
    
    profile = MOCK_STYLE_PROFILES[user_id]
    
    # Apply updates
    for field, value in updates.dict(exclude_unset=True).items():
        if value is not None:
            setattr(profile, field, value)
    
    profile.updated_at = datetime.utcnow().isoformat()
    
    return {
        "success": True,
        "profile": profile.dict(),
        "message": "Style preferences updated"
    }

@router.get("/recommendations", response_model=Dict[str, Any])
async def get_lee_wuh_recommendations(user_id: str = "user_001", limit: int = 5):
    """Get Lee-Wuh's personalized recommendations based on style memory."""
    recommendations = MOCK_LEE_WUH_MEMORY.get(user_id, [])
    
    # Sort by confidence
    recommendations = sorted(recommendations, key=lambda x: x.confidence, reverse=True)
    
    return {
        "success": True,
        "recommendations": [r.dict() for r in recommendations[:limit]],
        "total_available": len(recommendations),
        "based_on": {
            "proof_vault_assets": len([a for a in MOCK_STYLE_PROFILES.get(user_id, {}).dict().values() if a]),
            "style_profile_exists": user_id in MOCK_STYLE_PROFILES
        }
    }

@router.post("/learn/clip-feedback", response_model=Dict[str, Any])
async def learn_from_clip_feedback(
    clip_id: str,
    approved: bool,
    feedback_notes: Optional[str] = None,
    style_tags: Optional[List[str]] = None,
    user_id: str = "user_001"
):
    """Learn from user feedback on a clip."""
    # In a real implementation, this would update the style profile based on feedback
    # For now, just acknowledge the learning
    
    learnings = []
    
    if approved:
        learnings.append("Positive example added to style memory")
        if style_tags:
            learnings.append(f"Style tags recorded: {', '.join(style_tags)}")
    else:
        learnings.append("Negative example recorded for avoidance")
        if feedback_notes:
            learnings.append(f"Feedback analyzed: {feedback_notes[:50]}...")
    
    return {
        "success": True,
        "message": "Feedback recorded. Lee-Wuh will use this to improve future recommendations.",
        "learnings": learnings,
        "next_recommendation_update": "Available in 24 hours"
    }

@router.get("/hooks/best", response_model=Dict[str, Any])
async def get_best_hook_patterns(user_id: str = "user_001", platform: Optional[str] = None):
    """Get best performing hook patterns for this creator."""
    profile = MOCK_STYLE_PROFILES.get(user_id)
    
    if not profile:
        return {
            "success": True,
            "patterns": None,
            "message": "No style memory yet. Generate and approve some clips first!"
        }
    
    # Return hook patterns based on preferences and past performance
    recommended_patterns = []
    
    for style in profile.preferred_hook_styles:
        if style == HookStyle.QUESTION:
            recommended_patterns.extend([
                "Have you ever wondered...",
                "What if I told you...",
                "Why do most people..."
            ])
        elif style == HookStyle.CURIOSITY:
            recommended_patterns.extend([
                "You won't believe what happens...",
                "The truth about...",
                "This changes everything..."
            ])
        elif style == HookStyle.CONTROVERSY:
            recommended_patterns.extend([
                "Stop doing this...",
                "Most experts are wrong about...",
                "Unpopular opinion:..."
            ])
        elif style == HookStyle.HOW_TO:
            recommended_patterns.extend([
                "How to... in 30 seconds",
                "The fastest way to...",
                "Stop making this mistake..."
            ])
    
    return {
        "success": True,
        "recommended_patterns": recommended_patterns[:6],
        "based_on": f"Your preferred hook styles: {', '.join([s.value for s in profile.preferred_hook_styles])}",
        "platform": platform or "all"
    }

@router.get("/captions/style", response_model=Dict[str, Any])
async def get_caption_style_guide(user_id: str = "user_001"):
    """Get personalized caption style guide."""
    profile = MOCK_STYLE_PROFILES.get(user_id)
    
    if not profile or not profile.preferred_caption_style:
        return {
            "success": True,
            "style": None,
            "message": "No caption style preference set yet.",
            "default_guide": {
                "style": "standard",
                "max_words_per_line": 4,
                "font": "Bold sans-serif",
                "colors": ["White text", "Black outline"]
            }
        }
    
    style_guides = {
        CaptionStyle.MINIMAL: {
            "description": "Minimal text, maximum impact",
            "max_words_per_line": 3,
            "font": "Clean sans-serif",
            "colors": ["White", "Subtle shadow"],
            "example": "Simple.\nClean.\nPowerful."
        },
        CaptionStyle.BOLD: {
            "description": "Bold, attention-grabbing captions",
            "max_words_per_line": 4,
            "font": "Heavy weight sans-serif",
            "colors": ["White text", "Thick black outline"],
            "example": "THIS IS\nTHE MOMENT"
        },
        CaptionStyle.EDUCATIONAL: {
            "description": "Clear, informative text",
            "max_words_per_line": 5,
            "font": "Readable sans-serif",
            "colors": ["White", "Black outline"],
            "example": "Step 1: Identify\nStep 2: Analyze\nStep 3: Execute"
        }
    }
    
    return {
        "success": True,
        "style": profile.preferred_caption_style.value,
        "guide": style_guides.get(profile.preferred_caption_style, style_guides[CaptionStyle.BOLD]),
        "avoid_words": profile.avoid_words[:5] if profile.avoid_words else [],
        "preferred_words": profile.preferred_words[:5] if profile.preferred_words else []
    }

@router.get("/brand/voice", response_model=Dict[str, Any])
async def get_brand_voice_profile(user_id: str = "user_001"):
    """Get the creator's brand voice profile."""
    profile = MOCK_STYLE_PROFILES.get(user_id)
    
    if not profile:
        return {
            "success": True,
            "voice": None,
            "message": "Brand voice not configured. Set up your style profile!"
        }
    
    return {
        "success": True,
        "voice": {
            "brand_voice": profile.brand_voice,
            "tone_keywords": profile.tone_keywords,
            "niche": profile.niche,
            "target_audience": profile.target_audience,
            "content_vertical": profile.content_vertical
        },
        "voice_examples": {
            "confident_educational": "Direct, authoritative, teaching without being condescending",
            "playful_entertaining": "Fun, energetic, doesn't take itself too seriously",
            "professional_insightful": "Expert-level content, data-driven, serious tone"
        }.get(profile.brand_voice or "", "Custom brand voice configured")
    }

@router.post("/reset", response_model=Dict[str, Any])
async def reset_style_memory(user_id: str = "user_001", confirm: bool = False):
    """Reset style memory (for testing or fresh start)."""
    if not confirm:
        return {
            "success": False,
            "message": "Set confirm=true to reset style memory. This cannot be undone."
        }
    
    if user_id in MOCK_STYLE_PROFILES:
        del MOCK_STYLE_PROFILES[user_id]
    
    if user_id in MOCK_LEE_WUH_MEMORY:
        del MOCK_LEE_WUH_MEMORY[user_id]
    
    return {
        "success": True,
        "message": "Style memory reset. Starting fresh!"
    }
