from typing import List, Dict, Optional


def generate_script_variants(
    hook: str,
    style_type: str = "short_form",
    count: int = 3
) -> List[Dict[str, str]]:
    """
    Generate script variants based on a hook.
    This is a stub - full implementation would use LLM.
    """
    scripts = []
    
    if style_type == "short_form":
        templates = [
            {
                "variant": "direct",
                "script": f"{hook} Here's the breakdown.",
            },
            {
                "variant": "engagement",
                "script": f"{hook} 👇 What do you think?",
            },
            {
                "variant": "viral",
                "script": f"{hook} — nobody talks about this.",
            },
        ]
        scripts = templates[:count]
    
    return scripts


def build_script_from_template(
    hook: str,
    template: str = "hook_lead"
) -> str:
    """
    Build a script from a template pattern.
    """
    templates = {
        "hook_lead": f"{hook} Here's what you need to know.",
        "question_lead": f"{hook} Let me explain.",
        "controversy_lead": f"{hook} Here's why that's wrong.",
        "story_lead": f"{hook} Here's what happened.",
    }
    
    return templates.get(template, templates["hook_lead"])


def estimate_script_duration(script: str, words_per_second: float = 2.5) -> int:
    """
    Estimate script duration in seconds.
    """
    word_count = len(script.split())
    return int(word_count / words_per_second)


def format_script_for_caption(script: str, max_chars_per_line: int = 30) -> List[str]:
    """
    Format script for burned-in captions.
    """
    words = script.split()
    lines = []
    current_line = []
    
    for word in words:
        current_line.append(word)
        if len(" ".join(current_line)) > max_chars_per_line:
            lines.append(" ".join(current_line[:-1]))
            current_line = [word]
    
    if current_line:
        lines.append(" ".join(current_line))
    
    return lines