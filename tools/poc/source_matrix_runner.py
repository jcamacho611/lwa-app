#!/usr/bin/env python3
"""
LWA Source POC Matrix Runner

Purpose:
Prove which source types actually work end-to-end today.

This script tests:
- local media upload acceptance
- generate acceptance
- source_type returned by the backend
- rendered/playable URL presence when rendering is expected
- public URL blocked fallback behavior
- prompt-only behavior
- music and campaign strategy-only behavior
- unsupported public URL fallback behavior

It writes:
- poc/source-matrix-results.json
- poc/source-matrix-results.md

Run against a local backend:
  python3 tools/poc/source_matrix_runner.py --base-url http://127.0.0.1:8000

Required:
- backend running
- ffmpeg installed for media fixtures
- Python stdlib only
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import shutil
import subprocess
import time
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen


REPO_ROOT = Path(__file__).resolve().parents[2]
POC_DIR = REPO_ROOT / "poc"
FIXTURE_DIR = POC_DIR / "fixtures"
RESULT_JSON = POC_DIR / "source-matrix-results.json"
RESULT_MD = POC_DIR / "source-matrix-results.md"

MEDIA_URL_FIELDS = [
    "edited_clip_url",
    "clip_url",
    "raw_clip_url",
    "preview_url",
    "download_url",
]

DEFAULT_TIMEOUT_SECONDS = 180

PLATFORM_BLOCKED_EXPECTED_MESSAGE = (
    "This platform blocked server access. Upload the video/audio file directly, "
    "try another public source, or use prompt mode."
)

RAW_ERROR_MARKERS = [
    "yt-dlp",
    "--cookies",
    "cookies-from-browser",
    "sign in to confirm",
    "github.com/yt-dlp",
    "not a bot",
]


@dataclass
class MatrixCase:
    id: str
    label: str
    kind: str
    expected_mode: str
    expected_source_types: list[str] = field(default_factory=list)
    path: str | None = None
    prompt: str | None = None
    public_url: str | None = None
    content_type: str | None = None
    should_render: bool = False
    should_clean_fail: bool = False
    expected_fallback_message: str | None = None
    enabled: bool = True


@dataclass
class MatrixResult:
    id: str
    label: str
    kind: str
    expected_mode: str
    expected_source_types: list[str]
    upload_attempted: bool = False
    upload_accepted: bool = False
    upload_file_id: str | None = None
    upload_content_type: str | None = None
    upload_source_type: str | None = None
    generate_attempted: bool = False
    generate_accepted: bool = False
    status: str | None = None
    request_id: str | None = None
    returned_source_type: str | None = None
    source_type_ok: bool = False
    rendered_url_count: int = 0
    playable_url_count: int = 0
    rendered_urls: list[str] = field(default_factory=list)
    rendered_url_checks: list[dict[str, Any]] = field(default_factory=list)
    clip_count: int = 0
    rendered_clip_count: int = 0
    strategy_only_clip_count: int = 0
    clean_fallback: bool = False
    fallback_code: str | None = None
    fallback_message: str | None = None
    raw_error_leaked: bool = False
    http_status: int | None = None
    error: str | None = None
    passed: bool = False
    skipped: bool = False
    notes: list[str] = field(default_factory=list)


def run_command(command: list[str], timeout: int = DEFAULT_TIMEOUT_SECONDS) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=str(REPO_ROOT),
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )


def require_binary(name: str) -> bool:
    return shutil.which(name) is not None


def create_with_fallback(commands: list[list[str]], output_path: Path) -> bool:
    if output_path.exists():
        return True

    for command in commands:
        result = run_command(command)
        if result.returncode == 0 and output_path.exists() and output_path.stat().st_size > 0:
            return True

    return False


def create_video_fixture(output_path: Path, extension: str) -> bool:
    if not require_binary("ffmpeg"):
        return False

    common_input = [
        "ffmpeg",
        "-y",
        "-f",
        "lavfi",
        "-i",
        "testsrc=size=720x1280:rate=30:duration=10",
        "-f",
        "lavfi",
        "-i",
        "sine=frequency=1000:duration=10",
        "-shortest",
        "-pix_fmt",
        "yuv420p",
    ]

    if extension == "webm":
        return create_with_fallback(
            [
                common_input + ["-c:v", "libvpx-vp9", "-c:a", "libopus", str(output_path)],
                common_input + ["-c:v", "libvpx", "-c:a", "libvorbis", str(output_path)],
            ],
            output_path,
        )

    return create_with_fallback(
        [
            common_input + ["-c:v", "libx264", "-c:a", "aac", "-movflags", "+faststart", str(output_path)],
            common_input + [str(output_path)],
        ],
        output_path,
    )


def create_audio_fixture(output_path: Path, extension: str) -> bool:
    if not require_binary("ffmpeg"):
        return False

    if extension == "mp3":
        commands = [
            [
                "ffmpeg",
                "-y",
                "-f",
                "lavfi",
                "-i",
                "sine=frequency=1000:duration=10",
                "-c:a",
                "libmp3lame",
                str(output_path),
            ],
            [
                "ffmpeg",
                "-y",
                "-f",
                "lavfi",
                "-i",
                "sine=frequency=1000:duration=10",
                str(output_path),
            ],
        ]
    elif extension == "m4a":
        commands = [
            [
                "ffmpeg",
                "-y",
                "-f",
                "lavfi",
                "-i",
                "sine=frequency=1000:duration=10",
                "-c:a",
                "aac",
                str(output_path),
            ],
            [
                "ffmpeg",
                "-y",
                "-f",
                "lavfi",
                "-i",
                "sine=frequency=1000:duration=10",
                str(output_path),
            ],
        ]
    else:
        commands = [
            [
                "ffmpeg",
                "-y",
                "-f",
                "lavfi",
                "-i",
                "sine=frequency=1000:duration=10",
                str(output_path),
            ]
        ]

    return create_with_fallback(commands, output_path)


def create_image_fixture(output_path: Path, extension: str) -> bool:
    if require_binary("ffmpeg"):
        if create_with_fallback(
            [
                [
                    "ffmpeg",
                    "-y",
                    "-f",
                    "lavfi",
                    "-i",
                    "color=c=blue:s=720x1280:d=1",
                    "-frames:v",
                    "1",
                    str(output_path),
                ]
            ],
            output_path,
        ):
            return True

    if extension == "png" and not output_path.exists():
        output_path.write_bytes(
            bytes.fromhex(
                "89504e470d0a1a0a0000000d4948445200000001000000010802000000907753de"
                "0000000c49444154789c6360f8ffff3f0005fe02fea73581e80000000049454e44ae426082"
            )
        )
        return True

    if extension in {"jpg", "jpeg"} and not output_path.exists():
        output_path.write_bytes(
            bytes.fromhex(
                "ffd8ffe000104a46494600010101006000600000ffdb004300030202030202030303030403030405"
                "0805050404050a070706080c0a0c0c0b0a0b0b0d0e12100d0e110e0b0b101610111314151515"
                "0c0f171816141812141514ffc0000b080001000101011100ffc400140001000000000000000000"
                "0000000000000000008ffc4001410010000000000000000000000000000000000000000ffda"
                "0008010100003f00d2cf20ffd9"
            )
        )
        return True

    if extension == "webp" and not output_path.exists():
        output_path.write_bytes(
            bytes.fromhex(
                "52494646220000005745425056503820160000003001009d012a010001000ec0fe25a400037000000000"
            )
        )
        return True

    return output_path.exists() and output_path.stat().st_size > 0


def create_heif_fixture(source_png: Path, output_path: Path) -> bool:
    if output_path.exists():
        return True

    if require_binary("sips") and source_png.exists():
        result = run_command(["sips", "-s", "format", "heic", str(source_png), "--out", str(output_path)], timeout=60)
        if result.returncode == 0 and output_path.exists() and output_path.stat().st_size > 0:
            return True

    return False


def make_fixtures() -> dict[str, Path]:
    """
    Generate deterministic tiny fixtures.

    The goal is contract proof, not media quality.
    """
    FIXTURE_DIR.mkdir(parents=True, exist_ok=True)

    fixtures: dict[str, Path] = {}

    for extension in ["mp4", "mov", "m4v", "webm"]:
        path = FIXTURE_DIR / f"poc-video-10s.{extension}"
        if create_video_fixture(path, extension):
            fixtures[extension] = path

    for extension in ["mp3", "wav", "m4a"]:
        path = FIXTURE_DIR / f"poc-audio-10s.{extension}"
        if create_audio_fixture(path, extension):
            fixtures[extension] = path

    for extension in ["jpg", "png", "webp"]:
        path = FIXTURE_DIR / f"poc-image.{extension}"
        if create_image_fixture(path, extension):
            fixtures[extension] = path

    png = fixtures.get("png") or FIXTURE_DIR / "poc-image.png"
    for extension in ["heic", "heif"]:
        path = FIXTURE_DIR / f"poc-image.{extension}"
        if create_heif_fixture(png, path):
            fixtures[extension] = path

    return fixtures


def guess_content_type(path: Path) -> str:
    guessed, _ = mimetypes.guess_type(str(path))
    if guessed:
        return guessed

    suffix = path.suffix.lower()
    return {
        ".mp4": "video/mp4",
        ".mov": "video/quicktime",
        ".m4v": "video/x-m4v",
        ".webm": "video/webm",
        ".mp3": "audio/mpeg",
        ".wav": "audio/wav",
        ".m4a": "audio/mp4",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
        ".heic": "image/heic",
        ".heif": "image/heif",
    }.get(suffix, "application/octet-stream")


def http_json_request(
    url: str,
    method: str = "GET",
    body: Any | None = None,
    headers: dict[str, str] | None = None,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
) -> tuple[int, Any]:
    headers = headers or {}
    data_bytes: bytes | None = None

    if body is not None:
        data_bytes = json.dumps(body).encode("utf-8")
        headers = {"Content-Type": "application/json", **headers}

    request = Request(url, data=data_bytes, headers=headers, method=method)

    try:
        with urlopen(request, timeout=timeout) as response:
            response_body = response.read().decode("utf-8", errors="replace")
            parsed = json.loads(response_body) if response_body else {}
            return response.status, parsed
    except HTTPError as error:
        response_body = error.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(response_body) if response_body else {}
        except json.JSONDecodeError:
            parsed = {"message": response_body}
        return error.code, parsed
    except URLError as error:
        return 0, {"message": str(error)}


def upload_file(base_url: str, file_path: Path, client_id: str) -> tuple[int, Any]:
    boundary = f"----LWAProofBoundary{uuid.uuid4().hex}"
    content_type = guess_content_type(file_path)
    file_bytes = file_path.read_bytes()

    body = b"".join(
        [
            f"--{boundary}\r\n".encode(),
            (
                f'Content-Disposition: form-data; name="file"; filename="{file_path.name}"\r\n'
                f"Content-Type: {content_type}\r\n\r\n"
            ).encode(),
            file_bytes,
            b"\r\n",
            f"--{boundary}--\r\n".encode(),
        ]
    )

    request = Request(
        f"{base_url.rstrip('/')}/v1/uploads",
        data=body,
        method="POST",
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Content-Length": str(len(body)),
            "x-lwa-client-id": client_id,
        },
    )

    try:
        with urlopen(request, timeout=DEFAULT_TIMEOUT_SECONDS) as response:
            response_body = response.read().decode("utf-8", errors="replace")
            parsed = json.loads(response_body) if response_body else {}
            return response.status, parsed
    except HTTPError as error:
        response_body = error.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(response_body) if response_body else {}
        except json.JSONDecodeError:
            parsed = {"message": response_body}
        return error.code, parsed
    except URLError as error:
        return 0, {"message": str(error)}


def extract_error_message(payload: Any) -> str:
    if payload is None:
        return ""
    if isinstance(payload, str):
        return payload
    if isinstance(payload, list):
        return " ".join(extract_error_message(item) for item in payload)
    if isinstance(payload, dict):
        direct = payload.get("user_message") or payload.get("message") or payload.get("error") or payload.get("detail")
        if direct is not None and direct is not payload:
            return extract_error_message(direct)
        return " ".join(extract_error_message(value) for value in payload.values())
    return str(payload)


def raw_error_leaked(message: str) -> bool:
    lower = message.lower()
    return any(marker in lower for marker in RAW_ERROR_MARKERS)


def collect_media_urls(payload: Any) -> list[str]:
    urls: list[str] = []

    if not isinstance(payload, dict):
        return urls

    for top_level in ["preview_asset_url", "download_asset_url", "thumbnail_url"]:
        value = payload.get(top_level)
        if isinstance(value, str) and value.startswith(("http://", "https://", "/")):
            urls.append(value)

    clips = payload.get("clips") or []
    if isinstance(clips, list):
        for clip in clips:
            if not isinstance(clip, dict):
                continue
            for field_name in MEDIA_URL_FIELDS:
                value = clip.get(field_name)
                if isinstance(value, str) and value.startswith(("http://", "https://", "/")):
                    urls.append(value)

    return sorted(set(urls))


def count_rendered_clips(payload: Any) -> int:
    if not isinstance(payload, dict):
        return 0

    clips = payload.get("clips") or []
    if not isinstance(clips, list):
        return 0

    count = 0
    for clip in clips:
        if not isinstance(clip, dict):
            continue
        if any(isinstance(clip.get(field), str) and clip.get(field) for field in MEDIA_URL_FIELDS):
            count += 1
    return count


def absolute_url(base_url: str, candidate: str) -> str:
    if candidate.startswith(("http://", "https://")):
        return candidate
    return urljoin(f"{base_url.rstrip('/')}/", candidate.lstrip("/"))


def probe_rendered_url(base_url: str, candidate: str) -> dict[str, Any]:
    url = absolute_url(base_url, candidate)
    result: dict[str, Any] = {
        "url": candidate,
        "absolute_url": url,
        "http_status": None,
        "content_type": None,
        "content_length": None,
        "playable": False,
        "error": None,
    }

    try:
        request = Request(url, method="HEAD")
        with urlopen(request, timeout=30) as response:
            result["http_status"] = response.status
            result["content_type"] = response.headers.get("Content-Type")
            result["content_length"] = response.headers.get("Content-Length")
    except HTTPError as error:
        if error.code not in {405, 501}:
            result["http_status"] = error.code
            result["error"] = extract_error_message(error.read().decode("utf-8", errors="replace"))
            return result

        try:
            request = Request(url, headers={"Range": "bytes=0-0"}, method="GET")
            with urlopen(request, timeout=30) as response:
                result["http_status"] = response.status
                result["content_type"] = response.headers.get("Content-Type")
                result["content_length"] = response.headers.get("Content-Length")
        except Exception as fallback_error:
            result["error"] = str(fallback_error)
            return result
    except Exception as error:
        result["error"] = str(error)
        return result

    status = int(result["http_status"] or 0)
    content_type = str(result["content_type"] or "").lower()
    lower_url = url.lower()
    media_extension = lower_url.endswith((".mp4", ".mov", ".m4v", ".webm", ".mp3", ".wav", ".m4a"))
    result["playable"] = 200 <= status < 400 and (
        content_type.startswith("video/")
        or content_type.startswith("audio/")
        or media_extension
    )
    return result


def source_type_matches(returned: str | None, expected: list[str]) -> bool:
    if not expected:
        return True
    return (returned or "").strip().lower() in {value.strip().lower() for value in expected}


def build_cases(
    fixtures: dict[str, Path],
    youtube_url: str | None,
    twitch_url: str | None,
    unsupported_url: str | None,
) -> list[MatrixCase]:
    cases: list[MatrixCase] = []

    def add_fixture_case(
        extension: str,
        label: str,
        expected_mode: str,
        expected_source_types: list[str],
        should_render: bool,
    ) -> None:
        path = fixtures.get(extension)
        if not path:
            cases.append(
                MatrixCase(
                    id=f"upload_{extension}",
                    label=label,
                    kind="missing_fixture",
                    expected_mode=expected_mode,
                    expected_source_types=expected_source_types,
                    enabled=False,
                )
            )
            return

        cases.append(
            MatrixCase(
                id=f"upload_{extension}",
                label=label,
                kind="upload",
                expected_mode=expected_mode,
                expected_source_types=expected_source_types,
                path=str(path),
                content_type=guess_content_type(path),
                should_render=should_render,
            )
        )

    for extension, label in [
        ("mp4", "MP4 video upload"),
        ("mov", "MOV video upload"),
        ("m4v", "M4V video upload"),
        ("webm", "WEBM video upload"),
    ]:
        add_fixture_case(extension, label, "video", ["video_upload"], should_render=True)

    for extension, label in [
        ("mp3", "MP3 audio upload"),
        ("wav", "WAV audio upload"),
        ("m4a", "M4A audio upload"),
    ]:
        add_fixture_case(extension, label, "audio", ["audio_upload"], should_render=False)

    for extension, label in [
        ("jpg", "JPG image upload"),
        ("png", "PNG image upload"),
        ("webp", "WEBP image upload"),
        ("heic", "HEIC image upload"),
        ("heif", "HEIF image upload"),
    ]:
        add_fixture_case(extension, label, "image", ["image_upload"], should_render=False)

    cases.append(
        MatrixCase(
            id="prompt_only",
            label="Prompt-only idea generation",
            kind="prompt",
            expected_mode="idea",
            expected_source_types=["prompt", "idea"],
            prompt=(
                "Create three viral short-form clips for a creator explaining why upload-first "
                "clipping is more reliable than public link extraction."
            ),
            should_render=False,
        )
    )

    cases.append(
        MatrixCase(
            id="music_prompt",
            label="Music idea strategy package",
            kind="music",
            expected_mode="music",
            expected_source_types=["music"],
            prompt=(
                "Package this chorus idea into a short-form teaser with safe non-lyrical promo copy, "
                "thumbnail text, captions, and visual direction."
            ),
            should_render=False,
        )
    )

    cases.append(
        MatrixCase(
            id="campaign_objective",
            label="Campaign objective strategy package",
            kind="campaign",
            expected_mode="campaign",
            expected_source_types=["campaign"],
            prompt=(
                "Prepare a campaign-ready clip package for a creator selling an upload-first clipping workflow "
                "to streamers and agencies."
            ),
            should_render=False,
        )
    )

    if youtube_url:
        cases.append(
            MatrixCase(
                id="youtube_public_url",
                label="Public YouTube URL best-effort fallback",
                kind="public_url",
                expected_mode="url",
                expected_source_types=["url"],
                public_url=youtube_url,
                should_render=False,
                should_clean_fail=True,
                expected_fallback_message=PLATFORM_BLOCKED_EXPECTED_MESSAGE,
            )
        )

    if twitch_url:
        cases.append(
            MatrixCase(
                id="twitch_public_url",
                label="Public Twitch/stream URL best-effort fallback",
                kind="public_url",
                expected_mode="twitch",
                expected_source_types=["twitch", "stream", "url"],
                public_url=twitch_url,
                should_render=False,
                should_clean_fail=True,
            )
        )

    if unsupported_url:
        cases.append(
            MatrixCase(
                id="unsupported_public_url",
                label="Unsupported public URL fallback",
                kind="public_url",
                expected_mode="unsupported",
                expected_source_types=["url"],
                public_url=unsupported_url,
                should_render=False,
                should_clean_fail=True,
            )
        )

    return cases


def generate_payload_for_case(case: MatrixCase, upload_file_id: str | None = None) -> dict[str, Any]:
    if case.kind == "prompt":
        return {
            "prompt": case.prompt,
            "source_type": "prompt",
            "target_platform": "TikTok",
            "clip_count": 1,
            "content_angle": "POC prompt-only generation",
        }

    if case.kind == "music":
        return {
            "prompt": case.prompt,
            "source_type": "music",
            "target_platform": "TikTok",
            "clip_count": 1,
            "content_angle": "POC music strategy package",
        }

    if case.kind == "campaign":
        return {
            "source_type": "campaign",
            "campaign_goal": case.prompt,
            "campaign_brief": case.prompt,
            "allowed_platforms": ["TikTok", "YouTube Shorts", "Instagram Reels"],
            "target_platform": "TikTok",
            "clip_count": 1,
            "content_angle": "POC campaign objective package",
        }

    if case.kind == "public_url":
        return {
            "video_url": case.public_url,
            "source_url": case.public_url,
            "source_type": "twitch" if case.expected_mode == "twitch" else "url",
            "target_platform": "TikTok",
            "clip_count": 1,
            "content_angle": "POC public URL ingestion fallback",
        }

    return {
        "upload_file_id": upload_file_id,
        "target_platform": "TikTok",
        "clip_count": 1,
        "content_angle": f"POC source matrix test for {case.label}",
    }


def safe_client_id(value: str) -> str:
    safe = "".join(ch if ch.isalnum() or ch in {"_", "-"} else "_" for ch in value)
    return safe[:64]


def run_case(base_url: str, case: MatrixCase, client_id: str) -> MatrixResult:
    result = MatrixResult(
        id=case.id,
        label=case.label,
        kind=case.kind,
        expected_mode=case.expected_mode,
        expected_source_types=case.expected_source_types,
    )

    if not case.enabled:
        result.skipped = True
        result.notes.append("Case skipped because a fixture was unavailable in this environment.")
        return result

    upload_file_id: str | None = None

    if case.kind == "upload":
        result.upload_attempted = True
        if not case.path:
            result.error = "Upload case is missing path."
            return result
        upload_path = Path(case.path)

        upload_status, upload_payload = upload_file(base_url, upload_path, client_id)
        result.http_status = upload_status

        if 200 <= upload_status < 300:
            result.upload_accepted = True
            if isinstance(upload_payload, dict):
                upload_file_id = str(upload_payload.get("file_id") or "")
                result.upload_file_id = upload_file_id
                result.upload_content_type = str(upload_payload.get("content_type") or "")
                source_type_value = upload_payload.get("source_type")
                result.upload_source_type = str(source_type_value) if source_type_value else None
            if not upload_file_id:
                result.notes.append("Upload succeeded but did not return file_id.")
        else:
            result.error = extract_error_message(upload_payload)
            result.raw_error_leaked = raw_error_leaked(result.error)
            return result

    result.generate_attempted = True

    payload = generate_payload_for_case(case, upload_file_id)
    generate_status, generate_payload = http_json_request(
        f"{base_url.rstrip('/')}/v1/generate",
        method="POST",
        body=payload,
        headers={"x-lwa-client-id": client_id},
    )
    result.http_status = generate_status

    if 200 <= generate_status < 300 and isinstance(generate_payload, dict):
        result.generate_accepted = True
        result.status = str(generate_payload.get("status") or "")
        result.request_id = str(generate_payload.get("request_id") or "")
        result.returned_source_type = str(generate_payload.get("source_type") or "")
        result.source_type_ok = source_type_matches(result.returned_source_type, case.expected_source_types)

        raw_payload_text = extract_error_message(generate_payload)
        result.raw_error_leaked = raw_error_leaked(raw_payload_text)

        clips = generate_payload.get("clips") or []
        if isinstance(clips, list):
            result.clip_count = len(clips)
            result.rendered_clip_count = count_rendered_clips(generate_payload)
            result.strategy_only_clip_count = max(result.clip_count - result.rendered_clip_count, 0)

        result.rendered_urls = collect_media_urls(generate_payload)
        result.rendered_url_count = len(result.rendered_urls)
        result.rendered_url_checks = [probe_rendered_url(base_url, url) for url in result.rendered_urls]
        result.playable_url_count = len([check for check in result.rendered_url_checks if check.get("playable")])

        if not result.source_type_ok:
            result.notes.append(
                f"Expected source_type in {case.expected_source_types}, got {result.returned_source_type or 'missing'}."
            )
        if result.raw_error_leaked:
            result.notes.append("Raw backend/extractor error marker appeared in a successful response.")

        render_ok = True
        if case.should_render:
            render_ok = result.rendered_clip_count > 0 and result.playable_url_count > 0
            if not render_ok:
                result.notes.append("Expected rendered playable media URL but none was verified.")

        result.passed = result.generate_accepted and result.source_type_ok and render_ok and not result.raw_error_leaked
        return result

    message = extract_error_message(generate_payload)
    result.error = message
    result.raw_error_leaked = raw_error_leaked(message)

    if isinstance(generate_payload, dict):
        detail = generate_payload.get("detail")
        if isinstance(detail, dict):
            result.fallback_code = str(detail.get("code") or "")
            result.fallback_message = str(detail.get("user_message") or detail.get("message") or "")
        else:
            result.fallback_message = message

    result.clean_fallback = bool(result.fallback_message) and not result.raw_error_leaked

    if case.should_clean_fail:
        result.passed = result.clean_fallback
        if not result.passed:
            result.notes.append("Expected clean public URL fallback but raw error leaked or fallback was missing.")
        if (
            case.expected_fallback_message
            and result.fallback_message
            and result.fallback_message != case.expected_fallback_message
        ):
            result.notes.append("Fallback was clean but did not match the expected canonical message.")
    else:
        result.passed = False

    return result


def write_reports(
    *,
    results: list[MatrixResult],
    base_url: str,
    run_client_prefix: str,
    youtube_url: str | None,
    twitch_url: str | None,
    unsupported_url: str | None,
) -> None:
    POC_DIR.mkdir(parents=True, exist_ok=True)

    payload = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "base_url": base_url,
        "client_id_prefix": run_client_prefix,
        "youtube_url_tested": bool(youtube_url),
        "twitch_url_tested": bool(twitch_url),
        "unsupported_url_tested": bool(unsupported_url),
        "results": [asdict(result) for result in results],
    }
    RESULT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    passed = sum(1 for result in results if result.passed)
    failed = sum(1 for result in results if not result.passed and not result.skipped)
    skipped = sum(1 for result in results if result.skipped)

    lines: list[str] = []
    lines.append("# LWA Source POC Matrix Results")
    lines.append("")
    lines.append(f"Generated: {payload['generated_at']}")
    lines.append(f"Base URL: `{base_url}`")
    lines.append(f"Client ID prefix: `{run_client_prefix}`")
    lines.append(f"Summary: `{passed}` passed, `{failed}` failed, `{skipped}` skipped")
    lines.append("")
    lines.append("## Matrix")
    lines.append("")
    lines.append(
        "| Case | Expected | Upload | Generate | Source Type | Rendered Clips | Playable URLs | Clean Fallback | Raw Error Leak | Result |"
    )
    lines.append("|---|---|---:|---:|---|---:|---:|---:|---:|---|")

    for index, result in enumerate(results):
        if result.skipped:
            outcome = "SKIP"
        else:
            outcome = "PASS" if result.passed else "FAIL"
        lines.append(
            "| {case} | {expected} | {upload} | {generate} | {source_type} | {rendered} | {playable} | {fallback} | {leaked} | {outcome} |".format(
                case=result.label.replace("|", "\\|"),
                expected=", ".join(result.expected_source_types) or result.expected_mode,
                upload="yes" if result.upload_accepted else ("n/a" if not result.upload_attempted else "no"),
                generate="yes" if result.generate_accepted else ("n/a" if not result.generate_attempted else "no"),
                source_type=result.returned_source_type or result.upload_source_type or "n/a",
                rendered=result.rendered_clip_count,
                playable=result.playable_url_count,
                fallback="yes" if result.clean_fallback else "n/a",
                leaked="yes" if result.raw_error_leaked else "no",
                outcome=outcome,
            )
        )

    lines.append("")
    lines.append("## Details")
    lines.append("")

    for result in results:
        lines.append(f"### {result.label}")
        lines.append("")
        lines.append(f"- ID: `{result.id}`")
        lines.append(f"- Kind: `{result.kind}`")
        lines.append(f"- Expected mode: `{result.expected_mode}`")
        lines.append(f"- Expected source types: `{', '.join(result.expected_source_types) or 'n/a'}`")
        lines.append(f"- Upload accepted: `{result.upload_accepted}`")
        lines.append(f"- Generate accepted: `{result.generate_accepted}`")
        lines.append(f"- HTTP status: `{result.http_status}`")
        lines.append(f"- Request ID: `{result.request_id}`")
        lines.append(f"- Returned source type: `{result.returned_source_type}`")
        lines.append(f"- Source type OK: `{result.source_type_ok}`")
        lines.append(f"- Clip count: `{result.clip_count}`")
        lines.append(f"- Rendered clip count: `{result.rendered_clip_count}`")
        lines.append(f"- Strategy-only clip count: `{result.strategy_only_clip_count}`")
        lines.append(f"- Playable URL count: `{result.playable_url_count}`")
        lines.append(f"- Clean fallback: `{result.clean_fallback}`")
        lines.append(f"- Raw error leaked: `{result.raw_error_leaked}`")
        if result.fallback_code:
            lines.append(f"- Fallback code: `{result.fallback_code}`")
        if result.fallback_message:
            lines.append(f"- Fallback message: {result.fallback_message}")
        if result.error:
            lines.append(f"- Error: {result.error}")
        if result.rendered_urls:
            lines.append("- Rendered/media URLs:")
            for url in result.rendered_urls:
                lines.append(f"  - `{url}`")
        if result.rendered_url_checks:
            lines.append("- Rendered URL checks:")
            for check in result.rendered_url_checks:
                lines.append(
                    "  - `{url}` status=`{status}` content_type=`{content_type}` playable=`{playable}` error=`{error}`".format(
                        url=check.get("url"),
                        status=check.get("http_status"),
                        content_type=check.get("content_type"),
                        playable=check.get("playable"),
                        error=check.get("error"),
                    )
                )
        if result.notes:
            lines.append("- Notes:")
            for note in result.notes:
                lines.append(f"  - {note}")
        if index != len(results) - 1:
            lines.append("")

    RESULT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run LWA source POC matrix.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000", help="Backend base URL.")
    parser.add_argument("--youtube-url", default="", help="Optional YouTube URL to test blocked fallback.")
    parser.add_argument("--twitch-url", default="", help="Optional Twitch or stream URL to test fallback.")
    parser.add_argument("--unsupported-url", default="", help="Optional unsupported public URL to test clean fallback.")
    parser.add_argument("--client-id", default="", help="Optional x-lwa-client-id prefix.")
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")
    run_client_prefix = safe_client_id(
        f"{args.client_id or 'poc-source-matrix'}-{int(time.time())}-{uuid.uuid4().hex[:6]}"
    )

    print(f"[poc] repo: {REPO_ROOT}")
    print(f"[poc] base_url: {base_url}")
    print(f"[poc] client_id_prefix: {run_client_prefix}")

    health_status, health_payload = http_json_request(f"{base_url}/health")
    if not (200 <= health_status < 300):
        print(f"[poc] backend health failed: status={health_status} payload={health_payload}")
        return 1

    print(f"[poc] backend health OK: {health_payload}")

    fixtures = make_fixtures()
    cases = build_cases(
        fixtures,
        youtube_url=args.youtube_url or None,
        twitch_url=args.twitch_url or None,
        unsupported_url=args.unsupported_url or None,
    )

    results: list[MatrixResult] = []

    for case in cases:
        print(f"\n[poc] running {case.id}: {case.label}")
        case_client_id = safe_client_id(f"{run_client_prefix}-{case.id}")
        result = run_case(base_url, case, case_client_id)
        results.append(result)

        if result.skipped:
            status = "SKIP"
        else:
            status = "PASS" if result.passed else "FAIL"
        print(
            "[poc] result {status}: upload={upload} generate={generate} source_type={source_type} rendered={rendered} playable={playable} clean_fallback={fallback} leaked={leaked}".format(
                status=status,
                upload=result.upload_accepted,
                generate=result.generate_accepted,
                source_type=result.returned_source_type,
                rendered=result.rendered_clip_count,
                playable=result.playable_url_count,
                fallback=result.clean_fallback,
                leaked=result.raw_error_leaked,
            )
        )
        if result.error:
            print(f"[poc] error: {result.error[:300]}")
        for note in result.notes:
            print(f"[poc] note: {note}")

    write_reports(
        results=results,
        base_url=base_url,
        run_client_prefix=run_client_prefix,
        youtube_url=args.youtube_url or None,
        twitch_url=args.twitch_url or None,
        unsupported_url=args.unsupported_url or None,
    )

    passed = sum(1 for result in results if result.passed)
    failed = sum(1 for result in results if not result.passed and not result.skipped)
    skipped = sum(1 for result in results if result.skipped)

    print("\n[poc] complete")
    print(f"[poc] passed: {passed}")
    print(f"[poc] failed: {failed}")
    print(f"[poc] skipped: {skipped}")
    print(f"[poc] json: {RESULT_JSON}")
    print(f"[poc] markdown: {RESULT_MD}")

    # Do not fail the script just because some formats are unsupported.
    # The point is to produce a truth matrix.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
