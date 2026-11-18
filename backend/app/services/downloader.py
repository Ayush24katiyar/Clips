from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass

from ..core.errors import DownloadError
from ..utils.paths import source_path


@dataclass
class DownloadedSource:
    source_id: str
    path: str
    title: str
    duration: float
    height: int
    platform: str
    video_id: str | None


class Downloader:
    """yt-dlp wrapper. Never bypasses bot checks or auth walls."""

    def download(self, url: str, source_id: str, max_height: int = 2160) -> DownloadedSource:
        output = source_path(source_id)
        command = [
            "yt-dlp",
            "--js-runtimes", "node",
            "--no-playlist",
            "-f",
            f"bestvideo[height<={max_height}]+bestaudio/best[height<={max_height}]/best",
            "--merge-output-format",
            "mp4",
            "--write-info-json",
            "--no-overwrites",
            "-o",
            str(output.with_suffix("")) + ".%(ext)s",
            url,
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise DownloadError(result.stderr[-2000:])

        info_file = output.with_suffix("").with_suffix(".info.json")
        if not info_file.exists():
            candidates = list(output.parent.glob(f"{source_id}*.info.json"))
            if not candidates:
                raise DownloadError("yt-dlp did not write metadata")
            info_file = candidates[0]
        info = json.loads(info_file.read_text(encoding="utf-8"))

        actual = output
        if not actual.exists():
            candidates = list(output.parent.glob(f"{source_id}.*"))
            videos = [c for c in candidates if c.suffix in {".mp4", ".mkv", ".webm"}]
            if not videos:
                raise DownloadError("Downloaded video file not found")
            actual = videos[0]

        return DownloadedSource(
            source_id=source_id,
            path=str(actual),
            title=info.get("title", ""),
            duration=float(info.get("duration") or 0),
            height=int(info.get("height") or 0),
            platform=info.get("extractor_key", "youtube").lower(),
            video_id=info.get("id"),
        )
