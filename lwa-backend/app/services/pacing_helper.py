from typing import List, Dict, Optional
import re


def analyze_pacing(text: str) -> Dict[str, any]:
    """
    Analyze the pacing/rhythm of text for short-form optimization.
    """
    words = text.split()
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if not words:
        return {"rhythm_score": 0, "pacing_type": "unknown"}
    
    # Word-level analysis
    avg_word_length = sum(len(w) for w in words) / len(words)
    short_words = sum(1 for w in words if len(w) <= 3)
    short_word_ratio = short_words / len(words)
    
    # Sentence-level analysis
    avg_sentence_length = len(words) / max(len(sentences), 1)
    
    # Pacing type determination
    if short_word_ratio > 0.4 and avg_sentence_length < 8:
        pacing_type = "fast_rapid"
    elif short_word_ratio > 0.25:
        pacing_type = "moderate"
    else:
        pacing_type = "measured"
    
    # Rhythm score (higher = more punchy for short-form)
    rhythm_score = int((short_word_ratio * 40) + (30 if avg_sentence_length < 12 else 0))
    
    return {
        "rhythm_score": min(rhythm_score, 100),
        "pacing_type": pacing_type,
        "avg_word_length": round(avg_word_length, 2),
        "short_word_ratio": round(short_word_ratio, 2),
        "avg_sentence_length": round(avg_sentence_length, 1),
        "word_count": len(words),
    }


def optimize_for_pacing(text: str, target_type: str = "fast_rapid") -> str:
    """
    Optimize text for a specific pacing type.
    """
    analysis = analyze_pacing(text)
    
    if target_type == "fast_rapid":
        # Shorten sentences, use shorter words
        words = text.split()
        optimized = []
        for word in words:
            if len(word) > 6 and len(word) > 3:
                # Keep but don't elongate
                optimized.append(word)
            else:
                optimized.append(word)
        return " ".join(optimized[:20])  # Cap at 20 words
    
    return text


def detect_beat_markers(text: str) -> List[Dict[str, any]]:
    """
    Detect beat markers (pauses, emphasis points) in text.
    """
    beat_markers = []
    words = text.split()
    
    for i, word in enumerate(words):
        markers = []
        
        # Punctuation markers
        if word.endswith("?"):
            markers.append("curiosity_beat")
        if word.endswith("!"):
            markers.append("energy_beat")
        if "..." in word:
            markers.append("anticipation_beat")
        
        # Position markers
        if i == 0:
            markers.append("opening_beat")
        if i == len(words) - 1:
            markers.append("closing_beat")
        
        # Power word markers
        power_words = ["stop", "wait", "here", "this", "how", "why", "secret", "best", "top"]
        if word.lower() in power_words:
            markers.append("power_word")
        
        if markers:
            beat_markers.append({
                "word": word,
                "position": i,
                "markers": markers,
            })
    
    return beat_markers