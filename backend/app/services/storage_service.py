from __future__ import annotations

import shutil
from pathlib import Path

from ..core.config import settings


class StorageService:
    def cleanup_job(self, job_id: str) -> None:
        path = settings.storage_root / "clips" / job_id
        if path.exists():
            shutil.rmtree(path)

    def ensure_dirs(self) -> None:
        for kind in ("sources", "clips", "thumbs", "captions", "exports"):
            settings.storage_path(kind)

    def public_url(self, path: str | Path) -> str:
        relative = Path(path).relative_to(settings.storage_root)
        return f"/media/{relative.as_posix()}"
