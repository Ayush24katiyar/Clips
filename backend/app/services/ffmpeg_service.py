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

    filters = [_scale_filter(width, height)]
    if ass_path is not None:
        filters.append(f"subtitles={ass_path.as_posix()}")
    filters.append(f"fps={settings.output_fps}")
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
            ",".join(filters),
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
