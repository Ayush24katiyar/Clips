from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..controllers.clip_controller import ClipController
from ..db.session import get_db

router = APIRouter(prefix="/clips", tags=["captions"])


@router.get("/{clip_id}/captions")
def get_captions(clip_id: str, db: Session = Depends(get_db)) -> list[dict]:
    controller = ClipController(db)
    if controller.get(clip_id) is None:
        raise HTTPException(status_code=404, detail="Clip not found")
    return [
        {"format": c.format, "text": c.text, "words": c.words, "path": c.path} for c in controller.captions(clip_id)
    ]
