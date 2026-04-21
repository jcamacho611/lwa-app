def generate_cta(hook: str) -> str:
    """
    Generate a call-to-action based on hook content.
    """
    text = hook.lower()

    if "why" in text:
        return "Comment your take."
    if "how" in text:
        return "Save this."
    if "secret" in text:
        return "Share this."
    if "mistake" in text:
        return "Don't miss this."
    if "wrong" in text:
        return "Agree or disagree?"

    return "Follow for more."