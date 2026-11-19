from __future__ import annotations

import json
from pathlib import Path

from ..core.config import settings
from ..core.errors import TranscriptionError
from ..schemas.analysis import Transcript, TranscriptSegment, Word
from ..utils.paths import audio_path, transcript_path
from .ffmpeg_service import extract_audio, split_audio
from .groq_client import AIProvider


def _merge_transcripts(
    parts: list[tuple[Transcript, float]],
    overlap: float,
    language: str,
) -> Transcript:
    """Stitch offset-adjusted chunk transcripts into one, dropping overlap duplicates."""
    words: list[Word] = []
    segments: list[TranscriptSegment] = []
    texts: list[str] = []

    for index, (part, offset) in enumerate(parts):
        # After the first chunk, discard the overlapping head of the next chunk.
        head = offset + overlap if index else 0.0
        chunk_words = [
            Word(
                word=w.word,
                start=round(w.start + offset, 3),
                end=round(w.end + offset, 3),
                confidence=w.confidence,
            )
            for w in part.words
            if w.start >= overlap or index == 0
        ]
        words.extend(w for w in chunk_words if w.end > head)
        segments.extend(
            TranscriptSegment(
                start=round(s.start + offset, 3),
                end=round(s.end + offset, 3),
                text=s.text,
            )
            for s in part.segments
            if (s.start + offset) >= head
        )
        if part.text:
            texts.append(part.text.strip())

    return Transcript(language=language, text=" ".join(texts), words=words, segments=segments)


class Transcriber:
    def __init__(self, provider: AIProvider) -> None:
        self.provider = provider

    async def transcribe(self, source_id: str, video: Path, language: str | None = None) -> tuple[dict, Path]:
        cached = transcript_path(source_id)
        if cached.exists():
            return json.loads(cached.read_text(encoding="utf-8")), cached

        audio = audio_path(source_id)
        if not audio.exists():
            extract_audio(video, audio)
        if audio.stat().st_size == 0:
            raise TranscriptionError("Extracted audio is empty")

        if audio.stat().st_size > settings.groq_audio_max_bytes:
            chunks = split_audio(
                audio,
                audio.parent / f"{source_id}-chunks",
                settings.groq_audio_chunk_seconds,
                settings.groq_audio_chunk_overlap,
            )
        else:
            chunks = [(audio, 0.0)]
        try:
            parts: list[tuple[Transcript, float]] = []
            for chunk, offset in chunks:
                parts.append((await self.provider.transcribe(str(chunk), language), offset))
            transcript = _merge_transcripts(
                parts, settings.groq_audio_chunk_overlap, language or parts[0][0].language
            )
        except Exception as exc:
            raise TranscriptionError(str(exc)) from exc

        data = transcript.model_dump(mode="json")
        cached.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return data, cached
