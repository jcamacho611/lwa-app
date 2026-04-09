from __future__ import annotations

import asyncio
from datetime import datetime, timezone
import html
from typing import Any
from xml.etree import ElementTree

import httpx

from .schemas import TrendItem

GOOGLE_TRENDS_URL = "https://trends.google.com/trending/rss?geo=US"
REDDIT_TRENDS_URL = "https://api.reddit.com/r/popular?limit=6"
HN_TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{story_id}.json"


def fallback_trends() -> list[TrendItem]:
    return [
        TrendItem(
            id="google-fallback-ai",
            title="AI workflow",
            source="Google Trends",
            detail="Fallback trend when live feeds are unavailable.",
            url="https://trends.google.com",
        ),
        TrendItem(
            id="reddit-fallback-creators",
            title="creator economy",
            source="Reddit",
            detail="Fallback social signal for creator-led hooks.",
            url="https://www.reddit.com/r/CreatorEconomy/",
        ),
        TrendItem(
            id="hn-fallback-video-tools",
            title="video tooling",
            source="Hacker News",
            detail="Fallback product trend for software-minded creators.",
            url="https://news.ycombinator.com/",
        ),
    ]


async def fetch_public_trends(limit_per_source: int = 3) -> list[TrendItem]:
    async with httpx.AsyncClient(
        timeout=8.0,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0 Safari/537.36 LWA/1.0"
            ),
            "Accept": "application/json, text/plain, */*",
        },
    ) as client:
        results = await asyncio.gather(
            fetch_google_trends(client, limit_per_source),
            fetch_reddit_trends(client, limit_per_source),
            fetch_hacker_news_trends(client, limit_per_source),
            return_exceptions=True,
        )

    trends: list[TrendItem] = []
    for result in results:
        if isinstance(result, Exception):
            continue
        trends.extend(result)

    if trends:
        return trends

    return fallback_trends()


async def fetch_google_trends(client: httpx.AsyncClient, limit: int) -> list[TrendItem]:
    response = await client.get(GOOGLE_TRENDS_URL)
    response.raise_for_status()

    root = ElementTree.fromstring(response.text)
    namespace = {"ht": "https://trends.google.com/trending/rss"}
    items = root.findall("./channel/item")

    trends: list[TrendItem] = []
    for item in items[:limit]:
        title = item.findtext("title", default="Untitled trend").strip()
        traffic = item.findtext("ht:approx_traffic", default="Rising", namespaces=namespace).strip()
        link = item.findtext("link")
        trend_id = f"google-{slugify(title)}"
        trends.append(
            TrendItem(
                id=trend_id,
                title=title,
                source="Google Trends",
                detail=f"Approx traffic: {traffic}",
                url=link,
            )
        )

    return trends


async def fetch_reddit_trends(client: httpx.AsyncClient, limit: int) -> list[TrendItem]:
    response = await client.get(REDDIT_TRENDS_URL)
    response.raise_for_status()
    payload = response.json()
    children = payload.get("data", {}).get("children", [])

    trends: list[TrendItem] = []
    for child in children[:limit]:
        post = child.get("data", {})
        title = post.get("title", "Untitled post").strip()
        subreddit = post.get("subreddit_name_prefixed", "r/popular")
        permalink = post.get("permalink")
        comments = post.get("num_comments", 0)
        score = post.get("score", 0)
        trends.append(
            TrendItem(
                id=f"reddit-{post.get('id', slugify(title))}",
                title=html.unescape(title),
                source="Reddit",
                detail=f"{subreddit} • {score} score • {comments} comments",
                url=f"https://www.reddit.com{permalink}" if permalink else None,
            )
        )

    return trends


async def fetch_hacker_news_trends(client: httpx.AsyncClient, limit: int) -> list[TrendItem]:
    response = await client.get(HN_TOP_STORIES_URL)
    response.raise_for_status()
    story_ids: list[int] = response.json()[:limit]

    requests = [client.get(HN_ITEM_URL.format(story_id=story_id)) for story_id in story_ids]
    responses = await asyncio.gather(*requests, return_exceptions=True)

    trends: list[TrendItem] = []
    for story_id, item_response in zip(story_ids, responses):
        if isinstance(item_response, Exception):
            continue

        payload: dict[str, Any] = item_response.json()
        title = str(payload.get("title", "Untitled story")).strip()
        score = int(payload.get("score", 0))
        comments = int(payload.get("descendants", 0))
        url = payload.get("url") or f"https://news.ycombinator.com/item?id={story_id}"

        trends.append(
            TrendItem(
                id=f"hn-{story_id}",
                title=title,
                source="Hacker News",
                detail=f"{score} points • {comments} comments",
                url=url,
            )
        )

    return trends


def trends_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def slugify(value: str) -> str:
    return "".join(character.lower() if character.isalnum() else "-" for character in value).strip("-")
