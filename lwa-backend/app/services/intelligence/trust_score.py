"""
Trust Score Algorithm v0

Calculates trustworthiness scores for content, sources, and claims.
Used by the Opportunity Engine to prioritize reliable and authentic content.
"""

import logging
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


@dataclass
class TrustScoreResult:
    """Result of trust score calculation."""
    
    overall_score: float  # 0-100
    source_credibility: float
    content_authenticity: float
    claim_verifiability: float
    engagement_quality: float
    technical_quality: float
    
    # Detailed breakdown
    factors: Dict[str, float]
    reasoning: List[str]
    confidence: float
    timestamp: datetime


@dataclass
class SourceProfile:
    """Profile for trust scoring of content sources."""
    
    domain_authority: float
    historical_accuracy: float
    bias_score: float  # 0 (unbiased) to 1 (highly biased)
    fact_checking_score: float
    user_reports: float
    verification_status: str  # "verified", "unverified", "flagged"


class TrustScoreCalculator:
    """
    Calculates comprehensive trust scores for content and sources.
    
    Evaluates multiple dimensions of trustworthiness including
    source credibility, content authenticity, claim verifiability,
    engagement quality, and technical quality.
    """
    
    def __init__(self):
        self.trust_factors = {
            "source_credibility": 0.30,
            "content_authenticity": 0.25,
            "claim_verifiability": 0.20,
            "engagement_quality": 0.15,
            "technical_quality": 0.10,
        }
        
        # Domain reputation database (simplified)
        self.domain_reputation = {
            "reputable_news": ["bbc.com", "reuters.com", "ap.org", "npr.org"],
            "academic": ["edu", "gov", "org"],
            "social_platforms": ["youtube.com", "tiktok.com", "instagram.com"],
            "questionable": ["fake-news.example.com"],
        }
        
        # Red flag patterns
        self.red_flag_patterns = [
            r"clickbait|shocking|you won't believe",
            r"100%.*guaranteed|instant.*result",
            r"conspiracy.*theory|secret.*revealed",
            r"fake.*news|alternative.*facts",
        ]
    
    async def calculate_trust_score(
        self,
        content: Dict[str, Any],
        source_info: Optional[Dict[str, Any]] = None,
        engagement_data: Optional[Dict[str, Any]] = None,
        technical_data: Optional[Dict[str, Any]] = None
    ) -> TrustScoreResult:
        """
        Calculate comprehensive trust score for content.
        
        Args:
            content: Content data including text, metadata, claims
            source_info: Information about content source
            engagement_data: User engagement metrics
            technical_data: Technical quality indicators
            
        Returns:
            TrustScoreResult with detailed breakdown
        """
        
        try:
            # Extract content features
            text_content = content.get("text", "")
            claims = content.get("claims", [])
            metadata = content.get("metadata", {})
            
            # Calculate individual factor scores
            source_credibility = await self._calculate_source_credibility(
                source_info or {}
            )
            
            content_authenticity = await self._calculate_content_authenticity(
                text_content, metadata, claims
            )
            
            claim_verifiability = await self._calculate_claim_verifiability(
                claims, source_info or {}
            )
            
            engagement_quality = await self._calculate_engagement_quality(
                engagement_data or {}
            )
            
            technical_quality = await self._calculate_technical_quality(
                technical_data or {}
            )
            
            # Calculate weighted overall score
            overall_score = (
                source_credibility * self.trust_factors["source_credibility"] +
                content_authenticity * self.trust_factors["content_authenticity"] +
                claim_verifiability * self.trust_factors["claim_verifiability"] +
                engagement_quality * self.trust_factors["engagement_quality"] +
                technical_quality * self.trust_factors["technical_quality"]
            )
            
            # Generate reasoning
            reasoning = await self._generate_reasoning(
                source_credibility, content_authenticity, claim_verifiability,
                engagement_quality, technical_quality
            )
            
            # Collect all factors
            factors = {
                "source_credibility": source_credibility,
                "content_authenticity": content_authenticity,
                "claim_verifiability": claim_verifiability,
                "engagement_quality": engagement_quality,
                "technical_quality": technical_quality,
            }
            
            # Calculate confidence
            confidence = await self._calculate_confidence(factors, content)
            
            return TrustScoreResult(
                overall_score=round(overall_score, 2),
                source_credibility=round(source_credibility, 2),
                content_authenticity=round(content_authenticity, 2),
                claim_verifiability=round(claim_verifiability, 2),
                engagement_quality=round(engagement_quality, 2),
                technical_quality=round(technical_quality, 2),
                factors=factors,
                reasoning=reasoning,
                confidence=round(confidence, 2),
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Trust score calculation failed: {e}")
            return TrustScoreResult(
                overall_score=0.0,
                source_credibility=0.0,
                content_authenticity=0.0,
                claim_verifiability=0.0,
                engagement_quality=0.0,
                technical_quality=0.0,
                factors={},
                reasoning=[f"Calculation error: {str(e)}"],
                confidence=0.0,
                timestamp=datetime.utcnow()
            )
    
    async def _calculate_source_credibility(self, source_info: Dict[str, Any]) -> float:
        """Calculate source credibility score."""
        
        score = 50.0  # Base score
        
        # Domain reputation
        domain = source_info.get("domain", "")
        if any(rep in domain for rep in self.domain_reputation["reputable_news"]):
            score += 25.0
        elif any(rep in domain for rep in self.domain_reputation["academic"]):
            score += 30.0
        elif any(rep in domain for rep in self.domain_reputation["social_platforms"]):
            score += 5.0
        elif any(rep in domain for rep in self.domain_reputation["questionable"]):
            score -= 30.0
        
        # Verification status
        verification = source_info.get("verification_status", "")
        if verification == "verified":
            score += 15.0
        elif verification == "flagged":
            score -= 25.0
        
        # Historical accuracy
        accuracy = source_info.get("historical_accuracy", 0.5)
        score += (accuracy - 0.5) * 40.0
        
        # Bias score (lower bias = higher trust)
        bias = source_info.get("bias_score", 0.5)
        score += (0.5 - bias) * 20.0
        
        # Fact checking
        fact_check = source_info.get("fact_checking_score", 0.5)
        score += (fact_check - 0.5) * 30.0
        
        return max(0.0, min(100.0, score))
    
    async def _calculate_content_authenticity(
        self, text: str, metadata: Dict[str, Any], claims: List[Dict[str, Any]]
    ) -> float:
        """Calculate content authenticity score."""
        
        score = 50.0  # Base score
        
        # Check for red flags in text
        red_flag_count = 0
        for pattern in self.red_flag_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                red_flag_count += 1
        
        score -= red_flag_count * 10.0
        
        # Content length and depth
        word_count = len(text.split())
        if word_count > 500:
            score += 10.0
        elif word_count > 100:
            score += 5.0
        else:
            score -= 5.0
        
        # Structured content
        if metadata.get("has_citations", False):
            score += 15.0
        
        if metadata.get("has_sources", False):
            score += 10.0
        
        # Originality indicators
        if metadata.get("originality_score", 0.5) > 0.7:
            score += 10.0
        
        # Sentiment analysis (extreme sentiment can be less trustworthy)
        sentiment = metadata.get("sentiment_score", 0.0)
        if abs(sentiment) < 0.3:  # Neutral sentiment
            score += 5.0
        elif abs(sentiment) > 0.8:  # Extreme sentiment
            score -= 10.0
        
        return max(0.0, min(100.0, score))
    
    async def _calculate_claim_verifiability(
        self, claims: List[Dict[str, Any]], source_info: Dict[str, Any]
    ) -> float:
        """Calculate claim verifiability score."""
        
        if not claims:
            return 50.0  # Neutral score for no claims
        
        total_score = 0.0
        
        for claim in claims:
            claim_score = 50.0
            
            # Specific claims are more verifiable
            claim_text = claim.get("text", "")
            if any(keyword in claim_text.lower() for keyword in ["study", "research", "data", "statistics"]):
                claim_score += 10.0
            
            # Claims with evidence
            if claim.get("has_evidence", False):
                claim_score += 20.0
            
            # Claims with sources
            if claim.get("sources"):
                claim_score += 15.0
            
            # Factual vs opinion claims
            claim_type = claim.get("type", "opinion")
            if claim_type == "factual":
                claim_score += 10.0
            elif claim_type == "opinion":
                claim_score -= 5.0
            
            total_score += claim_score
        
        average_score = total_score / len(claims)
        return max(0.0, min(100.0, average_score))
    
    async def _calculate_engagement_quality(self, engagement_data: Dict[str, Any]) -> float:
        """Calculate engagement quality score."""
        
        if not engagement_data:
            return 50.0
        
        score = 50.0
        
        # Engagement ratio (likes/views)
        views = engagement_data.get("views", 0)
        likes = engagement_data.get("likes", 0)
        
        if views > 0:
            engagement_ratio = likes / views
            if engagement_ratio > 0.1:  # High engagement ratio
                score += 15.0
            elif engagement_ratio > 0.05:
                score += 10.0
            elif engagement_ratio < 0.01:  # Very low engagement
                score -= 10.0
        
        # Comment quality (meaningful discussions)
        comments = engagement_data.get("comments", 0)
        meaningful_comments = engagement_data.get("meaningful_comments", 0)
        
        if comments > 0:
            comment_quality_ratio = meaningful_comments / comments
            if comment_quality_ratio > 0.5:
                score += 15.0
            elif comment_quality_ratio > 0.3:
                score += 10.0
        
        # Share patterns (organic vs forced)
        shares = engagement_data.get("shares", 0)
        if shares > 100:
            score += 10.0
        
        # Bot detection (lower bot activity = higher trust)
        bot_score = engagement_data.get("bot_activity_score", 0.0)
        score -= bot_score * 20.0
        
        return max(0.0, min(100.0, score))
    
    async def _calculate_technical_quality(self, technical_data: Dict[str, Any]) -> float:
        """Calculate technical quality score."""
        
        if not technical_data:
            return 50.0
        
        score = 50.0
        
        # Video quality
        if "video" in technical_data:
            video_data = technical_data["video"]
            resolution = video_data.get("resolution", "")
            if "1080" in resolution or "720" in resolution:
                score += 10.0
            
            frame_rate = video_data.get("frame_rate", 0)
            if frame_rate >= 30:
                score += 5.0
            
            # Audio quality
            audio_bitrate = video_data.get("audio_bitrate", 0)
            if audio_bitrate >= 128:
                score += 5.0
        
        # Production quality
        production_score = technical_data.get("production_quality", 0.5)
        score += (production_score - 0.5) * 30.0
        
        # Technical consistency
        consistency_score = technical_data.get("technical_consistency", 0.5)
        score += (consistency_score - 0.5) * 20.0
        
        # Metadata completeness
        metadata_completeness = technical_data.get("metadata_completeness", 0.5)
        score += (metadata_completeness - 0.5) * 15.0
        
        return max(0.0, min(100.0, score))
    
    async def _generate_reasoning(
        self, source_cred: float, content_auth: float, claim_ver: float,
        engage_qual: float, tech_qual: float
    ) -> List[str]:
        """Generate reasoning explanations for the trust score."""
        
        reasoning = []
        
        # Source credibility reasoning
        if source_cred > 75:
            reasoning.append("Highly credible source with strong reputation")
        elif source_cred > 50:
            reasoning.append("Moderately credible source with some verification")
        elif source_cred > 25:
            reasoning.append("Questionable source with limited verification")
        else:
            reasoning.append("Low credibility source with significant concerns")
        
        # Content authenticity reasoning
        if content_auth > 75:
            reasoning.append("Content shows strong authenticity with proper sourcing")
        elif content_auth > 50:
            reasoning.append("Content appears generally authentic with minor concerns")
        elif content_auth > 25:
            reasoning.append("Content shows signs of inauthenticity or manipulation")
        else:
            reasoning.append("Content appears highly inauthentic or misleading")
        
        # Claim verifiability reasoning
        if claim_ver > 75:
            reasoning.append("Claims are highly verifiable with strong evidence")
        elif claim_ver > 50:
            reasoning.append("Claims are somewhat verifiable with partial evidence")
        elif claim_ver > 25:
            reasoning.append("Claims are difficult to verify with limited evidence")
        else:
            reasoning.append("Claims are unverifiable or lack supporting evidence")
        
        # Engagement quality reasoning
        if engage_qual > 75:
            reasoning.append("High-quality engagement with meaningful interactions")
        elif engage_qual > 50:
            reasoning.append("Moderate engagement quality with mixed interactions")
        elif engage_qual > 25:
            reasoning.append("Low-quality engagement with potential bot activity")
        else:
            reasoning.append("Poor engagement quality with significant bot activity")
        
        # Technical quality reasoning
        if tech_qual > 75:
            reasoning.append("Excellent technical quality with professional production")
        elif tech_qual > 50:
            reasoning.append("Good technical quality with decent production")
        elif tech_qual > 25:
            reasoning.append("Poor technical quality with production issues")
        else:
            reasoning.append("Very poor technical quality with major production problems")
        
        return reasoning
    
    async def _calculate_confidence(
        self, factors: Dict[str, float], content: Dict[str, Any]
    ) -> float:
        """Calculate confidence in the trust score calculation."""
        
        # Base confidence
        confidence = 0.8
        
        # Reduce confidence if data is limited
        if not content.get("text"):
            confidence -= 0.2
        
        if not content.get("metadata"):
            confidence -= 0.1
        
        # Check factor consistency
        factor_values = list(factors.values())
        if max(factor_values) - min(factor_values) > 50:
            confidence -= 0.1  # High variance reduces confidence
        
        # Check for extreme values
        if any(f < 10 or f > 90 for f in factor_values):
            confidence -= 0.1
        
        return max(0.0, min(1.0, confidence))
    
    async def batch_calculate_scores(
        self, content_list: List[Dict[str, Any]]
    ) -> List[TrustScoreResult]:
        """Calculate trust scores for multiple content items."""
        
        results = []
        
        for content in content_list:
            result = await self.calculate_trust_score(content)
            results.append(result)
        
        return results
    
    async def get_trust_trends(
        self, scores: List[TrustScoreResult], days: int = 30
    ) -> Dict[str, Any]:
        """Analyze trust score trends over time."""
        
        if not scores:
            return {}
        
        # Filter scores by time period
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        recent_scores = [
            s for s in scores 
            if s.timestamp >= cutoff_date
        ]
        
        if not recent_scores:
            return {}
        
        # Calculate trends
        overall_scores = [s.overall_score for s in recent_scores]
        
        return {
            "period_days": days,
            "total_scores": len(recent_scores),
            "average_score": sum(overall_scores) / len(overall_scores),
            "highest_score": max(overall_scores),
            "lowest_score": min(overall_scores),
            "score_distribution": {
                "high_trust": len([s for s in overall_scores if s > 75]),
                "medium_trust": len([s for s in overall_scores if 50 <= s <= 75]),
                "low_trust": len([s for s in overall_scores if s < 50]),
            },
            "factor_averages": {
                "source_credibility": sum(s.source_credibility for s in recent_scores) / len(recent_scores),
                "content_authenticity": sum(s.content_authenticity for s in recent_scores) / len(recent_scores),
                "claim_verifiability": sum(s.claim_verifiability for s in recent_scores) / len(recent_scores),
                "engagement_quality": sum(s.engagement_quality for s in recent_scores) / len(recent_scores),
                "technical_quality": sum(s.technical_quality for s in recent_scores) / len(recent_scores),
            }
        }


# Singleton instance
trust_score_calculator = TrustScoreCalculator()
