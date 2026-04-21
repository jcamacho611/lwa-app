from typing import Dict, List, Optional


# CTA patterns by tone
CTA_PATTERNS = {
    "curiosity": [
        "Comment your take.",
        "What do you think?",
        "Drop your opinion below.",
    ],
    "engagement": [
        "Follow for more.",
        "Like and follow.",
        "Don't miss the next one.",
    ],
    "authority": [
        "Save this for later.",
        "Save this.",
        "Bookmark this.",
    ],
    "viral": [
        "Share this.",
        "Send this to someone who needs to see it.",
        "Tag someone who needs to know.",
    ],
    "story": [
        "Part 2 coming soon.",
        "Follow to see what happens next.",
        "Next part drops tomorrow.",
    ],
}


def detect_cta_style(cta: str) -> Dict[str, any]:
    """
    Detect the style/tone of a CTA.
    """
    cta_lower = cta.lower()
    
    style = "neutral"
    if any(w in cta_lower for w in ["comment", "opinion", "take"]):
        style = "curiosity"
    elif any(w in cta_lower for w in ["save", "bookmark"]):
        style = "authority"
    elif any(w in cta_lower for w in ["share", "send", "tag"]):
        style = "viral"
    elif any(w in cta_lower for w in ["follow", "next", "part"]):
        style = "story"
    elif any(w in cta_lower for w in ["like", "follow"]):
        style = "engagement"
    
    return {
        "style": style,
        "is_actionable": any(w in cta_lower for w in ["save", "share", "comment", "follow", "tag"]),
    }


def generate_cta_for_style(hook_style: str) -> str:
    """
    Generate a CTA that matches the hook style.
    """
    ctas = CTA_PATTERNS.get(hook_style, CTA_PATTERNS["engagement"])
    return ctas[0]  # Return first option


def extract_cta_features(ctas: List[str]) -> Dict[str, any]:
    """
    Extract common features from a list of CTAs.
    """
    styles = [detect_cta_style(c) for c in ctas]
    
    style_counts = {}
    for s in styles:
        style_counts[s["style"]] = style_counts.get(s["style"], 0) + 1
    
    dominant_style = max(style_counts, key=style_counts.get) if style_counts else "neutral"
    actionability_ratio = sum(1 for s in styles if s["is_actionable"]) / len(styles) if styles else 0
    
    return {
        "dominant_style": dominant_style,
        "actionability_ratio": round(actionability_ratio, 2),
        "style_distribution": style_counts,
    }