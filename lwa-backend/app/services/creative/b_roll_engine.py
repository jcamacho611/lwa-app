"""
B Roll Scene Engine v0

Generates B-roll scenes and supplementary footage for video content.
Enhances main content with contextual, aesthetic, and engaging B-roll footage.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import json
import os

logger = logging.getLogger(__name__)


class BRollType(Enum):
    """Types of B-roll footage."""
    
    CONTEXTUAL = "contextual"
    AESTHETIC = "aesthetic"
    DEMONSTRATION = "demonstration"
    EMOTIONAL = "emotional"
    TRANSITIONAL = "transitional"
    TECHNICAL = "technical"
    STOCK = "stock"
    GENERATED = "generated"


class SceneComplexity(Enum):
    """Complexity levels for B-roll scenes."""
    
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    PROFESSIONAL = "professional"


@dataclass
class BRollRequest:
    """Request for B-roll scene generation."""
    
    main_content: str
    content_type: str
    target_duration: float
    b_roll_types: List[BRollType]
    style_preference: str
    brand_guidelines: Dict[str, Any]
    platform_requirements: Dict[str, Any]
    budget_constraints: Optional[float]
    quality_level: str
    include_music: bool
    include_sound_effects: bool


@dataclass
class SceneDescription:
    """Description of a B-roll scene."""
    
    scene_type: BRollType
    description: str
    duration: float
    complexity: SceneComplexity
    visual_elements: List[str]
    audio_elements: List[str]
    transition_type: str
    camera_movements: List[str]
    lighting_style: str
    color_grading: str
    props_needed: List[str]
    location_type: str


@dataclass
class BRollResult:
    """Result from B-roll scene generation."""
    
    scenes: List[SceneDescription]
    total_duration: float
    estimated_cost: float
    production_timeline: str
    technical_requirements: List[str]
    resource_needs: Dict[str, Any]
    creative_direction: str
    confidence_score: float
    metadata: Dict[str, Any]


class BRollSceneEngine:
    """
    Generates B-roll scenes and supplementary footage.
    
    Creates contextual, aesthetic, and engaging B-roll content
    to enhance main video footage.
    """
    
    def __init__(self):
        self.name = "b_roll_scene_engine"
        self.version = "1.0.0"
        
        # Scene templates
        self.scene_templates = {
            BRollType.CONTEXTUAL: {
                "description_templates": [
                    "Close-up of {subject} showing {detail}",
                    "Wide shot of {location} with {activity}",
                    "Medium shot focusing on {element}",
                    "Detail shot of {object} in {context}"
                ],
                "duration_range": (2.0, 8.0),
                "complexity": SceneComplexity.MODERATE,
                "common_elements": ["context", "environment", "subject"]
            },
            BRollType.AESTHETIC: {
                "description_templates": [
                    "Slow-motion shot of {subject} with {effect}",
                    "Time-lapse of {scene} showing {progression}",
                    "Artistic composition of {object} with {style}",
                    "Abstract visualization of {concept}"
                ],
                "duration_range": (3.0, 10.0),
                "complexity": SceneComplexity.COMPLEX,
                "common_elements": ["beauty", "artistry", "emotion"]
            },
            BRollType.DEMONSTRATION: {
                "description_templates": [
                    "Step-by-step demonstration of {process}",
                    "Close-up showing {technique} in action",
                    "Before/after comparison of {transformation}",
                    "Technical breakdown of {system}"
                ],
                "duration_range": (4.0, 12.0),
                "complexity": SceneComplexity.MODERATE,
                "common_elements": ["action", "process", "result"]
            },
            BRollType.EMOTIONAL: {
                "description_templates": [
                    "Emotional reaction to {situation}",
                    "Atmospheric shot of {mood} setting",
                    "Character moment showing {feeling}",
                    "Symbolic imagery representing {emotion}"
                ],
                "duration_range": (2.0, 6.0),
                "complexity": SceneComplexity.SIMPLE,
                "common_elements": ["emotion", "mood", "character"]
            },
            BRollType.TRANSITIONAL: {
                "description_templates": [
                    "Smooth transition from {scene_a} to {scene_b}",
                    "Match cut connecting {concept_a} and {concept_b}",
                    "Wipe transition showing {progression}",
                    "Cross-fade between {time_period_a} and {time_period_b}"
                ],
                "duration_range": (1.0, 3.0),
                "complexity": SceneComplexity.SIMPLE,
                "common_elements": ["transition", "flow", "connection"]
            },
            BRollType.TECHNICAL: {
                "description_templates": [
                    "Technical close-up of {component}",
                    "Diagram showing {system} functionality",
                    "Screen recording of {interface}",
                    "Animated explanation of {process}"
                ],
                "duration_range": (3.0, 8.0),
                "complexity": SceneComplexity.PROFESSIONAL,
                "common_elements": ["technology", "interface", "process"]
            },
            BRollType.STOCK: {
                "description_templates": [
                    "Stock footage of {category} scene",
                    "Archival material showing {historical_event}",
                    "Generic shot of {common_situation}",
                    "Stock animation of {concept}"
                ],
                "duration_range": (2.0, 6.0),
                "complexity": SceneComplexity.SIMPLE,
                "common_elements": ["stock", "generic", "archival"]
            },
            BRollType.GENERATED: {
                "description_templates": [
                    "AI-generated visualization of {concept}",
                    "Computer-generated animation of {process}",
                    "Digital recreation of {historical_scene}",
                    "Synthetic footage of {imagined_scenario}"
                ],
                "duration_range": (3.0, 8.0),
                "complexity": SceneComplexity.COMPLEX,
                "common_elements": ["generated", "digital", "synthetic"]
            }
        }
        
        # Camera movements
        self.camera_movements = {
            "static": "Static shot - no camera movement",
            "pan": "Pan - horizontal camera movement",
            "tilt": "Tilt - vertical camera movement",
            "dolly": "Dolly - camera moves forward/backward",
            "zoom": "Zoom - focal length change",
            "tracking": "Tracking - camera follows subject",
            "handheld": "Handheld - natural camera movement",
            "crane": "Crane - elevated camera movement",
            "steadicam": "Steadicam - smooth camera movement"
        }
        
        # Lighting styles
        self.lighting_styles = {
            "natural": "Natural lighting - soft, authentic",
            "dramatic": "Dramatic lighting - high contrast",
            "soft": "Soft lighting - gentle, flattering",
            "hard": "Hard lighting - sharp shadows",
            "studio": "Studio lighting - controlled, professional",
            "available": "Available light - practical lighting",
            "motivated": "Motivated light - story-driven lighting",
            "practical": "Practical lighting - functional light sources"
        }
        
        # Color grading presets
        self.color_grading_presets = {
            "natural": "Natural color - realistic tones",
            "warm": "Warm color - orange/yellow tones",
            "cool": "Cool color - blue/green tones",
            "vintage": "Vintage color - aged, film-like",
            "cinematic": "Cinematic color - film emulation",
            "high_contrast": "High contrast - dramatic tones",
            "pastel": "Pastel color - soft, muted tones",
            "monochrome": "Monochrome - black and white"
        }
    
    async def generate_b_roll_scenes(self, request: BRollRequest) -> BRollResult:
        """
        Generate B-roll scenes based on the request.
        
        Args:
            request: B-roll generation request with all parameters
            
        Returns:
            BRollResult with generated scene descriptions
        """
        
        try:
            # Analyze main content for B-roll opportunities
            content_analysis = await self._analyze_content(request)
            
            # Generate scene descriptions
            scenes = await self._generate_scenes(request, content_analysis)
            
            # Calculate production requirements
            production_requirements = await self._calculate_production_requirements(scenes, request)
            
            # Estimate costs and timeline
            cost_estimate = await self._estimate_cost(scenes, request)
            timeline = await self._estimate_timeline(scenes, request)
            
            # Generate creative direction
            creative_direction = await self._generate_creative_direction(request, content_analysis)
            
            # Calculate confidence score
            confidence_score = await self._calculate_confidence_score(request, content_analysis)
            
            return BRollResult(
                scenes=scenes,
                total_duration=sum(scene.duration for scene in scenes),
                estimated_cost=cost_estimate,
                production_timeline=timeline,
                technical_requirements=production_requirements["technical"],
                resource_needs=production_requirements["resources"],
                creative_direction=creative_direction,
                confidence_score=confidence_score,
                metadata={
                    "content_analysis": content_analysis,
                    "request_timestamp": datetime.utcnow().isoformat(),
                    "scene_count": len(scenes)
                }
            )
            
        except Exception as e:
            logger.error(f"B-roll scene generation failed: {e}")
            raise
    
    async def _analyze_content(self, request: BRollRequest) -> Dict[str, Any]:
        """Analyze main content to identify B-roll opportunities."""
        
        analysis = {
            "key_concepts": [],
            "visual_elements": [],
            "emotional_beats": [],
            "technical_elements": [],
            "transitional_points": [],
            "contextual_elements": [],
            "complexity_score": 0.5,
            "content_themes": []
        }
        
        # Extract key concepts from content
        content_words = request.main_content.lower().split()
        
        # Identify visual elements
        visual_keywords = [
            "show", "demonstrate", "display", "reveal", "present", "illustrate",
            "visual", "image", "picture", "video", "footage", "scene", "shot"
        ]
        
        analysis["visual_elements"] = [
            word for word in content_words if word in visual_keywords
        ][:5]
        
        # Identify emotional beats
        emotional_keywords = {
            "excitement": ["exciting", "amazing", "incredible", "wow", "thrilling"],
            "curiosity": ["curious", "mystery", "secret", "unknown", "discover"],
            "concern": ["worry", "concern", "problem", "issue", "challenge"],
            "joy": ["happy", "joy", "celebration", "success", "achievement"],
            "surprise": ["surprising", "unexpected", "shocking", "sudden"]
        }
        
        for emotion, words in emotional_keywords.items():
            if any(word in content_words for word in words):
                analysis["emotional_beats"].append(emotion)
        
        # Identify technical elements
        technical_keywords = [
            "technology", "software", "hardware", "system", "process", "method",
            "technique", "algorithm", "code", "data", "analysis", "research"
        ]
        
        analysis["technical_elements"] = [
            word for word in content_words if word in technical_keywords
        ][:3]
        
        # Identify transitional points
        transition_keywords = [
            "then", "next", "after", "before", "during", "while", "however",
            "therefore", "because", "although", "finally", "ultimately"
        ]
        
        analysis["transitional_points"] = [
            word for word in content_words if word in transition_keywords
        ][:3]
        
        # Identify contextual elements
        contextual_keywords = [
            "location", "environment", "setting", "background", "context",
            "situation", "circumstance", "condition", "state", "status"
        ]
        
        analysis["contextual_elements"] = [
            word for word in content_words if word in contextual_keywords
        ][:3]
        
        # Calculate complexity score
        complexity_indicators = [
            len(analysis["technical_elements"]) * 0.2,
            len(analysis["visual_elements"]) * 0.1,
            len(request.main_content.split()) / 100 * 0.1
        ]
        
        analysis["complexity_score"] = min(1.0, sum(complexity_indicators))
        
        # Extract content themes
        theme_keywords = {
            "technology": ["tech", "digital", "software", "hardware", "computer"],
            "education": ["learn", "teach", "study", "education", "knowledge"],
            "entertainment": ["fun", "entertainment", "enjoy", "play", "game"],
            "business": ["business", "work", "career", "professional", "company"],
            "lifestyle": ["life", "living", "health", "fitness", "wellness"]
        }
        
        for theme, words in theme_keywords.items():
            if any(word in content_words for word in words):
                analysis["content_themes"].append(theme)
        
        return analysis
    
    async def _generate_scenes(
        self, request: BRollRequest, analysis: Dict[str, Any]
    ) -> List[SceneDescription]:
        """Generate scene descriptions based on content analysis."""
        
        scenes = []
        remaining_duration = request.target_duration
        
        for b_roll_type in request.b_roll_types:
            if remaining_duration <= 0:
                break
            
            template = self.scene_templates[b_roll_type]
            
            # Calculate number of scenes for this type
            type_duration = sum(
                await self._generate_single_scene(b_roll_type, request, analysis, template)
                for _ in range(2)  # Generate 2 scenes per type initially
            )
            
            if type_duration <= remaining_duration:
                # Generate scenes for this type
                type_scenes = await self._generate_scenes_for_type(
                    b_roll_type, request, analysis, remaining_duration
                )
                scenes.extend(type_scenes)
                remaining_duration -= sum(scene.duration for scene in type_scenes)
        
        return scenes
    
    async def _generate_scenes_for_type(
        self, b_roll_type: BRollType, request: BRollRequest,
        analysis: Dict[str, Any], available_duration: float
    ) -> List[SceneDescription]:
        """Generate scenes for a specific B-roll type."""
        
        template = self.scene_templates[b_roll_type]
        scenes = []
        
        # Calculate optimal number of scenes
        avg_duration = sum(template["duration_range"]) / 2
        max_scenes = int(available_duration / avg_duration)
        
        for i in range(min(max_scenes, 3)):  # Max 3 scenes per type
            scene = await self._generate_single_scene(
                b_roll_type, request, analysis, template
            )
            scenes.append(scene)
        
        return scenes
    
    async def _generate_single_scene(
        self, b_roll_type: BRollType, request: BRollRequest,
        analysis: Dict[str, Any], template: Dict[str, Any]
    ) -> SceneDescription:
        """Generate a single scene description."""
        
        # Select template
        description_templates = template["description_templates"]
        template_text = description_templates[len(description_templates) % len(description_templates)]
        
        # Fill template with content elements
        description = await self._fill_template(template_text, analysis, b_roll_type)
        
        # Determine duration
        duration_range = template["duration_range"]
        duration = duration_range[0] + (duration_range[1] - duration_range[0]) * 0.5
        
        # Select visual elements
        visual_elements = await self._select_visual_elements(b_roll_type, analysis)
        
        # Select audio elements
        audio_elements = await self._select_audio_elements(b_roll_type, request)
        
        # Select camera movement
        camera_movement = await self._select_camera_movement(b_roll_type, analysis)
        
        # Select lighting style
        lighting_style = await self._select_lighting_style(b_roll_type, request.style_preference)
        
        # Select color grading
        color_grading = await self._select_color_grading(b_roll_type, request.brand_guidelines)
        
        # Determine props and location
        props_needed = await self._determine_props(b_roll_type, analysis)
        location_type = await self._determine_location(b_roll_type, analysis)
        
        # Select transition type
        transition_type = await self._select_transition_type(b_roll_type)
        
        return SceneDescription(
            scene_type=b_roll_type,
            description=description,
            duration=duration,
            complexity=template["complexity"],
            visual_elements=visual_elements,
            audio_elements=audio_elements,
            transition_type=transition_type,
            camera_movements=[camera_movement],
            lighting_style=lighting_style,
            color_grading=color_grading,
            props_needed=props_needed,
            location_type=location_type
        )
    
    async def _fill_template(
        self, template: str, analysis: Dict[str, Any], b_roll_type: BRollType
    ) -> str:
        """Fill template with content analysis elements."""
        
        filled_template = template
        
        # Replace placeholders with actual content
        replacements = {
            "{subject}": self._get_subject_from_analysis(analysis),
            "{detail}": self._get_detail_from_analysis(analysis),
            "{location}": self._get_location_from_analysis(analysis),
            "{activity}": self._get_activity_from_analysis(analysis),
            "{element}": self._get_element_from_analysis(analysis),
            "{object}": self._get_object_from_analysis(analysis),
            "{context}": self._get_context_from_analysis(analysis),
            "{scene}": self._get_scene_from_analysis(analysis),
            "{progression}": self._get_progression_from_analysis(analysis),
            "{style}": self._get_style_from_analysis(analysis),
            "{concept}": self._get_concept_from_analysis(analysis),
            "{process}": self._get_process_from_analysis(analysis),
            "{technique}": self._get_technique_from_analysis(analysis),
            "{system}": self._get_system_from_analysis(analysis),
            "{interface}": self._get_interface_from_analysis(analysis),
            "{situation}": self._get_situation_from_analysis(analysis),
            "{mood}": self._get_mood_from_analysis(analysis),
            "{feeling}": self._get_feeling_from_analysis(analysis),
            "{emotion}": self._get_emotion_from_analysis(analysis),
            "{scene_a}": "previous scene",
            "{scene_b}": "next scene",
            "{concept_a}": "previous concept",
            "{concept_b}": "next concept",
            "{time_period_a}": "earlier period",
            "{time_period_b}": "later period",
            "{category}": self._get_category_from_analysis(analysis),
            "{historical_event}": "historical moment",
            "{common_situation}": "everyday scenario",
            "{imagined_scenario}": "creative vision"
        }
        
        for placeholder, replacement in replacements.items():
            filled_template = filled_template.replace(placeholder, replacement)
        
        return filled_template
    
    def _get_subject_from_analysis(self, analysis: Dict[str, Any]) -> str:
        """Get subject from content analysis."""
        if analysis["visual_elements"]:
            return analysis["visual_elements"][0]
        return "main subject"
    
    def _get_detail_from_analysis(self, analysis: Dict[str, Any]) -> str:
        """Get detail from content analysis."""
        return "important detail"
    
    def _get_location_from_analysis(self, analysis: Dict[str, Any]) -> str:
        """Get location from content analysis."""
        if analysis["contextual_elements"]:
            return analysis["contextual_elements"][0]
        return "relevant location"
    
    def _get_activity_from_analysis(self, analysis: Dict[str, Any]) -> str:
        """Get activity from content analysis."""
        return "key activity"
    
    def _get_element_from_analysis(self, analysis: Dict[str, Any]) -> str:
        """Get element from content analysis."""
        if analysis["visual_elements"]:
            return analysis["visual_elements"][0]
        return "visual element"
    
    def _get_object_from_analysis(self, analysis: Dict[str, Any]) -> str:
        """Get object from content analysis."""
        return "relevant object"
    
    def _get_context_from_analysis(self, analysis: Dict[str, Any]) -> str:
        """Get context from content analysis."""
        if analysis["contextual_elements"]:
            return analysis["contextual_elements"][0]
        return "contextual setting"
    
    def _get_scene_from_analysis(self, analysis: Dict[str, Any]) -> str:
        """Get scene from content analysis."""
        return "key scene"
    
    def _get_progression_from_analysis(self, analysis: Dict[str, Any]) -> str:
        """Get progression from content analysis."""
        return "progression"
    
    def _get_style_from_analysis(self, analysis: Dict[str, Any]) -> str:
        """Get style from content analysis."""
        return "stylistic approach"
    
    def _get_concept_from_analysis(self, analysis: Dict[str, Any]) -> str:
        """Get concept from content analysis."""
        if analysis["content_themes"]:
            return analysis["content_themes"][0]
        return "key concept"
    
    def _get_process_from_analysis(self, analysis: Dict[str, Any]) -> str:
        """Get process from content analysis."""
        if analysis["technical_elements"]:
            return analysis["technical_elements"][0]
        return "process"
    
    def _get_technique_from_analysis(self, analysis: Dict[str, Any]) -> str:
        """Get technique from content analysis."""
        return "technique"
    
    def _get_system_from_analysis(self, analysis: Dict[str, Any]) -> str:
        """Get system from content analysis."""
        if analysis["technical_elements"]:
            return analysis["technical_elements"][0]
        return "system"
    
    def _get_interface_from_analysis(self, analysis: Dict[str, Any]) -> str:
        """Get interface from content analysis."""
        return "interface"
    
    def _get_situation_from_analysis(self, analysis: Dict[str, Any]) -> str:
        """Get situation from content analysis."""
        return "situation"
    
    def _get_mood_from_analysis(self, analysis: Dict[str, Any]) -> str:
        """Get mood from content analysis."""
        if analysis["emotional_beats"]:
            return analysis["emotional_beats"][0]
        return "mood"
    
    def _get_feeling_from_analysis(self, analysis: Dict[str, Any]) -> str:
        """Get feeling from content analysis."""
        if analysis["emotional_beats"]:
            return analysis["emotional_beats"][0]
        return "feeling"
    
    def _get_emotion_from_analysis(self, analysis: Dict[str, Any]) -> str:
        """Get emotion from content analysis."""
        if analysis["emotional_beats"]:
            return analysis["emotional_beats"][0]
        return "emotion"
    
    def _get_category_from_analysis(self, analysis: Dict[str, Any]) -> str:
        """Get category from content analysis."""
        if analysis["content_themes"]:
            return analysis["content_themes"][0]
        return "category"
    
    async def _select_visual_elements(
        self, b_roll_type: BRollType, analysis: Dict[str, Any]
    ) -> List[str]:
        """Select visual elements for B-roll type."""
        
        template = self.scene_templates[b_roll_type]
        base_elements = template["common_elements"]
        
        # Add analysis-specific elements
        if b_roll_type == BRollType.CONTEXTUAL:
            base_elements.extend(analysis["contextual_elements"])
        elif b_roll_type == BRollType.TECHNICAL:
            base_elements.extend(analysis["technical_elements"])
        elif b_roll_type == BRollType.EMOTIONAL:
            base_elements.extend(analysis["emotional_beats"])
        
        return list(set(base_elements))[:5]  # Return top 5 unique elements
    
    async def _select_audio_elements(
        self, b_roll_type: BRollType, request: BRollRequest
    ) -> List[str]:
        """Select audio elements for B-roll type."""
        
        audio_elements = []
        
        if request.include_music:
            audio_elements.append("background_music")
        
        if request.include_sound_effects:
            if b_roll_type == BRollType.DEMONSTRATION:
                audio_elements.extend(["process_sounds", "interaction_sounds"])
            elif b_roll_type == BRollType.EMOTIONAL:
                audio_elements.append("emotional_score")
            elif b_roll_type == BRollType.TRANSITIONAL:
                audio_elements.append("transition_sounds")
        
        return audio_elements
    
    async def _select_camera_movement(
        self, b_roll_type: BRollType, analysis: Dict[str, Any]
    ) -> str:
        """Select camera movement for B-roll type."""
        
        # Default camera movements by type
        type_movements = {
            BRollType.CONTEXTUAL: ["static", "pan", "tilt"],
            BRollType.AESTHETIC: ["dolly", "tracking", "crane"],
            BRollType.DEMONSTRATION: ["static", "zoom", "tracking"],
            BRollType.EMOTIONAL: ["handheld", "steadicam"],
            BRollType.TRANSITIONAL: ["pan", "tilt", "dolly"],
            BRollType.TECHNICAL: ["static", "zoom"],
            BRollType.STOCK: ["static", "pan"],
            BRollType.GENERATED: ["tracking", "crane"]
        }
        
        available_movements = type_movements.get(b_roll_type, ["static"])
        
        # Select based on complexity
        if analysis["complexity_score"] > 0.7:
            return available_movements[-1]  # Most complex movement
        else:
            return available_movements[0]  # Simple movement
    
    async def _select_lighting_style(
        self, b_roll_type: BRollType, style_preference: str
    ) -> str:
        """Select lighting style for B-roll type."""
        
        # Style-based lighting preferences
        style_lighting = {
            "professional": "studio",
            "cinematic": "dramatic",
            "natural": "natural",
            "artistic": "soft",
            "technical": "studio"
        }
        
        return style_lighting.get(style_preference, "natural")
    
    async def _select_color_grading(
        self, b_roll_type: BRollType, brand_guidelines: Dict[str, Any]
    ) -> str:
        """Select color grading for B-roll type."""
        
        # Use brand guidelines if available
        if "color_profile" in brand_guidelines:
            return brand_guidelines["color_profile"]
        
        # Default grading by type
        type_grading = {
            BRollType.CONTEXTUAL: "natural",
            BRollType.AESTHETIC: "cinematic",
            BRollType.DEMONSTRATION: "natural",
            BRollType.EMOTIONAL: "warm",
            BRollType.TRANSITIONAL: "cool",
            BRollType.TECHNICAL: "high_contrast",
            BRollType.STOCK: "natural",
            BRollType.GENERATED: "cinematic"
        }
        
        return type_grading.get(b_roll_type, "natural")
    
    async def _determine_props(
        self, b_roll_type: BRollType, analysis: Dict[str, Any]
    ) -> List[str]:
        """Determine props needed for B-roll type."""
        
        props = []
        
        if b_roll_type == BRollType.DEMONSTRATION:
            if analysis["technical_elements"]:
                props.extend(["equipment", "tools", "devices"])
        elif b_roll_type == BRollType.CONTEXTUAL:
            if analysis["contextual_elements"]:
                props.extend(["props", "objects", "items"])
        elif b_roll_type == BRollType.EMOTIONAL:
            props.extend(["emotional_props", "symbolic_objects"])
        
        return props[:3]  # Return top 3 props
    
    async def _determine_location(
        self, b_roll_type: BRollType, analysis: Dict[str, Any]
    ) -> str:
        """Determine location type for B-roll type."""
        
        # Location types by B-roll type
        type_locations = {
            BRollType.CONTEXTUAL: "real_location",
            BRollType.AESTHETIC: "studio_set",
            BRollType.DEMONSTRATION: "workshop",
            BRollType.EMOTIONAL: "emotional_set",
            BRollType.TRANSITIONAL: "neutral_space",
            BRollType.TECHNICAL: "technical_lab",
            BRollType.STOCK: "various_locations",
            BRollType.GENERATED: "digital_environment"
        }
        
        return type_locations.get(b_roll_type, "studio")
    
    async def _select_transition_type(self, b_roll_type: BRollType) -> str:
        """Select transition type for B-roll type."""
        
        # Transition types by B-roll type
        type_transitions = {
            BRollType.CONTEXTUAL: "cut",
            BRollType.AESTHETIC: "fade",
            BRollType.DEMONSTRATION: "cut",
            BRollType.EMOTIONAL: "fade",
            BRollType.TRANSITIONAL: "wipe",
            BRollType.TECHNICAL: "cut",
            BRollType.STOCK: "cut",
            BRollType.GENERATED: "dissolve"
        }
        
        return type_transitions.get(b_roll_type, "cut")
    
    async def _calculate_production_requirements(
        self, scenes: List[SceneDescription], request: BRollRequest
    ) -> Dict[str, Any]:
        """Calculate production requirements for scenes."""
        
        technical_requirements = []
        resource_needs = {
            "crew": [],
            "equipment": [],
            "locations": [],
            "props": [],
            "post_production": []
        }
        
        # Analyze scene requirements
        for scene in scenes:
            # Technical requirements
            if scene.complexity in [SceneComplexity.COMPLEX, SceneComplexity.PROFESSIONAL]:
                technical_requirements.append("professional_camera_equipment")
                technical_requirements.append("advanced_lighting")
            
            if "crane" in scene.camera_movements or "tracking" in scene.camera_movements:
                technical_requirements.append("camera_support_equipment")
            
            # Crew requirements
            if scene.complexity == SceneComplexity.PROFESSIONAL:
                resource_needs["crew"].extend(["director", "cinematographer", "lighting_technician"])
            elif scene.complexity == SceneComplexity.COMPLEX:
                resource_needs["crew"].append("cinematographer")
            
            # Equipment requirements
            if scene.lighting_style == "studio":
                resource_needs["equipment"].append("studio_lighting_kit")
            
            if scene.camera_movements != ["static"]:
                resource_needs["equipment"].append("camera_support_system")
            
            # Location requirements
            resource_needs["locations"].append(scene.location_type)
            
            # Props requirements
            resource_needs["props"].extend(scene.props_needed)
            
            # Post-production requirements
            if scene.color_grading != "natural":
                resource_needs["post_production"].append("color_grading")
            
            if len(scene.audio_elements) > 0:
                resource_needs["post_production"].append("audio_mixing")
        
        # Remove duplicates
        for key in resource_needs:
            resource_needs[key] = list(set(resource_needs[key]))
        
        technical_requirements = list(set(technical_requirements))
        
        return {
            "technical": technical_requirements,
            "resources": resource_needs
        }
    
    async def _estimate_cost(
        self, scenes: List[SceneDescription], request: BRollRequest
    ) -> float:
        """Estimate production cost for scenes."""
        
        base_cost_per_minute = 1000  # $1000 per minute base rate
        
        # Complexity multipliers
        complexity_multipliers = {
            SceneComplexity.SIMPLE: 0.5,
            SceneComplexity.MODERATE: 1.0,
            SceneComplexity.COMPLEX: 2.0,
            SceneComplexity.PROFESSIONAL: 3.0
        }
        
        total_cost = 0
        
        for scene in scenes:
            minute_cost = base_cost_per_minute * scene.duration
            complexity_multiplier = complexity_multipliers[scene.complexity]
            
            scene_cost = minute_cost * complexity_multiplier
            
            # Add equipment costs
            if scene.camera_movements != ["static"]:
                scene_cost += 500  # Equipment rental
            
            if scene.lighting_style == "studio":
                scene_cost += 300  # Lighting equipment
            
            total_cost += scene_cost
        
        # Apply budget constraints
        if request.budget_constraints and total_cost > request.budget_constraints:
            total_cost = request.budget_constraints
        
        return total_cost
    
    async def _estimate_timeline(
        self, scenes: List[SceneDescription], request: BRollRequest
    ) -> str:
        """Estimate production timeline."""
        
        total_duration = sum(scene.duration for scene in scenes)
        
        # Base production time (1 day per 2 minutes of footage)
        base_days = total_duration / 2
        
        # Complexity adjustments
        complexity_days = 0
        for scene in scenes:
            if scene.complexity == SceneComplexity.COMPLEX:
                complexity_days += 1
            elif scene.complexity == SceneComplexity.PROFESSIONAL:
                complexity_days += 2
        
        total_days = base_days + complexity_days
        
        # Add post-production time
        post_production_days = total_days * 0.5
        
        total_timeline = total_days + post_production_days
        
        if total_timeline < 1:
            return "Same day"
        elif total_timeline < 3:
            return f"{int(total_timeline)} days"
        elif total_timeline < 7:
            return f"{int(total_timeline)} days"
        elif total_timeline < 14:
            return f"{int(total_timeline/7)} weeks"
        else:
            return f"{int(total_timeline/7)} weeks"
    
    async def _generate_creative_direction(
        self, request: BRollRequest, analysis: Dict[str, Any]
    ) -> str:
        """Generate creative direction for B-roll production."""
        
        direction = []
        
        # Base direction
        direction.append("Create B-roll footage that enhances the main content")
        
        # Style-based direction
        if request.style_preference == "cinematic":
            direction.append("Focus on cinematic quality with dramatic lighting and camera movements")
        elif request.style_preference == "professional":
            direction.append("Maintain professional quality with clean, technical presentation")
        elif request.style_preference == "natural":
            direction.append("Emphasize natural, authentic footage with minimal production")
        
        # Content-based direction
        if analysis["emotional_beats"]:
            direction.append(f"Capture emotional moments: {', '.join(analysis['emotional_beats'])}")
        
        if analysis["technical_elements"]:
            direction.append("Clearly demonstrate technical processes and systems")
        
        if analysis["visual_elements"]:
            direction.append("Emphasize visual storytelling elements")
        
        return " | ".join(direction)
    
    async def _calculate_confidence_score(
        self, request: BRollRequest, analysis: Dict[str, Any]
    ) -> float:
        """Calculate confidence score for B-roll generation."""
        
        confidence = 0.5  # Base confidence
        
        # Boost confidence based on content analysis
        if analysis["visual_elements"]:
            confidence += 0.1
        
        if analysis["contextual_elements"]:
            confidence += 0.1
        
        if analysis["emotional_beats"]:
            confidence += 0.1
        
        if analysis["technical_elements"]:
            confidence += 0.1
        
        # Boost confidence based on request completeness
        if request.b_roll_types:
            confidence += 0.1
        
        if request.style_preference:
            confidence += 0.05
        
        return min(1.0, confidence)
    
    async def get_b_roll_recommendations(
        self, content: str, content_type: str, platform: str
    ) -> List[Dict[str, Any]]:
        """Get B-roll recommendations for content."""
        
        recommendations = []
        
        # Analyze content for B-roll opportunities
        content_lower = content.lower()
        
        # Contextual B-roll recommendations
        if any(word in content_lower for word in ["show", "demonstrate", "display"]):
            recommendations.append({
                "type": BRollType.CONTEXTUAL,
                "reason": "Content contains demonstration elements",
                "confidence": 0.8,
                "priority": "high"
            })
        
        # Technical B-roll recommendations
        if any(word in content_lower for word in ["technology", "software", "process", "system"]):
            recommendations.append({
                "type": BRollType.TECHNICAL,
                "reason": "Content contains technical elements",
                "confidence": 0.9,
                "priority": "high"
            })
        
        # Emotional B-roll recommendations
        if any(word in content_lower for word in ["feel", "emotion", "story", "journey"]):
            recommendations.append({
                "type": BRollType.EMOTIONAL,
                "reason": "Content contains emotional elements",
                "confidence": 0.7,
                "priority": "medium"
            })
        
        # Platform-specific recommendations
        if platform == "youtube":
            recommendations.append({
                "type": BRollType.AESTHETIC,
                "reason": "YouTube benefits from aesthetic B-roll",
                "confidence": 0.6,
                "priority": "medium"
            })
        
        return recommendations


# Singleton instance
b_roll_scene_engine = BRollSceneEngine()
