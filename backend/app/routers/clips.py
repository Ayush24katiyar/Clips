from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..controllers.clip_controller import ClipController
from ..db.session import get_db
from ..services.storage_service import StorageService

router = APIRouter(prefix="/clips", tags=["clips"])


@router.get("/job/{job_id}")
def list_clips(job_id: str, db: Session = Depends(get_db)) -> list[dict]:
    controller = ClipController(db)
    clips = controller.list_for_job(job_id)
    return [
        {
            "id": clip.id,
            "start": clip.start,
            "end": clip.end,
            "score": clip.score,
            "title": clip.title,
            "description": clip.description,
            "ratio": clip.ratio,
            "width": clip.width,
            "height": clip.height,
            "file_path": StorageService().public_url(clip.file_path),
            "webm_path": StorageService().public_url(clip.webm_path) if clip.webm_path else None,
            "thumbnail_path": (
                StorageService().public_url(controller.thumbnail(clip.id).path)
                if controller.thumbnail(clip.id)
                else None
            ),
        }
        for clip in clips
    ]
