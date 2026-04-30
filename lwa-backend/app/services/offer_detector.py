from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OfferDetectorResult:
    offer_fit_score: int
    signals: list[str]
    recommended_angle: str
    reason: str


OFFER_SIGNAL_TERMS: dict[str, tuple[str, ...]] = {
    "problem": ("problem", "struggle", "mistake", "pain", "stuck", "broken"),
    "result": ("result", "after", "changed", "grew", "saved", "improved"),
    "proof": ("proof", "case study", "example", "testimonial", "before"),
    "objection": ("but", "expensive", "hard", "too late", "wont work", "does not work"),
    "offer": ("book", "demo", "call", "join", "download", "try", "upgrade"),
    "authority": ("framework", "method", "system", "process", "operator"),
}


def clamp_score(value: int) -> int:
    return max(0, min(100, int(value)))


def detect_offer_signals(text: str) -> list[str]:
    lowered = text.lower()
    signals: list[str] = []
    for signal, terms in OFFER_SIGNAL_TERMS.items():
        if any(term in lowered for term in terms):
            signals.append(signal)
    return signals


def recommend_offer_angle(signals: list[str]) -> str:
    if "problem" in signals and "offer" in signals:
        return "pain_point_to_action"
    if "proof" in signals or "result" in signals:
        return "proof_or_transformation"
    if "objection" in signals:
        return "objection_handling"
    if "authority" in signals:
        return "authority_framework"
    return "awareness_clip"


def detect_offer_fit(*, transcript: str, creator_type: str | None = None, offer: str | None = None) -> OfferDetectorResult:
    signals = detect_offer_signals(transcript)
    score = 35 + len(signals) * 10
    if creator_type:
        score += 5
    if offer:
        score += 10
    angle = recommend_offer_angle(signals)
    return OfferDetectorResult(
        offer_fit_score=clamp_score(score),
        signals=signals,
        recommended_angle=angle,
        reason="Offer fit is based on problem, proof, objection, authority, and action signals.",
    )


def offer_fit_dict(**kwargs: object) -> dict[str, object]:
    result = detect_offer_fit(
        transcript=str(kwargs.get("transcript") or ""),
        creator_type=str(kwargs.get("creator_type") or "") if kwargs.get("creator_type") is not None else None,
        offer=str(kwargs.get("offer") or "") if kwargs.get("offer") is not None else None,
    )
    return result.__dict__.copy()
