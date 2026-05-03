"""
Lee-Wuh AI Brain / Council Controller v0

The AI brain interface that guides users through LWA with intelligent,
context-aware guidance. Lee-Wuh leads the council and provides
mascot messages, council summaries, and next-best-actions.

Uses deterministic local rules first. Future-gates live LLM integration.
"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger("uvicorn.error")


class LeeWuhVisualState(str, Enum):
    """Visual states for Lee-Wuh mascot."""
    
    IDLE = "idle"
    THINKING = "thinking"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    RENDERING = "rendering"
    ANALYZING = "analyzing"
    EXCITED = "excited"
    OVERLORD = "overlord"


class AppScreen(str, Enum):
    """Main app screens for context."""
    
    HOMEPAGE = "homepage"
    GENERATE = "generate"
    SOURCE_INTAKE = "source_intake"
    TIMELINE = "timeline"
    RENDER_JOBS = "render_jobs"
    CAPTIONS = "captions"
    AUDIO = "audio"
    PACKAGE_EXPORT = "package_export"
    MARKETPLACE = "marketplace"
    PROOF_VAULT = "proof_vault"
    CAMPAIGNS = "campaigns"
    SETTINGS = "settings"


@dataclass
class CouncilInput:
    """Input to the Lee-Wuh AI Brain."""
    
    app_state: str
    current_screen: AppScreen
    source_asset_ids: List[str] = field(default_factory=list)
    timeline_id: Optional[str] = None
    render_job_id: Optional[str] = None
    clip_id: Optional[str] = None
    user_goal: Optional[str] = None
    platform: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    engine_statuses: Dict[str, str] = field(default_factory=dict)
    user_id: Optional[str] = None
    has_credits: bool = True
    has_sources: bool = False
    has_clips: bool = False
    has_timeline: bool = False


@dataclass
class CouncilOutput:
    """Output from the Lee-Wuh AI Brain."""
    
    mascot_message: str
    council_summary: str
    next_best_action: str
    recommended_engine: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    confidence: int = 80
    visual_state: LeeWuhVisualState = LeeWuhVisualState.IDLE
    metadata: Dict[str, Any] = field(default_factory=dict)


class LeeWuhBrain:
    """
    Lee-Wuh AI Brain - Council Controller
    
    Processes app state and provides intelligent guidance through
    mascot messages, council summaries, and next-best-actions.
    """
    
    def __init__(self) -> None:
        self._dialogue_library = self._build_dialogue_library()
        self._state_mappings = self._build_state_mappings()
        self._council_rules = self._build_council_rules()
    
    async def process(self, input_data: CouncilInput) -> CouncilOutput:
        """
        Process council input and generate guidance.
        
        Args:
            input_data: Council input with app state and context
            
        Returns:
            CouncilOutput with mascot message, council summary, and next-best-action
        """
        
        try:
            # Determine visual state based on app state
            visual_state = self._determine_visual_state(input_data)
            
            # Generate mascot message
            mascot_message = self._generate_mascot_message(input_data, visual_state)
            
            # Generate council summary
            council_summary = self._generate_council_summary(input_data)
            
            # Determine next-best-action
            next_best_action = self._determine_next_best_action(input_data)
            
            # Identify recommended engine
            recommended_engine = self._recommend_engine(input_data)
            
            # Collect warnings
            warnings = self._collect_warnings(input_data)
            
            # Calculate confidence
            confidence = self._calculate_confidence(input_data)
            
            return CouncilOutput(
                mascot_message=mascot_message,
                council_summary=council_summary,
                next_best_action=next_best_action,
                recommended_engine=recommended_engine,
                warnings=warnings,
                confidence=confidence,
                visual_state=visual_state,
                metadata={
                    "screen": input_data.current_screen.value,
                    "has_sources": input_data.has_sources,
                    "has_clips": input_data.has_clips,
                    "has_timeline": input_data.has_timeline,
                    "engine_statuses": input_data.engine_statuses,
                }
            )
            
        except Exception as error:
            logger.error(f"lee_wuh_brain_processing_failed error={str(error)}")
            
            # Return safe fallback
            return CouncilOutput(
                mascot_message="I'm recalibrating. Give me a moment.",
                council_summary="Council systems are adjusting.",
                next_best_action="Wait for system recovery",
                warnings=["Brain processing error"],
                confidence=50,
                visual_state=LeeWuhVisualState.THINKING,
            )
    
    def _determine_visual_state(self, input_data: CouncilInput) -> LeeWuhVisualState:
        """Determine Lee-Wuh's visual state based on app state."""
        
        # Error state
        if "error" in input_data.app_state.lower():
            return LeeWuhVisualState.ERROR
        
        # Warning state
        if input_data.warnings:
            return LeeWuhVisualState.WARNING
        
        # Rendering state
        if input_data.render_job_id and "rendering" in input_data.app_state.lower():
            return LeeWuhVisualState.RENDERING
        
        # Analyzing state
        if "analyzing" in input_data.app_state.lower() or "ingesting" in input_data.app_state.lower():
            return LeeWuhVisualState.ANALYZING
        
        # Success state
        if "success" in input_data.app_state.lower() or "complete" in input_data.app_state.lower():
            return LeeWuhVisualState.SUCCESS
        
        # Excited state for new sources or clips
        if input_data.has_sources and not input_data.has_clips:
            return LeeWuhVisualState.EXCITED
        
        if input_data.has_clips and not input_data.has_timeline:
            return LeeWuhVisualState.EXCITED
        
        # Default idle
        return LeeWuhVisualState.IDLE
    
    def _generate_mascot_message(self, input_data: CouncilInput, visual_state: LeeWuhVisualState) -> str:
        """Generate Lee-Wuh mascot message based on context."""
        
        screen = input_data.current_screen
        has_sources = input_data.has_sources
        has_clips = input_data.has_clips
        has_timeline = input_data.has_timeline
        has_credits = input_data.has_credits
        
        # Screen-specific messages
        if screen == AppScreen.HOMEPAGE:
            if not has_sources:
                return "Drop the source. I'll find the first move."
            return "Welcome back. Let's create something powerful."
        
        if screen == AppScreen.SOURCE_INTAKE:
            if has_sources:
                return "Source received. I'm scanning hooks, proof, silence, and energy."
            return "Upload or link your source. I'll handle the rest."
        
        if screen == AppScreen.GENERATE:
            if not has_sources:
                return "Need a source first. Upload, link, or use prompt mode."
            if has_clips:
                return "Boss-level clip detected. Post this first."
            return "I'm analyzing your source for breakout moments."
        
        if screen == AppScreen.TIMELINE:
            if has_timeline:
                return "Timeline composed. Ready for render or export."
            return "Let's build your timeline. I'll arrange the moments."
        
        if screen == AppScreen.RENDER_JOBS:
            if input_data.render_job_id:
                return "Render in progress. I'm monitoring quality and timing."
            return "Queue your renders. I'll ensure they meet standards."
        
        if screen == AppScreen.CAPTIONS:
            return "Captions make clips accessible and viral. I'll style them right."
        
        if screen == AppScreen.AUDIO:
            return "Audio and music set the mood. I'll find the perfect match."
        
        if screen == AppScreen.PACKAGE_EXPORT:
            return "Package it for maximum impact. I'll organize everything."
        
        if screen == AppScreen.MARKETPLACE:
            return "Browse templates, services, and assets from top creators."
        
        if screen == AppScreen.PROOF_VAULT:
            return "Your proof assets live here. They build trust and authority."
        
        if screen == AppScreen.CAMPAIGNS:
            return "Campaigns turn clips into coordinated content strategies."
        
        if screen == AppScreen.SETTINGS:
            return "Configure your workspace. I'll help optimize your setup."
        
        # Visual state-specific messages
        if visual_state == LeeWuhVisualState.ERROR:
            return "Something went wrong. I'm working on a fix."
        
        if visual_state == LeeWuhVisualState.WARNING:
            return "I see a potential issue. Let's address it together."
        
        if visual_state == LeeWuhVisualState.RENDERING:
            return "Rendering in progress. Quality is my priority."
        
        if visual_state == LeeWuhVisualState.ANALYZING:
            return "Scanning for hooks, patterns, and opportunities."
        
        if visual_state == LeeWuhVisualState.SUCCESS:
            return "Excellent work. This one's ready to shine."
        
        if visual_state == LeeWuhVisualState.EXCITED:
            return "This has potential. Let's make it legendary."
        
        # Default messages
        if not has_credits:
            return "Credits running low. Consider upgrading for more power."
        
        return "I'm here to guide your creative journey. What's next?"
    
    def _generate_council_summary(self, input_data: CouncilInput) -> str:
        """Generate council summary based on current state."""
        
        parts = []
        
        # Screen context
        screen_name = input_data.current_screen.value.replace("_", " ").title()
        parts.append(f"Current focus: {screen_name}")
        
        # Asset status
        if input_data.has_sources:
            parts.append("Sources loaded and analyzed")
        if input_data.has_clips:
            parts.append("Clips generated and scored")
        if input_data.has_timeline:
            parts.append("Timeline composed")
        
        # Engine status
        if input_data.engine_statuses:
            healthy_engines = sum(1 for status in input_data.engine_statuses.values() if "ok" in status.lower())
            total_engines = len(input_data.engine_statuses)
            parts.append(f"Engines: {healthy_engines}/{total_engines} healthy")
        
        # Warnings
        if input_data.warnings:
            parts.append(f"{len(input_data.warnings)} warnings to review")
        
        # Credits
        if not input_data.has_credits:
            parts.append("Credits low - upgrade recommended")
        
        return " | ".join(parts) if parts else "Council systems ready"
    
    def _determine_next_best_action(self, input_data: CouncilInput) -> str:
        """Determine the best next action for the user."""
        
        screen = input_data.current_screen
        has_sources = input_data.has_sources
        has_clips = input_data.has_clips
        has_timeline = input_data.has_timeline
        has_credits = input_data.has_credits
        
        # Credit check first
        if not has_credits:
            return "Upgrade your plan to continue creating"
        
        # Screen-specific actions
        if screen == AppScreen.HOMEPAGE:
            if not has_sources:
                return "Upload a source or link content to get started"
            return "Review your recent clips or start a new generation"
        
        if screen == AppScreen.SOURCE_INTAKE:
            if not has_sources:
                return "Upload a video, audio file, or link content"
            return "Proceed to generate clips from your source"
        
        if screen == AppScreen.GENERATE:
            if not has_sources:
                return "Add a source before generating clips"
            if not has_clips:
                return "Generate clips to analyze your content"
            return "Review generated clips and select the best ones"
        
        if screen == AppScreen.TIMELINE:
            if not has_clips:
                return "Generate clips first before building a timeline"
            if not has_timeline:
                return "Compose a timeline from your clips"
            return "Review and export your timeline"
        
        if screen == AppScreen.RENDER_JOBS:
            if not has_timeline:
                return "Create a timeline before rendering"
            return "Queue a render job or check render status"
        
        if screen == AppScreen.CAPTIONS:
            if not has_clips:
                return "Generate clips before adding captions"
            return "Apply caption presets or custom styles"
        
        if screen == AppScreen.AUDIO:
            if not has_clips:
                return "Generate clips before adding audio"
            return "Select music or add voiceover"
        
        if screen == AppScreen.PACKAGE_EXPORT:
            if not has_clips:
                return "Generate clips before exporting"
            return "Package your content for multi-platform distribution"
        
        if screen == AppScreen.MARKETplace:
            return "Browse listings or create your own offerings"
        
        if screen == AppScreen.PROOF_VAULT:
            return "Save proof assets or review existing ones"
        
        if screen == AppScreen.CAMPAIGNS:
            if not has_clips:
                return "Generate clips before creating campaigns"
            return "Create a campaign from your clips"
        
        # Progressive actions
        if not has_sources:
            return "Add a source to begin"
        if not has_clips:
            return "Generate clips from your source"
        if not has_timeline:
            return "Compose a timeline from your clips"
        
        return "Review your work and export when ready"
    
    def _recommend_engine(self, input_data: CouncilInput) -> Optional[str]:
        """Recommend the best engine for the current context."""
        
        screen = input_data.current_screen
        
        if screen == AppScreen.GENERATE:
            return "clip_generator"
        if screen == AppScreen.TIMELINE:
            return "timeline_composer"
        if screen == AppScreen.RENDER_JOBS:
            return "ffmpeg_renderer"
        if screen == AppScreen.CAPTIONS:
            return "caption_engine"
        if screen == AppScreen.AUDIO:
            return "audio_engine"
        if screen == AppScreen.PACKAGE_EXPORT:
            return "campaign_export_packager"
        
        return None
    
    def _collect_warnings(self, input_data: CouncilInput) -> List[str]:
        """Collect relevant warnings based on current state."""
        
        warnings = []
        
        # Add existing warnings
        warnings.extend(input_data.warnings)
        
        # Credit warning
        if not input_data.has_credits:
            warnings.append("Credits running low")
        
        # Engine health warnings
        for engine_name, status in input_data.engine_statuses.items():
            if "error" in status.lower() or "fail" in status.lower():
                warnings.append(f"{engine_name} engine issue: {status}")
        
        return warnings
    
    def _calculate_confidence(self, input_data: CouncilInput) -> int:
        """Calculate confidence score for the guidance."""
        
        confidence = 80  # Base confidence
        
        # Reduce confidence if warnings
        if input_data.warnings:
            confidence -= min(len(input_data.warnings) * 5, 20)
        
        # Reduce confidence if engine issues
        for status in input_data.engine_statuses.values():
            if "error" in status.lower():
                confidence -= 10
        
        # Increase confidence if assets are present
        if input_data.has_sources:
            confidence += 5
        if input_data.has_clips:
            confidence += 5
        if input_data.has_timeline:
            confidence += 5
        
        # Ensure confidence stays in valid range
        return max(0, min(100, confidence))
    
    def _build_dialogue_library(self) -> Dict[str, List[str]]:
        """Build library of Lee-Wuh dialogue phrases."""
        
        return {
            "greeting": [
                "Welcome to LWA. I'm Lee-Wuh, your creative guide.",
                "Ready to create something powerful?",
                "Let's turn your content into impact.",
            ],
            "success": [
                "Excellent work. This one's ready to shine.",
                "Boss-level clip detected. Post this first.",
                "This one builds trust. Save it as proof.",
                "This one sells. Package it for conversion.",
            ],
            "thinking": [
                "I'm analyzing your source for breakout moments.",
                "Scanning hooks, proof, silence, and energy.",
                "The council is reviewing your content.",
            ],
            "warning": [
                "I see a potential issue. Let's address it together.",
                "This needs attention before proceeding.",
                "Mock mode is training ground. Real render comes next.",
            ],
            "error": [
                "Something went wrong. I'm working on a fix.",
                "Let me recalibrate. Give me a moment.",
                "The council is troubleshooting this issue.",
            ],
            "rendering": [
                "Render in progress. I'm monitoring quality and timing.",
                "Quality is my priority. This may take a moment.",
                "The forge is working on your content.",
            ],
        }
    
    def _build_state_mappings(self) -> Dict[str, LeeWuhVisualState]:
        """Build mappings from app states to visual states."""
        
        return {
            "idle": LeeWuhVisualState.IDLE,
            "loading": LeeWuhVisualState.THINKING,
            "analyzing": LeeWuhVisualState.ANALYZING,
            "processing": LeeWuhVisualState.RENDERING,
            "rendering": LeeWuhVisualState.RENDERING,
            "success": LeeWuhVisualState.SUCCESS,
            "complete": LeeWuhVisualState.SUCCESS,
            "error": LeeWuhVisualState.ERROR,
            "failed": LeeWuhVisualState.ERROR,
            "warning": LeeWuhVisualState.WARNING,
        }
    
    def _build_council_rules(self) -> Dict[str, str]:
        """Build council decision rules."""
        
        return {
            "safety_first": "Safety and rights always veto",
            "cost_aware": "Cost considerations always factor in",
            "user_first": "User experience is paramount",
            "performance": "Performance cannot be sacrificed",
            "no_blocking": "Lee-Wuh never blocks workflows",
            "business_guided": "Business goals guide technical decisions",
        }


# Singleton instance
lee_wuh_brain = LeeWuhBrain()
