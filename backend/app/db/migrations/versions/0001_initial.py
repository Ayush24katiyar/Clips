"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-11-18
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "sources",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("url", sa.Text, nullable=False),
        sa.Column("platform", sa.String(32), nullable=False),
        sa.Column("video_id", sa.String(64), nullable=True),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("duration", sa.Float, nullable=False),
        sa.Column("height", sa.Integer, nullable=False),
        sa.Column("source_path", sa.Text, nullable=False),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_sources_video_id", "sources", ["video_id"])
    op.create_table(
        "jobs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("source_id", sa.String(36), sa.ForeignKey("sources.id", ondelete="CASCADE")),
        sa.Column("status", sa.String(24), nullable=False),
        sa.Column("stage", sa.String(32), nullable=False),
        sa.Column("progress", sa.Integer, nullable=False),
        sa.Column("quality_mode", sa.String(24), nullable=False),
        sa.Column("params", sa.JSON, nullable=False),
        sa.Column("error", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_jobs_source_id", "jobs", ["source_id"])
    op.create_index("ix_jobs_status", "jobs", ["status"])
    op.create_index("ix_jobs_created_at", "jobs", ["created_at"])
    op.create_table(
        "clips",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("job_id", sa.String(36), sa.ForeignKey("jobs.id", ondelete="CASCADE")),
        sa.Column("start", sa.Float, nullable=False),
        sa.Column("end", sa.Float, nullable=False),
        sa.Column("score", sa.Float, nullable=False),
        sa.Column("ratio", sa.String(12), nullable=False),
        sa.Column("file_path", sa.Text, nullable=False),
        sa.Column("webm_path", sa.Text, nullable=True),
        sa.Column("width", sa.Integer, nullable=False),
        sa.Column("height", sa.Integer, nullable=False),
        sa.Column("crf", sa.Integer, nullable=False),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("reason", sa.Text, nullable=False),
    )
    op.create_index("ix_clips_job_id", "clips", ["job_id"])
    op.create_table(
        "captions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("clip_id", sa.String(36), sa.ForeignKey("clips.id", ondelete="CASCADE")),
        sa.Column("format", sa.String(8), nullable=False),
        sa.Column("text", sa.Text, nullable=False),
        sa.Column("words", sa.JSON, nullable=False),
        sa.Column("path", sa.Text, nullable=False),
    )
    op.create_index("ix_captions_clip_id", "captions", ["clip_id"])
    op.create_table(
        "thumbnails",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("clip_id", sa.String(36), sa.ForeignKey("clips.id", ondelete="CASCADE")),
        sa.Column("path", sa.Text, nullable=False),
        sa.Column("frame_time", sa.Float, nullable=False),
    )
    op.create_index("ix_thumbnails_clip_id", "thumbnails", ["clip_id"])
    op.create_table(
        "streamers",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("platform", sa.String(16), nullable=False),
        sa.Column("external_id", sa.String(64), nullable=False, unique=True),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("country", sa.String(8), nullable=True),
        sa.Column("category", sa.String(64), nullable=True),
        sa.Column("channel_url", sa.Text, nullable=False),
        sa.Column("avatar_url", sa.Text, nullable=True),
    )
    op.create_index("ix_streamers_platform", "streamers", ["platform"])
    op.create_index("ix_streamers_country", "streamers", ["country"])
    op.create_index("ix_streamers_category", "streamers", ["category"])
    op.create_table(
        "streamer_metrics",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("streamer_id", sa.String(36), sa.ForeignKey("streamers.id", ondelete="CASCADE")),
        sa.Column("views", sa.Integer, nullable=False),
        sa.Column("followers", sa.Integer, nullable=False),
        sa.Column("rank", sa.Integer, nullable=False),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_streamer_metrics_streamer_id", "streamer_metrics", ["streamer_id"])
    op.create_index("ix_streamer_metrics_captured_at", "streamer_metrics", ["captured_at"])


def downgrade() -> None:
    for table in (
        "streamer_metrics",
        "streamers",
        "thumbnails",
        "captions",
        "clips",
        "jobs",
        "sources",
        "users",
    ):
        op.drop_table(table)
