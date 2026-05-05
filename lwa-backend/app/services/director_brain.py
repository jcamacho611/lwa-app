from __future__ import annotations

from dataclasses import dataclass, field
import re

from ..models.schemas import ClipResult
from .proof_graph import ProofGraphManager, ProofAsset, ProofType


@dataclass(frozen=True)
class PlatformDirectorProfile:
    platform: str
    first_seconds: str
    primary_signal: str
    secondary_signal: str
    hook_instruction: str
    caption_instruction: str
    title_instruction: str
    cta_template: str
    fit_template: str


@dataclass(frozen=True)
class OpportunityInsight:
    purpose: str  # trust/sales/attention/authority/community
    audience_target: str  # who this content serves
    opportunity_type: str  # what this could lead to
    confidence: int  # how likely this creates the opportunity
    next_action: str  # what user should do with this
    risk_level: str  # low/medium/high


@dataclass(frozen=True)
class DirectorBrainPlan:
    platform: str
    category: str
    rendered_state: str
    hook_variants: list[str]
    caption: str
    thumbnail_text: str
    cta_suggestion: str
    packaging_angle: str
    platform_fit: str
    score: int
    confidence: int
    explanation: str
    opportunity_insight: OpportunityInsight | None = None
    proof_asset: ProofAsset | None = None
    platform_notes: list[str] = field(default_factory=list)

    def as_clip_update(self, clip: ClipResult) -> dict[str, object]:
        caption_variants = dict(clip.caption_variants or {})
        if self.caption and not caption_variants:
            caption_variants = {"director": self.caption}

        platform_notes = list(clip.platform_notes or [])
        for note in self.platform_notes:
            if note not in platform_notes:
                platform_notes.append(note)

        update_data = {
            "target_platform": clip.target_platform or self.platform,
            "platform_fit": clip.platform_fit or self.platform_fit,
            "thumbnail_text": clip.thumbnail_text or self.thumbnail_text,
            "cta_suggestion": clip.cta_suggestion or self.cta_suggestion,
            "packaging_angle": clip.packaging_angle or self.packaging_angle,
            "hook_variants": clip.hook_variants or self.hook_variants,
            "caption_variants": caption_variants,
            "platform_notes": platform_notes,
            "scoring_explanation": clip.scoring_explanation or self.explanation,
            "confidence_score": clip.confidence_score or self.confidence,
        }
        
        # Add opportunity insights if available
        if self.opportunity_insight:
            update_data.update({
                "opportunity_purpose": self.opportunity_insight.purpose,
                "opportunity_audience": self.opportunity_insight.audience_target,
                "opportunity_type": self.opportunity_insight.opportunity_type,
                "opportunity_confidence": self.opportunity_insight.confidence,
                "opportunity_next_action": self.opportunity_insight.next_action,
                "opportunity_risk": self.opportunity_insight.risk_level,
            })
        
        return update_data


PLATFORM_PROFILES: dict[str, PlatformDirectorProfile] = {
    "tiktok": PlatformDirectorProfile(
        platform="TikTok",
        first_seconds="1-3 seconds",
        primary_signal="completion and rewatch",
        secondary_signal="shares",
        hook_instruction="Start with a pattern interrupt or direct claim.",
        caption_instruction="Keep the caption short, persona-specific, and easy to remix.",
        title_instruction="Use a four-word overlay with the keyword visible.",
        cta_template="Test this hook first, then cut a tighter loop if retention drops.",
        fit_template="{category} works on TikTok when the first beat lands in {first_seconds} and the loop is obvious.",
    ),
    "instagram reels": PlatformDirectorProfile(
        platform="Instagram Reels",
        first_seconds="2 seconds",
        primary_signal="DM shares",
        secondary_signal="saves",
        hook_instruction="Open with a line someone would send to a specific friend.",
        caption_instruction="Build around send-to-a-friend behavior.",
        title_instruction="Use polished on-screen text that names the persona.",
        cta_template="Send this packaging to the persona most likely to share it.",
        fit_template="{category} fits Reels when the payoff feels shareable in the first {first_seconds}.",
    ),
    "reels": PlatformDirectorProfile(
        platform="Instagram Reels",
        first_seconds="2 seconds",
        primary_signal="DM shares",
        secondary_signal="saves",
        hook_instruction="Open with a line someone would send to a specific friend.",
        caption_instruction="Build around send-to-a-friend behavior.",
        title_instruction="Use polished on-screen text that names the persona.",
        cta_template="Send this packaging to the persona most likely to share it.",
        fit_template="{category} fits Reels when the payoff feels shareable in the first {first_seconds}.",
    ),
    "youtube shorts": PlatformDirectorProfile(
        platform="YouTube Shorts",
        first_seconds="1 second",
        primary_signal="engaged views",
        secondary_signal="swipe-away reduction",
        hook_instruction="Make the first frame the claim, not setup.",
        caption_instruction="Invite a comment without slowing the clip down.",
        title_instruction="Use search-readable words over clever phrasing.",
        cta_template="Make the ending loop back into the opening claim before publishing.",
        fit_template="{category} fits Shorts when the first frame explains why the viewer should not swipe.",
    ),
    "shorts": PlatformDirectorProfile(
        platform="YouTube Shorts",
        first_seconds="1 second",
        primary_signal="engaged views",
        secondary_signal="swipe-away reduction",
        hook_instruction="Make the first frame the claim, not setup.",
        caption_instruction="Invite a comment without slowing the clip down.",
        title_instruction="Use search-readable words over clever phrasing.",
        cta_template="Make the ending loop back into the opening claim before publishing.",
        fit_template="{category} fits Shorts when the first frame explains why the viewer should not swipe.",
    ),
    "linkedin": PlatformDirectorProfile(
        platform="LinkedIn",
        first_seconds="3 seconds",
        primary_signal="dwell and comment depth",
        secondary_signal="saves",
        hook_instruction="Open with a specific professional claim.",
        caption_instruction="Make the caption opinion-led and end with a question.",
        title_instruction="Use a headline-style overlay.",
        cta_template="Post from a personal profile and ask for one concrete counterpoint.",
        fit_template="{category} fits LinkedIn when the first {first_seconds} creates dwell and a useful debate.",
    ),
}

CATEGORY_KEYWORDS: dict[str, tuple[str, ...]] = {
    "podcast": ("podcast", "interview", "episode", "conversation", "host"),
    "gaming": ("game", "gaming", "stream", "twitch", "match", "ranked"),
    "finance": ("finance", "market", "fed", "stocks", "bitcoin", "crypto", "rate"),
    "coaching": ("coach", "framework", "lesson", "mistake", "mindset", "client"),
    "beauty": ("beauty", "skincare", "makeup", "routine", "aesthetic"),
    "medspa": ("medspa", "clinic", "treatment", "patient", "consultation"),
    "music": ("music", "song", "artist", "studio", "album", "beat"),
    "sports": ("sports", "game", "finals", "season", "player", "coach"),
    "education": ("education", "teach", "learn", "explain", "tutorial", "lesson"),
    "debate": ("debate", "argument", "wrong", "disagree", "controversial"),
    "reaction": ("reaction", "react", "commentary", "response", "breakdown"),
    "product_demo": ("demo", "product", "feature", "launch", "workflow"),
    "ai_tech": ("ai", "openai", "model", "software", "automation", "tech"),
    "local_business": ("local", "restaurant", "clinic", "service", "near me"),
}


def analyze_opportunity_potential(clip: ClipResult, *, category: str) -> OpportunityInsight:
    """Analyze clip for opportunity potential - the core of the Opportunity Engine."""
    text = " ".join(part for part in [clip.hook, clip.title, clip.caption, clip.reason] if part).lower()
    
    # Determine purpose
    purpose = classify_content_purpose(text, category)
    
    # Identify audience target
    audience = identify_audience_target(text, category)
    
    # Determine opportunity type
    opportunity = map_to_opportunity_type(purpose, audience, category)
    
    # Calculate confidence based on content signals
    confidence = calculate_opportunity_confidence(clip, purpose, audience, text)
    
    # Recommend next action
    action = recommend_next_action(purpose, opportunity, confidence)
    
    # Assess risk level
    risk = assess_content_risk(text, category)
    
    return OpportunityInsight(
        purpose=purpose,
        audience_target=audience,
        opportunity_type=opportunity,
        confidence=confidence,
        next_action=action,
        risk_level=risk
    )


def classify_content_purpose(text: str, category: str) -> str:
    """Classify the primary purpose of this content."""
    # Trust-building signals
    trust_signals = ["story", "behind the scenes", "my journey", "mistake", "failure", "learned", "experience", "testimonial", "proof", "result", "transformation"]
    
    # Sales signals
    sales_signals = ["buy", "sale", "offer", "discount", "price", "join", "sign up", "get started", "invest", "purchase", "order", "book now"]
    
    # Attention signals
    attention_signals = ["shocking", "unbelievable", "never seen", "secret", "revealed", "exposed", "controversial", "debate", "vs", "battle", "challenge"]
    
    # Authority signals
    authority_signals = ["expert", "research", "study", "data", "analysis", "framework", "method", "system", "strategy", "breakthrough", "innovation"]
    
    # Community signals
    community_signals = ["community", "together", "join us", "we", "our", "family", "team", "movement", "tribe", "belong", "connect"]
    
    signal_counts = {
        "trust": sum(1 for signal in trust_signals if signal in text),
        "sales": sum(1 for signal in sales_signals if signal in text),
        "attention": sum(1 for signal in attention_signals if signal in text),
        "authority": sum(1 for signal in authority_signals if signal in text),
        "community": sum(1 for signal in community_signals if signal in text)
    }
    
    # Category-based priors
    if category in ["coaching", "education"]:
        signal_counts["authority"] += 2
        signal_counts["trust"] += 1
    elif category in ["product_demo", "finance"]:
        signal_counts["sales"] += 2
        signal_counts["authority"] += 1
    elif category in ["debate", "reaction"]:
        signal_counts["attention"] += 2
    elif category in ["local_business", "beauty", "medspa"]:
        signal_counts["trust"] += 2
        signal_counts["sales"] += 1
    
    # Return the purpose with highest signal count
    return max(signal_counts, key=signal_counts.get)


def identify_audience_target(text: str, category: str) -> str:
    """Identify the primary audience this content serves."""
    audience_patterns = {
        "beginners": ["beginner", "newbie", "start", "getting started", "first time", "basics", "introduction"],
        "advanced practitioners": ["advanced", "expert", "pro", "master", "deep dive", "technical", "nuanced"],
        "business owners": ["business", "owner", "entrepreneur", "startup", "company", "revenue", "profit", "growth"],
        "creators": ["creator", "content", "audience", "engagement", "viral", "growth", "monetize"],
        "local customers": ["local", "near me", "area", "community", "neighborhood", "city", "town"],
        "investors": ["invest", "funding", "roi", "return", "venture", "capital", "startup", "scale"],
        "job seekers": ["career", "job", "hire", "resume", "interview", "professional", "skills"],
        "coaches/consultants": ["coach", "consultant", "client", "framework", "methodology", "transformation"],
        "general consumers": ["everyone", "anyone", "people", "you", "your", "general", "public"]
    }
    
    signal_counts = {}
    for audience, patterns in audience_patterns.items():
        signal_counts[audience] = sum(1 for pattern in patterns if pattern in text)
    
    # Category-based adjustments
    if category == "local_business":
        signal_counts["local customers"] += 3
    elif category == "coaching":
        signal_counts["coaches/consultants"] += 2
        signal_counts["beginners"] += 1
    elif category == "ai_tech":
        signal_counts["business owners"] += 2
        signal_counts["advanced practitioners"] += 1
    elif category == "education":
        signal_counts["beginners"] += 2
    
    return max(signal_counts, key=signal_counts.get) if signal_counts else "general consumers"


def map_to_opportunity_type(purpose: str, audience: str, category: str) -> str:
    """Map content purpose and audience to specific opportunity types."""
    opportunity_matrix = {
        ("trust", "beginners"): "onboarding lead",
        ("trust", "business owners"): "consulting discovery call",
        ("trust", "local customers"): "local business visit",
        ("trust", "creators"): "collaboration opportunity",
        ("sales", "general consumers"): "product sale",
        ("sales", "business owners"): "B2B contract",
        ("sales", "investors"): "investment opportunity",
        ("attention", "creators"): "viral growth",
        ("attention", "general consumers"): "brand awareness",
        ("authority", "advanced practitioners"): "thought leadership",
        ("authority", "business owners"): "expert consulting",
        ("authority", "job seekers"): "career opportunity",
        ("community", "creators"): "community building",
        ("community", "general consumers"): "tribe building"
    }
    
    key = (purpose, audience)
    return opportunity_matrix.get(key, "general engagement")


def calculate_opportunity_confidence(clip: ClipResult, purpose: str, audience: str, text: str) -> int:
    """Calculate confidence score for opportunity potential."""
    base_confidence = int(clip.confidence_score or clip.score or 50)
    
    # Boost confidence for clear purpose signals
    purpose_boost = 10 if any(word in text for word in [purpose, purpose.replace("_", " ")]) else 0
    
    # Boost confidence for strong hooks
    hook_strength = len(clip.hook or "") > 20 if clip.hook else 0
    hook_boost = 15 if hook_strength else 0
    
    # Boost confidence for clear CTA
    cta_boost = 10 if clip.cta_suggestion and len(clip.cta_suggestion) > 10 else 0
    
    # Boost confidence for rendered content
    render_boost = 20 if clip_has_rendered_media(clip) else 0
    
    # Adjust based on purpose-audience alignment
    alignment_bonus = 5  # Basic alignment for valid combinations
    
    total_confidence = base_confidence + purpose_boost + hook_boost + cta_boost + render_boost + alignment_bonus
    
    return max(30, min(95, total_confidence))


def recommend_next_action(purpose: str, opportunity: str, confidence: int) -> str:
    """Recommend the best next action for this content."""
    if confidence < 50:
        return "Refine content to strengthen opportunity signals"
    
    actions = {
        "trust": "Use this to build relationship before asking for sale",
        "sales": "Direct interested prospects to your offer immediately",
        "attention": "Post during peak hours to maximize viral potential",
        "authority": "Include in professional portfolio and LinkedIn",
        "community": "Share in niche communities to spark discussion"
    }
    
    base_action = actions.get(purpose, "Post and monitor engagement")
    
    if confidence > 80:
        return f"Priority: {base_action}"
    elif confidence > 65:
        return f"Good fit: {base_action}"
    else:
        return f"Test: {base_action}"


def assess_content_risk(text: str, category: str) -> str:
    """Assess risk level for this content."""
    high_risk_terms = ["guarantee", "promise", "always", "never", "perfect", "instant", "overnight"]
    medium_risk_terms = ["should", "could", "might", "maybe", "potentially", "typically"]
    
    high_risk_count = sum(1 for term in high_risk_terms if term in text)
    medium_risk_count = sum(1 for term in medium_risk_terms if term in text)
    
    if high_risk_count > 0:
        return "high"
    elif medium_risk_count > 2:
        return "medium"
    else:
        return "low"


def build_director_brain_plan(
    clip: ClipResult,
    *,
    target_platform: str | None,
    category: str | None = None,
    trends: list[str] | None = None,
    rendered_state: str | None = None,
    user_id: str = "guest:unknown",
) -> DirectorBrainPlan:
    profile = profile_for_platform(target_platform or clip.target_platform or clip.platform_fit)
    detected_category = normalize_category(category or clip.detected_category or clip.category) or infer_category(clip)
    state = rendered_state or ("rendered" if clip_has_rendered_media(clip) else "strategy_only")
    base_hook = compact_sentence(clip.hook or clip.title or "Lead with the strongest payoff")
    hook_variants = build_hook_variants(base_hook=base_hook, profile=profile, category=detected_category)
    thumbnail_text = build_thumbnail_text(base_hook, profile=profile, category=detected_category)
    caption = build_caption(clip=clip, profile=profile, category=detected_category, trends=trends or [])
    packaging_angle = infer_packaging_angle(clip, category=detected_category)
    platform_fit = profile.fit_template.format(category=detected_category.replace("_", " "), first_seconds=profile.first_seconds)
    score = score_for_platform(clip=clip, profile=profile, rendered_state=state)
    confidence = confidence_for_plan(clip=clip, score=score, rendered_state=state)
    
    # Add opportunity intelligence
    opportunity_insight = analyze_opportunity_potential(clip, category=detected_category)
    
    # Add proof graph integration
    proof_manager = ProofGraphManager(user_id)
    
    # Extract proof potential from this clip
    proof_asset = proof_manager.extract_proof_from_clip(
        clip=clip,
        proof_type=ProofType.transformation,  # Default to transformation proof
        confidence_boost=5,  # Boost confidence for clear proof moments
    )
    
    # Create proof graph if it doesn't exist
    proof_graph = proof_manager.get_user_proof_graph()
    
    notes = [
        f"{profile.platform}: optimize for {profile.primary_signal}; secondary signal is {profile.secondary_signal}.",
        profile.hook_instruction,
        f"Opportunity: {opportunity_insight.opportunity_type} for {opportunity_insight.audience_target}.",
        f"Next action: {opportunity_insight.next_action}",
        f"Proof potential: {proof_asset.proof_type.value} with confidence {proof_asset.confidence_score}",
    ]
    if state != "rendered":
        notes.append("Strategy-only: packaging is ready, but no playable media should be shown as export-ready.")
    
    return DirectorBrainPlan(
        platform=profile.platform,
        category=detected_category,
        rendered_state=state,
        hook_variants=hook_variants,
        caption=caption,
        thumbnail_text=thumbnail_text,
        cta_suggestion=clip.cta_suggestion or profile.cta_template,
        packaging_angle=clip.packaging_angle or packaging_angle,
        platform_fit=platform_fit,
        score=score,
        confidence=confidence,
        explanation=(
            f"Director Brain routed this as {detected_category.replace('_', ' ')} for {profile.platform}; "
            f"the score favors {profile.primary_signal} and keeps rendered truth as {state}. "
            f"Opportunity insight: {opportunity_insight.purpose} content for {opportunity_insight.audience_target}. "
            f"Proof extracted: {proof_asset.proof_type.value} moment with {proof_asset.confidence_score}% confidence."
        ),
        opportunity_insight=opportunity_insight,
        platform_notes=notes,
        proof_asset=proof_asset,  # Add proof asset to the plan
    )


def profile_for_platform(value: str | None) -> PlatformDirectorProfile:
    normalized = normalize_platform(value)
    return PLATFORM_PROFILES.get(normalized, PLATFORM_PROFILES["tiktok"])


def normalize_platform(value: str | None) -> str:
    raw = (value or "").strip().lower()
    if not raw:
        return "tiktok"
    if "linkedin" in raw:
        return "linkedin"
    if "reel" in raw or "instagram" in raw:
        return "instagram reels"
    if "short" in raw or "youtube" in raw:
        return "youtube shorts"
    if "tiktok" in raw:
        return "tiktok"
    return raw


def normalize_category(value: str | None) -> str | None:
    raw = (value or "").strip().lower().replace("-", "_").replace(" ", "_")
    if not raw:
        return None
    aliases = {
        "ai": "ai_tech",
        "tech": "ai_tech",
        "product": "product_demo",
        "local": "local_business",
        "education_explainer": "education",
    }
    return aliases.get(raw, raw)


def infer_category(clip: ClipResult) -> str:
    text = " ".join(
        part
        for part in [
            clip.title,
            clip.hook,
            clip.caption,
            clip.transcript_excerpt,
            clip.reason,
            clip.why_this_matters,
            clip.platform_fit,
        ]
        if part
    ).lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(re.search(rf"\b{re.escape(keyword)}\b", text) for keyword in keywords):
            return category
    return "education"


def build_hook_variants(*, base_hook: str, profile: PlatformDirectorProfile, category: str) -> list[str]:
    focus = category.replace("_", " ")
    if profile.platform == "TikTok":
        return [
            trim_words(base_hook, 12),
            trim_words(f"Stop scrolling if this {focus} mistake costs you attention", 12),
            trim_words(f"Nobody explains the {focus} payoff this directly", 12),
        ]
    if profile.platform == "Instagram Reels":
        return [
            trim_words(base_hook, 12),
            trim_words(f"Send this to a {focus} creator who needs the shortcut", 14),
            trim_words(f"Show this to someone still missing the payoff", 12),
        ]
    if profile.platform == "YouTube Shorts":
        return [
            trim_words(base_hook, 10),
            trim_words(f"The {focus} reason starts here", 10),
            trim_words(f"Watch the first frame before you swipe", 10),
        ]
    return [
        trim_words(base_hook, 15),
        trim_words(f"The useful {focus} lesson is hiding in the first claim", 15),
        trim_words(f"Most teams miss this {focus} signal until too late", 15),
    ]


def build_caption(
    *,
    clip: ClipResult,
    profile: PlatformDirectorProfile,
    category: str,
    trends: list[str],
) -> str:
    focus = category.replace("_", " ")
    trend = f" Trend angle: {trends[0]}." if trends else ""
    source = compact_sentence(clip.caption or clip.hook or clip.title or "")
    if profile.platform == "Instagram Reels":
        return trim_chars(f"Send this to a {focus} creator who needs the payoff faster. {source}{trend}", 200)
    if profile.platform == "LinkedIn":
        return trim_chars(f"{source} The practical question: where would this change your {focus} workflow?", 500)
    if profile.platform == "YouTube Shorts":
        return trim_chars(f"{source} Would you watch the loop twice?{trend}", 120)
    return trim_chars(f"{source} Save the strongest {focus} hook and test the loop first.{trend}", 200)


def build_thumbnail_text(base_hook: str, *, profile: PlatformDirectorProfile, category: str) -> str:
    if profile.platform == "LinkedIn":
        return title_case_words(trim_words(base_hook, 5))
    if profile.platform == "YouTube Shorts":
        return title_case_words(trim_words(base_hook, 4))
    if profile.platform == "Instagram Reels":
        return title_case_words(trim_words(f"{category.replace('_', ' ')} payoff", 4))
    return title_case_words(trim_words(base_hook, 4))


def infer_packaging_angle(clip: ClipResult, *, category: str) -> str:
    text = " ".join(part for part in [clip.hook, clip.title, clip.caption] if part).lower()
    if any(word in text for word in ("wrong", "mistake", "debate", "disagree")):
        return "controversy"
    if any(word in text for word in ("why", "hidden", "secret", "nobody")):
        return "curiosity"
    if any(word in text for word in ("story", "before", "after")):
        return "story"
    if category in {"product_demo", "education", "coaching", "ai_tech"}:
        return "value"
    return "payoff"


def score_for_platform(*, clip: ClipResult, profile: PlatformDirectorProfile, rendered_state: str) -> int:
    base = int(clip.virality_score or clip.confidence_score or clip.score or 70)
    if profile.platform == "TikTok" and (clip.hook or "").lower().startswith(("stop", "why", "how")):
        base += 4
    if profile.platform == "Instagram Reels" and any(word in (clip.caption or "").lower() for word in ("send", "share", "friend")):
        base += 4
    if profile.platform == "YouTube Shorts" and (clip.duration or 0) and int(clip.duration or 0) <= 35:
        base += 3
    if profile.platform == "LinkedIn" and any(word in (clip.caption or "").lower() for word in ("workflow", "team", "business")):
        base += 3
    if rendered_state != "rendered":
        base -= 3
    return max(0, min(base, 100))


def confidence_for_plan(*, clip: ClipResult, score: int, rendered_state: str) -> int:
    confidence = int(clip.confidence_score or score)
    if clip.transcript_excerpt:
        confidence += 3
    if rendered_state == "rendered":
        confidence += 2
    return max(45, min(confidence, 96))


def clip_has_rendered_media(clip: ClipResult) -> bool:
    return bool(clip.preview_url or clip.edited_clip_url or clip.clip_url or clip.raw_clip_url or clip.download_url)


def compact_sentence(value: str) -> str:
    normalized = re.sub(r"\s+", " ", value or "").strip()
    return normalized.rstrip(".")


def trim_words(value: str, limit: int) -> str:
    words = compact_sentence(value).split()
    if len(words) <= limit:
        return " ".join(words)
    return " ".join(words[:limit])


def trim_chars(value: str, limit: int) -> str:
    normalized = compact_sentence(value)
    if len(normalized) <= limit:
        return normalized
    return normalized[: max(0, limit - 1)].rstrip() + "."


def title_case_words(value: str) -> str:
    return " ".join(word[:1].upper() + word[1:] for word in compact_sentence(value).split())

def _director_api_platform(value: str | None) -> str:
    normalized = normalize_platform(value)
    if normalized == "instagram reels":
        return "instagram_reels"
    if normalized == "youtube shorts":
        return "youtube_shorts"
    if normalized == "reels":
        return "reels"
    return normalized.replace(" ", "_")


def _director_quality_gate(transcript: str) -> tuple[str, list[str], int]:
    text = (transcript or "").lower()
    risky_terms = ["guaranteed", "risk free", "passive income", "investment"]
    warnings = [term for term in risky_terms if term in text]
    if warnings:
        return "warning", [f"Risk language detected: {term}" for term in warnings], min(len(warnings) * 10, 40)
    return "pass", [], 0


def director_brain_package(
    *,
    transcript: str,
    target_platform: str | None = None,
    category: str | None = None,
    caption_preset: str | None = None,
) -> dict[str, object]:
    platform_code = _director_api_platform(target_platform)
    category_code = normalize_category(category) or infer_category(
        ClipResult(
            id="director_package_source",
            title=transcript[:80] or "Director Brain package",
            hook=transcript[:80] or "Director Brain package",
            caption=transcript or "Director Brain package",
            score=60,
            transcript_excerpt=transcript,
        )
    )
    quality_status, warnings, risk_penalty = _director_quality_gate(transcript)
    display_category = category_code.replace("_", " ").title()
    if display_category == "Ai Tech":
        display_category = "AI Tech"

    base_clip = ClipResult(
        id="director_package_source",
        title=transcript[:80] or "Director Brain package",
        hook=transcript[:80] or "Director Brain package",
        caption=transcript or "Director Brain package",
        score=max(55, 72 - risk_penalty),
        transcript_excerpt=transcript,
        category=category_code,
        target_platform=target_platform,
    )
    plan = build_director_brain_plan(
        base_clip,
        target_platform=target_platform,
        category=category_code,
        rendered_state="strategy_only",
    )
    score = max(35, plan.score - risk_penalty)

    return {
        "algorithm_version": "director-brain-v1",
        "target_platform": platform_code,
        "recommended_platform": platform_code,
        "recommended_content_type": display_category,
        "recommended_output_style": plan.packaging_angle,
        "platform_recommendation_reason": plan.platform_fit,
        "caption_preset": (caption_preset or "clean_op").replace("-", "_"),
        "hook_formula_codes": ["contrarian_claim", "dataset-pattern", "open-loop"],
        "hooks": plan.hook_variants,
        "captions": [plan.caption],
        "moments": [
            {
                "start_seconds": 0,
                "end_seconds": 30,
                "hook_window_seconds": 2,
                "reason": plan.explanation,
            }
        ],
        "score": score,
        "quality_gate_status": quality_status,
        "quality_gate_warnings": warnings,
        "risk_penalty": risk_penalty,
        "rationale": f"Director Brain packaged this as {display_category} for {platform_code}.",
    }

def _director_api_platform(value: str | None) -> str:
    normalized = normalize_platform(value)
    if normalized == "instagram reels":
        return "instagram_reels"
    if normalized == "youtube shorts":
        return "youtube_shorts"
    if normalized == "reels":
        return "reels"
    return normalized.replace(" ", "_")


def _director_quality_gate(transcript: str) -> tuple[str, list[str], int]:
    text = (transcript or "").lower()
    risky_terms = ["guaranteed", "risk free", "passive income", "investment"]
    warnings = [term for term in risky_terms if term in text]
    if warnings:
        return "warning", [f"Risk language detected: {term}" for term in warnings], min(len(warnings) * 10, 40)
    return "pass", [], 0


def director_brain_package(
    *,
    transcript: str,
    target_platform: str | None = None,
    category: str | None = None,
    caption_preset: str | None = None,
) -> dict[str, object]:
    platform_code = _director_api_platform(target_platform)
    category_code = normalize_category(category) or infer_category(
        ClipResult(
            id="director_package_source",
            title=transcript[:80] or "Director Brain package",
            hook=transcript[:80] or "Director Brain package",
            caption=transcript or "Director Brain package",
            score=60,
            transcript_excerpt=transcript,
        )
    )
    quality_status, warnings, risk_penalty = _director_quality_gate(transcript)
    display_category = category_code.replace("_", " ").title()
    if display_category == "Ai Tech":
        display_category = "AI Tech"

    base_clip = ClipResult(
        id="director_package_source",
        title=transcript[:80] or "Director Brain package",
        hook=transcript[:80] or "Director Brain package",
        caption=transcript or "Director Brain package",
        score=max(55, 72 - risk_penalty),
        transcript_excerpt=transcript,
        category=category_code,
        target_platform=target_platform,
    )
    plan = build_director_brain_plan(
        base_clip,
        target_platform=target_platform,
        category=category_code,
        rendered_state="strategy_only",
    )
    score = max(35, plan.score - risk_penalty)

    return {
        "algorithm_version": "director-brain-v1",
        "target_platform": platform_code,
        "recommended_platform": platform_code,
        "recommended_content_type": display_category,
        "recommended_output_style": plan.packaging_angle,
        "platform_recommendation_reason": plan.platform_fit,
        "caption_preset": (caption_preset or "clean_op").replace("-", "_"),
        "hook_formula_codes": ["contrarian_claim", "dataset-pattern", "open-loop"],
        "hooks": plan.hook_variants,
        "captions": [plan.caption],
        "moments": [
            {
                "start_seconds": 0,
                "end_seconds": 30,
                "hook_window_seconds": 2,
                "reason": plan.explanation,
            }
        ],
        "score": score,
        "quality_gate_status": quality_status,
        "quality_gate_warnings": warnings,
        "risk_penalty": risk_penalty,
        "rationale": f"Director Brain packaged this as {display_category} for {platform_code}.",
    }
