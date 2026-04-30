from __future__ import annotations

CAPTION_PRESET_CODES: tuple[str, ...] = (
    "crimson_pulse",
    "clean_op",
    "karaoke_neon",
    "signal_low",
    "bigframe",
    "soft_safe",
    "dev_brutal",
)


def list_caption_presets() -> list[dict[str, str]]:
    return [{"code": code} for code in CAPTION_PRESET_CODES]


def normalize_caption_preset(code: str | None) -> str:
    normalized = (code or "clean_op").strip().lower().replace("-", "_")
    return normalized if normalized in CAPTION_PRESET_CODES else "clean_op"
