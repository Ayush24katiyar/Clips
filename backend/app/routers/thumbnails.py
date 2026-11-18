from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from ..controllers.clip_controller import ClipController
from ..db.session import get_db

router = APIRouter(prefix="/clips", tags=["thumbnails"])


@router.get("/{clip_id}/thumbnail")
def get_thumbnail(clip_id: str, db: Session = Depends(get_db)) -> FileResponse:
    thumbnail = ClipController(db).thumbnail(clip_id)
    if thumbnail is None:
        raise HTTPException(status_code=404, detail="Thumbnail not found")
    return FileResponse(thumbnail.path, media_type="image/jpeg")
