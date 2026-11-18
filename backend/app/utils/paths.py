from __future__ import annotations

from pathlib import Path

from ..core.config import settings


def job_dir(job_id: str) -> Path:
    path = settings.storage_root / "clips" / job_id
    path.mkdir(parents=True, exist_ok=True)
    return path


def source_path(source_id: str, suffix: str = ".mp4") -> Path:
    path = settings.storage_path("sources") / f"{source_id}{suffix}"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def audio_path(source_id: str) -> Path:
    return settings.storage_path("captions") / f"{source_id}.flac"


def transcript_path(source_id: str) -> Path:
    return settings.storage_path("captions") / f"{source_id}.transcript.json"


def thumbnail_path(clip_id: str) -> Path:
    return settings.storage_path("thumbs") / f"{clip_id}.jpg"
