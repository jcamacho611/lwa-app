"""
Intelligence Service — Phase 1
Provides content category definitions, emotional trigger library, hook library,
clip scoring helpers, category/trigger matching, hook selection, and packaging
angle intelligence.
"""
from __future__ import annotations

import re
from typing import Optional


# ---------------------------------------------------------------------------
# Content Category Definitions (15 types)
# ---------------------------------------------------------------------------

CONTENT_CATEGORIES: dict[str, dict] = {
    "educational_value": {
        "label": "Educational / Value",
        "description": "Teaches something actionable or explains a concept clearly.",
        "keywords": (
            "how to", "tutorial", "learn", "explain", "guide", "tip", "trick",
            "lesson", "teach", "understand", "breakdown", "step by step", "walkthrough",
        ),
        "primary_triggers": ("curiosity", "inspiration"),
        "best_platforms": ("YouTube Shorts", "TikTok"),
        "packaging_angle": "value",
    },
    "reaction_commentary": {
        "label": "Reaction / Commentary",
        "description": "Creator reacts to or comments on existing content or events.",
        "keywords": (
            "reaction", "react", "commentary", "podcast", "interview", "stream",
            "review", "breakdown", "respond", "watching", "thoughts on",
        ),
        "primary_triggers": ("humor", "curiosity", "shock"),
        "best_platforms": ("YouTube Shorts", "TikTok"),
        "packaging_angle": "curiosity",
    },
    "shock_reveal": {
        "label": "Shock / Reveal",
        "description": "Delivers a surprising twist, secret, or unexpected reveal.",
        "keywords": (
            "shocking", "shock", "reveal", "twist", "secret", "plot twist",
            "crazy", "wait for it", "you won't believe", "insane", "unbelievable",
        ),
        "primary_triggers": ("shock", "urgency", "curiosity"),
        "best_platforms": ("TikTok", "Instagram Reels"),
        "packaging_angle": "shock",
    },
    "meme_quotecore": {
        "label": "Meme / Quote-core",
        "description": "Punchy one-liners, relatable quotes, or meme-format content.",
        "keywords": (
            "meme", "quote", "funny", "joke", "one-liner", "insane line",
            "caption this", "relatable", "lol", "lmao", "fr fr",
        ),
        "primary_triggers": ("humor", "relatability"),
        "best_platforms": ("TikTok", "Instagram Reels"),
        "packaging_angle": "curiosity",
    },
    "story_payoff": {
        "label": "Story Payoff",
        "description": "Narrative arc with a satisfying conclusion or turning point.",
        "keywords": (
            "story", "happened", "moment", "ending", "then", "finally",
            "payoff", "turned out", "realized", "started", "when i", "the day",
        ),
        "primary_triggers": ("inspiration", "relatability", "curiosity"),
        "best_platforms": ("YouTube Shorts", "TikTok"),
        "packaging_angle": "story",
    },
    "animal_absurdity": {
        "label": "Animal / Absurdity",
        "description": "Animals, chaotic moments, or pure absurdist humor.",
        "keywords": (
            "dog", "cat", "animal", "pet", "absurd", "weird", "chaos",
            "wild animal", "bird", "fish", "hamster", "random", "unexpected",
        ),
        "primary_triggers": ("humor", "shock"),
        "best_platforms": ("TikTok", "Instagram Reels"),
        "packaging_angle": "shock",
    },
    "polished_lifestyle": {
        "label": "Polished Lifestyle",
        "description": "Aesthetic, aspirational, or beauty/fashion/travel content.",
        "keywords": (
            "beauty", "fashion", "outfit", "routine", "travel", "aesthetic",
            "morning routine", "fit check", "vlog", "day in my life", "grwm",
            "get ready", "lifestyle", "luxury",
        ),
        "primary_triggers": ("inspiration", "relatability"),
        "best_platforms": ("Instagram Reels", "TikTok"),
        "packaging_angle": "value",
    },
    "controversy_debate": {
        "label": "Controversy / Debate",
        "description": "Contrarian takes, hot opinions, or debate-worthy claims.",
        "keywords": (
            "wrong", "never", "nobody", "myth", "mistake", "unpopular opinion",
            "hot take", "disagree", "controversial", "debate", "actually",
            "everyone is wrong", "stop doing",
        ),
        "primary_triggers": ("urgency", "shock", "curiosity"),
        "best_platforms": ("TikTok", "YouTube Shorts"),
        "packaging_angle": "controversy",
    },
    "tutorial_howto": {
        "label": "Tutorial / How-To",
        "description": "Step-by-step instructions or demonstrations.",
        "keywords": (
            "step", "steps", "how i", "here's how", "do this", "try this",
            "method", "process", "technique", "formula", "system", "framework",
        ),
        "primary_triggers": ("curiosity", "inspiration"),
        "best_platforms": ("YouTube Shorts", "TikTok"),
        "packaging_angle": "value",
    },
    "motivational_inspiration": {
        "label": "Motivational / Inspiration",
        "description": "Uplifting, motivational, or mindset-shifting content.",
        "keywords": (
            "motivat", "inspire", "mindset", "believe", "achieve", "success",
            "grind", "hustle", "dream", "goal", "potential", "overcome",
            "never give up", "keep going",
        ),
        "primary_triggers": ("inspiration", "relatability"),
        "best_platforms": ("Instagram Reels", "YouTube Shorts"),
        "packaging_angle": "story",
    },
    "gaming_esports": {
        "label": "Gaming / Esports",
        "description": "Gameplay highlights, gaming commentary, or esports moments.",
        "keywords": (
            "game", "gaming", "gameplay", "clip", "highlight", "esport",
            "streamer", "twitch", "speedrun", "glitch", "boss", "level",
            "ranked", "clutch", "play",
        ),
        "primary_triggers": ("shock", "humor", "curiosity"),
        "best_platforms": ("TikTok", "YouTube Shorts"),
        "packaging_angle": "shock",
    },
    "finance_business": {
        "label": "Finance / Business",
        "description": "Money, investing, entrepreneurship, or business strategy.",
        "keywords": (
            "money", "invest", "stock", "crypto", "business", "entrepreneur",
            "income", "revenue", "profit", "wealth", "financial", "budget",
            "side hustle", "passive income",
        ),
        "primary_triggers": ("urgency", "curiosity", "inspiration"),
        "best_platforms": ("YouTube Shorts", "TikTok"),
        "packaging_angle": "value",
    },
    "fitness_health": {
        "label": "Fitness / Health",
        "description": "Workout, nutrition, wellness, or health transformation content.",
        "keywords": (
            "workout", "fitness", "gym", "exercise", "diet", "nutrition",
            "health", "weight", "muscle", "cardio", "protein", "calories",
            "transformation", "body",
        ),
        "primary_triggers": ("inspiration", "curiosity"),
        "best_platforms": ("Instagram Reels", "TikTok"),
        "packaging_angle": "value",
    },
    "news_current_events": {
        "label": "News / Current Events",
        "description": "Breaking news, trending topics, or current event commentary.",
        "keywords": (
            "news", "breaking", "update", "latest", "today", "just happened",
            "trending", "viral", "everyone is talking", "current", "2024", "2025",
        ),
        "primary_triggers": ("urgency", "shock", "curiosity"),
        "best_platforms": ("TikTok", "YouTube Shorts"),
        "packaging_angle": "curiosity",
    },
    "anime_fandom": {
        "label": "Anime / Fandom Edit",
        "description": "Anime clips, fandom edits, or character-driven content.",
        "keywords": (
            "anime", "manga", "amv", "fandom", "arc", "character", "episode",
            "edit", "op", "opening", "scene", "fight scene", "waifu", "isekai",
        ),
        "primary_triggers": ("curiosity", "inspiration", "relatability"),
        "best_platforms": ("TikTok", "Instagram Reels"),
        "packaging_angle": "story",
    },
}


# ---------------------------------------------------------------------------
# Emotional Trigger Library
# ---------------------------------------------------------------------------

EMOTIONAL_TRIGGERS: dict[str, dict] = {
    "urgency": {
        "label": "Urgency",
        "description": "Creates a sense of time pressure or FOMO.",
        "keywords": (
            "now", "today", "before it's too late", "don't miss", "limited",
            "hurry", "fast", "quick", "immediately", "right now", "asap",
            "deadline", "expires", "last chance",
        ),
        "hook_prefix_templates": [
            "Stop what you're doing — {focus} is happening right now.",
            "You have {timeframe} to act on {focus} before it's gone.",
            "This {focus} window is closing faster than most people realize.",
        ],
    },
    "curiosity": {
        "label": "Curiosity",
        "description": "Opens a loop the viewer needs to close.",
        "keywords": (
            "why", "how", "secret", "nobody knows", "most people don't",
            "the real reason", "what actually", "here's what", "turns out",
            "you didn't know", "hidden", "behind the scenes",
        ),
        "hook_prefix_templates": [
            "Here's the {focus} secret most creators never figure out.",
            "Why {focus} works differently than everyone thinks.",
            "The real reason {focus} keeps outperforming everything else.",
        ],
    },
    "humor": {
        "label": "Humor",
        "description": "Triggers laughter, surprise, or comedic recognition.",
        "keywords": (
            "funny", "lol", "hilarious", "joke", "comedy", "absurd",
            "ridiculous", "chaotic", "unhinged", "wild", "insane", "wtf",
        ),
        "hook_prefix_templates": [
            "Nobody prepared me for how {focus} actually goes.",
            "The {focus} moment that broke the internet for good reason.",
            "This {focus} clip is the most chaotic thing you'll see today.",
        ],
    },
    "inspiration": {
        "label": "Inspiration",
        "description": "Motivates action or shifts perspective positively.",
        "keywords": (
            "inspire", "motivate", "achieve", "possible", "believe", "transform",
            "change", "growth", "level up", "potential", "breakthrough", "proof",
        ),
        "hook_prefix_templates": [
            "This {focus} moment is proof that the shift is real.",
            "If you're still sleeping on {focus}, this clip will wake you up.",
            "The {focus} turning point that changes how you see this.",
        ],
    },
    "shock": {
        "label": "Shock",
        "description": "Delivers an unexpected or jaw-dropping moment.",
        "keywords": (
            "shocking", "unbelievable", "can't believe", "jaw drop", "plot twist",
            "wait what", "no way", "impossible", "crazy", "insane", "wild",
        ),
        "hook_prefix_templates": [
            "Nobody saw the {focus} twist coming — and that's the point.",
            "The {focus} reveal that stopped everyone mid-scroll.",
            "Wait until you see what happens with {focus}.",
        ],
    },
    "relatability": {
        "label": "Relatability",
        "description": "Makes the viewer feel seen or understood.",
        "keywords": (
            "everyone", "we all", "you know when", "that feeling", "same",
            "relatable", "literally me", "pov", "when you", "if you",
        ),
        "hook_prefix_templates": [
            "Every creator who's dealt with {focus} will feel this one.",
            "If you've ever struggled with {focus}, this clip is for you.",
            "The {focus} moment that every single person in this space has lived.",
        ],
    },
    "controversy": {
        "label": "Controversy",
        "description": "Challenges assumptions or invites strong disagreement.",
        "keywords": (
            "wrong", "unpopular", "hot take", "disagree", "actually", "myth",
            "stop", "never", "nobody talks about", "the truth about",
        ),
        "hook_prefix_templates": [
            "Most people are completely wrong about {focus} — here's why.",
            "The {focus} take nobody wants to say out loud.",
            "Stop doing {focus} the way everyone tells you to.",
        ],
    },
    "nostalgia": {
        "label": "Nostalgia",
        "description": "Evokes fond memories or a longing for the past.",
        "keywords": (
            "remember when", "back in", "throwback", "old school", "classic",
            "used to", "nostalgia", "childhood", "miss", "those days",
        ),
        "hook_prefix_templates": [
            "Remember when {focus} actually worked like this?",
            "This {focus} throwback hits different now.",
            "The {focus} era that shaped everything we do today.",
        ],
    },
}


# ---------------------------------------------------------------------------
# Hook Library — category × trigger → hook templates
# ---------------------------------------------------------------------------

HOOK_LIBRARY: dict[tuple[str, str], list[str]] = {
    ("educational_value", "curiosity"): [
        "Here's the {focus} framework most people skip entirely.",
        "The {focus} method that actually works — and why nobody teaches it.",
        "Stop guessing. Here's exactly how {focus} works.",
    ],
    ("educational_value", "inspiration"): [
        "This {focus} breakdown will change how you approach everything.",
        "Once you understand {focus} this way, you can't unsee it.",
        "The {focus} insight that separates the top 1% from everyone else.",
    ],
    ("reaction_commentary", "humor"): [
        "I watched {focus} so you don't have to — and it was a lot.",
        "My honest reaction to {focus} is not what anyone expected.",
        "The {focus} moment that made me stop the video and rewatch it.",
    ],
    ("reaction_commentary", "curiosity"): [
        "Here's what nobody is saying about {focus}.",
        "My take on {focus} after watching it three times.",
        "The {focus} detail everyone missed in the first watch.",
    ],
    ("shock_reveal", "shock"): [
        "Nobody saw the {focus} twist coming.",
        "The {focus} reveal that broke the comment section.",
        "Wait until you see what {focus} actually means.",
    ],
    ("shock_reveal", "urgency"): [
        "The {focus} reveal you need to see before it gets taken down.",
        "This {focus} moment is spreading fast — watch it now.",
        "Stop scrolling. The {focus} reveal is right here.",
    ],
    ("meme_quotecore", "humor"): [
        "The {focus} line that lives rent-free in my head.",
        "This {focus} quote is the most accurate thing I've ever heard.",
        "One sentence about {focus} that explains everything.",
    ],
    ("meme_quotecore", "relatability"): [
        "Every creator who's dealt with {focus} will feel this.",
        "The {focus} moment that is literally all of us.",
        "If you've ever experienced {focus}, this one's for you.",
    ],
    ("story_payoff", "inspiration"): [
        "This is the {focus} moment that changed everything.",
        "The {focus} turning point most people never reach.",
        "Here's exactly when {focus} started working.",
    ],
    ("story_payoff", "curiosity"): [
        "The {focus} story nobody tells you about.",
        "Here's what actually happened with {focus}.",
        "The {focus} moment that made everything click.",
    ],
    ("controversy_debate", "controversy"): [
        "Most people are completely wrong about {focus}.",
        "The {focus} take nobody wants to say out loud.",
        "Stop doing {focus} the way everyone tells you to.",
    ],
    ("controversy_debate", "shock"): [
        "The {focus} truth that will make some people very uncomfortable.",
        "Nobody talks about the {focus} problem — until now.",
        "The {focus} reality that breaks the popular narrative.",
    ],
    ("motivational_inspiration", "inspiration"): [
        "This {focus} proof will make you rethink what's possible.",
        "The {focus} shift that separates people who make it from those who don't.",
        "If you're still sleeping on {focus}, this clip will wake you up.",
    ],
    ("finance_business", "urgency"): [
        "The {focus} window is closing faster than most people realize.",
        "Stop waiting on {focus} — the early movers are already ahead.",
        "This {focus} opportunity won't look the same in six months.",
    ],
    ("finance_business", "curiosity"): [
        "Here's the {focus} move most people overlook entirely.",
        "The {focus} strategy that actually compounds over time.",
        "Why {focus} works differently than every finance creator tells you.",
    ],
    ("fitness_health", "inspiration"): [
        "The {focus} shift that makes everything else easier.",
        "This {focus} approach is the one that actually sticks.",
        "Here's what {focus} looks like when it's actually working.",
    ],
    ("gaming_esports", "shock"): [
        "The {focus} play that nobody thought was possible.",
        "This {focus} clip broke the meta and nobody noticed.",
        "The {focus} moment that changed how everyone plays this.",
    ],
    ("news_current_events", "urgency"): [
        "The {focus} update you need to know about right now.",
        "Here's what's actually happening with {focus} today.",
        "The {focus} development that changes everything going forward.",
    ],
    ("anime_fandom", "curiosity"): [
        "The {focus} detail that most people completely missed.",
        "Here's what the {focus} scene actually means.",
        "The {focus} moment that recontextualizes the entire arc.",
    ],
}

# Fallback hooks for any category/trigger combination not in the library
_FALLBACK_HOOKS: list[str] = [
    "The {focus} angle most creators are still sleeping on.",
    "Here's why {focus} is the highest-upside move right now.",
    "If you post one clip about {focus}, make it this one.",
]


# ---------------------------------------------------------------------------
# Category Detection
# ---------------------------------------------------------------------------

def detect_content_category(
    *,
    title: str = "",
    description: str = "",
    transcript: str = "",
    visual_summary: str = "",
    source_platform: str = "",
    selected_trend: str = "",
    content_angle: str = "",
) -> tuple[str, float]:
    """
    Returns (category_key, confidence) for the best-matching content category.
    Confidence is a float between 0.0 and 1.0.
    """
    combined = " ".join(
        part
        for part in [title, description, transcript[:800], visual_summary, source_platform, selected_trend, content_angle]
        if part
    ).lower()
    combined = re.sub(r"\s+", " ", combined)

    scored: list[tuple[str, int]] = []
    for key, category in CONTENT_CATEGORIES.items():
        hits = sum(1 for kw in category["keywords"] if kw in combined)
        scored.append((key, hits))

    best_key, best_hits = max(scored, key=lambda item: item[1], default=("educational_value", 0))

    if best_hits == 0:
        # Platform-based fallback
        platform_lower = source_platform.lower()
        if platform_lower in {"youtube", "twitch"}:
            return "reaction_commentary", 0.45
        if platform_lower == "instagram":
            return "polished_lifestyle", 0.45
        return "educational_value", 0.40

    # Confidence scales with keyword density
    total_keywords = len(CONTENT_CATEGORIES[best_key]["keywords"])
    confidence = min(0.45 + (best_hits / max(total_keywords, 1)) * 0.55, 0.97)
    return best_key, round(confidence, 3)


# ---------------------------------------------------------------------------
# Emotional Trigger Detection
# ---------------------------------------------------------------------------

def detect_emotional_triggers(
    *,
    title: str = "",
    hook: str = "",
    caption: str = "",
    transcript_excerpt: str = "",
    packaging_angle: str = "",
) -> list[str]:
    """
    Returns a list of detected emotional trigger keys (up to 3), ordered by strength.
    """
    combined = " ".join(
        part for part in [title, hook, caption, transcript_excerpt] if part
    ).lower()

    # Angle-to-trigger mapping for fast path
    angle_trigger_map: dict[str, str] = {
        "shock": "shock",
        "story": "inspiration",
        "curiosity": "curiosity",
        "controversy": "controversy",
        "value": "curiosity",
    }

    scored: list[tuple[str, int]] = []
    for key, trigger in EMOTIONAL_TRIGGERS.items():
        hits = sum(1 for kw in trigger["keywords"] if kw in combined)
        # Boost the trigger that matches the packaging angle
        if key == angle_trigger_map.get(packaging_angle, ""):
            hits += 3
        scored.append((key, hits))

    scored.sort(key=lambda item: -item[1])
    # Return top 3 triggers that have at least 1 hit, or top 1 from angle map
    result = [key for key, hits in scored if hits > 0][:3]
    if not result:
        fallback = angle_trigger_map.get(packaging_angle, "curiosity")
        result = [fallback]
    return result


# ---------------------------------------------------------------------------
# Hook Selection
# ---------------------------------------------------------------------------

def select_best_hooks(
    *,
    category_key: str,
    triggers: list[str],
    focus: str,
    count: int = 3,
) -> list[str]:
    """
    Returns `count` hook strings selected from the hook library based on
    category and trigger match, with focus substituted in.
    """
    collected: list[str] = []

    for trigger in triggers:
        key = (category_key, trigger)
        templates = HOOK_LIBRARY.get(key, [])
        for template in templates:
            hook = template.replace("{focus}", focus)
            if hook not in collected:
                collected.append(hook)
        if len(collected) >= count:
            break

    # Fill remaining slots from fallback
    if len(collected) < count:
        for template in _FALLBACK_HOOKS:
            hook = template.replace("{focus}", focus)
            if hook not in collected:
                collected.append(hook)
            if len(collected) >= count:
                break

    return collected[:count]


# ---------------------------------------------------------------------------
# Packaging Angle Intelligence
# ---------------------------------------------------------------------------

def build_packaging_intelligence(
    *,
    category_key: str,
    triggers: list[str],
    packaging_angle: str,
    target_platform: str,
    confidence: float,
) -> dict:
    """
    Returns a packaging_intelligence dict with angle, confidence, and reasoning.
    """
    category = CONTENT_CATEGORIES.get(category_key, CONTENT_CATEGORIES["educational_value"])
    primary_trigger = triggers[0] if triggers else "curiosity"
    trigger_info = EMOTIONAL_TRIGGERS.get(primary_trigger, EMOTIONAL_TRIGGERS["curiosity"])

    # Determine if the packaging angle aligns with the category's preferred angle
    preferred_angle = category.get("packaging_angle", "value")
    angle_match = packaging_angle == preferred_angle
    angle_confidence = min(confidence + (0.08 if angle_match else -0.05), 0.97)

    reasoning = (
        f"This clip reads as {category['label'].lower()} content with a strong "
        f"{trigger_info['label'].lower()} signal. "
        f"The {packaging_angle} packaging angle "
        + ("aligns well" if angle_match else "diverges slightly")
        + f" with the category's natural fit for {target_platform}."
    )

    return {
        "angle": packaging_angle,
        "category": category["label"],
        "primary_trigger": trigger_info["label"],
        "confidence": round(angle_confidence, 3),
        "reasoning": reasoning,
        "best_platforms": list(category.get("best_platforms", [target_platform])),
        "angle_match": angle_match,
    }


# ---------------------------------------------------------------------------
# Why-This-Matters Generation
# ---------------------------------------------------------------------------

def generate_why_this_matters(
    *,
    category_key: str,
    triggers: list[str],
    packaging_angle: str,
    target_platform: str,
    post_rank: int,
    focus: str,
) -> str:
    """
    Generates a specific, intelligence-driven why_this_matters explanation.
    """
    category = CONTENT_CATEGORIES.get(category_key, CONTENT_CATEGORIES["educational_value"])
    primary_trigger = triggers[0] if triggers else "curiosity"
    trigger_info = EMOTIONAL_TRIGGERS.get(primary_trigger, EMOTIONAL_TRIGGERS["curiosity"])
    category_label = category["label"].lower()
    trigger_label = trigger_info["label"].lower()

    if post_rank == 1:
        return (
            f"Open with this because the {focus} moment delivers a clear {trigger_label} signal "
            f"that {target_platform} viewers respond to immediately — "
            f"the {category_label} framing earns the first impression fast."
        )
    if post_rank == 2:
        return (
            f"Use this second because the {packaging_angle} angle deepens the {category_label} "
            f"narrative after the opener has already earned attention, "
            f"keeping the {target_platform} stack coherent and the {trigger_label} loop open."
        )
    return (
        f"Hold this for later in the stack — the {focus} payoff lands harder once viewers "
        f"already understand the {category_label} context, "
        f"and the {trigger_label} close converts attention into action on {target_platform}."
    )


# ---------------------------------------------------------------------------
# Clip Scoring Helpers
# ---------------------------------------------------------------------------

def score_clip_with_intelligence(
    *,
    base_score: int,
    category_key: str,
    triggers: list[str],
    has_transcript: bool,
    duration_seconds: int | None,
    packaging_angle: str,
    target_platform: str,
) -> tuple[int, float]:
    """
    Returns (enriched_score, confidence) using intelligence signals.
    """
    category = CONTENT_CATEGORIES.get(category_key, CONTENT_CATEGORIES["educational_value"])
    preferred_angle = category.get("packaging_angle", "value")

    # Trigger strength bonus (more triggers = stronger signal)
    trigger_bonus = min(len(triggers) * 3, 9)

    # Angle alignment bonus
    angle_bonus = 5 if packaging_angle == preferred_angle else 0

    # Platform fit bonus
    platform_bonus = 4 if target_platform in category.get("best_platforms", []) else 0

    # Transcript bonus
    transcript_bonus = 6 if has_transcript else 0

    # Duration sweet spot bonus (15–45 seconds is ideal for short-form)
    duration_bonus = 0
    if duration_seconds is not None:
        if 15 <= duration_seconds <= 45:
            duration_bonus = 5
        elif 10 <= duration_seconds <= 60:
            duration_bonus = 3

    enriched = min(
        max(base_score + trigger_bonus + angle_bonus + platform_bonus + transcript_bonus + duration_bonus, base_score),
        99,
    )
    confidence = min(
        max(0.45, (enriched / 100.0) + (0.04 if has_transcript else 0.0)),
        0.97,
    )
    return enriched, round(confidence, 3)


# ---------------------------------------------------------------------------
# Caption Style Intelligence
# ---------------------------------------------------------------------------

def caption_style_from_intelligence(
    *,
    category_key: str,
    primary_trigger: str,
    target_platform: str,
    packaging_angle: str,
) -> str:
    """
    Returns a specific caption style string based on intelligence signals.
    """
    # Trigger-first mapping
    trigger_styles: dict[str, str] = {
        "urgency": "Urgency-driven interrupt",
        "curiosity": "Question-led teaser",
        "humor": "Punchy comedic hook",
        "inspiration": "Aspirational payoff",
        "shock": "Punchy interrupt",
        "relatability": "Empathy-first opener",
        "controversy": "Tension-led contrarian",
        "nostalgia": "Throwback emotional",
    }

    # Packaging angle override
    angle_styles: dict[str, str] = {
        "controversy": "Tension-led contrarian",
        "story": "Beat-driven narrative",
        "curiosity": "Question-led teaser",
        "shock": "Punchy interrupt",
    }

    if packaging_angle in angle_styles:
        return angle_styles[packaging_angle]

    if primary_trigger in trigger_styles:
        return trigger_styles[primary_trigger]

    # Platform fallback
    platform_lower = target_platform.lower()
    if "tiktok" in platform_lower:
        return "Punchy proof-first"
    if "instagram" in platform_lower or "reels" in platform_lower:
        return "Polished emotional"
    if "youtube" in platform_lower or "shorts" in platform_lower:
        return "Clarity-led payoff"
    return "Short-form native"


# ---------------------------------------------------------------------------
# Platform Fit Intelligence
# ---------------------------------------------------------------------------

def platform_fit_from_intelligence(
    *,
    category_key: str,
    triggers: list[str],
    target_platform: str,
    packaging_angle: str,
) -> str:
    """
    Returns a specific platform_fit string based on intelligence signals.
    """
    category = CONTENT_CATEGORIES.get(category_key, CONTENT_CATEGORIES["educational_value"])
    category_label = category["label"].lower()
    primary_trigger = triggers[0] if triggers else "curiosity"
    trigger_label = EMOTIONAL_TRIGGERS.get(primary_trigger, {}).get("label", "curiosity").lower()
    platform_lower = target_platform.lower()

    if "tiktok" in platform_lower:
        return (
            f"TikTok-ready {category_label} content with a {trigger_label} hook "
            f"and {packaging_angle} pacing built for fast cold-open retention."
        )
    if "instagram" in platform_lower or "reels" in platform_lower:
        return (
            f"Reels-optimized {category_label} framing with a {trigger_label} signal "
            f"and polished {packaging_angle} packaging for visual-first audiences."
        )
    if "youtube" in platform_lower or "shorts" in platform_lower:
        return (
            f"Shorts-native {category_label} structure with a {trigger_label} opener "
            f"and context-light {packaging_angle} setup for payoff-first clipping."
        )
    return (
        f"{target_platform} packaging built around {category_label} content "
        f"with a {trigger_label} signal and {packaging_angle} angle."
    )


# ---------------------------------------------------------------------------
# Enrich Clip with Intelligence
# ---------------------------------------------------------------------------

def enrich_clip_with_intelligence(
    *,
    clip_id: str,
    title: str,
    hook: str,
    caption: str,
    transcript_excerpt: str | None,
    packaging_angle: str,
    target_platform: str,
    post_rank: int,
    base_score: int,
    base_confidence: float,
    source_title: str = "",
    source_description: str = "",
    source_transcript: str = "",
    source_platform: str = "",
    selected_trend: str = "",
    content_angle: str = "",
    start_time: str | None = None,
    end_time: str | None = None,
) -> dict:
    """
    Master enrichment function. Returns a dict of intelligence-enriched fields
    suitable for use in clip.model_copy(update=...).
    """
    # Detect category
    category_key, category_confidence = detect_content_category(
        title=title,
        description=source_description,
        transcript=source_transcript or transcript_excerpt or "",
        source_platform=source_platform,
        selected_trend=selected_trend,
        content_angle=content_angle,
    )

    # Detect triggers
    triggers = detect_emotional_triggers(
        title=title,
        hook=hook,
        caption=caption,
        transcript_excerpt=transcript_excerpt or "",
        packaging_angle=packaging_angle,
    )

    # Compute duration (inline to avoid circular import with clip_service)
    duration_seconds = _parse_duration(start_time, end_time)

    # Score with intelligence
    enriched_score, enriched_confidence = score_clip_with_intelligence(
        base_score=base_score,
        category_key=category_key,
        triggers=triggers,
        has_transcript=bool(transcript_excerpt),
        duration_seconds=duration_seconds,
        packaging_angle=packaging_angle,
        target_platform=target_platform,
    )

    # Build focus phrase
    focus = _compact_focus(transcript_excerpt or title or hook)

    # Select hooks
    hook_variants = select_best_hooks(
        category_key=category_key,
        triggers=triggers,
        focus=focus,
        count=3,
    )

    # Build packaging intelligence
    packaging_intel = build_packaging_intelligence(
        category_key=category_key,
        triggers=triggers,
        packaging_angle=packaging_angle,
        target_platform=target_platform,
        confidence=enriched_confidence,
    )

    # Generate why_this_matters
    why_this_matters = generate_why_this_matters(
        category_key=category_key,
        triggers=triggers,
        packaging_angle=packaging_angle,
        target_platform=target_platform,
        post_rank=post_rank,
        focus=focus,
    )

    # Caption style
    primary_trigger = triggers[0] if triggers else "curiosity"
    caption_style = caption_style_from_intelligence(
        category_key=category_key,
        primary_trigger=primary_trigger,
        target_platform=target_platform,
        packaging_angle=packaging_angle,
    )

    # Platform fit
    platform_fit = platform_fit_from_intelligence(
        category_key=category_key,
        triggers=triggers,
        target_platform=target_platform,
        packaging_angle=packaging_angle,
    )

    return {
        "score": enriched_score,
        "virality_score": enriched_score,
        "confidence": enriched_confidence,
        "confidence_score": max(int(round(enriched_confidence * 100)), 55),
        "why_this_matters": why_this_matters,
        "hook_variants": hook_variants,
        "caption_style": caption_style,
        "platform_fit": platform_fit,
        "packaging_intelligence": packaging_intel,
        "emotional_triggers": triggers,
        "category": CONTENT_CATEGORIES.get(category_key, {}).get("label", "Educational / Value"),
    }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _compact_focus(value: str) -> str:
    words = re.findall(r"[A-Za-z0-9']+", value)
    return " ".join(words[:3]).lower() if words else "this clip"


def _parse_timestamp(value: str | None) -> int | None:
    if not value:
        return None
    try:
        parts = [int(float(part)) for part in value.split(":")]
    except Exception:
        return None
    if len(parts) == 2:
        minutes, seconds = parts
        return (minutes * 60) + seconds
    if len(parts) == 3:
        hours, minutes, seconds = parts
        return (hours * 3600) + (minutes * 60) + seconds
    return None


def _parse_duration(start_time: str | None, end_time: str | None) -> int | None:
    start = _parse_timestamp(start_time)
    end = _parse_timestamp(end_time)
    if start is None or end is None or end <= start:
        return None
    return max(int(end - start), 1)
