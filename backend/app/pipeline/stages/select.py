from __future__ import annotations

from ...core.errors import AnalysisError
from ..context import JobContext, ProgressFn


async def run(ctx: JobContext, progress: ProgressFn) -> JobContext:
    if not ctx.candidates:
        raise AnalysisError("No clip candidates produced")
    # Re-rank and clamp to source duration; in-point refinement at visual peaks
    # is added in Phase 2 (face/audio signal fusion).
    valid = [clip for clip in ctx.candidates if 0 <= clip.start < clip.end <= (ctx.source_duration or clip.end)]
    if not valid:
        valid = ctx.candidates
    ctx.candidates = sorted(valid, key=lambda c: c.score, reverse=True)[: ctx.clip_count]
    await progress("select", 100, f"Selected {len(ctx.candidates)} clips")
    return ctx
