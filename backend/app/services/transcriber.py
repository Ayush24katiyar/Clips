from __future__ import annotations

import json
from pathlib import Path

from ..core.errors import TranscriptionError
from ..utils.paths import audio_path, transcript_path
from .ffmpeg_service import extract_audio
from .groq_client import AIProvider


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

        try:
            transcript = await self.provider.transcribe(str(audio), language)
        except Exception as exc:
            raise TranscriptionError(str(exc)) from exc

        data = transcript.model_dump(mode="json")
        cached.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return data, cached
