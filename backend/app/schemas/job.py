from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl

from .analysis import ClipCandidate


class CreateJobRequest(BaseModel):
    url: HttpUrl
    quality_mode: str = Field(default="visually_lossless")
    ratio: str = Field(default="9:16")
    # "crop" = face/center crop; "letterbox" = full frame on blurred fill (gaming).
    reframe: str = Field(default="crop")
    clip_count: int = Field(default=7, ge=1, le=20)
    source_height: int = Field(default=2160, ge=144, le=4320)
    # Sample a bounded window of a long stream. 0 = from the beginning / to the end.
    source_start_seconds: int = Field(default=0, ge=0, le=86400)
    source_max_seconds: int = Field(default=0, ge=0, le=86400)
    clip_min_seconds: float = Field(default=15.0, gt=0)
    clip_max_seconds: float = Field(default=90.0, gt=0)
    language: str | None = None
    burn_captions: bool = True
    generate_thumbnail: bool = True
    webm: bool = False


class JobStatus(BaseModel):
    id: str
    status: str
    stage: str
    progress: int
    error: str | None = None


class JobRead(JobStatus):
    source_id: str
    quality_mode: str
    created_at: datetime
    finished_at: datetime | None = None
    clips: list[ClipCandidate] = Field(default_factory=list)
