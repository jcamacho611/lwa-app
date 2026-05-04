"""Analysis Engine - Deterministic Content Intelligence (NO AI REQUIRED)

This module provides a fully self-contained content intelligence system
that analyzes text and generates clips using heuristics, templates,
and keyword scoring. Works 100% offline without any external AI dependencies.

CORE PRINCIPLE: Always return at least 3 clips, never fail.
"""

from __future__ import annotations

import re
import random
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from collections import Counter


# =============================================================================
# CONFIGURATION
# =============================================================================

# Emotional keywords that signal strong moments
EMOTIONAL_KEYWORDS = {
    "high": [
        "truth", "secret", "mistake", "wrong", "never", "always",
        "nobody", "everyone", "impossible", "guaranteed", "proof",
        "exposed", "hidden", "real reason", "actually", "honestly",
        "devastating", "shocking", "surprising", "unexpected", "reveal",
    ],
    "medium": [
        "important", "crucial", "essential", "must", "need", "should",
        "key", "critical", "vital", "necessary", "fundamental",
        "powerful", "effective", "proven", "tested", "works",
    ],
}

# Pattern detection for strong claims
STRONG_PATTERNS = [
    r"\bthis is (why|how|what|the)\b",
    r"\bstop (doing|saying|thinking)\b",
    r"\byou('re| are) (doing|getting|missing)\b",
    r"\bmost people\b",
    r"\bnobody tells you\b",
    r"\bthe real (reason|truth|problem)\b",
    r"\bif you want\b",
    r"\bhere's (what|why|how)\b",
    r"\byou need to\b",
]

HOOK_TEMPLATES = [
    "Nobody tells you this about {topic}",
    "This changes everything about {topic}",
    "You're doing {topic} wrong",
    "This is why you're not growing with {topic}",
    "The truth about {topic} nobody talks about",
    "Stop doing this with {topic}",
    "This {topic} hack saves hours",
    "If you want {outcome}, do this",
    "Most people get {topic} wrong",
    "The #1 mistake in {topic}",
]

CAPTION_TEMPLATES = [
    "Save this before you forget.",
    "Most people miss this.",
    "This will change how you see this.",
    "Watch this twice.",
    "Tag someone who needs this.",
    "Which part hit you hardest?",
    "This is the secret sauce.",
    "Don't skip this part.",
    "This is pure gold.",
    "The part at 0:15 hits different.",
]

CTA_TEMPLATES = [
    "Follow for more {topic} tips",
    "Save this for later",
    "Share with someone who needs this",
    "Comment if this helped",
    "Follow for part 2",
]


@dataclass
class ScoredSentence:
    """A sentence with its calculated importance score."""
    text: str
    index: int
    score: float
    keywords: List[str]
    patterns: List[str]


@dataclass
class ClipSegment:
    """A segment of content ready to become a clip."""
    id: str
    text: str
    hook: str
    caption: str
    cta: str
    thumbnail: str
    score: float
    why: str
    rank: int


class AnalysisEngine:
    """Offline content analysis engine - no AI required."""
    
    def __init__(self):
        self.high_keywords = set(EMOTIONAL_KEYWORDS["high"])
        self.medium_keywords = set(EMOTIONAL_KEYWORDS["medium"])
        self.patterns = [re.compile(p, re.IGNORECASE) for p in STRONG_PATTERNS]
    
    def analyze_text(self, text: str, min_clips: int = 3) -> List[ClipSegment]:
        """Main entry point: analyze text and return clips.
        
        GUARANTEE: Always returns at least min_clips.
        """
        # Step 1: Split into sentences
        sentences = self._split_sentences(text)
        
        if not sentences:
            # Emergency fallback: treat entire text as one sentence
            sentences = [text.strip()] if text.strip() else ["Content ready for analysis."]
        
        # Step 2: Score each sentence
        scored = self._score_sentences(sentences)
        
        # Step 3: Build segments
        segments = self._build_segments(scored)
        
        # Step 4: Generate clips from segments
        clips = self._generate_clips(segments, min_clips)
        
        # Step 5: Ensure minimum clips (duplicate if needed)
        clips = self._ensure_minimum_clips(clips, text, min_clips)
        
        return clips
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        text = text.replace("\n", " ").strip()
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _score_sentences(self, sentences: List[str]) -> List[ScoredSentence]:
        """Score sentences based on keywords, patterns, and heuristics."""
        scored = []
        
        for i, sent in enumerate(sentences):
            text_lower = sent.lower()
            words = set(re.findall(r'\b\w+\b', text_lower))
            
            # Keyword scoring
            score = 0.0
            matched_keywords = []
            
            # High-intensity keywords
            high_matches = words & self.high_keywords
            score += len(high_matches) * 0.3
            matched_keywords.extend(high_matches)
            
            # Medium keywords
            medium_matches = words & self.medium_keywords
            score += len(medium_matches) * 0.15
            matched_keywords.extend(medium_matches)
            
            # Pattern matching
            matched_patterns = []
            for pattern in self.patterns:
                if pattern.search(sent):
                    score += 0.25
                    matched_patterns.append(pattern.pattern[:30])
            
            # Emotional punctuation
            if "!" in sent:
                score += 0.2
            if "?" in sent:
                score += 0.1
            
            # Length scoring (8-20 words ideal)
            word_count = len(sent.split())
            if 8 <= word_count <= 20:
                score += 0.2
            elif 5 <= word_count <= 25:
                score += 0.1
            
            # Cap at 1.0
            score = min(score, 1.0)
            
            scored.append(ScoredSentence(
                text=sent,
                index=i,
                score=score,
                keywords=matched_keywords,
                patterns=matched_patterns
            ))
        
        return scored
    
    def _build_segments(self, scored: List[ScoredSentence]) -> List[List[ScoredSentence]]:
        """Group sentences into 2-4 sentence segments."""
        if len(scored) <= 4:
            # If short, return as one segment
            return [scored] if scored else []
        
        segments = []
        used_indices = set()
        
        # Sort by score descending
        sorted_sentences = sorted(scored, key=lambda s: s.score, reverse=True)
        
        # Build around high-scoring anchor sentences
        for anchor in sorted_sentences[:min(10, len(scored))]:
            if anchor.index in used_indices:
                continue
            
            # Build segment: anchor + 1-2 neighbors
            segment = [anchor]
            used_indices.add(anchor.index)
            
            # Add previous sentence if exists and not used
            if anchor.index - 1 >= 0 and (anchor.index - 1) not in used_indices:
                prev_sent = scored[anchor.index - 1]
                segment.insert(0, prev_sent)
                used_indices.add(anchor.index - 1)
            
            # Add next sentence if exists and not used
            if anchor.index + 1 < len(scored) and (anchor.index + 1) not in used_indices:
                next_sent = scored[anchor.index + 1]
                segment.append(next_sent)
                used_indices.add(anchor.index + 1)
            
            if len(segment) >= 2:
                segments.append(segment)
        
        # Add remaining sentences as filler segments
        remaining = [s for s in scored if s.index not in used_indices]
        for i in range(0, len(remaining), 2):
            chunk = remaining[i:i+2]
            if len(chunk) >= 2:
                segments.append(chunk)
        
        return segments
    
    def _generate_clips(self, segments: List[List[ScoredSentence]], min_clips: int) -> List[ClipSegment]:
        """Generate ClipSegment objects from sentence groups."""
        clips = []
        
        # Sort segments by average score
        def avg_score(seg):
            return sum(s.score for s in seg) / len(seg)
        
        sorted_segments = sorted(segments, key=avg_score, reverse=True)
        
        for i, seg in enumerate(sorted_segments[:10]):  # Max 10 clips
            text = " ".join(s.text for s in seg)
            score = avg_score(seg)
            topic = self._extract_topic(text)
            
            clip = ClipSegment(
                id=f"clip_{i+1:03d}",
                text=text,
                hook=self._generate_hook(topic),
                caption=self._generate_caption(),
                cta=self._generate_cta(topic),
                thumbnail=self._generate_thumbnail(text),
                score=score,
                why=self._generate_why(seg),
                rank=i+1
            )
            clips.append(clip)
        
        return clips
    
    def _ensure_minimum_clips(self, clips: List[ClipSegment], original_text: str, min_clips: int) -> List[ClipSegment]:
        """GUARANTEE: Always return at least min_clips."""
        if len(clips) >= min_clips:
            return clips
        
        # Need to create fallback clips
        topic = self._extract_topic(original_text)
        current_count = len(clips)
        
        for i in range(current_count, min_clips):
            clip = ClipSegment(
                id=f"clip_{i+1:03d}",
                text=original_text[:200] if len(original_text) > 200 else original_text,
                hook=self._generate_hook(topic),
                caption=self._generate_caption(),
                cta=self._generate_cta(topic),
                thumbnail=self._generate_thumbnail(original_text),
                score=0.5,
                why="Fallback clip ensuring you always have content to work with.",
                rank=i+1
            )
            clips.append(clip)
        
        return clips
    
    def _extract_topic(self, text: str) -> str:
        """Extract main topic from text."""
        words = re.findall(r'\b[a-z]{4,}\b', text.lower())
        common = {"this", "that", "with", "from", "they", "have", "were", "been", "their", "what"}
        candidates = [w for w in words if w not in common]
        
        if candidates:
            most_common = Counter(candidates).most_common(1)[0][0]
            return most_common
        return "content"
    
    def _generate_hook(self, topic: str) -> str:
        """Generate hook using templates."""
        template = random.choice(HOOK_TEMPLATES)
        return template.format(topic=topic, outcome="success")
    
    def _generate_caption(self) -> str:
        """Generate caption using templates."""
        return random.choice(CAPTION_TEMPLATES)
    
    def _generate_cta(self, topic: str) -> str:
        """Generate CTA using templates."""
        template = random.choice(CTA_TEMPLATES)
        return template.format(topic=topic)
    
    def _generate_thumbnail(self, text: str) -> str:
        """Generate thumbnail text."""
        text_upper = text.upper()
        for phrase in ["TRUTH", "SECRET", "MISTAKE", "STOP", "WARNING", "THIS"]:
            if phrase in text_upper:
                return phrase
        words = [w for w in text_upper.split() if len(w) > 3]
        if words:
            return " ".join(words[:2])
        return "WATCH THIS"
    
    def _generate_why(self, segment: List[ScoredSentence]) -> str:
        """Generate explanation of why clip works."""
        scores = [s.score for s in segment]
        avg = sum(scores) / len(scores)
        
        if avg > 0.7:
            return "High emotional intensity with strong keywords and clear value proposition."
        elif avg > 0.5:
            return "Good engagement potential with relevant keywords and clear message."
        else:
            return "Solid content chunk that provides value to the viewer."


# Global instance
_engine: Optional[AnalysisEngine] = None

def get_analysis_engine() -> AnalysisEngine:
    """Get or create the global analysis engine instance."""
    global _engine
    if _engine is None:
        _engine = AnalysisEngine()
    return _engine


def analyze_content(text: str, min_clips: int = 3) -> List[Dict[str, Any]]:
    """Analyze text and return clips. ALWAYS returns at least min_clips."""
    engine = get_analysis_engine()
    clips = engine.analyze_text(text, min_clips)
    
    return [
        {
            "clip_id": c.id,
            "hook": c.hook,
            "caption": c.caption,
            "text": c.text,
            "cta": c.cta,
            "thumbnail_text": c.thumbnail,
            "score": round(c.score, 2),
            "why": c.why,
            "rank": c.rank,
        }
        for c in clips
    ]
