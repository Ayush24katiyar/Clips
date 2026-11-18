from __future__ import annotations

import asyncio
import json
from typing import Any, Protocol

from groq import AsyncGroq

from ..core.config import settings
from ..core.errors import ProviderError
from ..schemas.analysis import Transcript

MAX_RETRIES = 5


class AIProvider(Protocol):
    async def transcribe(self, audio_path: str, language: str | None = None) -> Transcript: ...

    async def complete_json(self, system: str, user: str, schema: type) -> Any: ...


class GroqProvider:
    def __init__(self) -> None:
        if not settings.groq_api_key:
            raise ProviderError("GROQ_API_KEY is not configured")
        self.client = AsyncGroq(api_key=settings.groq_api_key)

    async def _retry(self, call: Any, *args: Any, **kwargs: Any) -> Any:
        for attempt in range(MAX_RETRIES):
            try:
                return await call(*args, **kwargs)
            except Exception as exc:
                status = getattr(exc, "status_code", 0)
                retryable = status in (429, 500, 502, 503, 504) or (
                    status == 400 and "json_validate_failed" in str(exc)
                )
                if not retryable or attempt == MAX_RETRIES - 1:
                    raise ProviderError(f"Groq request failed: {exc}") from exc
                await asyncio.sleep(min(2**attempt, 20))
        raise ProviderError("Groq retries exhausted")

    async def transcribe(self, audio_path: str, language: str | None = None) -> Transcript:
        with open(audio_path, "rb") as handle:
            response = await self._retry(
                self.client.audio.transcriptions.create,
                file=handle,
                model=settings.groq_transcribe_model,
                response_format="verbose_json",
                timestamp_granularities=["word", "segment"],
                **({"language": language} if language else {}),
                temperature=0.0,
            )
        data = response if isinstance(response, dict) else response.model_dump()
        return Transcript.model_validate(data)

    async def complete_json(self, system: str, user: str, schema: type) -> Any:
        response = await self._retry(
            self.client.chat.completions.create,
            model=settings.groq_text_model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
            max_completion_tokens=4096,
            reasoning_effort="low",
        )
        content = response.choices[0].message.content
        if not content:
            raise ProviderError("Groq returned an empty response")
        try:
            return schema.model_validate(json.loads(content))
        except (ValueError, TypeError) as exc:
            raise ProviderError(f"Groq returned invalid JSON: {content[:500]}") from exc


def get_provider() -> AIProvider:
    if settings.ai_provider == "groq":
        return GroqProvider()
    if settings.ai_provider == "local":
        from .local_provider import LocalProvider

        return LocalProvider()
    raise ProviderError(f"Unknown AI provider: {settings.ai_provider}")
