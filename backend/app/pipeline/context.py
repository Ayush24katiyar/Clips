from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field

from ..schemas.analysis import ClipCandidate, Transcript

ProgressFn = Callable[[str, int, str], Awaitable[None]]


@dataclass
class JobContext:
    job_id: str
    url: str
    quality_mode: str = "visually_lossless"
    ratio: str = "9:16"
    reframe: str = "crop"
    source_height: int = 2160
    source_start_seconds: int = 0
    source_max_seconds: int = 0
    clip_count: int = 7
    clip_min_seconds: float = 15.0
    clip_max_seconds: float = 90.0
    language: str | None = None
    burn_captions: bool = True
    generate_thumbnail: bool = True
    webm: bool = False

    source_id: str = ""
    source_path: str = ""
    source_duration: float = 0.0
    transcript: Transcript | None = None
    candidates: list[ClipCandidate] = field(default_factory=list)
    artifacts: dict[str, object] = field(default_factory=dict)
    rendered: list[dict[str, object]] = field(default_factory=list)

    def width_height(self) -> tuple[int, int]:
        if self.ratio == "9:16":
            return 1080, 1920
        if self.ratio == "1:1":
            return 1080, 1080
        if self.ratio == "4:5":
            return 1080, 1350
        return 1920, 1080
