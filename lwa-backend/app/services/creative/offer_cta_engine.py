"""
Offer CTA Engine v0

Identifies monetization opportunities and suggests effective calls-to-action
for content conversion and revenue generation.
"""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger("uvicorn.error")


class OfferType(str, Enum):
    """Types of offers and CTAs."""
    
    PRODUCT_SALE = "product_sale"
    SERVICE_BOOKING = "service_booking"
    COURSE_ENROLLMENT = "course_enrollment"
    NEWSLETTER_SIGNUP = "newsletter_signup"
    FREE_TRIAL = "free_trial"
    CONSULTATION_BOOKING = "consultation_booking"
    DOWNLOAD_OFFER = "download_offer"
    WEBINAR_REGISTRATION = "webinar_registration"
    AFFILIATE_LINK = "affiliate_link"
    DONATION = "donation"


class ConversionGoal(str, Enum):
    """Conversion goals for offers."""
    
    LEAD_GENERATION = "lead_generation"
    DIRECT_SALE = "direct_sale"
    BRAND_AWARENESS = "brand_awareness"
    COMMUNITY_BUILDING = "community_building"
    EMAIL_CAPTURE = "email_capture"
    TRAFFIC_DRIVE = "traffic_drive"


class ContentCategory(str, Enum):
    """Content categories for offer matching."""
    
    EDUCATIONAL = "educational"
    ENTERTAINMENT = "entertainment"
    INSPIRATIONAL = "inspirational"
    PROMOTIONAL = "promotional"
    REVIEW = "review"
    TUTORIAL = "tutorial"
    STORYTELLING = "storytelling"


@dataclass
class MonetizationOpportunity:
    """Monetization opportunity for content."""
    
    offer_type: OfferType
    title: str
    description: str
    conversion_goal: ConversionGoal
    value_proposition: str
    urgency_factors: List[str] = field(default_factory=list)
    target_audience: str = "general"
    confidence_score: float = 0.0
    estimated_conversion_rate: float = 0.0


@dataclass
class CallToAction:
    """Call-to-action recommendation."""
    
    text: str
    placement: str  # beginning, middle, end, overlay
    urgency: str  # low, medium, high
    visual_style: str
    button_color: str
    timing: str  # immediate, after_content, end_screen
    follow_up_action: Optional[str] = None


@dataclass
class OfferRecommendation:
    """Complete offer recommendation with CTA."""
    
    opportunity: MonetizationOpportunity
    primary_cta: CallToAction
    secondary_ctas: List[CallToAction] = field(default_factory=list)
    implementation_notes: List[str] = field(default_factory=list)
    tracking_suggestions: List[str] = field(default_factory=list)


class OfferCTAEngine:
    """
    Offer CTA engine for identifying monetization opportunities
    and suggesting effective calls-to-action.
    """
    
    def __init__(self) -> None:
        self._offer_templates = self._build_offer_templates()
        self._cta_patterns = self._build_cta_patterns()
        self._conversion_strategies = self._build_conversion_strategies()
    
    def analyze_monetization_opportunities(
        self,
        content_description: str,
        content_category: ContentCategory,
        target_audience: str = "general",
        platform: str = "tiktok"
    ) -> List[OfferRecommendation]:
        """
        Analyze content for monetization opportunities.
        
        Args:
            content_description: Description of the content
            content_category: Category of the content
            target_audience: Target audience
            platform: Target platform
            
        Returns:
            List of offer recommendations
        """
        opportunities = []
        
        # Identify potential offers based on content
        content_lower = content_description.lower()
        
        # Check for educational content
        if content_category == ContentCategory.EDUCATIONAL:
            opportunities.extend(self._analyze_educational_offers(content_lower, target_audience))
        
        # Check for review content
        if content_category == ContentCategory.REVIEW:
            opportunities.extend(self._analyze_review_offers(content_lower, target_audience))
        
        # Check for tutorial content
        if content_category == ContentCategory.TUTORIAL:
            opportunities.extend(self._analyze_tutorial_offers(content_lower, target_audience))
        
        # Check for inspirational content
        if content_category == ContentCategory.INSPIRATIONAL:
            opportunities.extend(self._analyze_inspirational_offers(content_lower, target_audience))
        
        # Generate CTAs for each opportunity
        recommendations = []
        for opportunity in opportunities:
            cta = self._generate_primary_cta(opportunity, platform)
            secondary_ctas = self._generate_secondary_ctas(opportunity, platform)
            
            recommendation = OfferRecommendation(
                opportunity=opportunity,
                primary_cta=cta,
                secondary_ctas=secondary_ctas,
                implementation_notes=self._get_implementation_notes(opportunity),
                tracking_suggestions=self._get_tracking_suggestions(opportunity)
            )
            
            recommendations.append(recommendation)
        
        # Sort by confidence score
        recommendations.sort(key=lambda x: x.opportunity.confidence_score, reverse=True)
        
        return recommendations[:3]  # Return top 3 recommendations
    
    def generate_effective_cta(
        self,
        offer_type: OfferType,
        content_context: str,
        platform: str = "tiktok",
        urgency_level: str = "medium"
    ) -> CallToAction:
        """
        Generate effective CTA for specific offer type.
        
        Args:
            offer_type: Type of offer
            content_context: Context of the content
            platform: Target platform
            urgency_level: Urgency level (low, medium, high)
            
        Returns:
            Call-to-action recommendation
        """
        
        cta_templates = self._cta_patterns.get(offer_type, {})
        platform_ctas = cta_templates.get(platform, {})
        
        urgency_ctas = platform_ctas.get(urgency_level, [])
        
        if urgency_ctas:
            import random
            cta_text = random.choice(urgency_ctas)
        else:
            cta_text = self._get_default_cta(offer_type)
        
        return CallToAction(
            text=cta_text,
            placement="end",
            urgency=urgency_level,
            visual_style=self._get_visual_style(offer_type, platform),
            button_color=self._get_button_color(offer_type),
            timing="end_screen",
            follow_up_action=self._get_follow_up_action(offer_type)
        )
    
    def optimize_conversion_rate(
        self,
        current_cta: str,
        offer_type: OfferType,
        platform: str,
        performance_data: Optional[Dict[str, float]] = None
    ) -> Dict[str, any]:
        """
        Optimize CTA for better conversion rate.
        
        Args:
            current_cta: Current CTA text
            offer_type: Type of offer
            platform: Target platform
            performance_data: Performance metrics
            
        Returns:
            Optimization suggestions
        """
        suggestions = {
            "text_improvements": [],
            "timing_adjustments": [],
            "visual_enhancements": [],
            "urgency_elements": [],
            "trust_signals": []
        }
        
        # Analyze current CTA
        cta_lower = current_cta.lower()
        
        # Text improvements
        if not any(word in cta_lower for word in ["free", "instant", "limited"]):
            suggestions["text_improvements"].append("Add urgency words like 'limited' or 'instant'")
        
        if "click" not in cta_lower and "tap" not in cta_lower:
            suggestions["text_improvements"].append("Add action words like 'click' or 'tap'")
        
        # Timing adjustments
        suggestions["timing_adjustments"] = [
            "Test CTA at beginning, middle, and end",
            "Consider overlay CTA for mobile platforms",
            "Use end-screen CTA for longer content"
        ]
        
        # Visual enhancements
        suggestions["visual_enhancements"] = [
            "Use contrasting button colors",
            "Add animation to draw attention",
            "Ensure CTA is thumb-friendly for mobile"
        ]
        
        # Urgency elements
        if urgency not in cta_lower:
            suggestions["urgency_elements"] = [
                "Add countdown timer",
                "Include 'limited time' messaging",
                "Show stock/availability status"
            ]
        
        # Trust signals
        suggestions["trust_signals"] = [
            "Add social proof (reviews, testimonials)",
            "Include security badges for payments",
            "Display money-back guarantee"
        ]
        
        return suggestions
    
    def _analyze_educational_offers(
        self,
        content_lower: str,
        target_audience: str
    ) -> List[MonetizationOpportunity]:
        """Analyze educational content for offers."""
        opportunities = []
        
        if any(word in content_lower for word in ["learn", "study", "course", "education"]):
            opportunities.append(MonetizationOpportunity(
                offer_type=OfferType.COURSE_ENROLLMENT,
                title="Premium Course",
                description="Comprehensive course on the topic",
                conversion_goal=ConversionGoal.DIRECT_SALE,
                value_proposition="Deep dive into subject with expert guidance",
                urgency_factors=["limited seats", "early bird pricing"],
                target_audience=target_audience,
                confidence_score=0.8,
                estimated_conversion_rate=0.03
            ))
            
            opportunities.append(MonetizationOpportunity(
                offer_type=OfferType.FREE_TRIAL,
                title="Free Course Preview",
                description="Try before you buy with free lessons",
                conversion_goal=ConversionGoal.LEAD_GENERATION,
                value_proposition="Experience teaching style before committing",
                urgency_factors=["trial period limited"],
                target_audience=target_audience,
                confidence_score=0.7,
                estimated_conversion_rate=0.15
            ))
        
        return opportunities
    
    def _analyze_review_offers(
        self,
        content_lower: str,
        target_audience: str
    ) -> List[MonetizationOpportunity]:
        """Analyze review content for offers."""
        opportunities = []
        
        if any(word in content_lower for word in ["review", "test", "recommendation"]):
            opportunities.append(MonetizationOpportunity(
                offer_type=OfferType.AFFILIATE_LINK,
                title="Product Affiliate",
                description="Earn commission through product recommendations",
                conversion_goal=ConversionGoal.DIRECT_SALE,
                value_proposition="Support the channel while getting great products",
                urgency_factors=["discount codes", "limited time offers"],
                target_audience=target_audience,
                confidence_score=0.6,
                estimated_conversion_rate=0.02
            ))
        
        return opportunities
    
    def _analyze_tutorial_offers(
        self,
        content_lower: str,
        target_audience: str
    ) -> List[MonetizationOpportunity]:
        """Analyze tutorial content for offers."""
        opportunities = []
        
        if any(word in content_lower for word in ["how to", "tutorial", "guide", "step by step"]):
            opportunities.append(MonetizationOpportunity(
                offer_type=OfferType.DOWNLOAD_OFFER,
                title="Resource Download",
                description="Downloadable templates, checklists, or resources",
                conversion_goal=ConversionGoal.EMAIL_CAPTURE,
                value_proposition="Free resources to implement the tutorial",
                urgency_factors=["limited downloads", "exclusive content"],
                target_audience=target_audience,
                confidence_score=0.7,
                estimated_conversion_rate=0.25
            ))
        
        return opportunities
    
    def _analyze_inspirational_offers(
        self,
        content_lower: str,
        target_audience: str
    ) -> List[MonetizationOpportunity]:
        """Analyze inspirational content for offers."""
        opportunities = []
        
        if any(word in content_lower for word in ["inspiration", "motivation", "success", "journey"]):
            opportunities.append(MonetizationOpportunity(
                offer_type=OfferType.NEWSLETTER_SIGNUP,
                title="Inspiration Newsletter",
                description="Daily or weekly inspiration and motivation",
                conversion_goal=ConversionGoal.EMAIL_CAPTURE,
                value_proposition="Regular motivation delivered to your inbox",
                urgency_factors=["exclusive content for subscribers"],
                target_audience=target_audience,
                confidence_score=0.6,
                estimated_conversion_rate=0.20
            ))
        
        return opportunities
    
    def _generate_primary_cta(
        self,
        opportunity: MonetizationOpportunity,
        platform: str
    ) -> CallToAction:
        """Generate primary CTA for opportunity."""
        
        cta_mapping = {
            OfferType.COURSE_ENROLLMENT: "Enroll Now - Limited Spots",
            OfferType.FREE_TRIAL: "Start Free Trial",
            OfferType.AFFILIATE_LINK: "Get This Deal",
            OfferType.DOWNLOAD_OFFER: "Download Free",
            OfferType.NEWSLETTER_SIGNUP: "Subscribe for More"
        }
        
        cta_text = cta_mapping.get(opportunity.offer_type, "Learn More")
        
        return CallToAction(
            text=cta_text,
            placement="end",
            urgency="medium",
            visual_style="button",
            button_color=self._get_button_color(opportunity.offer_type),
            timing="end_screen"
        )
    
    def _generate_secondary_ctas(
        self,
        opportunity: MonetizationOpportunity,
        platform: str
    ) -> List[CallToAction]:
        """Generate secondary CTAs for opportunity."""
        secondary_ctas = []
        
        # Add newsletter signup as secondary CTA for most offers
        if opportunity.offer_type != OfferType.NEWSLETTER_SIGNUP:
            secondary_ctas.append(CallToAction(
                text="Get Free Tips",
                placement="middle",
                urgency="low",
                visual_style="text",
                button_color="blue",
                timing="after_content"
            ))
        
        return secondary_ctas
    
    def _get_implementation_notes(self, opportunity: MonetizationOpportunity) -> List[str]:
        """Get implementation notes for opportunity."""
        notes = []
        
        if opportunity.offer_type == OfferType.COURSE_ENROLLMENT:
            notes.extend([
                "Add course preview clips",
                "Include student testimonials",
                "Show course curriculum highlights"
            ])
        elif opportunity.offer_type == OfferType.AFFILIATE_LINK:
            notes.extend([
                "Disclose affiliate relationship",
                "Show product in use",
                "Include discount code if available"
            ])
        
        return notes
    
    def _get_tracking_suggestions(self, opportunity: MonetizationOpportunity) -> List[str]:
        """Get tracking suggestions for opportunity."""
        return [
            "Use UTM parameters for tracking",
            "Set up conversion pixels",
            "Track click-through rates",
            "Monitor conversion funnels"
        ]
    
    def _get_default_cta(self, offer_type: OfferType) -> str:
        """Get default CTA for offer type."""
        defaults = {
            OfferType.PRODUCT_SALE: "Buy Now",
            OfferType.SERVICE_BOOKING: "Book Now",
            OfferType.COURSE_ENROLLMENT: "Enroll Now",
            OfferType.NEWSLETTER_SIGNUP: "Subscribe",
            OfferType.FREE_TRIAL: "Try Free",
            OfferType.DOWNLOAD_OFFER: "Download",
            OfferType.WEBINAR_REGISTRATION: "Register",
            OfferType.AFFILIATE_LINK: "Shop Now",
            OfferType.DONATION: "Donate"
        }
        
        return defaults.get(offer_type, "Learn More")
    
    def _get_visual_style(self, offer_type: OfferType, platform: str) -> str:
        """Get visual style for CTA."""
        if platform == "tiktok":
            return "overlay_text"
        elif platform == "instagram_reels":
            return "button"
        else:
            return "button"
    
    def _get_button_color(self, offer_type: OfferType) -> str:
        """Get button color for offer type."""
        colors = {
            OfferType.PRODUCT_SALE: "red",
            OfferType.SERVICE_BOOKING: "blue",
            OfferType.COURSE_ENROLLMENT: "purple",
            OfferType.NEWSLETTER_SIGNUP: "green",
            OfferType.FREE_TRIAL: "orange",
            OfferType.DOWNLOAD_OFFER: "blue",
            OfferType.WEBINAR_REGISTRATION: "purple",
            OfferType.AFFILIATE_LINK: "yellow",
            OfferType.DONATION: "green"
        }
        
        return colors.get(offer_type, "blue")
    
    def _get_follow_up_action(self, offer_type: OfferType) -> Optional[str]:
        """Get follow-up action for offer type."""
        follow_ups = {
            OfferType.COURSE_ENROLLMENT: "Send welcome email",
            OfferType.NEWSLETTER_SIGNUP: "Send confirmation email",
            OfferType.FREE_TRIAL: "Schedule onboarding call",
            OfferType.DOWNLOAD_OFFER: "Send resource via email"
        }
        
        return follow_ups.get(offer_type)
    
    def _build_offer_templates(self) -> Dict[str, Dict[str, any]]:
        """Build offer templates database."""
        return {
            "educational": {
                "course": {
                    "title": "Comprehensive Course",
                    "description": "Deep dive into subject",
                    "price_range": "$97-$997"
                },
                "workshop": {
                    "title": "Live Workshop",
                    "description": "Interactive learning session",
                    "price_range": "$47-$297"
                }
            },
            "tools": {
                "software": {
                    "title": "Premium Software",
                    "description": "Professional tool",
                    "price_range": "$29-$199/month"
                },
                "template": {
                    "title": "Template Pack",
                    "description": "Ready-to-use templates",
                    "price_range": "$27-$97"
                }
            }
        }
    
    def _build_cta_patterns(self) -> Dict[OfferType, Dict[str, Dict[str, List[str]]]]:
        """Build CTA patterns database."""
        return {
            OfferType.COURSE_ENROLLMENT: {
                "tiktok": {
                    "high": ["Enroll Now - Only 3 Spots Left!", "Join Course - Price Increases Tonight"],
                    "medium": ["Learn More - Free Preview", "Enroll in Course"],
                    "low": ["Explore Course", "See Curriculum"]
                }
            },
            OfferType.NEWSLETTER_SIGNUP: {
                "tiktok": {
                    "high": ["Subscribe - Exclusive Content!", "Join List - Free Gift Inside"],
                    "medium": ["Get Tips Weekly", "Subscribe for Updates"],
                    "low": ["Follow for More", "See More Content"]
                }
            }
        }
    
    def _build_conversion_strategies(self) -> Dict[str, List[str]]:
        """Build conversion strategies database."""
        return {
            "urgency": ["limited time", "limited spots", "price increase", "exclusive"],
            "trust": ["guarantee", "testimonials", "social proof", "security"],
            "value": ["free bonus", "discount", "premium content", "expert access"],
            "simplicity": ["one click", "instant access", "easy signup", "quick start"]
        }


# Singleton instance
offer_cta_engine = OfferCTAEngine()
