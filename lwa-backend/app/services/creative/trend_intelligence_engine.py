"""
Trend Intelligence Engine v0

Identifies viral patterns, platform trends, and content opportunities
for strategic content creation and platform optimization.
"""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta

logger = logging.getLogger("uvicorn.error")


class TrendType(str, Enum):
    """Types of trends to track."""
    
    VIRAL_FORMAT = "viral_format"
    HASHTAG = "hashtag"
    CHALLENGE = "challenge"
    SOUND = "sound"
    EFFECT = "effect"
    TOPIC = "topic"
    CELEBRITY = "celebrity"
    MEME = "meme"


class Platform(str, Enum):
    """Social media platforms."""
    
    TIKTOK = "tiktok"
    INSTAGRAM_REELS = "instagram_reels"
    YOUTUBE_SHORTS = "youtube_shorts"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"


@dataclass
class TrendSignal:
    """Individual trend signal."""
    
    trend_type: TrendType
    platform: Platform
    name: str
    description: str
    engagement_score: float
    growth_rate: float
    duration_days: int
    hashtags: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    discovered_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ContentOpportunity:
    """Content opportunity based on trends."""
    
    trend: TrendSignal
    recommended_format: str
    hook_templates: List[str] = field(default_factory=list)
    caption_templates: List[str] = field(default_factory=list)
    timing_suggestions: List[str] = field(default_factory=list)
    confidence_score: float = 0.0


class TrendIntelligenceEngine:
    """
    Trend intelligence engine for identifying viral patterns
    and content opportunities across platforms.
    """
    
    def __init__(self) -> None:
        self._trend_database: List[TrendSignal] = []
        self._viral_patterns = self._build_viral_patterns()
        self._platform_insights = self._build_platform_insights()
        self._initialize_mock_trends()
    
    def analyze_content_trends(
        self,
        content_description: str,
        target_platforms: List[Platform],
        timeframe_days: int = 7
    ) -> List[ContentOpportunity]:
        """
        Analyze content for trend opportunities.
        
        Args:
            content_description: Description of the content
            target_platforms: Target platforms
            timeframe_days: Analysis timeframe in days
            
        Returns:
            List of content opportunities
        """
        opportunities = []
        
        for platform in target_platforms:
            platform_trends = self._get_active_trends(platform, timeframe_days)
            
            for trend in platform_trends:
                if self._matches_content(content_description, trend):
                    opportunity = self._create_opportunity(trend, content_description)
                    opportunities.append(opportunity)
        
        # Sort by confidence score
        opportunities.sort(key=lambda x: x.confidence_score, reverse=True)
        
        return opportunities[:5]  # Return top 5 opportunities
    
    def get_viral_patterns(
        self,
        platform: Platform,
        content_type: str = "video"
    ) -> Dict[str, List[str]]:
        """
        Get viral patterns for specific platform and content type.
        
        Args:
            platform: Target platform
            content_type: Type of content
            
        Returns:
            Dictionary of pattern categories with examples
        """
        patterns = self._viral_patterns.get(platform, {})
        
        if content_type in patterns:
            return patterns[content_type]
        
        return patterns.get("general", {})
    
    def get_trending_hashtags(
        self,
        platform: Platform,
        category: Optional[str] = None
    ) -> List[str]:
        """
        Get trending hashtags for platform and category.
        
        Args:
            platform: Target platform
            category: Optional category filter
            
        Returns:
            List of trending hashtags
        """
        platform_trends = self._get_active_trends(platform, 7)
        
        hashtags = []
        for trend in platform_trends:
            if trend.trend_type == TrendType.HASHTAG:
                if not category or category.lower() in trend.name.lower():
                    hashtags.extend(trend.hashtags)
        
        return list(set(hashtags))[:20]  # Return unique hashtags, max 20
    
    def predict_trend_lifecycle(
        self,
        trend_name: str,
        platform: Platform
    ) -> Dict[str, any]:
        """
        Predict the lifecycle of a trend.
        
        Args:
            trend_name: Name of the trend
            platform: Platform where trend is active
            
        Returns:
            Dictionary with lifecycle predictions
        """
        trend = self._find_trend(trend_name, platform)
        
        if not trend:
            return {
                "found": False,
                "message": "Trend not found in database"
            }
        
        # Calculate lifecycle predictions
        peak_date = trend.discovered_at + timedelta(days=trend.duration_days // 2)
        end_date = trend.discovered_at + timedelta(days=trend.duration_days)
        
        return {
            "found": True,
            "trend": trend.name,
            "current_phase": self._get_trend_phase(trend),
            "peak_date": peak_date.isoformat(),
            "end_date": end_date.isoformat(),
            "remaining_days": max(0, (end_date - datetime.utcnow()).days),
            "engagement_trend": "rising" if trend.growth_rate > 0 else "falling",
            "recommendation": self._get_trend_recommendation(trend)
        }
    
    def _get_active_trends(
        self,
        platform: Platform,
        timeframe_days: int
    ) -> List[TrendSignal]:
        """Get active trends for platform within timeframe."""
        cutoff_date = datetime.utcnow() - timedelta(days=timeframe_days)
        
        return [
            trend for trend in self._trend_database
            if trend.platform == platform and trend.discovered_at >= cutoff_date
        ]
    
    def _matches_content(self, content_description: str, trend: TrendSignal) -> bool:
        """Check if content matches trend."""
        content_lower = content_description.lower()
        trend_lower = trend.name.lower() + " " + trend.description.lower()
        
        # Simple keyword matching
        keywords = ["how to", "tutorial", "review", "reaction", "challenge", "funny"]
        
        for keyword in keywords:
            if keyword in content_lower and keyword in trend_lower:
                return True
        
        # Check for topic overlap
        content_words = set(content_lower.split())
        trend_words = set(trend_lower.split())
        
        overlap = content_words.intersection(trend_words)
        return len(overlap) > 2
    
    def _create_opportunity(
        self,
        trend: TrendSignal,
        content_description: str
    ) -> ContentOpportunity:
        """Create content opportunity from trend."""
        
        hook_templates = [
            f"{trend.name} is taking over {trend.platform.value}!",
            f"Here's why {trend.name} is going viral",
            f"Everyone's doing {trend.name}, here's how",
        ]
        
        caption_templates = [
            f"Join the {trend.name} trend! {trend.description}",
            f"{trend.name} 🔥 {trend.description}",
            f"Trying out the {trend.name} trend",
        ]
        
        timing_suggestions = [
            "Post during peak hours (7-9 PM)",
            "Use trending audio for maximum reach",
            "Include relevant hashtags",
        ]
        
        confidence = min(0.9, trend.engagement_score * trend.growth_rate)
        
        return ContentOpportunity(
            trend=trend,
            recommended_format="short_form_video",
            hook_templates=hook_templates,
            caption_templates=caption_templates,
            timing_suggestions=timing_suggestions,
            confidence_score=confidence
        )
    
    def _find_trend(self, trend_name: str, platform: Platform) -> Optional[TrendSignal]:
        """Find trend by name and platform."""
        for trend in self._trend_database:
            if trend.platform == platform and trend.name.lower() == trend_name.lower():
                return trend
        return None
    
    def _get_trend_phase(self, trend: TrendSignal) -> str:
        """Get current phase of trend lifecycle."""
        days_since_discovery = (datetime.utcnow() - trend.discovered_at).days
        
        if days_since_discovery < trend.duration_days * 0.2:
            return "emerging"
        elif days_since_discovery < trend.duration_days * 0.5:
            return "rising"
        elif days_since_discovery < trend.duration_days * 0.8:
            return "peak"
        else:
            return "declining"
    
    def _get_trend_recommendation(self, trend: TrendSignal) -> str:
        """Get recommendation for trend."""
        phase = self._get_trend_phase(trend)
        
        recommendations = {
            "emerging": "Jump in early for maximum growth potential",
            "rising": "Great time to participate, high engagement",
            "peak": "Still good engagement, but competition is high",
            "declining": "Consider if it aligns with your brand"
        }
        
        return recommendations.get(phase, "Monitor trend performance")
    
    def _build_viral_patterns(self) -> Dict[Platform, Dict[str, List[str]]]:
        """Build viral patterns database."""
        return {
            Platform.TIKTOK: {
                "video": {
                    "hooks": [
                        "Wait for it...",
                        "POV:",
                        "Nobody talks about this",
                        "This changes everything",
                    ],
                    "formats": [
                        "Before/after transformation",
                        "Day in the life",
                        "Tutorial/review",
                        "Reaction video",
                    ],
                    "timing": [
                        "First 3 seconds crucial",
                        "15-60 seconds optimal",
                        "Post 7-9 PM for reach",
                    ]
                }
            },
            Platform.INSTAGRAM_REELS: {
                "video": {
                    "hooks": [
                        "You won't believe this",
                        "Here's the secret",
                        "Stop scrolling if...",
                    ],
                    "formats": [
                        "Quick tips",
                        "Behind the scenes",
                        "Product showcase",
                        "Storytelling",
                    ],
                    "timing": [
                        "First 2 seconds matter",
                        "15-30 seconds ideal",
                        "Post multiple times per week",
                    ]
                }
            },
            Platform.YOUTUBE_SHORTS: {
                "video": {
                    "hooks": [
                        "The truth about...",
                        "Why nobody...",
                        "Here's what they don't tell you",
                    ],
                    "formats": [
                        "Educational content",
                        "Entertainment",
                        "How-to guides",
                        "News updates",
                    ],
                    "timing": [
                        "Title and thumbnail crucial",
                        "30-60 seconds optimal",
                        "Consistent posting schedule",
                    ]
                }
            }
        }
    
    def _build_platform_insights(self) -> Dict[Platform, Dict[str, any]]:
        """Build platform-specific insights."""
        return {
            Platform.TIKTOK: {
                "optimal_length": "15-60 seconds",
                "peak_hours": "7-9 PM",
                "engagement_factors": ["music", "hashtags", "trends"],
                "content_types": ["entertainment", "education", "lifestyle"]
            },
            Platform.INSTAGRAM_REELS: {
                "optimal_length": "15-30 seconds",
                "peak_hours": "12-3 PM, 7-9 PM",
                "engagement_factors": ["visuals", "music", "hashtags"],
                "content_types": ["lifestyle", "beauty", "food", "travel"]
            },
            Platform.YOUTUBE_SHORTS: {
                "optimal_length": "30-60 seconds",
                "peak_hours": "2-4 PM, 7-9 PM",
                "engagement_factors": ["title", "thumbnail", "content"],
                "content_types": ["education", "entertainment", "news"]
            }
        }
    
    def _initialize_mock_trends(self) -> None:
        """Initialize mock trend database."""
        mock_trends = [
            TrendSignal(
                trend_type=TrendType.HASHTAG,
                platform=Platform.TIKTOK,
                name="#LearnOnTikTok",
                description="Educational content trend",
                engagement_score=0.8,
                growth_rate=0.15,
                duration_days=14,
                hashtags=["#learnonTikTok", "#education", "#tutorial"]
            ),
            TrendSignal(
                trend_type=TrendType.SOUND,
                platform=Platform.INSTAGRAM_REELS,
                name="Phonk Music Trend",
                description="Phonk music in background",
                engagement_score=0.9,
                growth_rate=0.2,
                duration_days=10,
                hashtags=["#phonk", "#music", "#trend"]
            ),
            TrendSignal(
                trend_type=TrendType.CHALLENGE,
                platform=Platform.YOUTUBE_SHORTS,
                name="30-Day Challenge",
                description="30-day transformation challenges",
                engagement_score=0.7,
                growth_rate=0.1,
                duration_days=21,
                hashtags=["#challenge", "30day", "transformation"]
            )
        ]
        
        self._trend_database.extend(mock_trends)


# Singleton instance
trend_intelligence_engine = TrendIntelligenceEngine()
