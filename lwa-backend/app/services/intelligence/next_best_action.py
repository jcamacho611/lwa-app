"""
Next-Best-Action Engine v0

Recommends the optimal next action for creators based on current state,
opportunity analysis, and historical performance. Part of the LWA Intelligence system.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import json

logger = logging.getLogger(__name__)


class ActionType(Enum):
    """Types of actions that can be recommended."""
    
    CREATE_CONTENT = "create_content"
    OPTIMIZE_CONTENT = "optimize_content"
    POST_CONTENT = "post_content"
    ENGAGE_AUDIENCE = "engage_audience"
    ANALYZE_PERFORMANCE = "analyze_performance"
    EXPAND_REACH = "expand_reach"
    MONETIZE = "monetize"
    COLLABORATE = "collaborate"
    LEARN_SKILL = "learn_skill"
    TAKE_BREAK = "take_break"


@dataclass
class ActionRecommendation:
    """Recommended action with details."""
    
    action_type: ActionType
    title: str
    description: str
    priority: float  # 0-100
    confidence: float  # 0-100
    estimated_impact: float  # 0-100
    time_required: int  # minutes
    resources_needed: List[str]
    expected_outcome: str
    reasoning: List[str]
    next_steps: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "action_type": self.action_type.value,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "confidence": self.confidence,
            "estimated_impact": self.estimated_impact,
            "time_required": self.time_required,
            "resources_needed": self.resources_needed,
            "expected_outcome": self.expected_outcome,
            "reasoning": self.reasoning,
            "next_steps": self.next_steps,
        }


@dataclass
class CreatorState:
    """Current state of the creator."""
    
    recent_posts: List[Dict[str, Any]]
    current_projects: List[Dict[str, Any]]
    performance_metrics: Dict[str, float]
    audience_growth: float
    engagement_rate: float
    revenue: float
    content_frequency: float
    skill_level: Dict[str, float]
    available_time: int  # minutes per day
    resources: List[str]
    goals: List[str]


class NextBestActionEngine:
    """
    Analyzes creator state and recommends the optimal next action.
    
    Uses opportunity analysis, performance data, and creator goals
    to suggest the most valuable next step.
    """
    
    def __init__(self):
        self.action_weights = {
            "opportunity_alignment": 0.35,
            "performance_gap": 0.25,
            "resource_availability": 0.20,
            "goal_alignment": 0.15,
            "timing_optimal": 0.05,
        }
        
        # Action templates
        self.action_templates = {
            ActionType.CREATE_CONTENT: {
                "high_performing": "Create {content_type} content about {topic}",
                "trending": "Create content about {trending_topic}",
                "audience_request": "Create {content_type} based on audience feedback",
            },
            ActionType.OPTIMIZE_CONTENT: {
                "underperforming": "Optimize underperforming {content_type}",
                "seo_improve": "Improve SEO for {content_type}",
                "engagement_boost": "Add engagement elements to {content_type}",
            },
            ActionType.POST_CONTENT: {
                "optimal_timing": "Post {content_type} at optimal time",
                "platform_specific": "Post {content_type} to {platform}",
                "frequency_maintain": "Maintain posting schedule",
            },
            ActionType.ENGAGE_AUDIENCE: {
                "respond_comments": "Respond to audience comments",
                "ask_questions": "Engage audience with questions",
                "run_poll": "Run audience poll for feedback",
            },
            ActionType.ANALYZE_PERFORMANCE: {
                "review_metrics": "Review performance metrics",
                "analyze_trends": "Analyze content performance trends",
                "competitor_analysis": "Analyze competitor strategies",
            },
            ActionType.EXPAND_REACH: {
                "new_platform": "Expand to {new_platform}",
                "collaboration": "Collaborate with {creator_type}",
                "cross_promotion": "Cross-promote with complementary creator",
            },
            ActionType.MONETIZE: {
                "affiliate_products": "Promote relevant affiliate products",
                "sponsor_content": "Create sponsored content",
                "merchandise": "Launch merchandise line",
            },
            ActionType.LEARN_SKILL: {
                "content_creation": "Learn {skill} for better content",
                "platform_algorithm": "Study {platform} algorithm changes",
                "audience_insights": "Learn audience analysis techniques",
            },
            ActionType.TAKE_BREAK: {
                "creative_recharge": "Take creative break to avoid burnout",
                "strategic_planning": "Plan content strategy during break",
                "skill_development": "Use break time for skill development",
            },
        }
    
    async def get_next_best_action(
        self,
        creator_state: CreatorState,
        market_opportunities: Optional[List[Dict[str, Any]]] = None,
        performance_history: Optional[List[Dict[str, Any]]] = None
    ) -> List[ActionRecommendation]:
        """
        Get recommended next actions for the creator.
        
        Args:
            creator_state: Current creator state and context
            market_opportunities: Available market opportunities
            performance_history: Historical performance data
            
        Returns:
            List of recommended actions sorted by priority
        """
        
        try:
            # Generate all potential actions
            all_actions = []
            
            # Analyze content creation opportunities
            content_actions = await self._analyze_content_opportunities(
                creator_state, market_opportunities or []
            )
            all_actions.extend(content_actions)
            
            # Analyze optimization opportunities
            optimization_actions = await self._analyze_optimization_opportunities(
                creator_state, performance_history or []
            )
            all_actions.extend(optimization_actions)
            
            # Analyze engagement opportunities
            engagement_actions = await self._analyze_engagement_opportunities(
                creator_state
            )
            all_actions.extend(engagement_actions)
            
            # Analyze growth opportunities
            growth_actions = await self._analyze_growth_opportunities(
                creator_state, market_opportunities or []
            )
            all_actions.extend(growth_actions)
            
            # Analyze monetization opportunities
            monetization_actions = await self._analyze_monetization_opportunities(
                creator_state
            )
            all_actions.extend(monetization_actions)
            
            # Sort by priority and return top recommendations
            sorted_actions = sorted(
                all_actions, 
                key=lambda x: x.priority, 
                reverse=True
            )
            
            return sorted_actions[:10]  # Return top 10 recommendations
            
        except Exception as e:
            logger.error(f"Next best action analysis failed: {e}")
            return []
    
    async def _analyze_content_opportunities(
        self, creator_state: CreatorState, market_opportunities: List[Dict[str, Any]]
    ) -> List[ActionRecommendation]:
        """Analyze content creation opportunities."""
        
        actions = []
        
        # Check for high-performing content types
        performance_metrics = creator_state.performance_metrics
        if performance_metrics:
            best_type = max(performance_metrics.keys(), 
                           key=lambda k: performance_metrics.get(k, {}).get("engagement_rate", 0))
            
            actions.append(ActionRecommendation(
                action_type=ActionType.CREATE_CONTENT,
                title=f"Create more {best_type} content",
                description=f"Your {best_type} content performs best. Create more to capitalize on this success.",
                priority=75.0,
                confidence=85.0,
                estimated_impact=80.0,
                time_required=60,
                resources_needed=["camera", "editing software"],
                expected_outcome="Higher engagement and audience growth",
                reasoning=[
                    f"{best_type} content has {performance_metrics[best_type].get('engagement_rate', 0):.1%} engagement",
                    "Audience responds well to this content type",
                    "Algorithm favors consistent content types"
                ],
                next_steps=[
                    "Research trending topics in your niche",
                    "Plan content structure and key points",
                    "Create and edit content",
                    "Post at optimal time"
                ]
            ))
        
        # Check for trending opportunities
        for opportunity in market_opportunities[:3]:  # Top 3 opportunities
            if opportunity.get("opportunity_score", 0) > 70:
                actions.append(ActionRecommendation(
                    action_type=ActionType.CREATE_CONTENT,
                    title=f"Create content about {opportunity.get('topic', 'trending topic')}",
                    description=f"High-opportunity topic with {opportunity.get('opportunity_score', 0):.0f} score",
                    priority=opportunity.get("opportunity_score", 0),
                    confidence=75.0,
                    estimated_impact=85.0,
                    time_required=90,
                    resources_needed=["research", "content creation tools"],
                    expected_outcome="Tap into trending audience interest",
                    reasoning=[
                        f"Topic has {opportunity.get('opportunity_score', 0):.0f} opportunity score",
                        f"Market growth rate: {opportunity.get('growth_rate', 0):.1%}",
                        "Low competition in this niche"
                    ],
                    next_steps=[
                        "Research topic thoroughly",
                        "Create unique angle or perspective",
                        "Produce high-quality content",
                        "Engage with audience responses"
                    ]
                ))
        
        return actions
    
    async def _analyze_optimization_opportunities(
        self, creator_state: CreatorState, performance_history: List[Dict[str, Any]]
    ) -> List[ActionRecommendation]:
        """Analyze content optimization opportunities."""
        
        actions = []
        
        # Find underperforming content
        recent_posts = creator_state.recent_posts
        if recent_posts:
            underperforming = [
                post for post in recent_posts 
                if post.get("engagement_rate", 0) < creator_state.engagement_rate * 0.8
            ]
            
            if underperforming:
                worst_performing = min(underperforming, 
                                   key=lambda x: x.get("engagement_rate", 0))
                
                actions.append(ActionRecommendation(
                    action_type=ActionType.OPTIMIZE_CONTENT,
                    title=f"Optimize underperforming {worst_performing.get('type', 'content')}",
                    description=f"This content has only {worst_performing.get('engagement_rate', 0):.1%} engagement",
                    priority=65.0,
                    confidence=80.0,
                    estimated_impact=60.0,
                    time_required=30,
                    resources_needed=["analytics", "editing tools"],
                    expected_outcome="Improve engagement of existing content",
                    reasoning=[
                        f"Content engagement is {worst_performing.get('engagement_rate', 0):.1%} below average",
                        "Optimization can recover performance",
                        "Algorithm may re-promote improved content"
                    ],
                    next_steps=[
                        "Analyze why content underperformed",
                        "Update thumbnail, title, or description",
                        "Add relevant hashtags or tags",
                        "Monitor performance after changes"
                    ]
                ))
        
        # Check for SEO improvements
        if creator_state.performance_metrics.get("search_traffic", 0) < 1000:
            actions.append(ActionRecommendation(
                action_type=ActionType.OPTIMIZE_CONTENT,
                title="Improve SEO for better discoverability",
                description="Low search traffic indicates SEO optimization needed",
                priority=70.0,
                confidence=75.0,
                estimated_impact=75.0,
                time_required=45,
                resources_needed=["keyword research tools", "analytics"],
                expected_outcome="Increased organic traffic and discoverability",
                reasoning=[
                    "Current search traffic is below optimal",
                    "SEO improvements have long-term benefits",
                    "Better discoverability leads to sustainable growth"
                ],
                next_steps=[
                    "Research relevant keywords in your niche",
                    "Update titles and descriptions with keywords",
                    "Optimize video tags and descriptions",
                    "Track search traffic improvements"
                ]
            ))
        
        return actions
    
    async def _analyze_engagement_opportunities(
        self, creator_state: CreatorState
    ) -> List[ActionRecommendation]:
        """Analyze audience engagement opportunities."""
        
        actions = []
        
        # Check for unanswered comments
        recent_posts = creator_state.recent_posts
        unanswered_comments = sum(
            post.get("unanswered_comments", 0) for post in recent_posts
        )
        
        if unanswered_comments > 10:
            actions.append(ActionRecommendation(
                action_type=ActionType.ENGAGE_AUDIENCE,
                title="Respond to audience comments",
                description=f"You have {unanswered_comments} unanswered comments",
                priority=80.0,
                confidence=90.0,
                estimated_impact=70.0,
                time_required=20,
                resources_needed=["social media access"],
                expected_outcome="Stronger community and higher engagement",
                reasoning=[
                    f"{unanswered_comments} comments need responses",
                    "Engagement builds community loyalty",
                    "Algorithm favors active creators"
                ],
                next_steps=[
                    "Review and respond to recent comments",
                    "Ask follow-up questions to encourage discussion",
                    "Thank audience for their engagement",
                    "Monitor for new comments"
                ]
            ))
        
        # Check for audience interaction patterns
        if creator_state.engagement_rate < 0.05:  # 5% engagement rate
            actions.append(ActionRecommendation(
                action_type=ActionType.ENGAGE_AUDIENCE,
                title="Boost audience engagement",
                description="Low engagement rate suggests need for more interaction",
                priority=75.0,
                confidence=80.0,
                estimated_impact=65.0,
                time_required=15,
                resources_needed=["content ideas"],
                expected_outcome="Higher engagement and community growth",
                reasoning=[
                    f"Current engagement rate is {creator_state.engagement_rate:.1%}",
                    "Higher engagement leads to better reach",
                    "Active audience is more valuable"
                ],
                next_steps=[
                    "Ask questions in your content",
                    "Run polls or surveys",
                    "Respond to comments promptly",
                    "Create interactive content"
                ]
            ))
        
        return actions
    
    async def _analyze_growth_opportunities(
        self, creator_state: CreatorState, market_opportunities: List[Dict[str, Any]]
    ) -> List[ActionRecommendation]:
        """Analyze growth and expansion opportunities."""
        
        actions = []
        
        # Check for platform expansion
        current_platforms = set(creator_state.performance_metrics.keys())
        all_platforms = {"tiktok", "instagram", "youtube", "twitter", "linkedin"}
        expansion_platforms = all_platforms - current_platforms
        
        if expansion_platforms and creator_state.audience_growth < 0.1:  # 10% monthly growth
            for platform in list(expansion_platforms)[:2]:  # Top 2 platforms
                actions.append(ActionRecommendation(
                    action_type=ActionType.EXPAND_REACH,
                    title=f"Expand to {platform.title()}",
                    description=f"New platform opportunity with potential audience growth",
                    priority=70.0,
                    confidence=70.0,
                    estimated_impact=75.0,
                    time_required=120,
                    resources_needed=[f"{platform} account", "content adaptation"],
                    expected_outcome="New audience and revenue streams",
                    reasoning=[
                        f"{platform.title()} has {market_opportunities[0].get('market_size', 0):.0f} users",
                        "Platform expansion diversifies revenue",
                        "Cross-platform presence increases brand authority"
                    ],
                    next_steps=[
                        f"Create {platform} account",
                        "Adapt content for platform format",
                        "Build initial content library",
                        "Promote across platforms"
                    ]
                ))
        
        # Check for collaboration opportunities
        if creator_state.audience_growth < 0.05:  # 5% monthly growth
            actions.append(ActionRecommendation(
                action_type=ActionType.COLLABORATE,
                title="Collaborate with complementary creators",
                description="Partnerships can significantly boost audience growth",
                priority=65.0,
                confidence=60.0,
                estimated_impact=80.0,
                time_required=180,
                resources_needed=["networking", "collaboration tools"],
                expected_outcome="Audience expansion and new content ideas",
                reasoning=[
                    "Slow audience growth indicates need for expansion",
                    "Collaborations expose you to new audiences",
                    "Partnerships can lead to long-term growth"
                ],
                next_steps=[
                    "Identify complementary creators in your niche",
                    "Reach out with collaboration proposals",
                    "Plan collaborative content",
                    "Promote collaboration across platforms"
                ]
            ))
        
        return actions
    
    async def _analyze_monetization_opportunities(
        self, creator_state: CreatorState
    ) -> List[ActionRecommendation]:
        """Analyze monetization opportunities."""
        
        actions = []
        
        # Check if creator is ready for monetization
        audience_size = creator_state.performance_metrics.get("total_followers", 0)
        engagement_rate = creator_state.engagement_rate
        
        if audience_size > 10000 and engagement_rate > 0.05 and creator_state.revenue < 100:
            actions.append(ActionRecommendation(
                action_type=ActionType.MONETIZE,
                title="Start monetization strategy",
                description="Your audience size and engagement support monetization",
                priority=80.0,
                confidence=85.0,
                estimated_impact=90.0,
                time_required=60,
                resources_needed=["monetization platform", "sponsor contacts"],
                expected_outcome="Generate revenue from your content",
                reasoning=[
                    f"Audience size: {audience_size:,} followers",
                    f"Engagement rate: {engagement_rate:.1%}",
                    "Current revenue is below potential"
                ],
                next_steps=[
                    "Research monetization options",
                    "Set up sponsor or affiliate partnerships",
                    "Create monetization strategy",
                    "Track revenue performance"
                ]
            ))
        
        # Check for affiliate opportunities
        if creator_state.skill_level.get("product_reviews", 0) > 0.7:
            actions.append(ActionRecommendation(
                action_type=ActionType.MONETIZE,
                title="Add affiliate marketing",
                description="Your product review skills can generate affiliate revenue",
                priority=70.0,
                confidence=75.0,
                estimated_impact=60.0,
                time_required=30,
                resources_needed=["affiliate programs", "disclosure compliance"],
                expected_outcome="Additional revenue stream",
                reasoning=[
                    "Strong product review skills identified",
                    "Affiliate marketing fits your content style",
                    "Low barrier to entry"
                ],
                next_steps=[
                    "Join relevant affiliate programs",
                    "Create disclosure statements",
                    "Integrate affiliate links naturally",
                    "Track affiliate performance"
                ]
            ))
        
        return actions
    
    async def get_action_performance_feedback(
        self, action: ActionRecommendation, actual_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get feedback on action performance to improve future recommendations.
        
        Args:
            action: The action that was taken
            actual_results: Results from implementing the action
            
        Returns:
            Performance feedback and learning insights
        """
        
        feedback = {
            "action_type": action.action_type.value,
            "predicted_impact": action.estimated_impact,
            "actual_impact": actual_results.get("impact_score", 0),
            "accuracy": abs(action.estimated_impact - actual_results.get("impact_score", 0)),
            "success": actual_results.get("success", False),
            "lessons_learned": [],
            "recommendation_adjustments": []
        }
        
        # Analyze prediction accuracy
        if feedback["accuracy"] < 20:
            feedback["lessons_learned"].append("High prediction accuracy - maintain current model")
        elif feedback["accuracy"] < 40:
            feedback["lessons_learned"].append("Moderate prediction accuracy - model working well")
        else:
            feedback["lessons_learned"].append("Low prediction accuracy - model needs adjustment")
            feedback["recommendation_adjustments"].append("Adjust confidence scores for similar actions")
        
        # Analyze success factors
        if actual_results.get("success", False):
            feedback["lessons_learned"].append("Action was successful - increase priority for similar recommendations")
        else:
            feedback["lessons_learned"].append("Action was unsuccessful - analyze failure factors")
            feedback["recommendation_adjustments"].append("Reduce priority for similar actions")
        
        return feedback


# Singleton instance
next_best_action_engine = NextBestActionEngine()
