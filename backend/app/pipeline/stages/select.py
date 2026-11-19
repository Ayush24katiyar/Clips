from __future__ import annotations

from ...core.errors import AnalysisError
from ...schemas.analysis import ClipCandidate
from ..context import JobContext, ProgressFn


async def run(ctx: JobContext, progress: ProgressFn) -> JobContext:
    duration = ctx.source_duration or 0
    if duration <= ctx.clip_min_seconds:
        raise AnalysisError("Source is too short to produce a clip")

    valid = [
        clip
        for clip in ctx.candidates
        if 0 <= clip.start < clip.end <= duration
    ]
    valid = sorted(valid, key=lambda c: c.score, reverse=True)[: ctx.clip_count]

    # Always deliver the requested number of clips. Fill any gap with windows
    # spread across the whole source, skipping spots already covered.
    if len(valid) < ctx.clip_count:
        span = min(ctx.clip_max_seconds, duration)
        for i in range(ctx.clip_count):
            start = i * (duration - span) / max(ctx.clip_count - 1, 1)
            end = min(start + span, duration)
            overlap = any(
                start < c.end and end > c.start for c in valid
            )
            if not overlap:
                valid.append(
                    ClipCandidate(
                        start=float(start),
                        end=float(end),
                        score=50.0,
                        reason="Automatic even-spacing fallback",
                        title=f"Clip {len(valid) + 1}",
                        description="Automatically selected segment.",
                    )
                )
            if len(valid) >= ctx.clip_count:
                break

    ctx.candidates = valid
    await progress("select", 100, f"Selected {len(ctx.candidates)} clips")
    return ctx
