from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import JSON, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db.base import Base


def _id() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(UTC)


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_id)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(default=_now)


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_id)
    url: Mapped[str] = mapped_column(Text)
    platform: Mapped[str] = mapped_column(String(32), default="youtube")
    video_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    title: Mapped[str] = mapped_column(Text, default="")
    duration: Mapped[float] = mapped_column(Float, default=0.0)
    height: Mapped[int] = mapped_column(Integer, default=0)
    source_path: Mapped[str] = mapped_column(Text, default="")
    fetched_at: Mapped[datetime] = mapped_column(default=_now)

    jobs: Mapped[list[Job]] = relationship(back_populates="source", cascade="all, delete-orphan")


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_id)
    source_id: Mapped[str] = mapped_column(ForeignKey("sources.id", ondelete="CASCADE"), index=True)
    status: Mapped[str] = mapped_column(String(24), default="queued", index=True)
    stage: Mapped[str] = mapped_column(String(32), default="")
    progress: Mapped[int] = mapped_column(Integer, default=0)
    quality_mode: Mapped[str] = mapped_column(String(24), default="visually_lossless")
    params: Mapped[dict] = mapped_column(JSON, default=dict)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=_now, index=True)
    finished_at: Mapped[datetime | None] = mapped_column(nullable=True)

    source: Mapped[Source] = relationship(back_populates="jobs")
    clips: Mapped[list[Clip]] = relationship(back_populates="job", cascade="all, delete-orphan")


class Clip(Base):
    __tablename__ = "clips"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_id)
    job_id: Mapped[str] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), index=True)
    start: Mapped[float] = mapped_column(Float)
    end: Mapped[float] = mapped_column(Float)
    score: Mapped[float] = mapped_column(Float, default=0.0)
    ratio: Mapped[str] = mapped_column(String(12), default="9:16")
    file_path: Mapped[str] = mapped_column(Text, default="")
    webm_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    width: Mapped[int] = mapped_column(Integer, default=0)
    height: Mapped[int] = mapped_column(Integer, default=0)
    crf: Mapped[int] = mapped_column(Integer, default=17)
    title: Mapped[str] = mapped_column(Text, default="")
    description: Mapped[str] = mapped_column(Text, default="")
    reason: Mapped[str] = mapped_column(Text, default="")

    job: Mapped[Job] = relationship(back_populates="clips")
    captions: Mapped[list[Caption]] = relationship(back_populates="clip", cascade="all, delete-orphan")
    thumbnails: Mapped[list[Thumbnail]] = relationship(back_populates="clip", cascade="all, delete-orphan")


class Caption(Base):
    __tablename__ = "captions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_id)
    clip_id: Mapped[str] = mapped_column(ForeignKey("clips.id", ondelete="CASCADE"), index=True)
    format: Mapped[str] = mapped_column(String(8), default="srt")
    text: Mapped[str] = mapped_column(Text, default="")
    words: Mapped[list] = mapped_column(JSON, default=list)
    path: Mapped[str] = mapped_column(Text, default="")

    clip: Mapped[Clip] = relationship(back_populates="captions")


class Thumbnail(Base):
    __tablename__ = "thumbnails"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_id)
    clip_id: Mapped[str] = mapped_column(ForeignKey("clips.id", ondelete="CASCADE"), index=True)
    path: Mapped[str] = mapped_column(Text)
    frame_time: Mapped[float] = mapped_column(Float, default=0.0)

    clip: Mapped[Clip] = relationship(back_populates="thumbnails")


class Streamer(Base):
    __tablename__ = "streamers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_id)
    platform: Mapped[str] = mapped_column(String(16), index=True)
    external_id: Mapped[str] = mapped_column(String(64), unique=True)
    name: Mapped[str] = mapped_column(Text)
    country: Mapped[str | None] = mapped_column(String(8), nullable=True, index=True)
    category: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    channel_url: Mapped[str] = mapped_column(Text, default="")
    avatar_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    metrics: Mapped[list[StreamerMetric]] = relationship(back_populates="streamer", cascade="all, delete-orphan")


class StreamerMetric(Base):
    __tablename__ = "streamer_metrics"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_id)
    streamer_id: Mapped[str] = mapped_column(ForeignKey("streamers.id", ondelete="CASCADE"), index=True)
    views: Mapped[int] = mapped_column(Integer, default=0)
    followers: Mapped[int] = mapped_column(Integer, default=0)
    rank: Mapped[int] = mapped_column(Integer, default=0)
    captured_at: Mapped[datetime] = mapped_column(default=_now, index=True)

    streamer: Mapped[Streamer] = relationship(back_populates="metrics")
