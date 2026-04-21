from typing import List, Dict, Optional


# Topic expansion keywords
EXPANSION_KEYWORDS = {
    "how": ["works", "actually", "really", "actually works"],
    "why": ["matters", "important", "matters more"],
    "what": ["nobody tells you", "you need to know", "the truth about"],
    "best": ["tips", "strategies", "ways", "methods"],
    "mistake": ["people make", "you're making", "to avoid"],
    "secret": ["nobody talks about", "that nobody knows", "about"],
}


def expand_topic(topic: str, angle: str = "curiosity") -> List[str]:
    """
    Expand a topic into multiple angles/variations.
    """
    topic_lower = topic.lower()
    expansions = []
    
    if angle == "curiosity":
        expansions = [
            f"How {topic_lower} actually works",
            f"Why {topic_lower} matters more than you think",
            f"The secret about {topic_lower} nobody tells you",
            f"What nobody tells you about {topic_lower}",
        ]
    elif angle == "controversy":
        expansions = [
            f"Everyone thinks {topic_lower} is great. They're wrong.",
            f"The biggest mistake people make with {topic_lower}",
            f"Nobody talks about the truth regarding {topic_lower}",
        ]
    elif angle == "story":
        expansions = [
            f"I tried {topic_lower} for 30 days. Here's what happened.",
            f"What happened when I started {topic_lower}",
            f"The story of {topic_lower} nobody knows",
        ]
    elif angle == "authority":
        expansions = [
            f"Best {topic_lower} strategy (backed by data)",
            f"Top 5 {topic_lower} tips that actually work",
            f"Ultimate guide to {topic_lower}",
        ]
    else:
        expansions = [
            f"Everything about {topic_lower} you need to know",
            f"Why {topic_lower} is worth your time",
        ]
    
    return expansions


def generate_topic_variants(base_topic: str, count: int = 5) -> List[Dict[str, str]]:
    """
    Generate multiple topic variants with different angles.
    """
    angles = ["curiosity", "controversy", "story", "authority"]
    variants = []
    
    for angle in angles[:count]:
        expanded = expand_topic(base_topic, angle)
        variants.append({
            "angle": angle,
            "hooks": expanded,
        })
    
    return variants


def extract_topic_keywords(topic: str) -> List[str]:
    """
    Extract key terms from a topic for expansion.
    """
    words = topic.lower().split()
    
    # Filter out common stop words
    stop_words = {"the", "a", "an", "is", "are", "was", "were", "to", "of", "in", "for", "on", "with", "about"}
    keywords = [w for w in words if w not in stop_words and len(w) > 2]
    
    return keywords