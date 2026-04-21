from typing import Dict


def generate_caption_variants(hook: str) -> Dict[str, str]:
    """
    Generate multiple caption variants for a hook.
    """
    base = hook.strip()

    return {
        "short": base,
        "engagement": f"{base} 👇 What do you think?",
        "viral": f"{base} — nobody talks about this.",
        "authority": f"{base}. Here's the breakdown.",
    }


def build_burned_caption(hook: str) -> str:
    """
    Build a burned-in caption optimized for mobile readability.
    Chunks text into 2-4 word lines for short-form.
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

    return "\n".join(lines[:4])  # limit lines for short-form