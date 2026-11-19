from __future__ import annotations

import hashlib
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Clip, Job, Source, Thumbnail
from ..schemas.job import CreateJobRequest


class JobController:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, payload: CreateJobRequest) -> Job:
        from ..workers.tasks import process_job  # lazy: avoids controller/worker circular import

        source_id = hashlib.sha256(str(payload.url).encode()).hexdigest()[:32]
        source = self.db.get(Source, source_id) or Source(
            id=source_id,
            url=str(payload.url),
            platform="youtube",
            title="",
        )
        job = Job(
            source=source,
            quality_mode=payload.quality_mode,
            params=payload.model_dump(mode="json"),
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)

        context = {
            "job_id": job.id,
            "source_id": source.id,
            "url": str(payload.url),
            "quality_mode": payload.quality_mode,
            "ratio": payload.ratio,
            "reframe": payload.reframe,
            "source_height": payload.source_height,
            "source_start_seconds": payload.source_start_seconds,
            "source_max_seconds": payload.source_max_seconds,
            "clip_count": payload.clip_count,
            "clip_min_seconds": payload.clip_min_seconds,
            "clip_max_seconds": payload.clip_max_seconds,
            "language": payload.language,
            "burn_captions": payload.burn_captions,
            "generate_thumbnail": payload.generate_thumbnail,
            "webm": payload.webm,
        }
        process_job.delay(context)
        return job

    def list(self, limit: int = 50) -> list[Job]:
        return list(self.db.scalars(select(Job).order_by(Job.created_at.desc()).limit(limit)))

    def get(self, job_id: str) -> Job | None:
        return self.db.get(Job, job_id)

    def mark_failed(self, job_id: str, message: str) -> None:
        job = self.db.get(Job, job_id)
        if job is None:
            return
        job.status = "failed"
        job.error = message
        job.finished_at = datetime.now(UTC)
        self.db.commit()

    def save_rendered(self, job_id: str, rendered: list[dict]) -> None:
        job = self.db.get(Job, job_id)
        if job is None:
            return
        for item in rendered:
            candidate = item["candidate"]
            clip = Clip(
                job_id=job_id,
                start=candidate["start"],
                end=candidate["end"],
                score=candidate["score"],
                title=candidate.get("title", ""),
                description=candidate.get("description", ""),
                reason=candidate.get("reason", ""),
                ratio=job.params.get("ratio", "9:16"),
                file_path=item["path"],
                webm_path=item.get("webm_path"),
                width=item["width"],
                height=item["height"],
                crf=item["crf"],
            )
            self.db.add(clip)
            self.db.flush()
            if item.get("thumbnail_path"):
                self.db.add(
                    Thumbnail(
                        clip_id=clip.id,
                        path=str(item["thumbnail_path"]),
                        frame_time=0.0,
                    )
                )
        job.status = "succeeded"
        job.progress = 100
        job.finished_at = datetime.now(UTC)
        self.db.commit()
