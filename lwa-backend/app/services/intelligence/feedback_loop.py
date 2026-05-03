"""
Feedback Loop System v0

Collects, analyzes, and learns from user feedback to continuously improve
the LWA intelligence systems. Part of the Opportunity Engine learning pipeline.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import json

logger = logging.getLogger(__name__)


class FeedbackType(Enum):
    """Types of feedback that can be collected."""
    
    CONTENT_QUALITY = "content_quality"
    RECOMMENDATION_ACCURACY = "recommendation_accuracy"
    USER_SATISFACTION = "user_satisfaction"
    PERFORMANCE_METRICS = "performance_metrics"
    ERROR_REPORT = "error_report"
    FEATURE_REQUEST = "feature_request"
    IMPROVEMENT_SUGGESTION = "improvement_suggestion"


@dataclass
class FeedbackRecord:
    """Individual feedback record."""
    
    id: str
    user_id: str
    feedback_type: FeedbackType
    rating: Optional[float]  # 1-5 or 1-10 scale
    content: Optional[str]
    metadata: Dict[str, Any]
    context: Dict[str, Any]
    timestamp: datetime
    processed: bool = False
    insights: Optional[List[str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "feedback_type": self.feedback_type.value,
            "rating": self.rating,
            "content": self.content,
            "metadata": self.metadata,
            "context": self.context,
            "timestamp": self.timestamp.isoformat(),
            "processed": self.processed,
            "insights": self.insights,
        }


@dataclass
class FeedbackAnalysis:
    """Analysis results for feedback data."""
    
    total_feedback: int
    average_rating: float
    rating_distribution: Dict[str, int]
    common_themes: List[str]
    improvement_areas: List[str]
    success_factors: List[str]
    trends: Dict[str, Any]
    recommendations: List[str]
    confidence: float
    analysis_period: str


class FeedbackLoop:
    """
    Collects and analyzes user feedback to improve LWA systems.
    
    Processes feedback from multiple sources and generates actionable
    insights for system improvements.
    """
    
    def __init__(self):
        self.feedback_storage = []  # In-memory storage (replace with database)
        self.analysis_cache = {}
        self.feedback_weights = {
            "recent": 0.4,  # More recent feedback gets higher weight
            "high_rating": 0.3,  # High ratings indicate success
            "detailed": 0.2,  # Detailed feedback provides more insights
            "contextual": 0.1,  # Feedback with context is more valuable
        }
        
        # Feedback patterns to analyze
        self.feedback_patterns = {
            "positive_keywords": [
                "excellent", "amazing", "perfect", "love", "great", "helpful",
                "accurate", "useful", "valuable", "outstanding", "fantastic"
            ],
            "negative_keywords": [
                "poor", "bad", "terrible", "hate", "useless", "inaccurate",
                "confusing", "difficult", "broken", "wrong", "disappointed"
            ],
            "improvement_keywords": [
                "could", "should", "wish", "better", "improve", "add", "feature",
                "missing", "need", "want", "expect", "suggest", "recommend"
            ],
            "success_keywords": [
                "success", "worked", "achieved", "accomplished", "result",
                "outcome", "goal", "target", "completed", "finished", "done"
            ]
        }
    
    async def collect_feedback(
        self,
        user_id: str,
        feedback_type: FeedbackType,
        rating: Optional[float] = None,
        content: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Collect feedback from user.
        
        Args:
            user_id: User identifier
            feedback_type: Type of feedback
            rating: Numerical rating (1-5 or 1-10)
            content: Text feedback content
            metadata: Additional metadata
            context: Context information (action, content, etc.)
            
        Returns:
            Feedback record ID
        """
        
        try:
            # Generate unique ID
            feedback_id = f"feedback_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{user_id}"
            
            # Create feedback record
            record = FeedbackRecord(
                id=feedback_id,
                user_id=user_id,
                feedback_type=feedback_type,
                rating=rating,
                content=content,
                metadata=metadata or {},
                context=context or {},
                timestamp=datetime.utcnow()
            )
            
            # Store feedback
            self.feedback_storage.append(record)
            
            logger.info(f"Collected feedback {feedback_id} from user {user_id}")
            
            return feedback_id
            
        except Exception as e:
            logger.error(f"Failed to collect feedback: {e}")
            raise
    
    async def analyze_feedback(
        self,
        feedback_type: Optional[FeedbackType] = None,
        time_period_days: int = 30,
        min_feedback_count: int = 10
    ) -> FeedbackAnalysis:
        """
        Analyze collected feedback patterns.
        
        Args:
            feedback_type: Specific feedback type to analyze
            time_period_days: Analysis time period in days
            min_feedback_count: Minimum feedback count for analysis
            
        Returns:
            FeedbackAnalysis with insights and recommendations
        """
        
        try:
            # Filter feedback by type and time period
            cutoff_date = datetime.utcnow() - timedelta(days=time_period_days)
            
            filtered_feedback = [
                record for record in self.feedback_storage
                if record.timestamp >= cutoff_date and
                (feedback_type is None or record.feedback_type == feedback_type)
            ]
            
            if len(filtered_feedback) < min_feedback_count:
                return FeedbackAnalysis(
                    total_feedback=len(filtered_feedback),
                    average_rating=0.0,
                    rating_distribution={},
                    common_themes=[],
                    improvement_areas=[],
                    success_factors=[],
                    trends={},
                    recommendations=[],
                    confidence=0.0,
                    analysis_period=f"Last {time_period_days} days"
                )
            
            # Calculate basic statistics
            ratings = [r.rating for r in filtered_feedback if r.rating is not None]
            average_rating = sum(ratings) / len(ratings) if ratings else 0.0
            
            # Rating distribution
            rating_distribution = self._calculate_rating_distribution(ratings)
            
            # Analyze text feedback
            text_feedback = [r.content for r in filtered_feedback if r.content]
            text_analysis = await self._analyze_text_feedback(text_feedback)
            
            # Identify trends
            trends = await self._identify_trends(filtered_feedback)
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(
                average_rating, text_analysis, trends
            )
            
            # Calculate confidence
            confidence = self._calculate_analysis_confidence(
                len(filtered_feedback), len(ratings), len(text_feedback)
            )
            
            analysis = FeedbackAnalysis(
                total_feedback=len(filtered_feedback),
                average_rating=average_rating,
                rating_distribution=rating_distribution,
                common_themes=text_analysis.get("themes", []),
                improvement_areas=text_analysis.get("improvements", []),
                success_factors=text_analysis.get("successes", []),
                trends=trends,
                recommendations=recommendations,
                confidence=confidence,
                analysis_period=f"Last {time_period_days} days"
            )
            
            # Cache analysis
            cache_key = f"{feedback_type.value if feedback_type else 'all'}_{time_period_days}"
            self.analysis_cache[cache_key] = analysis
            
            return analysis
            
        except Exception as e:
            logger.error(f"Feedback analysis failed: {e}")
            return FeedbackAnalysis(
                total_feedback=0,
                average_rating=0.0,
                rating_distribution={},
                common_themes=[],
                improvement_areas=[],
                success_factors=[],
                trends={},
                recommendations=[],
                confidence=0.0,
                analysis_period=f"Last {time_period_days} days"
            )
    
    def _calculate_rating_distribution(self, ratings: List[float]) -> Dict[str, int]:
        """Calculate distribution of ratings."""
        
        if not ratings:
            return {}
        
        distribution = {}
        for rating in ratings:
            if rating <= 2:
                key = "1-2 stars"
            elif rating <= 3:
                key = "3 stars"
            elif rating <= 4:
                key = "4 stars"
            else:
                key = "5 stars"
            
            distribution[key] = distribution.get(key, 0) + 1
        
        return distribution
    
    async def _analyze_text_feedback(self, text_feedback: List[str]) -> Dict[str, List[str]]:
        """Analyze text feedback for themes and patterns."""
        
        analysis = {
            "themes": [],
            "improvements": [],
            "successes": [],
            "sentiments": []
        }
        
        if not text_feedback:
            return analysis
        
        # Combine all text for analysis
        all_text = " ".join(text_feedback).lower()
        
        # Count keyword occurrences
        keyword_counts = {}
        for category, keywords in self.feedback_patterns.items():
            count = sum(1 for keyword in keywords if keyword in all_text)
            if count > 0:
                keyword_counts[category] = count
        
        # Extract themes based on keyword patterns
        if keyword_counts.get("positive_keywords", 0) > 0:
            analysis["sentiments"].append("Generally positive feedback")
        
        if keyword_counts.get("negative_keywords", 0) > 0:
            analysis["sentiments"].append("Areas need improvement")
        
        if keyword_counts.get("improvement_keywords", 0) > 0:
            analysis["improvements"].append("Users want additional features")
            analysis["improvements"].append("Functionality improvements requested")
        
        if keyword_counts.get("success_keywords", 0) > 0:
            analysis["successes"].append("Users achieving desired outcomes")
            analysis["successes"].append("System meeting user expectations")
        
        # Find common phrases (simplified)
        common_phrases = self._extract_common_phrases(text_feedback)
        analysis["themes"].extend(common_phrases[:5])  # Top 5 themes
        
        return analysis
    
    def _extract_common_phrases(self, text_feedback: List[str]) -> List[str]:
        """Extract common phrases from text feedback."""
        
        # Simple phrase extraction (could be enhanced with NLP)
        phrase_counts = {}
        
        for text in text_feedback:
            words = text.lower().split()
            # Look for 2-3 word phrases
            for i in range(len(words) - 1):
                phrase = " ".join(words[i:i+2])
                phrase_counts[phrase] = phrase_counts.get(phrase, 0) + 1
            
            for i in range(len(words) - 2):
                phrase = " ".join(words[i:i+3])
                phrase_counts[phrase] = phrase_counts.get(phrase, 0) + 1
        
        # Return most common phrases
        sorted_phrases = sorted(phrase_counts.items(), key=lambda x: x[1], reverse=True)
        return [phrase for phrase, count in sorted_phrases if count > 1]
    
    async def _identify_trends(self, feedback: List[FeedbackRecord]) -> Dict[str, Any]:
        """Identify trends in feedback over time."""
        
        trends = {
            "rating_trend": "stable",
            "volume_trend": "stable",
            "type_distribution": {},
            "temporal_patterns": {}
        }
        
        if len(feedback) < 5:
            return trends
        
        # Sort by timestamp
        sorted_feedback = sorted(feedback, key=lambda x: x.timestamp)
        
        # Analyze rating trend
        ratings = [r.rating for r in sorted_feedback if r.rating is not None]
        if len(ratings) >= 3:
            first_half = ratings[:len(ratings)//2]
            second_half = ratings[len(ratings)//2:]
            
            first_avg = sum(first_half) / len(first_half)
            second_avg = sum(second_half) / len(second_half)
            
            if second_avg > first_avg + 0.5:
                trends["rating_trend"] = "improving"
            elif second_avg < first_avg - 0.5:
                trends["rating_trend"] = "declining"
        
        # Analyze feedback type distribution
        type_counts = {}
        for record in feedback:
            type_name = record.feedback_type.value
            type_counts[type_name] = type_counts.get(type_name, 0) + 1
        
        total_feedback = len(feedback)
        for type_name, count in type_counts.items():
            trends["type_distribution"][type_name] = count / total_feedback
        
        return trends
    
    async def _generate_recommendations(
        self, average_rating: float, text_analysis: Dict[str, List[str]], trends: Dict[str, Any]
    ) -> List[str]:
        """Generate actionable recommendations based on feedback analysis."""
        
        recommendations = []
        
        # Rating-based recommendations
        if average_rating < 3.0:
            recommendations.append("Critical improvements needed - user satisfaction is low")
            recommendations.append("Prioritize fixing major issues and user pain points")
        elif average_rating < 4.0:
            recommendations.append("Moderate improvements needed to enhance user experience")
            recommendations.append("Focus on addressing common user complaints")
        elif average_rating > 4.5:
            recommendations.append("Excellent user satisfaction - maintain current quality")
            recommendations.append("Consider incremental enhancements and new features")
        
        # Text-based recommendations
        improvements = text_analysis.get("improvements", [])
        if "Users want additional features" in improvements:
            recommendations.append("Develop requested features based on user feedback")
        
        if "Functionality improvements requested" in improvements:
            recommendations.append("Improve existing functionality based on user suggestions")
        
        # Trend-based recommendations
        if trends.get("rating_trend") == "declining":
            recommendations.append("Investigate causes of declining satisfaction")
            recommendations.append("Implement corrective measures to reverse trend")
        
        elif trends.get("rating_trend") == "improving":
            recommendations.append("Continue current improvement trajectory")
            recommendations.append("Identify and double down on successful changes")
        
        # Type-based recommendations
        type_dist = trends.get("type_distribution", {})
        if type_dist.get("error_report", 0) > 0.2:
            recommendations.append("Address error reports to improve system reliability")
        
        if type_dist.get("feature_request", 0) > 0.3:
            recommendations.append("Consider implementing popular feature requests")
        
        return recommendations
    
    def _calculate_analysis_confidence(
        self, total_feedback: int, rating_count: int, text_count: int
    ) -> float:
        """Calculate confidence in analysis results."""
        
        # Base confidence from sample size
        if total_feedback < 10:
            sample_confidence = 0.3
        elif total_feedback < 50:
            sample_confidence = 0.6
        elif total_feedback < 200:
            sample_confidence = 0.8
        else:
            sample_confidence = 0.9
        
        # Adjust for data completeness
        data_completeness = (rating_count / total_feedback + text_count / total_feedback) / 2
        
        # Combine factors
        confidence = sample_confidence * (0.7 + 0.3 * data_completeness)
        
        return min(1.0, confidence)
    
    async def get_feedback_summary(
        self, user_id: Optional[str] = None, days: int = 7
    ) -> Dict[str, Any]:
        """Get summary of recent feedback."""
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        filtered_feedback = [
            record for record in self.feedback_storage
            if record.timestamp >= cutoff_date and
            (user_id is None or record.user_id == user_id)
        ]
        
        summary = {
            "period": f"Last {days} days",
            "total_feedback": len(filtered_feedback),
            "by_type": {},
            "average_rating": 0.0,
            "recent_feedback": []
        }
        
        # Count by type
        type_counts = {}
        for record in filtered_feedback:
            type_name = record.feedback_type.value
            type_counts[type_name] = type_counts.get(type_name, 0) + 1
        
        summary["by_type"] = type_counts
        
        # Calculate average rating
        ratings = [r.rating for r in filtered_feedback if r.rating is not None]
        if ratings:
            summary["average_rating"] = sum(ratings) / len(ratings)
        
        # Get recent feedback
        recent_feedback = sorted(filtered_feedback, key=lambda x: x.timestamp, reverse=True)[:5]
        summary["recent_feedback"] = [
            {
                "id": r.id,
                "type": r.feedback_type.value,
                "rating": r.rating,
                "content": r.content[:100] + "..." if r.content and len(r.content) > 100 else r.content,
                "timestamp": r.timestamp.isoformat()
            }
            for r in recent_feedback
        ]
        
        return summary
    
    async def process_feedback_for_learning(
        self, feedback_id: str
    ) -> Dict[str, Any]:
        """Process specific feedback for machine learning."""
        
        # Find feedback record
        record = None
        for r in self.feedback_storage:
            if r.id == feedback_id:
                record = r
                break
        
        if not record:
            raise ValueError(f"Feedback record {feedback_id} not found")
        
        # Extract learning signals
        learning_signals = {
            "user_id": record.user_id,
            "feedback_type": record.feedback_type.value,
            "rating": record.rating,
            "content_sentiment": self._analyze_sentiment(record.content) if record.content else None,
            "context_features": self._extract_context_features(record.context),
            "metadata_features": self._extract_metadata_features(record.metadata),
            "timestamp": record.timestamp.isoformat()
        }
        
        # Mark as processed
        record.processed = True
        
        # Generate insights
        insights = await self._generate_feedback_insights(record)
        record.insights = insights
        
        return {
            "feedback_id": feedback_id,
            "learning_signals": learning_signals,
            "insights": insights,
            "processed_at": datetime.utcnow().isoformat()
        }
    
    def _analyze_sentiment(self, text: str) -> str:
        """Simple sentiment analysis (could be enhanced with NLP)."""
        
        if not text:
            return "neutral"
        
        text_lower = text.lower()
        
        positive_count = sum(1 for word in self.feedback_patterns["positive_keywords"] if word in text_lower)
        negative_count = sum(1 for word in self.feedback_patterns["negative_keywords"] if word in text_lower)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    def _extract_context_features(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract features from context."""
        
        features = {}
        
        # Action type
        if "action" in context:
            features["action_type"] = context["action"]
        
        # Content type
        if "content_type" in context:
            features["content_type"] = context["content_type"]
        
        # Platform
        if "platform" in context:
            features["platform"] = context["platform"]
        
        # Time of day
        if "timestamp" in context:
            try:
                timestamp = datetime.fromisoformat(context["timestamp"])
                features["time_of_day"] = timestamp.hour
            except:
                pass
        
        return features
    
    def _extract_metadata_features(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Extract features from metadata."""
        
        features = {}
        
        # User agent
        if "user_agent" in metadata:
            features["device_type"] = self._classify_device(metadata["user_agent"])
        
        # Session info
        if "session_duration" in metadata:
            features["session_length"] = metadata["session_duration"]
        
        return features
    
    def _classify_device(self, user_agent: str) -> str:
        """Classify device from user agent string."""
        
        user_agent_lower = user_agent.lower()
        
        if "mobile" in user_agent_lower or "android" in user_agent_lower or "iphone" in user_agent_lower:
            return "mobile"
        elif "tablet" in user_agent_lower or "ipad" in user_agent_lower:
            return "tablet"
        else:
            return "desktop"
    
    async def _generate_feedback_insights(self, record: FeedbackRecord) -> List[str]:
        """Generate insights from feedback record."""
        
        insights = []
        
        # Rating insights
        if record.rating:
            if record.rating >= 4:
                insights.append("High satisfaction indicated")
            elif record.rating <= 2:
                insights.append("Significant issues identified")
            else:
                insights.append("Moderate satisfaction")
        
        # Content insights
        if record.content:
            content_length = len(record.content.split())
            if content_length > 50:
                insights.append("Detailed feedback provided")
            elif content_length < 10:
                insights.append("Brief feedback provided")
        
        # Context insights
        if record.context.get("action"):
            insights.append(f"Feedback related to {record.context['action']} action")
        
        return insights


# Singleton instance
feedback_loop = FeedbackLoop()
