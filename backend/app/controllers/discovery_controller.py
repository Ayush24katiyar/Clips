from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Streamer, StreamerMetric
from ..services.discovery_service import DiscoveryService, StreamerItem


class DiscoveryController:
    def __init__(self, db: Session) -> None:
        self.db = db

    def refresh(self, region: str = "US") -> list[Streamer]:
        service = DiscoveryService()
        items: list[StreamerItem] = service.youtube_popular(region) + service.twitch_top()
        saved: list[Streamer] = []
        for item in items:
            streamer = self.db.scalar(
                select(Streamer).where(
                    Streamer.platform == item.platform,
                    Streamer.external_id == item.external_id,
                )
            )
            if streamer is None:
                streamer = Streamer(
                    platform=item.platform,
                    external_id=item.external_id,
                    name=item.name,
                    country=item.country,
                    category=item.category,
                    channel_url=item.channel_url,
                    avatar_url=item.avatar_url,
                )
                self.db.add(streamer)
                self.db.flush()
            self.db.add(
                StreamerMetric(
                    streamer_id=streamer.id,
                    views=item.views,
                    rank=item.rank,
                    followers=0,
                )
            )
            saved.append(streamer)
        self.db.commit()
        return saved

    def list(self, country: str | None = None, category: str | None = None) -> list[Streamer]:
        query = select(Streamer)
        if country:
            query = query.where(Streamer.country == country)
        if category:
            query = query.where(Streamer.category.ilike(f"%{category}%"))
        return list(self.db.scalars(query.limit(100)))
