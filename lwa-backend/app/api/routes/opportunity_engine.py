from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional

from app.core.auth import get_current_user_optional
from app.core.config import Settings, get_settings
from app.services.director_brain import (
    analyze_opportunity_potential,
    classify_content_purpose,
    identify_audience_target,
    map_to_opportunity_type,
    OpportunityInsight
)
from app.models.schemas import ClipResult

router = APIRouter()


class OpportunityAnalysisRequest(BaseModel):
    title: Optional[str] = None
    hook: Optional[str] = None
    caption: Optional[str] = None
    reason: Optional[str] = None
    category: Optional[str] = None
    transcript: Optional[str] = None


class OpportunityAnalysisResponse(BaseModel):
    purpose: str
    audience_target: str
    opportunity_type: str
    confidence: int
    next_action: str
    risk_level: str
    explanation: str


class ContentProfileRequest(BaseModel):
    user_niche: Optional[str] = None
    target_audience: Optional[str] = None
    primary_offer: Optional[str] = None
    content_goals: Optional[List[str]] = None
    platforms: Optional[List[str]] = None


class DailyRecommendationResponse(BaseModel):
    best_move_today: str
    opportunity_type: str
    confidence: int
    next_action: str
    platform_recommendation: str
    content_purpose: str
    risk_assessment: str


@router.post("/opportunity-engine/analyze", response_model=OpportunityAnalysisResponse)
async def analyze_content_opportunity(
    request: OpportunityAnalysisRequest,
    current_user: dict = Depends(get_current_user_optional),
    settings: Settings = Depends(get_settings),
):
    """Analyze content for opportunity potential using the Opportunity Engine."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Create a mock clip for analysis
    clip = ClipResult(
        id="opportunity_analysis",
        title=request.title or "",
        hook=request.hook or "",
        caption=request.caption or "",
        reason=request.reason or "",
        category=request.category or "education",
        transcript_excerpt=request.transcript or "",
        score=70,
        confidence_score=70,
    )
    
    # Analyze opportunity potential
    category = request.category or "education"
    insight = analyze_opportunity_potential(clip, category=category)
    
    return OpportunityAnalysisResponse(
        purpose=insight.purpose,
        audience_target=insight.audience_target,
        opportunity_type=insight.opportunity_type,
        confidence=insight.confidence,
        next_action=insight.next_action,
        risk_level=insight.risk_level,
        explanation=f"This content is designed to build {insight.purpose} with {insight.audience_target} and could lead to {insight.opportunity_type}."
    )


@router.get("/opportunity-engine/daily-recommendation", response_model=DailyRecommendationResponse)
async def get_daily_opportunity_recommendation(
    current_user: dict = Depends(get_current_user_optional),
    settings: Settings = Depends(get_settings),
):
    """Get today's best content move based on user profile and goals."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user_id = current_user.get("user_id", f"guest:{current_user.get('id', 'unknown')}")
    
    # For now, return a default recommendation
    # In the future, this would analyze user's content history and profile
    recommendation = DailyRecommendationResponse(
        best_move_today="Post a trust-building clip that shows your expertise and process",
        opportunity_type="consulting discovery call",
        confidence=75,
        next_action="Share this with business owners who need your expertise",
        platform_recommendation="LinkedIn for professional credibility",
        content_purpose="trust",
        risk_assessment="low"
    )
    
    return recommendation


@router.get("/opportunity-engine/purpose-classification")
async def get_purpose_classification_guide(
    current_user: dict = Depends(get_current_user_optional),
    settings: Settings = Depends(get_settings),
):
    """Get guide to content purpose classifications."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    purposes = {
        "trust": {
            "description": "Build relationship and credibility with your audience",
            "signals": ["story", "behind the scenes", "my journey", "mistake", "failure", "learned", "experience", "testimonial", "proof", "result", "transformation"],
            "best_for": ["onboarding leads", "building relationships", "showing expertise"],
            "next_action": "Use this to build relationship before asking for sale"
        },
        "sales": {
            "description": "Direct content toward conversion and revenue",
            "signals": ["buy", "sale", "offer", "discount", "price", "join", "sign up", "get started", "invest", "purchase", "order", "book now"],
            "best_for": ["product sales", "service bookings", "course enrollments"],
            "next_action": "Direct interested prospects to your offer immediately"
        },
        "attention": {
            "description": "Create viral potential and maximize reach",
            "signals": ["shocking", "unbelievable", "never seen", "secret", "revealed", "exposed", "controversial", "debate", "vs", "battle", "challenge"],
            "best_for": ["viral growth", "brand awareness", "audience expansion"],
            "next_action": "Post during peak hours to maximize viral potential"
        },
        "authority": {
            "description": "Establish expertise and thought leadership",
            "signals": ["expert", "research", "study", "data", "analysis", "framework", "method", "system", "strategy", "breakthrough", "innovation"],
            "best_for": ["thought leadership", "expert consulting", "career opportunities"],
            "next_action": "Include in professional portfolio and LinkedIn"
        },
        "community": {
            "description": "Build tribe and foster connection",
            "signals": ["community", "together", "join us", "we", "our", "family", "team", "movement", "tribe", "belong", "connect"],
            "best_for": ["community building", "tribe building", "engagement"],
            "next_action": "Share in niche communities to spark discussion"
        }
    }
    
    return JSONResponse(content={
        "purposes": purposes,
        "usage": "Each piece of content should have a clear purpose. The Opportunity Engine analyzes your content and tells you what purpose it serves and what opportunity it creates."
    })


@router.get("/opportunity-engine/audience-targets")
async def get_audience_target_guide(
    current_user: dict = Depends(get_current_user_optional),
    settings: Settings = Depends(get_settings),
):
    """Get guide to audience targeting options."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    audiences = {
        "beginners": {
            "description": "People new to your topic or industry",
            "signals": ["beginner", "newbie", "start", "getting started", "first time", "basics", "introduction"],
            "opportunity": "onboarding lead",
            "best_content": "Educational, foundational content"
        },
        "advanced practitioners": {
            "description": "Experienced individuals in your field",
            "signals": ["advanced", "expert", "pro", "master", "deep dive", "technical", "nuanced"],
            "opportunity": "thought leadership",
            "best_content": "Advanced strategies, technical insights"
        },
        "business owners": {
            "description": "Entrepreneurs and business decision makers",
            "signals": ["business", "owner", "entrepreneur", "startup", "company", "revenue", "profit", "growth"],
            "opportunity": "expert consulting",
            "best_content": "Business strategies, growth tactics"
        },
        "creators": {
            "description": "Content creators and influencers",
            "signals": ["creator", "content", "audience", "engagement", "viral", "growth", "monetize"],
            "opportunity": "collaboration opportunity",
            "best_content": "Creator strategies, monetization tactics"
        },
        "local customers": {
            "description": "People in your geographic area",
            "signals": ["local", "near me", "area", "community", "neighborhood", "city", "town"],
            "opportunity": "local business visit",
            "best_content": "Local expertise, community involvement"
        },
        "investors": {
            "description": "People looking to invest or fund",
            "signals": ["invest", "funding", "roi", "return", "venture", "capital", "startup", "scale"],
            "opportunity": "investment opportunity",
            "best_content": "Growth metrics, market opportunity, team vision"
        },
        "job seekers": {
            "description": "People looking for career opportunities",
            "signals": ["career", "job", "hire", "resume", "interview", "professional", "skills"],
            "opportunity": "career opportunity",
            "best_content": "Career advice, skill development, industry insights"
        },
        "coaches/consultants": {
            "description": "Other coaches and consultants",
            "signals": ["coach", "consultant", "client", "framework", "methodology", "transformation"],
            "opportunity": "peer collaboration",
            "best_content": "Coaching methods, client success stories"
        },
        "general consumers": {
            "description": "Broad audience without specific expertise",
            "signals": ["everyone", "anyone", "people", "you", "your", "general", "public"],
            "opportunity": "general engagement",
            "best_content": "Entertaining, educational, broadly appealing content"
        }
    }
    
    return JSONResponse(content={
        "audiences": audiences,
        "usage": "The Opportunity Engine identifies who your content serves and what opportunity it creates with that audience."
    })


@router.get("/opportunity-engine/opportunity-types")
async def get_opportunity_type_guide(
    current_user: dict = Depends(get_current_user_optional),
    settings: Settings = Depends(get_settings),
):
    """Get guide to opportunity types and their business value."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    opportunities = {
        "onboarding lead": {
            "description": "Convert interested people into your ecosystem",
            "value": "Builds pipeline for future sales",
            "best_purpose": "trust",
            "best_audience": "beginners"
        },
        "consulting discovery call": {
            "description": "Generate high-value consulting conversations",
            "value": "Premium service revenue",
            "best_purpose": "trust",
            "best_audience": "business owners"
        },
        "local business visit": {
            "description": "Drive local customers to your business",
            "value": "Local market dominance",
            "best_purpose": "trust",
            "best_audience": "local customers"
        },
        "collaboration opportunity": {
            "description": "Create partnerships with other creators",
            "value": "Audience expansion and credibility",
            "best_purpose": "trust",
            "best_audience": "creators"
        },
        "product sale": {
            "description": "Direct product or service purchases",
            "value": "Immediate revenue",
            "best_purpose": "sales",
            "best_audience": "general consumers"
        },
        "B2B contract": {
            "description": "Business-to-business service agreements",
            "value": "High-value recurring revenue",
            "best_purpose": "sales",
            "best_audience": "business owners"
        },
        "investment opportunity": {
            "description": "Attract funding or investment",
            "value": "Growth capital and strategic support",
            "best_purpose": "sales",
            "best_audience": "investors"
        },
        "viral growth": {
            "description": "Rapid audience expansion through sharing",
            "value": "Scale and brand awareness",
            "best_purpose": "attention",
            "best_audience": "creators"
        },
        "brand awareness": {
            "description": "Increase recognition and recall",
            "value": "Long-term brand equity",
            "best_purpose": "attention",
            "best_audience": "general consumers"
        },
        "thought leadership": {
            "description": "Establish expertise in your field",
            "value": "Premium positioning and opportunities",
            "best_purpose": "authority",
            "best_audience": "advanced practitioners"
        },
        "expert consulting": {
            "description": "Generate high-value consulting work",
            "value": "Premium service revenue",
            "best_purpose": "authority",
            "best_audience": "business owners"
        },
        "career opportunity": {
            "description": "Create job or career advancement opportunities",
            "value": "Professional growth and income",
            "best_purpose": "authority",
            "best_audience": "job seekers"
        },
        "community building": {
            "description": "Create engaged community around your brand",
            "value": "Long-term loyalty and advocacy",
            "best_purpose": "community",
            "best_audience": "creators"
        },
        "tribe building": {
            "description": "Build dedicated following of true fans",
            "value": "Sustainable business and support",
            "best_purpose": "community",
            "best_audience": "general consumers"
        },
        "general engagement": {
            "description": "Generate likes, comments, and basic interaction",
            "value": "Algorithm favorability and basic presence",
            "best_purpose": "any",
            "best_audience": "general consumers"
        }
    }
    
    return JSONResponse(content={
        "opportunities": opportunities,
        "usage": "Each piece of content creates specific business opportunities. The Opportunity Engine maps your content to the most valuable opportunities."
    })
