"""Deterministic clip generation engine - no AI APIs required."""
from __future__ import annotations
import re
import random
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from collections import Counter

# Template libraries
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
]

EMOTIONAL_KEYWORDS = {
    "high": ["truth", "secret", "mistake", "wrong", "never", "always", "nobody", "everyone", "proof", "exposed"],
    "medium": ["important", "crucial", "essential", "must", "need", "key", "critical", "powerful", "proven"],
}

STRONG_PATTERNS = [
    r"\bthis is (why|how|what|the)\b",
    r"\bstop (doing|saying|thinking)\b",
    r"\byou('re| are) (doing|getting|missing)\b",
    r"\bmost people\b",
    r"\bnobody tells you\b",
    r"\bthe real (reason|truth|problem)\b",
    r"\bif you want\b",
]

@dataclass
class ClipResult:
    clip_id: str
    hook: str
    caption: str
    text_content: str
    ai_score: float
    why_this_works: str
    cta: str
    thumbnail_text: str
    duration: int
    status: str = "strategy_only"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "clip_id": self.clip_id,
            "hook": self.hook,
            "caption": self.caption,
            "text": self.text_content,
            "ai_score": round(self.ai_score, 2),
            "why_this_matters": self.why_this_works,
            "cta": self.cta,
            "thumbnail_text": self.thumbnail_text,
            "duration_seconds": self.duration,
            "render_status": self.status,
        }


class DeterministicClipEngine:
    """Offline-first clip generation using heuristics and templates."""
    
    def __init__(self):
        self.high_kw = set(EMOTIONAL_KEYWORDS["high"])
        self.medium_kw = set(EMOTIONAL_KEYWORDS["medium"])
        self.patterns = [re.compile(p, re.IGNORECASE) for p in STRONG_PATTERNS]
        self.clip_counter = 0
    
    def generate_clips(self, text: str, min_clips: int = 3) -> List[ClipResult]:
        """Generate clips from text input. Always returns at least min_clips."""
        sentences = self._split_sentences(text)
        if len(sentences) < 2:
            # If too short, duplicate to meet minimum
            sentences = sentences * min_clips
        
        scored = self._score_sentences(sentences)
        segments = self._build_segments(scored, min_clips)
        
        clips = []
        for seg in segments[:10]:  # Max 10 clips
            self.clip_counter += 1
            clip = self._create_clip(seg, self.clip_counter)
            clips.append(clip)
        
        # Ensure minimum clips
        while len(clips) < min_clips:
            self.clip_counter += 1
            clips.append(self._create_fallback_clip(sentences, self.clip_counter))
        
        return clips
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        text = text.replace("\n", " ").strip()
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _score_sentences(self, sentences: List[str]) -> List[tuple]:
        """Score sentences: (index, text, score)."""
        scored = []
        for i, sent in enumerate(sentences):
            score = self._calculate_score(sent)
            scored.append((i, sent, score))
        return scored
    
    def _calculate_score(self, sentence: str) -> float:
        """Calculate sentence score using heuristics."""
        text_lower = sentence.lower()
        words = set(re.findall(r'\b\w+\b', text_lower))
        
        # Keyword scoring
        score = len(words & self.high_kw) * 0.3 + len(words & self.medium_kw) * 0.15
        
        # Pattern matching
        score += sum(0.25 for p in self.patterns if p.search(sentence))
        
        # Emotional punctuation
        if "!" in sentence:
            score += 0.2
        
        # Length scoring (8-20 words ideal)
        word_count = len(sentence.split())
        if 8 <= word_count <= 20:
            score += 0.2
        elif 5 <= word_count <= 25:
            score += 0.1
        
        return min(score, 1.0)
    
    def _build_segments(self, scored: List[tuple], min_segments: int) -> List[List[tuple]]:
        """Build clip segments from scored sentences."""
        # Sort by score descending
        sorted_sentences = sorted(scored, key=lambda x: x[2], reverse=True)
        
        segments = []
        used_indices = set()
        
        for idx, sent, score in sorted_sentences:
            if idx in used_indices:
                continue
            
            # Build segment: anchor + 1-2 neighbors
            segment = [(idx, sent, score)]
            used_indices.add(idx)
            
            # Add next sentence if available and not used
            if idx + 1 < len(scored) and (idx + 1) not in used_indices:
                next_sent = scored[idx + 1]
                segment.append(next_sent)
                used_indices.add(idx + 1)
            
            # Add previous if segment is short
            if len(segment) < 2 and idx - 1 >= 0 and (idx - 1) not in used_indices:
                prev_sent = scored[idx - 1]
                segment.insert(0, prev_sent)
                used_indices.add(idx - 1)
            
            if len(segment) >= 2:
                segments.append(segment)
        
        # Add remaining as segments if needed
        remaining = [s for s in scored if s[0] not in used_indices]
        for i in range(0, len(remaining), 2):
            chunk = remaining[i:i+2]
            if len(chunk) >= 2:
                segments.append(chunk)
        
        return segments
    
    def _create_clip(self, segment: List[tuple], counter: int) -> ClipResult:
        """Create a ClipResult from a segment."""
        # Combine sentences
        texts = [s[1] for s in segment]
        full_text = " ".join(texts)
        
        # Calculate score
        avg_score = sum(s[2] for s in segment) / len(segment)
        
        # Extract topic
        topic = self._extract_topic(full_text)
        
        # Generate content
        hook = self._generate_hook(topic)
        caption = random.choice(CAPTION_TEMPLATES)
        cta = f"Follow for more {topic} tips"
        thumbnail = self._generate_thumbnail(texts)
        why = self._generate_why(segment)
        
        # Duration estimate
        words = len(full_text.split())
        duration = max(15, min(60, int(words / 150 * 60)))
        
        return ClipResult(
            clip_id=f"clip_{counter:03d}",
            hook=hook,
            caption=caption,
            text_content=full_text,
            ai_score=avg_score,
            why_this_works=why,
            cta=cta,
            thumbnail_text=thumbnail,
            duration=duration,
        )
    
    def _create_fallback_clip(self, sentences: List[str], counter: int) -> ClipResult:
        """Create a fallback clip when needed."""
        text = " ".join(sentences[:3]) if len(sentences) >= 3 else " ".join(sentences)
        topic = self._extract_topic(text)
        
        return ClipResult(
            clip_id=f"clip_{counter:03d}",
            hook=f"This is everything about {topic}",
            caption="You need to see this.",
            text_content=text,
            ai_score=0.5,
            why_this_works="Covers the essential points clearly.",
            cta="Follow for more",
            thumbnail_text="KEY POINT",
            duration=20,
        )
    
    def _extract_topic(self, text: str) -> str:
        """Extract main topic from text."""
        words = re.findall(r'\b[a-z]{4,}\b', text.lower())
        common = {"this", "that", "with", "from", "they", "have", "were", "been", "their", "what", "when", "where", "which", "while", "about"}
        candidates = [w for w in words if w not in common]
        
        if candidates:
            most_common = Counter(candidates).most_common(1)[0][0]
            return most_common
        return "content"
    
    def _generate_hook(self, topic: str) -> str:
        """Generate hook using templates."""
        template = random.choice(HOOK_TEMPLATES)
        return template.format(topic=topic, outcome="success")
    
    def _generate_thumbnail(self, sentences: List[str]) -> str:
        """Generate thumbnail text."""
        all_text = " ".join(sentences).upper()
        
        # Look for capitalized phrases or important words
        for phrase in ["TRUTH", "SECRET", "MISTAKE", "STOP", "WARNING", "THIS"]:
            if phrase in all_text:
                return phrase
        
        # Return first 2-3 significant words
        words = [w for w in all_text.split() if len(w) > 3]
        if words:
            return " ".join(words[:2])
        
        return "WATCH THIS"
    
    def _generate_why(self, segment: List[tuple]) -> str:
        """Generate explanation of why clip works."""
        scores = [s[2] for s in segment]
        avg = sum(scores) / len(scores)
        
        if avg > 0.7:
            return "High emotional intensity with strong keywords and clear value proposition."
        elif avg > 0.5:
            return "Good engagement potential with relevant keywords and clear message."
        else:
            return "Solid content chunk that provides value to the viewer."


# Global instance
_clip_engine: Optional[DeterministicClipEngine] = None

def get_clip_engine() -> DeterministicClipEngine:
    """Get or create the global clip engine instance."""
    global _clip_engine
    if _clip_engine is None:
        _clip_engine = DeterministicClipEngine()
    return _clip_engine

def generate_clips_offline(text: str, min_clips: int = 3) -> List[Dict[str, Any]]:
    """Generate clips without any AI APIs. Always returns results."""
    engine = get_clip_engine()
    clips = engine.generate_clips(text, min_clips)
    return [c.to_dict() for c in clips]
