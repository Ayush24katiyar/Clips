from __future__ import annotations

import json

from ...utils.paths import job_dir
from ..context import JobContext, ProgressFn


async def run(ctx: JobContext, progress: ProgressFn) -> JobContext:
    directory = job_dir(ctx.job_id)
    manifest = {
        "job_id": ctx.job_id,
        "source_url": ctx.url,
        "quality_mode": ctx.quality_mode,
        "ratio": ctx.ratio,
        "clips": ctx.rendered,
    }
    path = directory / "manifest.json"
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    ctx.artifacts["manifest"] = str(path)
    await progress("package", 100, f"Packaged {len(ctx.rendered)} clips")
    return ctx
