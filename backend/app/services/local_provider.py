from __future__ import annotations

import json
from typing import Any

import httpx
from faster_whisper import WhisperModel

from ..core.config import settings
from ..core.errors import ProviderError
from ..schemas.analysis import Transcript, Word

_model: WhisperModel | None = None


def _whisper() -> WhisperModel:
    global _model
    if _model is None:
        _model = WhisperModel(
            settings.local_whisper_model,
            device=settings.local_whisper_device,
            compute_type="int8",
        )
    return _model


class LocalProvider:
    """Offline fallback: faster-whisper + Ollama. Same interface as GroqProvider."""

    async def transcribe(self, audio_path: str, language: str | None = None) -> Transcript:
        segments, info = _whisper().transcribe(audio_path, word_timestamps=True, language=language, vad_filter=True)
        words: list[Word] = []
        texts: list[str] = []
        for segment in segments:
            texts.append(segment.text)
            for word in segment.words or []:
                words.append(Word(word=word.word, start=word.start, end=word.end))
        return Transcript(
            language=info.language,
            text="".join(texts).strip(),
            words=words,
        )

    async def complete_json(self, system: str, user: str, schema: type) -> Any:
        async with httpx.AsyncClient(base_url=settings.ollama_base_url, timeout=120) as client:
            response = await client.post(
                "/api/generate",
                json={
                    "model": settings.ollama_model,
                    "prompt": f"{system}\n\n{user}\n\nReturn valid JSON only.",
                    "format": "json",
                    "stream": False,
                },
            )
            response.raise_for_status()
            content = response.json().get("response", "")
        try:
            return schema.model_validate(json.loads(content))
        except (ValueError, TypeError) as exc:
            raise ProviderError(f"Ollama returned invalid JSON: {content[:500]}") from exc
