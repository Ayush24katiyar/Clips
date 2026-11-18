from __future__ import annotations

from pathlib import Path

from ...services.thumbnail_service import ThumbnailService
from ..context import JobContext, ProgressFn


async def run(ctx: JobContext, progress: ProgressFn) -> JobContext:
    if not ctx.generate_thumbnail:
        await progress("thumbnail", 100, "Skipped")
        return ctx

    service = ThumbnailService()
    for index, item in enumerate(ctx.rendered, 1):
        clip_id = f"{ctx.job_id}_{index:02d}"
        candidate = item["candidate"]
        duration = float(candidate["end"]) - float(candidate["start"])
        frame = min(1.5, duration / 3)
        output = service.generate(
            clip_id,
            Path(str(item["path"])),
            frame,
            str(candidate.get("title") or "Clip"),
        )
        item["thumbnail_path"] = str(output)

    await progress("thumbnail", 100, "Thumbnails ready")
    return ctx
