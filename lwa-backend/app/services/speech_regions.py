from __future__ import annotations

from typing import Dict, List


def invert_silence_to_speech(
    silence_regions: List[Dict],
    video_duration: float,
    *,
    min_speech_duration: float = 1.2,
) -> List[Dict]:
    speech_regions: List[Dict] = []
    cursor = 0.0

    for region in sorted(silence_regions, key=lambda item: float(item.get("start_time", 0.0))):
        start = max(float(region.get("start_time", 0.0)), 0.0)
        end = max(float(region.get("end_time", start)), start)

        if start - cursor >= min_speech_duration:
            speech_regions.append(
                {
                    "type": "speech",
                    "region_type": "speech",
                    "start_time": round(cursor, 2),
                    "end_time": round(start, 2),
                    "duration": round(start - cursor, 2),
                }
            )

        cursor = max(cursor, end)

    if video_duration - cursor >= min_speech_duration:
        speech_regions.append(
            {
                "type": "speech",
                "region_type": "speech",
                "start_time": round(cursor, 2),
                "end_time": round(float(video_duration), 2),
                "duration": round(float(video_duration) - cursor, 2),
            }
        )

    return speech_regions
