from __future__ import annotations

from dataclasses import dataclass

import httpx

from ..core.config import settings


@dataclass
class StreamerItem:
    platform: str
    external_id: str
    name: str
    country: str | None
    category: str | None
    channel_url: str
    avatar_url: str | None
    views: int
    rank: int


class DiscoveryService:
    def youtube_popular(self, region: str = "US") -> list[StreamerItem]:
        if not settings.youtube_api_key:
            return []
        response = httpx.get(
            "https://www.googleapis.com/youtube/v3/videos",
            params={
                "part": "snippet,statistics",
                "chart": "mostPopular",
                "regionCode": region,
                "maxResults": 25,
                "key": settings.youtube_api_key,
            },
            timeout=20,
        )
        response.raise_for_status()
        items: list[StreamerItem] = []
        for rank, item in enumerate(response.json().get("items", []), 1):
            snippet = item.get("snippet", {})
            channel_id = snippet.get("channelId", "")
            items.append(
                StreamerItem(
                    platform="youtube",
                    external_id=channel_id,
                    name=snippet.get("channelTitle", ""),
                    country=region,
                    category=snippet.get("categoryId"),
                    channel_url=f"https://www.youtube.com/channel/{channel_id}",
                    avatar_url=snippet.get("thumbnails", {}).get("default", {}).get("url"),
                    views=int(item.get("statistics", {}).get("viewCount", 0)),
                    rank=rank,
                )
            )
        return items

    def twitch_top(self, limit: int = 25) -> list[StreamerItem]:
        if not (settings.twitch_client_id and settings.twitch_client_secret):
            return []
        token_response = httpx.post(
            "https://id.twitch.tv/oauth2/token",
            params={
                "client_id": settings.twitch_client_id,
                "client_secret": settings.twitch_client_secret,
                "grant_type": "client_credentials",
            },
            timeout=20,
        )
        token_response.raise_for_status()
        token = token_response.json()["access_token"]
        response = httpx.get(
            "https://api.twitch.tv/helix/streams",
            params={"first": limit},
            headers={"Client-ID": settings.twitch_client_id, "Authorization": f"Bearer {token}"},
            timeout=20,
        )
        response.raise_for_status()
        return [
            StreamerItem(
                platform="twitch",
                external_id=item["user_id"],
                name=item["user_name"],
                country=None,
                category=item.get("game_name"),
                channel_url=f"https://www.twitch.tv/{item['user_login']}",
                avatar_url=item.get("thumbnail_url"),
                views=item.get("viewer_count", 0),
                rank=rank,
            )
            for rank, item in enumerate(response.json().get("data", []), 1)
        ]
