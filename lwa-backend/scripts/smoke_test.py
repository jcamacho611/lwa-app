#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.request


def read_json(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=20) as response:
        return json.loads(response.read().decode())


def post_json(url: str, payload: dict) -> dict:
    body = json.dumps(payload).encode()
    request = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode())


def main() -> int:
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"
    video_url = sys.argv[2] if len(sys.argv) > 2 else "https://www.w3schools.com/html/mov_bbb.mp4"
    base_url = base_url.rstrip("/")

    try:
        health = read_json(f"{base_url}/health")
        print("health:", json.dumps(health, indent=2))

        created = post_json(
            f"{base_url}/v1/jobs",
            {"video_url": video_url, "target_platform": "TikTok"},
        )
        print("job created:", json.dumps(created, indent=2))

        job_id = created["job_id"]
        deadline = time.time() + 180
        while time.time() < deadline:
            status = read_json(f"{base_url}/v1/jobs/{job_id}")
            print("job status:", status["status"], "-", status["message"])
            if status["status"] == "completed":
                result = status["result"]
                print("result summary:", json.dumps(result["processing_summary"], indent=2))
                if result["clips"]:
                    print("first clip asset:", result["clips"][0].get("clip_url"))
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
