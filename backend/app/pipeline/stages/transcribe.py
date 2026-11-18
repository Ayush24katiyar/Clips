from __future__ import annotations

from pathlib import Path

from ...schemas.analysis import Transcript
from ...services.groq_client import get_provider
from ...services.transcriber import Transcriber
from ..context import JobContext, ProgressFn


async def run(ctx: JobContext, progress: ProgressFn) -> JobContext:
    await progress("transcribe", 5, "Extracting audio")
    data, path = await Transcriber(get_provider()).transcribe(ctx.source_id, Path(ctx.source_path), ctx.language)
    ctx.transcript = Transcript.model_validate(data)
    ctx.artifacts["transcript_path"] = str(path)
    await progress("transcribe", 100, f"Transcribed {len(ctx.transcript.words)} words")
    return ctx
