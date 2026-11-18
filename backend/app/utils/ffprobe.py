from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass

from ..core.config import settings


@dataclass
class MediaInfo:
    duration: float
    width: int
    height: int
    codec: str
    pix_fmt: str
    has_audio: bool

    @property
    def fps(self) -> float:
        return self._fps

    @classmethod
    def from_dict(cls, data: dict) -> MediaInfo:
        video = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), {})
        rate = video.get("r_frame_rate", "30/1")
        try:
            num, den = rate.split("/")
            fps = float(num) / float(den)
        except (ValueError, ZeroDivisionError):
            fps = 30.0
        info = cls(
            duration=float(data.get("format", {}).get("duration", 0)),
            width=int(video.get("width", 0)),
            height=int(video.get("height", 0)),
            codec=video.get("codec_name", ""),
            pix_fmt=video.get("pix_fmt", ""),
            has_audio=any(s.get("codec_type") == "audio" for s in data.get("streams", [])),
        )
        info._fps = fps
        return info


def probe(path: str | object) -> MediaInfo:
    """Run ffprobe. Only this module and ffmpeg_service may call ffprobe."""
    result = subprocess.run(
        [
            settings.ffprobe_bin,
            "-v",
            "error",
            "-show_entries",
            "format=duration:stream=index,codec_name,codec_type,width,height,pix_fmt,r_frame_rate",
            "-of",
            "json",
            str(path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return MediaInfo.from_dict(json.loads(result.stdout))
