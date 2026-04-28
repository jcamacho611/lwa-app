# =============================================================================
# LWA OMEGA / CLAUDE HANDOFF
# =============================================================================
# Safety rules: DO NOT remove existing routes. DO NOT touch lwa-ios.
# DO NOT make this file fatal to generation if it fails.
# Search markers: CLAUDE HANDOFF | LWA OMEGA | INTELLIGENCE DATA CORE
#                 UPLOAD-FIRST CLIPPING ENGINE | NONFATAL PIPELINE
# =============================================================================
#
# =============================================================================
# INTELLIGENCE DATA CORE
# =============================================================================
# Claude:
#   This is the file-backed foundation for LWA's proprietary clipping brain.
#
# It stores and exposes:
#   - platform rules        (platform_rules.json)
#   - hook formulas         (hook_formulas.json)
#   - caption presets       (caption_style_presets.json)
#   - scoring weights       (scoring_weights.json)
#   - content categories    (content_categories.json)
#   - risk rules            (risk_rules.json)
#   - supported formats     (supported_media_formats.json)
#   - feedback events       (JSONL runtime log)
#   - performance events    (JSONL runtime log)
#
# Intentionally JSON/JSONL-backed first — works before Postgres, Twitch,
# TikTok, Instagram, or paid AI providers are required.
#
# Future direction:
#   Every generated clip should eventually teach LWA what works.
# =============================================================================

"""
intelligence_data_core.py — File-backed intelligence data core for LWA.

Loads seed data from JSON files and exposes deterministic scoring, risk
checking, event logging, and feedback collection.

No external API dependencies. All failures are nonfatal.
"""
from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from .intelligence_registry import (
    build_unified_category_profile,
    build_unified_platform_profile,
    load_intelligence_tables,
    public_claim_guard,
    suggest_weight_adjustments_from_feedback,
    validate_intelligence_tables,
)

logger = logging.getLogger("uvicorn.error")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_SEED_DIR = Path(__file__).parent.parent / "data" / "intelligence_seed"
_RUNTIME_DIR = Path(__file__).parent.parent / "data" / "intelligence_runtime"

_SEED_FILES = {
    "platform_rules":              "platform_rules.json",
    "scoring_weights":             "scoring_weights.json",
    "scoring_component_defs":      "scoring_component_definitions.json",
    "hook_formulas":               "hook_formulas.json",
    "caption_style_presets":       "caption_style_presets.json",
    "content_categories":          "content_categories.json",
    "moment_types":                "moment_types.json",
    "risk_rules":                  "risk_rules.json",
    "supported_media_formats":     "supported_media_formats.json",
}


# ---------------------------------------------------------------------------
# Core class
# ---------------------------------------------------------------------------

class IntelligenceDataCore:
    """
    Singleton-style intelligence data core.
    Load once; serve many requests.
    """

    def __init__(self) -> None:
        self._data: Dict[str, Any] = {}
        self._loaded = False
        self._load_errors: List[str] = []
        self._runtime_dir = _RUNTIME_DIR

        try:
            self._runtime_dir.mkdir(parents=True, exist_ok=True)
        except OSError:
            pass

        self._load_seed_data()

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------

    def _load_seed_data(self) -> None:
        """Load all JSON seed files. Errors are nonfatal."""
        for key, filename in _SEED_FILES.items():
            path = _SEED_DIR / filename
            try:
                self._data[key] = json.loads(path.read_text(encoding="utf-8"))
                logger.debug("intelligence_data_core: loaded %s", filename)
            except FileNotFoundError:
                self._load_errors.append(f"seed file not found: {filename}")
                self._data[key] = {} if "rules" in key or "weights" in key else []
                logger.warning("intelligence_data_core: seed file missing: %s", filename)
            except json.JSONDecodeError as exc:
                self._load_errors.append(f"JSON error in {filename}: {exc}")
                self._data[key] = {} if "rules" in key or "weights" in key else []
                logger.warning("intelligence_data_core: JSON error in %s: %s", filename, exc)

        self._loaded = True

    def validate_seed_data(self) -> Dict[str, Any]:
        """Return a validation summary of loaded seed data."""
        status = {}
        for key, filename in _SEED_FILES.items():
            d = self._data.get(key)
            if isinstance(d, dict):
                status[key] = {"ok": bool(d), "count": len(d), "type": "dict"}
            elif isinstance(d, list):
                status[key] = {"ok": bool(d), "count": len(d), "type": "list"}
            else:
                status[key] = {"ok": False, "count": 0, "type": "unknown"}
        return {
            "seed_status": status,
            "load_errors": self._load_errors,
            "registry_validation": validate_intelligence_tables(),
        }

    # ------------------------------------------------------------------
    # Data accessors
    # ------------------------------------------------------------------

    def all_rules(self) -> Dict[str, Any]:
        unified = load_intelligence_tables()
        return {
            **dict(self._data),
            "viral_intelligence": unified.get("viral", {}),
            "capabilities": unified.get("capabilities", []),
            "runtime_sources": unified.get("runtime_sources", {}),
        }

    def platform_rules(self) -> Dict[str, Any]:
        return dict(self._data.get("platform_rules", {}))

    def hook_formulas(self) -> List[Dict]:
        return list(self._data.get("hook_formulas", []))

    def content_categories(self) -> List[Dict]:
        return list(self._data.get("content_categories", []))

    def caption_presets(self) -> List[Dict]:
        return list(self._data.get("caption_style_presets", []))

    def scoring_weights(self) -> Dict[str, Any]:
        return dict(self._data.get("scoring_weights", {}))

    def risk_rules(self) -> List[Dict]:
        return list(self._data.get("risk_rules", []))

    def supported_formats(self) -> Dict[str, Any]:
        return dict(self._data.get("supported_media_formats", {}))

    def moment_types(self) -> List[Dict]:
        return list(self._data.get("moment_types", []))

    def viral_signal_rules(self) -> List[Dict]:
        return list(load_intelligence_tables().get("viral", {}).get("viral_signal_rules", []))

    def viral_platform_rules(self) -> List[Dict]:
        return list(load_intelligence_tables().get("viral", {}).get("platform_rules", []))

    def viral_content_category_rules(self) -> List[Dict]:
        return list(load_intelligence_tables().get("viral", {}).get("content_category_rules", []))

    def hook_formula_library(self) -> List[Dict]:
        return list(load_intelligence_tables().get("viral", {}).get("hook_formula_library", []))

    def frontend_badge_rules(self) -> List[Dict]:
        return list(load_intelligence_tables().get("viral", {}).get("frontend_badge_rules", []))

    def sales_positioning(self) -> List[Dict]:
        return list(load_intelligence_tables().get("viral", {}).get("sales_positioning_matrix", []))

    def competitor_matrix(self) -> List[Dict]:
        return list(load_intelligence_tables().get("viral", {}).get("competitor_matrix", []))

    def unified_platform_profiles(self) -> Dict[str, Dict[str, Any]]:
        profiles: Dict[str, Dict[str, Any]] = {}
        for rule in self.viral_platform_rules():
            platform = str(rule.get("platform") or "")
            profiles[platform] = build_unified_platform_profile(platform)
        return profiles

    def unified_category_profiles(self) -> Dict[str, Dict[str, Any]]:
        profiles: Dict[str, Dict[str, Any]] = {}
        for rule in self.viral_content_category_rules():
            category = str(rule.get("category") or "")
            profiles[category] = build_unified_category_profile(category)
        return profiles

    def claim_guard_check(self, text: str) -> Dict[str, Any]:
        return public_claim_guard(text)

    def suggest_weight_adjustments_from_feedback(self, limit: int = 200) -> Dict[str, Any]:
        return suggest_weight_adjustments_from_feedback(limit=limit)

    # ------------------------------------------------------------------
    # Scoring
    # ------------------------------------------------------------------

    def score_clip(self, clip_data: Dict) -> Dict[str, Any]:
        """
        Deterministic local clip score from available clip data.

        Accepts a dict with any combination of:
          transcript, hook, platform, duration_seconds, filler_word_count,
          word_count, has_face, audio_ok, has_captions, category, etc.

        Returns virality_score (0–100), component scores, and confidence.
        """
        weights_cfg = self._data.get("scoring_weights", {})
        weights = {k: v["weight"] for k, v in weights_cfg.get("components", {}).items()}

        scores: Dict[str, float] = {}

        # Hook score — basic keyword match
        hook = str(clip_data.get("hook", "") or clip_data.get("transcript", ""))[:500].lower()
        hook_s = 30.0
        hook_formulas = self._data.get("hook_formulas", [])
        for formula in hook_formulas:
            for pat in formula.get("detection_patterns", []):
                if pat in hook:
                    hook_s = min(hook_s + 15, 85)
                    break
        scores["hook_score"] = round(hook_s, 1)

        # Retention — proxy from filler word density
        word_count = max(int(clip_data.get("word_count", 100)), 1)
        filler_count = int(clip_data.get("filler_word_count", 0))
        filler_ratio = filler_count / word_count
        retention_s = max(20.0, 80.0 - filler_ratio * 200)
        scores["retention_score"] = round(min(retention_s, 85), 1)

        # Emotional spike — keyword presence in transcript
        transcript = str(clip_data.get("transcript", "")).lower()
        emotion_keywords = ["can't believe", "honestly", "insane", "shocked", "amazing", "wow", "incredible"]
        emotion_hits = sum(1 for kw in emotion_keywords if kw in transcript)
        scores["emotional_spike_score"] = round(min(30 + emotion_hits * 12, 85), 1)

        # Clarity — audio and structure
        audio_ok = bool(clip_data.get("audio_ok", True))
        scores["clarity_score"] = 70.0 if audio_ok else 30.0

        # Platform fit
        platform = str(clip_data.get("platform", "tiktok")).lower()
        duration = float(clip_data.get("duration_seconds", 30))
        platform_rules_data = self._data.get("platform_rules", {})
        pr = platform_rules_data.get(platform, {})
        fit = 50.0
        if pr:
            min_d = pr.get("min_duration_s", 5)
            max_d = pr.get("max_duration_s", 90)
            tgt = pr.get("target_duration_s", 30)
            if min_d <= duration <= max_d:
                fit += 20
            if abs(duration - tgt) <= 10:
                fit += 20
        scores["platform_fit_score"] = round(min(fit, 90), 1)

        # Visual energy
        has_face = bool(clip_data.get("has_face", False))
        scores["visual_energy_score"] = 60.0 if has_face else 40.0

        # Audio energy
        scores["audio_energy_score"] = 65.0 if audio_ok else 25.0

        # Controversy — contrarian keywords
        controversy_keywords = ["wrong", "actually", "myth", "nobody tells", "stop doing", "unpopular"]
        controversy_hits = sum(1 for kw in controversy_keywords if kw in transcript)
        scores["controversy_score"] = round(min(20 + controversy_hits * 15, 80), 1)

        # Educational value — instruction keywords
        edu_keywords = ["how to", "step", "here's why", "the reason", "tip", "trick", "learn"]
        edu_hits = sum(1 for kw in edu_keywords if kw in transcript)
        scores["educational_value_score"] = round(min(20 + edu_hits * 12, 80), 1)

        # Share/comment
        share_keywords = ["if you", "every time", "when you", "send this", "share this"]
        share_hits = sum(1 for kw in share_keywords if kw in transcript)
        scores["share_comment_score"] = round(min(20 + share_hits * 15, 75), 1)

        # Render readiness
        render_ok = audio_ok and duration >= 8
        scores["render_readiness_score"] = 80.0 if render_ok else 30.0

        # Commercial value
        commercial_keywords = ["buy", "sign up", "join", "enroll", "book", "free", "discount", "offer"]
        commercial_hits = sum(1 for kw in commercial_keywords if kw in transcript)
        scores["commercial_value_score"] = round(min(20 + commercial_hits * 12, 70), 1)

        # Virality score
        virality = 0.0
        for component, w in weights.items():
            virality += scores.get(component, 50.0) * w

        # Confidence: how much signal did we actually have?
        signal_count = sum([
            1 if clip_data.get("transcript") else 0,
            1 if clip_data.get("audio_ok") is not None else 0,
            1 if clip_data.get("duration_seconds") else 0,
            1 if clip_data.get("has_face") is not None else 0,
            1 if clip_data.get("platform") else 0,
        ])
        confidence = round(min(signal_count / 5.0, 1.0), 2)

        return {
            "virality_score": round(virality, 1),
            "confidence_score": confidence,
            "component_scores": scores,
            "platform": platform,
            "render_recommended": scores.get("render_readiness_score", 0) >= 60,
        }

    # ------------------------------------------------------------------
    # Risk checking
    # ------------------------------------------------------------------

    def risk_check(self, clip_data: Dict) -> List[Dict]:
        """
        Check clip data against risk rules. Returns list of triggered risks.
        """
        text = (
            str(clip_data.get("transcript", "")).lower() + " " +
            str(clip_data.get("hook", "")).lower() + " " +
            str(clip_data.get("caption", "")).lower()
        )
        category = str(clip_data.get("category", "")).lower()
        triggered: List[Dict] = []

        for rule in self._data.get("risk_rules", []):
            hit = False
            for kw in rule.get("detection_keywords", []):
                if kw.lower() in text:
                    hit = True
                    break
            if not hit:
                for cat in rule.get("detection_categories", []):
                    if cat == category:
                        hit = True
                        break
            if hit:
                triggered.append({
                    "rule_id": rule["id"],
                    "name": rule["name"],
                    "severity": rule["severity"],
                    "action": rule["action"],
                    "disclaimer": rule.get("disclaimer"),
                })
        return triggered

    # ------------------------------------------------------------------
    # Event logging
    # ------------------------------------------------------------------

    def _jsonl_path(self, name: str) -> Path:
        return self._runtime_dir / f"{name}.jsonl"

    def _append_jsonl(self, filename: str, record: Dict) -> bool:
        try:
            path = self._jsonl_path(filename)
            with path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(record) + "\n")
            return True
        except OSError as exc:
            logger.warning("intelligence_data_core: append_jsonl failed: %s", exc)
            return False

    def append_event(self, event: Dict) -> bool:
        """Append a general event to the events log."""
        record = {"ts": time.time(), "type": "event", **event}
        return self._append_jsonl("events", record)

    def append_feedback(self, clip_id: str, feedback: Dict) -> bool:
        """Append feedback for a specific clip."""
        record = {"ts": time.time(), "clip_id": clip_id, "type": "feedback", **feedback}
        return self._append_jsonl("feedback", record)

    def feedback_summary(self, limit: int = 100) -> Dict[str, Any]:
        """Return a summary of recent feedback records."""
        records: List[Dict] = []
        path = self._jsonl_path("feedback")
        try:
            if path.exists():
                lines = path.read_text(encoding="utf-8").splitlines()
                for line in lines[-limit:]:
                    try:
                        records.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
        except OSError:
            pass

        total = len(records)
        positive = sum(1 for r in records if r.get("rating", 0) >= 4)
        return {
            "total_feedback_records": total,
            "positive_count": positive,
            "negative_count": total - positive,
            "recent_records": records[-10:],
        }

    def append_performance(self, clip_id: str, metrics: Dict) -> bool:
        """Append manual performance data for a clip."""
        record = {"ts": time.time(), "clip_id": clip_id, "type": "performance", **metrics}
        return self._append_jsonl("performance", record)

    def performance_for_clip(self, clip_id: str) -> List[Dict]:
        """Return all performance records for a given clip_id."""
        records: List[Dict] = []
        path = self._jsonl_path("performance")
        try:
            if path.exists():
                for line in path.read_text(encoding="utf-8").splitlines():
                    try:
                        r = json.loads(line)
                        if r.get("clip_id") == clip_id:
                            records.append(r)
                    except json.JSONDecodeError:
                        pass
        except OSError:
            pass
        return records


# ---------------------------------------------------------------------------
# Singleton accessor
# ---------------------------------------------------------------------------

_core_instance: Optional[IntelligenceDataCore] = None


def get_intelligence_core() -> IntelligenceDataCore:
    """Return the shared IntelligenceDataCore instance (created on first call)."""
    global _core_instance
    if _core_instance is None:
        _core_instance = IntelligenceDataCore()
    return _core_instance
