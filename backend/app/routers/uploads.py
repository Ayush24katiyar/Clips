from __future__ import annotations

import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from ..core.config import settings
from ..db.session import get_db
from ..models import Source

router = APIRouter(prefix="/uploads", tags=["uploads"])

ALLOWED = {".mp4", ".mkv", ".mov", ".webm", ".m4v"}


@router.post("")
async def upload_video(file: UploadFile = File(...), db: Session = Depends(get_db)) -> dict:
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {suffix}")
    source_id = str(uuid.uuid4())
    destination = settings.storage_path("sources") / f"{source_id}{suffix}"
    with destination.open("wb") as handle:
        shutil.copyfileobj(file.file, handle)
    source = Source(id=source_id, url=f"file://{destination}", title=file.filename or "upload")
    db.add(source)
    db.commit()
    return {"source_id": source_id, "path": str(destination)}
