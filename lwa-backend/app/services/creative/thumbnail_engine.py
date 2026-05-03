"""
Thumbnail Creative Engine v0

Generates creative thumbnails for video content using AI and design principles.
Optimizes thumbnails for maximum click-through rates and engagement.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import json
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import io
import base64

logger = logging.getLogger(__name__)


class ThumbnailStyle(Enum):
    """Thumbnail style categories."""
    
    BOLD_TEXT = "bold_text"
    CINEMATIC = "cinematic"
    MINIMALIST = "minimalist"
    TRENDING = "trending"
    QUESTION = "question"
    COMPARISON = "comparison"
    TUTORIAL = "tutorial"
    REACTION = "reaction"


@dataclass
class ThumbnailRequest:
    """Request for thumbnail generation."""
    
    video_title: str
    video_description: str
    target_audience: str
    platform: str
    style: ThumbnailStyle
    brand_colors: List[str]
    key_moments: List[str]
    emotional_tone: str
    call_to_action: Optional[str]
    include_face: bool
    include_text: bool
    aspect_ratio: str


@dataclass
class ThumbnailResult:
    """Result from thumbnail generation."""
    
    thumbnail_url: str
    thumbnail_path: str
    style_used: str
    elements_used: List[str]
    color_palette: List[str]
    text_overlays: List[Dict[str, Any]]
    confidence_score: float
    engagement_prediction: float
    generation_time_seconds: float
    metadata: Dict[str, Any]


class ThumbnailCreativeEngine:
    """
    Generates creative thumbnails optimized for engagement.
    
    Uses AI-powered design principles and platform-specific
    optimization to create high-performing thumbnails.
    """
    
    def __init__(self):
        self.name = "thumbnail_creative_engine"
        self.version = "1.0.0"
        
        # Platform-specific dimensions
        self.platform_dimensions = {
            "youtube": {"width": 1280, "height": 720},
            "tiktok": {"width": 1080, "height": 1920},
            "instagram": {"width": 1080, "height": 1350},
            "facebook": {"width": 1200, "height": 630},
            "twitter": {"width": 1200, "height": 675},
        }
        
        # Color psychology
        self.color_psychology = {
            "red": {"emotion": "excitement", "ctr_boost": 0.15},
            "yellow": {"emotion": "happiness", "ctr_boost": 0.12},
            "blue": {"emotion": "trust", "ctr_boost": 0.08},
            "green": {"emotion": "growth", "ctr_boost": 0.10},
            "purple": {"emotion": "luxury", "ctr_boost": 0.13},
            "orange": {"emotion": "enthusiasm", "ctr_boost": 0.14},
            "black": {"emotion": "power", "ctr_boost": 0.11},
            "white": {"emotion": "clean", "ctr_boost": 0.05},
        }
        
        # High-CTR elements
        self.high_ctr_elements = {
            "face": {"ctr_boost": 0.20, "importance": "high"},
            "text": {"ctr_boost": 0.15, "importance": "medium"},
            "contrast": {"ctr_boost": 0.18, "importance": "high"},
            "emotion": {"ctr_boost": 0.12, "importance": "medium"},
            "branding": {"ctr_boost": 0.08, "importance": "low"},
            "numbers": {"ctr_boost": 0.10, "importance": "medium"},
            "arrows": {"ctr_boost": 0.07, "importance": "low"},
        }
        
        # Text optimization
        self.text_optimization = {
            "max_words": 6,
            "font_size_ratio": 0.12,  # 12% of image height
            "contrast_ratio": 4.5,  # WCAG AA standard
            "readability_score": 0.8,
        }
    
    async def generate_thumbnail(self, request: ThumbnailRequest) -> ThumbnailResult:
        """
        Generate a creative thumbnail based on the request.
        
        Args:
            request: Thumbnail generation request with all parameters
            
        Returns:
            ThumbnailResult with generated thumbnail information
        """
        
        try:
            start_time = datetime.utcnow()
            
            # Analyze content for thumbnail elements
            content_analysis = await self._analyze_content(request)
            
            # Select optimal style and elements
            style_config = await self._select_style_config(request, content_analysis)
            
            # Generate color palette
            color_palette = await self._generate_color_palette(request, style_config)
            
            # Create thumbnail composition
            thumbnail_image = await self._create_thumbnail_composition(
                request, style_config, color_palette, content_analysis
            )
            
            # Add text overlays
            if request.include_text:
                thumbnail_image = await self._add_text_overlays(
                    thumbnail_image, request, style_config
                )
            
            # Apply final optimizations
            thumbnail_image = await self._apply_optimizations(
                thumbnail_image, style_config
            )
            
            # Save thumbnail
            thumbnail_path = await self._save_thumbnail(thumbnail_image, request)
            
            # Calculate metrics
            generation_time = (datetime.utcnow() - start_time).total_seconds()
            confidence_score = await self._calculate_confidence_score(
                request, style_config, content_analysis
            )
            engagement_prediction = await self._predict_engagement(
                style_config, content_analysis
            )
            
            return ThumbnailResult(
                thumbnail_url=f"/thumbnails/{os.path.basename(thumbnail_path)}",
                thumbnail_path=thumbnail_path,
                style_used=style_config["style_name"],
                elements_used=style_config["elements"],
                color_palette=color_palette,
                text_overlays=style_config.get("text_overlays", []),
                confidence_score=confidence_score,
                engagement_prediction=engagement_prediction,
                generation_time_seconds=generation_time,
                metadata={
                    "platform": request.platform,
                    "aspect_ratio": request.aspect_ratio,
                    "generation_timestamp": start_time.isoformat(),
                    "content_analysis": content_analysis
                }
            )
            
        except Exception as e:
            logger.error(f"Thumbnail generation failed: {e}")
            raise
    
    async def _analyze_content(self, request: ThumbnailRequest) -> Dict[str, Any]:
        """Analyze content to extract thumbnail-worthy elements."""
        
        analysis = {
            "keywords": [],
            "emotions": [],
            "key_moments": [],
            "entities": [],
            "sentiment": "neutral",
            "complexity": "medium",
            "visual_elements": []
        }
        
        # Extract keywords from title and description
        title_words = request.video_title.lower().split()
        desc_words = request.video_description.lower().split()
        all_words = title_words + desc_words
        
        # Identify impactful keywords
        impactful_words = [
            "shocking", "revealed", "secret", "exposed", "truth", "amazing",
            "incredible", "unbelievable", "never", "first", "ultimate", "best",
            "worst", "hacked", "leaked", "banned", "controversial", "viral"
        ]
        
        analysis["keywords"] = [
            word for word in all_words if word in impactful_words
        ][:5]  # Top 5 impactful words
        
        # Detect emotions
        emotion_words = {
            "excitement": ["amazing", "incredible", "shocking", "wow", "unbelievable"],
            "curiosity": ["secret", "revealed", "truth", "exposed", "mystery"],
            "fear": ["danger", "warning", "risk", "threat", "scary"],
            "anger": ["outrageous", "unacceptable", "shocking", "terrible"],
            "joy": ["happy", "beautiful", "wonderful", "amazing", "fantastic"]
        }
        
        for emotion, words in emotion_words.items():
            if any(word in all_words for word in words):
                analysis["emotions"].append(emotion)
        
        # Extract key moments
        analysis["key_moments"] = request.key_moments[:3]  # Top 3 moments
        
        # Determine sentiment
        positive_words = ["amazing", "incredible", "best", "beautiful", "wonderful"]
        negative_words = ["terrible", "worst", "shocking", "danger", "scary"]
        
        positive_count = sum(1 for word in all_words if word in positive_words)
        negative_count = sum(1 for word in all_words if word in negative_words)
        
        if positive_count > negative_count:
            analysis["sentiment"] = "positive"
        elif negative_count > positive_count:
            analysis["sentiment"] = "negative"
        
        # Determine complexity
        if len(all_words) > 50:
            analysis["complexity"] = "high"
        elif len(all_words) < 20:
            analysis["complexity"] = "low"
        
        # Identify visual elements
        if any(word in all_words for word in ["face", "person", "people", "man", "woman"]):
            analysis["visual_elements"].append("face")
        
        if any(word in all_words for word in ["money", "cash", "dollar", "rich"]):
            analysis["visual_elements"].append("money")
        
        if any(word in all_words for word in ["tech", "computer", "phone", "digital"]):
            analysis["visual_elements"].append("technology")
        
        return analysis
    
    async def _select_style_config(
        self, request: ThumbnailRequest, analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Select optimal style configuration based on content and platform."""
        
        style_configs = {
            ThumbnailStyle.BOLD_TEXT: {
                "style_name": "bold_text",
                "elements": ["text", "contrast", "emotion"],
                "layout": "centered_text",
                "text_style": "bold",
                "background": "gradient",
                "color_scheme": "high_contrast"
            },
            ThumbnailStyle.CINEMATIC: {
                "style_name": "cinematic",
                "elements": ["emotion", "contrast", "branding"],
                "layout": "cinematic",
                "text_style": "elegant",
                "background": "dark_moody",
                "color_scheme": "dramatic"
            },
            ThumbnailStyle.MINIMALIST: {
                "style_name": "minimalist",
                "elements": ["text", "contrast"],
                "layout": "clean",
                "text_style": "simple",
                "background": "solid",
                "color_scheme": "monochrome"
            },
            ThumbnailStyle.TRENDING: {
                "style_name": "trending",
                "elements": ["face", "emotion", "text"],
                "layout": "trending",
                "text_style": "viral",
                "background": "vibrant",
                "color_scheme": "eye_catching"
            },
            ThumbnailStyle.QUESTION: {
                "style_name": "question",
                "elements": ["text", "curiosity"],
                "layout": "question_mark",
                "text_style": "intriguing",
                "background": "mystery",
                "color_scheme": "curious"
            },
            ThumbnailStyle.COMPARISON: {
                "style_name": "comparison",
                "elements": ["contrast", "text"],
                "layout": "split_screen",
                "text_style": "versus",
                "background": "divided",
                "color_scheme": "contrasting"
            },
            ThumbnailStyle.TUTORIAL: {
                "style_name": "tutorial",
                "elements": ["text", "numbers"],
                "layout": "step_by_step",
                "text_style": "educational",
                "background": "clean",
                "color_scheme": "professional"
            },
            ThumbnailStyle.REACTION: {
                "style_name": "reaction",
                "elements": ["face", "emotion"],
                "layout": "reaction_shot",
                "text_style": "expressive",
                "background": "emotional",
                "color_scheme": "emotional"
            }
        }
        
        # Select base style
        base_config = style_configs[request.style]
        
        # Customize based on analysis
        if analysis["emotions"]:
            base_config["elements"].extend(analysis["emotions"])
        
        if request.include_face and "face" not in base_config["elements"]:
            base_config["elements"].append("face")
        
        # Platform-specific adjustments
        if request.platform == "tiktok":
            base_config["layout"] = "vertical_focus"
        elif request.platform == "youtube":
            base_config["elements"].append("branding")
        
        return base_config
    
    async def _generate_color_palette(
        self, request: ThumbnailRequest, style_config: Dict[str, Any]
    ) -> List[str]:
        """Generate optimal color palette for the thumbnail."""
        
        base_colors = request.brand_colors if request.brand_colors else [
            "#FF0000", "#000000", "#FFFFFF"  # Default red, black, white
        ]
        
        # Add emotional colors based on content
        emotional_colors = []
        if style_config.get("color_scheme") == "high_contrast":
            emotional_colors.extend(["#000000", "#FFFFFF", "#FF0000"])
        elif style_config.get("color_scheme") == "dramatic":
            emotional_colors.extend(["#1a1a1a", "#FFD700", "#8B0000"])
        elif style_config.get("color_scheme") == "eye_catching":
            emotional_colors.extend(["#FF1493", "#00FF00", "#FFD700"])
        elif style_config.get("color_scheme") == "curious":
            emotional_colors.extend(["#4B0082", "#FFA500", "#FFFFFF"])
        
        # Combine and deduplicate
        all_colors = list(set(base_colors + emotional_colors))
        
        return all_colors[:5]  # Return top 5 colors
    
    async def _create_thumbnail_composition(
        self, request: ThumbnailRequest, style_config: Dict[str, Any],
        color_palette: List[str], analysis: Dict[str, Any]
    ) -> Image.Image:
        """Create the base thumbnail composition."""
        
        # Get dimensions for platform
        dimensions = self.platform_dimensions.get(
            request.platform, 
            self.platform_dimensions["youtube"]
        )
        
        # Create base image
        image = Image.new("RGB", (dimensions["width"], dimensions["height"]), "white")
        draw = ImageDraw.Draw(image)
        
        # Apply background based on style
        if style_config.get("background") == "gradient":
            image = self._apply_gradient_background(image, color_palette)
        elif style_config.get("background") == "dark_moody":
            image = self._apply_dark_background(image, color_palette)
        elif style_config.get("background") == "vibrant":
            image = self._apply_vibrant_background(image, color_palette)
        
        # Add visual elements
        if "face" in style_config["elements"] and request.include_face:
            image = self._add_face_element(image, style_config)
        
        if "emotion" in style_config["elements"]:
            image = self._add_emotion_element(image, analysis["emotions"], color_palette)
        
        if "contrast" in style_config["elements"]:
            image = self._add_contrast_element(image, color_palette)
        
        return image
    
    def _apply_gradient_background(self, image: Image.Image, colors: List[str]) -> Image.Image:
        """Apply gradient background to image."""
        
        width, height = image.size
        gradient = Image.new("RGB", (width, height))
        
        # Create simple gradient (top to bottom)
        for y in range(height):
            ratio = y / height
            # Interpolate between colors
            color1 = self._hex_to_rgb(colors[0] if len(colors) > 0 else "#000000")
            color2 = self._hex_to_rgb(colors[1] if len(colors) > 1 else "#FFFFFF")
            
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            
            for x in range(width):
                gradient.putpixel((x, y), (r, g, b))
        
        return gradient
    
    def _apply_dark_background(self, image: Image.Image, colors: List[str]) -> Image.Image:
        """Apply dark moody background."""
        
        width, height = image.size
        dark_color = self._hex_to_rgb("#1a1a1a")
        
        dark_image = Image.new("RGB", (width, height), dark_color)
        
        # Add subtle gradient
        for y in range(height):
            ratio = y / height * 0.3  # Subtle gradient
            accent_color = self._hex_to_rgb(colors[1] if len(colors) > 1 else "#333333")
            
            r = int(dark_color[0] * (1 - ratio) + accent_color[0] * ratio)
            g = int(dark_color[1] * (1 - ratio) + accent_color[1] * ratio)
            b = int(dark_color[2] * (1 - ratio) + accent_color[2] * ratio)
            
            for x in range(width):
                dark_image.putpixel((x, y), (r, g, b))
        
        return dark_image
    
    def _apply_vibrant_background(self, image: Image.Image, colors: List[str]) -> Image.Image:
        """Apply vibrant eye-catching background."""
        
        width, height = image.size
        
        # Create vibrant gradient with multiple colors
        vibrant_image = Image.new("RGB", (width, height))
        
        for y in range(height):
            ratio = y / height
            
            # Use 3 colors for vibrant effect
            if ratio < 0.33:
                color1 = self._hex_to_rgb(colors[0] if len(colors) > 0 else "#FF1493")
                color2 = self._hex_to_rgb(colors[1] if len(colors) > 1 else "#00FF00")
                local_ratio = ratio / 0.33
            elif ratio < 0.67:
                color1 = self._hex_to_rgb(colors[1] if len(colors) > 1 else "#00FF00")
                color2 = self._hex_to_rgb(colors[2] if len(colors) > 2 else "#FFD700")
                local_ratio = (ratio - 0.33) / 0.34
            else:
                color1 = self._hex_to_rgb(colors[2] if len(colors) > 2 else "#FFD700")
                color2 = self._hex_to_rgb(colors[0] if len(colors) > 0 else "#FF1493")
                local_ratio = (ratio - 0.67) / 0.33
            
            r = int(color1[0] * (1 - local_ratio) + color2[0] * local_ratio)
            g = int(color1[1] * (1 - local_ratio) + color2[1] * local_ratio)
            b = int(color1[2] * (1 - local_ratio) + color2[2] * local_ratio)
            
            for x in range(width):
                vibrant_image.putpixel((x, y), (r, g, b))
        
        return vibrant_image
    
    def _add_face_element(self, image: Image.Image, style_config: Dict[str, Any]) -> Image.Image:
        """Add face element to thumbnail (placeholder for AI generation)."""
        
        # This would integrate with AI face generation
        # For now, add a placeholder circle
        draw = ImageDraw.Draw(image)
        width, height = image.size
        
        # Add face placeholder
        face_size = min(width, height) // 3
        face_x = (width - face_size) // 2
        face_y = (height - face_size) // 2
        
        # Draw simple face placeholder
        draw.ellipse(
            [face_x, face_y, face_x + face_size, face_y + face_size],
            fill="#FFB6C1", outline="#FF69B4", width=3
        )
        
        # Add eyes
        eye_y = face_y + face_size // 3
        left_eye_x = face_x + face_size // 3
        right_eye_x = face_x + 2 * face_size // 3
        
        draw.ellipse(
            [left_eye_x - 10, eye_y - 5, left_eye_x + 10, eye_y + 5],
            fill="#000000"
        )
        draw.ellipse(
            [right_eye_x - 10, eye_y - 5, right_eye_x + 10, eye_y + 5],
            fill="#000000"
        )
        
        # Add mouth based on emotion
        mouth_y = face_y + 2 * face_size // 3
        if style_config.get("text_style") == "expressive":
            # Happy mouth
            draw.arc(
                [face_x + face_size // 4, mouth_y - 20, 
                 face_x + 3 * face_size // 4, mouth_y + 20],
                0, 180, fill="#000000", width=3
            )
        else:
            # Neutral mouth
            draw.line(
                [face_x + face_size // 4, mouth_y, face_x + 3 * face_size // 4, mouth_y],
                fill="#000000", width=3
            )
        
        return image
    
    def _add_emotion_element(
        self, image: Image.Image, emotions: List[str], colors: List[str]
    ) -> Image.Image:
        """Add emotion-based visual elements."""
        
        draw = ImageDraw.Draw(image)
        width, height = image.size
        
        for emotion in emotions[:2]:  # Limit to 2 emotions
            if emotion == "excitement":
                # Add exclamation marks
                for i in range(3):
                    x = width - 50 - i * 30
                    y = 30 + i * 20
                    draw.text((x, y), "!", fill="#FF0000", font_size=40)
            
            elif emotion == "curiosity":
                # Add question marks
                for i in range(2):
                    x = 30 + i * 40
                    y = 30 + i * 15
                    draw.text((x, y), "?", fill="#4B0082", font_size=35)
            
            elif emotion == "fear":
                # Add warning triangles
                for i in range(2):
                    x = width - 80 - i * 50
                    y = height - 80 - i * 30
                    points = [
                        (x, y - 20), (x - 20, y + 20), (x + 20, y + 20)
                    ]
                    draw.polygon(points, fill="#FF0000")
        
        return image
    
    def _add_contrast_element(self, image: Image.Image, colors: List[str]) -> Image.Image:
        """Add contrast elements for visual impact."""
        
        draw = ImageDraw.Draw(image)
        width, height = image.size
        
        # Add contrasting shapes
        if len(colors) >= 2:
            color1 = self._hex_to_rgb(colors[0])
            color2 = self._hex_to_rgb(colors[1])
            
            # Add diagonal split
            for y in range(height):
                for x in range(width):
                    if x + y < width + height // 2:
                        image.putpixel((x, y), color1)
                    else:
                        image.putpixel((x, y), color2)
        
        return image
    
    async def _add_text_overlays(
        self, image: Image.Image, request: ThumbnailRequest, style_config: Dict[str, Any]
    ) -> Image.Image:
        """Add text overlays to thumbnail."""
        
        draw = ImageDraw.Draw(image)
        width, height = image.size
        
        # Extract key text from title
        title_words = request.video_title.split()
        max_words = self.text_optimization["max_words"]
        key_text = " ".join(title_words[:max_words])
        
        # Calculate font size
        font_size = int(height * self.text_optimization["font_size_ratio"])
        
        # Add main text
        text_color = "#FFFFFF"  # Default white for contrast
        if style_config.get("color_scheme") == "high_contrast":
            text_color = "#FFFF00"  # Yellow for high contrast
        
        # Calculate text position (centered)
        try:
            # Try to load a font
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            # Fallback to default font
            font = ImageFont.load_default()
        
        # Get text dimensions
        bbox = draw.textbbox((0, 0), key_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Center text
        text_x = (width - text_width) // 2
        text_y = (height - text_height) // 2
        
        # Add text shadow for better readability
        shadow_offset = 3
        draw.text(
            (text_x + shadow_offset, text_y + shadow_offset),
            key_text, fill="#000000", font=font
        )
        
        # Add main text
        draw.text((text_x, text_y), key_text, fill=text_color, font=font)
        
        # Add call to action if provided
        if request.call_to_action:
            cta_font_size = font_size // 2
            try:
                cta_font = ImageFont.truetype("arial.ttf", cta_font_size)
            except:
                cta_font = ImageFont.load_default()
            
            cta_y = text_y + text_height + 20
            draw.text(
                (text_x, cta_y), request.call_to_action,
                fill="#FFD700", font=cta_font
            )
        
        return image
    
    async def _apply_optimizations(
        self, image: Image.Image, style_config: Dict[str, Any]
    ) -> Image.Image:
        """Apply final optimizations to thumbnail."""
        
        # Apply slight sharpening for clarity
        image = image.filter(ImageFilter.SHARPEN)
        
        # Adjust brightness and contrast
        from PIL import ImageEnhance
        
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.2)  # Increase contrast by 20%
        
        # Enhance brightness
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(1.1)  # Increase brightness by 10%
        
        return image
    
    async def _save_thumbnail(self, image: Image.Image, request: ThumbnailRequest) -> str:
        """Save thumbnail to file system."""
        
        # Create filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"thumbnail_{request.platform}_{timestamp}.jpg"
        
        # Create directory if it doesn't exist
        thumbnail_dir = os.path.join("uploads", "thumbnails")
        os.makedirs(thumbnail_dir, exist_ok=True)
        
        # Save image
        thumbnail_path = os.path.join(thumbnail_dir, filename)
        image.save(thumbnail_path, "JPEG", quality=95)
        
        return thumbnail_path
    
    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple."""
        
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    async def _calculate_confidence_score(
        self, request: ThumbnailRequest, style_config: Dict[str, Any], analysis: Dict[str, Any]
    ) -> float:
        """Calculate confidence score for the generated thumbnail."""
        
        confidence = 0.5  # Base confidence
        
        # Boost confidence based on elements used
        element_boost = len(style_config["elements"]) * 0.1
        confidence += element_boost
        
        # Boost based on color palette
        if len(request.brand_colors) >= 3:
            confidence += 0.1
        
        # Boost based on content analysis
        if analysis["keywords"]:
            confidence += 0.1
        
        if analysis["emotions"]:
            confidence += 0.1
        
        # Boost based on text optimization
        if request.include_text and len(request.video_title.split()) <= 6:
            confidence += 0.1
        
        return min(1.0, confidence)
    
    async def _predict_engagement(
        self, style_config: Dict[str, Any], analysis: Dict[str, Any]
    ) -> float:
        """Predict engagement rate for the thumbnail."""
        
        base_ctr = 0.05  # 5% base CTR
        
        # Add boosts for high-CTR elements
        for element in style_config["elements"]:
            if element in self.high_ctr_elements:
                base_ctr += self.high_ctr_elements[element]["ctr_boost"]
        
        # Add boost for emotional content
        if analysis["emotions"]:
            base_ctr += 0.05
        
        # Add boost for keywords
        if analysis["keywords"]:
            base_ctr += len(analysis["keywords"]) * 0.02
        
        # Cap at reasonable maximum
        return min(base_ctr, 0.25)  # Max 25% CTR
    
    async def get_style_recommendations(
        self, video_title: str, platform: str, target_audience: str
    ) -> List[Dict[str, Any]]:
        """Get style recommendations for a video."""
        
        recommendations = []
        
        # Analyze title for style hints
        title_lower = video_title.lower()
        
        if any(word in title_lower for word in ["shocking", "revealed", "secret"]):
            recommendations.append({
                "style": ThumbnailStyle.BOLD_TEXT,
                "reason": "Title contains curiosity-inducing words",
                "confidence": 0.8
            })
        
        if any(word in title_lower for word in ["tutorial", "how to", "guide"]):
            recommendations.append({
                "style": ThumbnailStyle.TUTORIAL,
                "reason": "Educational content detected",
                "confidence": 0.9
            })
        
        if any(word in title_lower for word in ["vs", "versus", "comparison"]):
            recommendations.append({
                "style": ThumbnailStyle.COMPARISON,
                "reason": "Comparison content detected",
                "confidence": 0.85
            })
        
        if "?" in video_title:
            recommendations.append({
                "style": ThumbnailStyle.QUESTION,
                "reason": "Question-based title detected",
                "confidence": 0.75
            })
        
        # Platform-specific recommendations
        if platform == "tiktok":
            recommendations.append({
                "style": ThumbnailStyle.TRENDING,
                "reason": "TikTok benefits from trending styles",
                "confidence": 0.7
            })
        elif platform == "youtube":
            recommendations.append({
                "style": ThumbnailStyle.CINEMATIC,
                "reason": "YouTube benefits from cinematic thumbnails",
                "confidence": 0.6
            })
        
        return recommendations


# Singleton instance
thumbnail_creative_engine = ThumbnailCreativeEngine()
