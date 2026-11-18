from __future__ import annotations

from app.pipeline.pipeline import new_context


def test_new_context_defaults() -> None:
    ctx = new_context("https://www.youtube.com/watch?v=abc123", {"job_id": "job-1"})
    assert ctx.job_id == "job-1"
    assert ctx.quality_mode == "visually_lossless"
    assert ctx.clip_count == 7
    assert ctx.width_height() == (1080, 1920)


def test_new_context_widescreen() -> None:
    ctx = new_context("https://example.com/v", {"ratio": "16:9"})
    assert ctx.width_height() == (1920, 1080)
