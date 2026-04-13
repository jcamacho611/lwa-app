#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
import uuid


CLIENT_ID_HEADER = "x-lwa-client-id"
API_KEY_HEADER = "x-api-key"


def default_headers() -> dict[str, str]:
    headers = {
        CLIENT_ID_HEADER: os.getenv("LWA_SMOKE_CLIENT_ID", f"smoke-{uuid.uuid4().hex[:12]}"),
    }
    api_key = os.getenv("LWA_SMOKE_API_KEY", "").strip()
    if api_key:
        headers[API_KEY_HEADER] = api_key
    return headers


def read_json(url: str, headers: dict[str, str] | None = None) -> dict:
    request = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode())


def post_json(url: str, payload: dict, headers: dict[str, str] | None = None) -> dict:
    body = json.dumps(payload).encode()
    request_headers = {"Content-Type": "application/json"}
    request_headers.update(headers or {})
    request = urllib.request.Request(url, data=body, headers=request_headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode())


def main() -> int:
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"
    video_url = sys.argv[2] if len(sys.argv) > 2 else "https://www.w3schools.com/html/mov_bbb.mp4"
    base_url = base_url.rstrip("/")
    headers = default_headers()

    try:
        health = read_json(f"{base_url}/health", headers=headers)
        print("health:", json.dumps(health, indent=2))
        if health.get("status") != "ok":
            print("health check did not return ok")
            return 1
        dependencies = health.get("dependencies", {})
        if not dependencies.get("ffmpeg") or not dependencies.get("yt_dlp"):
            print("required runtime dependencies are not available")
            return 1

        generated = post_json(
            f"{base_url}/generate",
            {"video_url": video_url, "target_platform": "TikTok"},
            headers=headers,
        )
        print("generate summary:", json.dumps(generated["processing_summary"], indent=2))
        if generated["processing_summary"].get("processing_mode") == "mock":
            print("generate endpoint fell back to mock mode")
            return 1
        if generated["processing_summary"].get("assets_created", 0) <= 0:
            print("generate endpoint produced no assets")
            return 1
        if not any(clip.get("clip_url") for clip in generated.get("clips", [])):
            print("generate endpoint returned no clip_url values")
            return 1
        first_generated_clip = next((clip for clip in generated.get("clips", []) if clip.get("clip_url")), None)
        if first_generated_clip:
            print("generate first clip asset:", first_generated_clip.get("clip_url"))

        created = post_json(
            f"{base_url}/v1/jobs",
            {"video_url": video_url, "target_platform": "TikTok"},
            headers=headers,
        )
        print("job created:", json.dumps(created, indent=2))

        job_id = created["job_id"]
        deadline = time.time() + 180
        while time.time() < deadline:
            status = read_json(f"{base_url}/v1/jobs/{job_id}", headers=headers)
            print("job status:", status["status"], "-", status["message"])
            if status["status"] == "completed":
                result = status["result"]
                print("result summary:", json.dumps(result["processing_summary"], indent=2))
                if result["clips"]:
                    print("first clip asset:", result["clips"][0].get("clip_url"))
                if result["processing_summary"].get("processing_mode") == "mock":
                    print("job endpoint fell back to mock mode")
                    return 1
                if result["processing_summary"].get("assets_created", 0) <= 0:
                    print("job endpoint produced no assets")
                    return 1
                return 0
            if status["status"] == "failed":
                print("job failed:", json.dumps(status, indent=2))
                return 1
            time.sleep(1.5)

        print("job timed out")
        return 1
    except urllib.error.HTTPError as error:
        body = error.read().decode()
        print(f"http error {error.code}: {body}")
        return 1
    except Exception as error:  # pragma: no cover
        print(f"error: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
