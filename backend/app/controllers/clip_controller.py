from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Caption, Clip, Thumbnail


class ClipController:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_for_job(self, job_id: str) -> list[Clip]:
        return list(self.db.scalars(select(Clip).where(Clip.job_id == job_id).order_by(Clip.score.desc())))

    def get(self, clip_id: str) -> Clip | None:
        return self.db.get(Clip, clip_id)

    def captions(self, clip_id: str) -> list[Caption]:
        return list(self.db.scalars(select(Caption).where(Caption.clip_id == clip_id)))

    def thumbnail(self, clip_id: str) -> Thumbnail | None:
        return self.db.scalar(select(Thumbnail).where(Thumbnail.clip_id == clip_id).limit(1))
