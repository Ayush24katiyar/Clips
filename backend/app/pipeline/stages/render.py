from __future__ import annotations

from pathlib import Path

from ...core.config import settings
from ...services.captions_service import CaptionsService
from ...services.ffmpeg_service import render_clip, to_webm, validate_output
from ...utils.ffprobe import probe
from ...utils.paths import job_dir
from ..context import JobContext, ProgressFn


async def run(ctx: JobContext, progress: ProgressFn) -> JobContext:
    width, height = ctx.width_height()
    directory = job_dir(ctx.job_id)
    source = Path(ctx.source_path)
    total = len(ctx.candidates)

    for index, clip in enumerate(ctx.candidates, 1):
        output = directory / f"clip_{index:02d}.mp4"
        ass_path = None
        if ctx.burn_captions and ctx.transcript is not None:
            paths = CaptionsService().write_all(ctx.transcript, clip, directory)
            ass_path = paths.get("ass")

        await progress("render", int(index / total * 90), f"Rendering clip {index}/{total}")
        render_clip(
            source,
            output,
            clip.start,
            clip.end,
            quality_mode=ctx.quality_mode,
            width=width,
            height=height,
            ass_path=ass_path,
        )
        if ctx.quality_mode == "visually_lossless":
            validate_output(output, clip.end - clip.start)

        webm_path = None
        if ctx.webm:
            webm_path = directory / f"clip_{index:02d}.webm"
            to_webm(output, webm_path)

        info = probe(output)
        ctx.rendered.append(
            {
                "index": index,
                "candidate": clip.model_dump(mode="json"),
                "path": str(output),
                "webm_path": str(webm_path) if webm_path else None,
                "width": info.width,
                "height": info.height,
                "crf": settings.crf_final,
            }
        )

    await progress("render", 100, f"Rendered {total} clips")
    return ctx
