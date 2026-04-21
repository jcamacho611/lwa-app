def infer_packaging_angle(title: str = "", hook: str = "") -> str:
    """
    Infer the packaging angle for a clip based on title and hook.
    """
    text = f"{title} {hook}".lower()

    # Controversy/contrarian angle
    if any(word in text for word in ["wrong", "mistake", "nobody", "never", "stop"]):
        return "controversy"

    # Curiosity/educational angle
    if any(word in text for word in ["how", "why", "exact", "secret", "this"]):
        return "curiosity"

    # Story narrative angle
    if any(word in text for word in ["story", "happened", "then", "finally"]):
        return "story"

    # Authority/best-of angle
    if any(word in text for word in ["best", "top", "fastest", "most", "ultimate"]):
        return "authority"

    return "insight"