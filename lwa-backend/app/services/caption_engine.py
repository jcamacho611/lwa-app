"""
Caption Engine v0

Generates professional captions with multiple styles, presets,
and mobile-optimized burned-in captions for short-form content.
"""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger("uvicorn.error")


class CaptionPreset(str, Enum):
    """Caption style presets."""
    
    CLEAN_OP = "clean_op"
    CRIMSON_PULSE = "crimson_pulse"
    KARAOKE_NEON = "karaoke_neon"
    SIGNAL_LOW = "signal_low"
    BIGFRAME = "bigframe"
    SOFT_SAFE = "soft_safe"
    DEV_BRUTAL = "dev_brutal"


@dataclass
class CaptionStyle:
    """Caption styling configuration."""
    
    preset: CaptionPreset
    font_family: str
    font_size: int
    font_weight: str
    color: str
    background_color: str
    background_opacity: float
    position: str  # top, middle, bottom
    animation: str
    word_timing: bool = True


@dataclass
class CaptionLine:
    """Single caption line with timing."""
    
    text: str
    start_time: float
    end_time: float
    confidence: float = 1.0


@dataclass
class CaptionTrack:
    """Complete caption track for a video."""
    
    lines: List[CaptionLine]
    style: CaptionStyle
    language: str = "en"
    total_duration: float = 0.0


class CaptionEngine:
    """
    Caption generation and styling engine.
    
    Provides caption variants, burned-in captions, and styling presets
    optimized for short-form mobile content.
    """
    
    def __init__(self) -> None:
        self._style_presets = self._build_style_presets()
        self._caption_templates = self._build_caption_templates()
    
    def generate_caption_variants(self, hook: str, platform: Optional[str] = None) -> Dict[str, str]:
        """
        Generate multiple caption variants for a hook.
        
        Args:
            hook: The main hook text
            platform: Target platform for platform-specific variants
            
        Returns:
            Dictionary of caption variants by style
        """
        base = hook.strip()
        
        variants = {
            "short": base,
            "engagement": f"{base} 👇 What do you think?",
            "viral": f"{base} — nobody talks about this.",
            "authority": f"{base}. Here's the breakdown.",
        }
        
        # Platform-specific variants
        if platform == "tiktok":
            variants["tiktok_viral"] = f"{base} #fyp #viral"
        elif platform == "instagram_reels":
            variants["ig_reels"] = f"{base} 🎬"
        elif platform == "youtube_shorts":
            variants["yt_shorts"] = f"{base} 🔥"
        
        return variants
    
    def build_burned_caption(self, hook: str, max_lines: int = 4) -> str:
        """
        Build a burned-in caption optimized for mobile readability.
        Chunks text into 2-4 word lines for short-form.
        
        Args:
            hook: The caption text
            max_lines: Maximum number of lines for the caption
            
        Returns:
            Multi-line caption string
        """
        words = hook.split()
        
        # Mobile readability: chunk into 2–4 word lines
        lines = []
        chunk = []
        
        for word in words:
            chunk.append(word)
            if len(chunk) >= 3:
                lines.append(" ".join(chunk))
                chunk = []
        
        if chunk:
            lines.append(" ".join(chunk))
        
        return "\n".join(lines[:max_lines])
    
    def apply_preset(self, text: str, preset: CaptionPreset) -> CaptionStyle:
        """
        Apply a caption preset to text.
        
        Args:
            text: The caption text
            preset: The caption preset to apply
            
        Returns:
            CaptionStyle with preset configuration
        """
        return self._style_presets.get(preset, self._style_presets[CaptionPreset.CLEAN_OP])
    
    def generate_caption_track(
        self,
        transcript: str,
        duration: float,
        preset: CaptionPreset = CaptionPreset.CLEAN_OP
    ) -> CaptionTrack:
        """
        Generate a complete caption track from transcript.
        
        Args:
            transcript: Full transcript text
            duration: Total video duration in seconds
            preset: Caption preset to use
            
        Returns:
            CaptionTrack with timed lines
        """
        # Split transcript into sentences
        sentences = self._split_sentences(transcript)
        
        # Calculate timing for each sentence
        lines = []
        time_per_sentence = duration / len(sentences) if sentences else 0
        
        for i, sentence in enumerate(sentences):
            start_time = i * time_per_sentence
            end_time = (i + 1) * time_per_sentence
            
            lines.append(CaptionLine(
                text=sentence.strip(),
                start_time=start_time,
                end_time=end_time,
                confidence=0.9
            ))
        
        style = self.apply_preset(transcript, preset)
        
        return CaptionTrack(
            lines=lines,
            style=style,
            language="en",
            total_duration=duration
        )
    
    def optimize_for_mobile(self, caption: str, max_chars_per_line: int = 20) -> str:
        """
        Optimize caption text for mobile display.
        
        Args:
            caption: The caption text
            max_chars_per_line: Maximum characters per line
            
        Returns:
            Optimized multi-line caption
        """
        words = caption.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            word_length = len(word)
            
            if current_length + word_length + 1 <= max_chars_per_line:
                current_line.append(word)
                current_length += word_length + 1
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]
                current_length = word_length
        
        if current_line:
            lines.append(" ".join(current_line))
        
        return "\n".join(lines)
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        import re
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _build_style_presets(self) -> Dict[CaptionPreset, CaptionStyle]:
        """Build caption style presets."""
        return {
            CaptionPreset.CLEAN_OP: CaptionStyle(
                preset=CaptionPreset.CLEAN_OP,
                font_family="Inter",
                font_size=24,
                font_weight="600",
                color="#FFFFFF",
                background_color="#000000",
                background_opacity=0.7,
                position="bottom",
                animation="fade_in"
            ),
            CaptionPreset.CRIMSON_PULSE: CaptionStyle(
                preset=CaptionPreset.CRIMSON_PULSE,
                font_family="Inter",
                font_size=28,
                font_weight="700",
                color="#FF0000",
                background_color="#000000",
                background_opacity=0.8,
                position="middle",
                animation="pulse"
            ),
            CaptionPreset.KARAOKE_NEON: CaptionStyle(
                preset=CaptionPreset.KARAOKE_NEON,
                font_family="Inter",
                font_size=26,
                font_weight="700",
                color="#00FF00",
                background_color="#000000",
                background_opacity=0.9,
                position="bottom",
                animation="word_by_word"
            ),
            CaptionPreset.SIGNAL_LOW: CaptionStyle(
                preset=CaptionPreset.SIGNAL_LOW,
                font_family="Inter",
                font_size=20,
                font_weight="400",
                color="#CCCCCC",
                background_color="#000000",
                background_opacity=0.5,
                position="bottom",
                animation="fade_in"
            ),
            CaptionPreset.BIGFRAME: CaptionStyle(
                preset=CaptionPreset.BIGFRAME,
                font_family="Inter",
                font_size=32,
                font_weight="800",
                color="#FFFFFF",
                background_color="#000000",
                background_opacity=0.9,
                position="middle",
                animation="scale_in"
            ),
            CaptionPreset.SOFT_SAFE: CaptionStyle(
                preset=CaptionPreset.SOFT_SAFE,
                font_family="Inter",
                font_size=22,
                font_weight="500",
                color="#FFFFFF",
                background_color="#000000",
                background_opacity=0.6,
                position="bottom",
                animation="fade_in"
            ),
            CaptionPreset.DEV_BRUTAL: CaptionStyle(
                preset=CaptionPreset.DEV_BRUTAL,
                font_family="Courier New",
                font_size=24,
                font_weight="700",
                color="#00FF00",
                background_color="#000000",
                background_opacity=0.8,
                position="top",
                animation="typewriter"
            ),
        }
    
    def _build_caption_templates(self) -> Dict[str, List[str]]:
        """Build caption templates for different content types."""
        return {
            "hook": [
                "This changes everything.",
                "Nobody talks about this.",
                "Here's what I learned.",
                "Stop making this mistake.",
            ],
            "cta": [
                "Link in bio",
                "Follow for more",
                "Save this",
                "Share with someone who needs this",
            ],
            "engagement": [
                "What do you think?",
                "Drop a comment",
                "Tag someone",
                "Double tap if you agree",
            ],
        }


# Singleton instance
caption_engine = CaptionEngine()