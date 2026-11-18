from __future__ import annotations

from ...core.errors import AnalysisError
from ...services.analyzer import Analyzer
from ...services.groq_client import get_provider
from ..context import JobContext, ProgressFn


async def run(ctx: JobContext, progress: ProgressFn) -> JobContext:
    if ctx.transcript is None:
        raise AnalysisError("Transcript missing before analysis")
    await progress("analyze", 10, "Scoring moments")
    plan = await Analyzer(get_provider()).analyze(
        ctx.transcript, ctx.clip_count, ctx.clip_min_seconds, ctx.clip_max_seconds
    )
    ctx.candidates = plan.clips
    ctx.artifacts["analysis"] = plan.model_dump(mode="json")
    await progress("analyze", 100, f"{len(plan.clips)} moments selected")
    return ctx
