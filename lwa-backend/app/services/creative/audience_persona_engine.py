"""
Audience Persona Engine v0

Identifies target audiences and personalizes content recommendations
for maximum engagement and conversion.
"""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger("uvicorn.error")


class AudienceType(str, Enum):
    """Types of audience personas."""
    
    GENERAL_CONSUMER = "general_consumer"
    CREATIVE_PROFESSIONAL = "creative_professional"
    BUSINESS_OWNER = "business_owner"
    STUDENT = "student"
    ENTREPRENEUR = "entrepreneur"
    INFLUENCER = "influencer"
    TECH_ENTHUSIAST = "tech_enthusiast"
    WELLNESS_SEEKER = "wellness_seeker"
    GAMER = "gamer"
    PARENT = "parent"


class ContentGoal(str, Enum):
    """Content goals for audience targeting."""
    
    ENTERTAINMENT = "entertainment"
    EDUCATION = "education"
    INSPIRATION = "inspiration"
    CONVERSION = "conversion"
    COMMUNITY = "community"
    AWARENESS = "awareness"


class Platform(str, Enum):
    """Social media platforms."""
    
    TIKTOK = "tiktok"
    INSTAGRAM_REELS = "instagram_reels"
    YOUTUBE_SHORTS = "youtube_shorts"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"


@dataclass
class AudiencePersona:
    """Audience persona definition."""
    
    persona_type: AudienceType
    name: str
    description: str
    demographics: Dict[str, any] = field(default_factory=dict)
    interests: List[str] = field(default_factory=list)
    pain_points: List[str] = field(default_factory=list)
    motivations: List[str] = field(default_factory=list)
    preferred_platforms: List[Platform] = field(default_factory=list)
    content_preferences: Dict[str, List[str]] = field(default_factory=dict)
    engagement_patterns: Dict[str, any] = field(default_factory=dict)


@dataclass
class PersonalizedRecommendation:
    """Personalized content recommendation."""
    
    target_persona: AudienceType
    content_hook: str
    caption_style: str
    call_to_action: str
    recommended_platforms: List[Platform]
    optimal_timing: List[str]
    content_format: str
    tone: str
    key_topics: List[str] = field(default_factory=list)


class AudiencePersonaEngine:
    """
    Audience persona engine for identifying target audiences
    and personalizing content recommendations.
    """
    
    def __init__(self) -> None:
        self._persona_database: Dict[AudienceType, AudiencePersona] = {}
        self._content_strategies = self._build_content_strategies()
        self._initialize_personas()
    
    def identify_target_audience(
        self,
        content_description: str,
        content_goal: ContentGoal,
        target_platforms: Optional[List[Platform]] = None
    ) -> List[AudienceType]:
        """
        Identify target audiences for content.
        
        Args:
            content_description: Description of the content
            content_goal: Goal of the content
            target_platforms: Target platforms (optional)
            
        Returns:
            List of suitable audience types
        """
        suitable_audiences = []
        
        for persona_type, persona in self._persona_database.items():
            if self._matches_content(content_description, persona, content_goal):
                if not target_platforms or any(p in persona.preferred_platforms for p in target_platforms):
                    suitable_audiences.append(persona_type)
        
        return suitable_audiences
    
    def generate_personalized_content(
        self,
        target_persona: AudienceType,
        content_description: str,
        content_goal: ContentGoal,
        platform: Platform
    ) -> PersonalizedRecommendation:
        """
        Generate personalized content recommendations.
        
        Args:
            target_persona: Target audience persona
            content_description: Description of the content
            content_goal: Goal of the content
            platform: Target platform
            
        Returns:
            Personalized content recommendation
        """
        persona = self._persona_database.get(target_persona)
        if not persona:
            raise ValueError(f"Persona not found: {target_persona}")
        
        # Generate personalized content based on persona
        hook = self._generate_hook(persona, content_description, content_goal)
        caption_style = self._generate_caption_style(persona, platform)
        call_to_action = self._generate_cta(persona, content_goal)
        content_format = self._determine_content_format(persona, platform)
        tone = self._determine_tone(persona, content_goal)
        key_topics = self._extract_key_topics(persona, content_description)
        
        return PersonalizedRecommendation(
            target_persona=target_persona,
            content_hook=hook,
            caption_style=caption_style,
            call_to_action=call_to_action,
            recommended_platforms=[platform],
            optimal_timing=persona.engagement_patterns.get("optimal_times", []),
            content_format=content_format,
            tone=tone,
            key_topics=key_topics
        )
    
    def get_audience_insights(
        self,
        persona_type: AudienceType
    ) -> Dict[str, any]:
        """
        Get detailed insights about an audience persona.
        
        Args:
            persona_type: Audience persona type
            
        Returns:
            Dictionary with audience insights
        """
        persona = self._persona_database.get(persona_type)
        if not persona:
            return {"error": "Persona not found"}
        
        return {
            "persona": persona.name,
            "description": persona.description,
            "demographics": persona.demographics,
            "interests": persona.interests,
            "pain_points": persona.pain_points,
            "motivations": persona.motivations,
            "preferred_platforms": [p.value for p in persona.preferred_platforms],
            "content_preferences": persona.content_preferences,
            "engagement_patterns": persona.engagement_patterns
        }
    
    def optimize_content_for_audience(
        self,
        content: str,
        target_persona: AudienceType,
        platform: Platform
    ) -> Dict[str, any]:
        """
        Optimize existing content for target audience.
        
        Args:
            content: Existing content
            target_persona: Target audience persona
            platform: Target platform
            
        Returns:
            Dictionary with optimization suggestions
        """
        persona = self._persona_database.get(target_persona)
        if not persona:
            return {"error": "Persona not found"}
        
        suggestions = {
            "hook_improvements": [],
            "caption_enhancements": [],
            "timing_recommendations": [],
            "format_suggestions": [],
            "topic_adjustments": []
        }
        
        # Analyze content and provide suggestions
        content_lower = content.lower()
        
        # Hook improvements
        if not any(word in content_lower for word in ["wait", "stop", "you won't"]):
            suggestions["hook_improvements"].append("Add attention-grabbing opening")
        
        # Caption enhancements
        if len(content.split()) < 20:
            suggestions["caption_enhancements"].append("Add more descriptive content")
        
        # Timing recommendations
        optimal_times = persona.engagement_patterns.get("optimal_times", [])
        if optimal_times:
            suggestions["timing_recommendations"] = optimal_times
        
        # Format suggestions
        platform_formats = persona.content_preferences.get(platform.value, [])
        if platform_formats:
            suggestions["format_suggestions"] = platform_formats
        
        return suggestions
    
    def _matches_content(
        self,
        content_description: str,
        persona: AudiencePersona,
        content_goal: ContentGoal
    ) -> bool:
        """Check if content matches persona and goal."""
        content_lower = content_description.lower()
        
        # Check interests match
        for interest in persona.interests:
            if interest.lower() in content_lower:
                return True
        
        # Check pain points match
        for pain_point in persona.pain_points:
            if pain_point.lower() in content_lower:
                return True
        
        # Check motivations match
        for motivation in persona.motivations:
            if motivation.lower() in content_lower:
                return True
        
        return False
    
    def _generate_hook(
        self,
        persona: AudiencePersona,
        content_description: str,
        content_goal: ContentGoal
    ) -> str:
        """Generate personalized hook for persona."""
        
        hooks = {
            AudienceType.GENERAL_CONSUMER: [
                "You won't believe this simple trick",
                "Here's what everyone's missing",
                "Stop scrolling if you want to know"
            ],
            AudienceType.CREATIVE_PROFESSIONAL: [
                "The secret tool creatives are using",
                "Level up your creative workflow",
                "Here's how the pros do it"
            ],
            AudienceType.BUSINESS_OWNER: [
                "This strategy changed my business",
                "The ROI you've been looking for",
                "Stop making this business mistake"
            ],
            AudienceType.STUDENT: [
                "Study hack you need right now",
                "Ace your exams with this method",
                "What teachers don't tell you"
            ]
        }
        
        persona_hooks = hooks.get(persona.persona_type, [
            "You need to see this",
            "Here's something important",
            "Don't miss this"
        ])
        
        # Return most relevant hook based on content
        import random
        return random.choice(persona_hooks)
    
    def _generate_caption_style(
        self,
        persona: AudiencePersona,
        platform: Platform
    ) -> str:
        """Generate caption style for persona and platform."""
        
        styles = {
            AudienceType.GENERAL_CONSUMER: "Casual, engaging, with emojis",
            AudienceType.CREATIVE_PROFESSIONAL: "Professional, insightful, value-focused",
            AudienceType.BUSINESS_OWNER: "Results-oriented, actionable, data-driven",
            AudienceType.STUDENT: "Educational, helpful, step-by-step"
        }
        
        return styles.get(persona.persona_type, "Engaging and informative")
    
    def _generate_cta(
        self,
        persona: AudiencePersona,
        content_goal: ContentGoal
    ) -> str:
        """Generate call-to-action for persona and goal."""
        
        cta_mapping = {
            ContentGoal.ENTERTAINMENT: "Share with someone who needs a laugh",
            ContentGoal.EDUCATION: "Save this for later",
            ContentGoal.INSPIRATION: "Follow for more motivation",
            ContentGoal.CONVERSION: "Click link in bio",
            ContentGoal.COMMUNITY: "Join the conversation below",
            ContentGoal.AWARENESS: "Like and share to spread the word"
        }
        
        return cta_mapping.get(content_goal, "Engage with this content")
    
    def _determine_content_format(
        self,
        persona: AudiencePersona,
        platform: Platform
    ) -> str:
        """Determine best content format for persona and platform."""
        
        platform_formats = persona.content_preferences.get(platform.value, [])
        return platform_formats[0] if platform_formats else "short_form_video"
    
    def _determine_tone(
        self,
        persona: AudiencePersona,
        content_goal: ContentGoal
    ) -> str:
        """Determine content tone for persona and goal."""
        
        tones = {
            AudienceType.GENERAL_CONSUMER: "Friendly and relatable",
            AudienceType.CREATIVE_PROFESSIONAL: "Expert and helpful",
            AudienceType.BUSINESS_OWNER: "Confident and authoritative",
            AudienceType.STUDENT: "Encouraging and supportive"
        }
        
        return tones.get(persona.persona_type, "Engaging and authentic")
    
    def _extract_key_topics(
        self,
        persona: AudiencePersona,
        content_description: str
    ) -> List[str]:
        """Extract key topics from content based on persona interests."""
        content_lower = content_description.lower()
        key_topics = []
        
        for interest in persona.interests:
            if interest.lower() in content_lower:
                key_topics.append(interest)
        
        return key_topics[:3]  # Return top 3 topics
    
    def _build_content_strategies(self) -> Dict[str, Dict[str, any]]:
        """Build content strategies database."""
        return {
            "hook_patterns": {
                "question": "Have you ever wondered...",
                "shock": "You won't believe...",
                "curiosity": "Here's what nobody tells you...",
                "benefit": "The secret to achieving...",
                "urgency": "Stop what you're doing and..."
            },
            "caption_structures": {
                "problem_solution": "Problem → Solution → Result",
                "storytelling": "Hook → Story → Lesson → CTA",
                "educational": "What → Why → How → Next steps",
                "entertainment": "Setup → Punchline → Engagement"
            }
        }
    
    def _initialize_personas(self) -> None:
        """Initialize audience persona database."""
        
        # General Consumer
        general_consumer = AudiencePersona(
            persona_type=AudienceType.GENERAL_CONSUMER,
            name="General Consumer",
            description="Broad audience seeking entertainment and useful information",
            demographics={"age_range": "18-65", "locations": "Global"},
            interests=["entertainment", "lifestyle", "trends", "life hacks"],
            pain_points=["time management", "information overload", "decision making"],
            motivations=["convenience", "entertainment", "self-improvement"],
            preferred_platforms=[Platform.TIKTOK, Platform.INSTAGRAM_REELS],
            content_preferences={
                "tiktok": ["entertainment", "trends", "life hacks"],
                "instagram_reels": ["lifestyle", "inspiration", "tutorials"]
            },
            engagement_patterns={"optimal_times": ["7-9 PM"], "engagement_rate": "high"}
        )
        
        # Creative Professional
        creative_professional = AudiencePersona(
            persona_type=AudienceType.CREATIVE_PROFESSIONAL,
            name="Creative Professional",
            description="Designers, artists, content creators seeking tools and techniques",
            demographics={"age_range": "22-45", "locations": "Urban areas"},
            interests=["design", "art", "technology", "creativity", "tools"],
            pain_points=["creative blocks", "tool limitations", "client management"],
            motivations=["skill improvement", "efficiency", "inspiration"],
            preferred_platforms=[Platform.INSTAGRAM_REELS, Platform.YOUTUBE_SHORTS],
            content_preferences={
                "instagram_reels": ["tutorials", "behind the scenes", "tool reviews"],
                "youtube_shorts": ["education", "techniques", "industry insights"]
            },
            engagement_patterns={"optimal_times": ["12-3 PM", "7-9 PM"], "engagement_rate": "medium"}
        )
        
        # Business Owner
        business_owner = AudiencePersona(
            persona_type=AudienceType.BUSINESS_OWNER,
            name="Business Owner",
            description="Entrepreneurs and business leaders seeking growth strategies",
            demographics={"age_range": "25-55", "locations": "Global"},
            interests=["business", "marketing", "finance", "technology", "growth"],
            pain_points=["time constraints", "competition", "scaling challenges"],
            motivations=["profitability", "growth", "efficiency"],
            preferred_platforms=[Platform.LINKEDIN, Platform.YOUTUBE_SHORTS],
            content_preferences={
                "linkedin": ["business insights", "leadership", "industry trends"],
                "youtube_shorts": ["business tips", "strategies", "case studies"]
            },
            engagement_patterns={"optimal_times": ["9-11 AM", "2-4 PM"], "engagement_rate": "medium"}
        )
        
        # Student
        student = AudiencePersona(
            persona_type=AudienceType.STUDENT,
            name="Student",
            description="Students seeking educational content and study tips",
            demographics={"age_range": "16-25", "locations": "Global"},
            interests=["education", "study techniques", "career", "technology"],
            pain_points=["time management", "exam stress", "information retention"],
            motivations=["academic success", "career preparation", "efficiency"],
            preferred_platforms=[Platform.TIKTOK, Platform.YOUTUBE_SHORTS],
            content_preferences={
                "tiktok": ["study hacks", "exam tips", "motivation"],
                "youtube_shorts": ["education", "tutorials", "career advice"]
            },
            engagement_patterns={"optimal_times": ["3-6 PM", "8-10 PM"], "engagement_rate": "high"}
        )
        
        self._persona_database = {
            AudienceType.GENERAL_CONSUMER: general_consumer,
            AudienceType.CREATIVE_PROFESSIONAL: creative_professional,
            AudienceType.BUSINESS_OWNER: business_owner,
            AudienceType.STUDENT: student
        }


# Singleton instance
audience_persona_engine = AudiencePersonaEngine()
