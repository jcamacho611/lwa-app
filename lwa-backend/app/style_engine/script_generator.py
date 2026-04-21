from __future__ import annotations

from ..models.schemas import GeneratedScripts
from .diversity_engine import diversify_outputs
from .style_extractor import StyleProfile, extract_style
from .topic_expander import expand_topics


def build_script_pack(
    *,
    source_title: str | None,
    transcript: str | None,
    target_platform: str,
    clip_phrases: list[str],
) -> GeneratedScripts:
    source_text = " ".join(part for part in [transcript or "", " ".join(clip_phrases)] if part)
    style = extract_style(source_text)
    topics = expand_topics(source_title=source_title, transcript=transcript, clip_phrases=clip_phrases)
    primary_topic = first_topic(topics) or (source_title or "this idea")
    hooks = build_hooks(primary_topic=primary_topic, style=style)
    titles = build_titles(primary_topic=primary_topic, target_platform=target_platform, style=style)
    ctas = build_ctas(style=style)
    main = build_script(topic=primary_topic, hook=hooks[0], cta=ctas[0], style=style)
    variant_topics = (
        topics["stronger_angles"]
        + topics["emotional_variants"]
        + topics["adjacent_topics"]
        + topics["skill_levels"]
    )
    variants = [
        build_script(topic=topic, hook=hook, cta=cta, style=style)
        for topic, hook, cta in zip(variant_topics, hooks[1:] + hooks, ctas[1:] + ctas)
    ]

    return GeneratedScripts(
        main=main,
        variants=diversify_outputs(variants, limit=2),
        hooks=diversify_outputs(hooks, limit=3),
        titles=diversify_outputs(titles, limit=3),
        ctas=diversify_outputs(ctas, limit=2),
    )


def build_script(*, topic: str, hook: str, cta: str, style: StyleProfile) -> str:
    proof_line = "Here is the proof" if style.tone != "emotional" else "Here is why it hits"
    if style.structure_pattern == "question-answer-cta":
        middle = f"The answer is simple: {topic} only works when the setup gets cut fast and the payoff stays obvious."
    elif style.structure_pattern == "claim-proof-action":
        middle = f"{proof_line}: start with the strongest claim, show the result, then move straight to the action."
    else:
        middle = f"{proof_line}: {topic} has a clean setup, a fast turn, and a payoff people can repeat."
    return f"{hook} {middle} {cta}"


def build_hooks(*, primary_topic: str, style: StyleProfile) -> list[str]:
    if style.hook_style == "contrarian":
        return [
            f"Most people get {primary_topic} wrong.",
            f"The mistake with {primary_topic} is obvious once you see it.",
            f"Nobody frames {primary_topic} like this.",
        ]
    if style.hook_style == "interrupt":
        return [
            f"Stop scrolling. {primary_topic} is the part that matters.",
            f"This {primary_topic} moment changes the whole clip.",
            f"Watch this before you skip {primary_topic}.",
        ]
    if style.hook_style == "question":
        return [
            f"Why does {primary_topic} keep working?",
            f"What makes {primary_topic} hit so fast?",
            f"How would you explain {primary_topic} in one short?",
        ]
    return [
        f"Here is the fastest way to understand {primary_topic}.",
        f"This is the cleanest {primary_topic} angle.",
        f"If you post about {primary_topic}, start here.",
    ]


def build_titles(*, primary_topic: str, target_platform: str, style: StyleProfile) -> list[str]:
    platform = target_platform or "Shorts"
    return [
        f"{primary_topic.title()} In 30 Seconds",
        f"The {primary_topic.title()} Clip",
        f"{platform}: {style.tone.title()} Angle",
    ]


def build_ctas(*, style: StyleProfile) -> list[str]:
    if style.cta_style == "part-two":
        return ["Comment if you want part two.", "Follow for the next cut."]
    if style.cta_style == "save-share":
        return ["Save this before you forget it.", "Send this to someone building content."]
    return ["Comment which side you are on.", "Follow for the next breakdown."]


def first_topic(topics: dict[str, list[str]]) -> str | None:
    for values in topics.values():
        if values:
            return values[0]
    return None
