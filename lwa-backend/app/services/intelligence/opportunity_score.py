"""
Opportunity Score Algorithm v0

Calculates opportunity scores for content based on market potential,
engagement likelihood, and creator value. Used by the Opportunity Engine
to prioritize high-value opportunities for creators.
"""

import logging
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


@dataclass
class OpportunityScoreResult:
    """Result of opportunity score calculation."""
    
    overall_score: float  # 0-100
    market_potential: float
    engagement_likelihood: float
    creator_value: float
    trend_alignment: float
    competition_gap: float
    
    # Detailed breakdown
    factors: Dict[str, float]
    opportunities: List[str]
    risks: List[str]
    recommendations: List[str]
    confidence: float
    timestamp: datetime


@dataclass
class MarketTrend:
    """Market trend data for opportunity analysis."""
    
    trend_name: str
    growth_rate: float
    market_size: float
    competition_level: float
    engagement_rate: float
    monetization_potential: float


class OpportunityScoreCalculator:
    """
    Calculates comprehensive opportunity scores for content.
    
    Evaluates market potential, engagement likelihood, creator value,
    trend alignment, and competition gap to identify high-value opportunities.
    """
    
    def __init__(self):
        self.opportunity_factors = {
            "market_potential": 0.30,
            "engagement_likelihood": 0.25,
            "creator_value": 0.20,
            "trend_alignment": 0.15,
            "competition_gap": 0.10,
        }
        
        # Market trends database (simplified)
        self.market_trends = {
            "short_form_video": MarketTrend(
                "Short-form Video", 0.85, 50000000000, 0.7, 0.12, 0.8
            ),
            "educational_content": MarketTrend(
                "Educational Content", 0.65, 25000000000, 0.5, 0.08, 0.7
            ),
            "entertainment": MarketTrend(
                "Entertainment", 0.75, 75000000000, 0.8, 0.15, 0.6
            ),
            "how_to_tutorials": MarketTrend(
                "How-to Tutorials", 0.70, 30000000000, 0.6, 0.10, 0.75
            ),
            "product_reviews": MarketTrend(
                "Product Reviews", 0.60, 20000000000, 0.7, 0.09, 0.85
            ),
        }
        
        # High-opportunity keywords
        self.opportunity_keywords = {
            "high_value": [
                "tutorial", "review", "how to", "guide", "tips", "tricks",
                "secret", "hack", "method", "technique", "strategy"
            ],
            "trending": [
                "viral", "trending", "popular", "new", "latest", "breaking",
                "exclusive", "behind the scenes", "first look", "reveal"
            ],
            "engagement": [
                "challenge", "reaction", "comparison", "test", "experiment",
                "try", "experience", "journey", "transformation", "before after"
            ],
        }
        
        # Platform-specific opportunities
        self.platform_opportunities = {
            "tiktok": {
                "trending_sounds": 0.8,
                "challenges": 0.9,
                "duets": 0.7,
                "stitch": 0.6,
                "short_form": 0.9,
            },
            "instagram": {
                "reels": 0.8,
                "stories": 0.7,
                "carousels": 0.6,
                "igtv": 0.5,
                "shopping": 0.8,
            },
            "youtube": {
                "shorts": 0.8,
                "premiere": 0.6,
                "community": 0.7,
                "membership": 0.7,
                "superchat": 0.6,
            },
        }
    
    async def calculate_opportunity_score(
        self,
        content: Dict[str, Any],
        market_data: Optional[Dict[str, Any]] = None,
        creator_profile: Optional[Dict[str, Any]] = None,
        platform_data: Optional[Dict[str, Any]] = None
    ) -> OpportunityScoreResult:
        """
        Calculate comprehensive opportunity score for content.
        
        Args:
            content: Content data including text, metadata, category
            market_data: Market and trend information
            creator_profile: Creator's profile and history
            platform_data: Platform-specific data and opportunities
            
        Returns:
            OpportunityScoreResult with detailed breakdown
        """
        
        try:
            # Extract content features
            text_content = content.get("text", "")
            category = content.get("category", "")
            tags = content.get("tags", [])
            metadata = content.get("metadata", {})
            
            # Calculate individual factor scores
            market_potential = await self._calculate_market_potential(
                content, market_data or {}
            )
            
            engagement_likelihood = await self._calculate_engagement_likelihood(
                content, platform_data or {}
            )
            
            creator_value = await self._calculate_creator_value(
                content, creator_profile or {}
            )
            
            trend_alignment = await self._calculate_trend_alignment(
                content, market_data or {}
            )
            
            competition_gap = await self._calculate_competition_gap(
                content, market_data or {}
            )
            
            # Calculate weighted overall score
            overall_score = (
                market_potential * self.opportunity_factors["market_potential"] +
                engagement_likelihood * self.opportunity_factors["engagement_likelihood"] +
                creator_value * self.opportunity_factors["creator_value"] +
                trend_alignment * self.opportunity_factors["trend_alignment"] +
                competition_gap * self.opportunity_factors["competition_gap"]
            )
            
            # Generate opportunities and risks
            opportunities = await self._identify_opportunities(
                content, market_data or {}, platform_data or {}
            )
            
            risks = await self._identify_risks(
                content, market_data or {}, creator_profile or {}
            )
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(
                overall_score, opportunities, risks
            )
            
            # Collect all factors
            factors = {
                "market_potential": market_potential,
                "engagement_likelihood": engagement_likelihood,
                "creator_value": creator_value,
                "trend_alignment": trend_alignment,
                "competition_gap": competition_gap,
            }
            
            # Calculate confidence
            confidence = await self._calculate_confidence(factors, content)
            
            return OpportunityScoreResult(
                overall_score=round(overall_score, 2),
                market_potential=round(market_potential, 2),
                engagement_likelihood=round(engagement_likelihood, 2),
                creator_value=round(creator_value, 2),
                trend_alignment=round(trend_alignment, 2),
                competition_gap=round(competition_gap, 2),
                factors=factors,
                opportunities=opportunities,
                risks=risks,
                recommendations=recommendations,
                confidence=round(confidence, 2),
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Opportunity score calculation failed: {e}")
            return OpportunityScoreResult(
                overall_score=0.0,
                market_potential=0.0,
                engagement_likelihood=0.0,
                creator_value=0.0,
                trend_alignment=0.0,
                competition_gap=0.0,
                factors={},
                opportunities=[f"Calculation error: {str(e)}"],
                risks=[],
                recommendations=[],
                confidence=0.0,
                timestamp=datetime.utcnow()
            )
    
    async def _calculate_market_potential(
        self, content: Dict[str, Any], market_data: Dict[str, Any]
    ) -> float:
        """Calculate market potential score."""
        
        score = 50.0  # Base score
        
        # Category alignment with market trends
        category = content.get("category", "").lower()
        
        for trend_name, trend in self.market_trends.items():
            if trend_name.lower() in category:
                score += trend.growth_rate * 30.0
                score += (trend.engagement_rate - 0.1) * 20.0
                score += trend.monetization_potential * 15.0
                break
        
        # Market size factor
        market_size = market_data.get("market_size", 0)
        if market_size > 1000000000:  # > 1B
            score += 10.0
        elif market_size > 100000000:  # > 100M
            score += 5.0
        
        # Growth rate
        growth_rate = market_data.get("growth_rate", 0.0)
        score += growth_rate * 25.0
        
        # Seasonality (lower seasonality = more consistent opportunity)
        seasonality = market_data.get("seasonality_score", 0.5)
        score += (1.0 - seasonality) * 10.0
        
        # Geographic reach
        geographic_reach = market_data.get("geographic_reach", 0.5)
        score += geographic_reach * 10.0
        
        return max(0.0, min(100.0, score))
    
    async def _calculate_engagement_likelihood(
        self, content: Dict[str, Any], platform_data: Dict[str, Any]
    ) -> float:
        """Calculate engagement likelihood score."""
        
        score = 50.0  # Base score
        
        text_content = content.get("text", "")
        platform = platform_data.get("platform", "").lower()
        
        # Platform-specific engagement factors
        if platform in self.platform_opportunities:
            platform_ops = self.platform_opportunities[platform]
            
            # Check for platform-specific features
            if any(feature in text_content.lower() for feature in ["sound", "audio", "music"]) and platform == "tiktok":
                score += platform_ops["trending_sounds"] * 15.0
            
            if "challenge" in text_content.lower():
                score += platform_ops.get("challenges", 0.5) * 15.0
            
            if platform == "tiktok" and len(text_content.split()) < 50:  # Short text for TikTok
                score += 10.0
        
        # Content type engagement
        content_type = content.get("type", "").lower()
        high_engagement_types = ["tutorial", "review", "reaction", "challenge", "experiment"]
        if any(ctype in content_type for ctype in high_engagement_types):
            score += 15.0
        
        # Opportunity keywords
        keyword_score = 0
        for category, keywords in self.opportunity_keywords.items():
            matches = sum(1 for keyword in keywords if keyword in text_content.lower())
            keyword_score += matches * 5.0
        
        score += min(keyword_score, 25.0)
        
        # Emotional content (higher engagement)
        sentiment = content.get("sentiment_score", 0.0)
        if abs(sentiment) > 0.5:  # Strong sentiment
            score += 10.0
        
        # Call-to-action presence
        if any(cta in text_content.lower() for cta in ["comment", "share", "like", "follow", "subscribe"]):
            score += 8.0
        
        # Question-based content (encourages engagement)
        if "?" in text_content:
            score += 5.0
        
        return max(0.0, min(100.0, score))
    
    async def _calculate_creator_value(
        self, content: Dict[str, Any], creator_profile: Dict[str, Any]
    ) -> float:
        """Calculate creator value score."""
        
        score = 50.0  # Base score
        
        # Creator expertise alignment
        creator_expertise = creator_profile.get("expertise_areas", [])
        content_category = content.get("category", "")
        
        if any(expertise.lower() in content_category.lower() for expertise in creator_expertise):
            score += 20.0
        
        # Audience match
        creator_audience = creator_profile.get("audience_demographics", {})
        content_target = content.get("target_audience", {})
        
        # Simple audience match calculation
        match_score = 0
        for key in ["age_range", "interests", "location"]:
            if key in creator_audience and key in content_target:
                if creator_audience[key] == content_target[key]:
                    match_score += 10.0
        
        score += min(match_score, 25.0)
        
        # Historical performance
        avg_engagement = creator_profile.get("average_engagement_rate", 0.05)
        if avg_engagement > 0.15:  # High engagement
            score += 15.0
        elif avg_engagement > 0.08:  # Above average
            score += 10.0
        elif avg_engagement > 0.05:  # Average
            score += 5.0
        
        # Content frequency
        content_frequency = creator_profile.get("content_frequency", 0)  # posts per week
        if content_frequency >= 7:  # Daily content
            score += 10.0
        elif content_frequency >= 3:  # Regular content
            score += 5.0
        
        # Monetization history
        monetization_success = creator_profile.get("monetization_success_rate", 0.0)
        score += monetization_success * 15.0
        
        return max(0.0, min(100.0, score))
    
    async def _calculate_trend_alignment(
        self, content: Dict[str, Any], market_data: Dict[str, Any]
    ) -> float:
        """Calculate trend alignment score."""
        
        score = 50.0  # Base score
        
        text_content = content.get("text", "").lower()
        tags = [tag.lower() for tag in content.get("tags", [])]
        
        # Check for trending keywords
        trending_keywords = market_data.get("trending_keywords", [])
        trend_matches = sum(1 for keyword in trending_keywords if keyword in text_content or keyword in tags)
        score += trend_matches * 8.0
        
        # Hashtag alignment
        hashtags = market_data.get("trending_hashtags", [])
        hashtag_matches = sum(1 for hashtag in hashtags if hashtag in text_content or hashtag in tags)
        score += hashtag_matches * 6.0
        
        # Format alignment
        trending_formats = market_data.get("trending_formats", [])
        content_format = content.get("format", "")
        if content_format in trending_formats:
            score += 15.0
        
        # Topic alignment
        trending_topics = market_data.get("trending_topics", [])
        content_topic = content.get("topic", "")
        if content_topic in trending_topics:
            score += 12.0
        
        # Timing alignment
        optimal_timing = market_data.get("optimal_posting_time", "")
        current_time = datetime.utcnow().hour
        if optimal_timing and str(current_time) in optimal_timing:
            score += 8.0
        
        return max(0.0, min(100.0, score))
    
    async def _calculate_competition_gap(
        self, content: Dict[str, Any], market_data: Dict[str, Any]
    ) -> float:
        """Calculate competition gap score (lower competition = higher opportunity)."""
        
        score = 50.0  # Base score
        
        # Competition level
        competition_level = market_data.get("competition_level", 0.5)
        score += (1.0 - competition_level) * 30.0
        
        # Market saturation
        saturation = market_data.get("market_saturation", 0.5)
        score += (1.0 - saturation) * 20.0
        
        # Content uniqueness
        content_uniqueness = market_data.get("content_uniqueness_score", 0.5)
        score += content_uniqueness * 25.0
        
        # Niche specificity
        niche_specificity = content.get("niche_specificity", 0.5)
        score += niche_specificity * 15.0
        
        # Entry barriers
        entry_barriers = market_data.get("entry_barriers", 0.5)
        score += (1.0 - entry_barriers) * 10.0
        
        return max(0.0, min(100.0, score))
    
    async def _identify_opportunities(
        self, content: Dict[str, Any], market_data: Dict[str, Any], platform_data: Dict[str, Any]
    ) -> List[str]:
        """Identify specific opportunities for the content."""
        
        opportunities = []
        
        text_content = content.get("text", "").lower()
        category = content.get("category", "")
        
        # Market opportunities
        if market_data.get("growth_rate", 0) > 0.7:
            opportunities.append(f"High-growth market in {category}")
        
        if market_data.get("monetization_potential", 0) > 0.8:
            opportunities.append("Strong monetization potential")
        
        # Platform opportunities
        platform = platform_data.get("platform", "")
        if platform == "tiktok" and len(text_content.split()) < 60:
            opportunities.append("Optimal length for TikTok algorithm")
        
        if platform == "instagram" and any(word in text_content for word in ["tutorial", "guide"]):
            opportunities.append("Educational content performs well on Instagram Reels")
        
        # Content opportunities
        if "tutorial" in text_content:
            opportunities.append("Tutorial content has high shareability")
        
        if "review" in text_content:
            opportunities.append("Review content drives affiliate revenue")
        
        if any(word in text_content for word in ["challenge", "experiment"]):
            opportunities.append("Challenge content encourages user participation")
        
        # Trend opportunities
        trending_keywords = market_data.get("trending_keywords", [])
        matched_keywords = [kw for kw in trending_keywords if kw in text_content]
        if matched_keywords:
            opportunities.append(f"Aligns with trending topics: {', '.join(matched_keywords[:3])}")
        
        return opportunities
    
    async def _identify_risks(
        self, content: Dict[str, Any], market_data: Dict[str, Any], creator_profile: Dict[str, Any]
    ) -> List[str]:
        """Identify potential risks for the content."""
        
        risks = []
        
        # Market risks
        if market_data.get("competition_level", 0) > 0.8:
            risks.append("High competition in this category")
        
        if market_data.get("market_saturation", 0) > 0.7:
            risks.append("Market is approaching saturation")
        
        # Content risks
        text_length = len(content.get("text", "").split())
        if text_length > 500:
            risks.append("Long-form content may have lower engagement on short-form platforms")
        
        if text_length < 20:
            risks.append("Very short content may lack value")
        
        # Creator risks
        creator_expertise = creator_profile.get("expertise_areas", [])
        content_category = content.get("category", "")
        
        if not any(expertise.lower() in content_category.lower() for expertise in creator_expertise):
            risks.append("Content outside creator's established expertise")
        
        # Timing risks
        optimal_timing = market_data.get("optimal_posting_time", "")
        if optimal_timing:
            risks.append("Posting outside optimal engagement window")
        
        return risks
    
    async def _generate_recommendations(
        self, overall_score: float, opportunities: List[str], risks: List[str]
    ) -> List[str]:
        """Generate actionable recommendations based on analysis."""
        
        recommendations = []
        
        # Score-based recommendations
        if overall_score > 80:
            recommendations.append("High opportunity score - proceed with content creation")
        elif overall_score > 60:
            recommendations.append("Moderate opportunity - consider optimizing content")
        elif overall_score > 40:
            recommendations.append("Low opportunity - significant optimization needed")
        else:
            recommendations.append("Very low opportunity - reconsider content strategy")
        
        # Opportunity-based recommendations
        if "monetization" in " ".join(opportunities).lower():
            recommendations.append("Focus on monetization strategies and affiliate partnerships")
        
        if "engagement" in " ".join(opportunities).lower():
            recommendations.append("Optimize posting schedule and engagement tactics")
        
        # Risk-based recommendations
        if "competition" in " ".join(risks).lower():
            recommendations.append("Differentiate content to stand out from competitors")
        
        if "expertise" in " ".join(risks).lower():
            recommendations.append("Build credibility in this content category")
        
        # General recommendations
        if len(opportunities) > len(risks):
            recommendations.append("Leverage identified opportunities for maximum impact")
        else:
            recommendations.append("Address identified risks before content creation")
        
        return recommendations
    
    async def _calculate_confidence(
        self, factors: Dict[str, float], content: Dict[str, Any]
    ) -> float:
        """Calculate confidence in the opportunity score calculation."""
        
        # Base confidence
        confidence = 0.8
        
        # Reduce confidence if data is limited
        if not content.get("text"):
            confidence -= 0.2
        
        if not content.get("category"):
            confidence -= 0.1
        
        # Check factor consistency
        factor_values = list(factors.values())
        if max(factor_values) - min(factor_values) > 60:
            confidence -= 0.1  # High variance reduces confidence
        
        # Check for extreme values
        if any(f < 10 or f > 90 for f in factor_values):
            confidence -= 0.1
        
        return max(0.0, min(1.0, confidence))
    
    async def batch_calculate_scores(
        self, content_list: List[Dict[str, Any]]
    ) -> List[OpportunityScoreResult]:
        """Calculate opportunity scores for multiple content items."""
        
        results = []
        
        for content in content_list:
            result = await self.calculate_opportunity_score(content)
            results.append(result)
        
        return results
    
    async def get_top_opportunities(
        self, scores: List[OpportunityScoreResult], limit: int = 10
    ) -> List[OpportunityScoreResult]:
        """Get top scoring opportunities."""
        
        # Sort by overall score
        sorted_scores = sorted(scores, key=lambda x: x.overall_score, reverse=True)
        
        return sorted_scores[:limit]


# Singleton instance
opportunity_score_calculator = OpportunityScoreCalculator()
