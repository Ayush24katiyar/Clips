from __future__ import annotations

import uuid
from collections.abc import Awaitable, Callable

from ..core.config import settings
from ..core.errors import ClipForgeError
from ..core.events import ProgressEvent, bus
from ..core.logging import job_logger
from .context import JobContext
from .stages import analyze, ingest, package, render, select, thumbnail, transcribe

STAGES = [ingest, transcribe, analyze, select, render, package, thumbnail]
logger = job_logger(__name__, "pipeline")


ProgressHook = Callable[[str, int], Awaitable[None]]


async def run_pipeline(ctx: JobContext, progress_hook: ProgressHook | None = None) -> list[dict[str, object]]:
    async def progress(stage: str, percent: int, message: str) -> None:
        log = job_logger(__name__, ctx.job_id)
        log.info("%s %d%% %s", stage, percent, message)
        await bus.publish(ProgressEvent(job_id=ctx.job_id, stage=stage, percent=percent, message=message))
        if progress_hook is not None:
            await progress_hook(stage, percent)

    try:
        for stage in STAGES:
            ctx = await stage.run(ctx, progress)
        await bus.publish(
            ProgressEvent(job_id=ctx.job_id, stage="done", percent=100, message="Done", status="succeeded")
        )
        return ctx.rendered
    except ClipForgeError as exc:
        await bus.publish(
            ProgressEvent(job_id=ctx.job_id, stage="failed", percent=0, message=str(exc), status="failed")
        )
        raise


def new_context(url: str, params: dict[str, object] | None = None) -> JobContext:
    params = params or {}
    return JobContext(
        job_id=str(params.get("job_id") or uuid.uuid4()),
        source_id=str(uuid.uuid4()),
        url=url,
        quality_mode=str(params.get("quality_mode", settings.default_quality_mode)),
        ratio=str(params.get("ratio", settings.default_ratio)),
        clip_count=int(params.get("clip_count", 7)),
        clip_min_seconds=float(params.get("clip_min_seconds", 15)),
        clip_max_seconds=float(params.get("clip_max_seconds", 90)),
        language=params.get("language") or None,
        burn_captions=bool(params.get("burn_captions", True)),
        generate_thumbnail=bool(params.get("generate_thumbnail", True)),
        webm=bool(params.get("webm", False)),
    )
