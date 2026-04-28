from __future__ import annotations

from functools import lru_cache
import json
import re
from pathlib import Path
from typing import Any

from .capability_registry import list_capabilities

# =============================================================================
# LWA OMEGA
# UNIFIED INTELLIGENCE REGISTRY
# VIRTUAL CLIPPING DATA INTELLIGENCE
# NONFATAL PIPELINE
# =============================================================================

_APP_DIR = Path(__file__).resolve().parents[1]
_DATA_DIR = _APP_DIR / "data"
_INTELLIGENCE_SEED_DIR = _DATA_DIR / "intelligence_seed"
_VIRAL_DIR = _DATA_DIR / "viral_intelligence"
_TWITCH_DIR = _DATA_DIR / "twitch_seed"
_RUNTIME_DIR = _DATA_DIR / "intelligence_runtime"

_PLATFORM_ALIASES = {
    "tiktok": "tiktok",
    "tik_tok": "tiktok",
    "instagram": "reels",
    "instagram_reels": "reels",
    "reels_instagram": "reels",
    "reels": "reels",
    "youtube": "shorts",
    "youtube_shorts": "shorts",
    "shorts": "shorts",
    "linkedin_video": "linkedin",
    "linkedin": "linkedin",
    "x_video": "x",
    "twitter": "x",
    "x": "x",
    "facebook": "facebook",
    "facebook_reels": "facebook",
    "whop_community": "whop",
    "whop": "whop",
}

_FORBIDDEN_PUBLIC_CLAIMS = (
    "guaranteed viral",
    "guaranteed views",
    "guaranteed revenue",
    "guaranteed payout",
    "guaranteed income",
    "auto-posts to tiktok",
    "auto-posts to instagram",
    "direct-posts to youtube",
    "official whop payout automation",
    "browses whop campaigns natively",
    "submits campaign links automatically",
    "processes private videos without login",
    "replaces human editors completely",
    "full twitch live ingestion",
)

_ALLOWED_PUBLIC_CLAIMS = (
    "helps prepare clips",
    "upload-first workflow",
    "local fallback",
    "ranked clip packages",
    "hook variants",
    "captions",
    "timestamps",
    "platform compatibility guidance",
    "rendered vs strategy-only separation",
    "campaign-ready foundation",
    "twitch intelligence foundation",
    "score transparency",
)

_SIGNAL_FRONTEND_COPY: dict[str, dict[str, Any]] = {
    "vs_001": {
        "frontend_label": "Hook Strength",
        "frontend_description": "How strongly the clip opens in the first seconds.",
        "data_inputs_required": ["hook", "caption", "transcript", "audio_energy_optional"],
        "minimum_confidence_to_show": 0.55,
        "owner_council_role": "AI Intelligence Lead",
    },
    "vs_002": {
        "frontend_label": "Standalone Value",
        "frontend_description": "How well the clip stands on its own without extra context.",
        "data_inputs_required": ["title", "hook", "caption", "transcript"],
        "minimum_confidence_to_show": 0.55,
        "owner_council_role": "Chief Product Architect",
    },
    "vs_003": {
        "frontend_label": "Emotion",
        "frontend_description": "How much emotional pressure the moment carries.",
        "data_inputs_required": ["hook", "caption", "transcript", "audio_energy_optional"],
        "minimum_confidence_to_show": 0.5,
        "owner_council_role": "AI Intelligence Lead",
    },
    "vs_004": {
        "frontend_label": "Quotability",
        "frontend_description": "Whether the clip contains a line worth repeating or screenshotting.",
        "data_inputs_required": ["hook", "caption", "transcript"],
        "minimum_confidence_to_show": 0.55,
        "owner_council_role": "Sales Enablement Lead",
    },
    "vs_005": {
        "frontend_label": "Information Density",
        "frontend_description": "How much clear value the clip delivers per second.",
        "data_inputs_required": ["caption", "transcript", "duration_optional"],
        "minimum_confidence_to_show": 0.55,
        "owner_council_role": "AI Intelligence Lead",
    },
    "vs_006": {
        "frontend_label": "Payoff Arc",
        "frontend_description": "Whether the clip builds to a clear setup-to-payoff turn.",
        "data_inputs_required": ["hook", "caption", "transcript"],
        "minimum_confidence_to_show": 0.52,
        "owner_council_role": "Chief Product Architect",
    },
    "vs_007": {
        "frontend_label": "Shareability",
        "frontend_description": "How likely the framing is to trigger shares, saves, or DMs.",
        "data_inputs_required": ["hook", "caption", "transcript"],
        "minimum_confidence_to_show": 0.55,
        "owner_council_role": "Growth + SEO Lead",
    },
    "vs_008": {
        "frontend_label": "Curiosity Gap",
        "frontend_description": "Whether the opening creates a real reason to stay for the next beat.",
        "data_inputs_required": ["hook", "caption", "transcript"],
        "minimum_confidence_to_show": 0.55,
        "owner_council_role": "Chief Product Architect",
    },
    "vs_009": {
        "frontend_label": "Authority",
        "frontend_description": "How much the speaker sounds like they know what they are talking about.",
        "data_inputs_required": ["hook", "caption", "transcript"],
        "minimum_confidence_to_show": 0.5,
        "owner_council_role": "Sales Enablement Lead",
    },
    "vs_010": {
        "frontend_label": "Visual Anchor",
        "frontend_description": "Whether the clip has usable visual proof or a strong on-screen anchor.",
        "data_inputs_required": ["preview_url_optional", "clip_url_optional", "edited_clip_url_optional"],
        "minimum_confidence_to_show": 0.5,
        "owner_council_role": "Video Processing Lead",
    },
    "vs_011": {
        "frontend_label": "Conflict Beat",
        "frontend_description": "Whether the clip introduces a sharp disagreement or contrarian turn.",
        "data_inputs_required": ["hook", "caption", "transcript"],
        "minimum_confidence_to_show": 0.5,
        "owner_council_role": "Growth + SEO Lead",
    },
    "vs_012": {
        "frontend_label": "Loopability",
        "frontend_description": "How easily the ending can feed into another replay or series beat.",
        "data_inputs_required": ["hook", "caption", "duration_optional", "asset_presence_optional"],
        "minimum_confidence_to_show": 0.45,
        "owner_council_role": "Frontend / Muse-01 Creative Systems Director",
    },
}

_CATEGORY_PREFERRED_PLATFORMS = {
    "podcast": ["youtube_shorts", "tiktok", "reels_instagram"],
    "livestream_gaming": ["tiktok", "youtube_shorts", "x_video"],
    "business_strategy": ["linkedin_video", "youtube_shorts", "reels_instagram"],
    "finance_personal": ["reels_instagram", "youtube_shorts", "tiktok"],
    "coaching_self_dev": ["reels_instagram", "tiktok", "youtube_shorts"],
    "beauty_skincare": ["reels_instagram", "tiktok", "youtube_shorts"],
    "medspa_clinical": ["reels_instagram", "linkedin_video", "youtube_shorts"],
    "music_artist": ["tiktok", "reels_instagram", "youtube_shorts"],
    "sports_highlights": ["tiktok", "youtube_shorts", "reels_instagram"],
    "education_explainer": ["youtube_shorts", "linkedin_video", "tiktok"],
    "debate_political": ["x_video", "youtube_shorts", "tiktok"],
    "reaction": ["tiktok", "youtube_shorts", "reels_instagram"],
    "product_demo": ["reels_instagram", "youtube_shorts", "linkedin_video"],
    "ai_tech_review": ["youtube_shorts", "linkedin_video", "x_video"],
    "local_business": ["reels_instagram", "tiktok", "facebook_reels"],
}

_CATEGORY_RISK_FLAGS = {
    "medspa_clinical": ["medical_claim_review"],
    "finance_personal": ["financial_claim_review"],
    "debate_political": ["moderation_watch"],
    "local_business": ["proof_required"],
}

_CATEGORY_SALES_ANGLE = {
    "podcast": "best-clip-first transparency for long-form hosts",
    "business_strategy": "clean editorial packaging for authority-led content",
    "finance_personal": "proof-first ranking with strong claim discipline",
    "coaching_self_dev": "hook variants and premium repurposing without clutter",
    "product_demo": "result-first packaging with clearer CTA paths",
}

_BADGE_DEPENDENCIES = {
    "Best Clip First": ["rank", "score", "is_best_clip"],
    "Rendered": ["clip_url", "edited_clip_url", "preview_url", "render_status", "is_rendered"],
    "Ideas Only": ["strategy_only", "is_strategy_only", "rendered", "is_rendered"],
    "Strong Hook": ["signals.vs_001"],
    "High Shareability": ["signals.vs_007"],
    "Platform Mismatch": ["platform_compatibility", "duration", "target_platform"],
    "Captions Missing": ["caption_track", "caption_srt_url", "caption_vtt_url", "caption_txt_url"],
    "Trend Match": ["trend_match_score"],
    "Score Pill": ["score"],
    "Provider Pill": ["ai_provider"],
}

_KNOWN_BACKEND_FIELDS = {
    "rank",
    "score",
    "is_best_clip",
    "clip_url",
    "edited_clip_url",
    "preview_url",
    "render_status",
    "is_rendered",
    "strategy_only",
    "is_strategy_only",
    "rendered",
    "signals.vs_001",
    "signals.vs_007",
    "platform_compatibility",
    "duration",
    "target_platform",
    "caption_track",
    "caption_srt_url",
    "caption_vtt_url",
    "caption_txt_url",
    "trend_match_score",
    "ai_provider",
}


def normalize_platform_key(platform: str | None) -> str:
    normalized = (platform or "").strip().lower().replace("-", "_").replace(" ", "_")
    return _PLATFORM_ALIASES.get(normalized, normalized or "tiktok")


def _display_name_from_slug(value: str) -> str:
    return value.replace("_", " ").replace("-", " ").title()


def _source_confidence(source: str | None) -> str:
    lowered = (source or "").lower()
    if "assumption" in lowered:
        return "assumption"
    if any(token in lowered for token in ("mosseri", "tiktok", "youtube", "meta", "linkedin")):
        return "platform_direct"
    if any(token in lowered for token in ("whitehat", "forkoff", "operator", "agency")):
        return "operator_data"
    if any(token in lowered for token in ("vizard", "reap", "flowshorts", "miraflow", "castmagic", "vidiq")):
        return "vendor_biased"
    return "industry_research"


def _read_json(path: Path, fallback: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback


def _read_dir(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    payload: dict[str, Any] = {}
    for file_path in sorted(path.glob("*.json")):
        payload[file_path.stem] = _read_json(file_path, [] if file_path.name.endswith(".json") else {})
    return payload


def _runtime_sources_summary() -> dict[str, Any]:
    summary: dict[str, Any] = {}
    for name in ("feedback", "performance", "events"):
        path = _RUNTIME_DIR / f"{name}.jsonl"
        count = 0
        if path.exists():
            try:
                count = len(path.read_text(encoding="utf-8").splitlines())
            except OSError:
                count = 0
        summary[name] = {
            "path": str(path),
            "exists": path.exists(),
            "record_count": count,
        }
    return summary


def _signal_name_by_id(rows: list[dict[str, Any]]) -> dict[str, str]:
    return {str(row.get("id")): str(row.get("signal_name")) for row in rows if row.get("id")}


def _caption_presets_by_id(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    presets: dict[str, dict[str, Any]] = {}
    for row in rows:
        row_id = str(row.get("id") or "")
        if row_id:
            presets[row_id] = row
    return presets


def _resolve_preset_name(preset_id: str | None, presets: dict[str, dict[str, Any]]) -> str | None:
    if not preset_id:
        return None
    preset = presets.get(preset_id)
    if isinstance(preset, dict):
        return str(preset.get("preset_name") or preset_id)
    return preset_id


def _platform_display_name(platform: str) -> str:
    mapping = {
        "tiktok": "TikTok",
        "reels_instagram": "Instagram Reels",
        "youtube_shorts": "YouTube Shorts",
        "facebook_reels": "Facebook Reels",
        "x_video": "X Video",
        "linkedin_video": "LinkedIn Video",
        "whop_community": "Whop Community",
    }
    return mapping.get(platform, _display_name_from_slug(platform))


def _extend_viral_signal_rules(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    extended: list[dict[str, Any]] = []
    for row in rows:
        signal_id = str(row.get("id") or "")
        defaults = _SIGNAL_FRONTEND_COPY.get(signal_id, {})
        extended.append(
            {
                **row,
                "source": row.get("source") or "internal council seed from viral intelligence report",
                "source_confidence": row.get("source_confidence") or _source_confidence(row.get("source")),
                "user_visible": bool(row.get("user_visible", True)),
                "frontend_label": row.get("frontend_label") or defaults.get("frontend_label") or _display_name_from_slug(str(row.get("signal_name", signal_id))),
                "frontend_description": row.get("frontend_description") or defaults.get("frontend_description") or "",
                "data_inputs_required": row.get("data_inputs_required") or defaults.get("data_inputs_required") or [],
                "fallback_detection_supported": bool(row.get("fallback_detection_supported", True)),
                "minimum_confidence_to_show": float(row.get("minimum_confidence_to_show", defaults.get("minimum_confidence_to_show", 0.5))),
                "owner_council_role": row.get("owner_council_role") or defaults.get("owner_council_role") or "AI Intelligence Lead",
            }
        )
    return extended


def _extend_platform_rules(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    defaults = {
        "tiktok": "karaoke_bold",
        "reels_instagram": "clean_editorial",
        "youtube_shorts": "clean_editorial",
        "facebook_reels": "clean_editorial",
        "x_video": "clean_editorial",
        "linkedin_video": "clean_editorial",
        "whop_community": "clean_editorial",
    }
    extended: list[dict[str, Any]] = []
    for row in rows:
        platform = str(row.get("platform") or "")
        optimal = row.get("optimal_length_sec") or [0, 0]
        min_length = int(row.get("min_length_sec", optimal[0] if len(optimal) >= 1 else 0))
        max_length = int(row.get("max_length_sec", optimal[1] if len(optimal) >= 2 else 0))
        extended.append(
            {
                **row,
                "display_name": row.get("display_name") or _platform_display_name(platform),
                "min_length_sec": min_length,
                "max_length_sec": max_length,
                "source_confidence": row.get("source_confidence") or _source_confidence(row.get("source")),
                "export_profile_id": row.get("export_profile_id") or normalize_platform_key(platform),
                "default_caption_preset": row.get("default_caption_preset") or defaults.get(platform, "clean_editorial"),
                "badge_rules": row.get("badge_rules") or ["Score Pill", "Provider Pill", "Platform Mismatch"],
                "unsupported_claims": row.get("unsupported_claims")
                or ["guaranteed viral", "guaranteed views", "direct-posting"],
                "public_copy_allowed": bool(row.get("public_copy_allowed", True)),
            }
        )
    return extended


def _extend_content_categories(
    rows: list[dict[str, Any]],
    presets: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    extended: list[dict[str, Any]] = []
    for row in rows:
        category = str(row.get("category") or "")
        preset_id = str(row.get("caption_preset") or "")
        extended.append(
            {
                **row,
                "display_name": row.get("display_name") or _display_name_from_slug(category),
                "preferred_platforms": row.get("preferred_platforms") or _CATEGORY_PREFERRED_PLATFORMS.get(category, ["tiktok", "reels_instagram"]),
                "default_caption_preset": row.get("default_caption_preset") or _resolve_preset_name(preset_id, presets) or "clean_editorial",
                "risk_flags": row.get("risk_flags") or _CATEGORY_RISK_FLAGS.get(category, []),
                "sales_positioning_angle": row.get("sales_positioning_angle") or _CATEGORY_SALES_ANGLE.get(category, "ranked clip packaging"),
                "source_confidence": row.get("source_confidence") or _source_confidence(row.get("source")),
                "owner_council_role": row.get("owner_council_role") or "Chief Product Architect",
            }
        )
    return extended


def _extend_hook_formulas(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    extended: list[dict[str, Any]] = []
    for row in rows:
        best_for = list(row.get("best_for") or [])
        extended.append(
            {
                **row,
                "avoid_for": row.get("avoid_for") or ["medspa_clinical"] if row.get("name") == "tabloid_punch" else row.get("avoid_for") or [],
                "risk_level": row.get("risk_level") or ("medium" if "controvers" in str(row.get("name", "")).lower() else "low"),
                "requires_fact_check": bool(row.get("requires_fact_check", any(category in {"finance_personal", "medspa_clinical", "debate_political"} for category in best_for))),
                "platform_fit": row.get("platform_fit") or _infer_platform_fit(best_for),
                "category_fit": row.get("category_fit") or best_for,
                "output_label": row.get("output_label") or _display_name_from_slug(str(row.get("name") or "hook_formula")),
            }
        )
    return extended


def _infer_platform_fit(categories: list[str]) -> list[str]:
    platforms: list[str] = []
    for category in categories:
        for platform in _CATEGORY_PREFERRED_PLATFORMS.get(category, []):
            if platform not in platforms:
                platforms.append(platform)
    return platforms


def _extend_caption_presets(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    extended: list[dict[str, Any]] = []
    for row in rows:
        categories = list(row.get("category_fit") or [])
        extended.append(
            {
                **row,
                "display_name": row.get("display_name") or _display_name_from_slug(str(row.get("preset_name") or row.get("id") or "caption_preset")),
                "platform_fit": row.get("platform_fit") or _infer_platform_fit(categories),
                "accessibility_notes": row.get("accessibility_notes") or "Keep contrast readable on sound-off mobile playback.",
                "implementation_status": row.get("implementation_status") or "data_only",
            }
        )
    return extended


def _extend_thumbnail_rules(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    extended: list[dict[str, Any]] = []
    for row in rows:
        rule_text = str(row.get("rule") or "")
        enforcement = "recommendation"
        if "never" in rule_text.lower():
            enforcement = "warning"
        if "should not lie" in rule_text.lower():
            enforcement = "block"
        extended.append(
            {
                **row,
                "source_confidence": row.get("source_confidence") or _source_confidence(row.get("source")),
                "enforcement": row.get("enforcement") or enforcement,
                "frontend_message": row.get("frontend_message") or rule_text,
                "related_capability": row.get("related_capability") or "rendered_vs_strategy_packages",
            }
        )
    return extended


def _extend_frontend_badges(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    extended: list[dict[str, Any]] = []
    for row in rows:
        badge = str(row.get("badge") or "")
        applies_to = "both"
        if badge == "Rendered":
            applies_to = "rendered"
        elif badge == "Ideas Only":
            applies_to = "strategy_only"
        extended.append(
            {
                **row,
                "max_per_card_group": row.get("max_per_card_group") or 3,
                "user_visible": bool(row.get("user_visible", True)),
                "applies_to": row.get("applies_to") or applies_to,
                "source_table": row.get("source_table") or "frontend_badge_rules",
                "backend_field_dependencies": row.get("backend_field_dependencies") or _BADGE_DEPENDENCIES.get(badge, []),
            }
        )
    return extended


def _extend_competitor_matrix(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            **row,
            "claim_safety": row.get("claim_safety") or "internal_only",
            "source_confidence": row.get("source_confidence") or "vendor_biased",
            "sales_use_allowed": bool(row.get("sales_use_allowed", True)),
            "public_use_allowed": bool(row.get("public_use_allowed", False)),
        }
        for row in rows
    ]


def _extend_sales_positioning(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    extended: list[dict[str, Any]] = []
    for row in rows:
        lwa_claim = str(row.get("lwa_claim") or row.get("lwa_positioning") or "")
        pain = str(row.get("pain") or "")
        proof = str(row.get("proof_point") or "")
        segment = str(row.get("segment") or "")
        extended.append(
            {
                "segment": segment,
                "pain": pain,
                "competitor_claim": row.get("competitor_claim") or "",
                "lwa_claim": lwa_claim,
                "proof_point": proof,
                "safe_script": row.get("safe_script") or f"{lwa_claim}. Proof point: {proof}".strip(),
                "risky_words_to_avoid": row.get("risky_words_to_avoid") or ["guaranteed", "automatic", "viral"],
                "sales_stage": row.get("sales_stage") or ("close" if "whop" in segment else "discovery"),
                "owner_role": row.get("owner_role") or "Sales Enablement Lead",
            }
        )
    return extended


def _build_viral_tables(raw: dict[str, Any]) -> dict[str, Any]:
    signal_rules = _extend_viral_signal_rules(list(raw.get("viral_signal_rules") or []))
    caption_presets = _extend_caption_presets(list(raw.get("caption_style_presets") or []))
    presets_by_id = _caption_presets_by_id(caption_presets)
    content_categories = _extend_content_categories(list(raw.get("content_category_rules") or []), presets_by_id)
    hook_formulas = _extend_hook_formulas(list(raw.get("hook_formula_library") or []))
    platform_rules = _extend_platform_rules(list(raw.get("platform_rules") or []))
    thumbnail_rules = _extend_thumbnail_rules(list(raw.get("thumbnail_rules") or []))
    frontend_badges = _extend_frontend_badges(list(raw.get("frontend_badge_rules") or []))
    competitor_matrix = _extend_competitor_matrix(list(raw.get("competitor_matrix") or []))
    sales_positioning = _extend_sales_positioning(list(raw.get("sales_positioning_matrix") or []))

    clip_scoring_weights = dict(raw.get("clip_scoring_weights") or {})
    platform_modifiers = dict(raw.get("platform_modifiers") or clip_scoring_weights.get("platform_modifiers") or {})

    return {
        **raw,
        "viral_signal_rules": signal_rules,
        "platform_rules": platform_rules,
        "content_category_rules": content_categories,
        "hook_formula_library": hook_formulas,
        "caption_style_presets": caption_presets,
        "thumbnail_rules": thumbnail_rules,
        "frontend_badge_rules": frontend_badges,
        "competitor_matrix": competitor_matrix,
        "sales_positioning_matrix": sales_positioning,
        "clip_scoring_weights": clip_scoring_weights,
        "platform_modifiers": platform_modifiers,
    }


@lru_cache(maxsize=1)
def load_intelligence_tables() -> dict[str, Any]:
    product_tables = _read_dir(_INTELLIGENCE_SEED_DIR)
    viral_tables = _read_dir(_VIRAL_DIR)
    twitch_tables = _read_dir(_TWITCH_DIR)
    capabilities = [record.model_dump() for record in list_capabilities()]

    return {
        "viral": _build_viral_tables(viral_tables),
        "product": product_tables,
        "twitch": twitch_tables,
        "capabilities": capabilities,
        "runtime_sources": _runtime_sources_summary(),
    }


def validate_intelligence_tables() -> dict[str, Any]:
    tables = load_intelligence_tables()
    viral = tables["viral"]
    capabilities = tables["capabilities"]

    errors: list[str] = []
    warnings: list[str] = []

    signal_rules = list(viral.get("viral_signal_rules") or [])
    signal_ids = [str(row.get("id")) for row in signal_rules if row.get("id")]
    signal_names = {str(row.get("signal_name")) for row in signal_rules if row.get("signal_name")}
    signal_weight_total = round(sum(float(row.get("weight_default") or 0.0) for row in signal_rules), 6)
    if signal_weight_total != 1.0:
        errors.append(f"viral signal weights must sum to 1.0, got {signal_weight_total}")
    if len(signal_ids) != len(set(signal_ids)):
        errors.append("viral signal ids must be unique")

    platform_modifiers = dict(viral.get("platform_modifiers") or {})
    for platform, modifiers in platform_modifiers.items():
        for signal_id in modifiers:
            if signal_id not in signal_ids:
                errors.append(f"platform modifier {platform}.{signal_id} references unknown signal")

    presets = {str(row.get("id")) for row in viral.get("caption_style_presets", []) if row.get("id")}
    for row in viral.get("content_category_rules", []):
        for signal_name in row.get("top_signal_weights", []):
            if signal_name not in signal_names:
                errors.append(f"category {row.get('category')} references unknown signal name {signal_name}")
        preset_id = str(row.get("caption_preset") or "")
        if preset_id and preset_id not in presets:
            errors.append(f"category {row.get('category')} references missing caption preset {preset_id}")

    for row in viral.get("frontend_badge_rules", []):
        for dependency in row.get("backend_field_dependencies", []):
            if dependency not in _KNOWN_BACKEND_FIELDS:
                warnings.append(f"badge {row.get('badge')} dependency {dependency} is future-facing")

    for row in viral.get("sales_positioning_matrix", []):
        lowered_claim = f"{row.get('lwa_claim', '')} {row.get('safe_script', '')}".lower()
        for forbidden in _FORBIDDEN_PUBLIC_CLAIMS:
            if forbidden in lowered_claim:
                errors.append(f"sales positioning for {row.get('segment')} uses forbidden claim {forbidden}")

    for capability in capabilities:
        if capability.get("status") == "intentionally_unsupported" and capability.get("public_claim") == "allowed":
            errors.append(f"capability {capability.get('id')} cannot be intentionally unsupported and publicly allowed")

    return {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "signal_weight_total": signal_weight_total,
        "signal_count": len(signal_ids),
    }


def _platform_rule_index() -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for row in load_intelligence_tables()["viral"].get("platform_rules", []):
        platform = str(row.get("platform") or "")
        index[platform] = row
        index[normalize_platform_key(platform)] = row
    return index


def _category_rule_index() -> dict[str, dict[str, Any]]:
    return {
        str(row.get("category") or ""): row
        for row in load_intelligence_tables()["viral"].get("content_category_rules", [])
    }


def _caption_preset_index() -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for row in load_intelligence_tables()["viral"].get("caption_style_presets", []):
        row_id = str(row.get("id") or "")
        preset_name = str(row.get("preset_name") or "")
        if row_id:
            index[row_id] = row
        if preset_name:
            index[preset_name] = row
    return index


def build_unified_platform_profile(platform: str | None) -> dict[str, Any]:
    tables = load_intelligence_tables()
    viral = tables["viral"]
    canonical = normalize_platform_key(platform)
    platform_index = _platform_rule_index()
    row = platform_index.get(canonical) or platform_index.get(platform or "") or {}
    default_caption = str(row.get("default_caption_preset") or "clean_editorial")
    capabilities = {item["id"]: item for item in tables.get("capabilities", [])}
    return {
        "canonical_platform": canonical,
        "rule": row,
        "platform_modifiers": dict(viral.get("platform_modifiers", {}).get(canonical, {})),
        "default_caption_preset": default_caption,
        "default_caption_preset_details": _caption_preset_index().get(default_caption, {}),
        "badge_rules": viral.get("frontend_badge_rules", []),
        "unsupported_claims": row.get("unsupported_claims", list(_FORBIDDEN_PUBLIC_CLAIMS)),
        "public_copy_allowed": row.get("public_copy_allowed", True),
        "capability_state": {
            "direct_social_posting": capabilities.get("direct_social_posting"),
            "campaign_submission_automation": capabilities.get("campaign_submission_automation"),
        },
    }


def build_unified_category_profile(category: str | None) -> dict[str, Any]:
    canonical = str(category or "").strip() or "podcast"
    row = _category_rule_index().get(canonical, {})
    caption_preset = str(row.get("default_caption_preset") or "clean_editorial")
    sales_rows = load_intelligence_tables()["viral"].get("sales_positioning_matrix", [])
    matching_sales = [
        entry for entry in sales_rows
        if canonical.split("_")[0] in str(entry.get("segment", ""))
    ]
    if not matching_sales:
        matching_sales = sales_rows[:2]
    return {
        "category": canonical,
        "rule": row,
        "hook_formulas": [
            formula
            for formula in load_intelligence_tables()["viral"].get("hook_formula_library", [])
            if canonical in formula.get("category_fit", []) or canonical in formula.get("best_for", [])
        ],
        "caption_preset": caption_preset,
        "caption_preset_details": _caption_preset_index().get(caption_preset, {}),
        "risk_flags": row.get("risk_flags", []),
        "sales_positioning": matching_sales,
    }


def _signal_weights_for(platform: str | None, category: str | None) -> dict[str, float]:
    viral = load_intelligence_tables()["viral"]
    base_weights = dict(viral.get("clip_scoring_weights", {}).get("base_weights") or {})
    if not base_weights:
        base_weights = {row["id"]: float(row.get("weight_default") or 0.0) for row in viral.get("viral_signal_rules", [])}
    modifiers = dict(viral.get("platform_modifiers", {}).get(normalize_platform_key(platform), {}))
    category_modifiers = dict(viral.get("clip_scoring_weights", {}).get("category_modifiers", {}).get(str(category or ""), {}))
    signal_name_lookup = _signal_name_by_id(viral.get("viral_signal_rules", []))

    effective: dict[str, float] = {}
    for signal_id, base_weight in base_weights.items():
        name = signal_name_lookup.get(signal_id, signal_id)
        platform_multiplier = float(modifiers.get(signal_id, 1.0))
        category_multiplier = float(category_modifiers.get(signal_id, category_modifiers.get(name, 1.0)))
        effective[signal_id] = float(base_weight) * platform_multiplier * category_multiplier
    total = sum(effective.values()) or 1.0
    return {signal_id: value / total for signal_id, value in effective.items()}


def build_clip_intelligence_context(platform: str | None, category: str | None) -> dict[str, Any]:
    category_profile = build_unified_category_profile(category)
    return {
        "platform_profile": build_unified_platform_profile(platform),
        "category_profile": category_profile,
        "signal_weights": _signal_weights_for(platform, category_profile.get("category")),
        "hook_formulas": category_profile.get("hook_formulas") or load_intelligence_tables()["viral"].get("hook_formula_library", []),
        "caption_presets": load_intelligence_tables()["viral"].get("caption_style_presets", []),
        "badge_rules": load_intelligence_tables()["viral"].get("frontend_badge_rules", []),
    }


def public_claim_guard(text: str) -> dict[str, Any]:
    lowered = (text or "").lower()
    warnings: list[str] = []
    blocked_terms: list[str] = []

    for forbidden in _FORBIDDEN_PUBLIC_CLAIMS:
        if forbidden in lowered:
            blocked_terms.append(forbidden)
    if blocked_terms:
        warnings.append("Contains forbidden public claims that require rewrite.")

    capabilities = load_intelligence_tables().get("capabilities", [])
    for capability in capabilities:
        if capability.get("public_claim") == "not_allowed":
            capability_name = str(capability.get("name") or capability.get("id") or "").lower()
            capability_tokens = [token for token in re.split(r"[^a-z0-9]+", capability_name) if len(token) > 3]
            if capability_tokens and all(token in lowered for token in capability_tokens[:2]):
                warnings.append(f"References not-allowed capability: {capability.get('id')}")

    return {
        "safe": not blocked_terms,
        "warnings": warnings,
        "blocked_terms": blocked_terms,
        "allowed_examples": list(_ALLOWED_PUBLIC_CLAIMS),
    }


def suggest_weight_adjustments_from_feedback(limit: int = 200) -> dict[str, Any]:
    feedback_path = _RUNTIME_DIR / "feedback.jsonl"
    performance_path = _RUNTIME_DIR / "performance.jsonl"
    feedback_rows: list[dict[str, Any]] = []
    performance_rows: list[dict[str, Any]] = []

    for path, target in ((feedback_path, feedback_rows), (performance_path, performance_rows)):
        if not path.exists():
            continue
        try:
            for line in path.read_text(encoding="utf-8").splitlines()[-limit:]:
                try:
                    target.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        except OSError:
            continue

    recommendations: list[dict[str, Any]] = []
    if feedback_rows:
        low_score_positive = [
            row for row in feedback_rows
            if (row.get("user_rating") or row.get("rating") or 0) >= 4 and (row.get("score") or 0) < 65
        ]
        if low_score_positive:
            recommendations.append(
                {
                    "type": "review_thresholds",
                    "message": "Several positively rated clips scored below 65. Review fallback signal weighting before changing seed tables.",
                    "sample_size": len(low_score_positive),
                }
            )
    if performance_rows:
        high_score_low_engagement = [
            row for row in performance_rows
            if (row.get("score") or 0) >= 80 and (row.get("shares") or 0) == 0 and (row.get("saves") or 0) == 0
        ]
        if high_score_low_engagement:
            recommendations.append(
                {
                    "type": "shareability_audit",
                    "message": "High-scoring clips with low saves/shares suggest reviewing shareability_phrase and curiosity weighting.",
                    "sample_size": len(high_score_low_engagement),
                }
            )

    return {
        "feedback_records_considered": len(feedback_rows),
        "performance_records_considered": len(performance_rows),
        "recommendations": recommendations,
        "seed_mutation_performed": False,
    }
