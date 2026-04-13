from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import time
from typing import Any


def _b64url_encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _b64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode((value + padding).encode("ascii"))


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    iterations = 390_000
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return "pbkdf2_sha256${iterations}${salt}${digest}".format(
        iterations=iterations,
        salt=_b64url_encode(salt),
        digest=_b64url_encode(digest),
    )


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        algorithm, iterations, salt, digest = stored_hash.split("$", 3)
    except ValueError:
        return False

    if algorithm != "pbkdf2_sha256":
        return False

    calculated = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        _b64url_decode(salt),
        int(iterations),
    )
    return hmac.compare_digest(_b64url_encode(calculated), digest)


def create_access_token(*, secret: str, user_id: str, email: str, plan: str, exp_minutes: int) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    now = int(time.time())
    payload = {
        "sub": user_id,
        "email": email,
        "plan": plan,
        "iat": now,
        "exp": now + (exp_minutes * 60),
    }
    signing_input = ".".join(
        [
            _b64url_encode(json.dumps(header, separators=(",", ":"), sort_keys=True).encode("utf-8")),
            _b64url_encode(json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")),
        ]
    )
    signature = hmac.new(secret.encode("utf-8"), signing_input.encode("ascii"), hashlib.sha256).digest()
    return f"{signing_input}.{_b64url_encode(signature)}"


def decode_access_token(token: str, *, secret: str) -> dict[str, Any]:
    try:
        header_segment, payload_segment, signature_segment = token.split(".", 2)
    except ValueError as error:
        raise ValueError("Invalid token format") from error

    signing_input = f"{header_segment}.{payload_segment}".encode("ascii")
    expected = hmac.new(secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
    provided = _b64url_decode(signature_segment)
    if not hmac.compare_digest(expected, provided):
        raise ValueError("Invalid token signature")

    payload = json.loads(_b64url_decode(payload_segment).decode("utf-8"))
    if int(payload.get("exp", 0)) <= int(time.time()):
        raise ValueError("Token expired")
    return payload
