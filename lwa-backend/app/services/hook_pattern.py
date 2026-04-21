from typing import List, Dict, Optional
import re


# High-performing hook patterns
HOOK_PATTERNS = {
    "stop": [
        r"\bstop\b",
        r"\bwait\b",
        r"\bhold on\b",
    ],
    "controversy": [
        r"\bwrong\b",
        r"\bmistake\b",
        r"\bnobody\b",
        r"\bnever\b",
    ],
    "curiosity": [
        r"\bhow\b",
        r"\bwhy\b",
        r"\bsecret\b",
        r"\bthis\b",
    ],
    "story": [
        r"\bhappened\b",
        r"\bthen\b",
        r"\bfinally\b",
        r"\bstory\b",
    ],
    "authority": [
        r"\bbest\b",
        r"\btop\b",
        r"\bmost\b",
        r"\bultimate\b",
    ],
    "numbers": [
        r"\b\d+\b",
    ],
}


def detect_hook_pattern(hook: str) -> Dict[str, any]:
    """
    Detect which pattern a hook follows.
    """
    hook_lower = hook.lower()
    matched_patterns = []
    
    for pattern_name, regexes in HOOK_PATTERNS.items():
        for regex in regexes:
            if re.search(regex, hook_lower):
                matched_patterns.append(pattern_name)
                break
    
    # Determine primary pattern
    primary = matched_patterns[0] if matched_patterns else "neutral"
    
    return {
        "patterns": matched_patterns,
        "primary": primary,
        "is_viral_style": len(matched_patterns) > 0,
    }


def score_hook_strength(hook: str) -> Dict[str, any]:
    """
    Score a hook's strength based on pattern and structure.
    """
    pattern = detect_hook_pattern(hook)
    words = hook.split()
    
    score = 0
    reasons = []
    
    # Pattern bonus
    if pattern["is_viral_style"]:
        score += 20
        reasons.append(f"matches viral pattern: {pattern['primary']}")
    
    # Length check (8-20 words optimal for short-form)
    if 8 <= len(words) <= 20:
        score += 15
        reasons.append("optimal length")
    elif len(words) < 8:
        score += 5
        reasons.append("short but punchy")
    elif len(words) > 30:
        score -= 10
        reasons.append("too long for short-form")
    
    # Punctuation energy
    if "?" in hook:
        score += 10
        reasons.append("question creates curiosity")
    if "!" in hook:
        score += 5
        reasons.append("exclamation adds energy")
    if "..." in hook:
        score += 10
        reasons.append("ellipsis creates anticipation")
    
    # First-word power words
    first_words = ["this", "here", "how", "why", "what", "stop", "wait"]
    if words and words[0].lower() in first_words:
        score += 10
        reasons.append("strong first word")
    
    return {
        "score": min(score, 100),
        "pattern": pattern,
        "reasons": reasons,
        "word_count": len(words),
    }


def generate_hook_variants(topic: str, count: int = 5) -> List[str]:
    """
    Generate hook variants for a topic using pattern templates.
    """
    templates = [
        f"Everyone thinks they know about {topic}. They're wrong.",
        f"How {topic} actually works (nobody explains this).",
        f"This is the biggest mistake people make with {topic}.",
        f"Nobody talks about the truth regarding {topic}.",
        f"I tried {topic} for 30 days. Here's what happened.",
        f"Why {topic} matters more than you think.",
        f"The secret about {topic} nobody tells you.",
        f"Stop doing {topic} the old way. Do this instead.",
        f"What nobody tells you about {topic}.",
        f"Best {topic} strategy I've ever used.",
    ]
    
    return templates[:count]