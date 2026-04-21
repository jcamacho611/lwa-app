from typing import Dict, List, Optional


def extract_style_features(hook: str, caption: str = "") -> Dict[str, any]:
    """
    Extract style features from a hook/caption for style replication.
    """
    text = f"{hook} {caption}".lower()
    words = text.split()

    # Pacing analysis
    avg_word_length = sum(len(w) for w in words) / max(len(words), 1)
    
    # Sentence structure
    has_questions = "?" in hook
    has_exclamation = "!" in hook
    has_ellipsis = "..." in hook
    
    # Tone indicators
    is_controversial = any(w in text for w in ["wrong", "mistake", "nobody", "never", "stop"])
    is_curious = any(w in text for w in ["how", "why", "secret", "this"])
    is_story = any(w in text for w in ["story", "happened", "then", "finally"])
    is_authority = any(w in text for w in ["best", "top", "most", "ultimate"])
    
    # Length category
    if len(words) <= 10:
        length_category = "ultra_short"
    elif len(words) <= 18:
        length_category = "short_form"
    elif len(words) <= 30:
        length_category = "medium"
    else:
        length_category = "long"

    return {
        "avg_word_length": round(avg_word_length, 2),
        "word_count": len(words),
        "has_questions": has_questions,
        "has_exclamation": has_exclamation,
        "has_ellipsis": has_ellipsis,
        "tone_controversial": is_controversial,
        "tone_curious": is_curious,
        "tone_story": is_story,
        "tone_authority": is_authority,
        "length_category": length_category,
    }


def detect_style_pattern(hooks: List[str]) -> Dict[str, any]:
    """
    Detect common style patterns across multiple hooks.
    """
    if not hooks:
        return {"style_type": "neutral", "confidence": 0.0}

    features = [extract_style_features(h) for h in hooks]
    
    # Aggregate tone signals
    tone_scores = {
        "controversy": sum(1 for f in features if f["tone_controversial"]),
        "curiosity": sum(1 for f in features if f["tone_curious"]),
        "story": sum(1 for f in features if f["tone_story"]),
        "authority": sum(1 for f in features if f["tone_authority"]),
    }
    
    dominant_tone = max(tone_scores, key=tone_scores.get)
    confidence = tone_scores[dominant_tone] / len(features) if features else 0
    
    # Length consensus
    length_counts = {}
    for f in features:
        lc = f["length_category"]
        length_counts[lc] = length_counts.get(lc, 0) + 1
    consensus_length = max(length_counts, key=length_counts.get) if length_counts else "short_form"
    
    return {
        "style_type": dominant_tone,
        "confidence": round(confidence, 2),
        "length_category": consensus_length,
        "avg_word_count": sum(f["word_count"] for f in features) / len(features),
        "question_ratio": sum(1 for f in features if f["has_questions"]) / len(features),
    }


def replicate_style(source_hooks: List[str], target_topic: str) -> List[str]:
    """
    Replicate the style from source hooks onto a new topic.
    This is a stub - full implementation would use LLM.
    """
    style = detect_style_pattern(source_hooks)
    
    # Simple pattern-based replication (placeholder for LLM)
    templates = {
        "controversy": [
            f"Everyone thinks {target_topic} is great. They're wrong.",
            f"Nobody talks about the truth about {target_topic}.",
            f"This is the biggest mistake people make about {target_topic}.",
        ],
        "curiosity": [
            f"How {target_topic} actually works (nobody explains this).",
            f"Why {target_topic} matters more than you think.",
            f"The secret about {target_topic} nobody tells you.",
        ],
        "story": [
            f"I tried {target_topic} for 30 days. Here's what happened.",
            f"What happened when I started {target_topic}.",
            f"The story of {target_topic} nobody knows.",
        ],
        "authority": [
            f"The best {target_topic} strategy (backed by data).",
            f"Top 5 {target_topic} tips that actually work.",
            f"Ultimate guide to {target_topic}.",
        ],
    }
    
    return templates.get(style["style_type"], templates["curiosity"])