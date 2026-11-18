from __future__ import annotations

from app.schemas.analysis import ClipCandidate, Transcript, Word
from app.services.captions_service import CaptionsService


def _transcript() -> Transcript:
    return Transcript(
        words=[
            Word(word="Hello", start=10.0, end=10.4),
            Word(word="world", start=10.4, end=10.9),
            Word(word="again", start=20.0, end=20.3),
        ]
    )


def test_words_between_filters_by_time() -> None:
    transcript = _transcript()
    assert [w.word for w in transcript.words_between(10.0, 11.0)] == ["Hello", "world"]


def test_caption_files_are_written(tmp_path) -> None:
    clip = ClipCandidate(start=10.0, end=11.0, score=80)
    paths = CaptionsService().write_all(_transcript(), clip, tmp_path)
    assert set(paths) == {"srt", "vtt", "ass"}
    assert "Hello" in paths["srt"].read_text(encoding="utf-8")
    assert "WEBVTT" in paths["vtt"].read_text(encoding="utf-8")
    assert "Dialogue:" in paths["ass"].read_text(encoding="utf-8")
