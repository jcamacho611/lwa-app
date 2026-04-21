from typing import List, Dict


def trim_silence_windows(segments: List[Dict], max_silence_gap: float = 0.8) -> List[Dict]:
    """
    Lightweight silence-aware cleanup using transcript/audio segment gaps.
    Expects segments shaped like:
    { "start": float, "end": float, "text": str, "energy": float|None }
    """
    if not segments:
        return []

    cleaned = [segments[0]]

    for seg in segments[1:]:
        prev = cleaned[-1]
        gap = max(0.0, float(seg.get("start", 0)) - float(prev.get("end", 0)))

        # If silence gap is too large, keep as new beat.
        if gap > max_silence_gap:
            cleaned.append(seg)
            continue

        # Merge tiny-gap segments to tighten pacing.
        merged = {
            "start": prev.get("start", 0),
            "end": seg.get("end", prev.get("end", 0)),
            "text": f'{prev.get("text", "").strip()} {seg.get("text", "").strip()}'.strip(),
            "energy": max(float(prev.get("energy", 0) or 0), float(seg.get("energy", 0) or 0)),
        }
        cleaned[-1] = merged

    return cleaned