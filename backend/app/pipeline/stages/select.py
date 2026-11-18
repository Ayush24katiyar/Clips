from __future__ import annotations

from ...core.errors import AnalysisError
from ...schemas.analysis import ClipCandidate
from ..context import JobContext, ProgressFn


async def run(ctx: JobContext, progress: ProgressFn) -> JobContext:
    if not ctx.candidates:
        # Last-resort deterministic windows so a job never dies here.
        duration = ctx.source_duration or 0
        if duration <= ctx.clip_min_seconds:
            raise AnalysisError("Source is too short to produce a clip")
        span = min(ctx.clip_max_seconds, duration)
        ctx.candidates = [
            ClipCandidate(
                start=float(i * duration / ctx.clip_count),
                end=float(min(i * duration / ctx.clip_count + span, duration)),
                score=50.0,
                reason="Automatic even-spacing fallback",
                title=f"Clip {i + 1}",
                description="Automatically selected segment.",
            )
            for i in range(ctx.clip_count)
        ]
    # Re-rank and clamp to source duration; in-point refinement at visual peaks
    # is added in Phase 2 (face/audio signal fusion).
    valid = [clip for clip in ctx.candidates if 0 <= clip.start < clip.end <= (ctx.source_duration or clip.end)]
    if not valid:
        valid = ctx.candidates
    ctx.candidates = sorted(valid, key=lambda c: c.score, reverse=True)[: ctx.clip_count]
    await progress("select", 100, f"Selected {len(ctx.candidates)} clips")
    return ctx
