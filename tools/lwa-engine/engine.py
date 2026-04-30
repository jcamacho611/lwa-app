#!/usr/bin/env python3
"""Standalone LWA content extraction prototype.

This tool intentionally lives outside the production backend/web runtime.
It accepts a public video URL, reads source metadata with yt-dlp, and asks
Claude for short-form clipping ideas, hooks, captions, titles, and strategy.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from typing import Any


DEFAULT_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-latest")


@dataclass(frozen=True)
class VideoMetadata:
    url: str
    title: str
    description: str
    duration: int | None
    uploader: str
    webpage_url: str
    raw: dict[str, Any]


def require_yt_dlp() -> None:
    if shutil.which("yt-dlp") is None:
        raise RuntimeError("yt-dlp is not installed or not on PATH. Install it with: pip install yt-dlp")


def load_metadata(url: str) -> VideoMetadata:
    require_yt_dlp()
    command = ["yt-dlp", "--dump-json", "--no-playlist", url]
    try:
        completed = subprocess.run(command, check=True, capture_output=True, text=True, timeout=45)
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("yt-dlp timed out while reading metadata.") from exc
    except subprocess.CalledProcessError as exc:
        message = exc.stderr.strip() or exc.stdout.strip() or "yt-dlp failed to read metadata."
        raise RuntimeError(message) from exc

    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("yt-dlp returned invalid JSON metadata.") from exc

    return VideoMetadata(
        url=url,
        title=str(payload.get("title") or "Untitled source"),
        description=str(payload.get("description") or ""),
        duration=payload.get("duration") if isinstance(payload.get("duration"), int) else None,
        uploader=str(payload.get("uploader") or payload.get("channel") or "Unknown"),
        webpage_url=str(payload.get("webpage_url") or url),
        raw=payload,
    )


def build_prompt(metadata: VideoMetadata) -> str:
    duration = f"{metadata.duration} seconds" if metadata.duration else "unknown duration"
    description = metadata.description[:3500]
    return f"""
You are LWA's prototype clipping strategist.

Given source metadata only, infer the strongest short-form opportunities.
If transcript is missing, say the ideas are inferred from metadata and keep them honest.
Do not guarantee views, virality, revenue, or platform approval.

Source URL: {metadata.webpage_url}
Title: {metadata.title}
Uploader: {metadata.uploader}
Duration: {duration}
Description:
{description}

Return markdown with these exact sections:

## Source Read
Briefly explain what the source likely contains and the uncertainty level.

## 5 Hooks
Give 5 short, punchy hooks.

## 5 Short-Form Clip Ideas
For each: clip idea, likely moment, target platform, recommended length, why it could work.

## Platform Captions
Give captions for TikTok, Instagram Reels, and YouTube Shorts.

## 5 Titles
Give 5 short titles.

## Posting Strategy
Give a short posting strategy with post order and caution notes.
""".strip()


def call_claude(prompt: str) -> str:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is missing. Export it before running this prototype.")

    try:
        import anthropic  # type: ignore
    except ImportError as exc:
        raise RuntimeError("anthropic is not installed. Install it with: pip install anthropic") from exc

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model=DEFAULT_MODEL,
        max_tokens=1800,
        temperature=0.7,
        messages=[{"role": "user", "content": prompt}],
    )

    parts: list[str] = []
    for block in message.content:
        text = getattr(block, "text", None)
        if text:
            parts.append(text)
    return "\n".join(parts).strip()


def run(url: str) -> str:
    metadata = load_metadata(url)
    prompt = build_prompt(metadata)
    return call_claude(prompt)


def main() -> int:
    print("LWA Engine Prototype")
    print("Paste a public video URL and press Enter.")
    url = input("URL: ").strip()
    if not url:
        print("No URL provided.", file=sys.stderr)
        return 2

    try:
        result = run(url)
    except Exception as exc:  # intentionally broad for terminal prototype ergonomics
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print("\n" + result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
