from __future__ import annotations

import asyncio
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from ..controllers.job_controller import JobController
from ..core.errors import ClipForgeError
from ..db.session import SessionLocal
from ..models import Job
from ..pipeline.context import JobContext
from ..pipeline.pipeline import run_pipeline
from .celery_app import celery_app


def _set_status(job_id: str, status: str, stage: str = "", progress: int = 0) -> None:
    db: Session = SessionLocal()
    try:
        job = db.get(Job, job_id)
        if job is None:
            return
        job.status = status
        if stage:
            job.stage = stage
        if progress:
            job.progress = progress
        if status in {"succeeded", "failed"}:
            job.finished_at = datetime.now(UTC)
        db.commit()
    finally:
        db.close()


async def _run(ctx: JobContext) -> list[dict[str, object]]:
    async def db_progress(stage: str, percent: int) -> None:
        await asyncio.to_thread(_set_status, ctx.job_id, "running", stage, percent)

    return await run_pipeline(ctx, db_progress)


@celery_app.task(bind=True, name="clipforge.process_job")
def process_job(self, job_payload: dict) -> list[dict]:
    ctx = JobContext(**job_payload)
    _set_status(ctx.job_id, "running", "ingest", 0)
    try:
        rendered = asyncio.run(_run(ctx))
    except ClipForgeError as exc:
        _set_status(ctx.job_id, "failed")
        db: Session = SessionLocal()
        try:
            JobController(db).mark_failed(ctx.job_id, str(exc))
        finally:
            db.close()
        self.update_state(state="FAILURE", meta={"error": str(exc)})
        raise

    db: Session = SessionLocal()
    try:
        JobController(db).save_rendered(ctx.job_id, rendered)
    finally:
        db.close()
    return rendered
