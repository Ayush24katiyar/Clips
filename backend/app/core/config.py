from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # AI
    ai_provider: str = "groq"
    groq_api_key: str = ""
    groq_transcribe_model: str = "whisper-large-v3-turbo"
    # Groq's free tier allows 25 MB per audio request; 10-min 16 kHz FLAC chunks stay well under.
    groq_audio_max_bytes: int = 20 * 1024 * 1024
    groq_audio_chunk_seconds: int = 600
    groq_audio_chunk_overlap: float = 3.0
    # Free-tier TPM is 8000; cap the analysis prompt to ~550 timestamped words.
    groq_analysis_max_words: int = 500
    groq_text_model: str = "openai/gpt-oss-20b"
    groq_vision_model: str = "qwen/qwen3.8-27b"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:3b"
    local_whisper_model: str = "large-v3"
    local_whisper_device: str = "cpu"

    # Discovery
    youtube_api_key: str = ""
    twitch_client_id: str = ""
    twitch_client_secret: str = ""

    # Infrastructure
    database_url: str = "postgresql+psycopg://clipforge:clipforge@db:5432/clipforge"
    redis_url: str = "redis://redis:6379/0"
    storage_root: Path = Path("storage")

    # Optional browser-session cookies for public videos the user is viewing.
    youtube_cookies_file: str = ""

    # Media binaries (set to absolute paths if not on PATH)
    ffmpeg_bin: str = "ffmpeg"
    ffprobe_bin: str = "ffprobe"

    # Media
    default_quality_mode: str = "visually_lossless"
    default_ratio: str = "9:16"
    render_height: int = 1080
    crf_final: int = 17
    crf_draft: int = 20
    crf_balanced: int = 21
    output_fps: int = 30
    loudness_target: float = -14.0

    # Server
    api_port: int = 8000
    frontend_port: int = 3000
    cors_origins: str = "http://localhost:3000"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    def storage_path(self, kind: str) -> Path:
        path = self.storage_root / kind
        path.mkdir(parents=True, exist_ok=True)
        return path


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
