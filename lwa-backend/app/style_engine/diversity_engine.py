from __future__ import annotations

import re


def diversify_outputs(items: list[str], *, limit: int) -> list[str]:
    selected: list[str] = []
    seen_signatures: set[str] = set()
    for item in items:
        normalized = normalize(item)
        if not normalized:
            continue
        signature = " ".join(significant_tokens(normalized)[:5])
        if signature in seen_signatures:
            continue
        seen_signatures.add(signature)
        selected.append(item.strip())
        if len(selected) >= limit:
            break
    return selected


def normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def significant_tokens(value: str) -> list[str]:
    ignored = {"this", "that", "with", "from", "your", "what", "when", "where", "about", "people"}
    return [token for token in re.findall(r"[a-z0-9']+", value.lower()) if len(token) > 3 and token not in ignored]
