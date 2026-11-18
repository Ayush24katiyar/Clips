from __future__ import annotations

from ...services.downloader import Downloader
from ..context import JobContext, ProgressFn


async def run(ctx: JobContext, progress: ProgressFn) -> JobContext:
    await progress("ingest", 5, "Downloading source")
    downloaded = Downloader().download(ctx.url, ctx.source_id)
    ctx.source_path = downloaded.path
    ctx.source_duration = downloaded.duration
    ctx.artifacts["source_meta"] = downloaded
    await progress("ingest", 100, f"Source ready ({downloaded.height}p)")
    return ctx
