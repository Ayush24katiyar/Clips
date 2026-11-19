from __future__ import annotations

import subprocess
from pathlib import Path

from ..core.config import settings
from ..core.errors import RenderError, ValidationError
from ..utils.ffprobe import MediaInfo, probe

QUALITY_CRF = {
    "visually_lossless": settings.crf_final,
    "balanced": settings.crf_balanced,
    "bit_exact": None,
    "true_lossless": None,
}


def run(command: list[str]) -> None:
    """Single entry point for FFmpeg subprocess calls."""
    command[0] = settings.ffmpeg_bin
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise RenderError(f"FFmpeg failed: {result.stderr[-2000:]}")


def extract_audio(source: Path, output: Path) -> Path:
    """16 kHz mono FLAC — Groq-compatible and lossless."""
    output.parent.mkdir(parents=True, exist_ok=True)
    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(source),
            "-ar",
            "16000",
            "-ac",
            "1",
            "-map",
            "0:a:0",
            "-c:a",
            "flac",
            str(output),
        ]
    )
    return output


def split_audio(
    source: Path,
    output_dir: Path,
    chunk_seconds: int,
    overlap: float,
) -> list[tuple[Path, float]]:
    """Split long audio into overlapping FLAC chunks.

    Returns a list of (chunk path, start offset in the source). The overlap is
    appended to each chunk so words on a boundary are not cut in half.
    """
    duration = probe(str(source)).duration
    if duration <= chunk_seconds:
        return [(source, 0.0)]

    output_dir.mkdir(parents=True, exist_ok=True)
    chunks: list[tuple[Path, float]] = []
    start = 0.0
    index = 0
    while start < duration:
        length = min(chunk_seconds, duration - start)
        target = output_dir / f"chunk_{index:04d}.flac"
        run(
            [
                "ffmpeg",
                "-y",
                "-ss", f"{start:.3f}",
                "-i", str(source),
                "-t", f"{length + overlap:.3f}",
                "-c:a", "flac",
                str(target),
            ]
        )
        chunks.append((target, start))
        start += chunk_seconds
        index += 1
    return chunks


def extract_frame(source: Path, output: Path, at: float) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    run(
        [
            "ffmpeg",
            "-y",
            "-ss",
            f"{at:.3f}",
            "-i",
            str(source),
            "-frames:v",
            "1",
            "-update",
            "1",
            str(output),
        ]
    )
    return output


def _scale_filter(width: int, height: int) -> str:
    return f"scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height}"


def render_clip(
    source: Path,
    output: Path,
    start: float,
    end: float,
    quality_mode: str = "visually_lossless",
    width: int = 1080,
    height: int = 1920,
    ass_path: Path | None = None,
    preset: str = "slow",
    reframe: str = "crop",
) -> Path:
    duration = max(end - start, 0.1)
    output.parent.mkdir(parents=True, exist_ok=True)

    if quality_mode == "bit_exact":
        if ass_path is not None:
            raise RenderError("bit_exact mode cannot burn captions; use visually_lossless")
        run(
            [
                "ffmpeg",
                "-y",
                "-ss",
                f"{start:.3f}",
                "-i",
                str(source),
                "-t",
                f"{duration:.3f}",
                "-map",
                "0",
                "-c",
                "copy",
                str(output),
            ]
        )
        return output

    if quality_mode == "true_lossless":
        run(
            [
                "ffmpeg",
                "-y",
                "-ss",
                f"{start:.3f}",
                "-i",
                str(source),
                "-t",
                f"{duration:.3f}",
                "-c:v",
                "ffv1",
                "-level",
                "3",
                "-c:a",
                "flac",
                str(output),
            ]
        )
        return output

    crf = QUALITY_CRF.get(quality_mode, settings.crf_final)
    if quality_mode == "balanced":
        preset = "medium"

    if reframe == "letterbox":
        # Keep the full 16:9 game frame (including facecam) over a blurred fill.
        # No stretching, no lost subject — suited to gaming streams.
        filters = [
            "split=2[bg][fg]",
            f"[bg]scale={width}:{height}:force_original_aspect_ratio=increase,"
            f"crop={width}:{height},boxblur=24:2[bgs]",
            f"[fg]scale={width}:-2[fgs]",
            "[bgs][fgs]overlay=(W-w)/2:(H-h)/2",
        ]
        video_filter = ";".join(filters)
        if ass_path is not None:
            video_filter += f",subtitles={ass_path.as_posix()}"
        video_filter += f",fps={settings.output_fps}"
    else:
        filters = [_scale_filter(width, height)]
        if ass_path is not None:
            filters.append(f"subtitles={ass_path.as_posix()}")
        filters.append(f"fps={settings.output_fps}")
        video_filter = ",".join(filters)

    audio_filter = f"loudnorm=I={settings.loudness_target}:TP=-1:LRA=11"

    run(
        [
            "ffmpeg",
            "-y",
            "-ss",
            f"{start:.3f}",
            "-i",
            str(source),
            "-t",
            f"{duration:.3f}",
            "-vf",
            video_filter,
            "-af",
            audio_filter,
            "-c:v",
            "libx264",
            "-preset",
            preset,
            "-crf",
            str(crf),
            "-profile:v",
            "high",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "320k",
            "-ar",
            "48000",
            "-movflags",
            "+faststart",
            str(output),
        ]
    )
    return output


def render_draft(source: Path, output: Path, start: float, end: float) -> Path:
    duration = max(end - start, 0.1)
    run(
        [
            "ffmpeg",
            "-y",
            "-ss",
            f"{start:.3f}",
            "-i",
            str(source),
            "-t",
            f"{duration:.3f}",
            "-c:v",
            "h264_nvenc",
            "-cq",
            str(settings.crf_draft),
            "-preset",
            "p4",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            str(output),
        ]
    )
    return output


def to_webm(source: Path, output: Path) -> Path:
    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(source),
            "-c:v",
            "libvpx-vp9",
            "-crf",
            "30",
            "-b:v",
            "0",
            "-c:a",
            "libopus",
            "-b:a",
            "128k",
            str(output),
        ]
    )
    return output


def validate_output(path: Path, expected_duration: float) -> MediaInfo:
    info = probe(path)
    if info.codec != "h264" or not info.has_audio:
        raise ValidationError(f"Invalid output streams for {path}: {info}")
    if abs(info.duration - expected_duration) > 0.5:
        raise ValidationError(f"Duration mismatch: {info.duration} vs {expected_duration}")
    return info
