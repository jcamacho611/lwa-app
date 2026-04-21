def generate_thumbnail_text(title: str, hook: str) -> str:
    """
    Generate thumbnail text from title/hook - keep it short + punchy.
    """
    text = hook or title

    words = text.upper().split()

    # Keep thumbnail short + punchy (max 4 words)
    return " ".join(words[:4])