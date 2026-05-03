"""
Feedback Learning Loop v0

Analyzes performance data and improves future recommendations
through feedback collection, performance analysis, and learning algorithms.
"""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta

logger = logging.getLogger("uvicorn.error")


class FeedbackType(str, Enum):
    """Types of user feedback."""
    
    THUMBS_UP = "thumbs_up"
    THUMBS_DOWN = "thumbs_down"
    STAR_RATING = "star_rating"
    EDITED = "edited"
    REGENERATED = "regenerated"
    POSTED = "posted"
    SKIPPED = "skipped"


class PerformanceMetric(str, Enum):
    """Performance metrics for analysis."""
    
    ENGAGEMENT_RATE = "engagement_rate"
    VIEW_COUNT = "view_count"
    SHARE_COUNT = "share_count"
    CONVERSION_RATE = "conversion_rate"
    RETENTION_RATE = "retention_rate"


@dataclass
class FeedbackEntry:
    """Single feedback entry."""
    
    clip_id: str
    feedback_type: FeedbackType
    rating: Optional[int] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    user_id: Optional[str] = None
    metadata: Dict[str, any] = field(default_factory=dict)


@dataclass
class PerformanceData:
    """Performance data for a clip."""
    
    clip_id: str
    metrics: Dict[PerformanceMetric, float] = field(default_factory=dict)
    platform: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class LearningInsight:
    """Insight derived from feedback and performance data."""
    
    insight_type: str
    description: str
    confidence: float
    actionable: bool = True
    recommendation: Optional[str] = None


@dataclass
class LearningModel:
    """Learning model state."""
    
    model_version: str
    last_updated: datetime
    feedback_count: int
    performance_count: int
    insights: List[LearningInsight] = field(default_factory=list)
    model_weights: Dict[str, float] = field(default_factory=dict)


class FeedbackLearningLoop:
    """
    Feedback learning loop for continuous improvement.
    
    Collects feedback, analyzes performance, and improves recommendations
    through learning algorithms while respecting privacy.
    """
    
    def __init__(self) -> None:
        self._feedback_store: List[FeedbackEntry] = []
        self._performance_store: List[PerformanceData] = []
        self._learning_model = LearningModel(
            model_version="0.1.0",
            last_updated=datetime.utcnow(),
            feedback_count=0,
            performance_count=0
        )
        self._ab_tests: Dict[str, Dict[str, any]] = {}
    
    def collect_feedback(
        self,
        clip_id: str,
        feedback_type: FeedbackType,
        rating: Optional[int] = None,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, any]] = None
    ) -> FeedbackEntry:
        """
        Collect user feedback on a clip.
        
        Args:
            clip_id: ID of the clip
            feedback_type: Type of feedback
            rating: Optional numeric rating
            user_id: Optional user ID (anonymized in production)
            metadata: Additional metadata
            
        Returns:
            FeedbackEntry
        """
        entry = FeedbackEntry(
            clip_id=clip_id,
            feedback_type=feedback_type,
            rating=rating,
            user_id=self._anonymize_user_id(user_id) if user_id else None,
            metadata=metadata or {}
        )
        
        self._feedback_store.append(entry)
        self._learning_model.feedback_count += 1
        
        logger.info(f"feedback_collected clip_id={clip_id} type={feedback_type}")
        
        return entry
    
    def record_performance(
        self,
        clip_id: str,
        metrics: Dict[PerformanceMetric, float],
        platform: Optional[str] = None
    ) -> PerformanceData:
        """
        Record performance data for a clip.
        
        Args:
            clip_id: ID of the clip
            metrics: Performance metrics
            platform: Platform where clip was posted
            
        Returns:
            PerformanceData
        """
        data = PerformanceData(
            clip_id=clip_id,
            metrics=metrics,
            platform=platform
        )
        
        self._performance_store.append(data)
        self._learning_model.performance_count += 1
        
        logger.info(f"performance_recorded clip_id={clip_id} platform={platform}")
        
        return data
    
    def analyze_feedback(self, clip_id: Optional[str] = None) -> List[LearningInsight]:
        """
        Analyze feedback and generate insights.
        
        Args:
            clip_id: Optional clip ID to analyze (analyzes all if None)
            
        Returns:
            List of learning insights
        """
        insights = []
        
        # Filter feedback by clip_id if provided
        feedback_data = self._feedback_store
        if clip_id:
            feedback_data = [f for f in self._feedback_store if f.clip_id == clip_id]
        
        if not feedback_data:
            return insights
        
        # Calculate feedback distribution
        feedback_counts = {}
        for feedback in feedback_data:
            feedback_counts[feedback.feedback_type] = feedback_counts.get(feedback.feedback_type, 0) + 1
        
        # Generate insights from distribution
        total_feedback = len(feedback_data)
        
        thumbs_up_count = feedback_counts.get(FeedbackType.THUMBS_UP, 0)
        thumbs_down_count = feedback_counts.get(FeedbackType.THUMBS_DOWN, 0)
        
        if thumbs_up_count > thumbs_down_count * 2:
            insights.append(LearningInsight(
                insight_type="positive_sentiment",
                description="Strong positive feedback detected",
                confidence=thumbs_up_count / total_feedback,
                actionable=True,
                recommendation="Increase similar content generation"
            ))
        
        if thumbs_down_count > thumbs_up_count:
            insights.append(LearningInsight(
                insight_type="negative_sentiment",
                description="Negative feedback exceeds positive",
                confidence=thumbs_down_count / total_feedback,
                actionable=True,
                recommendation="Adjust generation parameters"
            ))
        
        posted_count = feedback_counts.get(FeedbackType.POSTED, 0)
        if posted_count > 0:
            insights.append(LearningInsight(
                insight_type="posting_behavior",
                description=f"Users posted {posted_count} clips",
                confidence=posted_count / total_feedback,
                actionable=True,
                recommendation="Prioritize similar clip styles"
            ))
        
        return insights
    
    def analyze_performance(self, clip_id: Optional[str] = None) -> List[LearningInsight]:
        """
        Analyze performance data and generate insights.
        
        Args:
            clip_id: Optional clip ID to analyze (analyzes all if None)
            
        Returns:
            List of learning insights
        """
        insights = []
        
        # Filter performance by clip_id if provided
        performance_data = self._performance_store
        if clip_id:
            performance_data = [p for p in self._performance_store if p.clip_id == clip_id]
        
        if not performance_data:
            return insights
        
        # Calculate average metrics
        metric_averages = {}
        for metric in PerformanceMetric:
            values = [p.metrics.get(metric, 0) for p in performance_data if metric in p.metrics]
            if values:
                metric_averages[metric] = sum(values) / len(values)
        
        # Generate insights from metrics
        if PerformanceMetric.ENGAGEMENT_RATE in metric_averages:
            engagement = metric_averages[PerformanceMetric.ENGAGEMENT_RATE]
            if engagement > 0.1:  # 10% engagement is high
                insights.append(LearningInsight(
                    insight_type="high_engagement",
                    description=f"High engagement rate: {engagement:.2%}",
                    confidence=0.8,
                    actionable=True,
                    recommendation="Scale similar content strategies"
                ))
        
        if PerformanceMetric.VIEW_COUNT in metric_averages:
            views = metric_averages[PerformanceMetric.VIEW_COUNT]
            if views > 10000:
                insights.append(LearningInsight(
                    insight_type="viral_potential",
                    description=f"High view count: {views:.0f}",
                    confidence=0.7,
                    actionable=True,
                    recommendation="Analyze viral factors for replication"
                ))
        
        return insights
    
    def update_learning_model(self) -> LearningModel:
        """
        Update learning model with new data.
        
        Returns:
            Updated LearningModel
        """
        # Analyze all feedback and performance
        feedback_insights = self.analyze_feedback()
        performance_insights = self.analyze_performance()
        
        # Combine insights
        all_insights = feedback_insights + performance_insights
        
        # Update model weights based on insights
        for insight in all_insights:
            if insight.insight_type == "positive_sentiment":
                self._learning_model.model_weights["positive_weight"] = \
                    self._learning_model.model_weights.get("positive_weight", 0.5) + 0.1
            elif insight.insight_type == "negative_sentiment":
                self._learning_model.model_weights["negative_weight"] = \
                    self._learning_model.model_weights.get("negative_weight", 0.5) + 0.1
            elif insight.insight_type == "high_engagement":
                self._learning_model.model_weights["engagement_weight"] = \
                    self._learning_model.model_weights.get("engagement_weight", 0.5) + 0.1
        
        # Normalize weights
        total_weight = sum(self._learning_model.model_weights.values())
        if total_weight > 0:
            for key in self._learning_model.model_weights:
                self._learning_model.model_weights[key] /= total_weight
        
        # Update model metadata
        self._learning_model.last_updated = datetime.utcnow()
        self._learning_model.insights = all_insights
        
        logger.info(f"learning_model_updated version={self._learning_model.model_version} insights={len(all_insights)}")
        
        return self._learning_model
    
    def create_ab_test(
        self,
        test_name: str,
        variants: List[Dict[str, any]],
        traffic_split: Optional[List[float]] = None
    ) -> str:
        """
        Create an A/B test for comparing strategies.
        
        Args:
            test_name: Name of the test
            variants: List of variant configurations
            traffic_split: Optional traffic split percentages
            
        Returns:
            Test ID
        """
        test_id = f"ab_test_{datetime.utcnow().timestamp()}"
        
        if traffic_split is None:
            # Equal split
            traffic_split = [1.0 / len(variants)] * len(variants)
        
        self._ab_tests[test_id] = {
            "name": test_name,
            "variants": variants,
            "traffic_split": traffic_split,
            "created_at": datetime.utcnow(),
            "results": {}
        }
        
        logger.info(f"ab_test_created test_id={test_id} variants={len(variants)}")
        
        return test_id
    
    def record_ab_test_result(
        self,
        test_id: str,
        variant_index: int,
        metric: str,
        value: float
    ) -> None:
        """
        Record result for an A/B test variant.
        
        Args:
            test_id: Test ID
            variant_index: Variant index
            metric: Metric name
            value: Metric value
        """
        if test_id not in self._ab_tests:
            logger.warning(f"ab_test_not_found test_id={test_id}")
            return
        
        if "results" not in self._ab_tests[test_id]:
            self._ab_tests[test_id]["results"] = {}
        
        variant_key = f"variant_{variant_index}"
        if variant_key not in self._ab_tests[test_id]["results"]:
            self._ab_tests[test_id]["results"][variant_key] = {}
        
        self._ab_tests[test_id]["results"][variant_key][metric] = value
        
        logger.info(f"ab_test_result_recorded test_id={test_id} variant={variant_index} metric={metric}")
    
    def get_recommendation_improvement(self) -> Dict[str, any]:
        """
        Get recommendation improvements based on learning.
        
        Returns:
            Dictionary of improvement recommendations
        """
        insights = self._learning_model.insights
        
        improvements = {
            "content_strategy": [],
            "caption_style": [],
            "timing": [],
            "platform_focus": []
        }
        
        for insight in insights:
            if insight.insight_type == "high_engagement":
                improvements["content_strategy"].append(insight.recommendation)
            elif insight.insight_type == "positive_sentiment":
                improvements["caption_style"].append("Use similar caption patterns")
            elif insight.insight_type == "posting_behavior":
                improvements["timing"].append("Post at similar times")
        
        return improvements
    
    def _anonymize_user_id(self, user_id: str) -> str:
        """Anonymize user ID for privacy."""
        import hashlib
        return hashlib.sha256(user_id.encode()).hexdigest()[:16]
    
    def get_learning_stats(self) -> Dict[str, any]:
        """Get learning system statistics."""
        return {
            "model_version": self._learning_model.model_version,
            "last_updated": self._learning_model.last_updated.isoformat(),
            "feedback_count": self._learning_model.feedback_count,
            "performance_count": self._learning_model.performance_count,
            "insights_count": len(self._learning_model.insights),
            "ab_tests_count": len(self._ab_tests),
            "model_weights": self._learning_model.model_weights
        }


# Singleton instance
feedback_learning_loop = FeedbackLearningLoop()
