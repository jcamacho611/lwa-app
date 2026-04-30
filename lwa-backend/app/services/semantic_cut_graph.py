from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# LWA OMEGA
# CLAUDE HANDOFF
# UPLOAD-FIRST CLIPPING ENGINE
# LOCAL-FIRST FALLBACK
# NONFATAL PIPELINE
# SEMANTIC CUT GRAPH

FILLER_TERMS = {"um", "uh", "like", "you know", "basically", "actually"}
HOOK_TERMS = {"secret", "mistake", "stop", "why", "how", "money", "never", "truth"}


@dataclass(frozen=True)
class SemanticCut:
    start_seconds: float
    end_seconds: float
    role: str
    score: int
    reason: str


def _text_score(text: str) -> int:
    lower = text.lower()
    score = 50
    score += sum(8 for term in HOOK_TERMS if term in lower)
    score -= sum(5 for term in FILLER_TERMS if term in lower)
    if "?" in text:
        score += 6
    if any(char.isdigit() for char in text):
        score += 5
    return max(0, min(100, score))


def build_semantic_cut_graph(transcript_segments: list[dict[str, Any]]) -> list[SemanticCut]:
    cuts: list[SemanticCut] = []
    for index, segment in enumerate(transcript_segments):
        text = str(segment.get("text") or segment.get("caption") or "").strip()
        start = float(segment.get("start_seconds") or segment.get("start") or index * 15)
        end = float(segment.get("end_seconds") or segment.get("end") or start + 15)
        if end <= start:
            continue
        score = _text_score(text)
        role = "hook" if score >= 70 and index <= 2 else "payoff" if index == len(transcript_segments) - 1 else "proof"
        cuts.append(
            SemanticCut(
                start_seconds=round(start, 2),
                end_seconds=round(end, 2),
                role=role,
                score=score,
                reason="Semantic score based on hook terms, filler density, questions, and numeric specificity.",
            )
        )
    return sorted(cuts, key=lambda cut: cut.score, reverse=True)


def semantic_overrides(transcript_segments: list[dict[str, Any]], limit: int = 5) -> list[dict[str, Any]]:
    return [cut.__dict__ for cut in build_semantic_cut_graph(transcript_segments)[:limit]]
