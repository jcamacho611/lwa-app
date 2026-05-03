"""
Viral Hook Lab Engine v0

Generates and analyzes viral hooks for video content to maximize
engagement and shareability. Uses psychological triggers and
platform-specific optimization strategies.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import json
import re

logger = logging.getLogger(__name__)


class HookType(Enum):
    """Types of viral hooks."""
    
    QUESTION = "question"
    CONTROVERSY = "controversy"
    CURIOSITY = "curiosity"
    EMOTION = "emotion"
    SURPRISE = "surprise"
    AUTHORITY = "authority"
    SOCIAL_PROOF = "social_proof"
    SCARCITY = "scarcity"
    STORY = "story"
    CHALLENGE = "challenge"
    REVELATION = "revelation"
    COMPARISON = "comparison"


class PsychologicalTrigger(Enum):
    """Psychological triggers for viral content."""
    
    CURIOSITY_GAP = "curiosity_gap"
    SOCIAL_VALIDATION = "social_validation"
    FEAR_OF_MISSING_OUT = "fear_of_missing_out"
    EMOTIONAL_AROUSAL = "emotional_arousal"
    COGNITIVE_DISSONANCE = "cognitive_dissonance"
    RECIPROCITY = "reciprocity"
    AUTHORITY_BIAS = "authority_bias"
    SIMILARITY_ATTRACTION = "similarity_attraction"
    LOSS_AVERSION = "loss_aversion"
    PATTERN_INTERRUPT = "pattern_interrupt"


@dataclass
class HookRequest:
    """Request for viral hook generation."""
    
    content_topic: str
    target_audience: str
    platform: str
    content_type: str
    desired_emotion: str
    hook_types: List[HookType]
    max_length: int
    brand_voice: str
    constraints: List[str]
    goals: List[str]


@dataclass
class HookAnalysis:
    """Analysis of a viral hook."""
    
    hook_text: str
    hook_type: HookType
    psychological_triggers: List[PsychologicalTrigger]
    viral_score: float
    engagement_prediction: float
    shareability_prediction: float
    memorability_score: float
    platform_optimization: float
    emotional_impact: float
    cognitive_load: float
    compliance_factors: List[str]
    risk_factors: List[str]
    optimization_suggestions: List[str]


@dataclass
class ViralHookResult:
    """Result from viral hook generation."""
    
    primary_hook: HookAnalysis
    alternative_hooks: List[HookAnalysis]
    hook_strategy: str
    implementation_timeline: str
    testing_recommendations: List[str]
    performance_metrics: Dict[str, Any]
    confidence_score: float
    metadata: Dict[str, Any]


class ViralHookLabEngine:
    """
    Generates and analyzes viral hooks for maximum engagement.
    
    Uses psychological triggers, platform optimization, and
    viral content patterns to create high-performing hooks.
    """
    
    def __init__(self):
        self.name = "viral_hook_lab_engine"
        self.version = "1.0.0"
        
        # Hook templates by type
        self.hook_templates = {
            HookType.QUESTION: [
                "What if {topic} could {outcome}?",
                "Can you believe {shocking_statement}?",
                "Why does {phenomenon} happen?",
                "How much {quantity} is too much?",
                "What would happen if {scenario}?",
                "Is {claim} really true?",
                "Did you know that {surprising_fact}?"
            ],
            HookType.CONTROVERSY: [
                "{controversial_statement} that will shock you",
                "The truth about {topic} they don't want you to know",
                "{topic} is actually {controversial_claim}",
                "Why {group} hates {topic}",
                "{topic} vs {opposition}: The real winner",
                "The dark side of {topic}",
                "{topic} is destroying {thing}",
            ],
            HookType.CURIOSITY: [
                "The secret behind {topic} revealed",
                "What {authority_figure} doesn't want you to know about {topic}",
                "The hidden truth about {topic}",
                "{topic}: What they're not telling you",
                "The mystery of {phenomenon} solved",
                "Unlock the power of {topic}",
                "The {adjective} secret of {topic}",
            ],
            HookType.EMOTION: [
                "This {emotional_event} will make you {emotion}",
                "The most {emotion} {topic} you'll ever see",
                "When {topic} makes you {emotion}",
                "The {emotion} truth about {topic}",
                "Why {topic} makes everyone {emotion}",
                "Prepare to be {emotion} by this {topic}",
                "The {emotion} side of {topic}",
            ],
            HookType.SURPRISE: [
                "I can't believe {shocking_discovery}",
                "{unexpected_event} changed everything",
                "You won't believe what happened to {subject}",
                "{topic} just {unexpected_action}",
                "The shocking truth about {topic}",
                "{number} things about {topic} that will blow your mind",
                "Wait until you see what {subject} did",
            ],
            HookType.AUTHORITY: [
                "{authority_figure} reveals the truth about {topic}",
                "According to {expert}, {topic} is {claim}",
                "The {institution} study that changes everything about {topic}",
                "{authority_figure}'s warning about {topic}",
                "What {authority_figure} says about {topic}",
                "The {authority_figure} guide to {topic}",
                "{authority_figure} exposes {topic}",
            ],
            HookType.SOCIAL_PROOF: [
                "{number} people can't be wrong about {topic}",
                "Everyone is talking about {topic}",
                "Why {influencer} loves {topic}",
                "{percentage}% of {group} agree on {topic}",
                "The {topic} trend that's taking over",
                "Join {number} people who {action}",
                "{social_platform} is obsessed with {topic}",
            ],
            HookType.SCARCITY: [
                "Last chance to {opportunity}",
                "Only {number} days left to {action}",
                "This {topic} won't last long",
                "The disappearing {topic}",
                "Why {topic} is becoming extinct",
                "Get {topic} before it's gone",
                "The last {topic} you'll ever need",
            ],
            HookType.STORY: [
                "The day {subject} {dramatic_event}",
                "How {subject} went from {start} to {end}",
                "The untold story of {topic}",
                "{subject}'s journey to {achievement}",
                "The moment everything changed for {subject}",
                "Behind the scenes of {topic}",
                "The real story behind {topic}",
            ],
            HookType.CHALLENGE: [
                "I tried {challenge} for {duration} and this happened",
                "Can you {action} in {timeframe}?",
                "The {challenge} that changed my life",
                "I bet you can't {difficult_task}",
                "{challenge}: Day {number}",
                "Taking on the {challenge}",
                "The ultimate {challenge}",
            ],
            HookType.REVELATION: [
                "I finally figured out {topic}",
                "The breakthrough that changes {field}",
                "The discovery that will revolutionize {topic}",
                "What I learned about {topic}",
                "The {adjective} truth about {topic}",
                "My {number}-year journey to {achievement}",
                "The revelation about {topic}",
            ],
            HookType.COMPARISON: [
                "{topic} vs {alternative}: Which is better?",
                "Why {topic} beats {competition}",
                "{topic} vs {topic}: The ultimate showdown",
                "Is {topic} really better than {alternative}?",
                "Comparing {topic} and {alternative}",
                "{topic} or {alternative}: The choice is clear",
                "{topic} vs {alternative}: The results will shock you",
            ]
        }
        
        # Psychological triggers mapping
        self.trigger_mapping = {
            HookType.QUESTION: [PsychologicalTrigger.CURIOSITY_GAP, PsychologicalTrigger.PATTERN_INTERRUPT],
            HookType.CONTROVERSY: [PsychologicalTrigger.COGNITIVE_DISSONANCE, PsychologicalTrigger.EMOTIONAL_AROUSAL],
            HookType.CURIOSITY: [PsychologicalTrigger.CURIOSITY_GAP, PsychologicalTrigger.PATTERN_INTERRUPT],
            HookType.EMOTION: [PsychologicalTrigger.EMOTIONAL_AROUSAL, PsychologicalTrigger.SIMILARITY_ATTRACTION],
            HookType.SURPRISE: [PsychologicalTrigger.PATTERN_INTERRUPT, PsychologicalTrigger.EMOTIONAL_AROUSAL],
            HookType.AUTHORITY: [PsychologicalTrigger.AUTHORITY_BIAS, PsychologicalTrigger.SOCIAL_VALIDATION],
            HookType.SOCIAL_PROOF: [PsychologicalTrigger.SOCIAL_VALIDATION, PsychologicalTrigger.SIMILARITY_ATTRACTION],
            HookType.SCARCITY: [PsychologicalTrigger.FEAR_OF_MISSING_OUT, PsychologicalTrigger.LOSS_AVERSION],
            HookType.STORY: [PsychologicalTrigger.SIMILARITY_ATTRACTION, PsychologicalTrigger.EMOTIONAL_AROUSAL],
            HookType.CHALLENGE: [PsychologicalTrigger.SOCIAL_VALIDATION, PsychologicalTrigger.EMOTIONAL_AROUSAL],
            HookType.REVELATION: [PsychologicalTrigger.CURIOSITY_GAP, PsychologicalTrigger.AUTHORITY_BIAS],
            HookType.COMPARISON: [PsychologicalTrigger.COGNITIVE_DISSONANCE, PsychologicalTrigger.SOCIAL_VALIDATION],
        }
        
        # Platform-specific optimization
        self.platform_optimization = {
            "tiktok": {
                "max_length": 100,
                "preferred_hooks": [HookType.SURPRISE, HookType.EMOTION, HookType.CHALLENGE],
                "style": "casual, energetic, trend-focused",
                "keywords": ["viral", "trend", "challenge", "shock", "wow"]
            },
            "youtube": {
                "max_length": 150,
                "preferred_hooks": [HookType.QUESTION, HookType.CURIOSITY, HookType.AUTHORITY],
                "style": "informative, educational, authoritative",
                "keywords": ["truth", "secret", "revealed", "explained", "guide"]
            },
            "instagram": {
                "max_length": 120,
                "preferred_hooks": [HookType.EMOTION, HookType.STORY, HookType.SOCIAL_PROOF],
                "style": "inspirational, aesthetic, community-focused",
                "keywords": ["love", "inspire", "community", "beautiful", "journey"]
            },
            "twitter": {
                "max_length": 80,
                "preferred_hooks": [HookType.CONTROVERSY, HookType.COMPARISON, HookType.SURPRISE],
                "style": "provocative, debatable, news-focused",
                "keywords": ["breaking", "debate", "opinion", "analysis", "trending"]
            }
        }
        
        # Viral patterns
        self.viral_patterns = {
            "number_list": "{number} {things} about {topic}",
            "secret_reveal": "The secret {adjective} {topic}",
            "shocking_claim": "{topic} is actually {shocking_attribute}",
            "emotional_reaction": "This {topic} will make you {emotion}",
            "authority_backed": "{authority} says {topic} is {claim}",
            "curiosity_gap": "Why {topic} {unexpected_behavior}",
            "social_proof": "{number} people are {action} because {topic}",
            "scarcity_urgency": "Last chance to {action} with {topic}",
            "challenge_accepted": "I {challenge} for {duration} and {result}",
            "story_twist": "The day {subject} {unexpected_event}"
        }
        
        # Emotional words
        self.emotional_words = {
            "positive": ["amazing", "incredible", "beautiful", "wonderful", "fantastic", "love", "joy", "happy", "exciting", "thrilling"],
            "negative": ["shocking", "terrible", "horrible", "scary", "dangerous", "worst", "hate", "fear", "anger", "outrageous"],
            "surprise": ["unbelievable", "unexpected", "surprising", "shocking", "mind-blowing", "insane", "crazy", "wild", "insane"],
            "curiosity": ["secret", "hidden", "mystery", "unknown", "revealed", "exposed", "uncovered", "discovered", "found"],
            "authority": ["expert", "scientist", "doctor", "professor", "study", "research", "analysis", "data", "proof"]
        }
    
    async def generate_viral_hooks(self, request: HookRequest) -> ViralHookResult:
        """
        Generate viral hooks based on the request.
        
        Args:
            request: Hook generation request with all parameters
            
        Returns:
            ViralHookResult with generated hooks and analysis
        """
        
        try:
            # Analyze request for optimal hook types
            hook_analysis = await self._analyze_request(request)
            
            # Generate primary hook
            primary_hook = await self._generate_primary_hook(request, hook_analysis)
            
            # Generate alternative hooks
            alternative_hooks = await self._generate_alternative_hooks(request, hook_analysis)
            
            # Create hook strategy
            hook_strategy = await self._create_hook_strategy(request, hook_analysis)
            
            # Generate implementation timeline
            timeline = await self._generate_implementation_timeline(primary_hook)
            
            # Create testing recommendations
            testing_recommendations = await self._generate_testing_recommendations(request, primary_hook)
            
            # Calculate performance metrics
            performance_metrics = await self._calculate_performance_metrics(primary_hook, request)
            
            # Calculate confidence score
            confidence_score = await self._calculate_confidence_score(request, hook_analysis)
            
            return ViralHookResult(
                primary_hook=primary_hook,
                alternative_hooks=alternative_hooks,
                hook_strategy=hook_strategy,
                implementation_timeline=timeline,
                testing_recommendations=testing_recommendations,
                performance_metrics=performance_metrics,
                confidence_score=confidence_score,
                metadata={
                    "request_analysis": hook_analysis,
                    "generation_timestamp": datetime.utcnow().isoformat(),
                    "hook_count": len(alternative_hooks) + 1
                }
            )
            
        except Exception as e:
            logger.error(f"Viral hook generation failed: {e}")
            raise
    
    async def _analyze_request(self, request: HookRequest) -> Dict[str, Any]:
        """Analyze request to determine optimal approach."""
        
        analysis = {
            "optimal_hook_types": [],
            "emotional_angle": "",
            "authority_angle": "",
            "curiosity_angle": "",
            "controversy_angle": "",
            "platform_constraints": {},
            "content_keywords": [],
            "target_audience_psychology": "",
            "viral_potential": 0.5,
            "risk_level": "low"
        }
        
        # Extract keywords from topic
        topic_words = request.content_topic.lower().split()
        analysis["content_keywords"] = topic_words[:10]  # Top 10 keywords
        
        # Determine platform constraints
        platform_config = self.platform_optimization.get(request.platform, {})
        analysis["platform_constraints"] = {
            "max_length": platform_config.get("max_length", 100),
            "preferred_hooks": platform_config.get("preferred_hooks", []),
            "style": platform_config.get("style", "neutral"),
            "keywords": platform_config.get("keywords", [])
        }
        
        # Determine emotional angle
        for emotion, words in self.emotional_words.items():
            if any(word in topic_words for word in words):
                analysis["emotional_angle"] = emotion
                break
        
        # Determine authority angle
        for authority_word in self.emotional_words["authority"]:
            if authority_word in topic_words:
                analysis["authority_angle"] = authority_word
                break
        
        # Determine curiosity angle
        curiosity_words = self.emotional_words["curiosity"]
        if any(word in topic_words for word in curiosity_words):
            analysis["curiosity_angle"] = "high"
        
        # Determine controversy angle
        controversy_indicators = ["vs", "versus", "debate", "argument", "fight", "battle", "war"]
        if any(word in topic_words for word in controversy_indicators):
            analysis["controversy_angle"] = "high"
            analysis["risk_level"] = "medium"
        
        # Calculate viral potential
        viral_indicators = [
            len(analysis["emotional_angle"]) * 0.2,
            len(analysis["curiosity_angle"]) * 0.15,
            len(analysis["controversy_angle"]) * 0.1,
            len(request.hook_types) * 0.1,
            len(analysis["content_keywords"]) * 0.05
        ]
        
        analysis["viral_potential"] = min(1.0, sum(viral_indicators))
        
        # Determine optimal hook types
        if request.hook_types:
            analysis["optimal_hook_types"] = request.hook_types
        else:
            analysis["optimal_hook_types"] = analysis["platform_constraints"]["preferred_hooks"]
        
        return analysis
    
    async def _generate_primary_hook(
        self, request: HookRequest, analysis: Dict[str, Any]
    ) -> HookAnalysis:
        """Generate the primary viral hook."""
        
        # Select best hook type
        best_hook_type = analysis["optimal_hook_types"][0]
        
        # Generate hook text
        hook_text = await self._generate_hook_text(best_hook_type, request, analysis)
        
        # Analyze psychological triggers
        triggers = self.trigger_mapping.get(best_hook_type, [])
        
        # Calculate scores
        viral_score = await self._calculate_viral_score(hook_text, best_hook_type, analysis)
        engagement_prediction = await self._predict_engagement(hook_text, request.platform)
        shareability_prediction = await self._predict_shareability(hook_text, analysis)
        memorability_score = await self._calculate_memorability(hook_text)
        platform_optimization = await self._calculate_platform_optimization(hook_text, request.platform)
        emotional_impact = await self._calculate_emotional_impact(hook_text, analysis)
        cognitive_load = await self._calculate_cognitive_load(hook_text)
        
        # Generate compliance and risk factors
        compliance_factors = await self._generate_compliance_factors(hook_text, request.constraints)
        risk_factors = await self._generate_risk_factors(hook_text, best_hook_type)
        
        # Generate optimization suggestions
        optimization_suggestions = await self._generate_optimization_suggestions(hook_text, analysis)
        
        return HookAnalysis(
            hook_text=hook_text,
            hook_type=best_hook_type,
            psychological_triggers=triggers,
            viral_score=viral_score,
            engagement_prediction=engagement_prediction,
            shareability_prediction=shareability_prediction,
            memorability_score=memorability_score,
            platform_optimization=platform_optimization,
            emotional_impact=emotional_impact,
            cognitive_load=cognitive_load,
            compliance_factors=compliance_factors,
            risk_factors=risk_factors,
            optimization_suggestions=optimization_suggestions
        )
    
    async def _generate_hook_text(
        self, hook_type: HookType, request: HookRequest, analysis: Dict[str, Any]
    ) -> str:
        """Generate hook text for specific type."""
        
        templates = self.hook_templates[hook_type]
        template = templates[len(templates) % len(templates)]
        
        # Fill template with content
        filled_template = await self._fill_hook_template(template, request, analysis)
        
        # Optimize for platform
        max_length = analysis["platform_constraints"]["max_length"]
        if len(filled_template) > max_length:
            filled_template = filled_template[:max_length-3] + "..."
        
        return filled_template
    
    async def _fill_hook_template(
        self, template: str, request: HookRequest, analysis: Dict[str, Any]
    ) -> str:
        """Fill hook template with request content."""
        
        filled_template = template
        
        # Common replacements
        replacements = {
            "{topic}": request.content_topic,
            "{subject}": request.content_topic.split()[0] if request.content_topic else "this",
            "{phenomenon}": "this phenomenon",
            "{outcome}": "happen",
            "{scenario}": "this happens",
            "{claim}": "true",
            "{shocking_statement}": "this shocking truth",
            "{controversial_statement}": "this controversial claim",
            "{controversial_claim}": "not what you think",
            "{group}": "everyone",
            "{opposition}": "the alternative",
            "{shocking_discovery}": "I discovered",
            "{unexpected_event}": "this happened",
            "{unexpected_action}": "changed everything",
            "{authority_figure}": "experts",
            "{expert}": "researchers",
            "{institution}": "studies",
            "{number}": "5",
            "{percentage}": "80%",
            "{social_platform}": "people",
            "{influencer}": "creators",
            "{quantity}": "much",
            "{adjective}": "shocking",
            "{dramatic_event}": "everything changed",
            "{start}": "nothing",
            "{end}": "everything",
            "{achievement}": "success",
            "{difficult_task}": "this challenge",
            "{timeframe}": "30 days",
            "{duration}": "30 days",
            "{action}": "act now",
            "{opportunity}": "this chance",
            "{field}": "this area",
            "{alternative}": "the other option",
            "{competition}": "competitors",
            "{unexpected_behavior}": "does this",
            "{result}": "this happened"
        }
        
        for placeholder, replacement in replacements.items():
            filled_template = filled_template.replace(placeholder, replacement)
        
        return filled_template
    
    async def _generate_alternative_hooks(
        self, request: HookRequest, analysis: Dict[str, Any]
    ) -> List[HookAnalysis]:
        """Generate alternative hooks for testing."""
        
        alternative_hooks = []
        
        # Generate hooks for different types
        for hook_type in analysis["optimal_hook_types"][1:4]:  # Top 3 alternatives
            hook_text = await self._generate_hook_text(hook_type, request, analysis)
            triggers = self.trigger_mapping.get(hook_type, [])
            
            # Calculate scores
            viral_score = await self._calculate_viral_score(hook_text, hook_type, analysis)
            engagement_prediction = await self._predict_engagement(hook_text, request.platform)
            shareability_prediction = await self._predict_shareability(hook_text, analysis)
            memorability_score = await self._calculate_memorability(hook_text)
            platform_optimization = await self._calculate_platform_optimization(hook_text, request.platform)
            emotional_impact = await self._calculate_emotional_impact(hook_text, analysis)
            cognitive_load = await self._calculate_cognitive_load(hook_text)
            
            alternative_hooks.append(HookAnalysis(
                hook_text=hook_text,
                hook_type=hook_type,
                psychological_triggers=triggers,
                viral_score=viral_score,
                engagement_prediction=engagement_prediction,
                shareability_prediction=shareability_prediction,
                memorability_score=memorability_score,
                platform_optimization=platform_optimization,
                emotional_impact=emotional_impact,
                cognitive_load=cognitive_load,
                compliance_factors=[],
                risk_factors=[],
                optimization_suggestions=[]
            ))
        
        return alternative_hooks
    
    async def _calculate_viral_score(
        self, hook_text: str, hook_type: HookType, analysis: Dict[str, Any]
    ) -> float:
        """Calculate viral potential score for hook."""
        
        score = 0.5  # Base score
        
        # Hook type scoring
        type_scores = {
            HookType.QUESTION: 0.7,
            HookType.CONTROVERSY: 0.8,
            HookType.CURIOSITY: 0.75,
            HookType.EMOTION: 0.7,
            HookType.SURPRISE: 0.8,
            HookType.AUTHORITY: 0.6,
            HookType.SOCIAL_PROOF: 0.6,
            HookType.SCARCITY: 0.7,
            HookType.STORY: 0.6,
            HookType.CHALLENGE: 0.7,
            HookType.REVELATION: 0.75,
            HookType.COMPARISON: 0.6
        }
        
        score += type_scores.get(hook_type, 0.5) * 0.3
        
        # Length optimization
        optimal_length = analysis["platform_constraints"]["max_length"]
        length_ratio = len(hook_text) / optimal_length
        if 0.7 <= length_ratio <= 0.9:
            score += 0.1
        
        # Emotional words
        emotional_count = sum(1 for words in self.emotional_words.values() 
                            for word in words if word in hook_text.lower())
        score += min(0.2, emotional_count * 0.05)
        
        # Question marks (curiosity)
        if "?" in hook_text:
            score += 0.05
        
        # Numbers (specificity)
        if any(char.isdigit() for char in hook_text):
            score += 0.05
        
        # Platform keywords
        platform_keywords = analysis["platform_constraints"]["keywords"]
        keyword_count = sum(1 for keyword in platform_keywords if keyword in hook_text.lower())
        score += min(0.1, keyword_count * 0.03)
        
        return min(1.0, score)
    
    async def _predict_engagement(self, hook_text: str, platform: str) -> float:
        """Predict engagement rate for hook."""
        
        base_engagement = {
            "tiktok": 0.08,  # 8% engagement
            "youtube": 0.05,  # 5% engagement
            "instagram": 0.06,  # 6% engagement
            "twitter": 0.04   # 4% engagement
        }
        
        base_rate = base_engagement.get(platform, 0.05)
        
        # Engagement boosters
        boost = 0.0
        
        # Emotional content
        if any(word in hook_text.lower() for word in self.emotional_words["positive"] + self.emotional_words["negative"]):
            boost += 0.02
        
        # Questions increase engagement
        if "?" in hook_text:
            boost += 0.015
        
        # Numbers increase specificity
        if any(char.isdigit() for char in hook_text):
            boost += 0.01
        
        # Surprise words
        if any(word in hook_text.lower() for word in self.emotional_words["surprise"]):
            boost += 0.025
        
        return min(0.15, base_rate + boost)
    
    async def _predict_shareability(self, hook_text: str, analysis: Dict[str, Any]) -> float:
        """Predict shareability of hook."""
        
        base_shareability = 0.03  # 3% base share rate
        
        # Shareability boosters
        boost = 0.0
        
        # Controversy increases sharing
        if analysis["controversy_angle"] == "high":
            boost += 0.02
        
        # Surprise increases sharing
        if any(word in hook_text.lower() for word in self.emotional_words["surprise"]):
            boost += 0.015
        
        # Authority increases sharing
        if analysis["authority_angle"]:
            boost += 0.01
        
        # Curiosity increases sharing
        if analysis["curiosity_angle"] == "high":
            boost += 0.015
        
        # Social proof increases sharing
        if any(word in hook_text.lower() for word in ["everyone", "people", "viral", "trending"]):
            boost += 0.01
        
        return min(0.1, base_shareability + boost)
    
    async def _calculate_memorability(self, hook_text: str) -> float:
        """Calculate memorability score for hook."""
        
        memorability = 0.5  # Base memorability
        
        # Shorter hooks are more memorable
        if len(hook_text) < 50:
            memorability += 0.1
        elif len(hook_text) > 100:
            memorability -= 0.1
        
        # Questions are memorable
        if "?" in hook_text:
            memorability += 0.05
        
        # Numbers are memorable
        if any(char.isdigit() for char in hook_text):
            memorability += 0.05
        
        # Emotional words are memorable
        emotional_count = sum(1 for words in self.emotional_words.values() 
                            for word in words if word in hook_text.lower())
        memorability += min(0.1, emotional_count * 0.03)
        
        # Surprise words are memorable
        if any(word in hook_text.lower() for word in self.emotional_words["surprise"]):
            memorability += 0.05
        
        return min(1.0, memorability)
    
    async def _calculate_platform_optimization(self, hook_text: str, platform: str) -> float:
        """Calculate platform optimization score."""
        
        platform_config = self.platform_optimization.get(platform, {})
        
        optimization = 0.5  # Base optimization
        
        # Length optimization
        max_length = platform_config.get("max_length", 100)
        if len(hook_text) <= max_length:
            optimization += 0.2
        
        # Preferred hook types
        preferred_hooks = platform_config.get("preferred_hooks", [])
        # This would require analyzing the hook type, simplified for now
        optimization += 0.1
        
        # Platform keywords
        platform_keywords = platform_config.get("keywords", [])
        keyword_count = sum(1 for keyword in platform_keywords if keyword in hook_text.lower())
        optimization += min(0.2, keyword_count * 0.05)
        
        return min(1.0, optimization)
    
    async def _calculate_emotional_impact(self, hook_text: str, analysis: Dict[str, Any]) -> float:
        """Calculate emotional impact score."""
        
        impact = 0.3  # Base impact
        
        # Emotional words
        positive_count = sum(1 for word in self.emotional_words["positive"] if word in hook_text.lower())
        negative_count = sum(1 for word in self.emotional_words["negative"] if word in hook_text.lower())
        surprise_count = sum(1 for word in self.emotional_words["surprise"] if word in hook_text.lower())
        
        total_emotional = positive_count + negative_count + surprise_count
        impact += min(0.4, total_emotional * 0.1)
        
        # Emotional angle from analysis
        if analysis["emotional_angle"]:
            impact += 0.2
        
        return min(1.0, impact)
    
    async def _calculate_cognitive_load(self, hook_text: str) -> float:
        """Calculate cognitive load required to understand hook."""
        
        # Lower cognitive load is better for virality
        base_load = 0.5
        
        # Shorter hooks have lower cognitive load
        if len(hook_text) < 30:
            base_load -= 0.2
        elif len(hook_text) > 80:
            base_load += 0.2
        
        # Complex words increase cognitive load
        complex_words = ["phenomenon", "methodology", "implementation", "utilization", "conceptualization"]
        complex_count = sum(1 for word in complex_words if word in hook_text.lower())
        base_load += min(0.3, complex_count * 0.1)
        
        # Questions reduce cognitive load (they guide thinking)
        if "?" in hook_text:
            base_load -= 0.1
        
        # Numbers reduce cognitive load (they provide structure)
        if any(char.isdigit() for char in hook_text):
            base_load -= 0.05
        
        return max(0.1, min(1.0, base_load))
    
    async def _generate_compliance_factors(self, hook_text: str, constraints: List[str]) -> List[str]:
        """Generate compliance factors for hook."""
        
        compliance = []
        
        # Check for common compliance issues
        if any(word in hook_text.lower() for word in ["guarantee", "promise", "always", "never"]):
            compliance.append("Avoid absolute claims")
        
        if any(word in hook_text.lower() for word in ["free", "win", "prize", "giveaway"]):
            compliance.append("Be clear about terms and conditions")
        
        if any(word in hook_text.lower() for word in ["buy", "purchase", "discount", "sale"]):
            compliance.append("Follow advertising disclosure requirements")
        
        # Add constraint-specific compliance
        for constraint in constraints:
            compliance.append(f"Respect: {constraint}")
        
        return compliance
    
    async def _generate_risk_factors(self, hook_text: str, hook_type: HookType) -> List[str]:
        """Generate risk factors for hook."""
        
        risks = []
        
        # High-risk hook types
        if hook_type == HookType.CONTROVERSY:
            risks.append("Controversial content may attract negative attention")
            risks.append("May trigger platform content policies")
        
        if hook_type == HookType.SURPRISE:
            risks.append("Clickbait concerns if not delivered")
        
        # Risky words
        risky_words = ["fake", "scam", "illegal", "dangerous", "harmful"]
        if any(word in hook_text.lower() for word in risky_words):
            risks.append("Potentially problematic language")
        
        # Medical or legal claims
        medical_words = ["cure", "treatment", "diagnosis", "medicine", "health"]
        if any(word in hook_text.lower() for word in medical_words):
            risks.append("Medical claims require disclaimers")
        
        return risks
    
    async def _generate_optimization_suggestions(
        self, hook_text: str, analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate optimization suggestions for hook."""
        
        suggestions = []
        
        # Length suggestions
        max_length = analysis["platform_constraints"]["max_length"]
        if len(hook_text) > max_length * 0.9:
            suggestions.append(f"Consider shortening to under {max_length} characters")
        
        # Emotional suggestions
        if not analysis["emotional_angle"]:
            suggestions.append("Add emotional words to increase engagement")
        
        # Curiosity suggestions
        if "?" not in hook_text and "why" not in hook_text.lower():
            suggestions.append("Consider adding a question to increase curiosity")
        
        # Number suggestions
        if not any(char.isdigit() for char in hook_text):
            suggestions.append("Add specific numbers to increase credibility")
        
        # Platform-specific suggestions
        platform_keywords = analysis["platform_constraints"]["keywords"]
        if not any(keyword in hook_text.lower() for keyword in platform_keywords):
            suggestions.append(f"Consider using platform keywords: {', '.join(platform_keywords[:3])}")
        
        return suggestions
    
    async def _create_hook_strategy(
        self, request: HookRequest, analysis: Dict[str, Any]
    ) -> str:
        """Create overall hook strategy."""
        
        strategy_parts = []
        
        # Primary strategy
        strategy_parts.append(f"Focus on {analysis['emotional_angle'] or 'neutral'} emotional appeal")
        
        # Platform strategy
        strategy_parts.append(f"Optimize for {request.platform} with {analysis['platform_constraints']['style']} style")
        
        # Risk management
        if analysis["risk_level"] == "medium":
            strategy_parts.append("Balance controversy with compliance")
        
        # Testing strategy
        strategy_parts.append("Test multiple hook variations to optimize performance")
        
        return " | ".join(strategy_parts)
    
    async def _generate_implementation_timeline(self, primary_hook: HookAnalysis) -> str:
        """Generate implementation timeline for hook."""
        
        if primary_hook.platform_optimization > 0.8:
            return "Ready for immediate implementation"
        elif primary_hook.platform_optimization > 0.6:
            return "Minor optimizations needed (1-2 days)"
        else:
            return "Significant revisions required (3-5 days)"
    
    async def _generate_testing_recommendations(
        self, request: HookRequest, primary_hook: HookAnalysis
    ) -> List[str]:
        """Generate testing recommendations."""
        
        recommendations = []
        
        # A/B testing
        recommendations.append("A/B test primary hook against top 2 alternatives")
        
        # Platform testing
        recommendations.append(f"Test on {request.platform} first, then expand to other platforms")
        
        # Timing testing
        recommendations.append("Test posting at different times of day")
        
        # Performance monitoring
        recommendations.append("Monitor engagement, shares, and comments for 7 days")
        
        # Iteration
        recommendations.append("Iterate based on performance data")
        
        return recommendations
    
    async def _calculate_performance_metrics(
        self, primary_hook: HookAnalysis, request: HookRequest
    ) -> Dict[str, Any]:
        """Calculate expected performance metrics."""
        
        metrics = {
            "expected_engagement_rate": primary_hook.engagement_prediction,
            "expected_share_rate": primary_hook.shareability_prediction,
            "expected_memorability_score": primary_hook.memorability_score,
            "viral_potential": primary_hook.viral_score,
            "platform_optimization": primary_hook.platform_optimization,
            "emotional_impact": primary_hook.emotional_impact,
            "cognitive_load": primary_hook.cognitive_load,
            "risk_level": "low" if len(primary_hook.risk_factors) == 0 else "medium" if len(primary_hook.risk_factors) <= 2 else "high"
        }
        
        return metrics
    
    async def _calculate_confidence_score(
        self, request: HookRequest, analysis: Dict[str, Any]
    ) -> float:
        """Calculate confidence score for generated hooks."""
        
        confidence = 0.5  # Base confidence
        
        # Boost confidence based on request completeness
        if request.hook_types:
            confidence += 0.1
        
        if request.content_topic:
            confidence += 0.1
        
        if request.target_audience:
            confidence += 0.1
        
        # Boost confidence based on analysis quality
        if analysis["viral_potential"] > 0.7:
            confidence += 0.1
        
        if analysis["platform_constraints"]:
            confidence += 0.1
        
        return min(1.0, confidence)
    
    async def get_hook_recommendations(
        self, content_topic: str, platform: str, target_audience: str
    ) -> List[Dict[str, Any]]:
        """Get hook recommendations for content."""
        
        recommendations = []
        
        # Analyze content for hook opportunities
        content_lower = content_topic.lower()
        
        # Question hooks
        if any(word in content_lower for word in ["how", "what", "why", "when", "where"]):
            recommendations.append({
                "type": HookType.QUESTION,
                "reason": "Content contains question words",
                "confidence": 0.8,
                "priority": "high"
            })
        
        # Surprise hooks
        if any(word in content_lower for word in ["shocking", "surprising", "unexpected", "revealed"]):
            recommendations.append({
                "type": HookType.SURPRISE,
                "reason": "Content contains surprise elements",
                "confidence": 0.9,
                "priority": "high"
            })
        
        # Emotion hooks
        emotional_words = ["love", "hate", "happy", "sad", "angry", "excited", "scared"]
        if any(word in content_lower for word in emotional_words):
            recommendations.append({
                "type": HookType.EMOTION,
                "reason": "Content contains emotional elements",
                "confidence": 0.7,
                "priority": "medium"
            })
        
        # Authority hooks
        authority_words = ["expert", "study", "research", "scientist", "doctor", "professor"]
        if any(word in content_lower for word in authority_words):
            recommendations.append({
                "type": HookType.AUTHORITY,
                "reason": "Content contains authority elements",
                "confidence": 0.8,
                "priority": "medium"
            })
        
        # Platform-specific recommendations
        if platform == "tiktok":
            recommendations.append({
                "type": HookType.CHALLENGE,
                "reason": "TikTok favors challenge content",
                "confidence": 0.7,
                "priority": "medium"
            })
        
        return recommendations


# Singleton instance
viral_hook_lab_engine = ViralHookLabEngine()
